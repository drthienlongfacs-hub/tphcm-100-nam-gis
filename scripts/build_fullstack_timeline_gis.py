#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the Full-Stack Mobile-First + Year-by-Year Timeline Interactive Web GIS Application:
- Supports interactive Timeline Scrubber (2024 -> 2050) with Play/Pause animation,
  automatic show/hide by completion year (`end_year <= Y`), construction state (`start_year <= Y < end_year`),
  or exact year completion (`end_year == Y`) to prevent visual overload and forecast exact infrastructure status per year.
- Includes 12 Strategic Urban Growth Poles / IFC / FTZ / TOD Zones and 7 Energy / Water / Environment Mega-Hubs.
- Includes Mobile-First Bottom Navigation & Slide-up Sheets, GPS Locator, Distance/TOD Radius Ruler, and 9-Map HD Lightbox Gallery.
"""

import json
import shutil

ARTIFACT_DIR = "/Users/longlinh/.gemini/antigravity/brain/624ff7d6-9c4e-45bc-b91e-8475160775c8"
SCRATCH_DIR = f"{ARTIFACT_DIR}/scratch"

with open(f"{SCRATCH_DIR}/full_gis_data.json", "r", encoding="utf-8") as f:
    gis_data = json.load(f)

gis_json_str = json.dumps(gis_data, ensure_ascii=False)

html_content = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <meta name="theme-color" content="#061020" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <title>GIS Quy Hoạch Tổng Thể TP.HCM 100 Năm (2025–2050) — Lộ Trình Xây Dựng Từng Năm & Tra Cứu Mọi Tuyến Đường</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    :root {
      --bg-dark: #060d18;
      --panel-bg: rgba(9, 18, 33, 0.96);
      --card-bg: rgba(15, 28, 49, 0.94);
      --border: rgba(0, 229, 255, 0.28);
      --cyan: #00e5ff;
      --green: #00e676;
      --amber: #ffc107;
      --orange: #ff6d00;
      --red: #ff1744;
      --purple: #e040fb;
      --text: #eaf4ff;
      --muted: #9ab3cc;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg-dark);
      color: var(--text);
      height: 100dvh;
      width: 100vw;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    /* TOP HEADER */
    .top-header {
      background: linear-gradient(90deg, #050e1c 0%, #0d213f 55%, #061325 100%);
      border-bottom: 2px solid var(--cyan);
      padding: 7px 14px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      z-index: 1200;
      box-shadow: 0 4px 16px rgba(0,0,0,0.7);
      flex-shrink: 0;
    }
    .header-row1 {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      flex-wrap: wrap;
    }
    .brand-title {
      display: flex;
      align-items: center;
      gap: 9px;
    }
    .brand-badge {
      background: linear-gradient(135deg, #00e5ff, #00e676);
      color: #03101f;
      font-weight: 900;
      font-size: 11px;
      padding: 4px 8px;
      border-radius: 5px;
      letter-spacing: 0.4px;
      white-space: nowrap;
    }
    .brand-title h1 {
      font-size: 15px;
      font-weight: 800;
      color: #fff;
      line-height: 1.2;
    }
    .brand-sub {
      font-size: 11.5px;
      color: #90e0ef;
    }
    .header-actions {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }
    .btn-action {
      background: rgba(0, 229, 255, 0.14);
      border: 1px solid var(--cyan);
      color: #ffffff;
      padding: 5px 10px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.16s;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      white-space: nowrap;
    }
    .btn-action:hover, .btn-action.active {
      background: var(--cyan);
      color: #03101f;
      box-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
    }
    .btn-action.amber {
      border-color: var(--amber);
      background: rgba(255, 193, 7, 0.16);
      color: #ffe082;
    }
    .btn-action.amber:hover, .btn-action.amber.active {
      background: var(--amber);
      color: #03101f;
    }
    .btn-action.green {
      border-color: var(--green);
      background: rgba(0, 230, 118, 0.16);
      color: #b9f6ca;
    }
    .btn-action.green:hover, .btn-action.green.active {
      background: var(--green);
      color: #03101f;
    }

    /* QUICK ZOOM BAR */
    .quick-zoom-bar {
      display: flex;
      align-items: center;
      gap: 5px;
      overflow-x: auto;
      scrollbar-width: none;
      padding-bottom: 2px;
    }
    .quick-zoom-bar::-webkit-scrollbar { display: none; }
    .qz-label {
      font-size: 11px;
      font-weight: 800;
      color: var(--amber);
      white-space: nowrap;
    }
    .qz-btn {
      background: rgba(255, 255, 255, 0.07);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #d8ecff;
      padding: 3.5px 9px;
      border-radius: 13px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.14s;
    }
    .qz-btn:hover {
      background: rgba(0, 230, 118, 0.22);
      border-color: var(--green);
      color: #fff;
    }

    /* MAIN WORKSPACE */
    .workspace {
      flex: 1;
      display: flex;
      position: relative;
      overflow: hidden;
    }
    .sidebar {
      width: 420px;
      min-width: 350px;
      max-width: 440px;
      background: var(--panel-bg);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      z-index: 1000;
      overflow: hidden;
      transition: transform 0.28s ease;
    }
    .sidebar-scroll {
      flex: 1;
      overflow-y: auto;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .panel-box {
      background: var(--card-bg);
      border: 1px solid rgba(0, 229, 255, 0.22);
      border-radius: 9px;
      padding: 10px 11px;
    }
    .panel-title {
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      color: var(--cyan);
      margin-bottom: 7px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    /* SEARCH & CHIPS */
    .search-input-wrap {
      position: relative;
      margin-bottom: 7px;
    }
    .search-input {
      width: 100%;
      padding: 8px 30px 8px 10px;
      border-radius: 7px;
      border: 1px solid rgba(0, 229, 255, 0.45);
      background: rgba(5, 12, 24, 0.94);
      color: #ffffff;
      font-size: 12.5px;
      outline: none;
    }
    .search-input:focus {
      border-color: var(--green);
      box-shadow: 0 0 8px rgba(0, 230, 118, 0.3);
    }
    .search-clear {
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      color: var(--muted);
      cursor: pointer;
      font-size: 14px;
    }
    .filter-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin-bottom: 7px;
    }
    .chip {
      font-size: 10.5px;
      padding: 3px 7px;
      border-radius: 11px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      background: rgba(255, 255, 255, 0.05);
      color: #cfe4f7;
      cursor: pointer;
    }
    .chip.active {
      background: var(--cyan);
      color: #03101f;
      border-color: var(--cyan);
      font-weight: 700;
    }
    .search-results-list {
      max-height: 230px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 5px;
      padding-right: 2px;
    }
    .result-item {
      background: rgba(7, 15, 28, 0.88);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-left: 4px solid var(--cyan);
      border-radius: 6px;
      padding: 6px 8px;
      cursor: pointer;
      transition: all 0.14s;
    }
    .result-item:hover {
      background: rgba(0, 229, 255, 0.14);
      border-color: var(--cyan);
    }
    .result-item .r-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 5px;
      font-size: 12px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 2px;
    }
    .result-item .r-tag {
      font-size: 9.5px;
      padding: 1px 5px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.12);
      color: #90e0ef;
      white-space: nowrap;
    }
    .result-item .r-sub {
      font-size: 11px;
      color: #ffeb85;
      line-height: 1.3;
    }
    .result-item .r-sched {
      font-size: 10.5px;
      color: #76ffa3;
      margin-top: 2px;
      font-weight: 600;
    }

    /* OVERLAY & LAYER CONTROLS */
    .overlay-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 5px;
      margin-bottom: 7px;
    }
    .ov-btn {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.18);
      color: #d8ecff;
      padding: 5px 7px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      text-align: left;
    }
    .ov-btn.active {
      background: rgba(0, 229, 255, 0.22);
      border-color: var(--cyan);
      color: #fff;
    }
    .slider-row {
      display: flex;
      align-items: center;
      gap: 7px;
      font-size: 11.5px;
      color: var(--muted);
      margin-top: 4px;
    }
    .slider-row input[type=range] {
      flex: 1;
      accent-color: var(--cyan);
    }
    .layer-toggles {
      display: flex;
      flex-direction: column;
      gap: 5px;
    }
    .layer-chk {
      display: flex;
      align-items: center;
      gap: 7px;
      font-size: 11.5px;
      cursor: pointer;
      color: #dcebfa;
    }
    .layer-chk input {
      accent-color: var(--cyan);
      width: 14px;
      height: 14px;
    }
    .swatch {
      width: 15px;
      height: 5px;
      border-radius: 3px;
      display: inline-block;
      flex-shrink: 0;
    }

    /* MAP CONTAINER */
    #map {
      flex: 1;
      height: 100%;
      background: #040a12;
    }

    /* INTERACTIVE YEAR-BY-YEAR TIMELINE DOCK */
    .timeline-dock {
      position: absolute;
      bottom: 12px;
      left: 432px;
      right: 12px;
      background: rgba(7, 16, 30, 0.95);
      border: 2px solid var(--cyan);
      border-radius: 12px;
      padding: 10px 14px;
      z-index: 950;
      box-shadow: 0 8px 28px rgba(0, 0, 0, 0.85);
      display: flex;
      flex-direction: column;
      gap: 7px;
      backdrop-filter: blur(8px);
      transition: all 0.25s ease;
    }
    .timeline-dock.minimized .tl-body {
      display: none;
    }
    .tl-top-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
    }
    .tl-title-group {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .tl-year-badge {
      background: linear-gradient(135deg, #ffc107, #ff6d00);
      color: #04101e;
      font-weight: 900;
      font-size: 15px;
      padding: 3px 11px;
      border-radius: 7px;
      box-shadow: 0 0 12px rgba(255, 193, 7, 0.45);
    }
    .tl-mode-select {
      background: #0b1c33;
      color: #fff;
      border: 1px solid var(--cyan);
      border-radius: 6px;
      padding: 4px 8px;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
    }
    .tl-kpi-strip {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      font-size: 11.5px;
    }
    .tl-kpi {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.14);
      padding: 3px 8px;
      border-radius: 6px;
      white-space: nowrap;
    }
    .tl-slider-row {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .tl-play-btn {
      background: linear-gradient(135deg, #00e676, #00b0ff);
      color: #03101f;
      border: none;
      padding: 6px 13px;
      border-radius: 7px;
      font-size: 12px;
      font-weight: 800;
      cursor: pointer;
      white-space: nowrap;
      box-shadow: 0 2px 10px rgba(0, 230, 118, 0.4);
    }
    .tl-range {
      flex: 1;
      height: 7px;
      accent-color: var(--amber);
      cursor: pointer;
    }
    .tl-milestones {
      display: flex;
      justify-content: space-between;
      gap: 4px;
      overflow-x: auto;
      padding-bottom: 2px;
    }
    .tl-m-btn {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.18);
      color: #cfe4f7;
      padding: 3px 8px;
      border-radius: 5px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
      flex: 1;
      text-align: center;
    }
    .tl-m-btn.active {
      background: var(--amber);
      color: #03101f;
      border-color: var(--amber);
      box-shadow: 0 0 8px rgba(255, 193, 7, 0.5);
    }
    .tl-headline-box {
      background: rgba(4, 11, 22, 0.85);
      border-left: 3px solid var(--green);
      padding: 5px 9px;
      border-radius: 5px;
      font-size: 11.5px;
      color: #d8ecff;
      line-height: 1.38;
      max-height: 58px;
      overflow-y: auto;
    }
    .tl-completed-chips {
      display: flex;
      gap: 5px;
      overflow-x: auto;
      padding-bottom: 2px;
      scrollbar-width: thin;
    }
    .tl-proj-chip {
      background: rgba(0, 230, 118, 0.14);
      border: 1px solid rgba(0, 230, 118, 0.5);
      color: #b9f6ca;
      padding: 2px 7px;
      border-radius: 11px;
      font-size: 10.5px;
      font-weight: 600;
      white-space: nowrap;
      cursor: pointer;
    }
    .tl-proj-chip:hover {
      background: var(--green);
      color: #03101f;
    }

    /* FLOATING MAP LABELS */
    .road-badge-label {
      background: rgba(8, 16, 30, 0.92);
      border: 1.5px solid #00e5ff;
      color: #ffffff;
      padding: 2px 6px;
      border-radius: 5px;
      font-size: 10.5px;
      font-weight: 700;
      white-space: nowrap;
      box-shadow: 0 2px 7px rgba(0,0,0,0.75);
      cursor: pointer;
    }
    .road-badge-label .b-w { color: #ffe082; }
    .road-badge-label .b-s { color: #76ffa3; }
    .ward-label-pin {
      background: rgba(12, 25, 45, 0.86);
      border: 1px solid rgba(144, 224, 239, 0.65);
      color: #e0f7fa;
      padding: 1px 5px;
      border-radius: 9px;
      font-size: 10px;
      font-weight: 600;
      white-space: nowrap;
    }

    /* LEAFLET POPUP */
    .leaflet-popup-content-wrapper {
      background: rgba(9, 18, 33, 0.97) !important;
      color: #eaf4ff !important;
      border: 2px solid var(--cyan) !important;
      border-radius: 10px !important;
      box-shadow: 0 8px 28px rgba(0,0,0,0.85) !important;
    }
    .leaflet-popup-tip { background: rgba(9, 18, 33, 0.97) !important; }
    .eng-popup {
      min-width: 280px;
      max-width: 380px;
      font-size: 12px;
      line-height: 1.45;
    }
    .eng-popup .ep-cat {
      display: inline-block;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      padding: 2px 7px;
      border-radius: 4px;
      background: rgba(0, 229, 255, 0.18);
      color: var(--cyan);
      margin-bottom: 4px;
    }
    .eng-popup h3 {
      font-size: 14px;
      color: #fff;
      margin-bottom: 7px;
      border-bottom: 1px solid rgba(255,255,255,0.15);
      padding-bottom: 5px;
    }
    .eng-popup .ep-row {
      margin-bottom: 5px;
      background: rgba(255,255,255,0.04);
      padding: 5px 7px;
      border-radius: 5px;
      border-left: 3px solid var(--cyan);
    }
    .eng-popup .ep-row.cur { border-left-color: #ff9100; }
    .eng-popup .ep-row.plan { border-left-color: #00e676; }
    .eng-popup .ep-row.sched { border-left-color: #00e5ff; }
    .eng-popup .ep-lbl {
      font-weight: 800;
      color: #90e0ef;
      display: block;
      font-size: 10.5px;
      text-transform: uppercase;
      margin-bottom: 2px;
    }
    .eng-popup .ep-val-cur { color: #ffcc80; font-weight: 600; }
    .eng-popup .ep-val-plan { color: #b9f6ca; font-weight: 700; }
    .eng-popup .ep-val-sched { color: #84ffff; font-weight: 700; }

    /* MODALS (MASTER TABLE & 9-MAP HD GALLERY) */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(3, 8, 16, 0.88);
      z-index: 2500;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 12px;
      backdrop-filter: blur(5px);
    }
    .modal-backdrop.open { display: flex; }
    .modal-window {
      width: 98%;
      max-width: 1440px;
      height: 92dvh;
      background: #091526;
      border: 2px solid var(--cyan);
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .modal-header {
      padding: 11px 16px;
      background: #0d213f;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
    }
    .modal-header h2 { font-size: 15px; color: #fff; }
    .modal-toolbar {
      padding: 8px 16px;
      background: #0b1a30;
      border-bottom: 1px solid rgba(255,255,255,0.1);
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      justify-content: space-between;
    }
    .modal-tabs { display: flex; flex-wrap: wrap; gap: 5px; }
    .m-tab {
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.2);
      color: #d8ecff;
      padding: 5px 10px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
    }
    .m-tab.active {
      background: var(--cyan);
      color: #03101f;
      border-color: var(--cyan);
    }
    .modal-body {
      flex: 1;
      overflow-y: auto;
      padding: 12px 16px;
    }
    table.master-tbl {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }
    table.master-tbl th {
      position: sticky;
      top: 0;
      background: #102a4c;
      color: var(--cyan);
      text-align: left;
      padding: 8px;
      border-bottom: 2px solid var(--cyan);
      z-index: 5;
    }
    table.master-tbl td {
      padding: 8px;
      border-bottom: 1px solid rgba(255,255,255,0.1);
      vertical-align: top;
      line-height: 1.4;
    }
    table.master-tbl tr:hover { background: rgba(0, 229, 255, 0.1); }
    .fly-btn {
      background: rgba(0, 230, 118, 0.18);
      border: 1px solid var(--green);
      color: #b9f6ca;
      padding: 4px 8px;
      border-radius: 5px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
    }

    /* GALLERY GRID */
    .gallery-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 14px;
    }
    .gallery-card {
      background: #0d1e36;
      border: 1px solid var(--border);
      border-radius: 9px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    .gallery-card img {
      width: 100%;
      height: auto;
      cursor: zoom-in;
      display: block;
    }
    .gallery-card .g-info {
      padding: 9px 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      font-weight: 700;
    }

    /* MOBILE BOTTOM NAVIGATION BAR */
    .mobile-nav {
      display: none;
      background: #061020;
      border-top: 2px solid var(--cyan);
      height: 54px;
      z-index: 1500;
      justify-content: space-around;
      align-items: center;
      flex-shrink: 0;
    }
    .m-nav-btn {
      background: none;
      border: none;
      color: #9ab3cc;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
      font-size: 10.5px;
      font-weight: 700;
      cursor: pointer;
      padding: 4px 8px;
    }
    .m-nav-btn.active {
      color: var(--cyan);
    }
    .m-nav-btn .ico { font-size: 17px; }

    /* RESPONSIVE MOBILE RULES (<= 860px) */
    @media (max-width: 860px) {
      .brand-title h1 { font-size: 13px; }
      .brand-sub { display: none; }
      .header-actions { display: none; }
      .mobile-nav { display: flex; }
      .sidebar {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        width: 100%;
        max-width: 100%;
        height: 68dvh;
        border-right: none;
        border-top: 2px solid var(--cyan);
        border-radius: 14px 14px 0 0;
        transform: translateY(105%);
        z-index: 1300;
      }
      .sidebar.mobile-open {
        transform: translateY(0);
      }
      .timeline-dock {
        left: 8px;
        right: 8px;
        bottom: 8px;
        padding: 8px 10px;
      }
      .gallery-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>

  <!-- TOP HEADER -->
  <header class="top-header">
    <div class="header-row1">
      <div class="brand-title">
        <span class="brand-badge">GIS 100 NĂM • LIVE TIMELINE</span>
        <div>
          <h1>BẢN ĐỒ SỐ QUY HOẠCH TỔNG THỂ TP.HCM 2025–2050, TẦM NHÌN 100 NĂM (6.772,59 KM² • 168 PHƯỜNG/XÃ)</h1>
          <div class="brand-sub">Kéo Timeline theo từng năm (2024–2050) để bật/tắt đúng các dự án hoàn thành • Xem chi tiết lộ giới (m), số làn & tiến độ mọi con đường</div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-action amber" onclick="openMasterModal('roads')">📋 Bảng Tra Cứu Toàn Bộ (350+ Dự Án & 168 Phường/Xã)</button>
        <button class="btn-action green" onclick="openGalleryModal()">🖼️ Bộ 9 Bản Đồ Zoom HD</button>
        <button class="btn-action" id="btnForceBadges" onclick="toggleForceAllBadges()">🏷️ Hiện Tất Cả Nhãn Lộ Giới (m)</button>
        <button class="btn-action" id="btnRuler" onclick="toggleRulerMode()">📏 Đo Khoảng Cách & TOD</button>
        <button class="btn-action" onclick="locateUserGPS()">📍 Vị Trí Của Tôi</button>
      </div>
    </div>

    <div class="quick-zoom-bar">
      <span class="qz-label">⚡ ZOOM NHANH:</span>
      <button class="qz-btn" onclick="flyToRegion(10.775, 106.705, 10)">Toàn TP.HCM</button>
      <button class="qz-btn" onclick="flyToRegion(10.772, 106.705, 14)">1. Lõi Sài Gòn – Thủ Thiêm</button>
      <button class="qz-btn" onclick="flyToRegion(10.715, 106.708, 13)">2. Nam Sài Gòn – Nhà Bè</button>
      <button class="qz-btn" onclick="flyToRegion(10.805, 106.778, 13)">3. Khu Đông Thủ Đức – Cát Lái</button>
      <button class="qz-btn" onclick="flyToRegion(10.848, 106.718, 14)">4. Quốc Lộ 13 – Bình Triệu</button>
      <button class="qz-btn" onclick="flyToRegion(10.812, 106.648, 14)">5. Tân Sơn Nhất T3 – Cộng Hòa</button>
      <button class="qz-btn" onclick="flyToRegion(10.722, 106.598, 13)">6. Tây Nam – QL1 – Tân Kiên</button>
      <button class="qz-btn" onclick="flyToRegion(10.915, 106.565, 12)">7. Tây Bắc – QL22 – Củ Chi</button>
      <button class="qz-btn" onclick="flyToRegion(10.995, 106.695, 12)">8. Bình Dương – Thủ Dầu Một</button>
      <button class="qz-btn" onclick="flyToRegion(10.515, 106.915, 11)">9. Cần Giờ – Siêu Cảng & ĐS 350km/h</button>
      <button class="qz-btn" onclick="flyToRegion(10.565, 107.045, 12)">10. Phú Mỹ – Cái Mép FTZ</button>
      <button class="qz-btn" onclick="flyToRegion(10.425, 107.215, 11)">11. Vũng Tàu – Hồ Tràm (ĐT.994)</button>
      <button class="qz-btn" onclick="flyToRegion(8.685, 106.608, 12)">12. Côn Đảo</button>
    </div>
  </header>

  <!-- MAIN WORKSPACE -->
  <div class="workspace">
    <!-- SIDEBAR (SLIDE-UP SHEET ON MOBILE) -->
    <aside class="sidebar" id="mainSidebar">
      <div class="sidebar-scroll">

        <!-- MOBILE QUICK TOOLS -->
        <div class="panel-box" style="display:flex;gap:6px;flex-wrap:wrap;justify-content:space-between;">
          <button class="btn-action" style="flex:1;justify-content:center;" onclick="locateUserGPS()">📍 Định vị GPS</button>
          <button class="btn-action" style="flex:1;justify-content:center;" id="btnRulerMob" onclick="toggleRulerMode()">📏 Đo khoảng cách</button>
          <button class="btn-action" style="flex:1;justify-content:center;" onclick="toggleForceAllBadges()">🏷️ Nhãn lộ giới</button>
        </div>

        <!-- 1. INSTANT SEARCH -->
        <div class="panel-box">
          <div class="panel-title">
            <span>🔍 TÌM MỌI TUYẾN ĐƯỜNG, CẦU, METRO & 168 PHƯỜNG/XÃ</span>
            <span id="searchCountBadge" style="color:#76ffa3;font-size:11px;"></span>
          </div>
          <div class="search-input-wrap">
            <input type="text" id="searchInput" class="search-input" placeholder="Gõ tên đường (VD: QL13, Nguyễn Tất Thành, Vành đai 3, Lê Văn Lương, Phường...)" oninput="renderSearchResults()" />
            <button class="search-clear" onclick="clearSearch()">✕</button>
          </div>
          <div class="filter-chips">
            <span class="chip active" onclick="setFilterCat('all', this)">Tất cả</span>
            <span class="chip" onclick="setFilterCat('road', this)">Đường & Cầu (76)</span>
            <span class="chip" onclick="setFilterCat('metro', this)">Metro & ĐS (16)</span>
            <span class="chip" onclick="setFilterCat('zone', this)">Khu Đô thị/FTZ (12)</span>
            <span class="chip" onclick="setFilterCat('hub', this)">Cảng/Sân bay/Ga (43)</span>
            <span class="chip" onclick="setFilterCat('ward', this)">168 Phường/Xã</span>
          </div>
          <div id="searchResults" class="search-results-list"></div>
        </div>

        <!-- 2. CHỒNG LỚP BẢN VẼ GỐC 2-A0 -->
        <div class="panel-box">
          <div class="panel-title">
            <span>🗺️ CHỒNG LỚP BẢN VẼ QUY HOẠCH GỐC 2-A0 (ULTRA-HD)</span>
          </div>
          <div class="overlay-grid">
            <button class="ov-btn active" id="ov_qh08a" onclick="switchA0Overlay('qh08a')">QH08A: Giao thông Đường bộ</button>
            <button class="ov-btn" id="ov_qh08c" onclick="switchA0Overlay('qh08c')">QH08C: Metro, Đường sắt & Sân bay</button>
            <button class="ov-btn" id="ov_qh11" onclick="switchA0Overlay('qh11')">QH11: Quy hoạch Sử dụng đất</button>
            <button class="ov-btn" id="ov_qh08b" onclick="switchA0Overlay('qh08b')">QH08B: Cảng biển & Đường thủy</button>
            <button class="ov-btn" id="ov_qh06" onclick="switchA0Overlay('qh06')">QH06: Định hướng Không gian</button>
            <button class="ov-btn" id="ov_none" onclick="switchA0Overlay('none')">Ẩn Bản vẽ A0 (Xem Google Maps rõ nhất)</button>
          </div>
          <div class="slider-row">
            <span>Độ mờ A0:</span>
            <input type="range" id="opacitySlider" min="0" max="100" value="38" oninput="updateA0Opacity(this.value)" />
            <span id="opacityVal" style="color:#00e5ff;font-weight:700;min-width:34px;">38%</span>
          </div>
          <div class="slider-row" style="margin-top:6px;">
            <span>Nền Bản đồ:</span>
            <select id="basemapSelect" onchange="switchBasemap(this.value)" style="flex:1;background:#081426;color:#fff;border:1px solid var(--cyan);padding:4px 7px;border-radius:5px;font-size:11.5px;">
              <option value="google_hybrid" selected>Google Maps Vệ tinh + Tên đường (Hybrid)</option>
              <option value="google_streets">Google Maps Đường phố Chi tiết (Streets)</option>
              <option value="google_sat">Google Earth Vệ tinh Thuần (Satellite)</option>
              <option value="carto_dark">Bản đồ Nền Tối Kỹ thuật (Dark Matter)</option>
            </select>
          </div>
        </div>

        <!-- 3. BẬT/TẮT CÁC LỚP KỸ THUẬT -->
        <div class="panel-box">
          <div class="panel-title">
            <span>📐 LỚP HẠ TẦNG & ĐÔ THỊ TRÊN BẢN ĐỒ</span>
          </div>
          <div class="layer-toggles">
            <label class="layer-chk"><input type="checkbox" checked onchange="toggleGroup('expressway', this.checked)" /><span class="swatch" style="background:#ff1744"></span>Cao tốc & Vành đai 2, 3, 4 (Lộ giới 60–120m)</label>
            <label class="layer-chk"><input type="checkbox" checked onchange="toggleGroup('bot_national', this.checked)" /><span class="swatch" style="background:#ffc107"></span>5 Dự án BOT Cửa ngõ NQ98 & Quốc lộ (QL13, QL1, QL22, QL50)</label>
            <label class="layer-chk"><input type="checkbox" checked onchange="toggleGroup('bridge_tunnel', this.checked)" /><span class="swatch" style="background:#00e5ff"></span>Cầu lớn, Hầm vượt sông/biển & Đại nút giao 3 tầng</label>
            <label class="layer-chk"><input type="checkbox" checked onchange="toggleGroup('urban_arterial', this.checked)" /><span class="swatch" style="background:#00e676"></span>Trục chính Đô thị mở rộng & 5 Đường trên cao</label>
            <label class="layer-chk"><input type="checkbox" checked onchange="toggleGroup('provincial', this.checked)" /><span class="swatch" style="background:#ff9100"></span>Đường tỉnh Bình Dương, Bà Rịa – Vũng Tàu & Củ Chi</label>
            <label class="layer-chk"><input type="checkbox" checked onchange="toggleGroup('metros', this.checked)" /><span class="swatch" style="background:#e040fb"></span>28 Tuyến Metro, ĐS Tốc độ cao 350km/h & ĐS Quốc gia</label>
            <label class="layer-chk"><input type="checkbox" checked onchange="toggleGroup('zones', this.checked)" /><span class="swatch" style="background:#ff4081"></span>12 Trung tâm Tài chính IFC, Khu Thương mại Tự do FTZ & Đô thị TOD</label>
            <label class="layer-chk"><input type="checkbox" checked onchange="toggleGroup('hubs', this.checked)" /><span class="swatch" style="background:#76ff03"></span>Sân bay (6), Siêu cảng biển, Ga ĐSQG (9), Depot (15) & ICD</label>
            <label class="layer-chk"><input type="checkbox" checked onchange="toggleGroup('utilities', this.checked)" /><span class="swatch" style="background:#ffea00"></span>Năng lượng LNG/Điện gió, Nhà máy Nước, XLNT & Đốt rác WTE</label>
            <label class="layer-chk"><input type="checkbox" checked onchange="toggleGroup('floods', this.checked)" /><span class="swatch" style="background:#2979ff"></span>Cống ngăn triều, Kênh Tham Lương – Xuyên Tâm & Điểm ngập</label>
            <label class="layer-chk"><input type="checkbox" checked onchange="toggleGroup('wards', this.checked)" /><span class="swatch" style="background:#90e0ef"></span>Tâm 168 Phường / Xã / Đặc khu Côn Đảo</label>
          </div>
        </div>

      </div>
    </aside>

    <!-- MAP VIEWPORT -->
    <main id="map"></main>

    <!-- INTERACTIVE YEAR-BY-YEAR TIMELINE DOCK -->
    <section class="timeline-dock" id="timelineDock">
      <div class="tl-top-row">
        <div class="tl-title-group">
          <span class="tl-year-badge" id="tlYearBadge">TOÀN BỘ (2025–2050)</span>
          <select id="tlModeSelect" class="tl-mode-select" onchange="onTimelineModeChange(this.value)">
            <option value="all">🌐 Xem Toàn bộ Quy hoạch 100 Năm (Tắt lọc theo năm)</option>
            <option value="cumulative">🎯 Dự báo Hiện trạng đến Năm [Y] (Ẩn dự án chưa làm)</option>
            <option value="completed_only">✅ Chỉ hiện Công trình ĐÃ XONG tính đến Năm [Y]</option>
            <option value="exact_year">🎉 Chỉ hiện Công trình Khánh thành Mới trong Năm [Y]</option>
            <option value="under_construction">🚧 Chỉ hiện Công trình Đang Thi công trong Năm [Y]</option>
          </select>
        </div>
        <div class="tl-kpi-strip">
          <span class="tl-kpi" id="kpiPop">👥 Dân số: <b>11,6 → 21,0 triệu</b></span>
          <span class="tl-kpi" id="kpiDone" style="color:#76ffa3;">✅ Đã xong: <b>--</b></span>
          <span class="tl-kpi" id="kpiActive" style="color:#ffe082;">🚧 Đang làm: <b>--</b></span>
          <span class="tl-kpi" id="kpiCapex" style="color:#84ffff;">💰 Vốn lũy kế: <b>--</b></span>
          <button class="btn-action" style="padding:3px 8px;font-size:11px;" onclick="toggleMinimizeTimeline()">🔽 Thu gọn</button>
        </div>
      </div>

      <div class="tl-body" style="display:flex;flex-direction:column;gap:6px;">
        <div class="tl-slider-row">
          <button class="tl-play-btn" id="btnPlayTimeline" onclick="togglePlayTimeline()">▶ Chạy Mô Phỏng (2024→2050)</button>
          <span style="font-size:11px;font-weight:700;color:#90e0ef;">2024</span>
          <input type="range" id="tlSlider" class="tl-range" min="2024" max="2050" step="1" value="2028" oninput="onYearSliderInput(this.value)" />
          <span style="font-size:11px;font-weight:700;color:#90e0ef;">2050</span>
        </div>

        <div class="tl-milestones">
          <button class="tl-m-btn active" data-yr="all" onclick="selectQuickYear('all')">Tất cả 100 Năm</button>
          <button class="tl-m-btn" data-yr="2025" onclick="selectQuickYear(2025)">2025 (Hiện trạng)</button>
          <button class="tl-m-btn" data-yr="2026" onclick="selectQuickYear(2026)">2026 (VĐ3, CT01, LT)</button>
          <button class="tl-m-btn" data-yr="2027" onclick="selectQuickYear(2027)">2027 (CT30, ĐT994)</button>
          <button class="tl-m-btn" data-yr="2028" onclick="selectQuickYear(2028)">2028 (5 BOT NQ98)</button>
          <button class="tl-m-btn" data-yr="2029" onclick="selectQuickYear(2029)">2029 (4 Cầu lớn, VĐ4)</button>
          <button class="tl-m-btn" data-yr="2030" onclick="selectQuickYear(2030)">2030 (Metro 2, Cảng CG)</button>
          <button class="tl-m-btn" data-yr="2035" onclick="selectQuickYear(2035)">2035 (355km Metro)</button>
          <button class="tl-m-btn" data-yr="2045" onclick="selectQuickYear(2045)">2045 (Cầu Cần Giờ-VT)</button>
          <button class="tl-m-btn" data-yr="2050" onclick="selectQuickYear(2050)">2050 (Tầm nhìn 100 năm)</button>
        </div>

        <div class="tl-headline-box" id="tlHeadlineBox">
          💡 <b>Hướng dẫn Timeline:</b> Bấm vào bất kỳ mốc năm nào ở trên (ví dụ <b>2026</b>, <b>2028</b>, <b>2030</b>, <b>2035</b>) hoặc bấm <b>"▶ Chạy Mô Phỏng"</b> để bản đồ tự động lọc và hiển thị chính xác những tuyến đường, cây cầu, tuyến Metro đã hoàn thành hoặc đang thi công tại thời điểm đó — giúp chống quá tải bản đồ và dự báo chính xác hiện trạng hạ tầng từng năm!
        </div>

        <div class="tl-completed-chips" id="tlCompletedChips"></div>
      </div>
    </section>
  </div>

  <!-- MOBILE BOTTOM NAVIGATION BAR -->
  <nav class="mobile-nav">
    <button class="m-nav-btn active" id="mnav_map" onclick="mobileNavSwitch('map')"><span class="ico">🗺️</span><span>Bản đồ</span></button>
    <button class="m-nav-btn" id="mnav_timeline" onclick="mobileNavSwitch('timeline')"><span class="ico">⏱️</span><span>Timeline Năm</span></button>
    <button class="m-nav-btn" id="mnav_search" onclick="mobileNavSwitch('search')"><span class="ico">🔍</span><span>Tìm & Lớp</span></button>
    <button class="m-nav-btn" id="mnav_table" onclick="mobileNavSwitch('table')"><span class="ico">📋</span><span>Bảng Tra Cứu</span></button>
    <button class="m-nav-btn" id="mnav_gallery" onclick="mobileNavSwitch('gallery')"><span class="ico">🖼️</span><span>9 Ảnh HD</span></button>
  </nav>

  <!-- MASTER LOOKUP TABLE MODAL -->
  <div class="modal-backdrop" id="masterModal">
    <div class="modal-window">
      <div class="modal-header">
        <div>
          <h2>📋 BẢNG TRA CỨU TOÀN DIỆN: ĐOẠN TUYẾN • HIỆN TRẠNG (M) → MỞ RỘNG (M/LÀN) • KHI NÀO XONG</h2>
          <div style="font-size:11.5px;color:#90e0ef;margin-top:2px;">Click nút <b>"🔍 Xem"</b> ở bất kỳ dòng nào để bay thẳng tới công trình hoặc Phường/Xã đó trên bản đồ</div>
        </div>
        <button class="btn-action" onclick="closeMasterModal()">✕ Đóng</button>
      </div>
      <div class="modal-toolbar">
        <div class="modal-tabs">
          <button class="m-tab active" id="tab_roads" onclick="switchModalTab('roads')">1. Đường Bộ & Cầu Lớn (76)</button>
          <button class="m-tab" id="tab_qh08a" onclick="switchModalTab('qh08a')">2. Bảng 77 Đường Tỉnh QH08A</button>
          <button class="m-tab" id="tab_metros" onclick="switchModalTab('metros')">3. Metro & Đường Sắt (28 Tuyến)</button>
          <button class="m-tab" id="tab_zones" onclick="switchModalTab('zones')">4. Khu Đô Thị, IFC, FTZ & Năng Lượng (19)</button>
          <button class="m-tab" id="tab_hubs" onclick="switchModalTab('hubs')">5. Cảng, Sân Bay, Ga, Depot & ICD (43)</button>
          <button class="m-tab" id="tab_wards" onclick="switchModalTab('wards')">6. 168 Phường / Xã / Đặc Khu</button>
        </div>
        <input type="text" id="modalSearchInput" class="search-input" style="max-width:300px;margin:0;" placeholder="Tìm nhanh trong bảng..." oninput="renderModalTable()" />
      </div>
      <div class="modal-body" id="modalTableContainer"></div>
    </div>
  </div>

  <!-- 9-MAP HD GALLERY MODAL -->
  <div class="modal-backdrop" id="galleryModal">
    <div class="modal-window">
      <div class="modal-header">
        <div>
          <h2>🖼️ THƯ VIỆN 9 BẢN ĐỒ QUY HOẠCH TỔNG THỂ & BẢN ĐỒ ZOOM CHI TIẾT ĐỘ PHÂN GIẢI CAO (2200 × 1750 PX)</h2>
          <div style="font-size:11.5px;color:#90e0ef;margin-top:2px;">Bấm vào bất kỳ bản đồ nào để mở ảnh gốc Ultra-HD sắc nét trên tab mới (hỗ trợ phóng to chi tiết trên điện thoại)</div>
        </div>
        <button class="btn-action" onclick="closeGalleryModal()">✕ Đóng</button>
      </div>
      <div class="modal-body">
        <div class="gallery-grid">
          <div class="gallery-card">
            <a href="Overlay_5_Lo_Trinh_Xay_Dung_Timeline_2025_2050.png" target="_blank"><img src="Overlay_5_Lo_Trinh_Xay_Dung_Timeline_2025_2050.png" loading="lazy" alt="Timeline 2025-2050" /></a>
            <div class="g-info"><span>1. Bản đồ Lộ trình Xây dựng & Hoàn thành Từng Năm (Timeline 2025→2050)</span><a class="fly-btn" href="Overlay_5_Lo_Trinh_Xay_Dung_Timeline_2025_2050.png" target="_blank">🔍 Mở HD</a></div>
          </div>
          <div class="gallery-card">
            <a href="Zoom_1_Trung_Tam_Sai_Gon_Thu_Thiem_Nam_Sai_Gon_Chi_Tiet.png" target="_blank"><img src="Zoom_1_Trung_Tam_Sai_Gon_Thu_Thiem_Nam_Sai_Gon_Chi_Tiet.png" loading="lazy" alt="Zoom 1" /></a>
            <div class="g-info"><span>2. Zoom Chi Tiết 1: Lõi Sài Gòn – Thủ Thiêm – Chợ Lớn – Tân Sơn Nhất – Nam Sài Gòn</span><a class="fly-btn" href="Zoom_1_Trung_Tam_Sai_Gon_Thu_Thiem_Nam_Sai_Gon_Chi_Tiet.png" target="_blank">🔍 Mở HD</a></div>
          </div>
          <div class="gallery-card">
            <a href="Zoom_2_Khu_Dong_Thu_Duc_Di_An_Cat_Lai_Vanh_Dai_2_3.png" target="_blank"><img src="Zoom_2_Khu_Dong_Thu_Duc_Di_An_Cat_Lai_Vanh_Dai_2_3.png" loading="lazy" alt="Zoom 2" /></a>
            <div class="g-info"><span>3. Zoom Chi Tiết 2: Khu Đông TP. Thủ Đức – Dĩ An – Cát Lái – Vành Đai 2 & 3</span><a class="fly-btn" href="Zoom_2_Khu_Dong_Thu_Duc_Di_An_Cat_Lai_Vanh_Dai_2_3.png" target="_blank">🔍 Mở HD</a></div>
          </div>
          <div class="gallery-card">
            <a href="Zoom_3_Cua_Ngo_Tay_Bac_Binh_Duong_Quoc_Lo_1_13_22_50.png" target="_blank"><img src="Zoom_3_Cua_Ngo_Tay_Bac_Binh_Duong_Quoc_Lo_1_13_22_50.png" loading="lazy" alt="Zoom 3" /></a>
            <div class="g-info"><span>4. Zoom Chi Tiết 3: Cửa Ngõ Tây Bắc – Củ Chi – Hóc Môn – Bình Chánh – Bình Dương</span><a class="fly-btn" href="Zoom_3_Cua_Ngo_Tay_Bac_Binh_Duong_Quoc_Lo_1_13_22_50.png" target="_blank">🔍 Mở HD</a></div>
          </div>
          <div class="gallery-card">
            <a href="Zoom_4_Cang_Bien_Can_Gio_Cai_Mep_Phu_My_Vung_Tau_Ho_Tram.png" target="_blank"><img src="Zoom_4_Cang_Bien_Can_Gio_Cai_Mep_Phu_My_Vung_Tau_Ho_Tram.png" loading="lazy" alt="Zoom 4" /></a>
            <div class="g-info"><span>5. Zoom Chi Tiết 4: Hành Lang Biển Cần Giờ – Cái Mép – Phú Mỹ – Vũng Tàu – Hồ Tràm</span><a class="fly-btn" href="Zoom_4_Cang_Bien_Can_Gio_Cai_Mep_Phu_My_Vung_Tau_Ho_Tram.png" target="_blank">🔍 Mở HD</a></div>
          </div>
          <div class="gallery-card">
            <a href="Overlay_1_Khong_Gian_5_Cuc_10_Vung_Ve_Tinh.png" target="_blank"><img src="Overlay_1_Khong_Gian_5_Cuc_10_Vung_Ve_Tinh.png" loading="lazy" alt="Overlay 1" /></a>
            <div class="g-info"><span>6. Bản đồ Tổng thể 1: Cấu trúc Không gian 5 Cực Phát triển – 10 Phân vùng Quản trị</span><a class="fly-btn" href="Overlay_1_Khong_Gian_5_Cuc_10_Vung_Ve_Tinh.png" target="_blank">🔍 Mở HD</a></div>
          </div>
          <div class="gallery-card">
            <a href="Overlay_2_Su_Dung_Dat_2030_2050_Ban_Do_Thuc.png" target="_blank"><img src="Overlay_2_Su_Dung_Dat_2030_2050_Ban_Do_Thuc.png" loading="lazy" alt="Overlay 2" /></a>
            <div class="g-info"><span>7. Bản đồ Tổng thể 2: Quy hoạch Sử dụng đất 2030–2050 Chồng lớp Bản đồ Thực tế</span><a class="fly-btn" href="Overlay_2_Su_Dung_Dat_2030_2050_Ban_Do_Thuc.png" target="_blank">🔍 Mở HD</a></div>
          </div>
          <div class="gallery-card">
            <a href="Overlay_3_Mang_Luoi_Metro_Duong_Sat_Cao_Toc_TOD.png" target="_blank"><img src="Overlay_3_Mang_Luoi_Metro_Duong_Sat_Cao_Toc_TOD.png" loading="lazy" alt="Overlay 3" /></a>
            <div class="g-info"><span>8. Bản đồ Tổng thể 3: Mạng lưới 28 Tuyến Metro, Đường sắt Cao tốc, Sân bay & Cảng biển</span><a class="fly-btn" href="Overlay_3_Mang_Luoi_Metro_Duong_Sat_Cao_Toc_TOD.png" target="_blank">🔍 Mở HD</a></div>
          </div>
          <div class="gallery-card">
            <a href="Overlay_4_Mo_Phong_Cuoc_Song_Di_Chuyen_100_Nam.png" target="_blank"><img src="Overlay_4_Mo_Phong_Cuoc_Song_Di_Chuyen_100_Nam.png" loading="lazy" alt="Overlay 4" /></a>
            <div class="g-info"><span>9. Bản đồ Tổng thể 4: Mô phỏng Cuộc sống, Di chuyển 15–30 Phút & Thích ứng Khí hậu 100 Năm</span><a class="fly-btn" href="Overlay_4_Mo_Phong_Cuoc_Song_Di_Chuyen_100_Nam.png" target="_blank">🔍 Mở HD</a></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    const GIS_DATA = __GIS_DATA_JSON__;

    const map = L.map('map', {
      center: [10.7780, 106.7120],
      zoom: 11,
      minZoom: 7,
      maxZoom: 19,
      zoomControl: true,
      preferCanvas: true
    });

    const basemaps = {
      google_hybrid: L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}&hl=vi', { maxZoom: 20, attribution: 'Google Maps Hybrid' }),
      google_streets: L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}&hl=vi', { maxZoom: 20, attribution: 'Google Maps Streets' }),
      google_sat: L.tileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}&hl=vi', { maxZoom: 20, attribution: 'Google Satellite' }),
      carto_dark: L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { maxZoom: 20, attribution: 'CartoDB Dark' })
    };
    let currentBasemap = basemaps.google_hybrid.addTo(map);

    function switchBasemap(key) {
      if (currentBasemap) map.removeLayer(currentBasemap);
      currentBasemap = basemaps[key];
      currentBasemap.addTo(map);
      currentBasemap.bringToBack();
    }

    // GEOREFERENCED 2-A0 OVERLAYS
    const A0_BOUNDS = [[10.1095, 105.8645], [11.7545, 107.6800]];
    const a0Files = {
      qh08a: 'QH08A_Geo_Overlay.png',
      qh08c: 'QH08C_Geo_Overlay.png',
      qh11:  'QH11_Geo_Overlay.png',
      qh08b: 'QH08B_Geo_Overlay.png',
      qh06:  'QH06_Geo_Overlay.png'
    };
    let currentA0Overlay = L.imageOverlay(a0Files.qh08a, A0_BOUNDS, { opacity: 0.38, interactive: false }).addTo(map);

    function switchA0Overlay(key) {
      document.querySelectorAll('.ov-btn').forEach(b => b.classList.remove('active'));
      const btn = document.getElementById('ov_' + key);
      if (btn) btn.classList.add('active');
      if (currentA0Overlay) {
        map.removeLayer(currentA0Overlay);
        currentA0Overlay = null;
      }
      if (key !== 'none' && a0Files[key]) {
        const op = parseFloat(document.getElementById('opacitySlider').value) / 100.0;
        currentA0Overlay = L.imageOverlay(a0Files[key], A0_BOUNDS, { opacity: op, interactive: false }).addTo(map);
      }
    }

    function updateA0Opacity(val) {
      document.getElementById('opacityVal').textContent = val + '%';
      if (currentA0Overlay) currentA0Overlay.setOpacity(parseFloat(val) / 100.0);
    }

    // LAYER GROUPS & TIMELINE ENTITY REGISTRY
    const layerGroups = {
      expressway: L.layerGroup().addTo(map),
      bot_national: L.layerGroup().addTo(map),
      bridge_tunnel: L.layerGroup().addTo(map),
      urban_arterial: L.layerGroup().addTo(map),
      provincial: L.layerGroup().addTo(map),
      metros: L.layerGroup().addTo(map),
      zones: L.layerGroup().addTo(map),
      hubs: L.layerGroup().addTo(map),
      utilities: L.layerGroup().addTo(map),
      floods: L.layerGroup().addTo(map),
      wards: L.layerGroup().addTo(map),
      roadBadges: L.layerGroup().addTo(map),
      wardLabels: L.layerGroup(),
      rulerLayer: L.layerGroup().addTo(map)
    };

    const featureLookup = {};
    const timelineRegistry = []; // Every project with { id, name, start_year, end_year, capex_num, groupKey, layers: [], badgeMarker, baseStyle }
    let forceAllBadges = false;

    function getMidpoint(coords) {
      if (!coords || coords.length === 0) return [10.776, 106.701];
      return coords[Math.floor(coords.length / 2)];
    }

    // 1. BUILD ROADS & BRIDGES
    GIS_DATA.roads.forEach(r => {
      let grpKey = 'urban_arterial';
      if (r.group.includes('Cao tốc')) grpKey = 'expressway';
      else if (r.group.includes('Quốc lộ')) grpKey = 'bot_national';
      else if (r.group.includes('Cầu lớn')) grpKey = 'bridge_tunnel';
      else if (r.group.includes('Đường tỉnh')) grpKey = 'provincial';

      const popupHtml = `
        <div class="eng-popup">
          <span class="ep-cat">${r.group} • Khởi công ${r.start_year} → Xong ${r.end_year}</span>
          <h3>${r.name}</h3>
          <div class="ep-row">
            <span class="ep-lbl">📍 Đoạn tuyến & Khu vực (${r.length_km}):</span>
            <div>${r.segment}</div>
          </div>
          <div class="ep-row cur">
            <span class="ep-lbl">⚠️ Hiện trạng (Mặt cắt m / Số làn / Điểm nghẽn):</span>
            <div class="ep-val-cur">${r.current_width}</div>
          </div>
          <div class="ep-row plan">
            <span class="ep-lbl">🚀 Quy hoạch Mở rộng (Lộ giới m / Số làn / Cầu cạn):</span>
            <div class="ep-val-plan">${r.planned_width}</div>
          </div>
          <div class="ep-row sched">
            <span class="ep-lbl">📅 Lộ trình Xây dựng & Khi nào xong:</span>
            <div class="ep-val-sched">${r.schedule}</div>
            <div style="margin-top:4px;font-size:11px;color:#ffd54f;">💰 <b>Tổng vốn:</b> ${r.capex}</div>
          </div>
        </div>
      `;

      const halo = L.polyline(r.coords, { color: '#040b16', weight: (r.weight || 4.5) + 4, opacity: 0.85, interactive: false }).addTo(layerGroups[grpKey]);
      const poly = L.polyline(r.coords, {
        color: r.color || '#00e676',
        weight: r.weight || 4.5,
        opacity: 0.96,
        dashArray: r.dash || null
      }).bindPopup(popupHtml, { maxWidth: 400 }).addTo(layerGroups[grpKey]);

      poly.bindTooltip(`<b>${r.code}</b> (${r.start_year}→<b>${r.end_year}</b>): ${r.badge}`, { sticky: true });

      const mid = getMidpoint(r.coords);
      const badgeMarker = L.marker(mid, {
        icon: L.divIcon({
          className: '',
          html: `<div class="road-badge-label" style="border-color:${r.color}"><span>${r.code}</span> • <span class="b-w">${r.badge.split('•')[0].replace(r.code + ':', '')}</span> • <span class="b-s">Xong ${r.end_year}</span></div>`,
          iconSize: null
        })
      }).bindPopup(popupHtml, { maxWidth: 400 });
      layerGroups.roadBadges.addLayer(badgeMarker);

      featureLookup[r.id] = { layer: poly, center: mid, zoom: 13, data: r, category: 'road' };
      timelineRegistry.push({
        id: r.id,
        code: r.code,
        name: r.name,
        start_year: r.start_year,
        end_year: r.end_year,
        capex_num: r.capex_num || 0,
        grpKey: grpKey,
        halo: halo,
        mainLayer: poly,
        badgeMarker: badgeMarker,
        isPolyline: true,
        baseColor: r.color || '#00e676',
        baseWeight: r.weight || 4.5,
        baseDash: r.dash || null
      });
    });

    // 2. BUILD METROS
    GIS_DATA.metros.forEach(m => {
      const popupHtml = `
        <div class="eng-popup">
          <span class="ep-cat" style="background:rgba(224,64,251,0.2);color:#ea80fc;">METRO / ĐƯỜNG SẮT • ${m.start_year} → ${m.end_year}</span>
          <h3>${m.name}</h3>
          <div class="ep-row">
            <span class="ep-lbl">🛤️ Lộ trình & Chiều dài (${m.length_km}):</span>
            <div>${m.route}</div>
          </div>
          <div class="ep-row plan">
            <span class="ep-lbl">⚙️ Thông số Kỹ thuật:</span>
            <div class="ep-val-plan">${m.tech_spec}</div>
          </div>
          <div class="ep-row sched">
            <span class="ep-lbl">📅 Lộ trình Hoàn thành:</span>
            <div class="ep-val-sched">${m.schedule}</div>
            <div style="margin-top:4px;font-size:11px;color:#ffd54f;">💰 <b>Tổng vốn:</b> ${m.capex}</div>
          </div>
        </div>
      `;

      const halo = L.polyline(m.coords, { color: '#050c18', weight: 8, opacity: 0.8, interactive: false }).addTo(layerGroups.metros);
      const poly = L.polyline(m.coords, { color: m.color || '#e040fb', weight: 4.5, opacity: 0.95, dashArray: '8, 6' })
        .bindPopup(popupHtml, { maxWidth: 400 }).addTo(layerGroups.metros);

      poly.bindTooltip(`<b>🚇 ${m.code}</b> (Hoàn thành: <b>${m.end_year}</b>)`, { sticky: true });
      const mid = getMidpoint(m.coords);
      featureLookup[m.id] = { layer: poly, center: mid, zoom: 12, data: m, category: 'metro' };
      timelineRegistry.push({
        id: m.id,
        code: m.code,
        name: m.name,
        start_year: m.start_year,
        end_year: m.end_year,
        capex_num: m.capex_num || 0,
        grpKey: 'metros',
        halo: halo,
        mainLayer: poly,
        badgeMarker: null,
        isPolyline: true,
        baseColor: m.color || '#e040fb',
        baseWeight: 4.5,
        baseDash: '8, 6'
      });
    });

    // 3. BUILD STRATEGIC URBAN ZONES (IFC, FTZ, TOD, INNOVATION POLES)
    (GIS_DATA.zones || []).forEach(z => {
      const popupHtml = `
        <div class="eng-popup">
          <span class="ep-cat" style="background:rgba(255,64,129,0.22);color:#ff80ab;">🏙️ ${z.type} (${z.start_year}→${z.end_year})</span>
          <h3>${z.name}</h3>
          <div class="ep-row">
            <span class="ep-lbl">📐 Quy mô Diện tích:</span>
            <div><b>${z.area_ha}</b></div>
          </div>
          <div class="ep-row plan">
            <span class="ep-lbl">🚀 Chức năng Chiến lược & Hạ tầng Kết nối:</span>
            <div class="ep-val-plan">${z.spec}</div>
          </div>
          <div class="ep-row sched">
            <span class="ep-lbl">📅 Lộ trình Đầu tư & Vận hành:</span>
            <div class="ep-val-sched">${z.schedule}</div>
          </div>
        </div>
      `;

      const circle = L.circle([z.lat, z.lon], {
        radius: z.radius_m || 2200,
        color: '#ff4081',
        weight: 2,
        dashArray: '6, 4',
        fillColor: '#ff4081',
        fillOpacity: 0.14
      }).bindPopup(popupHtml, { maxWidth: 400 }).addTo(layerGroups.zones);

      circle.bindTooltip(`<b>🏙️ ${z.name}</b> (${z.area_ha})`);
      featureLookup[z.id] = { layer: circle, center: [z.lat, z.lon], zoom: 13, data: z, category: 'zone' };
      timelineRegistry.push({
        id: z.id,
        code: z.name.slice(0, 32),
        name: z.name,
        start_year: z.start_year,
        end_year: z.end_year,
        capex_num: z.capex_num || 0,
        grpKey: 'zones',
        halo: null,
        mainLayer: circle,
        badgeMarker: null,
        isPolyline: false
      });
    });

    // 4. BUILD HUBS (AIRPORTS, SEAPORTS, RAIL STATIONS, DEPOTS, ICDS)
    const hubColors = { airport: '#ff3d00', seaport: '#00b0ff', rail_station: '#ffd600', depot: '#e040fb', logistics: '#76ff03' };
    const hubLabels = {
      airport: '✈️ CẢNG HÀNG KHÔNG / SÂN BAY',
      seaport: '🚢 CẢNG BIỂN / CẢNG KHÁCH QUỐC TẾ',
      rail_station: '🚉 GA ĐẦU MỐI ĐƯỜNG SẮT QUỐC GIA',
      depot: '🚈 DEPOT ĐƯỜNG SẮT ĐÔ THỊ (METRO)',
      logistics: '📦 TRUNG TÂM LOGISTICS & CẢNG CẠN ICD'
    };

    GIS_DATA.hubs.forEach(h => {
      const col = hubColors[h.type] || '#00e5ff';
      const popupHtml = `
        <div class="eng-popup">
          <span class="ep-cat">${hubLabels[h.type] || 'HẠ TẦNG ĐẦU MỐI'} • Xong ${h.end_year}</span>
          <h3>${h.name}</h3>
          <div class="ep-row plan">
            <span class="ep-lbl">📐 Quy mô & Công suất:</span>
            <div class="ep-val-plan">${h.spec}</div>
          </div>
          <div class="ep-row sched">
            <span class="ep-lbl">📅 Lộ trình Hoàn thành:</span>
            <div class="ep-val-sched">${h.schedule}</div>
          </div>
        </div>
      `;

      const marker = L.circleMarker([h.lat, h.lon], {
        radius: h.type === 'airport' || h.type === 'seaport' ? 8 : 6.5,
        fillColor: col,
        color: '#ffffff',
        weight: 2,
        fillOpacity: 0.95
      }).bindPopup(popupHtml, { maxWidth: 380 }).addTo(layerGroups.hubs);

      marker.bindTooltip(`<b>${h.name}</b> (Xong: ${h.end_year})`);
      featureLookup[h.id] = { layer: marker, center: [h.lat, h.lon], zoom: 13, data: h, category: 'hub' };
      timelineRegistry.push({
        id: h.id,
        code: h.name.slice(0, 30),
        name: h.name,
        start_year: h.start_year,
        end_year: h.end_year,
        capex_num: h.capex_num || 0,
        grpKey: 'hubs',
        halo: null,
        mainLayer: marker,
        badgeMarker: null,
        isPolyline: false
      });
    });

    // 5. BUILD ENERGY, WATER & ENVIRONMENT UTILITIES
    (GIS_DATA.utilities || []).forEach(u => {
      const popupHtml = `
        <div class="eng-popup">
          <span class="ep-cat" style="background:rgba(255,234,0,0.2);color:#ffea00;">⚡ ${u.type} • Xong ${u.end_year}</span>
          <h3>${u.name}</h3>
          <div class="ep-row plan">
            <span class="ep-lbl">⚙️ Công suất & Kỹ thuật:</span>
            <div class="ep-val-plan">${u.spec}</div>
          </div>
          <div class="ep-row sched">
            <span class="ep-lbl">📅 Tiến độ Vận hành:</span>
            <div class="ep-val-sched">${u.schedule}</div>
          </div>
        </div>
      `;

      const marker = L.circleMarker([u.lat, u.lon], {
        radius: 7.5,
        fillColor: '#ffea00',
        color: '#051020',
        weight: 2,
        fillOpacity: 0.95
      }).bindPopup(popupHtml, { maxWidth: 380 }).addTo(layerGroups.utilities);

      marker.bindTooltip(`<b>⚡ ${u.name}</b> (Xong: ${u.end_year})`);
      featureLookup[u.id] = { layer: marker, center: [u.lat, u.lon], zoom: 13, data: u, category: 'utility' };
      timelineRegistry.push({
        id: u.id,
        code: u.name.slice(0, 30),
        name: u.name,
        start_year: u.start_year,
        end_year: u.end_year,
        capex_num: u.capex_num || 0,
        grpKey: 'utilities',
        halo: null,
        mainLayer: marker,
        badgeMarker: null,
        isPolyline: false
      });
    });

    // 6. BUILD FLOOD & CANAL MEGA-PROJECTS
    GIS_DATA.floods.forEach(fl => {
      const popupHtml = `
        <div class="eng-popup">
          <span class="ep-cat" style="background:rgba(41,121,255,0.25);color:#82b1ff;">🌊 CHỐNG NGẬP & KIỂM SOÁT TRIỀU • Xong ${fl.end_year}</span>
          <h3>${fl.name}</h3>
          <div class="ep-row cur">
            <span class="ep-lbl">⚠️ Hiện trạng & Quy mô:</span>
            <div class="ep-val-cur">${fl.depth_status}</div>
          </div>
          <div class="ep-row plan">
            <span class="ep-lbl">📐 Cao độ Xây dựng Khống chế (Bảng 96):</span>
            <div class="ep-val-plan">${fl.hxd}</div>
          </div>
          <div class="ep-row sched">
            <span class="ep-lbl">📅 Kế hoạch Hoàn thành:</span>
            <div class="ep-val-sched">${fl.schedule}</div>
          </div>
        </div>
      `;

      const marker = L.circleMarker([fl.lat, fl.lon], {
        radius: 7.5,
        fillColor: '#2979ff',
        color: '#82b1ff',
        weight: 2.5,
        fillOpacity: 0.9
      }).bindPopup(popupHtml, { maxWidth: 380 }).addTo(layerGroups.floods);

      marker.bindTooltip(`<b>🌊 ${fl.name}</b> (${fl.hxd})`);
      featureLookup[fl.id] = { layer: marker, center: [fl.lat, fl.lon], zoom: 14, data: fl, category: 'flood' };
      timelineRegistry.push({
        id: fl.id,
        code: fl.name.slice(0, 30),
        name: fl.name,
        start_year: fl.start_year,
        end_year: fl.end_year,
        capex_num: fl.capex_num || 0,
        grpKey: 'floods',
        halo: null,
        mainLayer: marker,
        badgeMarker: null,
        isPolyline: false
      });
    });

    // 7. BUILD ALL 168 WARDS / COMMUNES / SPECIAL ZONE
    GIS_DATA.wards.forEach((w, idx) => {
      const wid = 'WARD_' + idx;
      const popupHtml = `
        <div class="eng-popup">
          <span class="ep-cat">${w.type.toUpperCase()} • ĐƠN VỊ HÀNH CHÍNH (${idx + 1}/168)</span>
          <h3>${w.name}</h3>
          <div class="ep-row">
            <span class="ep-lbl">🏛️ Phân vùng Quản trị:</span>
            <div><b>${w.subregion}</b><br/><span style="color:#90e0ef">${w.pole}</span></div>
          </div>
          <div class="ep-row plan">
            <span class="ep-lbl">🏗️ Định hướng Sử dụng đất 2030–2050:</span>
            <div class="ep-val-plan">${w.land_use}</div>
          </div>
          <div class="ep-row cur">
            <span class="ep-lbl">📐 Cao độ Nền Tối thiểu (Hxd - Bảng 96):</span>
            <div class="ep-val-cur">${w.hxd}</div>
          </div>
          <div class="ep-row sched">
            <span class="ep-lbl">🛣️ Dự án Giao thông Trọng điểm Qua Địa bàn:</span>
            <div class="ep-val-sched">${w.local_projects}</div>
          </div>
        </div>
      `;

      const dot = L.circleMarker([w.lat, w.lon], {
        radius: 4.5,
        fillColor: w.type === 'Phường' ? '#00e5ff' : (w.type === 'Đặc khu' ? '#ffeb3b' : '#69f0ae'),
        color: '#061224',
        weight: 1.5,
        fillOpacity: 0.9
      }).bindPopup(popupHtml, { maxWidth: 400 }).addTo(layerGroups.wards);

      dot.bindTooltip(`<b>${w.name}</b> (${w.hxd})`);
      const lbl = L.marker([w.lat, w.lon], {
        icon: L.divIcon({ className: '', html: `<div class="ward-label-pin">${w.name}</div>`, iconSize: null }),
        interactive: false
      });
      layerGroups.wardLabels.addLayer(lbl);
      featureLookup[wid] = { layer: dot, center: [w.lat, w.lon], zoom: 14, data: w, category: 'ward', id: wid };
    });

    // =========================================================================
    // YEAR-BY-YEAR TIMELINE ENGINE (SHOW/HIDE & FORECASTING BY YEAR)
    // =========================================================================
    let timelineMode = 'all'; // 'all' | 'cumulative' | 'completed_only' | 'exact_year' | 'under_construction'
    let selectedYear = 2028;
    let playTimer = null;

    function interpolatePopulation(yr) {
      if (yr <= 2025) return (11.2 + (yr - 2024) * 0.4).toFixed(1) + ' triệu';
      if (yr <= 2030) return (11.6 + (yr - 2025) * 0.58).toFixed(1) + ' triệu';
      if (yr <= 2040) return (14.5 + (yr - 2030) * 0.35).toFixed(1) + ' triệu';
      return (18.0 + (yr - 2040) * 0.30).toFixed(1) + ' triệu';
    }

    function applyTimelineFilter() {
      let doneCount = 0;
      let activeCount = 0;
      let cumCapex = 0;
      const yearFinishingItems = [];

      timelineRegistry.forEach(item => {
        const isDone = item.end_year <= selectedYear;
        const isConstructing = item.start_year <= selectedYear && item.end_year > selectedYear;
        const isExact = item.end_year === selectedYear;

        if (isDone) {
          doneCount++;
          cumCapex += item.capex_num;
        }
        if (isConstructing) activeCount++;
        if (isExact) yearFinishingItems.push(item);

        let visible = true;
        if (timelineMode === 'cumulative') {
          visible = isDone || isConstructing;
        } else if (timelineMode === 'completed_only') {
          visible = isDone;
        } else if (timelineMode === 'exact_year') {
          visible = isExact;
        } else if (timelineMode === 'under_construction') {
          visible = isConstructing;
        }

        const grp = layerGroups[item.grpKey];
        if (!visible) {
          if (item.halo && grp.hasLayer(item.halo)) grp.removeLayer(item.halo);
          if (grp.hasLayer(item.mainLayer)) grp.removeLayer(item.mainLayer);
          if (item.badgeMarker && layerGroups.roadBadges.hasLayer(item.badgeMarker)) {
            layerGroups.roadBadges.removeLayer(item.badgeMarker);
          }
        } else {
          if (item.halo && !grp.hasLayer(item.halo)) grp.addLayer(item.halo);
          if (!grp.hasLayer(item.mainLayer)) grp.addLayer(item.mainLayer);
          if (item.badgeMarker && !layerGroups.roadBadges.hasLayer(item.badgeMarker)) {
            layerGroups.roadBadges.addLayer(item.badgeMarker);
          }

          // Dynamic styling in cumulative mode: solid bright if done, dashed amber if under construction
          if (item.isPolyline) {
            if (timelineMode === 'cumulative' && isConstructing) {
              item.mainLayer.setStyle({
                color: '#ffd600',
                weight: item.baseWeight,
                opacity: 0.9,
                dashArray: '10, 7'
              });
            } else {
              item.mainLayer.setStyle({
                color: item.baseColor,
                weight: item.baseWeight,
                opacity: 0.96,
                dashArray: timelineMode === 'all' ? item.baseDash : null
              });
            }
          }
        }
      });

      // Update UI Badges & KPIs
      if (timelineMode === 'all') {
        document.getElementById('tlYearBadge').textContent = 'TOÀN BỘ (2025–2050)';
        document.getElementById('kpiPop').innerHTML = `👥 Dân số: <b>11,6 → 21,0 triệu</b>`;
        document.getElementById('kpiDone').innerHTML = `✅ Tổng dự án: <b>${timelineRegistry.length}</b>`;
        document.getElementById('kpiActive').innerHTML = `🚧 Lộ trình: <b>2024–2050</b>`;
        const totalCapex = timelineRegistry.reduce((s, x) => s + x.capex_num, 0);
        document.getElementById('kpiCapex').innerHTML = `💰 Tổng vốn QH: <b>${totalCapex.toLocaleString('vi-VN')} tỷ</b>`;
      } else {
        document.getElementById('tlYearBadge').textContent = `NĂM ${selectedYear}`;
        document.getElementById('kpiPop').innerHTML = `👥 Dân số ${selectedYear}: <b>${interpolatePopulation(selectedYear)}</b>`;
        document.getElementById('kpiDone').innerHTML = `✅ Đã xong ≤${selectedYear}: <b>${doneCount}/${timelineRegistry.length}</b>`;
        document.getElementById('kpiActive').innerHTML = `🚧 Đang thi công ${selectedYear}: <b>${activeCount}</b>`;
        document.getElementById('kpiCapex').innerHTML = `💰 Vốn hoàn thành ≤${selectedYear}: <b>${cumCapex.toLocaleString('vi-VN')} tỷ</b>`;

        // Update headline text
        const ms = GIS_DATA.timeline_milestones || {};
        let hl = ms[String(selectedYear)] ? ms[String(selectedYear)].headline : null;
        if (!hl) {
          if (yearFinishingItems.length > 0) {
            hl = `Trong năm ${selectedYear}, có ${yearFinishingItems.length} công trình hạ tầng trọng điểm dự kiến hoàn thành đưa vào khai thác, cùng ${activeCount} dự án đang thi công đồng loạt trên toàn địa bàn.`;
          } else {
            hl = `Tính đến năm ${selectedYear}: Đã hoàn thành lũy kế ${doneCount} công trình hạ tầng (${cumCapex.toLocaleString('vi-VN')} tỷ đồng), đang triển khai thi công ${activeCount} dự án lớn.`;
          }
        }
        document.getElementById('tlHeadlineBox').innerHTML = `📅 <b>Dấu mốc Năm ${selectedYear}:</b> ${hl}`;

        // Render clickable chips of projects finishing in or around selectedYear
        const chipList = yearFinishingItems.length > 0
          ? yearFinishingItems
          : timelineRegistry.filter(x => x.end_year <= selectedYear).slice(-12);

        document.getElementById('tlCompletedChips').innerHTML = chipList.map(it =>
          `<span class="tl-proj-chip" onclick="flyToFeature('${it.id}')">🎯 ${it.code} (Xong ${it.end_year})</span>`
        ).join('');
      }
    }

    function selectQuickYear(yr) {
      document.querySelectorAll('.tl-m-btn').forEach(b => {
        b.classList.toggle('active', String(b.getAttribute('data-yr')) === String(yr));
      });
      if (yr === 'all') {
        timelineMode = 'all';
        document.getElementById('tlModeSelect').value = 'all';
        document.getElementById('tlCompletedChips').innerHTML = '';
      } else {
        selectedYear = parseInt(yr, 10);
        document.getElementById('tlSlider').value = selectedYear;
        if (timelineMode === 'all') {
          timelineMode = 'cumulative';
          document.getElementById('tlModeSelect').value = 'cumulative';
        }
      }
      applyTimelineFilter();
    }

    function onYearSliderInput(val) {
      selectedYear = parseInt(val, 10);
      if (timelineMode === 'all') {
        timelineMode = 'cumulative';
        document.getElementById('tlModeSelect').value = 'cumulative';
      }
      document.querySelectorAll('.tl-m-btn').forEach(b => {
        b.classList.toggle('active', String(b.getAttribute('data-yr')) === String(selectedYear));
      });
      applyTimelineFilter();
    }

    function onTimelineModeChange(mode) {
      timelineMode = mode;
      if (mode === 'all') {
        document.querySelectorAll('.tl-m-btn').forEach(b => b.classList.toggle('active', b.getAttribute('data-yr') === 'all'));
      }
      applyTimelineFilter();
    }

    function togglePlayTimeline() {
      const btn = document.getElementById('btnPlayTimeline');
      if (playTimer) {
        clearInterval(playTimer);
        playTimer = null;
        btn.textContent = '▶ Chạy Mô Phỏng (2024→2050)';
        return;
      }
      if (timelineMode === 'all') {
        timelineMode = 'cumulative';
        document.getElementById('tlModeSelect').value = 'cumulative';
        selectedYear = 2024;
      }
      if (selectedYear >= 2050) selectedYear = 2024;
      btn.textContent = '⏸ Dừng Mô Phỏng';
      onYearSliderInput(selectedYear);

      playTimer = setInterval(() => {
        if (selectedYear < 2030) selectedYear += 1;
        else if (selectedYear < 2035) selectedYear = 2035;
        else if (selectedYear < 2045) selectedYear = 2045;
        else if (selectedYear < 2050) selectedYear = 2050;
        else {
          clearInterval(playTimer);
          playTimer = null;
          btn.textContent = '▶ Chạy Mô Phỏng (2024→2050)';
          return;
        }
        document.getElementById('tlSlider').value = selectedYear;
        onYearSliderInput(selectedYear);
      }, 1600);
    }

    function toggleMinimizeTimeline() {
      document.getElementById('timelineDock').classList.toggle('minimized');
    }

    // ZOOM-ADAPTIVE LABELS
    function updateZoomAdaptiveLayers() {
      const z = map.getZoom();
      if (z >= 12 || forceAllBadges) {
        if (!map.hasLayer(layerGroups.roadBadges)) map.addLayer(layerGroups.roadBadges);
      } else {
        if (map.hasLayer(layerGroups.roadBadges)) map.removeLayer(layerGroups.roadBadges);
      }
      if (z >= 13) {
        if (!map.hasLayer(layerGroups.wardLabels)) map.addLayer(layerGroups.wardLabels);
      } else {
        if (map.hasLayer(layerGroups.wardLabels)) map.removeLayer(layerGroups.wardLabels);
      }
    }
    map.on('zoomend', updateZoomAdaptiveLayers);
    updateZoomAdaptiveLayers();
    applyTimelineFilter();

    function toggleForceAllBadges() {
      forceAllBadges = !forceAllBadges;
      const btn = document.getElementById('btnForceBadges');
      if (btn) btn.classList.toggle('active', forceAllBadges);
      updateZoomAdaptiveLayers();
    }

    function toggleGroup(key, checked) {
      if (checked) map.addLayer(layerGroups[key]);
      else map.removeLayer(layerGroups[key]);
    }

    function flyToRegion(lat, lon, zoom) {
      document.getElementById('mainSidebar').classList.remove('mobile-open');
      map.flyTo([lat, lon], zoom, { duration: 1.0 });
    }

    function flyToFeature(fid) {
      const item = featureLookup[fid];
      if (!item) return;
      closeMasterModal();
      document.getElementById('mainSidebar').classList.remove('mobile-open');
      if (!map.hasLayer(item.layer)) {
        selectQuickYear('all');
      }
      map.flyTo(item.center, item.zoom, { duration: 1.0 });
      setTimeout(() => {
        if (item.layer && item.layer.openPopup) item.layer.openPopup(item.center);
      }, 1050);
    }

    // GPS LOCATOR & DISTANCE / TOD RULER
    function locateUserGPS() {
      if (!navigator.geolocation) {
        alert('Trình duyệt của bạn không hỗ trợ định vị GPS.');
        return;
      }
      navigator.geolocation.getCurrentPosition(pos => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        layerGroups.rulerLayer.clearLayers();
        L.circle([lat, lon], { radius: 800, color: '#00e676', weight: 2, dashArray: '5,5', fillColor: '#00e676', fillOpacity: 0.12 })
          .bindTooltip('Bán kính đi bộ TOD 800m quanh vị trí của bạn').addTo(layerGroups.rulerLayer);
        L.circleMarker([lat, lon], { radius: 9, fillColor: '#00e676', color: '#fff', weight: 3, fillOpacity: 1 })
          .bindPopup(`<div class="eng-popup"><span class="ep-cat">📍 VỊ TRÍ GPS HIỆN TẠI</span><h3>Tọa độ: ${lat.toFixed(5)}°N, ${lon.toFixed(5)}°E</h3><div class="ep-row plan">Vòng tròn xanh biểu thị bán kính TOD 800m quanh vị trí của bạn. Hãy bấm vào các tuyến đường/phường xã xung quanh để xem lộ giới mở rộng!</div></div>`)
          .addTo(layerGroups.rulerLayer).openPopup();
        map.flyTo([lat, lon], 14, { duration: 1.0 });
      }, () => {
        alert('Không thể lấy vị trí GPS. Hãy cấp quyền truy cập vị trí cho trình duyệt.');
      });
    }

    let rulerActive = false;
    let rulerStartPt = null;
    function toggleRulerMode() {
      rulerActive = !rulerActive;
      rulerStartPt = null;
      layerGroups.rulerLayer.clearLayers();
      const b1 = document.getElementById('btnRuler');
      const b2 = document.getElementById('btnRulerMob');
      if (b1) b1.classList.toggle('active', rulerActive);
      if (b2) b2.classList.toggle('active', rulerActive);
      if (rulerActive) {
        document.getElementById('mainSidebar').classList.remove('mobile-open');
        alert('Chế độ Đo khoảng cách & Bán kính TOD: Hãy chạm/click vào điểm thứ 1 và điểm thứ 2 trên bản đồ!');
      }
    }

    map.on('click', (e) => {
      if (!rulerActive) return;
      if (!rulerStartPt) {
        rulerStartPt = e.latlng;
        L.circleMarker(rulerStartPt, { radius: 7, fillColor: '#ffc107', color: '#fff', weight: 2, fillOpacity: 1 }).addTo(layerGroups.rulerLayer);
        L.circle(rulerStartPt, { radius: 500, color: '#00e5ff', weight: 1.5, dashArray: '4,4', fillOpacity: 0.08 })
          .bindTooltip('Bán kính TOD 500m').addTo(layerGroups.rulerLayer);
      } else {
        const endPt = e.latlng;
        const distM = map.distance(rulerStartPt, endPt);
        const distStr = distM >= 1000 ? (distM / 1000).toFixed(2) + ' km' : Math.round(distM) + ' m';
        L.circleMarker(endPt, { radius: 7, fillColor: '#00e676', color: '#fff', weight: 2, fillOpacity: 1 }).addTo(layerGroups.rulerLayer);
        L.polyline([rulerStartPt, endPt], { color: '#ffc107', weight: 4, dashArray: '6, 4' })
          .bindPopup(`<div class="eng-popup"><span class="ep-cat">📏 KHOẢNG CÁCH ĐO ĐẠC</span><h3>Khoảng cách: ${distStr}</h3><div class="ep-row">Từ (${rulerStartPt.lat.toFixed(4)}, ${rulerStartPt.lng.toFixed(4)}) đến (${endPt.lat.toFixed(4)}, ${endPt.lng.toFixed(4)})</div></div>`)
          .addTo(layerGroups.rulerLayer).openPopup();
        rulerStartPt = null;
      }
    });

    // SIDEBAR INSTANT SEARCH
    let currentFilterCat = 'all';
    function setFilterCat(cat, el) {
      currentFilterCat = cat;
      document.querySelectorAll('.filter-chips .chip').forEach(c => c.classList.remove('active'));
      if (el) el.classList.add('active');
      renderSearchResults();
    }
    function clearSearch() {
      document.getElementById('searchInput').value = '';
      renderSearchResults();
    }
    function renderSearchResults() {
      const q = (document.getElementById('searchInput').value || '').trim().toLowerCase();
      const container = document.getElementById('searchResults');
      const items = [];

      if (currentFilterCat === 'all' || currentFilterCat === 'road') {
        GIS_DATA.roads.forEach(r => {
          const hay = `${r.code} ${r.name} ${r.segment} ${r.current_width} ${r.planned_width} ${r.schedule} ${r.end_year}`.toLowerCase();
          if (!q || hay.includes(q)) {
            items.push({ id: r.id, title: r.code, tag: `Xong ${r.end_year}`, sub: r.planned_width.slice(0, 90) + '...', sched: `⏱️ ${r.schedule}`, color: r.color });
          }
        });
      }
      if (currentFilterCat === 'all' || currentFilterCat === 'metro') {
        GIS_DATA.metros.forEach(m => {
          const hay = `${m.code} ${m.name} ${m.route} ${m.schedule} ${m.end_year}`.toLowerCase();
          if (!q || hay.includes(q)) {
            items.push({ id: m.id, title: m.code, tag: `Xong ${m.end_year}`, sub: `${m.length_km} • ${m.tech_spec.slice(0, 80)}...`, sched: `⏱️ ${m.schedule}`, color: m.color });
          }
        });
      }
      if (currentFilterCat === 'all' || currentFilterCat === 'zone') {
        (GIS_DATA.zones || []).forEach(z => {
          const hay = `${z.name} ${z.type} ${z.spec} ${z.schedule}`.toLowerCase();
          if (!q || hay.includes(q)) {
            items.push({ id: z.id, title: z.name, tag: z.area_ha, sub: z.spec.slice(0, 90) + '...', sched: `⏱️ ${z.schedule}`, color: '#ff4081' });
          }
        });
      }
      if (currentFilterCat === 'all' || currentFilterCat === 'hub') {
        GIS_DATA.hubs.forEach(h => {
          const hay = `${h.name} ${h.spec} ${h.schedule}`.toLowerCase();
          if (!q || hay.includes(q)) {
            items.push({ id: h.id, title: h.name, tag: `Xong ${h.end_year}`, sub: h.spec, sched: `⏱️ ${h.schedule}`, color: '#76ff03' });
          }
        });
      }
      if (currentFilterCat === 'all' || currentFilterCat === 'ward') {
        GIS_DATA.wards.forEach((w, idx) => {
          const wid = 'WARD_' + idx;
          const hay = `${w.name} ${w.subregion} ${w.local_projects}`.toLowerCase();
          if (!q || hay.includes(q)) {
            items.push({ id: wid, title: w.name, tag: w.hxd, sub: w.subregion, sched: `🛣️ ${w.local_projects.slice(0, 85)}...`, color: '#00e5ff' });
          }
        });
      }

      document.getElementById('searchCountBadge').textContent = `${items.length} mục`;
      container.innerHTML = items.slice(0, 85).map(it => `
        <div class="result-item" style="border-left-color:${it.color}" onclick="flyToFeature('${it.id}')">
          <div class="r-head"><span>${it.title}</span><span class="r-tag">${it.tag}</span></div>
          <div class="r-sub">${it.sub}</div>
          <div class="r-sched">${it.sched}</div>
        </div>
      `).join('');
    }
    renderSearchResults();

    // MODALS & MOBILE NAVIGATION
    let currentModalTab = 'roads';
    function openMasterModal(tab) {
      if (tab) currentModalTab = tab;
      document.getElementById('masterModal').classList.add('open');
      switchModalTab(currentModalTab);
    }
    function closeMasterModal() { document.getElementById('masterModal').classList.remove('open'); }
    function openGalleryModal() { document.getElementById('galleryModal').classList.add('open'); }
    function closeGalleryModal() { document.getElementById('galleryModal').classList.remove('open'); }

    function mobileNavSwitch(target) {
      document.querySelectorAll('.m-nav-btn').forEach(b => b.classList.remove('active'));
      const btn = document.getElementById('mnav_' + target);
      if (btn) btn.classList.add('active');
      const sb = document.getElementById('mainSidebar');
      const td = document.getElementById('timelineDock');

      if (target === 'map') {
        sb.classList.remove('mobile-open');
        td.classList.add('minimized');
      } else if (target === 'timeline') {
        sb.classList.remove('mobile-open');
        td.classList.remove('minimized');
      } else if (target === 'search') {
        sb.classList.toggle('mobile-open');
      } else if (target === 'table') {
        sb.classList.remove('mobile-open');
        openMasterModal('roads');
      } else if (target === 'gallery') {
        sb.classList.remove('mobile-open');
        openGalleryModal();
      }
    }

    function switchModalTab(tab) {
      currentModalTab = tab;
      document.querySelectorAll('.m-tab').forEach(b => b.classList.remove('active'));
      const activeBtn = document.getElementById('tab_' + tab);
      if (activeBtn) activeBtn.classList.add('active');
      renderModalTable();
    }

    function renderModalTable() {
      const q = (document.getElementById('modalSearchInput').value || '').trim().toLowerCase();
      const box = document.getElementById('modalTableContainer');

      if (currentModalTab === 'roads') {
        const rows = GIS_DATA.roads.filter(r => !q || `${r.code} ${r.name} ${r.segment} ${r.current_width} ${r.planned_width} ${r.schedule} ${r.end_year}`.toLowerCase().includes(q));
        box.innerHTML = `<table class="master-tbl"><thead><tr><th>Tuyến đường / Cầu</th><th>Đoạn tuyến & Chiều dài</th><th>Hiện trạng (m/làn)</th><th>Quy hoạch Mở rộng (m/làn)</th><th>Năm xong & Tổng vốn</th><th>Bản đồ</th></tr></thead><tbody>
          ${rows.map(r => `<tr><td><b style="color:#00e5ff">${r.code}</b><br/><span style="font-size:11px;color:#9ab3cc">${r.group}</span></td><td><b>${r.length_km}</b><br/>${r.segment}</td><td style="color:#ffcc80">${r.current_width}</td><td style="color:#b9f6ca;font-weight:600">${r.planned_width}</td><td><span style="background:rgba(0,230,118,0.2);color:#76ffa3;padding:2px 6px;border-radius:4px;font-weight:800;">Xong ${r.end_year}</span><br/><span style="color:#84ffff">${r.schedule}</span><br/><span style="color:#ffd54f;font-size:11px">Vốn: ${r.capex}</span></td><td><button class="fly-btn" onclick="flyToFeature('${r.id}')">🔍 Xem</button></td></tr>`).join('')}
        </tbody></table>`;
      } else if (currentModalTab === 'qh08a') {
        const rows = GIS_DATA.qh08a_table.filter(r => !q || `${r.area} ${r.code} ${r.scale}`.toLowerCase().includes(q));
        box.innerHTML = `<table class="master-tbl"><thead><tr><th>TT</th><th>Khu vực</th><th>Mã hiệu & Tên Đường Tỉnh</th><th>Cấp Kỹ thuật & Quy mô Làn xe / Lộ giới Quy hoạch (QH08A)</th></tr></thead><tbody>
          ${rows.map(r => `<tr><td><b>#${r.tt}</b></td><td><b style="color:#90e0ef">${r.area}</b></td><td><b style="color:#ffc107">${r.code}</b></td><td style="color:#b9f6ca;font-weight:600">${r.scale}</td></tr>`).join('')}
        </tbody></table>`;
      } else if (currentModalTab === 'metros') {
        const rows = GIS_DATA.metros.filter(m => !q || `${m.code} ${m.name} ${m.route} ${m.schedule}`.toLowerCase().includes(q));
        box.innerHTML = `<table class="master-tbl"><thead><tr><th>Tuyến Metro / ĐS</th><th>Lộ trình & Chiều dài</th><th>Thông số Kỹ thuật</th><th>Năm hoàn thành & Vốn</th><th>Bản đồ</th></tr></thead><tbody>
          ${rows.map(m => `<tr><td><b style="color:#ea80fc">${m.code}</b><br/>${m.name}</td><td><b>${m.length_km}</b><br/>${m.route}</td><td style="color:#b9f6ca">${m.tech_spec}</td><td><span style="background:rgba(224,64,251,0.2);color:#ea80fc;padding:2px 6px;border-radius:4px;font-weight:800;">Xong ${m.end_year}</span><br/>${m.schedule}<br/><span style="color:#ffd54f">Vốn: ${m.capex}</span></td><td><button class="fly-btn" onclick="flyToFeature('${m.id}')">🔍 Xem</button></td></tr>`).join('')}
        </tbody></table>`;
      } else if (currentModalTab === 'zones') {
        const allZU = [...(GIS_DATA.zones || []), ...(GIS_DATA.utilities || [])].filter(z => !q || `${z.name} ${z.type} ${z.spec} ${z.schedule}`.toLowerCase().includes(q));
        box.innerHTML = `<table class="master-tbl"><thead><tr><th>Phân loại</th><th>Tên Khu Đô thị / FTZ / Tổ hợp Năng lượng - Môi trường</th><th>Quy mô & Chức năng Chiến lược</th><th>Lộ trình Hoàn thành</th><th>Bản đồ</th></tr></thead><tbody>
          ${allZU.map(z => `<tr><td><b style="color:#ff80ab">${z.type}</b></td><td><b>${z.name}</b></td><td style="color:#b9f6ca">${z.area_ha ? '<b>' + z.area_ha + ':</b> ' : ''}${z.spec}</td><td style="color:#84ffff"><b>Xong ${z.end_year}</b><br/>${z.schedule}</td><td><button class="fly-btn" onclick="flyToFeature('${z.id}')">🔍 Xem</button></td></tr>`).join('')}
        </tbody></table>`;
      } else if (currentModalTab === 'hubs') {
        const rows = GIS_DATA.hubs.filter(h => !q || `${h.name} ${h.spec} ${h.schedule}`.toLowerCase().includes(q));
        box.innerHTML = `<table class="master-tbl"><thead><tr><th>Phân loại</th><th>Tên Đầu mối Hạ tầng</th><th>Quy mô & Công suất</th><th>Tiến độ Hoàn thành</th><th>Bản đồ</th></tr></thead><tbody>
          ${rows.map(h => `<tr><td><b style="color:#00e5ff">${hubLabels[h.type] || h.type}</b></td><td><b>${h.name}</b></td><td style="color:#b9f6ca">${h.spec}</td><td style="color:#84ffff"><b>Xong ${h.end_year}</b><br/>${h.schedule}</td><td><button class="fly-btn" onclick="flyToFeature('${h.id}')">🔍 Xem</button></td></tr>`).join('')}
        </tbody></table>`;
      } else if (currentModalTab === 'wards') {
        const rows = GIS_DATA.wards.map((w, idx) => ({ ...w, wid: 'WARD_' + idx, num: idx + 1 })).filter(w => !q || `${w.name} ${w.subregion} ${w.local_projects}`.toLowerCase().includes(q));
        box.innerHTML = `<table class="master-tbl"><thead><tr><th>#</th><th>Phường / Xã / Đặc khu</th><th>Phân vùng Quản trị</th><th>Cao độ Hxd</th><th>Định hướng Đất đai & Các Dự án Giao thông Trọng điểm</th><th>Bản đồ</th></tr></thead><tbody>
          ${rows.map(w => `<tr><td><b>${w.num}</b></td><td><b style="color:#00e5ff">${w.name}</b></td><td>${w.subregion}</td><td style="color:#ffcc80;font-weight:700">${w.hxd}</td><td><div style="color:#b9f6ca">${w.land_use}</div><div style="color:#84ffff;font-size:11px;margin-top:3px;">🛣️ ${w.local_projects}</div></td><td><button class="fly-btn" onclick="flyToFeature('${w.wid}')">🔍 Xem</button></td></tr>`).join('')}
        </tbody></table>`;
      }
    }
  </script>
</body>
</html>
"""

final_html = html_content.replace("__GIS_DATA_JSON__", gis_json_str)

out_artifact = f"{ARTIFACT_DIR}/quy_hoach_100_nam_tphcm_gis_overlay.html"
out_downloads = "/Users/longlinh/Downloads/Quy_Hoach_100_Nam_TPHCM_GIS_Overlay.html"

with open(out_artifact, "w", encoding="utf-8") as f:
    f.write(final_html)

shutil.copyfile(out_artifact, out_downloads)
print("Successfully generated Full-Stack Mobile-First + Timeline Web GIS HTML!")
