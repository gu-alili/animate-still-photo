# 分层渲染与导出

需要 Python 3、Pillow、NumPy、SciPy，以及 PATH 中带 libx264 的 FFmpeg。

```bash
python -m pip install pillow numpy scipy
python scripts/animate.py scene.json output.mp4
```

用修复笔刷、图像编辑工具或干净天空采样制作底图。在原云占据的区域采样检查是否还有云轮廓。将透明 PNG 按原位置放在和底图同尺寸的画布上，星空里的厚云 alpha 接近 1，薄云边缘逐渐降至 0。先在小分辨率和短时长下试渲染，再用原图尺寸导出。下面的数值是 1920×1080 场景的起点，按图调整。

```json
{
  "background": "clean-plate.png",
  "fps": 24,
  "seconds": 5,
  "layers": [
    {
      "file": "cloud.png",
      "path": [[0, 0, 0], [1.5, 28, -4], [3.2, 105, -8], [5, 185, -13]],
      "shear": 10,
      "flow": 6
    }
  ]
}
```

路径每一项依次是秒、右移像素、下移像素。图层按从后到前的顺序绘制，超出画布的部分裁切。shear 是每秒横移的上下差值，flow 是局部位移幅度，以像素计。静止前景可用两组零位移关键帧叠在顶部。复杂的局部动作交给独立动效层，检查接缝和遮挡。

## 输出示例

```bash
ffmpeg -i output.mp4 -filter_complex_threads 2 -filter_complex \
  "fps=12,scale=800:-2:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" \
  -loop 0 output.gif
ffmpeg -ss 1 -i output.mp4 -t 3 -an -c:v libx264 -crf 16 \
  -pix_fmt yuv420p -movflags +faststart live-photo-source.mp4
ffprobe -v error -show_entries stream=width,height,r_frame_rate,duration,nb_frames output.mp4
ffmpeg -v error -i output.mp4 -f null -
```

GIF 循环回到第一帧时，单向运动可能出现跳切。根据画面选择接近的首尾状态或接受剪辑点。实况照片源短片从动作最易辨识的位置开始截取。
