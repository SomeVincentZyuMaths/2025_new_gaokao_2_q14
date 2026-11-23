import os
import asyncio
import subprocess
import json
import edge_tts

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio_part2")
os.makedirs(AUDIO_DIR, exist_ok=True)

VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "+10%"
FPS = 30

CUES = [
    # 【第一乐章 · 灵魂发问：直观猜想真的严谨吗？】
    {
        "id": 1,
        "chapter": 1,
        "text": "刚才在三维动画里，我们通过错位晃荡，找到了贴顶贴底、外切卡死的形态，算出了 2.5 厘米。",
        "subtitle": "刚才在三维动画里，我们通过错位外切卡死，\n算出了半径 r = 2.5 cm。"
    },
    {
        "id": 2,
        "chapter": 1,
        "text": "但这只是我们肉眼看到的对称形态，凭什么这就是全局最大值？",
        "subtitle": "但这只是直观对称摆法，凭什么它就是全局最大？"
    },
    {
        "id": 3,
        "chapter": 1,
        "text": "万一在三维空间里，存在某种极其刁钻的非对称姿态，能塞下 2.51 厘米的球呢？",
        "subtitle": "万一存在某种极其刁钻的非对称姿态，\n能塞下 2.51 cm 的球呢？"
    },
    {
        "id": 4,
        "chapter": 1,
        "text": "今天，我们就请出数学核武器——不等式链，给出无懈可击的严格数学证明！",
        "subtitle": "今天，我们请出数学核武器——不等式链，\n给出严格的数学证明！"
    },

    # 【第二乐章 · 规范建系：空间基准与代数符号约定】（新增核心乐章）
    {
        "id": 5,
        "chapter": 2,
        "text": "进行严格证明的第一步，必须规范建立空间直角坐标系！",
        "subtitle": "进行严格证明的第一步：规范建立空间直角坐标系！"
    },
    {
        "id": 6,
        "chapter": 2,
        "text": "以底面圆心为原点 O，x 轴与 y 轴在底面互相垂直，圆柱中心轴线为竖直向上的 z 轴。",
        "subtitle": "以底面圆心为原点 O，x 与 y 轴在底面垂直，\n中心轴为竖直向上的 z 轴。"
    },
    {
        "id": 7,
        "chapter": 2,
        "text": "圆柱容器的解析方程为：x² + y² ≤ 16，且竖直高度 z 在 0 到 9 之间。",
        "subtitle": "容器解析约束：x² + y² ≤ 16，且高度 0 ≤ z ≤ 9。"
    },
    {
        "id": 8,
        "chapter": 2,
        "text": "设两个球心分别为 欧一 和 欧二，底面垂直投影点分别为 披一 和 披二。",
        "subtitle": "设两球心为 O₁(x₁,y₁,z₁) 与 O₂(x₂,y₂,z₂)，\n底面投影点为 P₁ 与 P₂。"
    },
    {
        "id": 9,
        "chapter": 2,
        "text": "水平跨度为 Δρ，垂直高差为 Δz，空间球心距为 L。代数武器正式启动！",
        "subtitle": "水平跨度 Δρ，垂直高差 Δz，球心距 L。\n代数武器正式启动！"
    },

    # 【第三乐章 · 水平压榨：底面圆盘的几何极值】
    {
        "id": 10,
        "chapter": 3,
        "text": "首先，我们考察水平维度。要想球装进圆柱，球心在水平面上的投影，距离侧壁必须至少为 r！",
        "subtitle": "首先考察水平维度：球心水平投影，\n距离侧壁必须至少为 r！"
    },
    {
        "id": 11,
        "chapter": 3,
        "text": "这意味着，两个球心的水平投影点 P₁ 和 P₂，只能活动在半径为 4 减 r 的同心圆盘内！",
        "subtitle": "两球心水平投影 P₁ 与 P₂，\n只能活动在半径 4 - r 的同心圆盘内！"
    },
    {
        "id": 12,
        "chapter": 3,
        "text": "在一个半径为 4 减 r 的圆盘里，两点之间的最大水平距离，绝不可能超过该圆的直径！",
        "subtitle": "在半径 4 - r 的圆盘内，两点最大距离绝不可能超过直径！"
    },
    {
        "id": 13,
        "chapter": 3,
        "text": "因此，两球心水平跨度 Δρ，必然小于等于 2 倍的 4 减 r，也就是 8 减 2r！",
        "subtitle": "因此，水平跨度 Δρ 必然 ≤ 2(4 - r) = 8 - 2r！"
    },

    # 【第四乐章 · 竖直压榨：容器高度的绝对限制】
    {
        "id": 14,
        "chapter": 4,
        "text": "再看竖直方向。下球心最低不低于 r，上球心最高不高于 9 减 r。",
        "subtitle": "再看竖直方向：下球心最低为 r，上球心最高为 9 - r。"
    },
    {
        "id": 15,
        "chapter": 4,
        "text": "整个竖直方向的有效活动区间长度，只有 9 减 2r。两端贴满时高差达到极限！",
        "subtitle": "竖直有效活动区间长度只有 9 - 2r，\n两端贴满时高差达到极限！"
    },
    {
        "id": 16,
        "chapter": 4,
        "text": "所以，两球心的垂直高差 Δz，必然小于等于 9 减 2r！",
        "subtitle": "所以，垂直高差 Δz 必然 ≤ 9 - 2r！"
    },
    {
        "id": 17,
        "chapter": 4,
        "text": "圆柱的几何外壳，已经给球心在水平与竖直方向，死死焊上了物理天花板！",
        "subtitle": "圆柱外壳已给水平和竖直方向死死焊上了物理天花板！"
    },

    # 【第五乐章 · 不等式合体：勾股定理的空间绝杀】
    {
        "id": 18,
        "chapter": 5,
        "text": "接下来，是见证数学奇迹的高光时刻！",
        "subtitle": "接下来，是见证数学奇迹的高光时刻！"
    },
    {
        "id": 19,
        "chapter": 5,
        "text": "根据空间两点距离公式，两球心的距离平方 L²，恰好等于水平跨度平方加上垂直高差平方！",
        "subtitle": "由空间距离公式：球心距 L² = 水平跨度 Δρ² + 垂直高差 Δz²！"
    },
    {
        "id": 20,
        "chapter": 5,
        "text": "将两个极值代入，立刻得到球心距平方的绝对上限：小于等于 8 减 2r 的平方加上 9 减 2r 的平方！",
        "subtitle": "代入极值，得球心距 L² ≤ (8 - 2r)² + (9 - 2r)²！"
    },
    {
        "id": 21,
        "chapter": 5,
        "text": "而另一方面，两球互不相交的几何硬性约束要求：两球心距离绝不能小于 2r！",
        "subtitle": "而两球互不侵入的硬性几何约束：球心距 L ≥ 2r！"
    },
    {
        "id": 22,
        "chapter": 5,
        "text": "两头一夹，终极不等式链诞生了：4r² 小于等于球心距平方，小于等于 8 减 2r 的平方加上 9 减 2r 的平方！",
        "subtitle": "两头一夹，终极不等式链诞生：\n(2r)² ≤ L² ≤ (8 - 2r)² + (9 - 2r)²！"
    },

    # 【第六乐章 · 二次函数裁决：唯一的合法真理】
    {
        "id": 23,
        "chapter": 6,
        "text": "展开化简这个关于 r 的一元二次不等式：",
        "subtitle": "展开化简这个关于 r 的一元二次不等式："
    },
    {
        "id": 24,
        "chapter": 6,
        "text": "移项整理，得到 4r² - 68r + 145 大于等于 0！",
        "subtitle": "移项整理得：4r² - 68r + 145 ≥ 0！"
    },
    {
        "id": 25,
        "chapter": 6,
        "text": "因式分解：2r 减 5 乘以 2r 减 29 大于等于 0！",
        "subtitle": "因式分解：(2r - 5)(2r - 29) ≥ 0！"
    },
    {
        "id": 26,
        "chapter": 6,
        "text": "解得 r 小于等于 2.5，或者 r 大于等于 14.5！",
        "subtitle": "解得 r ≤ 2.5 或 r ≥ 14.5！"
    },
    {
        "id": 27,
        "chapter": 6,
        "text": "但在底面半径为 4 的圆柱内，r 必须小于 4，14.5 被彻底淘汰！",
        "subtitle": "但在底面半径为 4 的圆柱内 r < 4，14.5 被彻底淘汰！"
    },
    {
        "id": 28,
        "chapter": 6,
        "text": "剩下的唯一可能，就是 r 必须小于等于 2.5 厘米！",
        "subtitle": "剩下的唯一可能：r 必须 ≤ 2.5 cm！"
    },

    # 【第七乐章 · 总结升华：直觉与代数的完美闭环】
    {
        "id": 29,
        "chapter": 7,
        "text": "无论两球怎么旋转、怎么斜放，数学不等式像一道钢铁防线，将半径死死锁定在 2.5 厘米内！",
        "subtitle": "无论两球姿势如何刁钻，不等式链将半径死死锁定在 2.5 cm 内！"
    },
    {
        "id": 30,
        "chapter": 7,
        "text": "几何直觉探索形态，代数定理锁定极值。这，就是数学证明的极致浪漫！",
        "subtitle": "几何直觉探索形态，代数定理锁定极值。\n这才是数学证明的极致浪漫！"
    }
]

def get_audio_duration(file_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

async def generate_cues():
    print(f"Generating {len(CUES)} audio cues with voice '{VOICE}' (rate={RATE})...")
    for cue in CUES:
        cid = cue["id"]
        out_file = os.path.join(AUDIO_DIR, f"cue_{cid:02d}.mp3")
        cue["audio_path"] = out_file
        print(f"[{cid:02d}] Generating: {cue['text'][:25]}...")
        communicate = edge_tts.Communicate(cue["text"], VOICE, rate=RATE)
        await communicate.save(out_file)
        cue["duration"] = get_audio_duration(out_file)

def assemble_master_audio():
    print("\nAssembling master audio and computing exact timeline...")
    current_time = 0.5  # 开头留白 0.5s
    file_list_path = os.path.join(AUDIO_DIR, "concat_list.txt")

    timeline_data = {
        "voice": VOICE,
        "rate": RATE,
        "fps": FPS,
        "cues": []
    }

    with open(file_list_path, "w", encoding="utf-8") as concat_f:
        # 生成开头静音 0.5s
        silence_05 = os.path.join(AUDIO_DIR, "silence_05.mp3")
        if not os.path.exists(silence_05):
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                "-t", "0.5", "-q:a", "9", silence_05
            ], capture_output=True, check=True)
        concat_f.write(f"file '{silence_05.replace(chr(92), '/')}'\n")

        # 句间间隙 0.25s
        silence_gap = os.path.join(AUDIO_DIR, "silence_gap.mp3")
        if not os.path.exists(silence_gap):
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                "-t", "0.25", "-q:a", "9", silence_gap
            ], capture_output=True, check=True)

        for i, cue in enumerate(CUES):
            cue_start = current_time
            cue_end = cue_start + cue["duration"]
            start_frame = int(round(cue_start * FPS))
            end_frame = int(round(cue_end * FPS))

            timeline_data["cues"].append({
                "id": cue["id"],
                "chapter": cue["chapter"],
                "text": cue["text"],
                "subtitle": cue["subtitle"],
                "start_time": cue_start,
                "end_time": cue_end,
                "duration": cue["duration"],
                "start_frame": start_frame,
                "end_frame": end_frame
            })

            concat_f.write(f"file '{cue['audio_path'].replace(chr(92), '/')}'\n")
            current_time = cue_end

            # 如果不是最后一句，添加 0.25s 停顿
            if i < len(CUES) - 1:
                concat_f.write(f"file '{silence_gap.replace(chr(92), '/')}'\n")
                current_time += 0.25

    # 结尾留白 1.5s
    silence_end = os.path.join(AUDIO_DIR, "silence_end.mp3")
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
        "-t", "1.5", "-q:a", "9", silence_end
    ], capture_output=True, check=True)
    with open(file_list_path, "a", encoding="utf-8") as concat_f:
        concat_f.write(f"file '{silence_end.replace(chr(92), '/')}'\n")
    current_time += 1.5

    master_audio_path = os.path.join(BASE_DIR, "master_audio_part2.mp3")
    print(f"Concatenating audio to {master_audio_path}...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", file_list_path, "-c", "copy", master_audio_path
    ], capture_output=True, check=True)

    total_duration = get_audio_duration(master_audio_path)
    total_frames = int(round(total_duration * FPS))
    timeline_data["total_duration"] = total_duration
    timeline_data["total_frames"] = total_frames

    # 保存 JSON 时间线
    timeline_json_path = os.path.join(BASE_DIR, "audio_timeline_part2.json")
    with open(timeline_json_path, "w", encoding="utf-8") as jf:
        json.dump(timeline_data, jf, ensure_ascii=False, indent=2)
    print(f"Timeline written to {timeline_json_path}")

    # 保存 SRT 字幕
    srt_path = os.path.join(BASE_DIR, "subtitles_part2.srt")
    def format_srt_time(sec):
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        ms = int(round((sec - int(sec)) * 1000))
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    with open(srt_path, "w", encoding="utf-8") as srt_f:
        for idx, c in enumerate(timeline_data["cues"], 1):
            srt_f.write(f"{idx}\n")
            srt_f.write(f"{format_srt_time(c['start_time'])} --> {format_srt_time(c['end_time'])}\n")
            srt_f.write(f"{c['subtitle']}\n\n")
    print(f"SRT written to {srt_path}")

    print(f"\n==========================================")
    print(f"Master Audio Duration: {total_duration:.2f}s ({total_frames} frames @ {FPS} fps)")
    print(f"==========================================")

if __name__ == "__main__":
    asyncio.run(generate_cues())
    assemble_master_audio()
