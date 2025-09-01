import time
import gc
from galactic import GalacticUnicorn, Channel
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY

# Minimal program: show "Brush!" on a white background with black text.

gc.collect()

gu = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)

width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT

graphics.set_font("bitmap8")
gu.set_brightness(0.5)

# pens
PEN_WHITE = graphics.create_pen(0, 0, 0)
PEN_BLACK = graphics.create_pen(255, 255, 255)

# additional colors for the lightsaber animation
PEN_BG = graphics.create_pen(0, 0, 0)          # true black background
PEN_RED = graphics.create_pen(255, 0, 0)       # bright core
PEN_RED_MID = graphics.create_pen(180, 0, 0)   # mid glow
PEN_RED_LOW = graphics.create_pen(90, 0, 0)    # low glow

TEXT = "Pusse!"

# countdown length (seconds)
BRUSH_SECONDS = 120
COUNTDOWN_SCALE = 1


def show_brush():
    graphics.set_pen(PEN_WHITE)
    graphics.clear()
    w = graphics.measure_text(TEXT, 1)
    x = int((width - w) / 2)
    y = int((height / 2) - 4)
    graphics.set_pen(PEN_BLACK)
    graphics.text(TEXT, x, y, -1, 1)
    gu.update(graphics)


def show_time(remaining):
    # Short message to fit the display: "Brush X sec!"
    s = f"Puss {remaining} s!"
    scale = 1
    graphics.set_pen(PEN_WHITE)
    graphics.clear()
    w = graphics.measure_text(s, scale)
    x = int((width - w) / 2)
    # small top margin
    glyph_h = 8 * scale
    y = int((height - glyph_h) / 2) + 1
    graphics.set_pen(PEN_BLACK)
    graphics.text(s, x, y, -1, scale)
    gu.update(graphics)


def play_fanfare():
    try:
        ch = gu.synth_channel(0)
        # louder default volume (test carefully)
        ch.configure(waveforms=Channel.SQUARE + Channel.SINE,
                     attack=0.002,
                     decay=0.015,
                     sustain=0,
                     release=0.02,
                     volume=60000 / 65535)
        gu.play_synth()

        # notes = ((784, 0.22), (988, 0.22), (1175, 0.84)) # Simple melody

        notes = [ # Star Wars Imperial March theme
            (392, 0.3), (1, 0.1), (392, 0.3), (1, 0.1), (392, 0.3), (1, 0.1),  # G G G
            (311, 0.2),                                                        # Eb
            (466, 0.2),                                                        # Bb
            (392, 0.3), (1, 0.1),                                              # G
            (311, 0.2),                                                        # Eb
            (466, 0.2),                                                        # Bb
            (392, 0.4), (1, 0.1),                                              # G

            (587, 0.3),(1, 0.1), (587, 0.3), (1, 0.1), (587, 0.3), (1, 0.1),   # D D D
            (622, 0.2),                                                        # Eb (D#)
            (466, 0.2),                                                        # Bb
            (369, 0.3), (1, 0.1),                                              # F#
            (311, 0.2),                                                        # Eb
            (466, 0.2),                                                        # Bb
            (392, 0.4), (1, 0.1),                                              # G
        ]

        def draw_frame(frame):
            # Horizontal lightsaber: black background, bright red core, glow above/below and flickering end flares
            graphics.set_pen(PEN_BG)
            graphics.clear()

            cy = int(height / 2)
            left = 1
            right = width - 2

            # low outer glow (two pixels away)
            graphics.set_pen(PEN_RED_LOW)
            if cy - 2 >= 0:
                for x in range(left + 1, right - 1):
                    graphics.pixel(x, cy - 2)
            if cy + 2 < height:
                for x in range(left + 1, right - 1):
                    graphics.pixel(x, cy + 2)

            # mid glow (one pixel away)
            graphics.set_pen(PEN_RED_MID)
            if cy - 1 >= 0:
                for x in range(left, right + 1):
                    graphics.pixel(x, cy - 1)
            if cy + 1 < height:
                for x in range(left, right + 1):
                    graphics.pixel(x, cy + 1)

            # bright core
            graphics.set_pen(PEN_RED)
            for x in range(left, right + 1):
                graphics.pixel(x, cy)

            # flickering end flares (small bursts at each end)
            flare_on = (frame % 4) != 0
            if flare_on:
                fx = left
                for dx in range(0, 3):
                    for dy in (-1, 0, 1):
                        px = fx + dx
                        py = cy + dy
                        if 0 <= px < width and 0 <= py < height:
                            graphics.pixel(px, py)
                fx = right
                for dx in range(-2, 1):
                    for dy in (-1, 0, 1):
                        px = fx + dx
                        py = cy + dy
                        if 0 <= px < width and 0 <= py < height:
                            graphics.pixel(px, py)

            gu.update(graphics)

        for freq, dur in notes:
            ch.play_tone(freq, dur)
            # animate at ~20 FPS while the note plays
            steps = max(1, int(dur * 20))
            for step in range(steps):
                draw_frame(step)
                time.sleep(dur / steps)
    finally:
        # ensure synth is stopped and resources freed
        try:
            gu.stop_playing()
        except Exception:
            pass


while True:
    # show the idle message
    show_brush()

    # wait for A press
    if gu.is_pressed(GalacticUnicorn.SWITCH_A):
        # debounce: wait for release
        while gu.is_pressed(GalacticUnicorn.SWITCH_A):
            time.sleep(0.01)

        # countdown from BRUSH_SECONDS to 1, update every second
        restarted = False
        for remaining in range(BRUSH_SECONDS, 0, -1):
            # allow immediate restart if A pressed again
            if gu.is_pressed(GalacticUnicorn.SWITCH_A):
                restarted = True
                # wait for release before breaking
                while gu.is_pressed(GalacticUnicorn.SWITCH_A):
                    time.sleep(0.01)
                break

            show_time(remaining)
            # sleep in small steps so we can detect A presses quickly
            for _ in range(10):
                time.sleep(0.1)
                if gu.is_pressed(GalacticUnicorn.SWITCH_A):
                    restarted = True
                    break
            if restarted:
                break

        if not restarted:
            # countdown completed
            play_fanfare()

        # return to the Brush! message
        show_brush()

    time.sleep(0.05)