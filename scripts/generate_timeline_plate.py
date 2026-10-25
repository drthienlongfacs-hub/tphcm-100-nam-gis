#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Overlay_5_Lo_Trinh_Xay_Dung_Timeline_2025_2050.png (2200 x 1750 px):
Visualizing the Year-by-Year Construction & Completion Roadmap (2024-2025 -> 2026 -> 2027 -> 2028 -> 2029-2030 -> 2035 -> 2050)
on top of the real Google Maps basemap of Greater HCMC.
"""

import os
import json
from PIL import Image, ImageDraw
from generate_deep_zoom_maps import build_basemap_bbox, draw_glowing_polyline
from regenerate_plates_v2 import load_multi_fonts, draw_callout_card_v2, draw_on_road_pill, get_card_y_positions

ARTIFACT_DIR = "/Users/longlinh/.gemini/antigravity/brain/624ff7d6-9c4e-45bc-b91e-8475160775c8"
SCRATCH_DIR = f"{ARTIFACT_DIR}/scratch"

def cohort_color(end_year):
    if end_year <= 2025:
        return (0, 230, 118)     # Bright Green: Đã hoàn thành 2024-2025
    elif end_year == 2026:
        return (0, 229, 255)     # Cyan: Về đích năm 2026 (Vành đai 3, CT.01, CT.28, QL50, An Phú, Mỹ Thủy, Sân bay LT)
    elif end_year == 2027:
        return (255, 214, 0)     # Gold: Về đích năm 2027 (CT.30 Chơn Thành, ĐT.994 Ven biển 54m, ĐT.994B, Cầu Phước An, QL13 BD)
    elif end_year == 2028:
        return (255, 109, 0)     # Orange: Về đích năm 2028 (5 BOT NQ98: QL13, QL1, QL22, Nguyễn Hữu Thọ, Bình Tiên + Nguyễn Khoái, VĐ2, CT.31, CT.29)
    elif end_year <= 2030:
        return (255, 23, 68)     # Crimson: Về đích 2029-2030 (Cầu Cần Giờ, Cầu Thủ Thiêm 4, Cầu Cát Lái, Phú Mỹ 2, Vành đai 4, Metro 2, ĐS Cần Giờ, ĐS Long Thành)
    elif end_year <= 2035:
        return (224, 64, 251)    # Purple: Giai đoạn 2031-2035 (355km Metro NQ188: Metro 3, 4, 5, 6 + ĐS Tốc độ cao Bắc-Nam 350km/h)
    else:
        return (144, 164, 174)   # Silver-Blue: Tầm nhìn 2036-2050+ (Cầu vượt biển Cần Giờ-Vũng Tàu, Vành đai Metro 10...)

def main():
    with open(f"{SCRATCH_DIR}/full_gis_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    fonts = load_multi_fonts()
    W, H = 2200, 1750
    base, geo_to_px = build_basemap_bbox(11.220, 10.320, 106.340, 107.480, zoom=10, out_w=W, out_h=H, lyrs="y", darken=0.62)

    # Draw all roads colored by completion year cohort
    for r in data["roads"]:
        col = cohort_color(r["end_year"])
        pts = [geo_to_px(lat, lon) for lat, lon in r["coords"]]
        dsh = r["end_year"] > 2028
        base = draw_glowing_polyline(base, pts, col, width=6 if r["end_year"] <= 2030 else 4, dashed=dsh)

    # Draw metros colored by completion year cohort
    for m in data["metros"]:
        col = cohort_color(m["end_year"])
        pts = [geo_to_px(lat, lon) for lat, lon in m["coords"]]
        base = draw_glowing_polyline(base, pts, col, width=5, dashed=True)

    draw = ImageDraw.Draw(base)

    # Top Header
    draw.rectangle([0, 0, W, 86], fill=(8, 15, 28, 244))
    draw.line([(0, 86), (W, 86)], fill=(0, 229, 255, 220), width=3)
    draw.text((28, 14), "BẢN ĐỒ LỘ TRÌNH XÂY DỰNG & HOÀN THÀNH HẠ TẦNG THEO TỪNG NĂM (TIMELINE 2025 → 2026 → 2027 → 2028 → 2029–2030 → 2035 → 2050)", font=fonts["title"], fill=(255, 255, 255, 255))
    draw.text((28, 52), "Phân tầng màu sắc theo đúng năm dự kiến hoàn thành để đánh giá chính xác diện mạo thực tế của Đại Đô thị TP.HCM tại từng mốc thời gian", font=fonts["subtitle"], fill=(144, 224, 239, 255))

    # Bottom Timeline Cohort Legend Bar
    draw.rectangle([0, H - 56, W, H], fill=(8, 15, 28, 244))
    draw.line([(0, H - 56), (W, H - 56)], fill=(0, 229, 255, 190), width=2)
    legend_cohorts = [
        ((0, 230, 118), "2024–2025: Đã vận hành (Metro 1, Ga T3, Hầm NVL)"),
        ((0, 229, 255), "Năm 2026: Vành đai 3, CT.01, CT.28, QL50, Sân bay LT"),
        ((255, 214, 0), "Năm 2027: CT.30 Chơn Thành, ĐT.994 (54m), Cầu Phước An"),
        ((255, 109, 0), "Năm 2028: 5 BOT NQ98 (QL13, QL1, QL22, NHT, Bình Tiên), VĐ2, CT.31"),
        ((255, 23, 68), "2029–2030: 4 Cầu lớn, VĐ4, Metro 2, ĐS Cần Giờ & Long Thành"),
        ((224, 64, 251), "2031–2050: 355km Metro NQ188 & Cầu biển Cần Giờ–VT"),
    ]
    lx = 22
    ly = H - 36
    for col, lbl in legend_cohorts:
        draw.rounded_rectangle([lx, ly + 2, lx + 24, ly + 14], radius=3, fill=(*col, 255))
        draw.text((lx + 28, ly - 1), lbl, font=fonts["reg_sizes"][11], fill=(235, 242, 250, 255))
        lx += 28 + int(draw.textlength(lbl, font=fonts["reg_sizes"][11])) + 16

    CW = 595
    LX = 20
    RX = W - CW - 20
    CH = 88
    ys = get_card_y_positions(7, top_y=104, bottom_y=1585, card_h=CH)

    cards = [
        # Left Column: 2024-2025 -> 2026 -> 2027 -> 2028 (West/North/Central)
        ((LX, ys[0], CW, CH), geo_to_px(10.8080, 106.6520), (0, 230, 118),
         "MỐC 2024–2025 (ĐÃ HOÀN THÀNH & ĐƯA VÀO KHAI THÁC)",
         "Metro số 1 Bến Thành–Suối Tiên (19,7km) • Nhà ga T3 Tân Sơn Nhất & Đường nối Trần Quốc Hoàn (48m)",
         "Hầm chui Nguyễn Văn Linh–Nguyễn Hữu Thọ • Cầu Nam Lý • Đồng Văn Cống (60m) • Tân Kỳ Tân Quý (30m)",
         "Cáp điện ngầm xuyên biển 110kV Côn Đảo (9/2025) • Nhà máy XLNT Bình Hưng (469.000 m³/ngày)"),

        ((LX, ys[1], CW, CH), geo_to_px(10.8200, 106.5150), (0, 229, 255),
         "MỐC NĂM 2026 — KHÉP KÍN VÀNH ĐAI 3 & CỬA NGÕ TÂY NAM / CHỐNG NGẬP",
         "Thông xe Vành đai 3 TP.HCM (CT.40: 76,3 km, lộ giới 63–74,5m) & Mở rộng Quốc lộ 50 (34m, 6 làn)",
         "Hoàn thành Đường ven kênh Tham Lương – Bến Cát (31,5 km) & Vận hành 6 Siêu cống ngăn triều (10.000 tỷ)",
         "Vận hành Nhà máy XLNT Nhiêu Lộc – Thị Nghè (480.000 m³/ngày) • Tổng vốn về đích 2026: >260.000 tỷ"),

        ((LX, ys[2], CW, CH), geo_to_px(10.9836, 106.6661), (255, 214, 0),
         "MỐC NĂM 2027 — BÙNG NỔ TRỤC BẮC BÌNH DƯƠNG (CT.30 & QUỐC LỘ 13 8 LÀN)",
         "Thông xe Cao tốc TP.HCM – Thủ Dầu Một – Chơn Thành (CT.30: 60,3 km, lộ giới 60m)",
         "Hoàn thành mở rộng Quốc lộ 13 qua Bình Dương lên 8 làn xe (lộ giới 64m) & Đường Đỗ Xuân Hợp (30m)",
         "Hoàn thành Công viên KHCN mở rộng SHTP (Long Trường) & Đường Liên Phường thông toàn tuyến"),

        ((LX, ys[3], CW, CH), geo_to_px(10.9050, 106.5580), (255, 109, 0),
         "MỐC NĂM 2028 (KHU TÂY BẮC) — VỀ ĐÍCH QUỐC LỘ 22 (60M) & CAO TỐC MỘC BÀI",
         "Hoàn thành mở rộng Quốc lộ 22 (An Sương – Vành đai 3: 60m, 10 làn + 7 cầu vượt trực thông)",
         "Thông xe Cao tốc TP.HCM – Mộc Bài (CT.31: 51 km, lộ giới 60–80m) & Đường Nguyễn Văn Bứa (32–40m)",
         "Vận hành Khu liên hợp Đốt rác phát điện Tây Bắc Củ Chi & Dự án cải tạo Rạch Xuyên Tâm (17.229 tỷ)"),

        ((LX, ys[4], CW, CH), geo_to_px(10.7150, 106.5980), (255, 109, 0),
         "MỐC NĂM 2028 (KHU TÂY NAM & NỘI ĐÔ) — QUỐC LỘ 1 (60M), BÌNH TIÊN & NGUYỄN KHOÁI",
         "Hoàn thành mở rộng Quốc lộ 1 (An Lạc – Long An: 60m, 10–12 làn) & Mở rộng Cao tốc Trung Lương (8–10 làn)",
         "Thông xe Cầu đường Bình Tiên (30–40m), Cầu đường Nguyễn Khoái (4,96 km) & Nguyễn Tất Thành (30–40m)",
         "Hoàn thành cải tạo bờ Bắc Kênh Đôi (7.300 tỷ) & Mở rộng Hương Lộ 2 – Trần Văn Giàu (40m)"),

        ((LX, ys[5], CW, CH), geo_to_px(10.6950, 106.7050), (255, 109, 0),
         "MỐC NĂM 2028 (NAM SÀI GÒN & ĐÔNG BẮC) — CẦU CẠN QUỐC LỘ 13 & NGUYỄN HỮU THỌ",
         "Thông xe Quốc lộ 13 đoạn Bình Triệu – Vĩnh Bình (lộ giới 60m: Cầu cạn 4 làn 80km/h + 8–10 làn dưới đất)",
         "Thông xe Trục Bắc–Nam Nguyễn Hữu Thọ (lộ giới 60m: Cầu cạn 4 làn dài 7,2 km + 6 làn song hành)",
         "Giải quyết triệt để 100% điểm nghẽn cửa ngõ Đông Bắc (Bình Triệu) và cửa ngõ Nam Sài Gòn (Nhà Bè)"),

        ((LX, ys[6], CW, CH), geo_to_px(10.7120, 106.5820), (224, 64, 251),
         "MỐC NĂM 2031–2035 — HOÀN THÀNH 355 KM METRO NỘI ĐÔ (NGHỊ QUYẾT 188)",
         "Vận hành đồng bộ Metro số 1 kéo dài Bình Dương, Metro 2, Metro 3A, Metro 3B, Metro 4, Metro 5 & Metro 6",
         "Hoàn thành Đường sắt Quốc gia TP.HCM (Tân Kiên) – Cần Thơ (200 km/h) & Bàu Bàng – An Bình – Cái Mép",
         "Vận hành Đường sắt Tốc độ cao Bắc – Nam (350 km/h) từ Ga Đầu mối Thủ Thiêm đi Nha Trang – Hà Nội"),

        # Right Column: East / South-East / Coast Timeline (2026 -> 2027 -> 2028 -> 2029 -> 2030 -> 2045)
        ((RX, ys[0], CW, CH), geo_to_px(10.7850, 107.0350), (0, 229, 255),
         "MỐC NĂM 2026 (KHU ĐÔNG & ĐÔNG NAM) — SÂN BAY LONG THÀNH, CT.28 & CT.01",
         "Vận hành Sân bay Quốc tế Long Thành GĐ1 (25 triệu khách/năm) & Cao tốc Biên Hòa – Vũng Tàu (CT.28)",
         "Thông xe toàn tuyến Cao tốc Bến Lức – Long Thành (CT.01: 57,8 km) & Đường 991B Cái Mép (35–68m)",
         "Hoàn thành 3 Đại nút giao 3 tầng: An Phú (3.408 tỷ), Mỹ Thủy (3.622 tỷ) & Tân Vạn (1.831 tỷ)"),

        ((RX, ys[1], CW, CH), geo_to_px(10.4308, 107.2794), (255, 214, 0),
         "MỐC NĂM 2027 (HÀNH LANG BIỂN) — ĐẠI LỘ VEN BIỂN ĐT.994 (54M) & CẦU PHƯỚC AN",
         "Hoàn thành mở rộng 76,86 km Đường ven biển Vũng Tàu – Hồ Tràm – Bình Châu (ĐT.994: 40,5–54m, 6–8 làn)",
         "Thông xe Đường trục chính Bà Rịa – Vũng Tàu (ĐT.994B: Cao tốc đô thị 6–10 làn, lộ giới 68–100m)",
         "Hợp long & thông xe Cầu Phước An (rộng 27m, 6 làn, tĩnh không 55m) nối Cái Mép vào Cao tốc CT.01"),

        ((RX, ys[2], CW, CH), geo_to_px(10.7930, 106.8150), (255, 109, 0),
         "MỐC NĂM 2028 (KHU ĐÔNG) — KHÉP KÍN VÀNH ĐAI 2 & MỞ RỘNG CAO TỐC LONG THÀNH",
         "Khép kín Vành đai 2 Khu Đông Đoạn 1–2–3 (Phú Hữu – Phạm Văn Đồng – Gò Dưa: lộ giới 67m, 10–12 làn)",
         "Hoàn thành mở rộng Cao tốc TP.HCM – Long Thành (CT.29) lên 8–10 làn xe (lộ giới 60–116m)",
         "Hoàn thành mở rộng Nguyễn Thị Định (60–73m, 8–14 làn), Nguyễn Duy Trinh (30m) & Lã Xuân Oai (30m)"),

        ((RX, ys[3], CW, CH), geo_to_px(11.0089, 106.9530), (255, 23, 68),
         "MỐC NĂM 2029 (LIÊN VÙNG) — THÔNG XE ĐẠI LỘ VÀNH ĐAI 4 (CT.41 — 207 KM)",
         "Khép kín vành đai công nghiệp – cảng biển từ Cảng Cái Mép – Sân bay Long Thành – Bình Dương – Củ Chi – Hiệp Phước",
         "Giải phóng mặt bằng 74,5–120m (8 làn cao tốc; Giai đoạn 1 khai thác 4 làn cao tốc hoàn chỉnh + làn khẩn cấp)",
         "Tổng mức đầu tư 120.413 tỷ đồng • Tạo hành lang logistics tốc độ cao bao quanh toàn vùng TP.HCM"),

        ((RX, ys[4], CW, CH), geo_to_px(10.6650, 106.7620), (255, 23, 68),
         "MỐC NĂM 2029 (VƯỢT SÔNG & BIỂN) — 4 ĐẠI CẦU MỚI & ĐS TỐC ĐỘ CAO CẦN GIỜ",
         "Hoàn thành Cầu Cần Giờ (7,3km, 6 làn), Cầu Thủ Thiêm 4 (8 làn), Cầu Cát Lái (8 làn) & Cầu Phú Mỹ 2 (8 làn)",
         "Vận hành Tuyến Đường sắt Tốc độ cao Bến Thành – Cần Giờ (48,7 km, 250–350 km/h, đi 16 phút)",
         "Đưa vào hoạt động các phân khu chính của Siêu đô thị du lịch sinh thái lấn biển Cần Giờ (2.870 ha)"),

        ((RX, ys[5], CW, CH), geo_to_px(10.7820, 106.7480), (255, 23, 68),
         "MỐC NĂM 2030 — METRO SỐ 2, ĐS THỦ THIÊM – LONG THÀNH, SIÊU CẢNG CẦN GIỜ & FTZ",
         "Vận hành Tuyến Metro số 2 (Bến Thành – Tham Lương: 11,1 km) & Đường sắt Thủ Thiêm – Long Thành (41,8 km)",
         "Khai thác GĐ1 Siêu cảng Trung chuyển Quốc tế Cần Giờ (tàu 250.000 DWT) & Khu FTZ Cái Mép Hạ",
         "Hoàn thành Đại lộ Võ Văn Kiệt kéo dài nối Vành đai 3 (60m), Vành đai 2 Đoạn 4 & Cao tốc Long Thành – Hồ Tràm"),

        ((RX, ys[6], CW, CH), geo_to_px(10.3820, 107.0150), (144, 164, 174),
         "TẦM NHÌN 2036–2050 & 100 NĂM — CẦU/HẦM VƯỢT BIỂN CẦN GIỜ – VŨNG TÀU & 28 TUYẾN METRO",
         "Hoàn thành Cầu / Hầm vượt biển Cần Giờ – Vũng Tàu (14,5 km qua Vịnh Gành Rái: 6 làn bộ + 2 làn Metro)",
         "Hoàn thiện 5 Tuyến Đường trên cao nội đô (70,7 km), Đường ngầm ven sông Sài Gòn (9 km) & 28 tuyến Metro",
         "Quy mô dân số đạt 21,0 triệu người • Đô thị Toàn cầu Đa cực Net-Zero chống chịu biến đổi khí hậu 100 năm"),
    ]

    for box, tgt, acc, t, s, w, sch in cards:
        draw_callout_card_v2(draw, box, tgt, acc, t, s, w, sch, fonts)

    out_path = f"{ARTIFACT_DIR}/Overlay_5_Lo_Trinh_Xay_Dung_Timeline_2025_2050.png"
    base.convert("RGB").save(out_path, quality=95)
    print(f"Saved {out_path} successfully!")

if __name__ == "__main__":
    main()
