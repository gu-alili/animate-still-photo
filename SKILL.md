---
name: animate-still-photo
description: Turn a single still photo or illustration into a natural-looking short video, animated GIF, or iPhone Live Photo source clip. Use for localized motion such as starry skies, cloud arches with stairs, sailing boats, pink clouds over water, dusk clouds with signal lights, grass, water, and reflections, or when revising motion, star occlusion, and trails in an existing still-to-video project.
---

# 单张照片转动态视频

1. 读取源图并确认输出用途、画面比例、动效方向和强度。用户有参考视频时，比较开头、中段和结尾，记录每个物体的方向、速度变化、形态变化和遮挡。先保留原构图与清晰度。
2. 标记固定背景、活动物体和前景遮挡。补齐活动物体原来挡住的背景，单独检查干净底图。把云、薄云和其他活动主体抠成透明 PNG。固定星星保留在背景上。去除抠图带入的星点和底色，保留云的明暗纹理。
3. 根据观察设置路径。用连续插值控制速度和方向。厚云与薄云可采用不同速度。云沿风向整体流动时，可叠加低幅度、时间连续的局部变化。草尖和水波使用局部遮罩。倒影从同期主体运动推导，在水面区域叠加波纹。
4. 按画面选用[五种场景做法](references/scenes.md)。一张图可以组合多种动效，先确定固定地标与遮挡关系，再把每个运动物体安排到同一时间轴。
5. 用 [命令与参数](references/render.md) 运行 `scripts/animate.py`。它接收清理后的背景和对齐到画布的图层，并执行分层平移、剪切与局部流动。复杂的草浪或倒影可用独立遮罩流程生成，再合成到同一时间轴。保留原视频完整构图，按需导出 GIF 或实况照片转换用短片。
6. 检查起始、中段和末尾，并播放成片。放大检查固定物体边缘、厚云上的星点、云移开后露出的背景和画质。遇到残影先检查底图，再检查透明层。用 ffprobe 核对分辨率、帧率和时长，解码成片后交付。
7. 朋友圈多图需要动态效果时，先核实当前手机和微信版本支持的格式。把 iPhone 转换源明确标为 MP4 短片。只有导入相册并看到 LIVE 标记、长按可播放时，才确认实况照片成功。
