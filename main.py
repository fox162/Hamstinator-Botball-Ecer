import sys, os
import cv2
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from camera_utils.src.main import init_camera, release_camera
from color_detection.src.main import ColorDetector
from display_utils.src.main import DisplayManager
from omi_wheel.src.main import GoRightUp, Vor, LinksUm, RechtsUm, stop_motors, GoRight

def calculate_target_direction(frame_width, target_x, target_area, frame_area):
    center_zone = frame_width // 3
    left_edge = center_zone
    right_edge = center_zone * 2

    if target_area > frame_area * 0.8:
        return "stop"
    if target_x < left_edge:
        return "left"
    elif target_x > right_edge:
        return "right"
    else:
        return "center"

def draw_frame(frame, color_positions, target=None, initial_colors=None):
    display = frame.copy()

    # Draw initial color order if available
    if initial_colors:
        order_text = " | ".join(initial_colors)
        cv2.putText(display, f"Color Order: {order_text}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # If we have a target, only draw that one
    if target:
        (target_x, target_y), target_color = target
        color_rgb = {"red": (0, 0, 255), "green": (0, 255, 0), "blue": (255, 0, 0)}[target_color]
        cv2.rectangle(display, (target_x-50, target_y-50), (target_x+50, target_y+50), color_rgb, 2)
        cv2.putText(display, "TARGET", (target_x-40, target_y-60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color_rgb, 2)
    else:
        # Draw all detected colors during initial phase
        for (center_x, center_y), color in color_positions:
            color_rgb = {"red": (0, 0, 255), "green": (0, 255, 0), "blue": (255, 0, 0)}[color]
            cv2.rectangle(display, (center_x-50, center_y-50), (center_x+50, center_y+50), color_rgb, 2)
            cv2.putText(display, color.upper(), (center_x-40, center_y-60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color_rgb, 2)

    return display

def main():
    cap = init_camera()
    detector = ColorDetector()
    display = DisplayManager()

    cv2.namedWindow('Robot Vision', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Robot Vision', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    initial_colors = []
    target_acquired = False
    current_target = None
    last_seen_color = None
    sequence_started = False
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_area = frame_width * frame_height

    print("Waiting for initial color order...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        color_positions = detector.get_color_positions(frame)

        # Initial phase: Get color order
        if len(initial_colors) < 3 and color_positions:
            current_colors = [color for _, color in sorted(color_positions, key=lambda x: x[0][0])]
            if len(current_colors) == 3:
                if not initial_colors:
                    initial_colors = current_colors
                    print(f"\nInitial color order detected: {' | '.join(initial_colors)}")
                    print(f"Looking for sequence: {initial_colors[-1]} | RED/GREEN\n")

        # Draw frame with appropriate information
        display_frame = draw_frame(frame, color_positions,
                                 target=current_target if target_acquired else None,
                                 initial_colors=initial_colors)

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s') and not display.is_running:
            display.start_timer()
            print("Timer started! Moving right-up...")

        # Main movement logic
        if display.is_running:
            if not target_acquired:
                GoRight()  # Continue moving right-up

                # Look for sequence
                if color_positions:
                    # First, look for the last initial color
                    if not sequence_started:
                        for (center_x, center_y), color in color_positions:
                            if color == initial_colors[-1]:
                                sequence_started = True
                                last_seen_color = color
                                print(f"Found {color}, looking for RED/GREEN to the right...")
                                break

                    # If we found the last initial color, look for red/green to the right
                    elif sequence_started:
                        for (center_x, center_y), color in color_positions:
                            if color in ["red", "green"] and color != last_seen_color:
                                # Ensure the new object is to the right of the last object
                                last_object_x = [pos[0] for pos, col in color_positions if col == last_seen_color]
                                if last_object_x and center_x > max(last_object_x):
                                    current_target = ((center_x, center_y), color)
                                    target_acquired = True
                                    print(f"\nTarget sequence found!")
                                    print(f"Moving towards {color.upper()} target\n")
                                    stop_motors()
                                    break

            else:  # Target tracking phase
                target_found = False
                largest_target_area = 0
                target_position = None
                target_color = current_target[1]

                # Find current target in frame
                for (center_x, center_y), color in color_positions:
                    if color == target_color:
                        contour = detector.get_largest_contour(frame, color)
                        if contour is not None:
                            area = cv2.contourArea(contour)
                            if area > largest_target_area:
                                largest_target_area = area
                                target_position = (center_x, center_y)
                                current_target = ((center_x, center_y), color)
                                target_found = True

                if target_found:
                    direction = calculate_target_direction(
                        frame_width,
                        target_position[0],
                        largest_target_area,
                        frame_area
                    )

                    if direction == "stop":
                        print("Target reached!")
                        stop_motors()
                        break
                    elif direction == "left":
                        LinksUm()
                    elif direction == "right":
                        RechtsUm()
                    else:  # center
                        Vor()
                else:
                    print("Lost target - stopping")
                    stop_motors()

        cv2.imshow('Robot Vision', display_frame)

    stop_motors()
    release_camera(cap)

if __name__ == "__main__":
    main()