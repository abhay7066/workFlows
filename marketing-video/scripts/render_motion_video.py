#!/usr/bin/env python3
"""Programmatic Motion Graphic Reel Generator for NexConnect.

Renders high-definition vertical (1080x1920) 30fps video frames directly into ffmpeg,
synchronized with neural voiceover audio and ambient background music.
"""

import math
import os
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1080
HEIGHT = 1920
FPS = 30

FONT_DIR = "/usr/share/fonts/truetype/liberation"
FONT_BOLD_PATH = f"{FONT_DIR}/LiberationSans-Bold.ttf"
FONT_REG_PATH = f"{FONT_DIR}/LiberationSans-Regular.ttf"
FONT_MONO_PATH = f"{FONT_DIR}/LiberationMono-Bold.ttf"

FFMPEG_BIN = "/home/abhay-chauhan/work/workflows/.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"

# Color Palette
BG_DARK = (10, 15, 29)
CARD_BG = (17, 24, 39, 230)
CARD_BORDER = (55, 65, 81)
EMERALD = (16, 185, 129)
EMERALD_BG = (6, 78, 59)
CYAN = (6, 182, 212)
RED = (239, 68, 68)
RED_BG = (127, 29, 29)
WHITE = (255, 255, 255)
LIGHT_GRAY = (209, 213, 219)
MUTED = (148, 163, 184)
AMBER = (245, 158, 11)


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


# Preload fonts at needed sizes
font_title = get_font(FONT_BOLD_PATH, 58)
font_subtitle = get_font(FONT_BOLD_PATH, 42)
font_badge = get_font(FONT_BOLD_PATH, 28)
font_card_head = get_font(FONT_BOLD_PATH, 34)
font_body = get_font(FONT_REG_PATH, 30)
font_body_bold = get_font(FONT_BOLD_PATH, 30)
font_small = get_font(FONT_REG_PATH, 24)
font_mono = get_font(FONT_MONO_PATH, 28)
font_caption = get_font(FONT_BOLD_PATH, 32)
font_hero = get_font(FONT_BOLD_PATH, 74)
font_stat_num = get_font(FONT_BOLD_PATH, 68)


def draw_rounded_card(img, bbox, fill, outline, radius=24, outline_width=2):
    """Draw a card with alpha blending."""
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=outline_width)
    img.alpha_composite(overlay)


def draw_badge(img, x, y, text, bg_color, text_color, dot_color=None):
    """Draw a small pill badge with optional glowing status dot."""
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    bbox = d.textbbox((0, 0), text, font=font_badge)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    pad_left = 40 if dot_color else 24
    pad_right = 24
    pad_y = 12
    card_rect = [x, y, x + tw + pad_left + pad_right, y + th + pad_y * 2]
    d.rounded_rectangle(card_rect, radius=18, fill=bg_color)
    
    if dot_color:
        dot_cy = y + (card_rect[3] - y) // 2
        d.ellipse([x + 18, dot_cy - 6, x + 30, dot_cy + 6], fill=dot_color)
        
    d.text((x + pad_left, y + pad_y - 2), text, font=font_badge, fill=text_color)
    img.alpha_composite(overlay)


def draw_check_icon(d, x, y, size=24, color=EMERALD):
    """Draw a clean vector checkmark."""
    pts = [(x, y + size * 0.5), (x + size * 0.35, y + size * 0.9), (x + size, y + size * 0.15)]
    d.line([pts[0], pts[1]], fill=color, width=3)
    d.line([pts[1], pts[2]], fill=color, width=3)


def draw_subtitles(img, text):
    """Draw lower-third subtitles pill."""
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    
    words = text.split()
    lines = []
    curr = []
    for w in words:
        curr.append(w)
        line_str = " ".join(curr)
        bbox = d.textbbox((0, 0), line_str, font=font_caption)
        if (bbox[2] - bbox[0]) > 900:
            curr.pop()
            lines.append(" ".join(curr))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))
        
    line_h = 44
    total_h = len(lines) * line_h + 30
    box_top = 1680 - total_h // 2
    box_rect = [80, box_top, 1000, box_top + total_h]
    
    d.rounded_rectangle(box_rect, radius=20, fill=(0, 0, 0, 215), outline=(75, 85, 99), width=2)
    for idx, l in enumerate(lines):
        bbox = d.textbbox((0, 0), l, font=font_caption)
        tw = bbox[2] - bbox[0]
        tx = (WIDTH - tw) // 2
        ty = box_top + 16 + idx * line_h
        d.text((tx, ty), l, font=font_caption, fill=WHITE)
        
    img.alpha_composite(overlay)


def create_base_canvas(t, accent_color=(16, 185, 129)):
    """Create background with glowing particles and tech grid."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_DARK)
    d = ImageDraw.Draw(img)
    
    # Ambient gradient glow
    glow_x = int(WIDTH / 2 + math.sin(t * 1.5) * 120)
    glow_y = int(HEIGHT / 3 + math.cos(t * 1.2) * 100)
    
    glow_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_overlay)
    for r in range(400, 50, -50):
        alpha = int(12 * (1.0 - r / 400))
        glow_color = (*accent_color, alpha)
        gd.ellipse([glow_x - r, glow_y - r, glow_x + r, glow_y + r], fill=glow_color)
    img.alpha_composite(glow_overlay)
    
    # Grid lines
    grid_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    grd = ImageDraw.Draw(grid_overlay)
    for y in range(0, HEIGHT, 160):
        grd.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, 8), width=1)
    for x in range(0, WIDTH, 120):
        grd.line([(x, 0), (x, HEIGHT)], fill=(255, 255, 255, 8), width=1)
    img.alpha_composite(grid_overlay)
    
    # Brand Top Bar
    draw_badge(img, 80, 100, "NEXORA NEXCONNECT", (30, 41, 59, 220), CYAN)
    
    return img


def render_scene_1(t, rel_t):
    # Scene 1: 0.0s – 3.45s: DLT Approval Nightmare
    img = create_base_canvas(t, accent_color=(239, 68, 68))
    d = ImageDraw.Draw(img)
    
    draw_badge(img, 80, 180, "TELECOM COMPLIANCE BOTTLENECK", RED_BG, (254, 202, 202), dot_color=RED)
    
    d.text((80, 260), "STILL WAITING WEEKS FOR", font=font_subtitle, fill=LIGHT_GRAY)
    d.text((80, 315), "DLT APPROVALS?", font=font_title, fill=RED)
    
    card_rect = [80, 440, 1000, 1150]
    draw_rounded_card(img, card_rect, CARD_BG, (153, 27, 27), radius=28, outline_width=3)
    
    d.text((120, 480), "TRAI DLT Portal • Registration Queue", font=font_card_head, fill=WHITE)
    d.line([(120, 540), (960, 540)], fill=(75, 85, 99), width=2)
    
    pulse = (math.sin(t * 8) + 1) / 2
    glow_red = (int(185 + 70 * pulse), 28, 28)
    draw_badge(img, 120, 570, "STATUS: REJECTED", glow_red, WHITE, dot_color=(255, 100, 100))
    
    d.text((120, 660), "Principal Entity ID (PE):", font=font_small, fill=MUTED)
    d.text((120, 695), "1401552890000000001", font=font_mono, fill=WHITE)
    
    d.text((120, 770), "Requested Sender Header:", font=font_small, fill=MUTED)
    d.text((120, 805), "NEXORA (Pending 21 Days)", font=font_mono, fill=AMBER)
    
    d.text((120, 880), "Rejection Cause:", font=font_small, fill=MUTED)
    d.text((120, 915), "Variable formatting mismatch in template", font=font_body, fill=(252, 165, 165))
    
    callout = [120, 990, 960, 1090]
    draw_rounded_card(img, callout, (69, 10, 10, 180), (185, 28, 28), radius=16, outline_width=1)
    d.text((150, 1025), "[!] Campaigns Stalled • Zero Customer Reach", font=font_body_bold, fill=RED)
    
    draw_subtitles(img, "Still waiting weeks for telecom DLT approvals?")
    return img


def render_scene_2(t, rel_t):
    # Scene 2: 3.45s – 9.35s: Problem Breakdown
    img = create_base_canvas(t, accent_color=(245, 158, 11))
    d = ImageDraw.Draw(img)
    
    draw_badge(img, 80, 180, "HIGH-VOLUME DELIVERY CRISIS", (120, 53, 15), (253, 230, 138), dot_color=AMBER)
    
    d.text((80, 260), "DROPPED MESSAGES.", font=font_title, fill=WHITE)
    d.text((80, 330), "ZERO VISIBILITY.", font=font_title, fill=AMBER)
    
    cards_data = [
        ("1. Critical OTP & Alerts", "24,510 Messages Dropped", "Silent Carrier Rejection", RED),
        ("2. Carrier Aggregators", "Zero Real-Time Audit Logs", "No delivery status callbacks", AMBER),
        ("3. Budget Waste", "₹18,500 Wasted This Week", "No Auto-Refund on failures", (248, 113, 113))
    ]
    
    for i, (head, val, desc, col) in enumerate(cards_data):
        y_pos = 450 + i * 240
        slide_offset = max(0, int((1.0 - min(1.0, (rel_t - i * 0.4) * 3)) * 200))
        rect = [80 + slide_offset, y_pos, 1000 + slide_offset, y_pos + 200]
        
        draw_rounded_card(img, rect, CARD_BG, (75, 85, 99), radius=22)
        d.text((120 + slide_offset, y_pos + 25), head, font=font_body_bold, fill=MUTED)
        d.text((120 + slide_offset, y_pos + 70), val, font=font_card_head, fill=col)
        d.text((120 + slide_offset, y_pos + 130), f"• {desc}", font=font_small, fill=LIGHT_GRAY)
        
    draw_subtitles(img, "Endless compliance rejections, dropped SMS, and zero visibility into failed sends.")
    return img


def render_scene_3(t, rel_t):
    # Scene 3: 9.35s – 14.85s: Solution Intro
    img = create_base_canvas(t, accent_color=(16, 185, 129))
    d = ImageDraw.Draw(img)
    
    draw_badge(img, 80, 180, "ENTERPRISE CPaaS PLATFORM", EMERALD_BG, (167, 243, 208), dot_color=EMERALD)
    
    d.text((80, 260), "MEET NEXCONNECT", font=font_hero, fill=WHITE)
    d.text((80, 360), "Zero-Compliance-Headache Messaging", font=font_subtitle, fill=EMERALD)
    
    card_rect = [80, 480, 1000, 1260]
    draw_rounded_card(img, card_rect, CARD_BG, EMERALD, radius=32, outline_width=3)
    
    plat_box = [130, 530, 950, 720]
    draw_rounded_card(img, plat_box, (6, 78, 59, 200), EMERALD, radius=20, outline_width=2)
    d.text((170, 570), "Nexora NexConnect Engine", font=font_card_head, fill=WHITE)
    d.text((170, 630), "High-Throughput Enterprise SMS Infrastructure", font=font_small, fill=(209, 250, 229))
    
    solutions = [
        ("Automated Telecom DLT Sync", "Manage PE IDs, headers & templates in 1 place"),
        ("High-Throughput Bulk Engine", "Synchronous CPaaS dispatch with deduplication"),
        ("Upfront Atomic Wallet & Refunds", "Never pay for dropped or carrier-failed messages")
    ]
    
    for i, (title, sub) in enumerate(solutions):
        sy = 770 + i * 150
        draw_badge(img, 130, sy, title, (30, 41, 59, 220), CYAN, dot_color=EMERALD)
        d.text((130, sy + 65), sub, font=font_small, fill=LIGHT_GRAY)
        
    draw_subtitles(img, "Meet NexConnect: the enterprise messaging engine built for zero compliance headache.")
    return img


def render_scene_4(t, rel_t):
    # Scene 4: 14.85s – 21.50s: Feature 1 - DLT Console
    img = create_base_canvas(t, accent_color=(6, 182, 212))
    d = ImageDraw.Draw(img)
    
    draw_badge(img, 80, 180, "MODULE 01 • DLT COMPLIANCE", (12, 74, 96), (186, 230, 253), dot_color=CYAN)
    
    d.text((80, 260), "UNIFIED DLT CONSOLE", font=font_title, fill=WHITE)
    d.text((80, 330), "PE IDs, Headers & Templates Synced", font=font_subtitle, fill=CYAN)
    
    card_rect = [80, 430, 1000, 1280]
    draw_rounded_card(img, card_rect, CARD_BG, (14, 116, 144), radius=28, outline_width=2)
    
    d.text((120, 470), "DLT Management Console", font=font_card_head, fill=WHITE)
    d.line([(120, 520), (960, 520)], fill=(75, 85, 99), width=2)
    
    items = [
        ("Principal Entity (PE)", "1401552890000000001 (Airtel/Jio)", "ACTIVE & SYNCED", EMERALD),
        ("Sender Header (PEHeader)", "NEXORA • Transactional / Promo", "APPROVED", EMERALD),
        ("Template (HeaderTemplate)", "OTP_LOGIN_V2 ({#var#} OTP Code)", "APPROVED", EMERALD)
    ]
    
    for i, (title, val, status, col) in enumerate(items):
        iy = 550 + i * 180
        box = [120, iy, 960, iy + 140]
        draw_rounded_card(img, box, (30, 41, 59, 180), (51, 65, 85), radius=16)
        d.text((140, iy + 20), title, font=font_small, fill=MUTED)
        d.text((140, iy + 55), val, font=font_mono, fill=WHITE)
        draw_badge(img, 140, iy + 92, status, (6, 78, 59, 200), (167, 243, 208), dot_color=EMERALD)
        
    note_box = [120, 1130, 960, 1230]
    draw_rounded_card(img, note_box, (15, 23, 42, 220), (56, 189, 248), radius=16)
    d.text((150, 1165), "[+] 100% compliant with TRAI regulations across all telcos", font=font_body_bold, fill=CYAN)
    
    draw_subtitles(img, "Manage Principal Entity IDs, sender headers, and registered templates in one seamless console.")
    return img


def render_scene_5(t, rel_t):
    # Scene 5: 21.50s – 29.00s: High Volume Dispatch & Auto-Refund
    img = create_base_canvas(t, accent_color=(16, 185, 129))
    d = ImageDraw.Draw(img)
    
    draw_badge(img, 80, 180, "MODULE 02 • DISPATCH & BILLING", EMERALD_BG, (167, 243, 208), dot_color=EMERALD)
    
    d.text((80, 260), "HIGH-VOLUME DISPATCH", font=font_title, fill=WHITE)
    d.text((80, 330), "With Automatic Carrier Refunds", font=font_subtitle, fill=EMERALD)
    
    card_rect = [80, 430, 1000, 1290]
    draw_rounded_card(img, card_rect, CARD_BG, EMERALD, radius=28, outline_width=2)
    
    progress = min(1.0, rel_t / 4.0)
    sent_count = int(12840 * progress)
    
    d.text((120, 470), "Live Dispatch Counter", font=font_small, fill=MUTED)
    d.text((120, 510), f"{sent_count:,} / 12,840 Sent", font=font_stat_num, fill=WHITE)
    
    bar_rect = [120, 600, 960, 620]
    draw_rounded_card(img, bar_rect, (30, 41, 59), None, radius=10)
    fill_w = int(840 * progress)
    if fill_w > 10:
        fill_bar = [120, 600, 120 + fill_w, 620]
        draw_rounded_card(img, fill_bar, EMERALD, None, radius=10)
        
    draw_badge(img, 120, 650, "60s Sliding-Window Deduplication: ACTIVE", (15, 23, 42), CYAN, dot_color=CYAN)
    
    ledger_box = [120, 750, 960, 1140]
    draw_rounded_card(img, ledger_box, (15, 23, 42, 230), (55, 65, 81), radius=20)
    d.text((150, 780), "Company Wallet & Transaction Ledger", font=font_body_bold, fill=WHITE)
    d.line([(150, 830), (930, 830)], fill=(55, 65, 81), width=1)
    
    d.text((150, 860), "• Atomic Debit (Row Locked):", font=font_small, fill=MUTED)
    d.text((620, 860), "- 12,840 Credits", font=font_mono, fill=WHITE)
    
    d.text((150, 930), "• Carrier Dispatched Successfully:", font=font_small, fill=MUTED)
    d.text((620, 930), "12,838 Delivered", font=font_mono, fill=EMERALD)
    
    draw_rounded_card(img, [150, 1000, 930, 1090], (6, 78, 59, 200), EMERALD, radius=14)
    d.text((170, 1025), "[+] 2 Carrier Failures: +2 Credits AUTO-REFUNDED", font=font_body_bold, fill=(209, 250, 229))
    
    draw_subtitles(img, "Dispatch high-volume SMS with auto-deduplication, instant delivery, and automatic refunds on failed dispatches.")
    return img


def render_scene_6(t, rel_t):
    # Scene 6: 29.00s – 34.35s: SLA & Reliability
    img = create_base_canvas(t, accent_color=(6, 182, 212))
    d = ImageDraw.Draw(img)
    
    draw_badge(img, 80, 180, "ENTERPRISE BENCHMARKS", (12, 74, 96), (186, 230, 253), dot_color=CYAN)
    
    d.text((80, 260), "UNSHAKEABLE RELIABILITY", font=font_title, fill=WHITE)
    d.text((80, 330), "Guaranteed Delivery & Compliance", font=font_subtitle, fill=CYAN)
    
    grid_metrics = [
        ("99.9%", "Delivery Success Rate", EMERALD),
        ("1.4s", "Average OTP Latency", CYAN),
        ("5+ Telcos", "Airtel, Jio, VI, BSNL, Tata", WHITE),
        ("100%", "TRAI DLT Compliant", (167, 243, 208))
    ]
    
    for i, (val, label, col) in enumerate(grid_metrics):
        col_idx = i % 2
        row_idx = i // 2
        gx = 80 + col_idx * 480
        gy = 440 + row_idx * 330
        rect = [gx, gy, gx + 440, gy + 290]
        
        draw_rounded_card(img, rect, CARD_BG, (55, 65, 81), radius=24)
        d.text((gx + 40, gy + 50), val, font=font_hero, fill=col)
        d.text((gx + 40, gy + 170), label, font=font_body_bold, fill=LIGHT_GRAY)
        
    trust_box = [80, 1140, 1000, 1260]
    draw_rounded_card(img, trust_box, (15, 23, 42, 220), (55, 65, 81), radius=20)
    d.text((120, 1180), "[OK] Enterprise Multi-Tenant Architecture & REST API", font=font_card_head, fill=WHITE)
    
    draw_subtitles(img, "Guaranteed reliability and 100% compliance on every single send.")
    return img


def render_scene_7(t, rel_t):
    # Scene 7: 34.35s – 38.68s: Outro & Call to Action
    img = create_base_canvas(t, accent_color=(16, 185, 129))
    d = ImageDraw.Draw(img)
    
    draw_badge(img, 80, 180, "SCALE YOUR MESSAGING TODAY", EMERALD_BG, (167, 243, 208), dot_color=EMERALD)
    
    d.text((80, 260), "UPGRADE TO", font=font_title, fill=LIGHT_GRAY)
    d.text((80, 335), "NEXCONNECT TODAY", font=font_hero, fill=WHITE)
    
    card_rect = [80, 460, 1000, 1260]
    draw_rounded_card(img, card_rect, CARD_BG, EMERALD, radius=32, outline_width=3)
    
    logo_rect = [140, 520, 940, 720]
    draw_rounded_card(img, logo_rect, (6, 78, 59, 220), EMERALD, radius=24, outline_width=2)
    d.text((180, 570), "NEXORA NEXCONNECT", font=font_hero, fill=WHITE)
    d.text((180, 650), "Enterprise Communication Infrastructure", font=font_body, fill=(209, 250, 229))
    
    d.text((140, 770), "• Streamlined Telecom DLT Compliance", font=font_body_bold, fill=LIGHT_GRAY)
    d.text((140, 830), "• High-Throughput Bulk SMS Dispatch", font=font_body_bold, fill=LIGHT_GRAY)
    d.text((140, 890), "• Transparent Billing with Auto-Refunds", font=font_body_bold, fill=LIGHT_GRAY)
    
    pulse = (math.sin(t * 6) + 1) / 2
    btn_col = (int(16 + 20 * pulse), int(185 + 25 * pulse), int(129 + 30 * pulse))
    btn_rect = [140, 980, 940, 1110]
    draw_rounded_card(img, btn_rect, btn_col, WHITE, radius=24, outline_width=3)
    
    d.text((190, 1020), "SCHEDULE YOUR DEMO ->", font=font_subtitle, fill=BG_DARK)
    
    d.text((380, 1150), "nexora.com/demo", font=font_subtitle, fill=CYAN)
    
    draw_subtitles(img, "Book your live enterprise demo today at nexora dot com.")
    return img


def render_frame(t):
    """Render frame at time t."""
    if t < 3.45:
        return render_scene_1(t, t)
    elif t < 9.35:
        return render_scene_2(t, t - 3.45)
    elif t < 14.85:
        return render_scene_3(t, t - 9.35)
    elif t < 21.50:
        return render_scene_4(t, t - 14.85)
    elif t < 29.00:
        return render_scene_5(t, t - 21.50)
    elif t < 34.35:
        return render_scene_6(t, t - 29.00)
    else:
        return render_scene_7(t, t - 34.35)


def main():
    run_dir = Path("/home/abhay-chauhan/work/workflows/marketing-video/outputs/2026-10-10-nexconnect-sms")
    audio_file = run_dir / "audio" / "soundtrack.m4a"
    out_video = run_dir / "nexconnect_marketing_reel.mp4"
    
    if not audio_file.exists():
        print(f"Error: {audio_file} not found.")
        sys.exit(1)
        
    duration = 38.68
    total_frames = int(duration * FPS)
    
    print(f"Rendering NexConnect Motion Graphic Reel...")
    print(f"Resolution: {WIDTH}x{HEIGHT} (Vertical 9:16) @ {FPS} fps")
    print(f"Total Frames: {total_frames} (~{duration:.2f}s)")
    print(f"Audio Track: {audio_file}")
    print(f"Target Video: {out_video}")
    
    cmd = [
        FFMPEG_BIN, "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgba",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-r", str(FPS),
        "-i", "-",
        "-i", str(audio_file),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-shortest",
        str(out_video)
    ]
    
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    
    for frame_idx in range(total_frames):
        t = frame_idx / FPS
        frame_img = render_frame(t)
        p.stdin.write(frame_img.tobytes())
        if frame_idx % 60 == 0 or frame_idx == total_frames - 1:
            progress = (frame_idx + 1) / total_frames * 100
            print(f"  Frame {frame_idx + 1}/{total_frames} ({progress:.1f}%) — t={t:.2f}s")
            
    p.stdin.close()
    p.wait()
    
    if p.returncode != 0:
        print("FFmpeg error:", p.stderr.read().decode())
        sys.exit(1)
        
    print(f"\nSUCCESS! Rendered video saved to: {out_video}")
    print(f"File size: {out_video.stat().st_size / (1024 * 1024):.2f} MB")


if __name__ == "__main__":
    main()
