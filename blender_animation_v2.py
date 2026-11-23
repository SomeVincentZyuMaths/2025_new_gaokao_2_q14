import bpy
import os
import subprocess
import shutil
import json
import numpy as np

# 路径定义
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = r"X:\字体\霞鹜文楷LXGW_WenKai\lxgw-wenkai-v1.520\LXGWWenKai-Medium.ttf"
TIMELINE_FILE = os.path.join(BASE_DIR, "audio_timeline.json")
MASTER_AUDIO = os.path.join(BASE_DIR, "master_audio.mp3")
FRAMES_DIR = os.path.join(BASE_DIR, "frames_v2")
OUT_VIDEO = os.path.join(BASE_DIR, "render_2025_new_gaokao_2_q14_v2.mp4")

# 加载音频时间轴
with open(TIMELINE_FILE, "r", encoding="utf-8") as f:
    TIMELINE_META = json.load(f)

FPS = TIMELINE_META["fps"]
TOTAL_FRAMES = TIMELINE_META["total_frames"]
CUES = TIMELINE_META["cues"]

# 辅助查找 Cue 的起止帧
def get_cue_frame(cue_id):
    for c in CUES:
        if c["id"] == cue_id:
            return c["start_frame"], c["end_frame"]
    return 1, 30

def build_scene_v2(res=(1280, 720), total_frames=TOTAL_FRAMES):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # 1. 渲染器与帧输出设置
    engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = total_frames

    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = '8'

    os.makedirs(FRAMES_DIR, exist_ok=True)
    scene.render.filepath = os.path.join(FRAMES_DIR, "frame_")

    # 2. 世界环境：纯净深邃演播室背景 (#030406)
    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.006, 0.008, 0.012, 1.0)
        bg.inputs['Strength'].default_value = 0.45

    # =========================================================================
    # 3. 方案 A 材质库定义：深邃电镀蓝球 + 琥珀香槟微透圆柱
    # =========================================================================
    # (1) 皇家湛蓝电镀金属球
    mat_blue_metal = bpy.data.materials.new("RoyalBlueMetal")
    mat_blue_metal.use_nodes = True
    bsdf_bm = mat_blue_metal.node_tree.nodes.get("Principled BSDF")
    bsdf_bm.inputs['Base Color'].default_value = (0.08, 0.28, 0.88, 1.0)
    bsdf_bm.inputs['Metallic'].default_value = 0.94
    bsdf_bm.inputs['Roughness'].default_value = 0.16

    # (2) 琥珀香槟半透明物理玻璃圆柱外壳
    mat_amber_glass = bpy.data.materials.new("AmberChampagneGlass")
    mat_amber_glass.use_nodes = True
    bsdf_ag = mat_amber_glass.node_tree.nodes.get("Principled BSDF")
    bsdf_ag.inputs['Base Color'].default_value = (1.0, 0.78, 0.35, 1.0)
    bsdf_ag.inputs['Roughness'].default_value = 0.07
    if 'Alpha' in bsdf_ag.inputs:
        bsdf_ag.inputs['Alpha'].default_value = 0.32
    if 'Transmission Weight' in bsdf_ag.inputs:
        bsdf_ag.inputs['Transmission Weight'].default_value = 0.88
    if 'Emission Color' in bsdf_ag.inputs:
        bsdf_ag.inputs['Emission Color'].default_value = (1.0, 0.72, 0.25, 1.0)
        bsdf_ag.inputs['Emission Strength'].default_value = 0.4
    mat_amber_glass.blend_method = 'BLEND' if hasattr(mat_amber_glass, 'blend_method') else 'HASHED'

    # (3) 橙金发光线条材质
    mat_orange = bpy.data.materials.new("GlowOrange")
    mat_orange.use_nodes = True
    bsdf_orange = mat_orange.node_tree.nodes.get("Principled BSDF")
    bsdf_orange.inputs['Base Color'].default_value = (1.0, 0.62, 0.18, 1.0)
    if 'Emission Color' in bsdf_orange.inputs:
        bsdf_orange.inputs['Emission Color'].default_value = (1.0, 0.62, 0.18, 1.0)
        bsdf_orange.inputs['Emission Strength'].default_value = 3.6

    # (4) 荧光青蓝材质
    mat_cyan = bpy.data.materials.new("GlowCyan")
    mat_cyan.use_nodes = True
    bsdf_cyan = mat_cyan.node_tree.nodes.get("Principled BSDF")
    bsdf_cyan.inputs['Base Color'].default_value = (0.22, 0.90, 1.0, 1.0)
    if 'Emission Color' in bsdf_cyan.inputs:
        bsdf_cyan.inputs['Emission Color'].default_value = (0.22, 0.90, 1.0, 1.0)
        bsdf_cyan.inputs['Emission Strength'].default_value = 3.8

    # (5) 浅绿高亮材质
    mat_green = bpy.data.materials.new("GlowGreen")
    mat_green.use_nodes = True
    bsdf_green = mat_green.node_tree.nodes.get("Principled BSDF")
    bsdf_green.inputs['Base Color'].default_value = (0.55, 0.92, 0.38, 1.0)
    if 'Emission Color' in bsdf_green.inputs:
        bsdf_green.inputs['Emission Color'].default_value = (0.55, 0.92, 0.38, 1.0)
        bsdf_green.inputs['Emission Strength'].default_value = 3.0

    # (6) 正文字体材质
    mat_text_body = bpy.data.materials.new("TextBody")
    mat_text_body.use_nodes = True
    bsdf_tb = mat_text_body.node_tree.nodes.get("Principled BSDF")
    bsdf_tb.inputs['Base Color'].default_value = (0.92, 0.95, 0.98, 1.0)
    if 'Emission Color' in bsdf_tb.inputs:
        bsdf_tb.inputs['Emission Color'].default_value = (0.92, 0.95, 0.98, 1.0)
        bsdf_tb.inputs['Emission Strength'].default_value = 1.3

    # (7) 暗灰细线材质
    mat_dim = bpy.data.materials.new("DimLine")
    mat_dim.use_nodes = True
    bsdf_dim = mat_dim.node_tree.nodes.get("Principled BSDF")
    bsdf_dim.inputs['Base Color'].default_value = (0.20, 0.26, 0.35, 1.0)

    # (8) 激光投影引线材质
    mat_lead_line = bpy.data.materials.new("LeadLine")
    mat_lead_line.use_nodes = True
    bsdf_lead = mat_lead_line.node_tree.nodes.get("Principled BSDF")
    bsdf_lead.inputs['Base Color'].default_value = (0.35, 0.75, 0.95, 1.0)
    if 'Emission Color' in bsdf_lead.inputs:
        bsdf_lead.inputs['Emission Color'].default_value = (0.35, 0.75, 0.95, 1.0)
        bsdf_lead.inputs['Emission Strength'].default_value = 2.2

    # (9) 冲击波脉冲光环材质
    mat_pulse = bpy.data.materials.new("PulseShockwave")
    mat_pulse.use_nodes = True
    bsdf_pulse = mat_pulse.node_tree.nodes.get("Principled BSDF")
    bsdf_pulse.inputs['Base Color'].default_value = (1.0, 0.85, 0.3, 1.0)
    if 'Emission Color' in bsdf_pulse.inputs:
        bsdf_pulse.inputs['Emission Color'].default_value = (1.0, 0.85, 0.3, 1.0)
        bsdf_pulse.inputs['Emission Strength'].default_value = 8.0

    # =========================================================================
    # 4. 辅助工具与动画绑定
    # =========================================================================
    def create_tube_line(points, radius=0.03, mat=mat_orange, name="Line"):
        curve_data = bpy.data.curves.new(name=name, type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.bevel_depth = radius
        curve_data.bevel_resolution = 4
        spline = curve_data.splines.new('POLY')
        spline.points.add(len(points) - 1)
        for i, pt in enumerate(points):
            spline.points[i].co = (pt[0], pt[1], pt[2], 1)
        obj = bpy.data.objects.new(name, curve_data)
        bpy.context.collection.objects.link(obj)
        obj.data.materials.append(mat)
        if hasattr(obj, 'visible_shadow'):
            obj.visible_shadow = False
        return obj

    def animate_curve_growth(obj, f_start, f_end):
        curve_data = obj.data
        curve_data.bevel_factor_end = 0.0
        curve_data.keyframe_insert("bevel_factor_end", frame=1)
        curve_data.keyframe_insert("bevel_factor_end", frame=f_start)
        curve_data.bevel_factor_end = 1.0
        curve_data.keyframe_insert("bevel_factor_end", frame=f_end)

    def create_rounded_rect(cx, cz, w, h, r, mat=mat_orange, y=0.0, radius=0.032, name="RoundedRect"):
        n_seg = 12
        pts = []
        c_ru = (cx + w/2 - r, cz + h/2 - r)
        for th in np.linspace(0, np.pi/2, n_seg):
            pts.append((c_ru[0] + r*np.cos(th), y, c_ru[1] + r*np.sin(th)))
        c_lu = (cx - w/2 + r, cz + h/2 - r)
        for th in np.linspace(np.pi/2, np.pi, n_seg):
            pts.append((c_lu[0] + r*np.cos(th), y, c_lu[1] + r*np.sin(th)))
        c_lb = (cx - w/2 + r, cz - h/2 + r)
        for th in np.linspace(np.pi, 1.5*np.pi, n_seg):
            pts.append((c_lb[0] + r*np.cos(th), y, c_lb[1] + r*np.sin(th)))
        c_rb = (cx + w/2 - r, cz - h/2 + r)
        for th in np.linspace(1.5*np.pi, 2*np.pi, n_seg):
            pts.append((c_rb[0] + r*np.cos(th), y, c_rb[1] + r*np.sin(th)))

        curve_data = bpy.data.curves.new(name=name, type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.bevel_depth = radius
        curve_data.bevel_resolution = 4
        spline = curve_data.splines.new('POLY')
        spline.points.add(len(pts) - 1)
        for i, pt in enumerate(pts):
            spline.points[i].co = (pt[0], pt[1], pt[2], 1)
        spline.use_cyclic_u = True
        obj = bpy.data.objects.new(name, curve_data)
        bpy.context.collection.objects.link(obj)
        obj.data.materials.append(mat)
        if hasattr(obj, 'visible_shadow'):
            obj.visible_shadow = False
        return obj

    lxgw_font = None
    if os.path.exists(FONT_PATH):
        lxgw_font = bpy.data.fonts.load(FONT_PATH)

    def add_text_3d(text, location, scale=0.35, mat=mat_text_body, align='LEFT', extrude=0.012, bevel=0.002, name="Txt"):
        t_data = bpy.data.curves.new(name=name, type='FONT')
        t_data.body = text
        if lxgw_font:
            t_data.font = lxgw_font
        t_data.extrude = extrude
        t_data.bevel_depth = bevel
        t_data.bevel_resolution = 2
        t_data.align_x = align
        t_obj = bpy.data.objects.new(name, t_data)
        t_obj.location = location
        t_obj.scale = (scale, scale, scale)
        t_obj.rotation_euler = (np.pi / 2, 0, 0)
        bpy.context.collection.objects.link(t_obj)
        t_obj.data.materials.append(mat)
        if hasattr(t_obj, 'visible_glossy'):
            t_obj.visible_glossy = False
        if hasattr(t_obj, 'visible_shadow'):
            t_obj.visible_shadow = False
        return t_obj

    def animate_fade_in(obj, f_appear, duration=20, target_scale=None):
        if target_scale is None:
            target_scale = obj.scale.x
        obj.scale = (0.0001, 0.0001, 0.0001)
        obj.keyframe_insert("scale", frame=1)
        obj.keyframe_insert("scale", frame=f_appear)
        obj.scale = (target_scale * 1.08, target_scale * 1.08, target_scale * 1.08)
        obj.keyframe_insert("scale", frame=f_appear + int(duration * 0.7))
        obj.scale = (target_scale, target_scale, target_scale)
        obj.keyframe_insert("scale", frame=f_appear + duration)

    # =========================================================================
    # 5. 左侧板书卡片 (根据配音时间轴精确触发)
    # =========================================================================
    CARD_CX = -5.0
    CARD_CZ = 4.8
    CARD_W = 8.6
    CARD_H = 10.3

    # (1) 外围橙金圆角大边框
    card_border = create_rounded_rect(CARD_CX, CARD_CZ, CARD_W, CARD_H, r=0.45, mat=mat_orange, y=0.0, radius=0.035, name="CardBorder")
    animate_curve_growth(card_border, 1, 40)

    # (2) 顶部标签药丸框：【2025年新高考Ⅱ卷 · 第14题】
    TITLE_W = 5.2
    TITLE_H = 0.9
    TITLE_Z = CARD_CZ + CARD_H/2 - 0.78
    title_box = create_rounded_rect(CARD_CX - 1.25, TITLE_Z, TITLE_W, TITLE_H, r=0.25, mat=mat_orange, y=0.0, radius=0.028, name="TitleBadge")
    animate_curve_growth(title_box, 15, 50)
    t_head = add_text_3d("2025年新高考Ⅱ卷 · 第14题", (CARD_CX - 1.25, 0.0, TITLE_Z - 0.16), scale=0.42, mat=mat_text_body, align='CENTER')
    animate_fade_in(t_head, 25, 20, 0.42)

    # (3) 【原题呈现】(Cue 1~2: 帧 15 ~ 300)
    TEXT_L = CARD_CX - CARD_W/2 + 0.65
    f_c1_s, _ = get_cue_frame(1)
    f_c2_s, _ = get_cue_frame(2)
    t_q0 = add_text_3d("【原题呈现】", (TEXT_L, 0.0, 8.4), scale=0.40, mat=mat_orange)
    animate_fade_in(t_q0, f_c1_s + 10, 18, 0.40)
    t_q1 = add_text_3d("一个底面半径为 4cm，高为 9cm 的封闭圆柱形容器", (TEXT_L, 0.0, 7.7), scale=0.31)
    animate_fade_in(t_q1, f_c2_s, 20, 0.31)
    t_q2 = add_text_3d("内有两个半径相等的铁球，则铁球半径的最大值为", (TEXT_L, 0.0, 7.1), scale=0.31)
    animate_fade_in(t_q2, f_c2_s + 80, 20, 0.31)
    t_q3 = add_text_3d("_______ cm。", (TEXT_L, 0.0, 6.5), scale=0.31)
    animate_fade_in(t_q3, f_c2_s + 150, 20, 0.31)

    div_line = create_tube_line([(TEXT_L, 0.0, 6.15), (CARD_CX + CARD_W/2 - 0.65, 0.0, 6.15)], radius=0.014, mat=mat_dim, name="DivLine")
    animate_curve_growth(div_line, f_c2_s + 200, f_c2_s + 240)

    # (4) 【空间降维通解模型】与各阶段动态点亮
    # Cue 3: 探索设问
    f_c3_s, _ = get_cue_frame(3)
    t_m0 = add_text_3d("【空间探索与降维模型】", (TEXT_L, 0.0, 5.65), scale=0.40, mat=mat_green)
    animate_fade_in(t_m0, f_c3_s, 20, 0.40)

    # Cue 4~5: 探索一 (水平并排 r=2cm)
    f_c4_s, _ = get_cue_frame(4)
    f_c5_s, _ = get_cue_frame(5)
    t_exp1 = add_text_3d("① 探索一(水平并排)：4r = 8 ⇒ r = 2 cm (太矮,留空5cm)", (TEXT_L, 0.0, 5.0), scale=0.29, mat=mat_cyan)
    animate_fade_in(t_exp1, f_c5_s, 20, 0.29)

    # Cue 9~10: 探索二 (竖直叠放 r=2.25cm)
    f_c9_s, _ = get_cue_frame(9)
    f_c10_s, _ = get_cue_frame(10)
    t_exp2 = add_text_3d("② 探索二(竖直叠放)：4r = 9 ⇒ r = 2.25 cm (太瘦,缝隙3.5cm)", (TEXT_L, 0.0, 4.4), scale=0.29, mat=mat_cyan)
    animate_fade_in(t_exp2, f_c10_s, 20, 0.29)

    # Cue 13~16: 终极极限 (对角错开锁死)
    f_c13_s, _ = get_cue_frame(13)
    f_c14_s, _ = get_cue_frame(14)
    f_c16_s, f_c16_e = get_cue_frame(16)
    f_c17_s, _ = get_cue_frame(17)
    f_c22_s, _ = get_cue_frame(22)
    t_exp3 = add_text_3d("③ 终极形态：对角错位相切，全面锁死自由度！", (TEXT_L, 0.0, 3.8), scale=0.30, mat=mat_orange)
    animate_fade_in(t_exp3, f_c16_s, 20, 0.30)

    # Cue 19: 空间参数
    f_c19_s, _ = get_cue_frame(19)
    t_m_dz = add_text_3d("   高差 Δz = 9 - 2r, 水平跨度 Δρ = 8 - 2r, 斜边 2r", (TEXT_L, 0.0, 3.25), scale=0.28, mat=mat_cyan)
    animate_fade_in(t_m_dz, f_c19_s, 20, 0.28)

    # Cue 20: 空间勾股方程
    f_c20_s, _ = get_cue_frame(20)
    t_m3 = add_text_3d("④ 空间勾股定理：(8 - 2r)² + (9 - 2r)² = (2r)²", (TEXT_L, 0.0, 2.65), scale=0.30, mat=mat_orange)
    animate_fade_in(t_m3, f_c20_s, 20, 0.30)

    # Cue 21: 化简求解
    f_c21_s, _ = get_cue_frame(21)
    t_m4 = add_text_3d("⑤ 化简求解：4r² - 68r + 145 = (2r - 5)(2r - 29) = 0", (TEXT_L, 0.0, 2.05), scale=0.29)
    animate_fade_in(t_m4, f_c21_s, 20, 0.29)
    t_m5 = add_text_3d("   ⇒ 得最大半径 r = 2.5 cm (勾三股四弦五)", (TEXT_L, 0.0, 1.50), scale=0.29, mat=mat_green)
    animate_fade_in(t_m5, f_c21_s + 120, 20, 0.29)

    # Cue 23: 底部参考答案药丸卡片
    f_c23_s, _ = get_cue_frame(23)
    ANS_W = 4.2
    ANS_H = 0.85
    ANS_Z = 0.45
    ans_badge = create_rounded_rect(CARD_CX - 1.8, ANS_Z, ANS_W, ANS_H, r=0.22, mat=mat_orange, y=0.0, radius=0.032, name="AnsBadge")
    animate_curve_growth(ans_badge, f_c23_s, f_c23_s + 40)
    t_ans = add_text_3d("参考答案：2.5 cm", (CARD_CX - 1.8, 0.0, ANS_Z - 0.16), scale=0.42, mat=mat_cyan, align='CENTER')
    animate_fade_in(t_ans, f_c23_s + 20, 25, 0.42)

    # =========================================================================
    # 6. 右侧 3D 几何演播区 (方案 A：琥珀微透圆柱 + 皇家湛蓝电镀球体)
    # =========================================================================
    CYL_X = 4.4
    CYL_Y = 0.0
    R_CYL = 4.0
    H_CYL = 9.0

    # (1) 琥珀香槟圆柱外壳与圆环
    def make_cylinder_ring(z_val, name="CylRing"):
        ths = np.linspace(0, 2*np.pi, 96)
        pts = [(CYL_X + R_CYL * np.cos(th), CYL_Y + R_CYL * np.sin(th), z_val) for th in ths]
        return create_tube_line(pts, radius=0.052, mat=mat_orange, name=name)

    bot_ring = make_cylinder_ring(0.0, "CylBottomRing")
    top_ring = make_cylinder_ring(H_CYL, "CylTopRing")
    animate_curve_growth(bot_ring, 1, 40)
    animate_curve_growth(top_ring, 1, 40)

    for i, ang in enumerate([np.radians(25), np.radians(110), np.radians(205), np.radians(295)]):
        p1 = (CYL_X + R_CYL * np.cos(ang), CYL_Y + R_CYL * np.sin(ang), 0.0)
        p2 = (CYL_X + R_CYL * np.cos(ang), CYL_Y + R_CYL * np.sin(ang), H_CYL)
        strut = create_tube_line([p1, p2], radius=0.026, mat=mat_orange, name=f"CylStrut_{i}")
        animate_curve_growth(strut, 10, 50)

    # 琥珀香槟半透明圆柱壁
    curve_data = bpy.data.curves.new(name="CylAmberGlass", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.extrude = H_CYL / 2
    ths = np.linspace(-np.pi/10, np.pi + np.pi/10, 72)
    spline = curve_data.splines.new('POLY')
    spline.points.add(len(ths)-1)
    for i, th in enumerate(ths):
        spline.points[i].co = (CYL_X + R_CYL * np.cos(th), CYL_Y + R_CYL * np.sin(th), H_CYL / 2, 1)
    glass_obj = bpy.data.objects.new("CylAmberGlass", curve_data)
    bpy.context.collection.objects.link(glass_obj)
    glass_obj.data.materials.append(mat_amber_glass)

    # (2) 两个核心金属球 (基础半径 1.0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=80, ring_count=40, location=(0,0,0))
    ball1 = bpy.context.active_object
    ball1.name = "BlueSphere_1"
    ball1.data.materials.append(mat_blue_metal)
    bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=80, ring_count=40, location=(0,0,0))
    ball2 = bpy.context.active_object
    ball2.name = "BlueSphere_2"
    ball2.data.materials.append(mat_blue_metal)
    bpy.ops.object.shade_smooth()

    # =========================================================================
    # (3) 物理探索动画全轨迹关键帧 (精细绑定配音时间轴)
    # =========================================================================
    # 【阶段一 · 入场滑落】(帧 1 ~ 300)
    ball1.location = (CYL_X - 1.5, CYL_Y, 14.0)
    ball1.scale = (1.0, 1.0, 1.0)
    ball1.keyframe_insert("location", frame=40)
    ball1.keyframe_insert("scale", frame=40)
    ball1.location = (CYL_X - 2.0, CYL_Y, 1.0)
    ball1.keyframe_insert("location", frame=90)
    ball1.location = (CYL_X - 2.0, CYL_Y, 1.8)
    ball1.keyframe_insert("location", frame=110)
    ball1.location = (CYL_X - 2.0, CYL_Y, 1.0)
    ball1.keyframe_insert("location", frame=130)

    ball2.location = (CYL_X + 1.5, CYL_Y, 16.0)
    ball2.scale = (1.0, 1.0, 1.0)
    ball2.keyframe_insert("location", frame=70)
    ball2.keyframe_insert("scale", frame=70)
    ball2.location = (CYL_X + 1.0, CYL_Y, 3.2)
    ball2.keyframe_insert("location", frame=120)
    ball2.location = (CYL_X + 1.8, CYL_Y, 1.0)
    ball2.keyframe_insert("location", frame=160)

    # 【阶段二 · 探索一：水平并排 r = 2.0 cm + 上下移动晃荡】(Cue 4~8: 帧 f_c4_s ~ f_c8_e)
    _, f_c8_e = get_cue_frame(8)
    # 膨胀至 r = 2.0 并排在底面
    f_grow_p1_start = f_c4_s
    f_grow_p1_end = f_c5_s + 60
    ball1.location = (CYL_X - 2.0, CYL_Y, 1.0)
    ball1.scale = (1.0, 1.0, 1.0)
    ball1.keyframe_insert("location", frame=f_grow_p1_start)
    ball1.keyframe_insert("scale", frame=f_grow_p1_start)

    ball2.location = (CYL_X + 2.0, CYL_Y, 1.0)
    ball2.scale = (1.0, 1.0, 1.0)
    ball2.keyframe_insert("location", frame=f_grow_p1_start)
    ball2.keyframe_insert("scale", frame=f_grow_p1_start)

    ball1.location = (CYL_X - 2.0, CYL_Y, 2.0)
    ball1.scale = (2.0, 2.0, 2.0)
    ball1.keyframe_insert("location", frame=f_grow_p1_end)
    ball1.keyframe_insert("scale", frame=f_grow_p1_end)

    ball2.location = (CYL_X + 2.0, CYL_Y, 2.0)
    ball2.scale = (2.0, 2.0, 2.0)
    ball2.keyframe_insert("location", frame=f_grow_p1_end)
    ball2.keyframe_insert("scale", frame=f_grow_p1_end)

    # 上下晃荡动画 (Cue 6~7: 帧 f_c6_s ~ f_c7_e)
    f_c6_s, _ = get_cue_frame(6)
    f_c7_s, f_c7_e = get_cue_frame(7)
    # 向上浮起到 z = 6.5，再落回 z = 2.0
    f_bob1 = f_c6_s + 30
    f_bob2 = f_c6_s + 90
    f_bob3 = f_c7_s + 40
    ball1.location = (CYL_X - 2.0, CYL_Y, 6.5)
    ball2.location = (CYL_X + 2.0, CYL_Y, 6.5)
    ball1.keyframe_insert("location", frame=f_bob1)
    ball2.keyframe_insert("location", frame=f_bob1)

    ball1.location = (CYL_X - 2.0, CYL_Y, 2.0)
    ball2.location = (CYL_X + 2.0, CYL_Y, 2.0)
    ball1.keyframe_insert("location", frame=f_bob2)
    ball2.keyframe_insert("location", frame=f_bob2)

    ball1.location = (CYL_X - 2.0, CYL_Y, 5.0)
    ball2.location = (CYL_X + 2.0, CYL_Y, 5.0)
    ball1.keyframe_insert("location", frame=f_bob3)
    ball2.keyframe_insert("location", frame=f_bob3)

    # 顶部空旷标尺 (剩余高度 ΔH = 5 cm 提示)
    h_cue_line = create_tube_line([(CYL_X, 0, 4.0), (CYL_X, 0, 9.0)], radius=0.035, mat=mat_orange, name="RemainHeightLine")
    animate_curve_growth(h_cue_line, f_c7_s, f_c7_s + 30)
    t_rem_h = add_text_3d("剩余高差: 5 cm！", (CYL_X + 0.35, -1.0, 6.5), scale=0.33, mat=mat_orange)
    animate_fade_in(t_rem_h, f_c7_s + 15, 20, 0.33)

    # 结束探索一，清除标尺
    h_cue_line.scale = (0.0001, 0.0001, 0.0001)
    h_cue_line.keyframe_insert("scale", frame=f_c8_e)
    t_rem_h.scale = (0.0001, 0.0001, 0.0001)
    t_rem_h.keyframe_insert("scale", frame=f_c8_e)

    # 【阶段三 · 探索二：竖直叠放 r = 2.25 cm + 左右摆动晃荡】(Cue 9~12: 帧 f_c9_s ~ f_c12_e)
    _, f_c12_e = get_cue_frame(12)
    f_grow_p2_end = f_c10_s + 60
    # 下球在 (CYL_X, 0, 2.25)，上球在 (CYL_X, 0, 6.75)，r = 2.25
    ball1.location = (CYL_X, CYL_Y, 2.25)
    ball1.scale = (2.25, 2.25, 2.25)
    ball1.keyframe_insert("location", frame=f_grow_p2_end)
    ball1.keyframe_insert("scale", frame=f_grow_p2_end)

    ball2.location = (CYL_X, CYL_Y, 6.75)
    ball2.scale = (2.25, 2.25, 2.25)
    ball2.keyframe_insert("location", frame=f_grow_p2_end)
    ball2.keyframe_insert("scale", frame=f_grow_p2_end)

    # 左右晃荡动画 (Cue 11~12: 帧 f_c11_s ~ f_c12_e)
    f_c11_s, _ = get_cue_frame(11)
    f_c12_s, _ = get_cue_frame(12)
    f_sw1 = f_c11_s + 30
    f_sw2 = f_c11_s + 90
    f_sw3 = f_c12_s + 40
    # 向左摆
    ball1.location = (CYL_X - 1.6, CYL_Y, 2.25)
    ball2.location = (CYL_X - 1.6, CYL_Y, 6.75)
    ball1.keyframe_insert("location", frame=f_sw1)
    ball2.keyframe_insert("location", frame=f_sw1)
    # 向右摆
    ball1.location = (CYL_X + 1.6, CYL_Y, 2.25)
    ball2.location = (CYL_X + 1.6, CYL_Y, 6.75)
    ball1.keyframe_insert("location", frame=f_sw2)
    ball2.keyframe_insert("location", frame=f_sw2)
    # 居中
    ball1.location = (CYL_X, CYL_Y, 2.25)
    ball2.location = (CYL_X, CYL_Y, 6.75)
    ball1.keyframe_insert("location", frame=f_sw3)
    ball2.keyframe_insert("location", frame=f_sw3)

    # 侧边缝隙标尺 (3.5 cm 提示)
    w_cue_line = create_tube_line([(CYL_X + 2.25, 0, 4.5), (CYL_X + 4.0, 0, 4.5)], radius=0.035, mat=mat_cyan, name="RemainWidthLine")
    animate_curve_growth(w_cue_line, f_c12_s, f_c12_s + 30)
    t_rem_w = add_text_3d("侧面缝隙: 3.5 cm！", (CYL_X + 2.3, -1.0, 5.2), scale=0.33, mat=mat_cyan)
    animate_fade_in(t_rem_w, f_c12_s + 15, 20, 0.33)

    # 结束探索二，清除标尺
    w_cue_line.scale = (0.0001, 0.0001, 0.0001)
    w_cue_line.keyframe_insert("scale", frame=f_c12_e)
    t_rem_w.scale = (0.0001, 0.0001, 0.0001)
    t_rem_w.keyframe_insert("scale", frame=f_c12_e)

    # 【阶段四 · 对角错开滑动与终极锁死膨胀】(Cue 13~17: 帧 f_c13_s ~ f_c16_e)
    # 下球贴底靠左滑，上球顶天靠右滑，同步从 r = 2.25 膨胀至 r = 2.5
    f_diag_start = f_c14_s
    f_diag_end = f_c16_s + 40
    N_SLIDE = 30
    for step in range(N_SLIDE + 1):
        f = int(f_diag_start + (f_diag_end - f_diag_start) * (step / N_SLIDE))
        prog = step / N_SLIDE
        t_ease = prog * prog * (3 - 2 * prog)
        r_curr = 2.25 + 0.25 * t_ease
        b1_loc = (CYL_X - (4.0 - r_curr), CYL_Y, r_curr)
        b2_loc = (CYL_X + (4.0 - r_curr), CYL_Y, 9.0 - r_curr)

        ball1.location = b1_loc
        ball1.scale = (r_curr, r_curr, r_curr)
        ball1.keyframe_insert("location", frame=f)
        ball1.keyframe_insert("scale", frame=f)

        ball2.location = b2_loc
        ball2.scale = (r_curr, r_curr, r_curr)
        ball2.keyframe_insert("location", frame=f)
        ball2.keyframe_insert("scale", frame=f)

    # 保持终极位置到片尾
    ball1.keyframe_insert("location", frame=total_frames)
    ball1.keyframe_insert("scale", frame=total_frames)
    ball2.keyframe_insert("location", frame=total_frames)
    ball2.keyframe_insert("scale", frame=total_frames)

    # (4) 终极卡死瞬间冲击波光圈 (在 f_diag_end 爆发)
    real_O1 = (CYL_X - 1.5, CYL_Y, 2.5)
    real_O2 = (CYL_X + 1.5, CYL_Y, 6.5)
    real_Mid = ((real_O1[0]+real_O2[0])/2, CYL_Y, (real_O1[2]+real_O2[2])/2)

    pulse_curve = bpy.data.curves.new(name="PulseShockwave", type='CURVE')
    pulse_curve.dimensions = '3D'
    pulse_curve.bevel_depth = 0.04
    ths = np.linspace(0, 2*np.pi, 64)
    spline = pulse_curve.splines.new('POLY')
    spline.points.add(len(ths)-1)
    for i, th in enumerate(ths):
        spline.points[i].co = (real_Mid[0] + 0.8*np.cos(th), real_Mid[1], real_Mid[2] + 0.8*np.sin(th), 1)
    spline.use_cyclic_u = True
    pulse_obj = bpy.data.objects.new("PulseShockwave", pulse_curve)
    bpy.context.collection.objects.link(pulse_obj)
    pulse_obj.data.materials.append(mat_pulse)
    if hasattr(pulse_obj, 'visible_shadow'):
        pulse_obj.visible_shadow = False

    pulse_obj.scale = (0.0001, 0.0001, 0.0001)
    pulse_obj.keyframe_insert("scale", frame=1)
    pulse_obj.keyframe_insert("scale", frame=f_diag_end - 2)
    pulse_obj.scale = (1.0, 1.0, 1.0)
    pulse_obj.keyframe_insert("scale", frame=f_diag_end + 5)
    pulse_obj.scale = (4.0, 4.0, 4.0)
    pulse_obj.keyframe_insert("scale", frame=f_diag_end + 35)
    pulse_obj.scale = (0.0001, 0.0001, 0.0001)
    pulse_obj.keyframe_insert("scale", frame=f_diag_end + 38)

    # 内部球心连线
    inner_hypot = create_tube_line([real_O1, real_O2], radius=0.035, mat=mat_orange, name="InnerHypot")
    animate_curve_growth(inner_hypot, f_diag_end, f_diag_end + 30)

    # =========================================================================
    # (5) 前置无遮挡【纵剖面降维直角三角形】(纤细激光标尺规格)
    # =========================================================================
    FRONT_Y = -2.8
    tri_O1 = (CYL_X - 1.5, FRONT_Y, 2.5)
    tri_O2 = (CYL_X + 1.5, FRONT_Y, 6.5)
    tri_Corner = (CYL_X + 1.5, FRONT_Y, 2.5)
    tri_Mid = ((tri_O1[0]+tri_O2[0])/2, FRONT_Y, (tri_O1[2]+tri_O2[2])/2)

    # Cue 18: 降维模型引线射出
    f_c18_s, _ = get_cue_frame(18)
    lead1 = create_tube_line([real_O1, tri_O1], radius=0.016, mat=mat_lead_line, name="Lead_O1")
    lead2 = create_tube_line([real_O2, tri_O2], radius=0.016, mat=mat_lead_line, name="Lead_O2")
    lead3 = create_tube_line([real_Mid, tri_Mid], radius=0.016, mat=mat_lead_line, name="Lead_P")
    animate_curve_growth(lead1, f_c18_s, f_c18_s + 30)
    animate_curve_growth(lead2, f_c18_s, f_c18_s + 30)
    animate_curve_growth(lead3, f_c18_s, f_c18_s + 30)

    # Cue 19: 斜边、底边、竖直高生长
    f_c19_s, _ = get_cue_frame(19)
    hypot_front = create_tube_line([tri_O1, tri_O2], radius=0.045, mat=mat_orange, name="Hypot_Front")
    animate_curve_growth(hypot_front, f_c19_s, f_c19_s + 45)

    base_front = create_tube_line([tri_O1, tri_Corner], radius=0.032, mat=mat_cyan, name="Base_Front")
    animate_curve_growth(base_front, f_c19_s + 45, f_c19_s + 90)

    height_front = create_tube_line([tri_Corner, tri_O2], radius=0.032, mat=mat_cyan, name="Height_Front")
    animate_curve_growth(height_front, f_c19_s + 90, f_c19_s + 135)

    # 直角拐角标记
    corner_sz = 0.40
    p_c_left = (tri_Corner[0] - corner_sz, FRONT_Y, tri_Corner[2])
    p_c_up = (tri_Corner[0], FRONT_Y, tri_Corner[2] + corner_sz)
    p_c_mid = (tri_Corner[0] - corner_sz, FRONT_Y, tri_Corner[2] + corner_sz)
    right_mark = create_tube_line([p_c_left, p_c_mid, p_c_up], radius=0.020, mat=mat_cyan, name="RightAngleMark")
    animate_curve_growth(right_mark, f_c19_s + 135, f_c19_s + 155)

    # 发光微珠节点
    for pt, col_mat, f_dot in [(tri_O1, mat_orange, f_c19_s), (tri_Mid, mat_orange, f_c19_s + 25), (tri_Corner, mat_cyan, f_c19_s + 90), (tri_O2, mat_orange, f_c19_s + 135)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, location=pt)
        nd = bpy.context.active_object
        nd.data.materials.append(col_mat)
        if hasattr(nd, 'visible_shadow'):
            nd.visible_shadow = False
        animate_fade_in(nd, f_dot, 15, 1.0)

    # 3D 几何原位标注
    L_Y = -3.2
    t_o1 = add_text_3d("O₁ (底球心)", (tri_O1[0] - 0.35, L_Y, tri_O1[2] - 0.15), scale=0.33, mat=mat_orange, align='RIGHT')
    animate_fade_in(t_o1, f_c19_s + 10, 18, 0.33)

    t_o2 = add_text_3d("O₂ (顶球心)", (tri_O2[0] + 0.35, L_Y, tri_O2[2] + 0.15), scale=0.33, mat=mat_orange, align='LEFT')
    animate_fade_in(t_o2, f_c19_s + 135, 18, 0.33)

    t_pt_p = add_text_3d("相切点 P", (tri_Mid[0] - 0.35, L_Y, tri_Mid[2] + 0.35), scale=0.31, mat=mat_orange, align='RIGHT')
    animate_fade_in(t_pt_p, f_c19_s + 30, 18, 0.31)

    t_edge_h = add_text_3d("斜边: 2r = 5", (tri_Mid[0] + 0.35, L_Y, tri_Mid[2] - 0.25), scale=0.35, mat=mat_orange, align='LEFT')
    animate_fade_in(t_edge_h, f_c19_s + 35, 18, 0.35)

    t_edge_b = add_text_3d("水平跨度: 8 - 2r = 3", (CYL_X, L_Y, tri_Corner[2] - 0.65), scale=0.32, mat=mat_cyan, align='CENTER')
    animate_fade_in(t_edge_b, f_c19_s + 70, 18, 0.32)

    t_edge_v = add_text_3d("竖直高: 9 - 2r = 4", (tri_Corner[0] + 0.45, L_Y, 4.5), scale=0.32, mat=mat_cyan, align='LEFT')
    animate_fade_in(t_edge_v, f_c19_s + 115, 18, 0.32)

    t_proj_title = add_text_3d("【空间纵剖面降维直角三角形】", (CYL_X, L_Y, 9.8), scale=0.38, mat=mat_green, align='CENTER')
    animate_fade_in(t_proj_title, f_c18_s + 10, 20, 0.38)

    # =========================================================================
    # 7. 电影级摄影机运镜系统 (平滑轨道跟随)
    # =========================================================================
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(-0.3, 0.0, 4.8))
    target = bpy.context.active_object
    target.name = "CamCenter"

    bpy.ops.object.camera_add(location=(-0.3, -26.5, 6.2))
    cam = bpy.context.active_object
    cam.name = "MainCamera"
    cam.data.lens = 37.0
    scene.camera = cam

    track = cam.constraints.new(type='TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    # 全局黄金视角
    cam.location = (-0.3, -26.5, 6.2)
    cam.keyframe_insert("location", frame=1)
    cam.keyframe_insert("location", frame=f_c3_s)

    # 推进特写右侧圆柱探索过程 (Cue 4 ~ 16)
    cam.location = (2.2, -21.0, 5.8)
    cam.keyframe_insert("location", frame=f_c4_s + 60)
    cam.keyframe_insert("location", frame=f_c16_s)

    # 稍微拉退收入全息前置直角三角形 (Cue 17 ~ 22)
    cam.location = (1.2, -23.0, 5.8)
    cam.keyframe_insert("location", frame=f_c17_s)
    cam.keyframe_insert("location", frame=f_c22_s)

    # 回归全景黄金视角定格 (Cue 23 ~ 结尾)
    cam.location = (-0.3, -26.5, 6.2)
    cam.keyframe_insert("location", frame=f_c23_s + 40)
    cam.keyframe_insert("location", frame=total_frames)

    # =========================================================================
    # 8. 演播室级工业灯光系统
    # =========================================================================
    bpy.ops.object.light_add(type='AREA', location=(CYL_X, -6.0, 16.0))
    top_light = bpy.context.active_object
    top_light.data.energy = 4200
    top_light.data.size = 15.0
    top_light.data.color = (0.95, 0.98, 1.0)
    top_light.rotation_euler = (np.radians(20), 0, 0)

    bpy.ops.object.light_add(type='AREA', location=(CYL_X + 7.0, -14.0, 7.5))
    front_light = bpy.context.active_object
    front_light.data.energy = 3800
    front_light.data.size = 9.0
    front_light.data.color = (1.0, 1.0, 1.0)
    front_light.rotation_euler = (np.radians(45), 0, np.radians(30))

    bpy.ops.object.light_add(type='AREA', location=(CARD_CX, -15.0, CARD_CZ))
    board_light = bpy.context.active_object
    board_light.data.energy = 1600
    board_light.data.size = 11.0
    board_light.data.color = (0.96, 0.98, 1.0)

    bpy.ops.object.light_add(type='SPOT', location=(CYL_X - 1.0, 9.0, 8.5))
    rim_light = bpy.context.active_object
    rim_light.data.energy = 4500
    rim_light.data.spot_size = np.radians(75)
    rim_light.rotation_euler = (np.radians(-135), 0, 0)

    print("Animation scene v2 build complete!")

def render_and_encode_v2(res=(1280, 720), total_frames=TOTAL_FRAMES):
    if os.path.exists(FRAMES_DIR):
        shutil.rmtree(FRAMES_DIR)
    os.makedirs(FRAMES_DIR, exist_ok=True)

    build_scene_v2(res=res, total_frames=total_frames)

    print(f"Rendering {total_frames} frames to {FRAMES_DIR}...")
    bpy.ops.render.render(animation=True)
    print("Blender render finished! Now encoding video with audio via FFmpeg...")

    input_pattern = os.path.join(FRAMES_DIR, "frame_%04d.png")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", input_pattern,
        "-i", MASTER_AUDIO,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-preset", "slow",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUT_VIDEO
    ]
    print("Running FFmpeg:", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"FFmpeg encoding succeeded: {OUT_VIDEO}")
        shutil.rmtree(FRAMES_DIR)
        print("Cleaned temp frames directory.")
    else:
        print("FFmpeg encoding error:", res.stderr)

if __name__ == "__main__":
    render_and_encode_v2(res=(1280, 720), total_frames=TOTAL_FRAMES)
