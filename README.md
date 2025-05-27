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

## Assets

Gorilla sprite images can be generated automatically or provided manually.

### Generate default sprites
Ensure you have Pillow installed (`pip install Pillow`) and run:

```bash
python3 scripts/generate_gorilla_sprites.py
```

This will create the following files in `assets/images`:
- `gorilla_red.png` for Player 1 (red bandana gorilla)
- `gorilla_blue.png` for Player 2 (blue bandana gorilla)

### Custom sprites
Alternatively, place your own square PNG images (around 80×80px) with transparent backgrounds in `assets/images`:
- `gorilla_red.png` and `gorilla_blue.png`