#!/usr/bin/env python3
"""Generate default gorilla sprite images for Gorilla 2.0 game."""

import os
from PIL import Image, ImageDraw

# Constants
SIZE = 80
MONKEY_RADIUS = 20

def draw_gorilla(band_color):
    """Return an RGBA Image of a stylized gorilla with given bandana color."""
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Colors
    head_color = (80, 80, 80, 255)
    muzzle_color = (150, 150, 150, 255)
    eye_white = (255, 255, 255, 255)
    pupil_color = (0, 0, 0, 255)
    band_color = band_color + (255,)
    body_color = head_color

    # Head
    center = (SIZE // 2, SIZE // 2 - 10)
    head_r = MONKEY_RADIUS
    draw.ellipse([center[0] - head_r, center[1] - head_r,
                  center[0] + head_r, center[1] + head_r],
                  fill=head_color)
    # Ears
    ear_r = head_r // 2
    draw.ellipse([center[0] - head_r - ear_r + 5, center[1] - ear_r,
                  center[0] - head_r + ear_r + 5, center[1] + ear_r],
                  fill=head_color)
    draw.ellipse([center[0] + head_r - ear_r - 5, center[1] - ear_r,
                  center[0] + head_r + ear_r - 5, center[1] + ear_r],
                  fill=head_color)

    # Muzzle
    muzzle_w, muzzle_h = 36, 24
    draw.ellipse([center[0] - muzzle_w // 2, center[1] - muzzle_h // 4 + 10,
                  center[0] + muzzle_w // 2, center[1] + muzzle_h // 4 + 10],
                  fill=muzzle_color)
    # Eyes
    eye_w, eye_h = 8, 12
    eye_y = center[1] - 5
    draw.ellipse([center[0] - 12 - eye_w // 2, eye_y - eye_h // 2,
                  center[0] - 12 + eye_w // 2, eye_y + eye_h // 2],
                  fill=eye_white)
    draw.ellipse([center[0] + 12 - eye_w // 2, eye_y - eye_h // 2,
                  center[0] + 12 + eye_w // 2, eye_y + eye_h // 2],
                  fill=eye_white)
    # Pupils
    pupil_r = 3
    draw.ellipse([center[0] - 12 - pupil_r, eye_y - pupil_r,
                  center[0] - 12 + pupil_r, eye_y + pupil_r],
                  fill=pupil_color)
    draw.ellipse([center[0] + 12 - pupil_r, eye_y - pupil_r,
                  center[0] + 12 + pupil_r, eye_y + pupil_r],
                  fill=pupil_color)
    # Bandana
    band_h = 8
    draw.rectangle([center[0] - head_r, center[1] - band_h // 2 + 5,
                    center[0] + head_r, center[1] + band_h // 2 + 5],
                   fill=band_color)

    # Body
    body_w, body_h = 40, 24
    body_y = center[1] + head_r
    draw.ellipse([center[0] - body_w // 2, body_y,
                  center[0] + body_w // 2, body_y + body_h],
                  fill=body_color)

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