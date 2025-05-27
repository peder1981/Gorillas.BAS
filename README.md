 # Gorilla 2.0

 Modern reinterpretation of the classic QBASIC game Gorillas.BAS.

 ## Stack
 Python + Pygame

- ## MVP
- Local two-player duel with turn-based throwing of explosive bananas
- Adjustable angle, power, and wind settings
- Basic physics simulation with gravity and wind
- Score tracking and round reset

## Setup
 ```bash
 python3 -m venv venv
 source venv/bin/activate
 pip install -r requirements.txt
 ```

 ## Running
```bash
python3 src/main.py
# assets/ folder will be loaded automatically for images and sounds
```

### Resolution
The game window defaults to **1024×768** pixels.

### Comic-style Filter
The game applies a real-time comic-book filter (posterization) to emulate Stan Lee comics style. Ensure Pillow is installed (already included in requirements).

## Assets

Ogre sprite images can be generated automatically or provided manually.

### Generate default sprites (brown ogres)
Ensure you have Pillow installed (`pip install Pillow`) and run:

```bash
python3 scripts/generate_gorilla_sprites.py
```

This will create the following files in `assets/images` (each **120×120px**), using enhanced shading to emulate a richer 16‑bit art style:
- `gorilla_red.png` for Player 1 (ogre with red warpaint)
- `gorilla_blue.png` for Player 2 (ogre with blue warpaint)

### Custom ogre sprites
Alternatively, place your own square PNG images (around 120×120px) with transparent backgrounds in `assets/images`:
- `gorilla_red.png` and `gorilla_blue.png`