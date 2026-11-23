import os
import json
import manimpango
from manim import *
import numpy as np

# 基础目录与配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TIMELINE_FILE = os.path.join(BASE_DIR, "audio_timeline_part2.json")
config.media_dir = os.path.join(BASE_DIR, "media")
config.disable_caching = True

# 注册霞鹜文楷字体
FONT_PATH = r"X:\字体\霞鹜文楷LXGW_WenKai\lxgw-wenkai-v1.520\LXGWWenKai-Regular.ttf"
FONT_BOLD_PATH = r"X:\字体\霞鹜文楷LXGW_WenKai\lxgw-wenkai-v1.520\LXGWWenKai-Medium.ttf"
if os.path.exists(FONT_PATH):
    manimpango.register_font(FONT_PATH)
if os.path.exists(FONT_BOLD_PATH):
    manimpango.register_font(FONT_BOLD_PATH)

FONT = "LXGW WenKai"

# 色彩体系
COLOR_BG = "#0c1017"
COLOR_GOLD = "#F7D070"
COLOR_CYAN = "#4EC9B0"
COLOR_BLUE = "#58A6FF"
COLOR_PURPLE = "#BC8CFF"
COLOR_RED = "#FF7B72"
COLOR_GREEN = "#7EE787"
COLOR_ORANGE = "#FFA657"
COLOR_WHITE = "#EDEDED"
COLOR_GRAY = "#8B949E"
COLOR_CARD_BG = "#161B22"
COLOR_CARD_BORDER = "#30363D"

class MathProofPart2(Scene):
    def construct(self):
        # 1. 设置画布背景
        self.camera.background_color = COLOR_BG

        # 2. 读取音频时间轴
        with open(TIMELINE_FILE, "r", encoding="utf-8") as f:
            meta = json.load(f)
        cues = meta["cues"]

        # 3. 顶部 HUD 导航卡片
        hud_bg = RoundedRectangle(
            corner_radius=0.15, width=13.6, height=1.0,
            fill_color=COLOR_CARD_BG, fill_opacity=0.98,
            stroke_color=COLOR_CARD_BORDER, stroke_width=1.5
        ).to_edge(UP, buff=0.2)

        hud_title = Text("2025新高考II卷 · 第14题 · 严格数学证明篇", font=FONT, font_size=20, weight=BOLD, color=COLOR_GOLD)
        hud_sub = Text("空间直角坐标系与不等式链 · 证明 r ≤ 2.5 cm 的全局不可逾越性", font=FONT, font_size=13, color=COLOR_GRAY)
        hud_text = VGroup(hud_title, hud_sub).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        hud_text.next_to(hud_bg.get_left(), RIGHT, buff=0.5)

        # 章节指示标签
        chapter_badge_bg = RoundedRectangle(corner_radius=0.1, width=3.2, height=0.55, fill_color="#21262D", fill_opacity=1.0, stroke_color=COLOR_CYAN, stroke_width=1.2)
        chapter_badge_text = Text("第1幕 · 灵魂发问", font=FONT, font_size=14, color=COLOR_CYAN).move_to(chapter_badge_bg)
        chapter_badge = VGroup(chapter_badge_bg, chapter_badge_text).next_to(hud_bg.get_right(), LEFT, buff=0.5)

        hud_group = VGroup(hud_bg, hud_text, chapter_badge)
        self.add(hud_group)

        # 辅助播放函数：严格与 cue 毫秒级对齐
        def play_cue(cue_id, *anims, anim_duration=None):
            cue = cues[cue_id - 1]
            dur = cue["duration"]
            if anims:
                if anim_duration is not None:
                    ad = min(dur, anim_duration)
                else:
                    ad = min(dur * 0.75, 2.5)
                self.play(*anims, run_time=ad)
                rem = dur - ad
                if rem > 0.001:
                    self.wait(rem)
            else:
                self.wait(dur)
            # 补齐句间间隙 0.25s
            if cue_id < len(cues):
                self.wait(0.25)

        # 动态切幕函数
        def switch_badge(new_text, color=COLOR_CYAN):
            new_t = Text(new_text, font=FONT, font_size=14, color=color).move_to(chapter_badge_bg)
            return Transform(chapter_badge_text, new_t), chapter_badge_bg.animate.set_stroke(color=color)

        # =====================================================================
        # 第一乐章：灵魂发问与直观质疑 (Cues 1 ~ 4, ~28s)
        # =====================================================================
        left_card = RoundedRectangle(
            corner_radius=0.15, width=5.6, height=4.5,
            fill_color=COLOR_CARD_BG, fill_opacity=0.9,
            stroke_color=COLOR_GOLD, stroke_width=1.5
        ).shift(LEFT * 3.4 + DOWN * 0.6)

        left_title = Text("【三维直观探索：相切临界态】", font=FONT, font_size=16, color=COLOR_GOLD, weight=BOLD)
        
        cyl_top = Ellipse(width=3.2, height=1.0, color=COLOR_BLUE, stroke_width=2).shift(LEFT * 3.4 + UP * 0.4)
        cyl_bottom = Ellipse(width=3.2, height=1.0, color=COLOR_BLUE, stroke_width=2).shift(LEFT * 3.4 + DOWN * 1.6)
        cyl_l = Line(cyl_top.get_left(), cyl_bottom.get_left(), color=COLOR_BLUE, stroke_width=2)
        cyl_r = Line(cyl_top.get_right(), cyl_bottom.get_right(), color=COLOR_BLUE, stroke_width=2)
        
        ball1 = Circle(radius=0.85, color=COLOR_GOLD, fill_color=COLOR_GOLD, fill_opacity=0.3, stroke_width=2).shift(LEFT * 4.0 + DOWN * 1.2)
        ball2 = Circle(radius=0.85, color=COLOR_CYAN, fill_color=COLOR_CYAN, fill_opacity=0.3, stroke_width=2).shift(LEFT * 2.8 + UP * 0.0)
        tan_line = Line(ball1.get_center(), ball2.get_center(), color=COLOR_WHITE, stroke_width=2)
        lbl_r25 = Text("两球对角相切: r = 2.5 cm", font=FONT, font_size=14, color=COLOR_GOLD).next_to(cyl_bottom, DOWN, buff=0.15)
        
        left_schematic = VGroup(cyl_top, cyl_bottom, cyl_l, cyl_r, ball1, ball2, tan_line, lbl_r25)
        left_title.next_to(left_schematic, UP, buff=0.2)
        left_view = VGroup(left_card, left_title, left_schematic)

        # 右侧质疑卡片
        doubt_card = RoundedRectangle(
            corner_radius=0.15, width=6.2, height=4.5,
            fill_color=COLOR_CARD_BG, fill_opacity=0.9,
            stroke_color=COLOR_RED, stroke_width=1.5
        ).shift(RIGHT * 3.3 + DOWN * 0.6)

        doubt_t1 = Text("【直觉探索的局限性】", font=FONT, font_size=18, color=COLOR_RED, weight=BOLD)
        doubt_t2 = Text("• 3D动画中找到了对角外切构型：r = 2.5 cm", font=FONT, font_size=15, color=COLOR_WHITE)
        doubt_t3 = Text("• 质疑：这只是我们选定的一种对称摆法！", font=FONT, font_size=15, color=COLOR_ORANGE)
        doubt_t4 = Text("• 追问：是否存在某种极其刁钻的非对称姿态，\n  能塞下 r = 2.51 cm 的球？", font=FONT, font_size=15, color=COLOR_GOLD)
        doubt_weapon = Text("终极武器：不等式链压榨证明！", font=FONT, font_size=17, color=COLOR_CYAN, weight=BOLD)

        doubt_lines = VGroup(doubt_t1, doubt_t2, doubt_t3, doubt_t4, doubt_weapon).arrange(DOWN, aligned_edge=LEFT, buff=0.32).move_to(doubt_card)
        right_view = VGroup(doubt_card, doubt_lines)

        # Cue 1: 刚才在三维动画里，找到了相切形态...
        play_cue(1, FadeIn(left_view, shift=RIGHT * 0.3), anim_duration=2.0)

        # Cue 2: 但这只是对称摆法，凭什么全局最大？
        play_cue(2, FadeIn(doubt_card), Write(doubt_t1), Write(doubt_t2), Write(doubt_t3), anim_duration=3.0)

        # Cue 3: 万一有刁钻姿势能塞下 2.51cm 呢？
        play_cue(3, Write(doubt_t4), anim_duration=3.0)

        # Cue 4: 今天请出数学核武器——不等式链！
        weapon_box = SurroundingRectangle(doubt_weapon, color=COLOR_CYAN, stroke_width=2, buff=0.1)
        play_cue(4, FadeIn(doubt_weapon, shift=UP * 0.2), Create(weapon_box), anim_duration=2.5)

        # 清理 Scene 1 元素
        self.play(FadeOut(left_view), FadeOut(right_view), FadeOut(weapon_box), run_time=1.0)
        self.wait(0.2)

        # =====================================================================
        # 第二乐章：规范建系与符号约定 (Cues 5 ~ 9, ~28s) [新增乐章]
        # =====================================================================
        t_badge, b_badge = switch_badge("第2幕 · 空间建系与符号", COLOR_CYAN)
        self.play(t_badge, b_badge, run_time=0.6)

        # 左侧：空间直角坐标系轴测图
        origin_pt = LEFT * 3.6 + DOWN * 1.5
        
        # 三轴箭头
        axis_x = Arrow(origin_pt, origin_pt + np.array([2.0, -0.6, 0]), color=COLOR_RED, buff=0, stroke_width=3)
        axis_y = Arrow(origin_pt, origin_pt + np.array([2.0, 0.7, 0]), color=COLOR_GREEN, buff=0, stroke_width=3)
        axis_z = Arrow(origin_pt, origin_pt + np.array([0, 3.2, 0]), color=COLOR_BLUE, buff=0, stroke_width=3)
        
        lbl_x = Text("x", font=FONT, font_size=15, color=COLOR_RED).next_to(axis_x.get_end(), DOWN, buff=0.08)
        lbl_y = Text("y", font=FONT, font_size=15, color=COLOR_GREEN).next_to(axis_y.get_end(), UP, buff=0.08)
        lbl_z = Text("z (轴线)", font=FONT, font_size=15, color=COLOR_BLUE).next_to(axis_z.get_end(), UP, buff=0.08)
        dot_o = Dot(origin_pt, color=COLOR_GOLD, radius=0.09)
        lbl_o = Text("O(0,0,0)", font=FONT, font_size=13, color=COLOR_GOLD).next_to(dot_o, DL, buff=0.08)

        # 圆柱轮廓透视
        cyl_base_ell = Ellipse(width=3.6, height=1.3, color=COLOR_GRAY, stroke_width=1.5).move_to(origin_pt)
        cyl_top_ell = Ellipse(width=3.6, height=1.3, color=COLOR_GRAY, stroke_width=1.5).move_to(origin_pt + UP * 2.6)
        cyl_side_l = Line(cyl_base_ell.get_left(), cyl_top_ell.get_left(), color=COLOR_GRAY, stroke_width=1.5)
        cyl_side_r = Line(cyl_base_ell.get_right(), cyl_top_ell.get_right(), color=COLOR_GRAY, stroke_width=1.5)

        # 空间两球心及垂足
        # O1 下球心，O2 上球心
        pt_o1 = origin_pt + np.array([-0.6, 0.3, 0]) + UP * 0.7
        pt_p1 = origin_pt + np.array([-0.6, 0.3, 0])   # 投影到底面
        pt_o2 = origin_pt + np.array([0.7, -0.2, 0]) + UP * 2.0
        pt_p2 = origin_pt + np.array([0.7, -0.2, 0])   # 投影到底面

        dot_o1 = Dot(pt_o1, color=COLOR_GOLD, radius=0.09)
        lbl_o1 = Text("O₁(x₁,y₁,z₁)", font=FONT, font_size=12, color=COLOR_GOLD).next_to(dot_o1, LEFT, buff=0.06)
        dot_p1 = Dot(pt_p1, color=COLOR_GOLD, radius=0.07)
        lbl_p1 = Text("P₁", font=FONT, font_size=11, color=COLOR_GOLD).next_to(dot_p1, DOWN, buff=0.05)
        line_proj1 = DashedLine(pt_o1, pt_p1, color=COLOR_GOLD, stroke_width=1.5)

        dot_o2 = Dot(pt_o2, color=COLOR_CYAN, radius=0.09)
        lbl_o2 = Text("O₂(x₂,y₂,z₂)", font=FONT, font_size=12, color=COLOR_CYAN).next_to(dot_o2, RIGHT, buff=0.06)
        dot_p2 = Dot(pt_p2, color=COLOR_CYAN, radius=0.07)
        lbl_p2 = Text("P₂", font=FONT, font_size=11, color=COLOR_CYAN).next_to(dot_p2, DOWN, buff=0.05)
        line_proj2 = DashedLine(pt_o2, pt_p2, color=COLOR_CYAN, stroke_width=1.5)

        # 空间距离 L 与水平跨度 Δρ 连线
        line_l = Line(pt_o1, pt_o2, color=COLOR_WHITE, stroke_width=2.5)
        lbl_l = Text("球心距 L", font=FONT, font_size=12, color=COLOR_WHITE).next_to(line_l.get_center(), UP, buff=0.05)
        line_delta = DashedLine(pt_p1, pt_p2, color=COLOR_GOLD, stroke_width=2.0)
        lbl_delta = Text("Δρ", font=FONT, font_size=11, color=COLOR_GOLD).next_to(line_delta.get_center(), DOWN, buff=0.05)

        axes_3d_group = VGroup(
            cyl_base_ell, cyl_top_ell, cyl_side_l, cyl_side_r,
            axis_x, axis_y, axis_z, lbl_x, lbl_y, lbl_z, dot_o, lbl_o,
            dot_o1, lbl_o1, dot_p1, lbl_p1, line_proj1,
            dot_o2, lbl_o2, dot_p2, lbl_p2, line_proj2,
            line_l, lbl_l, line_delta, lbl_delta
        )

        # 右侧：空间直角坐标系与符号定义卡片
        coord_card = RoundedRectangle(
            corner_radius=0.15, width=6.5, height=4.8,
            fill_color=COLOR_CARD_BG, fill_opacity=0.92,
            stroke_color=COLOR_CYAN, stroke_width=1.5
        ).shift(RIGHT * 3.3 + DOWN * 0.5)

        cc_title = Text("【空间直角坐标系与符号约定】", font=FONT, font_size=17, color=COLOR_CYAN, weight=BOLD)
        
        cc_sec1 = Text("1. 空间基准坐标系：", font=FONT, font_size=14, color=COLOR_WHITE, weight=BOLD)
        cc_t1_1 = Text("• 原点 O(0,0,0)：圆柱底面中心", font=FONT, font_size=13, color=COLOR_WHITE)
        cc_t1_2 = Text("• xOy 平面：包含底面圆，x 轴与 y 轴互相垂直", font=FONT, font_size=13, color=COLOR_WHITE)
        cc_t1_3 = Text("• z 轴：沿圆柱中心对称轴竖直向上", font=FONT, font_size=13, color=COLOR_BLUE)

        cc_sec2 = Text("2. 容器解析约束：", font=FONT, font_size=14, color=COLOR_WHITE, weight=BOLD)
        cc_f2 = MathTex(r"x^2 + y^2 \le R^2 = 16, \quad 0 \le z \le H = 9", font_size=17, color=COLOR_GOLD)

        cc_sec3 = Text("3. 几何符号与变量定义：", font=FONT, font_size=14, color=COLOR_WHITE, weight=BOLD)
        cc_t3_1 = Text("• R = 4 (底面半径), H = 9 (容器高), r (铁球半径)", font=FONT, font_size=13, color=COLOR_GRAY)
        cc_t3_2 = Text("• O₁(x₁,y₁,z₁), O₂(x₂,y₂,z₂)：两球的球心空间坐标", font=FONT, font_size=13, color=COLOR_WHITE)
        cc_t3_3 = Text("• P₁, P₂：两球心在底面 xOy 的垂直投影点", font=FONT, font_size=13, color=COLOR_WHITE)
        cc_t3_4 = Text("• Δρ：水平跨度； Δz：垂直高差； L：球心距", font=FONT, font_size=13, color=COLOR_GOLD)

        coord_content = VGroup(
            cc_title,
            cc_sec1, cc_t1_1, cc_t1_2, cc_t1_3,
            cc_sec2, cc_f2,
            cc_sec3, cc_t3_1, cc_t3_2, cc_t3_3, cc_t3_4
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(coord_card)

        # Cue 5: 进行严格证明的第一步，必须规范建立空间直角坐标系！
        play_cue(5, FadeIn(coord_card), Write(cc_title), FadeIn(VGroup(cyl_base_ell, cyl_top_ell, cyl_side_l, cyl_side_r)), anim_duration=2.2)

        # Cue 6: 以底面圆心为原点 O，x 与 y 垂直，中心轴为 z 轴
        play_cue(6,
            Create(axis_x), Create(axis_y), Create(axis_z),
            FadeIn(lbl_x), FadeIn(lbl_y), FadeIn(lbl_z), FadeIn(dot_o), FadeIn(lbl_o),
            FadeIn(cc_sec1), Write(cc_t1_1), Write(cc_t1_2), Write(cc_t1_3),
            anim_duration=3.5
        )

        # Cue 7: 圆柱容器解析方程为 x²+y²≤16, 0≤z≤9
        play_cue(7, FadeIn(cc_sec2), Write(cc_f2), anim_duration=2.2)

        # Cue 8: 设两球心坐标为 O1, O2，底面投影点为 P1, P2
        play_cue(8,
            FadeIn(dot_o1), FadeIn(lbl_o1), Create(line_proj1), FadeIn(dot_p1), FadeIn(lbl_p1),
            FadeIn(dot_o2), FadeIn(lbl_o2), Create(line_proj2), FadeIn(dot_p2), FadeIn(lbl_p2),
            FadeIn(cc_sec3), Write(cc_t3_1), Write(cc_t3_2), Write(cc_t3_3),
            anim_duration=3.0
        )

        # Cue 9: 水平跨度为 Δρ，垂直高差为 Δz，球心距为 L。代数武器启动！
        play_cue(9,
            Create(line_l), FadeIn(lbl_l), Create(line_delta), FadeIn(lbl_delta),
            Write(cc_t3_4),
            anim_duration=2.8
        )

        # 清除第 2 幕元素
        self.play(FadeOut(axes_3d_group), FadeOut(coord_card), FadeOut(coord_content), run_time=0.8)
        self.wait(0.2)

        # =====================================================================
        # 第三乐章：水平压榨·底面圆盘几何极值 (Cues 10 ~ 13, ~30s)
        # =====================================================================
        t_badge, b_badge = switch_badge("第3幕 · 水平极值压榨", COLOR_BLUE)
        self.play(t_badge, b_badge, run_time=0.6)

        center_disk = LEFT * 3.4 + DOWN * 0.5
        R_outer = 2.4   # 代表 R = 4cm
        r_ball = 1.0    # 示意 r

        circle_outer = Circle(radius=R_outer, color=COLOR_GRAY, stroke_width=2.5).move_to(center_disk)
        circle_outer_label = Text("容器底面 (R = 4)", font=FONT, font_size=14, color=COLOR_GRAY).next_to(circle_outer, UP, buff=0.15)

        R_inner = R_outer - r_ball
        circle_inner = Circle(radius=R_inner, color=COLOR_BLUE, stroke_width=3.0).move_to(center_disk)
        circle_inner_fill = Circle(radius=R_inner, fill_color=COLOR_BLUE, fill_opacity=0.15, stroke_width=0).move_to(center_disk)
        circle_inner_label = Text("球心投影安全域 (半径 4 - r)", font=FONT, font_size=13, color=COLOR_BLUE).next_to(circle_inner, DOWN, buff=0.15)

        dot_p1_d = Dot(point=center_disk + np.array([-0.6, 0.4, 0]), color=COLOR_GOLD, radius=0.1)
        dot_p2_d = Dot(point=center_disk + np.array([0.7, -0.3, 0]), color=COLOR_GOLD, radius=0.1)
        lbl_p1_d = Text("P₁(x₁,y₁)", font=FONT, font_size=13, color=COLOR_GOLD).next_to(dot_p1_d, UP, buff=0.08)
        lbl_p2_d = Text("P₂(x₂,y₂)", font=FONT, font_size=13, color=COLOR_GOLD).next_to(dot_p2_d, DOWN, buff=0.08)
        line_delta_rho = Line(dot_p1_d.get_center(), dot_p2_d.get_center(), color=COLOR_GOLD, stroke_width=2.5)

        disk_group = VGroup(circle_outer, circle_outer_label, circle_inner, circle_inner_fill, circle_inner_label)
        points_group = VGroup(dot_p1_d, dot_p2_d, lbl_p1_d, lbl_p2_d, line_delta_rho)

        calc_card = RoundedRectangle(
            corner_radius=0.15, width=6.3, height=4.8,
            fill_color=COLOR_CARD_BG, fill_opacity=0.9,
            stroke_color=COLOR_CARD_BORDER, stroke_width=1.5
        ).shift(RIGHT * 3.3 + DOWN * 0.5)

        c2_t1 = Text("【维度一：水平几何极值】", font=FONT, font_size=18, color=COLOR_BLUE, weight=BOLD)
        c2_t2 = Text("1. 球体在圆柱内：球心距侧壁 ≥ r", font=FONT, font_size=15, color=COLOR_WHITE)
        c2_f1 = MathTex(r"\sqrt{x_i^2 + y_i^2} \le R - r = 4 - r", font_size=18, color=COLOR_CYAN)
        c2_t3 = Text("2. 球心投影 P₁, P₂ 落在半径 4 - r 圆盘内。", font=FONT, font_size=15, color=COLOR_WHITE)
        c2_t4 = Text("3. 圆盘内两点最大距离为直径：", font=FONT, font_size=15, color=COLOR_WHITE)
        c2_f2 = MathTex(r"\Delta \rho = \sqrt{(x_1 - x_2)^2 + (y_1 - y_2)^2} \le 2(4 - r)", font_size=18, color=COLOR_GOLD)
        c2_res = MathTex(r"\mathbf{\Delta \rho \le 8 - 2r}", font_size=23, color=COLOR_GOLD)
        c2_box = SurroundingRectangle(c2_res, color=COLOR_GOLD, stroke_width=2, buff=0.1)

        c2_group = VGroup(c2_t1, c2_t2, c2_f1, c2_t3, c2_t4, c2_f2, VGroup(c2_res, c2_box)).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(calc_card)

        # Cue 10: 首先考察水平维度，球心距侧壁至少为 r
        play_cue(10, FadeIn(calc_card), FadeIn(disk_group), Write(c2_t1), Write(c2_t2), Write(c2_f1), anim_duration=2.5)

        # Cue 11: 这意味着 P1 和 P2 只能活动在 4-r 的同心圆盘内
        play_cue(11, FadeIn(points_group), Write(c2_t3), anim_duration=2.5)

        # Cue 12: 圆盘内两点最大距离绝不超过直径
        target_p1 = center_disk + np.array([-R_inner, 0, 0])
        target_p2 = center_disk + np.array([R_inner, 0, 0])
        max_line = Line(target_p1, target_p2, color=COLOR_GOLD, stroke_width=3.5)
        lbl_diam = Text("最大跨度 = 直径 2(4-r)", font=FONT, font_size=13, color=COLOR_GOLD).next_to(max_line, UP, buff=0.1)

        play_cue(12,
            dot_p1_d.animate.move_to(target_p1),
            dot_p2_d.animate.move_to(target_p2),
            lbl_p1_d.animate.next_to(target_p1, LEFT, buff=0.1),
            lbl_p2_d.animate.next_to(target_p2, RIGHT, buff=0.1),
            Transform(line_delta_rho, max_line),
            FadeIn(lbl_diam),
            Write(c2_t4), Write(c2_f2),
            anim_duration=3.5
        )

        # Cue 13: 因此 Δρ ≤ 8 - 2r！
        play_cue(13, FadeIn(c2_res), Create(c2_box), anim_duration=2.0)

        # 淡出水平几何，切换到竖直
        self.play(
            FadeOut(disk_group), FadeOut(points_group), FadeOut(lbl_diam),
            calc_card.animate.scale(0.85).shift(LEFT * 5.8 + DOWN * 0.2),
            c2_group.animate.scale(0.85).shift(LEFT * 5.8 + DOWN * 0.2),
            run_time=1.0
        )

        # =====================================================================
        # 第四乐章：竖直压榨·容器高度的绝对限制 (Cues 14 ~ 17, ~28s)
        # =====================================================================
        t_badge, b_badge = switch_badge("第4幕 · 竖直极值压榨", COLOR_PURPLE)
        self.play(t_badge, b_badge, run_time=0.6)

        z_axis_center = RIGHT * 0.8 + DOWN * 0.5
        z_axis = NumberLine(
            x_range=[0, 9, 1], length=4.5, color=COLOR_GRAY,
            include_numbers=True, font_size=14, rotation=90 * DEGREES
        ).move_to(z_axis_center)
        z_lbl = Text("高度 Z (0 ~ 9)", font=FONT, font_size=14, color=COLOR_GRAY).next_to(z_axis, UP, buff=0.15)

        z_valid_bar = Line(
            z_axis.number_to_point(1.2), z_axis.number_to_point(9 - 1.2),
            color=COLOR_PURPLE, stroke_width=6
        )
        z_r_min = Dot(z_axis.number_to_point(1.2), color=COLOR_PURPLE, radius=0.1)
        z_r_max = Dot(z_axis.number_to_point(9 - 1.2), color=COLOR_PURPLE, radius=0.1)
        lbl_z_min = Text("下限: r", font=FONT, font_size=13, color=COLOR_PURPLE).next_to(z_r_min, LEFT, buff=0.1)
        lbl_z_max = Text("上限: 9 - r", font=FONT, font_size=13, color=COLOR_PURPLE).next_to(z_r_max, LEFT, buff=0.1)

        z_view = VGroup(z_axis, z_lbl, z_valid_bar, z_r_min, z_r_max, lbl_z_min, lbl_z_max)

        z_card = RoundedRectangle(
            corner_radius=0.15, width=4.8, height=4.8,
            fill_color=COLOR_CARD_BG, fill_opacity=0.9,
            stroke_color=COLOR_PURPLE, stroke_width=1.5
        ).shift(RIGHT * 4.3 + DOWN * 0.5)

        c3_t1 = Text("【维度二：竖直高度极值】", font=FONT, font_size=17, color=COLOR_PURPLE, weight=BOLD)
        c3_t2 = Text("1. 竖直方向活动区间限制：", font=FONT, font_size=14, color=COLOR_WHITE)
        c3_f1 = MathTex(r"r \le z_1, z_2 \le 9 - r", font_size=18, color=COLOR_CYAN)
        c3_t3 = Text("2. 有效区间长度只有 9 - 2r。", font=FONT, font_size=14, color=COLOR_WHITE)
        c3_t4 = Text("3. 两端贴满时高差取得最大：", font=FONT, font_size=14, color=COLOR_WHITE)
        c3_res = MathTex(r"\mathbf{\Delta z \le 9 - 2r}", font_size=23, color=COLOR_PURPLE)
        c3_box = SurroundingRectangle(c3_res, color=COLOR_PURPLE, stroke_width=2, buff=0.1)

        c3_group = VGroup(c3_t1, c3_t2, c3_f1, c3_t3, c3_t4, VGroup(c3_res, c3_box)).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(z_card)

        # Cue 14: 再看竖直方向，下球心不低于 r，上球心不高于 9-r
        play_cue(14, FadeIn(z_view), FadeIn(z_card), Write(c3_t1), Write(c3_t2), Write(c3_f1), anim_duration=2.5)

        # Cue 15: 整个竖直区间只有 9-2r，两端贴满时高差达到极限！
        delta_z_arrow = DoubleArrow(
            z_axis.number_to_point(1.2), z_axis.number_to_point(9 - 1.2),
            color=COLOR_GOLD, buff=0, stroke_width=3
        ).shift(RIGHT * 0.4)
        lbl_delta_z = Text("最大高差 Δz", font=FONT, font_size=13, color=COLOR_GOLD).next_to(delta_z_arrow, RIGHT, buff=0.1)
        play_cue(15, Create(delta_z_arrow), FadeIn(lbl_delta_z), Write(c3_t3), anim_duration=2.5)

        # Cue 16: 所以 Δz 必然 ≤ 9 - 2r！
        play_cue(16, Write(c3_t4), FadeIn(c3_res), Create(c3_box), anim_duration=2.0)

        # Cue 17: 圆柱外壳死死焊上物理天花板！
        play_cue(17, anim_duration=1.5)

        self.play(
            FadeOut(z_view), FadeOut(delta_z_arrow), FadeOut(lbl_delta_z),
            FadeOut(calc_card), FadeOut(c2_group),
            FadeOut(z_card), FadeOut(c3_group),
            run_time=0.8
        )

        # =====================================================================
        # 第五乐章：空间不等式链绝杀 (Cues 18 ~ 22, ~36s)
        # =====================================================================
        t_badge, b_badge = switch_badge("第5幕 · 空间不等式链绝杀", COLOR_GOLD)
        self.play(t_badge, b_badge, run_time=0.6)

        proof_card = RoundedRectangle(
            corner_radius=0.15, width=12.2, height=5.0,
            fill_color=COLOR_CARD_BG, fill_opacity=0.95,
            stroke_color=COLOR_GOLD, stroke_width=2.0
        ).shift(DOWN * 0.5)

        p_t0 = Text("【两维合一 · 空间勾股定理与不等式夹逼】", font=FONT, font_size=19, color=COLOR_GOLD, weight=BOLD)
        p_f1 = MathTex(r"L^2 = |O_1 - O_2|^2 = \Delta \rho^2 + \Delta z^2", font_size=24, color=COLOR_WHITE)

        p_t1 = Text("由外壳约束（几何上限）：", font=FONT, font_size=15, color=COLOR_BLUE)
        p_f2 = MathTex(r"L^2 \le (8 - 2r)^2 + (9 - 2r)^2", font_size=24, color=COLOR_BLUE)

        p_t2 = Text("由实体独立约束（物理下限）：两球互不相交，球心距必须大于等于 2r", font=FONT, font_size=15, color=COLOR_ORANGE)
        p_f3 = MathTex(r"L^2 \ge (2r)^2 = 4r^2", font_size=24, color=COLOR_ORANGE)

        p_final = MathTex(
            r"\mathbf{(2r)^2 \le L^2 \le (8 - 2r)^2 + (9 - 2r)^2}",
            font_size=28, color=COLOR_GOLD
        )
        p_final_box = SurroundingRectangle(p_final, color=COLOR_GOLD, stroke_width=2.5, buff=0.15)
        p_tag = Text("【终极代数不等式：消去所有位置坐标！】", font=FONT, font_size=16, color=COLOR_CYAN, weight=BOLD)

        chain_group = VGroup(
            p_t0, p_f1,
            VGroup(p_t1, p_f2).arrange(RIGHT, buff=0.4),
            VGroup(p_t2, p_f3).arrange(DOWN, aligned_edge=LEFT, buff=0.15),
            VGroup(p_final, p_final_box),
            p_tag
        ).arrange(DOWN, buff=0.26).move_to(proof_card)

        # Cue 18: 接下来是见证数学奇迹的高光时刻！
        play_cue(18, FadeIn(proof_card), Write(p_t0), anim_duration=2.0)

        # Cue 19: 空间两点距离公式 L² = Δρ² + Δz²
        play_cue(19, Write(p_f1), anim_duration=2.5)

        # Cue 20: 代入极值得 L² ≤ (8-2r)² + (9-2r)²
        play_cue(20, FadeIn(p_t1), Write(p_f2), anim_duration=2.8)

        # Cue 21: 另一方面，两球互不相交，球心距 L ≥ 2r！
        play_cue(21, FadeIn(p_t2), Write(p_f3), anim_duration=2.8)

        # Cue 22: 两头一夹，终极不等式链诞生！
        play_cue(22, FadeIn(p_final), Create(p_final_box), FadeIn(p_tag), anim_duration=3.5)

        # =====================================================================
        # 第六乐章：二次函数裁决·唯一的合法真理 (Cues 23 ~ 28, ~28s)
        # =====================================================================
        t_badge, b_badge = switch_badge("第6幕 · 二次函数裁决", COLOR_GREEN)
        self.play(t_badge, b_badge, run_time=0.6)

        # 彻底淡出第四幕所有的公式与大卡片
        self.play(
            FadeOut(proof_card), FadeOut(p_t0), FadeOut(p_f1), FadeOut(p_t1),
            FadeOut(p_f2), FadeOut(p_t2), FadeOut(p_f3), FadeOut(p_final),
            FadeOut(p_final_box), FadeOut(p_tag),
            run_time=0.8
        )

        eq_card = RoundedRectangle(
            corner_radius=0.15, width=5.6, height=4.4,
            fill_color=COLOR_CARD_BG, fill_opacity=0.9,
            stroke_color=COLOR_CARD_BORDER, stroke_width=1.5
        ).shift(LEFT * 3.4 + DOWN * 0.5)

        eq_t1 = Text("【代数化简与因式分解】", font=FONT, font_size=16, color=COLOR_GREEN, weight=BOLD)
        eq_l1 = MathTex(r"4r^2 \le (64 - 32r + 4r^2) + (81 - 36r + 4r^2)", font_size=16, color=COLOR_WHITE)
        eq_l2 = MathTex(r"4r^2 - 68r + 145 \ge 0", font_size=20, color=COLOR_CYAN)
        eq_l3 = MathTex(r"(2r - 5)(2r - 29) \ge 0", font_size=22, color=COLOR_GOLD)
        eq_l4 = MathTex(r"\implies r \le 2.5 \quad \text{or} \quad r \ge 14.5", font_size=20, color=COLOR_ORANGE)

        eq_group = VGroup(eq_t1, eq_l1, eq_l2, eq_l3, eq_l4).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(eq_card)

        axes = Axes(
            x_range=[0, 16, 2], y_range=[-120, 150, 100],
            x_length=5.6, y_length=3.2,
            axis_config={"color": COLOR_GRAY, "font_size": 12}
        ).shift(RIGHT * 3.3 + DOWN * 0.5)
        
        x_label = Text("r", font=FONT, font_size=15, color=COLOR_GRAY).next_to(axes.x_axis.get_end(), RIGHT, buff=0.1)
        y_label = Text("f(r)", font=FONT, font_size=15, color=COLOR_GRAY).next_to(axes.y_axis.get_end(), UP, buff=0.1)
        axes_labels = VGroup(x_label, y_label)

        parabola = axes.plot(lambda r: 4 * r**2 - 68 * r + 145, x_range=[0, 16], color=COLOR_CYAN, stroke_width=2.5)

        dot_r1 = Dot(axes.c2p(2.5, 0), color=COLOR_GREEN, radius=0.1)
        dot_r2 = Dot(axes.c2p(14.5, 0), color=COLOR_RED, radius=0.1)
        lbl_r1 = Text("r = 2.5", font=FONT, font_size=13, color=COLOR_GREEN).next_to(dot_r1, DOWN, buff=0.1)
        lbl_r2 = Text("r = 14.5", font=FONT, font_size=13, color=COLOR_RED).next_to(dot_r2, DOWN, buff=0.1)

        p_x0 = axes.c2p(0, 0)[0]
        p_x4 = axes.c2p(4, 0)[0]
        valid_zone = Rectangle(
            width=p_x4 - p_x0, height=2.8,
            fill_color=COLOR_GREEN, fill_opacity=0.15, stroke_width=0
        ).align_to(axes.c2p(0, 0), LEFT).shift(UP * 0.1)
        lbl_valid = Text("容器容积可行域 (r < 4)", font=FONT, font_size=12, color=COLOR_GREEN).next_to(valid_zone, UP, buff=0.08)

        cross_14 = Text("✖ 14.5 > 4 物理淘汰！", font=FONT, font_size=13, color=COLOR_RED, weight=BOLD).next_to(dot_r2, UP, buff=0.3)

        plot_group = VGroup(axes, axes_labels, parabola, dot_r1, dot_r2, lbl_r1, lbl_r2)

        # Cue 23: 展开化简一元二次不等式
        play_cue(23, FadeIn(eq_card), Write(eq_t1), Write(eq_l1), anim_duration=2.0)

        # Cue 24: 移项整理得 4r² - 68r + 145 ≥ 0
        play_cue(24, Write(eq_l2), anim_duration=2.0)

        # Cue 25: 因式分解 (2r - 5)(2r - 29) ≥ 0
        play_cue(25, Write(eq_l3), anim_duration=2.0)

        # Cue 26: 解得 r ≤ 2.5 或 r ≥ 14.5！
        play_cue(26, Write(eq_l4), FadeIn(plot_group), anim_duration=2.5)

        # Cue 27: 但底面半径为 4，r < 4，14.5 淘汰！
        play_cue(27, FadeIn(valid_zone), FadeIn(lbl_valid), FadeIn(cross_14), anim_duration=2.5)

        # Cue 28: 剩下的唯一可能：r ≤ 2.5 cm！
        res_stamp = RoundedRectangle(
            corner_radius=0.12, width=4.5, height=0.85,
            fill_color="#1F2A1E", fill_opacity=0.95,
            stroke_color=COLOR_GREEN, stroke_width=2.5
        ).shift(LEFT * 3.4 + DOWN * 2.2)
        res_stamp_text = Text("唯一解：r ≤ 2.5 cm", font=FONT, font_size=19, color=COLOR_GREEN, weight=BOLD).move_to(res_stamp)
        play_cue(28, FadeIn(res_stamp, shift=UP * 0.2), Write(res_stamp_text), anim_duration=2.2)

        # =====================================================================
        # 第七乐章：总结升华·直觉与代数的完美闭环 (Cues 29 ~ 30, ~16s)
        # =====================================================================
        t_badge, b_badge = switch_badge("第7幕 · 严格闭环结论", COLOR_GOLD)
        self.play(t_badge, b_badge, run_time=0.6)

        self.play(
            FadeOut(eq_card), FadeOut(eq_group), FadeOut(plot_group),
            FadeOut(valid_zone), FadeOut(lbl_valid), FadeOut(cross_14),
            FadeOut(res_stamp), FadeOut(res_stamp_text),
            run_time=0.8
        )

        final_card = RoundedRectangle(
            corner_radius=0.2, width=12.0, height=4.8,
            fill_color=COLOR_CARD_BG, fill_opacity=0.95,
            stroke_color=COLOR_GOLD, stroke_width=2.5
        ).shift(DOWN * 0.5)

        f_t1 = Text("【2025新高考II卷 第14题 · 严格证明完毕】", font=FONT, font_size=24, color=COLOR_GOLD, weight=BOLD)
        f_t2 = Text("几何直觉探索形态 · 代数定理锁定极值", font=FONT, font_size=20, color=COLOR_CYAN)

        f_box1 = RoundedRectangle(corner_radius=0.1, width=5.2, height=2.0, fill_color="#1F242C", fill_opacity=0.9, stroke_color=COLOR_BLUE, stroke_width=1.5)
        f_box1_text = VGroup(
            Text("第一部：3D 物理探索", font=FONT, font_size=16, color=COLOR_BLUE, weight=BOLD),
            Text("• 错位对角外切消除晃荡自由度", font=FONT, font_size=13, color=COLOR_WHITE),
            Text("• 构造出 r = 2.5 cm 的真实存在性", font=FONT, font_size=13, color=COLOR_GRAY)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(f_box1)

        f_box2 = RoundedRectangle(corner_radius=0.1, width=5.2, height=2.0, fill_color="#1F2A1E", fill_opacity=0.9, stroke_color=COLOR_GREEN, stroke_width=1.5)
        f_box2_text = VGroup(
            Text("第二部：空间建系与不等式证明", font=FONT, font_size=16, color=COLOR_GREEN, weight=BOLD),
            Text("• 水平 Δρ ≤ 8-2r, 竖直 Δz ≤ 9-2r", font=FONT, font_size=13, color=COLOR_WHITE),
            Text("• 4r² ≤ (8-2r)²+(9-2r)² ⇒ r ≤ 2.5", font=FONT, font_size=13, color=COLOR_GOLD)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(f_box2)

        boxes = VGroup(VGroup(f_box1, f_box1_text), VGroup(f_box2, f_box2_text)).arrange(RIGHT, buff=0.8)
        f_footer = Text("直觉发现上限，代数证明不可逾越 —— 这就是立体几何的满分浪漫！", font=FONT, font_size=16, color=COLOR_GOLD)

        final_content = VGroup(f_t1, f_t2, boxes, f_footer).arrange(DOWN, buff=0.28).move_to(final_card)

        # Cue 29: 无论怎么旋转斜放，数学不等式像一道钢铁防线死死锁定！
        play_cue(29, FadeIn(final_card), Write(f_t1), Write(f_t2), FadeIn(boxes), anim_duration=3.5)

        # Cue 30: 几何直觉探索形态，代数定理锁定极值。这就是数学证明的极致浪漫！
        play_cue(30, Write(f_footer), anim_duration=3.0)

        self.wait(1.5)
