#!/usr/bin/env python3
"""Generate default ogre sprite images for Gorilla 2.0 game."""

import os
from PIL import Image, ImageDraw

# Constants (adjust to match MONKEY_RADIUS in src/main.py)
SIZE = 120
MONKEY_RADIUS = 30

def lighten_color(rgb, factor):
    return tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)

def darken_color(rgb, factor):
    return tuple(max(0, int(c * (1 - factor))) for c in rgb)

def draw_gorilla(band_color):
    """Return an RGBA Image of a stylized brown ogre with given warpaint color."""
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Colors (brown ogre skin)
    head_color = (139, 69, 19, 255)
    eye_white = (255, 255, 255, 255)
    pupil_color = (0, 0, 0, 255)
    band_color = band_color + (255,)
    body_color = head_color

    # Head
    center = (SIZE // 2, SIZE // 2 - MONKEY_RADIUS // 3)
    head_r = MONKEY_RADIUS
    draw.ellipse([
        center[0] - head_r, center[1] - head_r,
        center[0] + head_r, center[1] + head_r,
    ], fill=head_color)
    # Ears (pointed ogre ears)
    ear_w = head_r // 2
    ear_h = head_r // 2
    draw.polygon([
        (center[0] - head_r, center[1] - ear_h // 2),
        (center[0] - head_r - ear_w, center[1]),
        (center[0] - head_r, center[1] + ear_h // 2),
    ], fill=head_color)
    draw.polygon([
        (center[0] + head_r, center[1] - ear_h // 2),
        (center[0] + head_r + ear_w, center[1]),
        (center[0] + head_r, center[1] + ear_h // 2),
    ], fill=head_color)

    hl_color = lighten_color(head_color[:3], 0.3) + (80,)
    sh_color = darken_color(head_color[:3], 0.4) + (100,)
    hl_r = int(head_r * 0.8)
    hl_center = (center[0] - int(head_r * 0.2), center[1] - int(head_r * 0.2))
    draw.ellipse([
        hl_center[0] - hl_r, hl_center[1] - hl_r,
        hl_center[0] + hl_r, hl_center[1] + hl_r,
    ], fill=hl_color)
    sh_r = int(head_r * 1.1)
    sh_center = (center[0] + int(head_r * 0.2), center[1] + int(head_r * 0.2))
    draw.ellipse([
        sh_center[0] - sh_r, sh_center[1] - sh_r,
        sh_center[0] + sh_r, sh_center[1] + sh_r,
    ], fill=sh_color)

    # Nose (triangular ogre nose)
    nose_w = head_r // 2
    nose_h = head_r // 3
    nose_color = darken_color(head_color[:3], 0.3) + (255,)
    draw.polygon([
        (center[0], center[1]),
        (center[0] - nose_w // 2, center[1] + nose_h),
        (center[0] + nose_w // 2, center[1] + nose_h),
    ], fill=nose_color)
    # Mouth (frown-like arc)
    mouth_w = head_r
    mouth_h = head_r // 2
    mouth_box = [
        center[0] - mouth_w // 2,
        center[1] + head_r // 4,
        center[0] + mouth_w // 2,
        center[1] + head_r // 4 + mouth_h,
    ]
    draw.arc(mouth_box, start=20, end=160, fill=pupil_color, width=3)
    # Eyes
    eye_w = int(MONKEY_RADIUS * 0.4)
    eye_h = int(MONKEY_RADIUS * 0.6)
    eye_y = center[1] - MONKEY_RADIUS // 4
    eye_x_off = int(MONKEY_RADIUS * 0.6)
    draw.ellipse([
        center[0] - eye_x_off - eye_w // 2,
        eye_y - eye_h // 2,
        center[0] - eye_x_off + eye_w // 2,
        eye_y + eye_h // 2,
    ], fill=eye_white)
    draw.ellipse([
        center[0] + eye_x_off - eye_w // 2,
        eye_y - eye_h // 2,
        center[0] + eye_x_off + eye_w // 2,
        eye_y + eye_h // 2,
    ], fill=eye_white)
    # Pupils
    pupil_r = max(3, MONKEY_RADIUS // 7)
    draw.ellipse([
        center[0] - eye_x_off - pupil_r,
        eye_y - pupil_r,
        center[0] - eye_x_off + pupil_r,
        eye_y + pupil_r,
    ], fill=pupil_color)
    draw.ellipse([
        center[0] + eye_x_off - pupil_r,
        eye_y - pupil_r,
        center[0] + eye_x_off + pupil_r,
        eye_y + pupil_r,
    ], fill=pupil_color)
    # Bandana
    band_h = max(int(MONKEY_RADIUS * 0.25), 6)
    draw.rectangle([
        center[0] - head_r,
        center[1] - band_h // 2 + MONKEY_RADIUS // 6,
        center[0] + head_r,
        center[1] + band_h // 2 + MONKEY_RADIUS // 6,
    ], fill=band_color)

    # Body
    body_w = int(MONKEY_RADIUS * 2)
    body_h = int(MONKEY_RADIUS * 1.2)
    body_y = center[1] + head_r
    draw.ellipse([
        center[0] - body_w // 2,
        body_y,
        center[0] + body_w // 2,
        body_y + body_h,
    ], fill=body_color)

    hl_color = lighten_color(body_color[:3], 0.3) + (80,)
    sh_color = darken_color(body_color[:3], 0.4) + (100,)
    b_center = (center[0], body_y + body_h // 2)
    hl_w = int(body_w * 0.8)
    hl_h = int(body_h * 0.8)
    draw.ellipse([
        b_center[0] - hl_w // 2 - int(body_w * 0.1),
        b_center[1] - hl_h // 2 - int(body_h * 0.1),
        b_center[0] + hl_w // 2 - int(body_w * 0.1),
        b_center[1] + hl_h // 2 - int(body_h * 0.1),
    ], fill=hl_color)
    sh_w = int(body_w * 1.1)
    sh_h = int(body_h * 1.1)
    draw.ellipse([
        b_center[0] - sh_w // 2 + int(body_w * 0.1),
        b_center[1] - sh_h // 2 + int(body_h * 0.1),
        b_center[0] + sh_w // 2 + int(body_w * 0.1),
        b_center[1] + sh_h // 2 + int(body_h * 0.1),
    ], fill=sh_color)

    arm_h = int(MONKEY_RADIUS * 0.6)
    arm_w = int(MONKEY_RADIUS * 1.5)
    arm_y = center[1] + head_r + int(body_h * 0.3)
    a1 = (center[0] - body_w // 2 - arm_w, arm_y, center[0] - body_w // 2, arm_y + arm_h)
    a2 = (center[0] + body_w // 2, arm_y, center[0] + body_w // 2 + arm_w, arm_y + arm_h)
    draw.ellipse(a1, fill=body_color)
    draw.ellipse(a2, fill=body_color)
    fist_r = int(MONKEY_RADIUS * 0.4)
    draw.ellipse((a1[0] - fist_r, arm_y + arm_h - fist_r, a1[0] + fist_r, arm_y + arm_h + fist_r), fill=head_color)
    draw.ellipse((a2[2] - fist_r, arm_y + arm_h - fist_r, a2[2] + fist_r, arm_y + arm_h + fist_r), fill=head_color)
    for ax, ay, bx, by in (a1, a2):
        w = bx - ax
        h = by - ay
        cx = ax + w / 2
        cy = ay + h / 2
        dx = int(w * 0.2)
        dy = int(h * 0.2)
        hl = lighten_color(body_color[:3], 0.3) + (80,)
        sh = darken_color(body_color[:3], 0.4) + (100,)
        hl_w = int(w * 0.8)
        hl_h = int(h * 0.8)
        draw.ellipse((cx - hl_w / 2 - dx, cy - hl_h / 2 - dy, cx + hl_w / 2 - dx, cy + hl_h / 2 - dy), fill=hl)
        sh_w = int(w * 1.1)
        sh_h = int(h * 1.1)
        draw.ellipse((cx - sh_w / 2 + dx, cy - sh_h / 2 + dy, cx + sh_w / 2 + dx, cy + sh_h / 2 + dy), fill=sh)

    leg_h = int(MONKEY_RADIUS * 0.8)
    leg_w = int(MONKEY_RADIUS * 0.7)
    leg_y = body_y + body_h - int(leg_h * 0.5)
    l1 = (center[0] - body_w // 4 - leg_w // 2, leg_y, center[0] - body_w // 4 + leg_w // 2, leg_y + leg_h)
    l2 = (center[0] + body_w // 4 - leg_w // 2, leg_y, center[0] + body_w // 4 + leg_w // 2, leg_y + leg_h)
    draw.ellipse(l1, fill=body_color)
    draw.ellipse(l2, fill=body_color)
    for ax, ay, bx, by in (l1, l2):
        w = bx - ax
        h = by - ay
        cx = ax + w / 2
        cy = ay + h / 2
        dx = int(w * 0.2)
        dy = int(h * 0.2)
        hl = lighten_color(body_color[:3], 0.3) + (80,)
        sh = darken_color(body_color[:3], 0.4) + (100,)
        hl_w = int(w * 0.8)
        hl_h = int(h * 0.8)
        draw.ellipse((cx - hl_w / 2 - dx, cy - hl_h / 2 - dy, cx + hl_w / 2 - dx, cy + hl_h / 2 - dy), fill=hl)
        sh_w = int(w * 1.1)
        sh_h = int(h * 1.1)
        draw.ellipse((cx - sh_w / 2 + dx, cy - sh_h / 2 + dy, cx + sh_w / 2 + dx, cy + sh_h / 2 + dy), fill=sh)

    return img

def main():
    """Generate gorilla sprite PNGs into assets/images/ directory."""
    os.makedirs('assets/images', exist_ok=True)
    colors = {'red': (200, 30, 30), 'blue': (30, 30, 200)}
    for name, rgb in colors.items():
        img = draw_gorilla(rgb)
        path = os.path.join('assets/images', f'gorilla_{name}.png')
        img.save(path)
        print(f"Created {path}")

if __name__ == '__main__':
    main()