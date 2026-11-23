"""Render hand-prepared, frame-aligned transparent layers over a clean plate."""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import map_coordinates


def render(config, folder, output):
    background = ImageOps.exif_transpose(Image.open(folder / config["background"]))
    background = np.asarray(background.convert("RGB"), dtype=np.float32)
    height, width = background.shape[:2]
    fps = int(config.get("fps", 24))
    count = round(float(config.get("seconds", 5)) * fps)
    if width % 2 or height % 2 or fps < 1 or count < 1:
        raise ValueError("Use even canvas dimensions, positive FPS and at least one frame.")
    y, x = np.mgrid[:height, :width].astype(np.float32)
    layers = []
    for spec in config["layers"]:
        rgba = np.asarray(Image.open(folder / spec["file"]).convert("RGBA"), dtype=np.float32)
        if rgba.shape[:2] != (height, width):
            raise ValueError(f"Layer dimensions must match the plate: {spec['file']}")
        rgba[..., 3] /= 255
        rgba[..., :3] *= rgba[..., 3:4]
        keys = np.asarray(spec["path"], dtype=float)
        if keys.ndim != 2 or keys.shape[1] != 3 or len(keys) < 2:
            raise ValueError("Each path needs two or more [time, x, y] keyframes.")
        layers.append((rgba, keys, PchipInterpolator(keys[:, 0], keys[:, 1:], axis=0), spec))
    command = [
        "ffmpeg", "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{width}x{height}", "-r", str(fps), "-i", "-", "-c:v", "libx264",
        "-pix_fmt", "yuv420p", "-crf", "16", "-movflags", "+faststart", str(output),
    ]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
        for frame in range(count):
            seconds = frame / fps
            canvas = background.copy()
            for rgba, keys, path, spec in layers:
                dx, dy = path(np.clip(seconds, keys[0, 0], keys[-1, 0]))
                detail = float(spec.get("flow", 0))
                shear = float(spec.get("shear", 0)) * seconds
                strength = (1 - np.exp(-seconds)) * detail
                source_x = x - dx - shear * (0.5 - y / height)
                source_y = y - dy + strength * np.sin(source_x / 73 - seconds * 0.8 + y / 101)
                source_x -= strength * np.sin(y / 53 - seconds * 0.6 + source_x / 109)
                positions = [source_y, source_x]
                warped = np.stack([
                    map_coordinates(rgba[..., channel], positions, order=1,
                                    mode="constant", cval=0, prefilter=False)
                    for channel in range(4)
                ], axis=-1)
                canvas = canvas * (1 - warped[..., 3:4]) + warped[..., :3]
            encoder.stdin.write(np.clip(canvas, 0, 255).astype(np.uint8).tobytes())
        encoder.stdin.close()
        if encoder.wait():
            raise RuntimeError("FFmpeg failed to encode the video.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene", type=Path, help="JSON scene and paths relative to its folder")
    parser.add_argument("output", type=Path, help="New .mp4 output path")
    args = parser.parse_args()
    render(json.loads(args.scene.read_text(encoding="utf-8")), args.scene.parent, args.output)
