import os
import sys
import json
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TIMELINE_FILE = os.path.join(BASE_DIR, "audio_timeline.json")
FONTS_DIR = r"X:\字体\霞鹜文楷LXGW_WenKai\lxgw-wenkai-v1.520"
ASS_PATH = os.path.join(BASE_DIR, "subtitles.ass")

ORIGINAL_VIDEO = os.path.join(BASE_DIR, "render_2025_new_gaokao_2_q14_v2.mp4")
CLEAN_VIDEO = os.path.join(BASE_DIR, "render_2025_new_gaokao_2_q14_v2_clean.mp4")
FINAL_SUB_VIDEO = os.path.join(BASE_DIR, "render_2025_new_gaokao_2_q14_v2.mp4")

# 字幕提前量 (秒)：宁早勿晚，提前 0.25 秒出现，延迟 0.1 秒淡出
LEAD_IN_BIAS = 0.25
TRAIL_OUT_BIAS = 0.10

def format_ass_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def calibrate_and_generate_ass(font_name="LXGW WenKai Medium", font_size=30):
    with open(TIMELINE_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)

    header = f"""[Script Info]
Title: 2025 New Gaokao II Q14 Subtitles
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
    highlight_ids = {5, 8, 10, 12, 13, 16, 17, 20, 21, 22, 23, 24}
    lines = [header]

    # 【核心校准】：master_audio.mp3 是紧密首尾相连拼接的（总时长 160.968s）
    # 从 0.0s 开始紧密累加真实持续时间，并赋予 -0.25s 提前量
    current_audio_time = 0.0

    calibrated_cues = []
    for c in meta["cues"]:
        dur = c["duration"]
        actual_start = current_audio_time
        actual_end = current_audio_time + dur

        # 注入提前量：早出 0.25s，晚收 0.10s
        sub_start = max(0.0, actual_start - LEAD_IN_BIAS)
        sub_end = actual_end + TRAIL_OUT_BIAS

        t_start_str = format_ass_time(sub_start)
        t_end_str = format_ass_time(sub_end)
        style = "Highlight" if c["id"] in highlight_ids else "Default"
        sub_text = c["subtitle"].replace("\n", "\\N")
        lines.append(f"Dialogue: 0,{t_start_str},{t_end_str},{style},,0,0,0,,{sub_text}\n")

        # 记录校准后数据
        c["start_time"] = actual_start
        c["end_time"] = actual_end
        calibrated_cues.append(c)

        current_audio_time = actual_end

    # 保存校准后的 ASS 字幕
    with open(ASS_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"Generated Calibrated ASS subtitle (Lead-in={LEAD_IN_BIAS}s): {ASS_PATH}")

    # 同时更新 audio_timeline.json
    meta["total_duration"] = current_audio_time
    meta["cues"] = calibrated_cues
    with open(TIMELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"Updated {TIMELINE_FILE} with actual audio timeline ({current_audio_time:.2f}s).")

def burn_subtitles():
    # 1. 确保纯净版视频存在
    if not os.path.exists(CLEAN_VIDEO) and os.path.exists(ORIGINAL_VIDEO):
        shutil.copyfile(ORIGINAL_VIDEO, CLEAN_VIDEO)
        print(f"Backed up clean video to: {CLEAN_VIDEO}")

    # 2. 重新校准并生成带提前量的 ASS 字幕
    calibrate_and_generate_ass()

    # 3. 烧录硬字幕
    tmp_out = os.path.join(BASE_DIR, "tmp_part1_subtitled.mp4")
    escaped_ass = ASS_PATH.replace("\\", "/").replace(":", "\\:")
    escaped_fonts = FONTS_DIR.replace("\\", "/").replace(":", "\\:")
    vf_filter = f"ass='{escaped_ass}':fontsdir='{escaped_fonts}'"

    cmd = [
        "ffmpeg", "-y",
        "-i", CLEAN_VIDEO,
        "-vf", vf_filter,
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "fast",
        "-c:a", "copy",
        tmp_out
    ]
    print("Running FFmpeg burn command for Part 1...")
    subprocess.run(cmd, check=True)

    if os.path.exists(FINAL_SUB_VIDEO):
        os.remove(FINAL_SUB_VIDEO)
    shutil.move(tmp_out, FINAL_SUB_VIDEO)
    print(f"Part 1 Subtitle Burn Success! Saved to: {FINAL_SUB_VIDEO}")

if __name__ == "__main__":
    burn_subtitles()
