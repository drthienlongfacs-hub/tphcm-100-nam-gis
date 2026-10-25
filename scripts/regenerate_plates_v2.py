#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regenerate the 4 Deep-Zoom Sector Engineering Map Plates (2200 x 1750 px) with:
1. Zero text overflow inside any callout card (auto-fitted font size per line + generous card width 600px).
2. Even vertical distribution of cards from y=104 to y=1520 (step=230px) so the map is visible between cards and leader lines are short and direct.
3. Direct on-road floating badges (Road Name | Width m | Completion Year) right on the road segments.
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from generate_deep_zoom_maps import build_basemap_bbox, draw_glowing_polyline, draw_header_and_footer, ARTIFACT_DIR

def load_multi_fonts():
    bold_candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf"
    ]
    reg_candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf"
    ]
    bold_fp = next((p for p in bold_candidates if os.path.exists(p)), None)
    reg_fp = next((p for p in reg_candidates if os.path.exists(p)), None)

    fonts = {
        "title": ImageFont.truetype(bold_fp, 27) if bold_fp else ImageFont.load_default(),
        "subtitle": ImageFont.truetype(reg_fp, 16) if reg_fp else ImageFont.load_default(),
        "legend_text": ImageFont.truetype(reg_fp, 13) if reg_fp else ImageFont.load_default(),
        "pill": ImageFont.truetype(bold_fp, 12) if bold_fp else ImageFont.load_default(),
        "bold_sizes": {},
        "reg_sizes": {}
    }
    for sz in range(10, 17):
        fonts["bold_sizes"][sz] = ImageFont.truetype(bold_fp, sz) if bold_fp else ImageFont.load_default()
        fonts["reg_sizes"][sz] = ImageFont.truetype(reg_fp, sz) if reg_fp else ImageFont.load_default()
    return fonts

def pick_fitting_font(draw, text, font_dict, max_width, start_size=14, min_size=10):
    for sz in range(start_size, min_size - 1, -1):
        f = font_dict[sz]
        if draw.textlength(text, font=f) <= max_width:
            return f
    return font_dict[min_size]

def draw_callout_card_v2(draw, box_xy, target_xy, accent_rgb, title, seg_line, width_line, sched_line, fonts):
    bx, by, bw, bh = box_xy
    tx, ty = target_xy
    cx = bx + bw // 2
    cy = by + bh // 2

    # Choose closest anchor on card edge to target_xy
    if tx < bx:
        ax = bx
        ay = max(by + 12, min(by + bh - 12, ty))
    elif tx > bx + bw:
        ax = bx + bw
        ay = max(by + 12, min(by + bh - 12, ty))
    else:
        ax = max(bx + 16, min(bx + bw - 16, tx))
        ay = by if ty < cy else by + bh

    # Leader line with dark halo + bright accent line
    draw.line([(ax, ay), (tx, ty)], fill=(0, 0, 0, 220), width=4)
    draw.line([(ax, ay), (tx, ty)], fill=(*accent_rgb, 250), width=2)

    # Target pin on the road/bridge
    draw.ellipse([tx - 7, ty - 7, tx + 7, ty + 7], fill=(8, 16, 28, 245), outline=(*accent_rgb, 255), width=3)
    draw.ellipse([tx - 3, ty - 3, tx + 3, ty + 3], fill=(255, 255, 255, 255))

    # Card shadow & body
    draw.rounded_rectangle([bx + 3, by + 4, bx + bw + 3, by + bh + 4], radius=8, fill=(0, 0, 0, 165))
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(9, 18, 32, 242), outline=(*accent_rgb, 240), width=2)
    draw.rounded_rectangle([bx, by, bx + 7, by + bh], radius=4, fill=(*accent_rgb, 255))

    max_txt_w = bw - 26
    px = bx + 14
    py = by + 8

    f_title = pick_fitting_font(draw, title, fonts["bold_sizes"], max_txt_w, start_size=15, min_size=11)
    draw.text((px, py), title, font=f_title, fill=(*accent_rgb, 255))
    py += 21

    s_txt = f"• Đoạn: {seg_line}"
    f_seg = pick_fitting_font(draw, s_txt, fonts["reg_sizes"], max_txt_w, start_size=13, min_size=10)
    draw.text((px, py), s_txt, font=f_seg, fill=(224, 236, 248, 255))
    py += 19

    w_txt = f"• Mặt cắt: {width_line}"
    f_w = pick_fitting_font(draw, w_txt, fonts["bold_sizes"], max_txt_w, start_size=13, min_size=10)
    draw.text((px, py), w_txt, font=f_w, fill=(255, 238, 128, 255))
    py += 19

    sch_txt = f"• Tiến độ: {sched_line}"
    f_sch = pick_fitting_font(draw, sch_txt, fonts["bold_sizes"], max_txt_w, start_size=13, min_size=10)
    draw.text((px, py), sch_txt, font=f_sch, fill=(118, 255, 163, 255))

def draw_on_road_pill(draw, xy, text, border_rgb, fonts):
    x, y = xy
    f = fonts["pill"]
    tw = int(draw.textlength(text, font=f))
    pw = tw + 14
    ph = 20
    bx = x - pw // 2
    by = y - ph // 2
    draw.rounded_rectangle([bx + 2, by + 2, bx + pw + 2, by + ph + 2], radius=5, fill=(0, 0, 0, 180))
    draw.rounded_rectangle([bx, by, bx + pw, by + ph], radius=5, fill=(8, 16, 30, 238), outline=(*border_rgb, 250), width=2)
    draw.text((bx + 7, by + 3), text, font=f, fill=(255, 255, 255, 255))

def get_card_y_positions(count=7, top_y=106, bottom_y=1560, card_h=88):
    step = (bottom_y - top_y - card_h) / max(1, count - 1)
    return [int(round(top_y + i * step)) for i in range(count)]

def build_all_4_plates():
    fonts = load_multi_fonts()
    W, H = 2200, 1750
    CW = 590
    LX = 20
    RX = W - CW - 20
    CH = 88
    ys = get_card_y_positions(7, top_y=104, bottom_y=1585, card_h=CH)

    # ==================== PLATE 1 ====================
    print("Rendering Plate 1 v2...")
    base, geo_to_px = build_basemap_bbox(10.875, 10.655, 106.585, 106.795, zoom=13, out_w=W, out_h=H, lyrs="y", darken=0.64)
    corridors_1 = [
        ([(10.8250, 106.7140), (10.8450, 106.7180), (10.8630, 106.7230), (10.8730, 106.7150)], (255, 193, 7), 8, False),
        ([(10.8010, 106.7110), (10.8120, 106.7120), (10.8250, 106.7140)], (0, 230, 118), 6, False),
        ([(10.8150, 106.6780), (10.8250, 106.7080), (10.8450, 106.7350), (10.8720, 106.7620)], (0, 200, 83), 6, False),
        ([(10.8010, 106.6620), (10.8060, 106.6450), (10.8180, 106.6320), (10.8420, 106.6150)], (0, 230, 118), 6, False),
        ([(10.7350, 106.6050), (10.7520, 106.6650), (10.7710, 106.7060), (10.7820, 106.7350), (10.7950, 106.7520)], (0, 230, 118), 7, False),
        ([(10.7685, 106.7065), (10.7610, 106.7120), (10.7535, 106.7185)], (0, 230, 118), 7, False),
        ([(10.7380, 106.6950), (10.7480, 106.6930), (10.7550, 106.6910), (10.7610, 106.6890)], (0, 229, 255), 7, False),
        ([(10.7460, 106.6420), (10.7350, 106.6450), (10.7220, 106.6480), (10.7100, 106.6520)], (0, 229, 255), 7, False),
        ([(10.7420, 106.7280), (10.7280, 106.7020), (10.7180, 106.6520), (10.6950, 106.5920)], (0, 200, 83), 8, False),
        ([(10.7280, 106.7020), (10.6950, 106.7050), (10.6620, 106.7180)], (255, 193, 7), 8, False),
        ([(10.7380, 106.6980), (10.7050, 106.6960), (10.6650, 106.6950)], (0, 230, 118), 6, False),
        ([(10.7420, 106.7420), (10.7280, 106.7480), (10.7120, 106.7420)], (0, 230, 118), 6, False),
        ([(10.7180, 106.6520), (10.6776, 106.6507), (10.6580, 106.6500)], (255, 193, 7), 7, False),
        ([(10.7420, 106.6050), (10.7150, 106.5980), (10.6950, 106.5920), (10.6750, 106.5880)], (255, 193, 7), 8, False),
        ([(10.7610, 106.7090), (10.7640, 106.7180)], (0, 229, 255), 7, False),
        ([(10.7580, 106.7230), (10.7450, 106.7260), (10.7320, 106.7250)], (0, 229, 255), 8, False),
        ([(10.7120, 106.7050), (10.7150, 106.7420), (10.7180, 106.7750)], (0, 229, 255), 7, True),
        ([(10.6780, 106.7420), (10.6650, 106.7620), (10.6580, 106.7750)], (0, 229, 255), 8, False),
        ([(10.7710, 106.6980), (10.7810, 106.7080), (10.8020, 106.7380), (10.8480, 106.7720)], (224, 64, 251), 5, True),
        ([(10.7820, 106.7480), (10.7710, 106.6980), (10.7850, 106.6720), (10.8020, 106.6450), (10.8280, 106.6250)], (224, 64, 251), 5, True),
        ([(10.7710, 106.6980), (10.7280, 106.7220), (10.6750, 106.7450)], (24, 255, 255), 5, True),
    ]
    for coords, col, w, dsh in corridors_1:
        base = draw_glowing_polyline(base, [geo_to_px(lat, lon) for lat, lon in coords], col, width=w, dashed=dsh)

    draw = ImageDraw.Draw(base)
    pills_1 = [
        (geo_to_px(10.8350, 106.7080), "Phạm Văn Đồng: 60m (12 làn)", (0, 200, 83)),
        (geo_to_px(10.7680, 106.6800), "Võ Văn Kiệt: 60m (10 làn)", (0, 230, 118)),
        (geo_to_px(10.7230, 106.6780), "Nguyễn Văn Linh: 120m (10 làn) • Hầm chui NHT đã xong", (0, 200, 83)),
        (geo_to_px(10.7720, 106.7000), "Ga Ngầm Bến Thành (Metro 1-2-3A-4)", (224, 64, 251)),
        (geo_to_px(10.7050, 106.6880), "Lê Văn Lương: 7m → 30-40m (6-8L)", (0, 230, 118)),
    ]
    for xy, txt, col in pills_1:
        draw_on_road_pill(draw, xy, txt, col, fonts)

    cards_1 = [
        ((LX, ys[0], CW, CH), geo_to_px(10.8060, 106.6450), (0, 230, 118),
         "1. ĐƯỜNG NỐI TRẦN QUỐC HOÀN – CỘNG HÒA & TRƯỜNG CHINH",
         "Lăng Cha Cả → Nhà ga T3 Tân Sơn Nhất → Mũi tàu Cộng Hòa – Âu Cơ (9,5 km)",
         "Đường nối T3: 29,5–48m (6 làn + cầu cạn) • Trường Chinh mở rộng: 18m → 60m (10 làn)",
         "Đường nối T3 & Nhà ga T3 (16.000 tỷ) ĐÃ XONG 4/2025 • Trường Chinh: 2026–2029"),
        ((LX, ys[1], CW, CH), geo_to_px(10.7900, 106.6620), (224, 64, 251),
         "2. METRO SỐ 2 (BẾN THÀNH – THAM LƯƠNG) & MỞ RỘNG CMT8",
         "Ga Bến Thành (Q.1) → Cách Mạng Tháng Tám → Trường Chinh → Tham Lương (11,1 km)",
         "Metro 2: 9,1km đi ngầm (9 ga ngầm) + 2km trên cao • Đường CMT8 mở rộng 30–35m (6 làn)",
         "Đã GPMB 99%, vốn Đầu tư công NQ188 (47.890 tỷ) • Khởi công 2025-2026 → Xong 2030"),
        ((LX, ys[2], CW, CH), geo_to_px(10.7480, 106.6280), (0, 230, 118),
         "3. TRỤC CHỢ LỚN: KINH DƯƠNG VƯƠNG – HỒNG BÀNG – LŨY BÁN BÍCH",
         "Vòng xoay An Lạc → Bến xe Miền Tây → Phú Lâm (Q.6) → Hồng Bàng / Âu Cơ",
         "Kinh Dương Vương: 60m (10 làn) • Lũy Bán Bích: 23–30m (6 làn) • Âu Cơ mở rộng 30m",
         "Kinh Dương Vương & Lũy Bán Bích đã xong • Mở rộng Âu Cơ & Ngầm Metro 3A, 6: 2026–2035"),
        ((LX, ys[3], CW, CH), geo_to_px(10.7350, 106.6050), (0, 230, 118),
         "4. ĐẠI LỘ VÕ VĂN KIỆT KÉO DÀI (NỐI VÀNH ĐAI 3) & VÀNH ĐAI 2 ĐOẠN 4",
         "Nút giao Quốc lộ 1 An Lạc → Tân Kiên → Vành đai 3 & Hồ Học Lãm – Phú Định",
         "Võ Văn Kiệt kéo dài (12,5km): Mở mới 60m (6–10 làn) • VĐ2 Đoạn 4 (5,3km): 14m → 60–67m",
         "Duyệt chủ trương 2026 (VVK kéo dài 19.400 tỷ; VĐ2 Đ4 16.400 tỷ) → Hoàn thành 2029–2030"),
        ((LX, ys[4], CW, CH), geo_to_px(10.7300, 106.6470), (0, 229, 255),
         "5. DỰ ÁN CẦU ĐƯỜNG BÌNH TIÊN (Q.6 – Q.8 – ĐẠI LỘ NGUYỄN VĂN LINH)",
         "Phạm Văn Chí (Q.6) → Vượt Kênh Tàu Hủ & Kênh Đôi (Q.8) → Nguyễn Văn Linh (3,66 km)",
         "Xây mới toàn tuyến: Cầu cạn trên cao rộng 16–30m (4–6 làn ô tô) + Đường song hành (tổng 30–40m)",
         "Đã duyệt ĐTC Ngân sách TP (Vốn 6.285 tỷ đồng) • Khởi công 01/07/2026 → Hoàn thành 2028"),
        ((LX, ys[5], CW, CH), geo_to_px(10.7050, 106.5950), (255, 193, 7),
         "6. QUỐC LỘ 1 CỬA NGÕ TÂY NAM (AN LẠC – BÌNH ĐIỀN – RANH LONG AN)",
         "Kinh Dương Vương (Bình Tân) → Nút giao Bình Thuận (Tân Kiên) → Cầu Bình Điền (9,62 km)",
         "Hiện trạng: 20–25m (4–6 làn, kẹt cứng) → Mở rộng lộ giới 60m (10–12 làn + Nút giao 3 tầng)",
         "Đã duyệt DA BOT Nghị quyết 98 (Vốn 16.285 tỷ đồng) • Khởi công 2026 → Hoàn thành 2028"),
        ((LX, ys[6], CW, CH), geo_to_px(10.6776, 106.6507), (255, 193, 7),
         "7. MỞ RỘNG QUỐC LỘ 50 & ĐƯỜNG VEN KÊNH ĐÔI (QUẬN 8 – BÌNH CHÁNH)",
         "Nguyễn Văn Linh → Song hành QL50 → Đa Phước → Cần Giuộc (6,92 km) & Kênh Đôi",
         "Quốc lộ 50: Hiện trạng 7–8m (2 làn) → Mở rộng lộ giới 34m (6 làn xe) • Kênh Đôi: 20–30m",
         "QL50 (1.498 tỷ) đang thi công nước rút → XONG 12/2026 • Bờ Bắc Kênh Đôi (7.300 tỷ) xong 2028"),

        ((RX, ys[0], CW, CH), geo_to_px(10.8480, 106.7190), (255, 193, 7),
         "8. QUỐC LỘ 13 (CẦU BÌNH TRIỆU → NGÃ TƯ BÌNH PHƯỚC → VĨNH BÌNH)",
         "Cầu Bình Triệu (Thủ Đức) → Hiệp Bình Phước (Vành đai 2) → Ranh Bình Dương (5,9 km)",
         "Hiện trạng: 19–22m (4–6 làn) → Mở rộng 60m (10–14 làn: Cầu cạn 4 làn + 8–10 làn dưới đất)",
         "Đã duyệt DA BOT Nghị quyết 98 (Vốn 21.724 tỷ đồng) • Khởi công Quý III/2026 → Hoàn thành 2028"),
        ((RX, ys[1], CW, CH), geo_to_px(10.8120, 106.7120), (0, 230, 118),
         "9. XÔ VIẾT NGHỆ TĨNH – ĐINH BỘ LĨNH & NÂNG CẦU BÌNH TRIỆU (BÌNH THẠNH)",
         "Ngã tư Hàng Xanh → Đài Liệt Sĩ → Bến xe Miền Đông cũ → Cầu Bình Triệu 1-2-3 (4,2 km)",
         "Hiện trạng: 16–21m (3–4 làn) → Mở rộng lộ giới 25–40m (6–8 làn) + Cầu Bình Triệu 3 (6 làn)",
         "Nâng tĩnh không Cầu Bình Triệu 1 xong 2026 • Mở rộng XVNT – Đinh Bộ Lĩnh (~10.000 tỷ): 2026–2030"),
        ((RX, ys[2], CW, CH), geo_to_px(10.7610, 106.7120), (0, 230, 118),
         "10. MỞ RỘNG ĐƯỜNG NGUYỄN TẤT THÀNH & CẦU THỦ THIÊM 3 (QUẬN 4)",
         "Cầu Khánh Hội → Dọc Cảng Nhà Rồng Khánh Hội → Cầu Tân Thuận 1 mới (2,5 km)",
         "Hiện trạng: 14m (4 làn, kẹt nặng) → Mở rộng 30–40m (8–10 làn) + Cầu Thủ Thiêm 3 (6 làn, 31m)",
         "Nguyễn Tất Thành & Cầu Tân Thuận 1 (~2.950 tỷ): Khởi công 7/2026 → Xong 2028 • Cầu TT3: 2027–2030"),
        ((RX, ys[3], CW, CH), geo_to_px(10.7520, 106.6920), (0, 229, 255),
         "11. DỰ ÁN CẦU ĐƯỜNG NGUYỄN KHOÁI (NỐI QUẬN 7 – QUẬN 4 – QUẬN 1)",
         "KDC Him Lam (Quận 7) → Vượt Kênh Tẻ → Nguyễn Khoái (Q.4) → Võ Văn Kiệt Q.1 (4,96 km)",
         "Cầu vượt trên cao rộng 6,5–25,5m (4–6 làn) + Mở rộng đường gom Nguyễn Khoái lên 26–35m",
         "Đầu tư công Ngân sách TP (Vốn 3.724 tỷ đồng) • Khởi công cuối 2025 – đầu 2026 → Hoàn thành 2028"),
        ((RX, ys[4], CW, CH), geo_to_px(10.7450, 106.7260), (0, 229, 255),
         "12. CẦU THỦ THIÊM 4 (THỦ THIÊM – QUẬN 7) & ĐƯỜNG ĐÀO TRÍ – HUỲNH TẤN PHÁT",
         "Nguyễn Cơ Thạch (Thủ Thiêm) → Vượt sông Sài Gòn → Huỳnh Tấn Phát – Nguyễn Văn Linh (2,16 km)",
         "Cầu Thủ Thiêm 4: Rộng 31–40m (8 làn xe) • Đường Đào Trí mở rộng 7m → 40m (6 làn) • HTP: 30m",
         "Cầu Thủ Thiêm 4 (~6.030 tỷ): Khởi công 2026-2027 → Hoàn thành 2028-2029 • Đào Trí: 2026–2029"),
        ((RX, ys[5], CW, CH), geo_to_px(10.6950, 106.7050), (255, 193, 7),
         "13. TRỤC BẮC–NAM NGUYỄN HỮU THỌ & ĐƯỜNG LÊ VĂN LƯƠNG (QUẬN 7 – NHÀ BÈ)",
         "Nguyễn Văn Linh → Nguyễn Hữu Thọ → Cao tốc Bến Lức Long Thành (8,6 km) & Lê Văn Lương (10,8 km)",
         "Nguyễn Hữu Thọ: 22m(4L) → 60m (10 làn: Cầu cạn 4 làn 80km/h + 6 làn dưới đất) • Lê Văn Lương: 30–40m",
         "Hầm chui NVL-NHT ĐÃ XONG 2025 • BOT Nguyễn Hữu Thọ (9.894 tỷ) khởi công 2026 → Hoàn thành 2028"),
        ((RX, ys[6], CW, CH), geo_to_px(10.6680, 106.7550), (0, 229, 255),
         "14. CẦU CẦN GIỜ, CẦU PHÚ MỸ 2 & ĐS TỐC ĐỘ CAO BẾN THÀNH – CẦN GIỜ",
         "Nhà Bè → Vượt sông Soài Rạp (Cầu Cần Giờ 7,3km) & Hoàng Quốc Việt → Nhơn Trạch (Cầu Phú Mỹ 2)",
         "Cầu Cần Giờ: Rộng 24,5m (6 làn, tĩnh không 55m) • Cầu Phú Mỹ 2: 8 làn • ĐS Cần Giờ: 350 km/h",
         "Cầu Cần Giờ (11.087 tỷ) & ĐS Cần Giờ (102.370 tỷ): Khởi công 2026 → Hoàn thành 2028–2029"),
    ]
    for box, tgt, acc, t, s, w, sch in cards_1:
        draw_callout_card_v2(draw, box, tgt, acc, t, s, w, sch, fonts)
    draw_header_and_footer(
        draw, W, H,
        "BẢN ĐỒ ZOOM CHI TIẾT 1: LÕI TRUNG TÂM SÀI GÒN – THỦ THIÊM – CHỢ LỚN – TÂN SƠN NHẤT – NAM SÀI GÒN",
        "Thông số kỹ thuật từng đoạn đường: Lộ giới hiện trạng (m/làn) → Quy hoạch mở rộng (m/làn), Cầu cạn trên cao, Cầu vượt sông & Mốc năm hoàn thành (2025–2030)",
        fonts
    )
    base.convert("RGB").save(f"{ARTIFACT_DIR}/Zoom_1_Trung_Tam_Sai_Gon_Thu_Thiem_Nam_Sai_Gon_Chi_Tiet.png", quality=95)

    # ==================== PLATE 2 ====================
    print("Rendering Plate 2 v2...")
    base, geo_to_px = build_basemap_bbox(10.935, 10.735, 106.700, 106.890, zoom=13, out_w=W, out_h=H, lyrs="y", darken=0.64)
    corridors_2 = [
        ([(10.7450, 106.7450), (10.7720, 106.7750), (10.7850, 106.7950), (10.8150, 106.7680), (10.8380, 106.7520), (10.8580, 106.7420), (10.8700, 106.7350)], (255, 23, 68), 8, False),
        ([(10.7390, 106.8551), (10.8050, 106.8380), (10.8500, 106.8350), (10.8950, 106.8320), (10.9250, 106.7650)], (213, 0, 0), 9, False),
        ([(10.7950, 106.7520), (10.7972, 106.7807), (10.7930, 106.8350), (10.7850, 106.8850)], (255, 82, 82), 8, False),
        ([(10.7990, 106.7270), (10.8250, 106.7580), (10.8500, 106.7760), (10.8750, 106.8080), (10.8950, 106.8320)], (0, 200, 83), 8, False),
        ([(10.7720, 106.7120), (10.7820, 106.7350), (10.7950, 106.7520), (10.8050, 106.7550)], (0, 230, 118), 7, False),
        ([(10.7850, 106.7320), (10.7900, 106.7420), (10.7950, 106.7520)], (0, 230, 118), 6, False),
        ([(10.7820, 106.7480), (10.7720, 106.7750), (10.7620, 106.7880)], (0, 230, 118), 7, False),
        ([(10.7680, 106.7820), (10.7580, 106.7980), (10.7450, 106.8200)], (0, 229, 255), 8, False),
        ([(10.7880, 106.7750), (10.7920, 106.8050), (10.8050, 106.8350)], (0, 230, 118), 6, False),
        ([(10.8020, 106.7620), (10.8020, 106.7850), (10.8030, 106.8120), (10.8050, 106.8350)], (0, 230, 118), 6, False),
        ([(10.8250, 106.7680), (10.8080, 106.7750), (10.7900, 106.7780)], (0, 230, 118), 6, False),
        ([(10.8480, 106.7730), (10.8420, 106.7950), (10.8150, 106.8050), (10.7920, 106.8050)], (0, 230, 118), 5, False),
        ([(10.8250, 106.7080), (10.8450, 106.7350), (10.8750, 106.7650), (10.9050, 106.7950)], (255, 193, 7), 7, False),
        ([(10.8700, 106.7350), (10.8950, 106.7420), (10.9280, 106.7450)], (255, 145, 0), 7, False),
        ([(10.7820, 106.7480), (10.7960, 106.8050), (10.7850, 106.8850)], (224, 64, 251), 5, True),
    ]
    for coords, col, w, dsh in corridors_2:
        base = draw_glowing_polyline(base, [geo_to_px(lat, lon) for lat, lon in coords], col, width=w, dashed=dsh)

    draw = ImageDraw.Draw(base)
    pills_2 = [
        (geo_to_px(10.8620, 106.7880), "Võ Nguyên Giáp: 113-153m (12-16 làn) + Metro 1", (0, 200, 83)),
        (geo_to_px(10.8350, 106.8350), "Vành đai 3 (CT.40): 63-74,5m (8 làn) • Thông xe 2026", (213, 0, 0)),
        (geo_to_px(10.7980, 106.7980), "Liên Phường: 30-60m (6 làn)", (0, 230, 118)),
        (geo_to_px(10.7800, 106.7620), "Đồng Văn Cống: 60m (10 làn)", (0, 230, 118)),
    ]
    for xy, txt, col in pills_2:
        draw_on_road_pill(draw, xy, txt, col, fonts)

    cards_2 = [
        ((LX, ys[0], CW, CH), geo_to_px(10.8850, 106.7420), (255, 145, 0),
         "1. ĐT.743, ĐT.743B & CAO TỐC TP.HCM – CHƠN THÀNH (DĨ AN – THUẬN AN)",
         "Nút giao Gò Dưa (Vành đai 2) → Sóng Thần → Ngã tư 550 → An Phú (19,5 km)",
         "Hiện hữu: Đã mở rộng 38–54m (6–8 làn + Cầu vượt 550) → Xây thêm Cầu cạn CT.30 (60m)",
         "Đường mặt đất 6–8 làn ĐÃ XONG • Cầu cạn nối Cao tốc Chơn Thành hoàn thành 2027"),
        ((LX, ys[1], CW, CH), geo_to_px(10.8580, 106.7420), (255, 23, 68),
         "2. VÀNH ĐAI 2 KHU ĐÔNG — KHÉP KÍN ĐOẠN 1, ĐOẠN 2 & ĐOẠN 3 (9,0 KM)",
         "Cầu Phú Hữu → Bình Thái (Võ Nguyên Giáp) → Phạm Văn Đồng → Gò Dưa (Quốc lộ 1)",
         "Mở mới khép kín lộ giới 67m (6 làn chính tuyến + 4–6 làn song hành + 3 nút giao 3 tầng)",
         "Đoạn 1 & 2 (13.800 tỷ) khởi công cuối 2025 – đầu 2026; Đoạn 3 tái khởi công → Xong 2027–2028"),
        ((LX, ys[2], CW, CH), geo_to_px(10.8550, 106.7480), (255, 193, 7),
         "3. ĐẠI LỘ PHẠM VĂN ĐỒNG – QUỐC LỘ 1K (THỦ ĐỨC – DĨ AN – BIÊN HÒA)",
         "Cầu Bình Lợi → Linh Tây → Ngã tư Linh Xuân (giao QL1) → Trung tâm Dĩ An (24,4 km)",
         "Phạm Văn Đồng: Hiện hữu 30–60m (6–12 làn) • Quốc lộ 1K: 42–60m (6–8 làn → nâng 8–10 làn)",
         "Đang khai thác hoàn chỉnh • Nút giao 3 tầng Phạm Văn Đồng – Vành đai 2 xong 2027–2028"),
        ((LX, ys[3], CW, CH), geo_to_px(10.8250, 106.7580), (0, 200, 83),
         "4. ĐẠI LỘ VÕ NGUYÊN GIÁP – XA LỘ HÀ NỘI & TUYẾN METRO SỐ 1",
         "Cầu Sài Gòn → Thảo Điền → Ngã tư Thủ Đức → Khu Công nghệ cao → Suối Tiên (15,7 km)",
         "Đã mở rộng lộ giới 113,5m – 153,5m (12 – 16 làn xe) + Tuyến Metro số 1 đi trên cao",
         "Metro số 1 (19,7km) ĐÃ VẬN HÀNH 12/2024 • Khép kín đường song hành Tân Vạn năm 2026"),
        ((LX, ys[4], CW, CH), geo_to_px(10.7880, 106.7420), (0, 230, 118),
         "5. ĐẠI LỘ MAI CHÍ THỌ, LƯƠNG ĐỊNH CỦA & GA ĐẦU MỐI ĐSQG THỦ THIÊM",
         "Hầm Thủ Thiêm → Trần Não → Lương Định Của → Nút giao 3 tầng An Phú (TP. Thủ Đức)",
         "Mai Chí Thọ: 100–140m (10–14 làn) • Lương Định Của: Mở rộng 30m (6 làn) • Ga Thủ Thiêm: 17,2ha",
         "Nút giao 3 tầng An Phú (3.408 tỷ: 2 hầm chui + cầu vượt) & Lương Định Của hoàn thành 2026"),
        ((LX, ys[5], CW, CH), geo_to_px(10.7720, 106.7750), (0, 230, 118),
         "6. ĐỒNG VĂN CỐNG, VÕ CHÍ CÔNG & ĐẠI NÚT GIAO 3 TẦNG MỸ THỦY",
         "Mai Chí Thọ → Đồng Văn Cống → Nút giao Mỹ Thủy → Võ Chí Công (Cầu Phú Mỹ)",
         "Đồng Văn Cống: Đã mở rộng 60m (10 làn) • Võ Chí Công (VĐ2): 67m (8–12 làn) + Nút Mỹ Thủy 3 tầng",
         "Đồng Văn Cống ĐÃ XONG 2024 • Nút giao 3 tầng Mỹ Thủy (3.622 tỷ) hoàn thành toàn bộ năm 2026"),
        ((LX, ys[6], CW, CH), geo_to_px(10.7580, 106.7980), (0, 229, 255),
         "7. MỞ RỘNG ĐƯỜNG NGUYỄN THỊ ĐỊNH & XÂY MỚI CẦU CÁT LÁI (THỦ ĐỨC – NHƠN TRẠCH)",
         "Giồng Ông Tố → Nút giao Mỹ Thủy → Cảng Cát Lái (5,2 km) → Cầu Cát Lái vượt sông Đồng Nai (11,6 km)",
         "Nguyễn Thị Định: 18m(4L) → Mở rộng 30m & 60–73m (8–14 làn) • Cầu Cát Lái: 33,5m (8 làn, tĩnh không 55m)",
         "Nguyễn Thị Định (6.875 tỷ) khởi công 2025-2026 → Xong 2027-2028 • Cầu Cát Lái (19.000 tỷ): 2026–2029"),

        ((RX, ys[0], CW, CH), geo_to_px(10.8950, 106.8320), (213, 0, 0),
         "8. VÀNH ĐAI 3 (CT.40) ĐOẠN CẦU CẠN LONG BÌNH – ĐẠI NÚT GIAO TÂN VẠN",
         "Cầu Nhơn Trạch → Cầu cạn Long Trường – Long Bình → Nút giao 3 tầng Tân Vạn → Dĩ An",
         "Giải phóng mặt bằng 63–74,5m (8 làn cao tốc + song hành); Cầu cạn trên cao 4–8 làn xuyên Thủ Đức",
         "Đang thi công nước rút (Nút giao Tân Vạn vốn 1.831 tỷ) → THÔNG XE TOÀN TUYẾN NĂM 2026"),
        ((RX, ys[1], CW, CH), geo_to_px(10.8420, 106.7950), (0, 230, 118),
         "9. ĐƯỜNG LÊ VĂN VIỆT – LÃ XUÂN OAI – HOÀNG HỮU NAM (KHU CÔNG NGHỆ CAO)",
         "Ngã tư Thủ Đức → Lê Văn Việt → Lã Xuân Oai (Cầu Tăng Nhơn Phú) → Bến xe Miền Đông Mới",
         "Hoàng Hữu Nam: Đã mở rộng 30m • Lã Xuân Oai: Hiện trạng 7–8m(2L) → Mở rộng 30m (6 làn)",
         "Hoàng Hữu Nam (30m) ĐÃ XONG 2025 • Cầu Tăng Nhơn Phú & Mở rộng Lã Xuân Oai 30m: 2026–2028"),
        ((RX, ys[2], CW, CH), geo_to_px(10.8080, 106.7750), (0, 230, 118),
         "10. MỞ RỘNG ĐƯỜNG ĐỖ XUÂN HỢP & CẦU NAM LÝ (XA LỘ HÀ NỘI – NGUYỄN DUY TRINH)",
         "Ngã tư Bình Thái (Võ Nguyên Giáp) → Cầu Nam Lý → Giao Cao tốc CT.29 → Nguyễn Duy Trinh (3,2 km)",
         "Cầu Nam Lý mới: Rộng 20m (4 làn) • Đường Đỗ Xuân Hợp: Mở rộng từ 7–12m lên lộ giới 30m (6 làn)",
         "Cầu Nam Lý (732 tỷ) ĐÃ THÔNG XE 10/2024 • Mặt đường Đỗ Xuân Hợp rộng 30m hoàn thành 2026–2027"),
        ((RX, ys[3], CW, CH), geo_to_px(10.8020, 106.7850), (0, 230, 118),
         "11. ĐƯỜNG LIÊN PHƯỜNG — TRỤC ĐÔNG TÂY MỚI KHU ĐÔNG (MAI CHÍ THỌ – VÀNH ĐAI 3)",
         "Mai Chí Thọ / Khu Thể thao Rạch Chiếc → Đỗ Xuân Hợp → Võ Chí Công (VĐ2) → Vành đai 3 (6,8 km)",
         "Khép kín toàn tuyến theo lộ giới quy hoạch 30m – 60m (Quy mô 6 làn xe cơ giới hoàn chỉnh)",
         "Đoạn mới nối thẳng ra Mai Chí Thọ ĐÃ THÔNG XE cuối 2025 • Đoạn cuối nối VĐ3: 2026–2028"),
        ((RX, ys[4], CW, CH), geo_to_px(10.7920, 106.8050), (0, 230, 118),
         "12. MỞ RỘNG ĐƯỜNG NGUYỄN DUY TRINH (VÀNH ĐAI 2 – PHÚ HỮU – LONG TRƯỜNG)",
         "Nút giao Vành đai 2 (Võ Chí Công) → Đường 990 (Cảng Phú Hữu) → Nguyễn Xiển (6,6 km)",
         "Hiện trạng: Chỉ rộng 7–8m (2 làn xe, điểm đen container) → Mở rộng lộ giới 30m (6 làn xe)",
         "Đã duyệt điều chỉnh chủ trương đầu tư (~2.600 tỷ đồng) • Khởi công 2026 → Hoàn thành 2028"),
        ((RX, ys[5], CW, CH), geo_to_px(10.7930, 106.8350), (255, 82, 82),
         "13. MỞ RỘNG CAO TỐC TP.HCM – LONG THÀNH – DẦU GIÂY (CT.29) LÊN 8–10 LÀN",
         "Nút giao An Phú → Vành đai 2 (4 km) → Vành đai 3 (Long Trường) → Cầu Long Thành – Sân bay LT",
         "Hiện trạng: 4 làn (26,5m) → Mở rộng lộ giới 60–116m (An Phú–VĐ3: 8 làn; VĐ3–Long Thành: 10 làn)",
         "Đoạn An Phú–VĐ2 khởi công cuối 2025; Toàn tuyến (~16.000 tỷ) hoàn thành năm 2027–2028"),
        ((RX, ys[6], CW, CH), geo_to_px(10.7880, 106.8550), (224, 64, 251),
         "14. ĐƯỜNG SẮT ĐÔ THỊ THỦ THIÊM – SÂN BAY LONG THÀNH & ĐS TỐC ĐỘ CAO BẮC–NAM",
         "Ga ĐSQG Thủ Thiêm → Dọc hành lang Cao tốc CT.29 & Vành đai 3 → Sân bay Quốc tế Long Thành",
         "ĐS Thủ Thiêm–Long Thành: 41,8km (20 ga, 120 km/h, đi 20 phút) • ĐS Bắc–Nam: 350 km/h",
         "ĐS Thủ Thiêm–Long Thành (84.750 tỷ): Khởi công 2026-2027 → Xong 2030 • ĐS Bắc–Nam: 2027–2035"),
    ]
    for box, tgt, acc, t, s, w, sch in cards_2:
        draw_callout_card_v2(draw, box, tgt, acc, t, s, w, sch, fonts)
    draw_header_and_footer(
        draw, W, H,
        "BẢN ĐỒ ZOOM CHI TIẾT 2: KHU ĐÔNG TP. THỦ ĐỨC – DĨ AN – THUẬN AN – CÁT LÁI – VÀNH ĐAI 2 & 3",
        "Chi tiết mặt cắt lộ giới (m), số làn xe hiện trạng vs mở rộng và mốc hoàn thành của toàn bộ mạng lưới đường bộ, nút giao 3 tầng, cầu lớn & đường sắt Khu Đông",
        fonts
    )
    base.convert("RGB").save(f"{ARTIFACT_DIR}/Zoom_2_Khu_Dong_Thu_Duc_Di_An_Cat_Lai_Vanh_Dai_2_3.png", quality=95)

    # ==================== PLATE 3 ====================
    print("Rendering Plate 3 v2...")
    base, geo_to_px = build_basemap_bbox(11.160, 10.690, 106.380, 106.840, zoom=11, out_w=W, out_h=H, lyrs="y", darken=0.64)
    corridors_3 = [
        ([(10.7051, 106.5136), (10.8200, 106.5150), (10.9500, 106.5550), (10.9850, 106.6650), (10.9350, 106.7650)], (213, 0, 0), 8, False),
        ([(10.7200, 106.4500), (10.8500, 106.3950), (11.0150, 106.4500), (11.1015, 106.5787), (11.1189, 106.6791), (11.0846, 106.8350)], (255, 109, 0), 8, True),
        ([(10.8420, 106.6150), (10.8750, 106.5850), (10.9050, 106.5580), (10.9650, 106.4850), (11.0250, 106.4050)], (255, 193, 7), 8, False),
        ([(10.9050, 106.5850), (10.9750, 106.5588), (11.0578, 106.3950)], (255, 61, 0), 8, False),
        ([(10.8250, 106.7140), (10.8750, 106.7150), (10.9212, 106.7139), (10.9836, 106.6661), (11.0859, 106.6247), (11.1500, 106.6280)], (255, 193, 7), 8, False),
        ([(10.8700, 106.7350), (10.9250, 106.7420), (10.9959, 106.7439), (11.0793, 106.7216), (11.1500, 106.7200)], (255, 61, 0), 8, False),
        ([(10.8950, 106.8320), (10.9550, 106.7550), (11.0250, 106.6850), (11.1350, 106.6450)], (255, 145, 0), 7, False),
        ([(11.0150, 106.6450), (11.0808, 106.6610), (11.1500, 106.7050)], (0, 230, 118), 6, False),
        ([(10.9743, 106.7782), (11.0535, 106.7528), (11.1335, 106.8260)], (0, 230, 118), 6, False),
        ([(10.9750, 106.6450), (10.9550, 106.5050), (10.9500, 106.4250)], (0, 230, 118), 6, False),
        ([(10.8420, 106.6150), (10.8550, 106.5650), (10.8480, 106.5050)], (0, 230, 118), 6, False),
        ([(10.7780, 106.6180), (10.7580, 106.5550), (10.7520, 106.4950)], (0, 230, 118), 6, False),
        ([(10.7350, 106.6050), (10.7450, 106.5550), (10.7650, 106.5120)], (0, 229, 255), 6, True),
        ([(10.8450, 106.7050), (10.9150, 106.6820), (10.9750, 106.6520), (11.0850, 106.5850)], (29, 233, 182), 6, True),
    ]
    for coords, col, w, dsh in corridors_3:
        base = draw_glowing_polyline(base, [geo_to_px(lat, lon) for lat, lon in coords], col, width=w, dashed=dsh)

    draw = ImageDraw.Draw(base)
    pills_3 = [
        (geo_to_px(11.0650, 106.6250), "QL13 Bình Dương: Mở rộng 64m (8 làn) • 2026-2027", (255, 193, 7)),
        (geo_to_px(10.9680, 106.6020), "Vành đai 3 (CT.40): 63-74,5m • Xong 2026", (213, 0, 0)),
        (geo_to_px(10.8920, 106.5720), "QL22: 20m → 60m (10 làn) • Xong 2028", (255, 193, 7)),
        (geo_to_px(10.7850, 106.5850), "QL1: Mở rộng 60m (10-12 làn) • Xong 2028", (255, 193, 7)),
    ]
    for xy, txt, col in pills_3:
        draw_on_road_pill(draw, xy, txt, col, fonts)

    cards_3 = [
        ((LX, ys[0], CW, CH), geo_to_px(11.0150, 106.4500), (255, 109, 0),
         "1. ĐƯỜNG VÀNH ĐAI 4 TP.HCM (CT.41 — CỦ CHI – BẾN CÁT – BẮC TÂN UYÊN)",
         "Đức Hòa → Củ Chi (vượt sông Sài Gòn tại Cầu Phú Thuận) → Bến Cát → Bắc Tân Uyên (~207 km)",
         "GPMB 1 lần theo lộ giới 74,5m – 120m (Quy hoạch 8 làn cao tốc; GĐ1 nền 25,5m, 4 làn + khẩn cấp)",
         "Đoạn Bình Dương khởi công 2025; Toàn tuyến (120.413 tỷ) khởi công 2026 → Hoàn thành 2028–2029"),
        ((LX, ys[1], CW, CH), geo_to_px(10.9750, 106.5588), (255, 61, 0),
         "2. CAO TỐC TP.HCM – MỘC BÀI (CT.31 — CỬA NGÕ TÂY BẮC ĐI TÂY NINH)",
         "Nút giao Vành đai 3 (Tân Thạnh Đông, Củ Chi) → Song song QL22 → Trảng Bàng – Mộc Bài (51 km)",
         "Mở mới hoàn toàn: Lộ giới GPMB 60–80m (6–8 làn, 120 km/h; GĐ1 nền 25,5m với 4 làn + khẩn cấp)",
         "Đã duyệt DA BOT + Ngân sách (Vốn 19.617 tỷ đồng) • Khởi công 2025–2026 → Hoàn thành 2027–2028"),
        ((LX, ys[2], CW, CH), geo_to_px(10.9550, 106.5050), (0, 230, 118),
         "3. TỈNH LỘ 8, ĐƯỜNG TỈNH 15 & CẦU PHÚ CƯỜNG 2 (CỦ CHI – THỦ DẦU MỘT)",
         "Cầu Phú Cường (Thủ Dầu Một) → Tỉnh lộ 8 xuyên Củ Chi (22,5 km) & ĐT.15 dọc sông Sài Gòn",
         "Theo Bảng QH08A (#68, #75): Hiện trạng 12–18m (2–4 làn) → Mở rộng lộ giới 30–40m (4–8 làn xe)",
         "Nâng cấp mở rộng Tỉnh lộ 8, ĐT.15 & xây mới đơn nguyên Cầu Phú Cường 2 giai đoạn 2026–2030"),
        ((LX, ys[3], CW, CH), geo_to_px(10.8750, 106.5850), (255, 193, 7),
         "4. QUỐC LỘ 22 — ĐƯỜNG XUYÊN Á (NÚT GIAO AN SƯƠNG → VÀNH ĐAI 3 / CỦ CHI)",
         "Nút giao 3 tầng An Sương (Q.12) → Hóc Môn → Nút giao Vành đai 3 Tân Thạnh Đông (8,03 km)",
         "Hiện trạng: 18–22m (4 làn) → Mở rộng lộ giới 60m (10 làn: 4 làn trục chính 80km/h + 7 cầu vượt)",
         "Đã duyệt DA BOT Nghị quyết 98 (Vốn 10.424 tỷ đồng) • Khởi công 2026 → Hoàn thành năm 2028"),
        ((LX, ys[4], CW, CH), geo_to_px(10.8550, 106.5650), (0, 230, 118),
         "5. ĐƯỜNG NGUYỄN VĂN BỨA & PHAN VĂN HỚN (HÓC MÔN – QUẬN 12 – ĐỨC HÒA)",
         "Ngã ba Giồng (Hóc Môn) → Nguyễn Văn Bứa → Cầu Lớn (8,5 km) & Song hành Phan Văn Hớn (8,5 km)",
         "Nguyễn Văn Bứa (#70 QH08A): 12m → Mở rộng 32–40m (6 làn + Cầu Lớn mới) • Phan Văn Hớn: 30–40m",
         "Dự án mở rộng Nguyễn Văn Bứa (Vốn 2.421 tỷ đồng) khởi công 2026 → Hoàn thành năm 2028"),
        ((LX, ys[5], CW, CH), geo_to_px(10.8200, 106.5150), (213, 0, 0),
         "6. ĐƯỜNG VÀNH ĐAI 3 (CT.40) ĐOẠN PHÍA TÂY (CỦ CHI – HÓC MÔN – BÌNH CHÁNH)",
         "Cầu Bình Gởi vượt sông Sài Gòn → Củ Chi (giao QL22, CT.31) → Hóc Môn → Bình Chánh (giao QL1)",
         "Giải phóng mặt bằng 1 lần lộ giới 63m – 74,5m (8 làn cao tốc + đường song hành hai bên 4–6 làn)",
         "Đang thi công đồng loạt nền đường và cầu vượt → THÔNG XE TOÀN TUYẾN TRONG NĂM 2026"),
        ((LX, ys[6], CW, CH), geo_to_px(10.7580, 106.5550), (0, 230, 118),
         "7. HƯƠNG LỘ 2, TRẦN VĂN GIÀU (TL.10), VÕ VĂN KIỆT KÉO DÀI & GA ĐSQG TÂN KIÊN",
         "Bình Tân – Tân Kiên – Bình Chánh (Cực Đầu mối Đường sắt, Y tế Kỹ thuật cao & Logistics Tây Nam)",
         "Trần Văn Giàu & Hương Lộ 2: 32–40m (6–8 làn) • Võ Văn Kiệt kéo dài: 60m • Ga Tân Kiên: 50 ha",
         "Hương Lộ 2 (Mã Lò–QL1) xong 2026 • Võ Văn Kiệt kéo dài (19.400 tỷ) & QL1 (60m): 2026–2030"),

        ((RX, ys[0], CW, CH), geo_to_px(11.1189, 106.6791), (255, 145, 0),
         "8. ĐẠI LỘ BÀU BÀNG – MỸ PHƯỚC – TÂN VẠN & ĐT.741 (BÌNH DƯƠNG)",
         "Nút giao Tân Vạn (Dĩ An) → Thuận An → Thủ Dầu Một → Bến Cát (Mỹ Phước) → Bàu Bàng (64 km)",
         "Mỹ Phước – Tân Vạn (#40 QH08A): Lộ giới 64m (6–10 làn xe) • ĐT.741 (#1 QH08A): 36–54m (6 làn)",
         "Chính tuyến 6–10 làn đang vận hành • Nâng cấp đoạn trùng Vành đai 3 & các cầu vượt xong 2026"),
        ((RX, ys[1], CW, CH), geo_to_px(11.0793, 106.7216), (255, 61, 0),
         "9. CAO TỐC TP.HCM – THỦ DẦU MỘT – CHƠN THÀNH (CT.30 — 60,3 KM)",
         "Nút giao Gò Dưa (Vành đai 2 Thủ Đức) → Thuận An, Tân Uyên, Bắc Tân Uyên, Phú Giáo, Bàu Bàng",
         "Lộ giới quy hoạch 60m (6 làn cao tốc 100 km/h + đường song hành; GĐ1 4 làn + làn khẩn cấp 25,5m)",
         "Đã khởi công xây dựng năm 2025 (Vốn 17.408 tỷ đồng) → Hoàn thành thông xe năm 2027"),
        ((RX, ys[2], CW, CH), geo_to_px(11.0535, 106.7528), (0, 230, 118),
         "10. TRỤC CÔNG NGHIỆP TÂN UYÊN – VSIP III: ĐT.746, ĐT.747 & ĐT.742",
         "Thuận An / Dĩ An → Tân Uyên → KCN VSIP III → Bắc Tân Uyên (Mục #4, #14, #21-23 Bảng QH08A)",
         "Hiện trạng: 15–28m (2–4 làn) → Đang mở rộng lên lộ giới 38m – 54m (Quy mô 6 – 8 làn xe cơ giới)",
         "Đoạn ĐT.746 qua VSIP III hoàn thành 2025–2026 • Toàn mạng lưới hoàn thiện 6–8 làn năm 2026–2028"),
        ((RX, ys[3], CW, CH), geo_to_px(10.9836, 106.6661), (255, 193, 7),
         "11. QUỐC LỘ 13 ĐẠI LỘ BÌNH DƯƠNG (VĨNH PHÚ – THUẬN AN – THỦ DẦU MỘT – BẾN CÁT)",
         "Cầu Vĩnh Bình → Ngã tư Bình Hòa → Trung tâm Thủ Dầu Một → Đại học Quốc tế Miền Đông / Bến Cát",
         "Hiện trạng: 6 làn xe (32m) → Đang thi công mở rộng lên 8 làn xe cơ giới, lộ giới 64m + cầu vượt",
         "Dự án mở rộng lên 8 làn xe (64m, vốn 6.255 tỷ) đang thi công → Hoàn thành năm 2026–2027"),
        ((RX, ys[4], CW, CH), geo_to_px(10.9750, 106.6520), (29, 233, 182),
         "12. ĐẠI LỘ VEN SÔNG SÀI GÒN (BỜ ĐÔNG BÌNH DƯƠNG & BỜ TÂY CỦ CHI – HÓC MÔN)",
         "Bờ Tây (Bình Thạnh – Q.12 – Hóc Môn – Củ Chi: 78 km) & Bờ Đông (Thuận An – Thủ Dầu Một – Bến Cát: 98 km)",
         "Mặt cắt quy hoạch 32m – 64m (Quy mô 4 – 8 làn xe cơ giới + Công viên bờ sông & Tuyến LRT số 11)",
         "Dự án liên vùng trọng điểm (Mục #42 QH08A) → Khởi công các phân đoạn chính giai đoạn 2026–2030"),
        ((RX, ys[5], CW, CH), geo_to_px(10.9250, 106.7420), (224, 64, 251),
         "13. METRO SỐ 1 KÉO DÀI ĐI TP MỚI BÌNH DƯƠNG & ĐƯỜNG SẮT BÀU BÀNG – CÁI MÉP",
         "Ga Suối Tiên → Dĩ An → Thuận An → Trung tâm Thành phố Mới Bình Dương (~30 km) & Ga An Bình",
         "Đường sắt đô thị trên cao khổ 1.435mm (110 km/h) + Đường sắt quốc gia đôi Bàu Bàng–An Bình–Cái Mép",
         "Metro Suối Tiên – Bình Dương (~51.000 tỷ): Khởi công 2027 → Hoàn thành ~2031–2032"),
        ((RX, ys[6], CW, CH), geo_to_px(10.8880, 106.7620), (0, 229, 255),
         "14. TỔ HỢP GA ĐẦU MỐI ĐSQG AN BÌNH – SÓNG THẦN & CỤM CẢNG CẠN ICD BÌNH DƯƠNG",
         "Ga An Bình – Sóng Thần (Dĩ An) + Cụm Cảng cạn ICD An Sơn, Thạnh Phước, Thái Hòa, Tân Uyên, Bến Cát",
         "Đầu mối đường sắt liên vận quốc tế lớn nhất miền Nam kết nối thẳng hàng công nghiệp ra Cảng Cái Mép",
         "Nâng cấp Ga Sóng Thần xong 2026 • Xây mới Tổ hợp Ga An Bình & ĐS Biên Hòa–Vũng Tàu: 2027–2035"),
    ]
    for box, tgt, acc, t, s, w, sch in cards_3:
        draw_callout_card_v2(draw, box, tgt, acc, t, s, w, sch, fonts)
    draw_header_and_footer(
        draw, W, H,
        "BẢN ĐỒ ZOOM CHI TIẾT 3: CỬA NGÕ TÂY BẮC – CỦ CHI – HÓC MÔN – BÌNH CHÁNH – THỦ DẦU MỘT – BẾN CÁT",
        "Chi tiết mặt cắt lộ giới (m), số làn hiện trạng vs mở rộng và tiến độ hoàn thành của QL22, QL13, QL1, CT.30, CT.31, Vành đai 3, Vành đai 4 & Đường tỉnh Bình Dương",
        fonts
    )
    base.convert("RGB").save(f"{ARTIFACT_DIR}/Zoom_3_Cua_Ngo_Tay_Bac_Binh_Duong_Quoc_Lo_1_13_22_50.png", quality=95)

    # ==================== PLATE 4 ====================
    print("Rendering Plate 4 v2...")
    base, geo_to_px = build_basemap_bbox(10.740, 10.310, 106.720, 107.520, zoom=11, out_w=W, out_h=H, lyrs="y", darken=0.64)
    corridors_4 = [
        ([(10.6580, 106.7350), (10.6550, 106.7950), (10.6600, 106.8600), (10.6650, 106.9950)], (255, 23, 68), 8, False),
        ([(10.6780, 106.7420), (10.6520, 106.7780), (10.5950, 106.8250), (10.5150, 106.8750), (10.4150, 106.9450)], (0, 230, 118), 7, False),
        ([(10.6750, 106.7450), (10.5650, 106.8450), (10.4150, 106.9450)], (224, 64, 251), 5, True),
        ([(10.3980, 106.9680), (10.3820, 107.0150), (10.3680, 107.0650)], (0, 229, 255), 8, True),
        ([(10.6450, 106.9750), (10.6050, 107.0180), (10.5708, 107.0369), (10.5217, 107.0347)], (0, 229, 255), 7, False),
        ([(10.5708, 107.0369), (10.5780, 107.0850)], (0, 230, 118), 6, False),
        ([(10.7200, 107.0100), (10.6644, 107.0433), (10.5792, 107.0658), (10.5050, 107.1450), (10.4150, 107.1250), (10.3550, 107.0850)], (255, 193, 7), 7, False),
        ([(10.7295, 107.0092), (10.6300, 107.0650), (10.5250, 107.1550), (10.4200, 107.1450), (10.3650, 107.0950)], (213, 0, 0), 8, False),
        ([(10.5800, 107.0500), (10.7200, 107.0800)], (255, 109, 0), 7, True),
        ([(10.4550, 107.0950), (10.4050, 107.1450), (10.4130, 107.2265), (10.4308, 107.2794), (10.4750, 107.3850), (10.5050, 107.4650)], (0, 230, 118), 8, False),
        ([(10.7300, 107.0400), (10.6800, 107.1800), (10.6000, 107.3200), (10.4850, 107.4250)], (255, 82, 82), 7, True),
        ([(10.5050, 107.1750), (10.4852, 107.2639), (10.5117, 107.3618), (10.5362, 107.4198), (10.5500, 107.4850)], (255, 193, 7), 6, False),
        ([(10.6298, 107.0754), (10.6566, 107.2314), (10.6480, 107.3850), (10.6426, 107.4950)], (0, 230, 118), 5, False),
    ]
    for coords, col, w, dsh in corridors_4:
        base = draw_glowing_polyline(base, [geo_to_px(lat, lon) for lat, lon in coords], col, width=w, dashed=dsh)

    draw = ImageDraw.Draw(base)
    pills_4 = [
        (geo_to_px(10.6600, 106.8900), "CT Bến Lức – Long Thành: 4→8 làn • Xong 2026", (255, 23, 68)),
        (geo_to_px(10.5450, 106.8650), "ĐS Cần Giờ 350km/h & Rừng Sác (40-120m)", (224, 64, 251)),
        (geo_to_px(10.5850, 107.1150), "CT Biên Hòa – Vũng Tàu (CT.28): Thông xe 2026", (213, 0, 0)),
        (geo_to_px(10.4150, 107.2265), "Ven biển ĐT.994: Mở rộng 40,5-54m (6-8 làn) • Xong 2026-2027", (0, 230, 118)),
    ]
    for xy, txt, col in pills_4:
        draw_on_road_pill(draw, xy, txt, col, fonts)

    cards_4 = [
        ((LX, ys[0], CW, CH), geo_to_px(10.6650, 106.7620), (0, 229, 255),
         "1. CẦU CẦN GIỜ (NHÀ BÈ – BÌNH KHÁNH) & CAO TỐC BẾN LỨC – LONG THÀNH",
         "Vượt sông Soài Rạp & Lòng Tàu (Cầu Cần Giờ 7,3km + Cầu Bình Khánh & Phước Khánh CT.01)",
         "Cầu Cần Giờ: Rộng 24,5m (6 làn, tĩnh không 55m) • Cao tốc CT.01: 4 → 8 làn (lộ giới 32,5–60m)",
         "Cao tốc Bến Lức – Long Thành THÔNG TOÀN TUYẾN 2026 • Cầu Cần Giờ (11.087 tỷ): 2026–2029"),
        ((LX, ys[1], CW, CH), geo_to_px(10.6150, 107.0150), (0, 229, 255),
         "2. CẦU PHƯỚC AN, ĐƯỜNG 991B & ĐƯỜNG LIÊN CẢNG CÁI MÉP – THỊ VẢI (ĐT.995)",
         "Cao tốc Bến Lức Long Thành → Cầu Phước An (4,38 km) → Liên cảng Cái Mép (21,3 km) → Đường 991B",
         "Cầu Phước An: Rộng 27m (6 làn, tĩnh không 55m) • Đường 991B: 35–68m (4–6 làn) • ĐT.995: 50–68m (6–10 làn)",
         "Đường 991B (3.875 tỷ) XONG 2026 • Cầu Phước An (4.877 tỷ) XONG 2027 • Nâng cấp ĐT.995: 2026–2030"),
        ((LX, ys[2], CW, CH), geo_to_px(10.5650, 106.8450), (224, 64, 251),
         "3. ĐS TỐC ĐỘ CAO BẾN THÀNH – CẦN GIỜ (350 KM/H) & ĐẠI LỘ RỪNG SÁC",
         "Quận 1 – Phú Mỹ Hưng – Nhà Bè – Rừng Sác – Đô thị Lấn biển Cần Giờ (48,7 km)",
         "ĐS tốc độ cao: Đi trên cao 100%, 250–350 km/h (đi 16 phút) • Đường Rừng Sác: 6–8 làn (40–120m)",
         "Nút giao Rừng Sác – CT.01 (2.400 tỷ) xong 2028 • ĐS Cần Giờ (102.370 tỷ): Khởi công 2026 → Xong 2028-2029"),
        ((LX, ys[3], CW, CH), geo_to_px(10.5250, 107.0180), (255, 193, 7),
         "4. CẢNG NƯỚC SÂU CÁI MÉP – THỊ VẢI, KHU THƯƠNG MẠI TỰ DO (FTZ) & CẢNG LONG SƠN",
         "Phường Phú Mỹ – Tân Phước – Đảo Long Sơn (Tổ hợp Cảng Cửa ngõ Quốc tế Đặc biệt & FTZ 3.749 ha)",
         "Tàu 250.000 DWT • Kết nối Vành đai 4 (CT.41), Quốc lộ 51 (6–10 làn) & Đường sắt Biên Hòa – Vũng Tàu",
         "Cảng Gemalink/CMIT đang khai thác • Bến Cái Mép Hạ (50.820 tỷ) & FTZ Cái Mép Hạ triển khai 2026–2030"),
        ((LX, ys[4], CW, CH), geo_to_px(10.4950, 106.9850), (0, 229, 255),
         "5. SIÊU CẢNG TRUNG CHUYỂN QUỐC TẾ CẦN GIỜ (CÙ LAO GÒ CON CHÓ)",
         "Cửa sông Cái Mép – Thị Vải (Xã Thạnh An, Cần Giờ) — Trung tâm Hàng hải Quốc tế",
         "Chiều dài bến 7,2 km (570 ha) • Đón siêu tàu mẹ 250.000 DWT (24.000 TEU) • Công suất 16,9 triệu TEU",
         "Thủ tướng đã phê duyệt chủ trương (1/2025, vốn 113.500 tỷ) • Khởi công GĐ1 2026 → Vận hành 2027–2030"),
        ((LX, ys[5], CW, CH), geo_to_px(10.4150, 106.9450), (0, 230, 118),
         "6. SIÊU ĐÔ THỊ DU LỊCH LẤN BIỂN CẦN GIỜ (2.870 HA) & CẢNG KHÁCH QUỐC TẾ",
         "Xã Cần Giờ (Long Hòa – Cần Thạnh) — Cực Đô thị Biển Sinh thái & Tài chính Xanh ESG",
         "Quy mô 2.870 ha (4 phân khu A-B-C-D, biển hồ 443 ha, tháp 108 tầng, cảng du thuyền & Depot Metro)",
         "Đã khởi công lấn biển & hạ tầng năm 2025 (Vốn ~217.050 tỷ đồng) → Hoàn thành giai đoạn 2028–2032"),
        ((LX, ys[6], CW, CH), geo_to_px(10.3820, 107.0150), (0, 229, 255),
         "7. CẦU / HẦM VƯỢT BIỂN CẦN GIỜ – VŨNG TÀU (BĂNG QUA VỊNH GÀNH RÁI)",
         "Mũi Cần Thạnh (Cần Giờ) → Vượt vịnh Gành Rái (14,5 km) → Sao Mai – Bến Đình (Phường Vũng Tàu)",
         "Cầu vượt biển kết hợp hầm dìm dưới luồng hàng hải: 6 làn cơ giới đường bộ + 2 làn Đường sắt Đô thị",
         "Công trình chiến lược 100 năm khép kín Vành đai Ven biển TP.HCM • Định hướng đầu tư 2030–2045"),

        ((RX, ys[0], CW, CH), geo_to_px(10.6300, 107.0650), (213, 0, 0),
         "8. CAO TỐC BIÊN HÒA – VŨNG TÀU (CT.28 — SÂN BAY LONG THÀNH – PHÚ MỸ – BÀ RỊA)",
         "Sân bay Quốc tế Long Thành → Thị xã Phú Mỹ (Cảng Cái Mép) → TP. Bà Rịa (53,7 km)",
         "Lộ giới GPMB 32m – 67m: Giai đoạn 1 quy mô 4–6 làn xe cao tốc (100 km/h) → Hoàn chỉnh 6–8 làn",
         "Đoạn qua Bà Rịa – Vũng Tàu (19,5 km) ĐÃ THÔNG XE KỸ THUẬT 4/2026 • Toàn tuyến hoàn thành 2026"),
        ((RX, ys[1], CW, CH), geo_to_px(10.6566, 107.2314), (0, 230, 118),
         "9. TRỤC ĐÔNG–TÂY CHÂU ĐỨC – XUYÊN MỘC: ĐT.991, ĐT.992 & QUỐC LỘ 56",
         "Mỹ Xuân (Cái Mép) → Ngãi Giao (Châu Đức) → Bình Châu (ĐT.991, 68 km) & Quốc lộ 56 (33 km)",
         "Theo Bảng QH08A (#45-46, II.10): Mở rộng lên 4 – 6 làn xe cơ giới + đường gom (lộ giới 36m – 54m)",
         "Tuyến tránh QL56 Bà Rịa đã hoàn thành • Mở rộng đồng bộ ĐT.991 & ĐT.992 giai đoạn 2026–2030"),
        ((RX, ys[2], CW, CH), geo_to_px(10.6000, 107.3200), (255, 82, 82),
         "10. CAO TỐC ĐÔ THỊ LONG THÀNH – HỒ TRÀM (TRỤC KẾT NỐI THẲNG SÂN BAY – BIỂN)",
         "Sân bay Quốc tế Long Thành / Phú Mỹ → Châu Đức → Xuyên Mộc → Khu du lịch biển Hồ Tràm (~45 km)",
         "Mở mới hoàn toàn (Mục I.8 Bảng QH08A): Cao tốc đô thị 4 – 6 làn xe (lộ giới 50m – 60m, 100 km/h)",
         "Rút ngắn thời gian từ Sân bay Long Thành đi Hồ Tràm còn 30 phút • Kế hoạch đầu tư 2026–2030"),
        ((RX, ys[3], CW, CH), geo_to_px(10.4650, 107.1750), (0, 230, 118),
         "11. ĐƯỜNG TRỤC CHÍNH BÀ RỊA – VŨNG TÀU (ĐT.994B — CAO TỐC ĐÔ THỊ VÀO VŨNG TÀU)",
         "Cuối Cao tốc CT.28 (QL56 Bà Rịa) → Vũng Vằn → Cầu Cửa Lấp → Đường 2/9 – 3/2 Vũng Tàu (16,4 km)",
         "Mục #59 QH08A: Cầu cạn cao tốc đô thị 4–6 làn ở giữa + Đường song hành (Tổng 6–10 làn, lộ giới 68–100m)",
         "Đang thi công đồng loạt 3 dự án thành phần (Vốn 13.900 tỷ đồng) → Hoàn thành năm 2026–2027"),
        ((RX, ys[4], CW, CH), geo_to_px(10.4280, 107.0580), (255, 193, 7),
         "12. SÂN BAY GÒ GĂNG, CẢNG TÀU KHÁCH QUỐC TẾ VŨNG TÀU & ĐƯỜNG 30/4 – 2/9",
         "Đảo Gò Găng (248,5 ha) & Bãi Trước – Bãi Sau Phường Vũng Tàu (Trung tâm Du lịch Biển Quốc tế)",
         "Sân bay Gò Găng cấp 3C • Cảng khách quốc tế đón siêu tàu 225.000 GT • Đường 30/4 & 2/9: 6–10 làn",
         "Chỉnh trang trục Thùy Vân Bãi Sau (1.094 tỷ) ĐÃ XONG 2025 • Cảng khách & Sân bay Gò Găng: 2026–2030"),
        ((RX, ys[5], CW, CH), geo_to_px(10.4308, 107.2794), (0, 230, 118),
         "13. ĐẠI LỘ VEN BIỂN ĐT.994 (VŨNG TÀU – LONG HẢI – PHƯỚC HẢI – HỒ TRÀM – BÌNH CHÂU)",
         "Long Sơn / Cầu Cửa Lấp 2 → Long Hải → Phước Hải → Lộc An → Hồ Tràm → Bình Châu (76,86 km)",
         "Hiện trạng cũ: 12m (2 làn) → Đang thi công mở rộng toàn tuyến lên lộ giới 40,5m – 54m (6 – 8 làn xe)",
         "Đang thi công 8 dự án thành phần trên toàn tuyến (Vốn ~7.000 tỷ) → HOÀN THÀNH NĂM 2026–2027"),
        ((RX, ys[6], CW, CH), geo_to_px(10.4850, 107.3850), (0, 229, 255),
         "14. CỤM TRỤC BIỂN ĐÔNG: QUỐC LỘ 55, ĐT.998 (TL.328), ĐT.999 (TL.329) & SÂN BAY ĐẤT ĐỎ",
         "Bà Rịa – Đất Đỏ – Xuyên Mộc – Hồ Tràm – Bình Châu & Sân bay chuyên dùng Lộc An – Đất Đỏ (244 ha)",
         "Quốc lộ 55, ĐT.998 (TL.328) & ĐT.999 (TL.329): Mở rộng từ 2 làn lên 4 – 6 làn xe (lộ giới 32–45m)",
         "Dự án mở rộng TL.328 & TL.329 hoàn thành 2026–2028 • Tuyến LRT Du lịch biển Vũng Tàu–Hồ Tràm: 2030–2045"),
    ]
    for box, tgt, acc, t, s, w, sch in cards_4:
        draw_callout_card_v2(draw, box, tgt, acc, t, s, w, sch, fonts)
    draw_header_and_footer(
        draw, W, H,
        "BẢN ĐỒ ZOOM CHI TIẾT 4: HÀNH LANG BIỂN CẦN GIỜ – CÁI MÉP THỊ VẢI – PHÚ MỸ – BÀ RỊA – VŨNG TÀU – HỒ TRÀM",
        "Chi tiết mặt cắt lộ giới (m), số làn xe hiện trạng vs mở rộng và tiến độ hoàn thành của Cầu Cần Giờ, ĐS 350km/h, Cầu Phước An, CT.28, ĐT.994B (100m) & Ven biển ĐT.994 (54m)",
        fonts
    )
    base.convert("RGB").save(f"{ARTIFACT_DIR}/Zoom_4_Cang_Bien_Can_Gio_Cai_Mep_Phu_My_Vung_Tau_Ho_Tram.png", quality=95)
    print("All 4 v2 plates rendered!")

if __name__ == "__main__":
    build_all_4_plates()
