# 2025年新高考II卷 第14题 · 圆柱内两等半径铁球的最大半径

> **原题题干**：一个底面半径为 4 cm、高为 9 cm 的封闭圆柱形容器内放入两个半径相同的铁球，求铁球半径的最大值。

本仓库用 Blender 3D 物理模拟做直觉探索，再用 Manim 做严格推导，最后用 Edge-TTS 晓晓配音合成成片。

## 文件结构

- `blender_scene.py` / `blender_scene_v2.py`：Blender 球体物理摆放场景脚本
- `blender_animation.py` / `blender_animation_v2.py`：Blender 动画导出脚本
- `proof_manim.py`：Manim 严格推导动画脚本
- `generate_audio.py` / `generate_audio_part2.py`：Edge-TTS 配音与音画对齐测量
- `audio_timeline.json` / `audio_timeline_part2.json`：配音时间轴
- `burn_subtitles.py`：用 ASS 字幕烧录画面
- `build_full_video.py`：片头 + 两段正文拼接为完整成片
- `tts.md` / `tts2.md`：两部分口播台词稿
- `render_2025_new_gaokao_2_q14_full.mp4`：完整成片

## 运行

```powershell
# Manim 推导动画（在上级目录的 .venv 中）
..\.venv\Scripts\manim.exe -qh proof_manim.py

# 配音生成
..\.venv\Scripts\python.exe generate_audio.py
..\.venv\Scripts\python.exe generate_audio_part2.py

# 拼接完整成片（依赖 ffmpeg 在 PATH 中）
..\.venv\Scripts\python.exe build_full_video.py
```

## 仓库说明

- `.gitignore` 排除了 `media/` 渲染中间产物，用上面的命令重新生成即可。
- 脚本里的霞鹜文楷字体路径写死为 `X:\字体\霞鹜文楷LXGW_WenKai\lxgw-wenkai-v1.520`，换机器运行前先改成本地路径（字体下载：<https://github.com/lxgw/LxgwWenKai/releases>）。
