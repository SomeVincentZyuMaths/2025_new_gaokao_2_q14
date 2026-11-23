import bpy
import os
import numpy as np

# 路径定义
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = r"X:\字体\霞鹜文楷LXGW_WenKai\lxgw-wenkai-v1.520\LXGWWenKai-Medium.ttf"
OUT_IMG = os.path.join(BASE_DIR, "preview_blender_first_look.png")

def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # 渲染器设置：优先 EEVEE-Next
    engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = False

    # 1. 世界环境：纯净深邃黑夜演播室 (#030406)
    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.006, 0.008, 0.012, 1.0)
        bg.inputs['Strength'].default_value = 0.45

    # =========================================================================
    # 2. 材质库定义
    # =========================================================================
    # (1) 银白高级拉丝不锈钢金属球 (Satin Brushed Stainless Steel, 细腻柔和光弧)
    mat_steel = bpy.data.materials.new("SilverSteel")
    mat_steel.use_nodes = True
    bsdf_steel = mat_steel.node_tree.nodes.get("Principled BSDF")
    bsdf_steel.inputs['Base Color'].default_value = (0.86, 0.89, 0.95, 1.0)
    bsdf_steel.inputs['Metallic'].default_value = 0.96
    bsdf_steel.inputs['Roughness'].default_value = 0.20

    # (2) 玻璃透明圆柱外壳 (幽蓝物理玻璃透光壳)
    mat_glass = bpy.data.materials.new("GlassShell")
    mat_glass.use_nodes = True
    bsdf_glass = mat_glass.node_tree.nodes.get("Principled BSDF")
    bsdf_glass.inputs['Base Color'].default_value = (0.12, 0.60, 1.0, 1.0)
    bsdf_glass.inputs['Roughness'].default_value = 0.08
    if 'Alpha' in bsdf_glass.inputs:
        bsdf_glass.inputs['Alpha'].default_value = 0.18
    if 'Transmission Weight' in bsdf_glass.inputs:
        bsdf_glass.inputs['Transmission Weight'].default_value = 0.94
    mat_glass.blend_method = 'BLEND' if hasattr(mat_glass, 'blend_method') else 'HASHED'

    # (3) 橙金发光线条材质 (卡片主边框、斜边、题目标签)
    mat_orange = bpy.data.materials.new("GlowOrange")
    mat_orange.use_nodes = True
    bsdf_orange = mat_orange.node_tree.nodes.get("Principled BSDF")
    bsdf_orange.inputs['Base Color'].default_value = (1.0, 0.62, 0.18, 1.0)
    if 'Emission Color' in bsdf_orange.inputs:
        bsdf_orange.inputs['Emission Color'].default_value = (1.0, 0.62, 0.18, 1.0)
        bsdf_orange.inputs['Emission Strength'].default_value = 3.6

    # (4) 荧光青蓝材质 (直角边、垂足、圆柱线框)
    mat_cyan = bpy.data.materials.new("GlowCyan")
    mat_cyan.use_nodes = True
    bsdf_cyan = mat_cyan.node_tree.nodes.get("Principled BSDF")
    bsdf_cyan.inputs['Base Color'].default_value = (0.22, 0.90, 1.0, 1.0)
    if 'Emission Color' in bsdf_cyan.inputs:
        bsdf_cyan.inputs['Emission Color'].default_value = (0.22, 0.90, 1.0, 1.0)
        bsdf_cyan.inputs['Emission Strength'].default_value = 3.8

    # (5) 浅绿高亮材质 (标题标识)
    mat_green = bpy.data.materials.new("GlowGreen")
    mat_green.use_nodes = True
    bsdf_green = mat_green.node_tree.nodes.get("Principled BSDF")
    bsdf_green.inputs['Base Color'].default_value = (0.55, 0.92, 0.38, 1.0)
    if 'Emission Color' in bsdf_green.inputs:
        bsdf_green.inputs['Emission Color'].default_value = (0.55, 0.92, 0.38, 1.0)
        bsdf_green.inputs['Emission Strength'].default_value = 3.0

    # (6) 3D 正文字体材质 (柔白微发光)
    mat_text_body = bpy.data.materials.new("TextBody")
    mat_text_body.use_nodes = True
    bsdf_tb = mat_text_body.node_tree.nodes.get("Principled BSDF")
    bsdf_tb.inputs['Base Color'].default_value = (0.92, 0.95, 0.98, 1.0)
    if 'Emission Color' in bsdf_tb.inputs:
        bsdf_tb.inputs['Emission Color'].default_value = (0.92, 0.95, 0.98, 1.0)
        bsdf_tb.inputs['Emission Strength'].default_value = 1.4

    # (7) 暗灰细线材质 (分割线)
    mat_dim = bpy.data.materials.new("DimLine")
    mat_dim.use_nodes = True
    bsdf_dim = mat_dim.node_tree.nodes.get("Principled BSDF")
    bsdf_dim.inputs['Base Color'].default_value = (0.20, 0.26, 0.35, 1.0)

    # (8) 投影引线材质 (淡青发光)
    mat_lead_line = bpy.data.materials.new("LeadLine")
    mat_lead_line.use_nodes = True
    bsdf_lead = mat_lead_line.node_tree.nodes.get("Principled BSDF")
    bsdf_lead.inputs['Base Color'].default_value = (0.3, 0.7, 0.9, 1.0)
    if 'Emission Color' in bsdf_lead.inputs:
        bsdf_lead.inputs['Emission Color'].default_value = (0.3, 0.7, 0.9, 1.0)
        bsdf_lead.inputs['Emission Strength'].default_value = 2.0

    # =========================================================================
    # 3. 辅助建模工具函数
    # =========================================================================
    def create_tube_line(points, radius=0.04, mat=mat_orange, name="Line"):
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

    def create_rounded_rect(cx, cz, w, h, r, mat=mat_orange, y=0.0, radius=0.035, name="RoundedRect"):
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

    # 载入霞鹜文楷字体
    lxgw_font = None
    if os.path.exists(FONT_PATH):
        lxgw_font = bpy.data.fonts.load(FONT_PATH)

    def add_text_3d(text, location, scale=0.35, mat=mat_text_body, align='LEFT', extrude=0.02, name="Txt"):
        t_data = bpy.data.curves.new(name=name, type='FONT')
        t_data.body = text
        if lxgw_font:
            t_data.font = lxgw_font
        t_data.extrude = extrude
        t_data.bevel_depth = 0.005
        t_data.bevel_resolution = 3
        t_data.align_x = align
        t_obj = bpy.data.objects.new(name, t_data)
        t_obj.location = location
        t_obj.scale = (scale, scale, scale)
        t_obj.rotation_euler = (np.pi / 2, 0, 0)
        bpy.context.collection.objects.link(t_obj)
        t_obj.data.materials.append(mat)
        # 彻底关闭文字在金属反射中的倒影与投射阴影，呈现清爽高级质感
        if hasattr(t_obj, 'visible_glossy'):
            t_obj.visible_glossy = False
        if hasattr(t_obj, 'visible_shadow'):
            t_obj.visible_shadow = False
        return t_obj

    # =========================================================================
    # 4. 左侧精美板书卡片 (纯净黑夜背景，高雅橙金细发光外框)
    # =========================================================================
    CARD_CX = -5.0
    CARD_CZ = 4.8
    CARD_W = 8.6
    CARD_H = 10.3

    # (1) 外围橙金圆角大边框 (与参考图一模一样的高雅细线)
    create_rounded_rect(CARD_CX, CARD_CZ, CARD_W, CARD_H, r=0.45, mat=mat_orange, y=0.0, radius=0.038, name="CardBorder")

    # (2) 顶部标签药丸框：【2025年新高考Ⅱ卷 · 第14题】
    TITLE_W = 5.2
    TITLE_H = 0.9
    TITLE_Z = CARD_CZ + CARD_H/2 - 0.78
    create_rounded_rect(CARD_CX - 1.25, TITLE_Z, TITLE_W, TITLE_H, r=0.25, mat=mat_orange, y=0.0, radius=0.03, name="TitleBadge")
    add_text_3d("2025年新高考Ⅱ卷 · 第14题", (CARD_CX - 1.25, 0.0, TITLE_Z - 0.16), scale=0.42, mat=mat_text_body, align='CENTER')

    # (3) 【原题呈现】
    TEXT_L = CARD_CX - CARD_W/2 + 0.65
    add_text_3d("【原题呈现】", (TEXT_L, 0.0, 8.4), scale=0.40, mat=mat_orange)
    add_text_3d("一个底面半径为 4cm，高为 9cm 的封闭圆柱形容器", (TEXT_L, 0.0, 7.7), scale=0.31)
    add_text_3d("内有两个半径相等的铁球，则铁球半径的最大值为", (TEXT_L, 0.0, 7.1), scale=0.31)
    add_text_3d("_______ cm。", (TEXT_L, 0.0, 6.5), scale=0.31)

    # 分割线
    create_tube_line([(TEXT_L, 0.0, 6.15), (CARD_CX + CARD_W/2 - 0.65, 0.0, 6.15)], radius=0.015, mat=mat_dim, name="DivLine")

    # (4) 【空间降维通解模型】
    add_text_3d("【空间降维通解模型】", (TEXT_L, 0.0, 5.65), scale=0.40, mat=mat_green)
    add_text_3d("① 极值状态：两球紧贴容器底顶与侧壁，且彼此相切", (TEXT_L, 0.0, 5.0), scale=0.30)
    add_text_3d("② 剖面降维：沿两球心作空间纵剖面直角三角形", (TEXT_L, 0.0, 4.4), scale=0.30)
    add_text_3d("   高差 Δz = H - 2r = 9 - 2r", (TEXT_L, 0.0, 3.85), scale=0.29, mat=mat_cyan)
    add_text_3d("   水平差 Δρ = 2(R - r) = 8 - 2r", (TEXT_L, 0.0, 3.35), scale=0.29, mat=mat_cyan)
    add_text_3d("   球心距 L = 2r (相切几何约束)", (TEXT_L, 0.0, 2.85), scale=0.29, mat=mat_orange)
    add_text_3d("③ 空间勾股定理：(8 - 2r)² + (9 - 2r)² = (2r)²", (TEXT_L, 0.0, 2.25), scale=0.30, mat=mat_orange)
    add_text_3d("④ 化简求解：4r² - 68r + 145 = (2r - 5)(2r - 29) = 0", (TEXT_L, 0.0, 1.70), scale=0.29)
    add_text_3d("   ⇒ 得最大半径 r = 2.5 cm (r = 14.5 > 4 舍去)", (TEXT_L, 0.0, 1.20), scale=0.29)

    # (5) 底部参考答案药丸卡片
    ANS_W = 4.2
    ANS_H = 0.85
    ANS_Z = 0.35
    create_rounded_rect(CARD_CX - 1.8, ANS_Z, ANS_W, ANS_H, r=0.22, mat=mat_orange, y=0.0, radius=0.035, name="AnsBadge")
    add_text_3d("参考答案：2.5 cm", (CARD_CX - 1.8, 0.0, ANS_Z - 0.16), scale=0.42, mat=mat_cyan, align='CENTER')

    # =========================================================================
    # 5. 右侧 3D 几何演播区 (圆柱 + 极限状态双铁球 + 前置无遮挡降维勾股剖面)
    # =========================================================================
    CYL_X = 4.4
    CYL_Y = 0.0
    R_CYL = 4.0
    H_CYL = 9.0
    r_sphere = 2.5

    # (1) 圆柱上下底面圆环 (青蓝色发光圆环)
    def make_cylinder_ring(z_val, name="CylRing"):
        ths = np.linspace(0, 2*np.pi, 96)
        pts = [(CYL_X + R_CYL * np.cos(th), CYL_Y + R_CYL * np.sin(th), z_val) for th in ths]
        return create_tube_line(pts, radius=0.065, mat=mat_cyan, name=name)

    make_cylinder_ring(0.0, "CylBottomRing")
    make_cylinder_ring(H_CYL, "CylTopRing")

    # (2) 圆柱4根特征母线 (精心调整角度，避开右侧文字，不发生遮挡穿插)
    for ang in [np.radians(25), np.radians(110), np.radians(205), np.radians(295)]:
        p1 = (CYL_X + R_CYL * np.cos(ang), CYL_Y + R_CYL * np.sin(ang), 0.0)
        p2 = (CYL_X + R_CYL * np.cos(ang), CYL_Y + R_CYL * np.sin(ang), H_CYL)
        create_tube_line([p1, p2], radius=0.035, mat=mat_cyan, name="CylStrut")

    # (3) 半剖圆柱玻璃后壁 (从 -15° 到 195°，前侧敞开以展现金属球)
    curve_data = bpy.data.curves.new(name="CylBackGlass", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.extrude = H_CYL / 2
    ths = np.linspace(-np.pi/12, np.pi + np.pi/12, 64)
    spline = curve_data.splines.new('POLY')
    spline.points.add(len(ths)-1)
    for i, th in enumerate(ths):
        spline.points[i].co = (CYL_X + R_CYL * np.cos(th), CYL_Y + R_CYL * np.sin(th), H_CYL / 2, 1)
    glass_obj = bpy.data.objects.new("CylBackGlass", curve_data)
    bpy.context.collection.objects.link(glass_obj)
    glass_obj.data.materials.append(mat_glass)

    # (4) 两个物理级银白金属铁球 (极限位置)
    # 下球 O1: 靠左(x = CYL_X - 1.5), 踩底(z = 2.5)
    real_O1 = (CYL_X - 1.5, CYL_Y, 2.5)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r_sphere, segments=80, ring_count=40, location=real_O1)
    ball1 = bpy.context.active_object
    ball1.name = "IronBall_Lower"
    ball1.data.materials.append(mat_steel)
    bpy.ops.object.shade_smooth()

    # 上球 O2: 靠右(x = CYL_X + 1.5), 顶天(z = 6.5)
    real_O2 = (CYL_X + 1.5, CYL_Y, 6.5)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r_sphere, segments=80, ring_count=40, location=real_O2)
    ball2 = bpy.context.active_object
    ball2.name = "IronBall_Upper"
    ball2.data.materials.append(mat_steel)
    bpy.ops.object.shade_smooth()

    # 真实球心发光核与真实切点
    real_Mid = ((real_O1[0]+real_O2[0])/2, CYL_Y, (real_O1[2]+real_O2[2])/2)
    for pt in [real_O1, real_O2, real_Mid]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=pt)
        dt = bpy.context.active_object
        dt.data.materials.append(mat_orange)

    # 真实内部球心连线
    create_tube_line([real_O1, real_O2], radius=0.045, mat=mat_orange, name="InnerHypot")

    # =========================================================================
    # (5) 前置无遮挡【纵剖面降维直角三角形】(位于 y = -2.8，刚好在两球前表面前方)
    # =========================================================================
    FRONT_Y = -2.8
    tri_O1 = (CYL_X - 1.5, FRONT_Y, 2.5)
    tri_O2 = (CYL_X + 1.5, FRONT_Y, 6.5)
    tri_Corner = (CYL_X + 1.5, FRONT_Y, 2.5)
    tri_Mid = ((tri_O1[0]+tri_O2[0])/2, FRONT_Y, (tri_O1[2]+tri_O2[2])/2)

    # 投影引线：连接真实球心与前方投影三角形
    create_tube_line([real_O1, tri_O1], radius=0.022, mat=mat_lead_line, name="Lead_O1")
    create_tube_line([real_O2, tri_O2], radius=0.022, mat=mat_lead_line, name="Lead_O2")
    create_tube_line([real_Mid, tri_Mid], radius=0.022, mat=mat_lead_line, name="Lead_P")

    # 直角三角形三边 (粗发光管)
    # 斜边：L = 2r = 5 (橙金粗发光管)
    create_tube_line([tri_O1, tri_O2], radius=0.080, mat=mat_orange, name="Hypot_Front")
    # 底边：Δx = 8 - 2r = 3 (青蓝发光管)
    create_tube_line([tri_O1, tri_Corner], radius=0.060, mat=mat_cyan, name="Base_Front")
    # 竖直高：Δz = 9 - 2r = 4 (青蓝发光管)
    create_tube_line([tri_Corner, tri_O2], radius=0.060, mat=mat_cyan, name="Height_Front")

    # 直角拐角标记
    corner_sz = 0.45
    p_c_left = (tri_Corner[0] - corner_sz, FRONT_Y, tri_Corner[2])
    p_c_up = (tri_Corner[0], FRONT_Y, tri_Corner[2] + corner_sz)
    p_c_mid = (tri_Corner[0] - corner_sz, FRONT_Y, tri_Corner[2] + corner_sz)
    create_tube_line([p_c_left, p_c_mid, p_c_up], radius=0.035, mat=mat_cyan, name="RightAngleMark")

    # 关键节点发光小球
    for pt, col_mat in [(tri_O1, mat_orange), (tri_O2, mat_orange), (tri_Corner, mat_cyan), (tri_Mid, mat_orange)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=pt)
        node_dot = bpy.context.active_object
        node_dot.data.materials.append(col_mat)

    # (6) 3D 几何原位标注 (悬浮在 y = -3.2 黄金平面，严格避免遮挡与倒影)
    L_Y = -3.2
    # 顶点标注
    add_text_3d("O₁ (底球心)", (tri_O1[0] - 0.35, L_Y, tri_O1[2] - 0.15), scale=0.34, mat=mat_orange, align='RIGHT')
    add_text_3d("O₂ (顶球心)", (tri_O2[0] + 0.35, L_Y, tri_O2[2] + 0.15), scale=0.34, mat=mat_orange, align='LEFT')
    add_text_3d("相切点 P", (tri_Mid[0] - 0.35, L_Y, tri_Mid[2] + 0.35), scale=0.32, mat=mat_orange, align='RIGHT')

    # 三边参数标注
    add_text_3d("斜边: 2r = 5", (tri_Mid[0] + 0.35, L_Y, tri_Mid[2] - 0.25), scale=0.36, mat=mat_orange, align='LEFT')
    add_text_3d("水平跨度: 8 - 2r = 3", (CYL_X, L_Y, tri_Corner[2] - 0.65), scale=0.33, mat=mat_cyan, align='CENTER')
    add_text_3d("竖直高: 9 - 2r = 4", (tri_Corner[0] + 0.45, L_Y, 4.5), scale=0.33, mat=mat_cyan, align='LEFT')

    # 右侧展区正上方大标题：【空间纵剖面降维直角三角形】
    add_text_3d("【空间纵剖面降维直角三角形】", (CYL_X, L_Y, 9.8), scale=0.38, mat=mat_green, align='CENTER')

    # =========================================================================
    # 6. 专业摄影机系统 (微俯立体透视，黄金比例取景)
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

    # =========================================================================
    # 7. 演播室级工业灯光系统 (打造璀璨通透金属质感)
    # =========================================================================
    # 主光 1: 顶部柔光天幕
    bpy.ops.object.light_add(type='AREA', location=(CYL_X, -6.0, 16.0))
    top_light = bpy.context.active_object
    top_light.data.energy = 4000
    top_light.data.size = 15.0
    top_light.data.color = (0.95, 0.98, 1.0)
    top_light.rotation_euler = (np.radians(20), 0, 0)

    # 主光 2: 右前方柔光箱 (带出金属球拉丝高光)
    bpy.ops.object.light_add(type='AREA', location=(CYL_X + 7.0, -14.0, 7.5))
    front_light = bpy.context.active_object
    front_light.data.energy = 3600
    front_light.data.size = 9.0
    front_light.data.color = (1.0, 1.0, 1.0)
    front_light.rotation_euler = (np.radians(45), 0, np.radians(30))

    # 辅光 3: 左侧板书专用正向补光
    bpy.ops.object.light_add(type='AREA', location=(CARD_CX, -15.0, CARD_CZ))
    board_light = bpy.context.active_object
    board_light.data.energy = 1600
    board_light.data.size = 11.0
    board_light.data.color = (0.96, 0.98, 1.0)

    # 轮廓光 4: 球体后侧边缘逆光 (Rim Light)
    bpy.ops.object.light_add(type='SPOT', location=(CYL_X - 1.0, 9.0, 8.5))
    rim_light = bpy.context.active_object
    rim_light.data.energy = 4200
    rim_light.data.spot_size = np.radians(75)
    rim_light.rotation_euler = (np.radians(-135), 0, 0)

    print("Scene build complete!")

if __name__ == "__main__":
    build_scene()
    bpy.context.scene.render.filepath = OUT_IMG
    print(f"Rendering to: {OUT_IMG}...")
    bpy.ops.render.render(write_still=True)
    print("Render finished successfully!")
