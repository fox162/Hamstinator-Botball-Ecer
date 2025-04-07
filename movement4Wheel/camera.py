import cv2
import numpy as np
from typing import List, Optional, Tuple
import math
import time
import sys
import os
import platform
import json


class ColorObject:
    def __init__(self, posx: int, posy: int, color: str, contour=None, area=0):
        self.posx = posx
        self.posy = posy
        self.color = color
        self.contour = contour  # Store the contour for drawing
        self.area = area        # Store area for tracking
        self.is_target = False  # Target flag
        self.id = None          # Object ID for tracking
        self.last_seen = 0      # Frame counter for tracking
        self.bounding_rect = None  # Store bounding rectangle


class Camera:
    def __init__(self, camera_idx: int = None):  
        self.camera_idx = camera_idx
        self.cap = None
        self.is_wombat = self._is_running_on_wombat()
        self.obj: List[ColorObject] = []  
        self.color_ranges = {  
            'green': {'lower': np.array([40, 50, 50], dtype=np.uint8), 'upper': np.array([80, 255, 255], dtype=np.uint8)},  
            'blue': {'lower': np.array([100, 50, 50], dtype=np.uint8), 'upper': np.array([140, 255, 255], dtype=np.uint8)},  
            'red': {'lower': np.array([160, 50, 50], dtype=np.uint8), 'upper': np.array([180, 255, 255], dtype=np.uint8)},
            'black': {'lower': np.array([0, 0, 0], dtype=np.uint8), 'upper': np.array([180, 255, 70], dtype=np.uint8)}
        }  
        self.active_color = 'green'  
        self.hsv_range = self.color_ranges[self.active_color]
        self.frame_count = 0
        self.next_object_id = 0
        self.target = None
        self.current_frame = None
        self.last_process_time = 0
        self.process_interval = 0.05
        self.roi = None  # Region of interest for detection
        
        # Load saved configuration if available
        self.config_file = self._get_config_file_path()
        self.load_config()
        
        # Initialize camera with retry mechanism
        self.demo_mode = False
        for retry in range(3):
            if self._initialize_camera():
                break
            time.sleep(0.5)
        
    def _is_running_on_wombat(self):
        """Detect if we're running on a Wombat device"""
        # Check for specific platform identifiers or files that would indicate Wombat
        if os.path.exists("/etc/wombat-release") or "wombat" in platform.platform().lower():
            return True
            
        # Alternative check based on platform
        if platform.system() == "Linux" and platform.machine() == "armv7l":
            # This is likely a Raspberry Pi or similar ARM device like Wombat
            return True
            
        return False
    
    def obj_width(self, obj: ColorObject) -> int:
        """Calculate width of the object based on its bounding rectangle"""
        if obj.bounding_rect is not None:
            x, y, w, h = obj.bounding_rect
            return w
        return 0

    def get_object_width(self, obj):
        """Get width of an object from its bounding rectangle"""
        if hasattr(obj, 'bounding_rect') and obj.bounding_rect is not None:
            x, y, w, h = obj.bounding_rect
            return w
        return 0

    def _initialize_camera(self):
        """Initialize camera with proper settings"""
        try:
            if self.cap is not None:
                self.cap.release()
                
            if self.camera_idx is None:
                # Try different camera indices
                for idx in [0, 1, 2]:
                    self.cap = cv2.VideoCapture(idx)
                    if self.cap.isOpened():
                        self.camera_idx = idx
                        break
            else:
                self.cap = cv2.VideoCapture(self.camera_idx)
            
            if not self.cap.isOpened():
                print(f"Failed to open camera {self.camera_idx}")
                return False
                
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Verify camera is working by reading a test frame
            for _ in range(3):
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    print(f"Successfully initialized camera {self.camera_idx}")
                    return True
                    
            print("Failed to read valid frame from camera")
            self.cap.release()
            self.cap = None
            return False
            
        except Exception as e:
            print(f"Error initializing camera: {e}")
            if self.cap:
                self.cap.release()
                self.cap = None
            return False

    def _get_demo_frame(self):
        """Generate a demo frame when no camera is available"""
        # Create a blank 640x480 image with text
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add some colored shapes to simulate objects
        # Red circle
        cv2.circle(frame, (160, 120), 30, (0, 0, 255), -1)
        # Green rectangle
        cv2.rectangle(frame, (320, 200), (380, 260), (0, 255, 0), -1)
        # Blue triangle
        pts = np.array([[500, 120], [460, 200], [540, 200]], np.int32)
        cv2.fillPoly(frame, [pts], (255, 0, 0))
        
        # Add message about demo mode
        cv2.putText(frame, "DEMO MODE - NO CAMERA", (180, 400), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Update object detection to match the demo shapes
        self.obj = [
            ColorObject(160, 120, 'red'),
            ColorObject(350, 230, 'green'),
            ColorObject(500, 170, 'blue')
        ]
        
        for i, obj in enumerate(self.obj):
            obj.id = i
            obj.area = 900
            obj.bounding_rect = (obj.posx-30, obj.posy-30, 60, 60)
        
        return frame
        
    def set_active_color(self, color: str):
        if color in self.color_ranges:
            self.active_color = color
            self.hsv_range = self.color_ranges[color]

    def update_color_range(self, color: str, hue_min: int, hue_max: int, sat_min: int, sat_max: int, val_min: int, val_max: int):
        if color in self.color_ranges:
            self.color_ranges[color]['lower'] = np.array([hue_min, sat_min, val_min], dtype=np.uint8)
            self.color_ranges[color]['upper'] = np.array([hue_max, sat_max, val_max], dtype=np.uint8)
            if color == self.active_color:
                self.hsv_range = self.color_ranges[color]

    def set_roi(self, y_start_percent, y_end_percent):
        """Set region of interest as percentage of frame height"""
        self.roi = (y_start_percent, y_end_percent)

    def detect_objects(self, frame):
        """Detect objects of all defined colors in the frame"""
        current_time = time.time()
        if current_time - self.last_process_time < self.process_interval:
            return self.obj
            
        self.last_process_time = current_time
        self.frame_count += 1
        found_objects = []
        
        original_height = frame.shape[0]
        
        # Use a smaller frame for processing to improve performance
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        small_height = small_frame.shape[0]
        
        # Apply ROI if set
        if self.roi:
            y_start = int(small_height * self.roi[0] / 100)
            y_end = int(small_height * self.roi[1] / 100)
            roi_height = y_end - y_start
            
            # Extract ROI from small frame
            small_frame = small_frame[y_start:y_end, :]
            
            if small_frame.size == 0:
                return self.obj
        
        hsv = cv2.cvtColor(small_frame, cv2.COLOR_BGR2HSV)
        
        # Process each color
        for color, range_data in self.color_ranges.items():
            mask = cv2.inRange(hsv, range_data['lower'], range_data['upper'])
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 50:
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                cx = x + w // 2
                cy = y + h // 2
                
                # Scale back to original frame coordinates
                cx *= 2
                if self.roi:
                    # Adjust y-coordinate based on ROI position
                    cy = (cy + y_start) * 2
                else:
                    cy *= 2
                
                # Create upscaled contour
                upscaled_contour = contour.copy()
                upscaled_contour[:, :, 0] *= 2
                upscaled_contour[:, :, 1] *= 2
                if self.roi:
                    # Adjust contour y-coordinates
                    upscaled_contour[:, :, 1] += y_start * 2
                
                x *= 2
                y *= 2
                if self.roi:
                    y += y_start * 2
                w *= 2
                h *= 2
                
                obj = ColorObject(cx, cy, color, upscaled_contour, area*4)
                obj.bounding_rect = (x, y, w, h)
                found_objects.append(obj)
                
        # Use very simple merging - faster and more aggressive
        merged_objects = self.merge_objects_by_overlap(found_objects)
        
        # Track objects between frames
        self.simple_track_objects(merged_objects)
        return merged_objects
    
    def merge_objects_by_overlap(self, objects):
        """Very aggressive merging based on bounding box overlap"""
        if not objects:
            return []
            
        # Group by color
        color_groups = {}
        for obj in objects:
            if obj.color not in color_groups:
                color_groups[obj.color] = []
            color_groups[obj.color].append(obj)
        
        merged_objects = []
        
        for color, group in color_groups.items():
            if len(group) <= 1:
                merged_objects.extend(group)
                continue
                
            # Sort by area (largest first)
            group.sort(key=lambda x: x.area, reverse=True)
            
            # Track which objects have been merged
            merged = set()
            
            for i, obj1 in enumerate(group):
                if i in merged:
                    continue
                    
                # Start a new merged group
                to_merge = [obj1]
                
                # Check all other objects for overlap or proximity
                for j, obj2 in enumerate(group):
                    if i == j or j in merged:
                        continue
                        
                    # Check if bounding boxes overlap or are very close
                    if self.boxes_overlap_or_close(obj1.bounding_rect, obj2.bounding_rect, 50):
                        to_merge.append(obj2)
                        merged.add(j)
                
                if len(to_merge) > 1:
                    # Create merged object
                    merged_obj = self.create_merged_object(to_merge, color)
                    merged_objects.append(merged_obj)
                else:
                    # Just add the original object
                    merged_objects.append(obj1)
        
        return merged_objects
    
    def boxes_overlap_or_close(self, box1, box2, distance_threshold):
        """Check if boxes overlap or are very close"""
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        # Calculate expanded boxes that include the distance threshold
        ex1, ey1 = x1 - distance_threshold, y1 - distance_threshold
        ew1, eh1 = w1 + 2*distance_threshold, h1 + 2*distance_threshold
        
        # Check if the expanded box of box1 overlaps with box2
        return not (ex1 + ew1 < x2 or x2 + w2 < ex1 or ey1 + eh1 < y2 or y2 + h2 < ey1)
    
    def create_merged_object(self, objects, color):
        """Create a merged object from a list of objects"""
        # Calculate bounding box that contains all objects
        min_x = min(obj.bounding_rect[0] for obj in objects)
        min_y = min(obj.bounding_rect[1] for obj in objects)
        max_x = max(obj.bounding_rect[0] + obj.bounding_rect[2] for obj in objects)
        max_y = max(obj.bounding_rect[1] + obj.bounding_rect[3] for obj in objects)
        
        # Calculate center point
        cx = (min_x + max_x) // 2
        cy = (min_y + max_y) // 2
        
        # Use contour of largest object
        largest_obj = max(objects, key=lambda x: x.area)
        
        # Create merged object
        merged_obj = ColorObject(
            posx=cx,
            posy=cy,
            color=color,
            contour=largest_obj.contour,
            area=sum(obj.area for obj in objects)
        )
        
        merged_obj.bounding_rect = (min_x, min_y, max_x - min_x, max_y - min_y)
        
        # If any object had an ID or was a target, preserve that information
        for obj in objects:
            if obj.id is not None:
                merged_obj.id = obj.id
                merged_obj.last_seen = obj.last_seen
            if obj.is_target:
                merged_obj.is_target = True
        
        return merged_obj
    
    def simple_track_objects(self, new_objects):
        """Much simpler tracking based on bounding box overlap"""
        # If first frame, assign IDs to all objects
        if not self.obj:
            for obj in new_objects:
                obj.id = self.next_object_id
                obj.last_seen = self.frame_count
                self.next_object_id += 1
            self.obj = new_objects
            return
            
        # Track which objects have been matched
        matched_new = set()
        matched_old = set()
        
        # For each old object, find a matching new object
        for i, old_obj in enumerate(self.obj):
            best_match = None
            best_overlap = 0
            
            for j, new_obj in enumerate(new_objects):
                if j in matched_new or new_obj.color != old_obj.color:
                    continue
                    
                # Check for bounding box overlap
                overlap = self.calculate_box_overlap(old_obj.bounding_rect, new_obj.bounding_rect)
                
                if overlap > best_overlap:
                    best_match = j
                    best_overlap = overlap
            
            # If found a match
            if best_match is not None and best_overlap > 0:
                matched_new.add(best_match)
                matched_old.add(i)
                
                # Transfer identity
                new_objects[best_match].id = old_obj.id
                new_objects[best_match].last_seen = self.frame_count
                new_objects[best_match].is_target = old_obj.is_target
                
                # Update target reference if needed
                if old_obj.is_target:
                    self.target = new_objects[best_match]
        
        # Assign new IDs to unmatched new objects
        for j, new_obj in enumerate(new_objects):
            if j not in matched_new:
                new_obj.id = self.next_object_id
                new_obj.last_seen = self.frame_count
                self.next_object_id += 1
        
        # Keep unmatched old objects that were seen recently
        for i, old_obj in enumerate(self.obj):
            if i not in matched_old:
                if self.frame_count - old_obj.last_seen < 5:
                    new_objects.append(old_obj)
                elif old_obj.is_target and self.frame_count - old_obj.last_seen < 10:
                    new_objects.append(old_obj)
                elif old_obj.is_target:
                    self.target = None
        
        # Update object list
        self.obj = new_objects
    
    def calculate_box_overlap(self, box1, box2):
        """Calculate how much box1 and box2 overlap"""
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        # Calculate intersection
        x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        intersection = x_overlap * y_overlap
        
        if intersection == 0:
            return 0
            
        # Calculate union
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        # Return intersection over union (IoU)
        return intersection / union

    def set_target(self, object_id):
        """Set an object as the target based on its ID"""
        for obj in self.obj:
            if obj.id == object_id:
                obj.is_target = True
                self.target = obj
            else:
                obj.is_target = False
    
    def clear_target(self):
        """Clear the current target"""
        for obj in self.obj:
            obj.is_target = False
        self.target = None

    def get_frame(self, mask_type=None):
        """Get frame from camera with improved error handling"""
        if self.cap is None or not self.cap.isOpened():
            # Try to reinitialize camera
            if not self._initialize_camera():
                print("Failed to initialize camera")
                return None, None
        
        # Try to get frame from camera
        try:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                print("Failed to read frame")
                return None, None
                
            # Process frame for object detection
            self.current_frame = frame.copy()
            self.detect_objects(frame)
            vis_frame = frame.copy()
            
            # Draw object visualizations
            if mask_type is None:
                for obj in self.obj:
                    if obj.contour is None:
                        continue
                        
                    color_map = {
                        'red': (0, 0, 255),
                        'green': (0, 255, 0),
                        'blue': (255, 0, 0)
                    }
                    
                    display_color = (0, 215, 255) if obj.is_target else color_map.get(obj.color, (255, 255, 255))
                    
                    if obj.bounding_rect:
                        x, y, w, h = obj.bounding_rect
                        cv2.rectangle(vis_frame, (x, y), (x + w, y + h), display_color, 2)
                    
                    cv2.circle(vis_frame, (obj.posx, obj.posy), 3, display_color, -1)
                    cv2.putText(vis_frame, f"ID:{obj.id}", (obj.posx + 10, obj.posy),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, display_color, 1)
                
                return vis_frame, None
            
            # Handle mask view
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, self.hsv_range['lower'], self.hsv_range['upper'])
            
            if mask_type == 'mask':
                result = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
                result[:, :, 3] = mask
                return frame, result
                
            result = np.zeros_like(frame)
            result[mask > 0] = frame[mask > 0]
            return frame, result
            
        except Exception as e:
            print(f"Error in get_frame: {e}")
            return None, None

    def release(self):  
        if self.cap is not None and self.cap.isOpened():  
            self.cap.release()
    
    def cleanup(self):
        """Ensure proper camera cleanup"""
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception as e:
                print(f"Error releasing camera: {e}")
            self.cap = None
        cv2.destroyAllWindows()

    def _get_config_file_path(self):
        """Get the appropriate configuration file path based on OS"""
        if sys.platform == "linux":
            # Use /var/lib for persistent data on Linux
            config_dir = "/var/lib/robot"
            if not os.path.exists(config_dir):
                try:
                    os.makedirs(config_dir, exist_ok=True)
                    # Make directory accessible to all users
                    os.chmod(config_dir, 0o777)
                except Exception as e:
                    print(f"Failed to create config directory: {e}")
                    # Fallback to user's home directory
                    config_dir = os.path.expanduser("~/.config/robot")
                    os.makedirs(config_dir, exist_ok=True)
        else:
            # On Windows, use AppData/Local
            config_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'Robot')
            os.makedirs(config_dir, exist_ok=True)
            
        config_file = os.path.join(config_dir, "camera_config.json")
        return config_file
    
    def save_config(self):
        """Save current color configurations to file"""
        try:
            # Get the config directory from environment variable
            config_file = os.environ.get('CAMERA_CONFIG_PATH')
            if not config_file:
                config_file = self._get_config_file_path()
                
            # Create directory if it doesn't exist
            config_dir = os.path.dirname(config_file)
            os.makedirs(config_dir, exist_ok=True)
            
            # Prepare configuration data
            config = {
                "color_ranges": {},
                "active_color": self.active_color
            }
            
            # Convert numpy arrays to lists for JSON serialization
            for color, range_data in self.color_ranges.items():
                config["color_ranges"][color] = {
                    "lower": range_data["lower"].tolist(),
                    "upper": range_data["upper"].tolist()
                }
            
            # Write configuration with pretty printing
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            
            print(f"Configuration saved to {config_file}")
            return True
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def load_config(self):
        """Load color configurations from file if it exists"""
        try:
            if not os.path.exists(self.config_file):
                print("No configuration file found. Using defaults.")
                return False
                
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                
            # Load color ranges
            if "color_ranges" in config:
                for color, range_data in config["color_ranges"].items():
                    if color in self.color_ranges:
                        self.color_ranges[color]["lower"] = np.array(range_data["lower"], dtype=np.uint8)
                        self.color_ranges[color]["upper"] = np.array(range_data["upper"], dtype=np.uint8)
            
            # Load active color
            if "active_color" in config and config["active_color"] in self.color_ranges:
                self.active_color = config["active_color"]
                self.hsv_range = self.color_ranges[self.active_color]
                
            print(f"Configuration loaded from {self.config_file}")
            return True
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False