#!/usr/bin/env python3
"""Pygame target visualization for x*(t).

Usage:
  python3 pygame_target.py            # attempts GUI mode
  python3 pygame_target.py --headless # runs console mode for verification
  python3 pygame_target.py --duration 10 --fps 30

Controls in GUI:
  SPACE - pause/resume
  C - clear trail
  ESC or window close - quit
"""

import sys
import math
import time
import argparse
import pygame
from datetime import datetime
WIDTH, HEIGHT = 1500, 1000




def x_star(t):
    return (-7.8*math.sin(0.12*t)
            + 1.6*math.sin(0.28*t)
            + 9.4*math.sin(0.37*t)
            - 10.6*math.sin(0.64*t))


def run_headless(duration=5.0, fps=20, out_csv=None, speed=10.0):
    dt = 1.0 / fps
    t0 = time.time()
    t = 0.0
    samples = []
    print(f"Headless mode: running for {duration}s at {fps} Hz (speed={speed} units/s)")
    while t < duration:
        y = x_star(t)
        x_forward = speed * t
        #print(f"t={t:.3f}, x_forward={x_forward:.6f}, y={y:.6f}")
        samples.append((t, x_forward, y))
        time.sleep(dt)
        t = time.time() - t0
    if out_csv:
        try:
            import csv
            with open(out_csv, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["t", "x"])
                w.writerows(samples)
            print(f"Saved {len(samples)} samples to {out_csv}")
        except Exception as e:
            print("Failed to save CSV:", e)
    return samples

def get_participant_info(screen, WIDTH, HEIGHT):
    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    participant_id = ""
    name = ""
    age = ""

    fields = ["participant_id", "name", "age"]
    active = 0  # which field is active

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active = (active + 1) % 3

                elif event.key == pygame.K_RETURN:
                    print("ENTER key detected!!!!!!!")
                    if participant_id and name and age:
                        return participant_id, name, int(age)

                elif event.key == pygame.K_BACKSPACE:
                    if active == 0:
                        participant_id = participant_id[:-1]
                    elif active == 1:
                        name = name[:-1]
                    elif active == 2:
                        age = age[:-1]

                else:
                    if active == 0 and event.unicode.isprintable():
                        participant_id += event.unicode
                    elif active == 1 and event.unicode.isprintable():
                        name += event.unicode
                    elif active == 2 and event.unicode.isdigit():
                        age += event.unicode

        # ---------- DRAW ----------
        screen.fill((20, 20, 20))

        title = font.render("Enter Participant Info", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        def draw_field(label, value, y, is_active):
            color = (255, 255, 0) if is_active else (200, 200, 200)
            text = font.render(f"{label}: {value}", True, color)
            screen.blit(text, (200, y))

        draw_field("Participant ID", participant_id, 180, active == 0)
        draw_field("Name", name, 240, active == 1)
        draw_field("Age", age, 300, active == 2)

        hint = font.render("TAB = switch fields   ENTER = start", True, (160, 160, 160))
        screen.blit(hint, (200, 380))

        pygame.display.flip()
        clock.tick(30)


def run_gui( screen, participant_id, name, age, fps=60, pixels_per_unit=12.0, duration=None, lookahead=2.0, lookahead_steps=20, save_video=None, log_writer=None, trial_id=0,):    #import pygame
    #pygame.init()
    WIDTH, HEIGHT = 1500, 1000
    pygame.display.set_caption("Moving Target (x*(t))")
    clock = pygame.time.Clock()

    center_x = WIDTH // 2
    center_y = HEIGHT // 2
    radius = 10
    color = (220, 50, 50)
    trail = []
    max_trail = 800
    
    cursor_radius = 6
    cursor_surf = pygame.Surface((cursor_radius*2, cursor_radius*2), pygame.SRCALPHA)
    pygame.draw.circle(
    cursor_surf,
    (255, 230, 50),  # yellow
    (cursor_radius, cursor_radius),
    cursor_radius
)
    pygame.mouse.set_cursor((cursor_radius, cursor_radius), cursor_surf)
    #pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW) # Other options include ARROW, CROSSHAIR, IBEAM, etc.
    

    start_time = time.time()
    running = True
    paused = False

    last_pos = (center_x, center_y)
    last_t = 0.0

   #import csv

    #log_file = open("tracking_data.csv", "w", newline="")
    #log_writer = csv.writer(log_file)
    #log_writer.writerow(["time", "tracker_x", "tracker_y", "mouse_x","mouse_y"])

    # video writer setup
    video_writer = None
    frame_count = 0
    if save_video:
        try:
            import cv2
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(save_video, fourcc, float(fps), (WIDTH, HEIGHT))
            print(f"Recording video to {save_video} at {fps} fps")
        except ImportError:
            print("cv2 (opencv-python) not available; trying imageio...")
            try:
                import imageio
                video_writer = imageio.get_writer(save_video, fps=fps, codec='libx264')
                print(f"Recording video to {save_video} at {fps} fps with imageio")
            except Exception as e:
                print(f"Video recording unavailable: {e}")
    ct = 0
    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x_units = mouse_x / pixels_per_unit
        mouse_y_units = (center_y - mouse_y) / pixels_per_unit
        dt_ms = clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_c:
                    trail.clear()
                elif event.key == pygame.K_ESCAPE:
                    running = False
        #if ct <=60:
            #ct +=1
        #else:
            #log_writer.writerow([t, x_units, y_units, mouse_x_units, mouse_y_units])
            #log_writer.writerow([trial_id,t, x_units,y_units,mouse_x_units, mouse_y_units,])
            #ct = 0

        # determine current time (respect paused state)
        if not paused:
            t = time.time() - start_time
            last_t = t
        else:
            t = last_t

        # vertical motion follows the sinusoidal equation
        y_units = x_star(t)
        # horizontal motion advances forward with time
        x_units = forward_speed * t

        if ct <=10:
            ct +=1
        else:
            timestamp = datetime.now().isoformat()
            #log_writer.writerow([t, x_units, y_units, mouse_x_units, mouse_y_units])
            log_writer.writerow([timestamp, participant_id, age, trial_id,t, x_units,y_units,mouse_x_units, mouse_y_units,])
            ct = 0

        x_px = int((x_units * pixels_per_unit) % WIDTH) if wrap else int(x_units * pixels_per_unit)
        y_px = int(center_y + y_units * pixels_per_unit)

        # preview (dotted) of future trajectory
        preview_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for k in range(1, lookahead_steps + 1):
            dt_future = (k * (lookahead / float(lookahead_steps)))
            t_future = t + dt_future
            y_f = x_star(t_future)
            x_f_units = forward_speed * t_future
            x_f_px = int((x_f_units * pixels_per_unit) % WIDTH) if wrap else int( x_f_units * pixels_per_unit)
            y_f_px = int(center_y + y_f * pixels_per_unit)
            alpha = int(200 * (1.0 - (k / float(lookahead_steps))))
            # small faded dot for lookahead
            pygame.draw.circle(preview_surf, (150, 200, 250, alpha), (x_f_px, y_f_px), 3)

        # if wrapping jumps backward, clear trail to avoid drawing long connector lines
        if wrap and trail and abs(x_px - trail[-1][0]) > WIDTH // 2:
            trail.clear()
        last_pos = (x_px, y_px)
        trail.append(last_pos)
        if len(trail) > max_trail:
            trail.pop(0)

        # draw
        screen.fill((30, 30, 30))
        # draw lookahead preview first (so trail/target overlay it)
        screen.blit(preview_surf, (0, 0))
        if len(trail) > 1:
            pygame.draw.lines(screen, (100, 200, 250), False, trail, 2)
        pygame.draw.line(screen, (80, 80, 80), (0, center_y), (WIDTH, center_y), 1)
        # draw target
        try:
            pygame.draw.circle(screen, color, last_pos, radius)
        except UnboundLocalError:
            # before first pos set
            pass

        font = pygame.font.SysFont(None, 20)
        try:
            t = time.time() - start_time
            y_units = x_star(t)
            x_units = forward_speed * t
            fps_text = font.render( f"t={t:.2f}s  " f"x={x_units:.2f}u  y={y_units:.2f}u  " f"mouse=({mouse_x_units:.2f}u,{mouse_y_units:.2f}u)  " f"FPS={clock.get_fps():.0f}", True, (200, 200, 200))
            #fps_text = font.render(f"t={t:.2f}s  x={x_units:.2f}u  y={y_units:.2f}u  " f"Mouse=({mouse_x},{mouse_y})  FPS={clock.get_fps():.0f}", True, (200, 200, 200))
            #fps_text = font.render(f"t={t:.2f}s  x={x_units:.2f}u  y={y_units:.2f}u  FPS={clock.get_fps():.0f}", True, (200,200,200))
            screen.blit(fps_text, (10, 10))
        except Exception:
            pass
        hint = font.render("SPACE: pause  C: clear trail  ESC or close window: quit", True, (150,150,150))
        screen.blit(hint, (10, HEIGHT-24))

        pygame.display.flip()

        # capture frame for video if recording
        if video_writer is not None:
            frame_count += 1
            # convert pygame surface to numpy array for video writer
            try:
                import cv2
                import numpy as np
                frame = pygame.surfarray.pixels3d(screen)
                frame = np.transpose(frame, (1, 0, 2))  # reshape to (height, width, channels)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                video_writer.write(frame)
            except ImportError:
                # fallback: imageio
                try:
                    import numpy as np
                    frame_array = pygame.surfarray.array3d(screen)
                    frame_array = np.transpose(frame_array, (1, 0, 2))
                    video_writer.append_data(frame_array)
                except Exception as e:
                    pass  # silently skip frame capture on error

        if duration is not None and (time.time() - start_time) > duration:
            running = False

    # finalize video
    if video_writer is not None:
        try:
            video_writer.release()
            print(f"Video saved: {save_video} ({frame_count} frames)")
        except Exception as e:
            print(f"Error finalizing video: {e}")
    #log_file.close()

    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true", help="Run in console/headless mode (no GUI)")
    parser.add_argument("--duration", type=float, default=5.0, help="Duration in seconds (default 5)")
    parser.add_argument("--fps", type=int, default=30, help="FPS for headless sampling or GUI (default 30)")
    parser.add_argument("--pixels-per-unit", type=float, default=12.0, help="Pixels per unit for GUI mapping (both axes)")
    parser.add_argument("--speed", type=float, default=1.0, help="Forward speed in units/sec (default 1.0)")
    parser.add_argument("--wrap", action="store_true", help="Wrap horizontal position when it moves off-screen")
    parser.add_argument("--lookahead", type=float, default=2.0, help="Lookahead duration in seconds for preview (GUI)")
    parser.add_argument("--lookahead-steps", type=int, default=20, help="Number of points to show in lookahead preview (GUI)")
    parser.add_argument("--out", type=str, help="Optional CSV output path for headless mode")
    parser.add_argument("--save-video", type=str, help="Save GUI output as MP4 video file (requires opencv-python or imageio)")
    parser.add_argument("--num_runs", type=int, default=3, help="Number of times to run the GUI")
    args = parser.parse_args()

    pygame.init()
    WIDTH, HEIGHT = 1500, 1000
    pygame.display.set_caption("Participant Info")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    participant_id, name, age = get_participant_info(screen, WIDTH, HEIGHT)
# now start trials
    if args.headless:
        run_headless(duration=args.duration, fps=args.fps, out_csv=args.out, speed=args.speed)
        return
    
    import csv

    log_file = open("tracking_data.csv", "w", newline="")
    log_writer = csv.writer(log_file)
    log_writer.writerow(["clock", "participant_id", "age", "trial", "time", "target_x", "target_y", "cursor_x","cursor_y"])

    #pygame.init()
    pygame.display.flip()

    # attempt GUI mode, but be tolerant if pygame display can't initialize
    try:
        # store speed and wrap as module-local variables for run_gui
        global forward_speed, wrap
        forward_speed = args.speed
        wrap = args.wrap
        for i in range(args.num_runs):
            run_gui(screen, participant_id, name, age, fps=args.fps,pixels_per_unit=args.pixels_per_unit,duration=args.duration,lookahead=args.lookahead,lookahead_steps=args.lookahead_steps,save_video=args.save_video,log_writer=log_writer,trial_id=i,)
            #run_gui(fps=args.fps, pixels_per_unit=args.pixels_per_unit, duration=args.duration, lookahead=args.lookahead, lookahead_steps=args.lookahead_steps, save_video=args.save_video)
        pygame.quit()
        log_file.close()

    except Exception as e:
        print("GUI mode failed or unavailable, falling back to headless. Error:", e)
        run_headless(duration=args.duration, fps=args.fps, out_csv=args.out)


if __name__ == "__main__":
    main()


