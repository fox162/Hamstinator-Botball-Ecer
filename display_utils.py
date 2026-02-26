import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


import cv2
import numpy as np
from datetime import datetime, timedelta

class DisplayManager:
    def __init__(self):
        self.start_time = None
        self.is_running = False
        self.color_order = []

    def start_timer(self):
        self.start_time = datetime.now()
        self.is_running = True

    def draw_interface(self, frame, color_positions):
        # Make copy of frame to avoid modifying original
        display = frame.copy()

        # Draw timer
        if self.is_running:
            elapsed = datetime.now() - self.start_time
            remaining = 119 - elapsed.total_seconds()
            if remaining <= 0:
                return None  # Signal to stop program
            timer_text = f"Time: {int(remaining)}s"
        else:
            timer_text = "Timer: Not Started"

        cv2.putText(display, timer_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Draw instructions
        cv2.putText(display, "Press 'S' to Start", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(display, "Press 'Q' to Quit", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Draw color order
        if self.color_order:
            order_text = " | ".join(self.color_order)
            cv2.putText(display, f"Color Order: {order_text}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Draw color boxes
        for (center_x, center_y), color in color_positions:
            color_rgb = {"red": (0, 0, 255), "green": (0, 255, 0), "blue": (255, 0, 0)}[color]
            cv2.rectangle(display, (center_x-50, center_y-50), (center_x+50, center_y+50), color_rgb, 2)
            cv2.putText(display, color.upper(), (center_x-40, center_y), cv2.FONT_HERSHEY_SIMPLEX, 1, color_rgb, 2)

        return display