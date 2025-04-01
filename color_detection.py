import cv2
import numpy as np

class ColorDetector:
    def __init__(self):
        # Define color ranges in HSV
        self.lower_red = np.array([160, 120, 120])
        self.upper_red = np.array([200, 255, 255])

        self.lower_green = np.array([40, 100, 100])
        self.upper_green = np.array([90, 255, 255])

        self.lower_blue = np.array([90, 120, 120])
        self.upper_blue = np.array([120, 255, 255])

    def detect_colors(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create masks for each color
        mask_red = cv2.inRange(hsv, self.lower_red, self.upper_red)
        mask_green = cv2.inRange(hsv, self.lower_green, self.upper_green)
        mask_blue = cv2.inRange(hsv, self.lower_blue, self.upper_blue)

        # Find contours for each color
        contours_red = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        contours_green = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        contours_blue = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        return contours_red, contours_green, contours_blue

    def get_color_positions(self, frame):
        contours_red, contours_green, contours_blue = self.detect_colors(frame)
        positions = []

        for color, contours in [("red", contours_red), ("green", contours_green), ("blue", contours_blue)]:
            if contours:
                largest = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest) > 500:
                    x, y, w, h = cv2.boundingRect(largest)
                    center_x = x + w // 2
                    center_y = y + h // 2
                    positions.append(((center_x, center_y), color))

        return sorted(positions, key=lambda x: x[0])
    
    def get_largest_contour(self, frame, target_color):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if target_color == "red":
            mask = cv2.inRange(hsv, self.lower_red, self.upper_red)
        elif target_color == "green":
            mask = cv2.inRange(hsv, self.lower_green, self.upper_green)
        elif target_color == "blue":
            mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        else:
            return None

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            return max(contours, key=cv2.contourArea)
        return None