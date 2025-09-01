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

TEXT = "Pusse!"

# countdown length (seconds)
BRUSH_SECONDS = 90
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

        notes = ((784, 0.22), (988, 0.22), (1175, 0.84))

        def draw_frame(frame):
            # simple pulsing border animation
            graphics.set_pen(PEN_WHITE)
            graphics.clear()
            thickness = 1 + (frame % 3)
            graphics.set_pen(PEN_BLACK)
            w = width
            h = height
            # top and bottom
            for t in range(thickness):
                for x in range(t, w - t):
                    graphics.pixel(x, t)
                    graphics.pixel(x, h - 1 - t)
            # left and right
            for t in range(thickness):
                for y in range(t, h - t):
                    graphics.pixel(t, y)
                    graphics.pixel(w - 1 - t, y)
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
