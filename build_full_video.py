import os
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = r"X:\字体\霞鹜文楷LXGW_WenKai\lxgw-wenkai-v1.520"

VIDEO_PART1 = os.path.join(BASE_DIR, "render_2025_new_gaokao_2_q14_v2.mp4")
VIDEO_PART2 = os.path.join(BASE_DIR, "render_2025_new_gaokao_2_q14_part2_proof.mp4")

INTRO1_VIDEO = os.path.join(BASE_DIR, "intro_part1.mp4")
INTRO2_VIDEO = os.path.join(BASE_DIR, "intro_part2.mp4")
FINAL_FULL_VIDEO = os.path.join(BASE_DIR, "render_2025_new_gaokao_2_q14_full.mp4")

def generate_intro_ass(ass_path, title, subtitle, title_color="&H0070D0F7", sub_color="&H00B0C94E"):
    # 生成画面绝对正中央居中对齐的片头字幕 (Alignment=5)
    # \fad(500,500) 实现 0.5s 淡入与 0.5s 淡出
    content = f"""[Script Info]
Title: Intro Card
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TitleStyle,LXGW WenKai Medium,42,{title_color},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2.0,1.0,5,30,30,0,1
Style: SubStyle,LXGW WenKai,24,{sub_color},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,1.5,0.8,5,30,30,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:03.50,TitleStyle,,0,0,0,,{{\\fad(500,500)\\pos(640,320)}}{title}
Dialogue: 0,0:00:00.00,0:00:03.50,SubStyle,,0,0,0,,{{\\fad(500,500)\\pos(640,410)}}{subtitle}
"""
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated intro ASS: {ass_path}")

def make_intro_clip(out_mp4, ass_path, duration=3.5):
    escaped_ass = ass_path.replace("\\", "/").replace(":", "\\:")
    escaped_fonts = FONTS_DIR.replace("\\", "/").replace(":", "\\:")
    vf_filter = f"ass='{escaped_ass}':fontsdir='{escaped_fonts}'"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=#0c1017:s=1280x720:r=30:d={duration}",
        "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
        "-vf", vf_filter,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "fast",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        out_mp4
    ]
    subprocess.run(cmd, check=True)
    print(f"Created intro clip: {out_mp4}")

def build_full():
    print("=== Step 1: Generating Intro Clips with Centered LXGW Subtitles ===")
    ass_intro1 = os.path.join(BASE_DIR, "intro1.ass")
    generate_intro_ass(
        ass_intro1,
        title="2025年新高考全国II卷 · 第14题",
        subtitle="【第一部 · 三维几何与空间探索】",
        title_color="&H0070D0F7",  # 金色
        sub_color="&H00B0C94E"    # 青色
    )
    make_intro_clip(INTRO1_VIDEO, ass_intro1, duration=3.5)

    ass_intro2 = os.path.join(BASE_DIR, "intro2.ass")
    generate_intro_ass(
        ass_intro2,
        title="第二部 · 空间建系与严格证明",
        subtitle="【直觉发现上限 · 代数定理锁定极值】",
        title_color="&H00B0C94E",  # 青色
        sub_color="&H0070D0F7"    # 金色
    )
    make_intro_clip(INTRO2_VIDEO, ass_intro2, duration=3.5)

    print("\n=== Step 2: Concatenating All Parts into Master Film ===")
    # 使用 FFmpeg 的 filter_complex concat，确保音视频时间戳绝对平滑连贯
    # 输入0: INTRO1, 输入1: VIDEO_PART1, 输入2: INTRO2, 输入3: VIDEO_PART2
    tmp_full = os.path.join(BASE_DIR, "tmp_full.mp4")
    cmd_concat = [
        "ffmpeg", "-y",
        "-i", INTRO1_VIDEO,
        "-i", VIDEO_PART1,
        "-i", INTRO2_VIDEO,
        "-i", VIDEO_PART2,
        "-filter_complex",
        "[0:v][0:a][1:v][1:a][2:v][2:a][3:v][3:a]concat=n=4:v=1:a=1[v][a]",
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        tmp_full
    ]
    print("Running FFmpeg concat pipeline...")
    subprocess.run(cmd_concat, check=True)

    if os.path.exists(FINAL_FULL_VIDEO):
        os.remove(FINAL_FULL_VIDEO)
    shutil.move(tmp_full, FINAL_FULL_VIDEO)
    print(f"\n🎉 ALL SUCCESS! Master video created at: {FINAL_FULL_VIDEO}")

if __name__ == "__main__":
    build_full()
