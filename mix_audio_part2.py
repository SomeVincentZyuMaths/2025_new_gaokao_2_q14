import os
import sys
import json
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TIMELINE_FILE = os.path.join(BASE_DIR, "audio_timeline_part2.json")
FONTS_DIR = r"X:\字体\霞鹜文楷LXGW_WenKai\lxgw-wenkai-v1.520"
ASS_PATH = os.path.join(BASE_DIR, "subtitles_part2.ass")
MASTER_AUDIO = os.path.join(BASE_DIR, "master_audio_part2.mp3")

# Manim 默认输出路径
MANIM_VIDEO_720P = os.path.join(BASE_DIR, "media", "videos", "proof_manim", "720p30", "MathProofPart2.mp4")

CLEAN_VIDEO = os.path.join(BASE_DIR, "render_2025_new_gaokao_2_q14_part2_proof_clean.mp4")
FINAL_VIDEO = os.path.join(BASE_DIR, "render_2025_new_gaokao_2_q14_part2_proof.mp4")

LEAD_IN_BIAS = 0.25
TRAIL_OUT_BIAS = 0.10

def format_ass_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def generate_ass(font_name="LXGW WenKai Medium", font_size=28):
    with open(TIMELINE_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)

    header = f"""[Script Info]
Title: 2025 New Gaokao II Q14 Part 2 Mathematical Proof
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H00F5FAFF,&H000000FF,&H00141414,&H80000000,-1,0,0,0,100,100,0,0,1,2.4,1.4,2,30,30,36,1
Style: Highlight,{font_name},{font_size + 2},&H002EE0FF,&H000000FF,&H000A0A0A,&H80000000,-1,0,0,0,100,100,0,0,1,2.8,1.6,2,30,30,36,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    # 核心公式与定论使用金色高亮
    highlight_ids = {4, 7, 9, 13, 16, 19, 20, 22, 24, 25, 26, 28, 29, 30}
    lines = [header]
    for c in meta["cues"]:
        # 注入提前量：早出 0.25s，晚收 0.10s
        sub_start = max(0.0, c["start_time"] - LEAD_IN_BIAS)
        sub_end = c["end_time"] + TRAIL_OUT_BIAS
        t_start = format_ass_time(sub_start)
        t_end = format_ass_time(sub_end)
        style = "Highlight" if c["id"] in highlight_ids else "Default"
        sub_text = c["subtitle"].replace("\n", "\\N")
        lines.append(f"Dialogue: 0,{t_start},{t_end},{style},,0,0,0,,{sub_text}\n")

    with open(ASS_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"Generated Calibrated ASS subtitle (Lead-in={LEAD_IN_BIAS}s): {ASS_PATH}")

def mix_and_burn():
    if not os.path.exists(MANIM_VIDEO_720P):
        print(f"Error: Manim raw video not found at {MANIM_VIDEO_720P}")
        return False

    generate_ass()

    # 1. 生成带音频的干净视频
    print(f"Step 1: Merging audio into clean video...")
    cmd_clean = [
        "ffmpeg", "-y",
        "-i", MANIM_VIDEO_720P,
        "-i", MASTER_AUDIO,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        CLEAN_VIDEO
    ]
    subprocess.run(cmd_clean, check=True)
    print(f"Clean video saved: {CLEAN_VIDEO}")

    # 2. 烧录 ASS 字幕生成最终成品
    print(f"Step 2: Burning hard subtitles into final video...")
    escaped_ass = ASS_PATH.replace("\\", "/").replace(":", "\\:")
    escaped_fonts = FONTS_DIR.replace("\\", "/").replace(":", "\\:")
    vf_filter = f"ass='{escaped_ass}':fontsdir='{escaped_fonts}'"

    tmp_out = os.path.join(BASE_DIR, "tmp_proof_final.mp4")
    cmd_sub = [
        "ffmpeg", "-y",
        "-i", CLEAN_VIDEO,
        "-vf", vf_filter,
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "fast",
        "-c:a", "copy",
        tmp_out
    ]
    subprocess.run(cmd_sub, check=True)

    if os.path.exists(FINAL_VIDEO):
        os.remove(FINAL_VIDEO)
    shutil.move(tmp_out, FINAL_VIDEO)
    print(f"Success! Final proof video generated: {FINAL_VIDEO}")
    return True

if __name__ == "__main__":
    mix_and_burn()
