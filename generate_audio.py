import os
import asyncio
import subprocess
import json
import edge_tts

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "+10%"
FPS = 30

CUES = [
    # 【第一乐章 · 题意破题与空间构想】
    {
        "id": 1,
        "chapter": 1,
        "text": "这是2025年新高考全国二卷的第十四题。",
        "subtitle": "这是 2025 年新高考全国 II 卷第 14 题。"
    },
    {
        "id": 2,
        "chapter": 1,
        "text": "底面半径为 4 厘米、高为 9 厘米的封闭圆柱形容器内，有两个半径相等的铁球，求铁球半径的最大值是多少。",
        "subtitle": "底面半径 4cm、高 9cm 的封闭圆柱形容器内有两个等大铁球，\n求铁球半径的最大值。"
    },
    {
        "id": 3,
        "chapter": 1,
        "text": "两个球到底怎么放，才能把半径撑到最大呢？我们直接在三维空间中做一次探索！",
        "subtitle": "两个球到底怎么放，才能把半径撑到最大？\n我们直接在三维空间中做一次探索！"
    },

    # 【第二乐章 · 直觉探索一：水平并排与上下晃荡】
    {
        "id": 4,
        "chapter": 2,
        "text": "首先，最容易想到的就是：把两个铁球水平并排挤在圆柱底面上。",
        "subtitle": "首先，最容易想到的是：把两球水平并排挤在底面上。"
    },
    {
        "id": 5,
        "chapter": 2,
        "text": "当两球直径之和刚好等于底面直径 8 厘米时，每个球的半径是 2 厘米。",
        "subtitle": "当两球直径之和等于底面直径 8cm 时，\n每个球的半径 r = 2 cm。"
    },
    {
        "id": 6,
        "chapter": 2,
        "text": "但是你看！两球就算并排紧贴，整体在圆柱里还可以大幅度地上下移动晃荡！",
        "subtitle": "但是你看！两球并排紧贴，整体在圆柱里还可以大幅上下晃荡！"
    },
    {
        "id": 7,
        "chapter": 2,
        "text": "圆柱的高足足有 9 厘米，上半截还空着整整 5 厘米的空间！",
        "subtitle": "圆柱高足足有 9cm，上半截还空着整整 5cm！"
    },
    {
        "id": 8,
        "chapter": 2,
        "text": "水平并排远远没有用足空间，铁球显然还能更大！",
        "subtitle": "水平并排远远没有用足空间，铁球显然还能更大！"
    },

    # 【第三乐章 · 直觉探索二：竖直叠放与左右晃荡】
    {
        "id": 9,
        "chapter": 3,
        "text": "既然上面空间大，那我们把两个球竖着串联叠放、顶天立地怎么样？",
        "subtitle": "既然上面空间大，我们把两球竖着串联叠放顶天立地！"
    },
    {
        "id": 10,
        "chapter": 3,
        "text": "两球直径加起来刚好等于圆柱的高 9 厘米，此时每个球的半径达到了 2.25 厘米！",
        "subtitle": "两球直径之和等于高 9cm，此时半径达到 2.25 cm！"
    },
    {
        "id": 11,
        "chapter": 3,
        "text": "但是你看！竖直方向顶死了，却可以在水平方向左右乱晃！",
        "subtitle": "竖直方向顶死了，却在水平方向左右乱晃！"
    },
    {
        "id": 12,
        "chapter": 3,
        "text": "底面直径有 8 厘米，而球的直径才 4.5 厘米，两侧还有足足 3.5 厘米的巨大空隙！",
        "subtitle": "底面直径 8cm，而球径仅 4.5cm，两侧留有 3.5cm 巨大缝隙！"
    },

    # 【第四乐章 · 空间错位与终极极限卡死】
    {
        "id": 13,
        "chapter": 4,
        "text": "怎样才能把高度和宽度同时榨干？答案呼之欲出——斜着错开！",
        "subtitle": "怎样才能把高和宽同时榨干？答案呼之欲出——斜着错开！"
    },
    {
        "id": 14,
        "chapter": 4,
        "text": "我们让一个球贴底靠左，另一个球顶天靠右，沿对角线彼此外切！",
        "subtitle": "一个球贴底靠左，另一个球顶天靠右，沿对角线彼此外切！"
    },
    {
        "id": 15,
        "chapter": 4,
        "text": "看！随着它们斜向错开，铁球开始继续向外疯狂膨胀！",
        "subtitle": "看！随着它们斜向错开，铁球开始继续向外疯狂膨胀！"
    },
    {
        "id": 16,
        "chapter": 4,
        "text": "下球踩死底面贴死左壁，上球顶死顶面贴死右壁，两球在对角线上彼此顶死相切！",
        "subtitle": "下球踩底贴左壁，上球顶天贴右壁，两球对角彼此顶死相切！"
    },
    {
        "id": 17,
        "chapter": 4,
        "text": "上下、左右、对角，三个维度的自由度全部锁死，空间被彻底榨干！",
        "subtitle": "上下、左右、对角，三个维度自由度全部锁死，空间被彻底榨干！"
    },

    # 【第五乐章 · 空间降维与秒杀勾三股四直角三角形】
    {
        "id": 18,
        "chapter": 5,
        "text": "极限状态一旦确定，几何模型瞬间降维！",
        "subtitle": "极限状态一旦确定，几何模型瞬间降维！"
    },
    {
        "id": 19,
        "chapter": 5,
        "text": "过两球球心做一个垂直纵剖面：竖直高差是 9 减 2r，水平跨度是 8 减 2r，球心连线斜边刚好是 2r！",
        "subtitle": "纵剖面直角三角形：竖直高差 9-2r，水平跨度 8-2r，斜边 2r！"
    },
    {
        "id": 20,
        "chapter": 5,
        "text": "空间勾股定理方程一秒列出：(8 - 2r)² + (9 - 2r)² = (2r)²！",
        "subtitle": "空间勾股定理：(8 - 2r)² + (9 - 2r)² = (2r)²！"
    },
    {
        "id": 21,
        "chapter": 5,
        "text": "化简因式分解：(2r - 5)(2r - 29) = 0，立刻算出最大半径 r 等于 2.5 厘米！",
        "subtitle": "化简得 (2r - 5)(2r - 29) = 0，解得最大半径 r = 2.5 cm！"
    },
    {
        "id": 22,
        "chapter": 5,
        "text": "高差是 4，底边是 3，斜边是 5，这正是我们最熟悉的黄金勾三股四弦五！",
        "subtitle": "高差 4，底边 3，斜边 5，正是我们最熟悉的黄金勾三股四弦五！"
    },

    # 【第六乐章 · 3D 全景回归与极值思维复盘】
    {
        "id": 23,
        "chapter": 6,
        "text": "最后我们拉远视角回顾：水平放太矮，竖直放太瘦，只有对角错开锁死自由度，才能达到完美的 2.5 厘米！",
        "subtitle": "水平放太矮，竖直放太瘦，只有对角错开锁死自由度，才达完美的 2.5 cm！"
    },
    {
        "id": 24,
        "chapter": 6,
        "text": "掌握空间立体几何的极限碰撞与降维投影，一眼看穿几何本质，极速秒杀压轴题！",
        "subtitle": "掌握空间几何的极限碰撞与降维投影，极速秒杀高考压轴题！"
    }
]

def get_audio_duration(file_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return float(res.stdout.strip())

def format_time_srt(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        ms = 999
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

async def main():
    print(f"Generating {len(CUES)} voice cues via edge-tts...")
    timeline = []
    current_time = 0.5  # 开头留 0.5 秒静音缓冲

    srt_lines = []
    audio_files = []

    for i, cue in enumerate(CUES):
        cue_file = os.path.join(AUDIO_DIR, f"cue_{cue['id']:02d}.mp3")
        comm = edge_tts.Communicate(cue["text"], VOICE, rate=RATE)
        await comm.save(cue_file)

        dur = get_audio_duration(cue_file)
        start_t = current_time
        end_t = current_time + dur

        start_f = int(round(start_t * FPS))
        end_f = int(round(end_t * FPS))

        cue_info = {
            "id": cue["id"],
            "chapter": cue["chapter"],
            "text": cue["text"],
            "subtitle": cue["subtitle"],
            "file": cue_file,
            "duration": dur,
            "start_time": start_t,
            "end_time": end_t,
            "start_frame": start_f,
            "end_frame": end_f
        }
        timeline.append(cue_info)
        audio_files.append(cue_file)

        # 写入 SRT 格式
        srt_lines.append(f"{i+1}")
        srt_lines.append(f"{format_time_srt(start_t)} --> {format_time_srt(end_t)}")
        srt_lines.append(cue["subtitle"])
        srt_lines.append("")

        # 句间轻微停顿 (0.35s)
        current_time = end_t + 0.35

    total_duration = current_time + 1.0  # 片尾留 1 秒定格
    total_frames = int(round(total_duration * FPS))

    # 保存 timeline.json
    meta = {
        "total_duration": total_duration,
        "total_frames": total_frames,
        "fps": FPS,
        "cues": timeline
    }
    with open(os.path.join(BASE_DIR, "audio_timeline.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # 保存 subtitles.srt
    with open(os.path.join(BASE_DIR, "subtitles.srt"), "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))

    # 合成完整 master_audio.mp3
    concat_list = os.path.join(AUDIO_DIR, "concat.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        # 首部 0.5s 静音
        f.write("ffconcat version 1.0\n")
        for cue in timeline:
            f.write(f"file '{os.path.basename(cue['file'])}'\n")
            f.write(f"duration {cue['duration']}\n")

    master_audio = os.path.join(BASE_DIR, "master_audio.mp3")
    cmd_merge = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c:a", "libmp3lame", "-q:a", "2",
        master_audio
    ]
    subprocess.run(cmd_merge, cwd=AUDIO_DIR, capture_output=True)

    print(f"Audio generation complete!")
    print(f"Total Duration: {total_duration:.2f} s ({total_frames} frames @ {FPS} fps)")
    print(f"Master Audio: {master_audio}")

if __name__ == "__main__":
    asyncio.run(main())
