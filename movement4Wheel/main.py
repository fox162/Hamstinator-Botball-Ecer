import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from screen.src.main import Screen
from camera.src.main import Camera
from omi_wheels.src.main import Omi_Wheel
from goon.src.main import Goon
import time
import threading
import numpy as np

import os
import sys
from pathlib import Path

# Define all global variables at the top of the file
started = True
program_menu_active = False
consecutive_single_object_frames = 0
status_label = None
robot_step = 0
sequence_start_time = None
target_object = None
countdown_running = False
countdown_value = 119.0
robot_thread = None  # Make sure this is defined
timer_label = None  # Also add this for completeness
goon_instance = None  # Global goon instance
drink_color = None

# Define config directory in user's home folder or AppData on Windows
if sys.platform == "win32":
    CONFIG_DIR = os.path.join(os.getenv('LOCALAPPDATA'), 'RobotConfig')
else:
    # On Linux, use ~/.config/robot
    CONFIG_DIR = os.path.expanduser("~/.config/robot")

# Create directory with appropriate permissions
try:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if sys.platform != "win32":
        # Set user read/write permissions on Linux
        os.chmod(CONFIG_DIR, 0o755)
except Exception as e:
    print(f"Warning: Could not create/set permissions on config directory: {e}")
    # Fallback to temporary directory if needed
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), "robot_config_temp")
    os.makedirs(CONFIG_DIR, exist_ok=True)

# Set environment variable for the camera config location
camera_config = os.path.join(CONFIG_DIR, "camera_config.json")
os.environ['CAMERA_CONFIG_PATH'] = camera_config

# Define robot control states
IDLE = 'idle'
MOVING_FORWARD = 'moving_forward'
ROTATING_LEFT = 'rotating_left'
MOVING_FORWARD_RIGHT = 'moving_forward_right'
MOVING_TOWARD_OBJECT = 'moving_toward_object'
ROTATING_BACK = 'rotating_back'
MOVING_RIGHT = 'moving_right'
COMPLETED = 'completed'

SCREEN_CENTER_X = 200

def setup_config_ui(screen, camera):
    # Config Colors menu
    screen.addCamera('ConfigColors', camera, 20, 20, 260, 200, 'rgb')
    screen.addCamera('ConfigColors', camera, 340, 20, 260, 200, 'mask')

    # Color indicator in a better position
    screen.addText('ConfigColors', 'Current Color:', 620, 20, False, 16, 'center')
    color_label = screen.addText('ConfigColors', camera.active_color.upper(), 620, 40, False, 16, 'center')

    # Create sliders
    slider_width = 700
    slider_y_start = 240
    slider_spacing = 30
    
    # Create a list to store references to all sliders
    sliders = []
    
    # HSV Sliders (storing references)
    h_min_slider = screen.addSlider('ConfigColors', 20, slider_y_start, slider_width, 0, 180,
                    camera.color_ranges[camera.active_color]['lower'][0],
                    lambda val: camera.update_color_range(
                        camera.active_color,
                        int(val),
                        camera.color_ranges[camera.active_color]['upper'][0],
                        camera.color_ranges[camera.active_color]['lower'][1],
                        camera.color_ranges[camera.active_color]['upper'][1],
                        camera.color_ranges[camera.active_color]['lower'][2],
                        camera.color_ranges[camera.active_color]['upper'][2]
                    ))
    sliders.append(h_min_slider)

    h_max_slider = screen.addSlider('ConfigColors', 20, slider_y_start + slider_spacing, slider_width, 0, 180,
                    camera.color_ranges[camera.active_color]['upper'][0],
                    lambda val: camera.update_color_range(
                        camera.active_color,
                        camera.color_ranges[camera.active_color]['lower'][0],
                        int(val),
                        camera.color_ranges[camera.active_color]['lower'][1],
                        camera.color_ranges[camera.active_color]['upper'][1],
                        camera.color_ranges[camera.active_color]['lower'][2],
                        camera.color_ranges[camera.active_color]['upper'][2]
                    ))
    sliders.append(h_max_slider)

    s_min_slider = screen.addSlider('ConfigColors', 20, slider_y_start + 2 * slider_spacing, slider_width, 0, 255,
                    camera.color_ranges[camera.active_color]['lower'][1],
                    lambda val: camera.update_color_range(
                        camera.active_color,
                        camera.color_ranges[camera.active_color]['lower'][0],
                        camera.color_ranges[camera.active_color]['upper'][0],
                        int(val),
                        camera.color_ranges[camera.active_color]['upper'][1],
                        camera.color_ranges[camera.active_color]['lower'][2],
                        camera.color_ranges[camera.active_color]['upper'][2]
                    ))
    sliders.append(s_min_slider)

    s_max_slider = screen.addSlider('ConfigColors', 20, slider_y_start + 3 * slider_spacing, slider_width, 0, 255,
                    camera.color_ranges[camera.active_color]['upper'][1],
                    lambda val: camera.update_color_range(
                        camera.active_color,
                        camera.color_ranges[camera.active_color]['lower'][0],
                        camera.color_ranges[camera.active_color]['upper'][0],
                        camera.color_ranges[camera.active_color]['lower'][1],
                        int(val),
                        camera.color_ranges[camera.active_color]['lower'][2],
                        camera.color_ranges[camera.active_color]['upper'][2]
                    ))
    sliders.append(s_max_slider)

    v_min_slider = screen.addSlider('ConfigColors', 20, slider_y_start + 4 * slider_spacing, slider_width, 0, 255,
                    camera.color_ranges[camera.active_color]['lower'][2],
                    lambda val: camera.update_color_range(
                        camera.active_color,
                        camera.color_ranges[camera.active_color]['lower'][0],
                        camera.color_ranges[camera.active_color]['upper'][0],
                        camera.color_ranges[camera.active_color]['lower'][1],
                        camera.color_ranges[camera.active_color]['upper'][1],
                        int(val),
                        camera.color_ranges[camera.active_color]['upper'][2]
                    ))
    sliders.append(v_min_slider)

    v_max_slider = screen.addSlider('ConfigColors', 20, slider_y_start + 5 * slider_spacing, slider_width, 0, 255,
                    camera.color_ranges[camera.active_color]['upper'][2],
                    lambda val: camera.update_color_range(
                        camera.active_color,
                        camera.color_ranges[camera.active_color]['lower'][0],
                        camera.color_ranges[camera.active_color]['upper'][0],
                        camera.color_ranges[camera.active_color]['lower'][1],
                        camera.color_ranges[camera.active_color]['upper'][1],
                        camera.color_ranges[camera.active_color]['lower'][2],
                        int(val)
                    ))
    sliders.append(v_max_slider)
    
    # Function to update sliders when color changes
    def update_sliders_for_color(color):
        screen.setSliderValue(h_min_slider, camera.color_ranges[color]['lower'][0])
        screen.setSliderValue(h_max_slider, camera.color_ranges[color]['upper'][0])
        screen.setSliderValue(s_min_slider, camera.color_ranges[color]['lower'][1])
        screen.setSliderValue(s_max_slider, camera.color_ranges[color]['upper'][1])
        screen.setSliderValue(v_min_slider, camera.color_ranges[color]['lower'][2])
        screen.setSliderValue(v_max_slider, camera.color_ranges[color]['upper'][2])
    
    # Status message for save operation
    save_status = screen.addText('ConfigColors', "", 620, 230, False, 14, 'center')
    
    # Function to save config with status feedback
    def save_config():
        try:
            # Ensure config directory exists with correct permissions
            if not os.path.exists(CONFIG_DIR):
                os.makedirs(CONFIG_DIR, exist_ok=True)
                if sys.platform != "win32":
                    os.chmod(CONFIG_DIR, 0o777)
            
            # Get config file path
            config_file = os.path.join(CONFIG_DIR, "camera_config.json")
            
            # Try to save
            success = camera.save_config()
            if success:
                # Set file permissions
                if sys.platform != "win32":
                    try:
                        os.chmod(config_file, 0o666)
                    except Exception as e:
                        print(f"Warning: Could not set file permissions: {e}")
                
                print(f"Configuration saved successfully to {config_file}")
                screen.updateText(save_status, "Configuration saved!")
            else:
                print("Save operation failed")
                screen.updateText(save_status, "Save failed!")
                
        except Exception as e:
            print(f"Save error: {e}")
            screen.updateText(save_status, f"Save error: {str(e)}")
        
        # Clear message after 2 seconds
        def clear_message():
            screen.updateText(save_status, "")
        screen.addTimerCallback(2000, clear_message)
    
    # Color buttons with updated callbacks
    button_width = 100
    button_height = 30
    col1_x = 560  # Left column x position
    col2_x = 670  # Right column x position
    button_y = 70  # Starting y position
    button_spacing = 40  # Vertical spacing between buttons
    
    # Column 1 buttons
    screen.addButton('ConfigColors', col1_x, button_y, button_width, button_height, 'Blue',
                    lambda: [camera.set_active_color('blue'), screen.updateText(color_label, 'BLUE'), update_sliders_for_color('blue')])
    screen.addButton('ConfigColors', col1_x, button_y + button_spacing, button_width, button_height, 'Green',
                    lambda: [camera.set_active_color('green'), screen.updateText(color_label, 'GREEN'), update_sliders_for_color('green')])
    
    # Column 2 buttons 
    screen.addButton('ConfigColors', col2_x, button_y, button_width, button_height, 'Red',
                    lambda: [camera.set_active_color('red'), screen.updateText(color_label, 'RED'), update_sliders_for_color('red')])
    screen.addButton('ConfigColors', col2_x, button_y + button_spacing, button_width, button_height, 'Black',
                    lambda: [camera.set_active_color('black'), screen.updateText(color_label, 'BLACK'), update_sliders_for_color('black')])
    
    # Save and Back buttons (centered)
    center_x = 615
    screen.addButton('ConfigColors', center_x, button_y + 2*button_spacing, button_width, button_height, 'Save', save_config)
    screen.addButton('ConfigColors', center_x, button_y + 3*button_spacing, button_width, button_height, 'Back',
                    lambda: screen.openMenu('Main'))


def setup_program_ui(screen, camera):
    global program_menu_active, status_label, robot_step, sequence_start_time
    global target_object, countdown_running, countdown_value, robot_thread  # Add robot_thread here
    
    # Add a large camera view on the right (400x300)
    screen.addCamera('Program', camera, 350, 20, 400, 300, 'rgb')
    
    # Title for the log area
    screen.addText('Program', 'Object Tracking Log', 20, 20, False, 16, 'left', 'bold')
    
    # Add timer display at the top of the log
    timer_label = screen.addText('Program', 'Timer: Not started', 180, 20, False, 16, 'center', 'bold')
    
    # Back button with handler that sets program_menu_active to False
    screen.addButton('Program', 20, 380, 100, 30, 'Back', lambda: [screen.openMenu('Main'), set_program_inactive()])
    
    # Function to set program_menu_active to False
    def set_program_inactive():
        global program_menu_active, countdown_running, robot_thread, goon_instance
        program_menu_active = False
        countdown_running = False
        if robot_thread and robot_thread.is_alive():
            emergency_stop = Omi_Wheel()
            emergency_stop.Stop()
        robot_thread = None
    
    # Create text labels for object counts - keep this section compact
    screen.addText('Program', 'Object Counts:', 20, 50, False, 14, 'left', 'bold')
    red_count_label = screen.addText('Program', 'Red: 0', 30, 75)
    green_count_label = screen.addText('Program', 'Green: 0', 30, 100)
    blue_count_label = screen.addText('Program', 'Blue: 0', 30, 125)
    
    # Create area for object positions - moved down to avoid overlap
    screen.addText('Program', 'Object Positions:', 20, 180, False, 14, 'left', 'bold')
    
    # Add status message for the robot state
    status_label = screen.addText('Program', 'Status: Waiting for objects', 20, 350, False, 14, 'left', 'bold')
    
    # Initialize state variables for robot control
    countdown_running = False
    countdown_value = 119.0
    target_object = None
    sequence_start_time = None
    
    # Robot sequence worker function to run in a separate thread
    def robot_sequence_worker():
        global robot_step, sequence_start_time, target_object
        global countdown_running, countdown_value, started
        
        omi_wheel = Omi_Wheel()
        
        try:
            while countdown_running and countdown_value > 0 and screen.getOpenMenu() == 'Program':
                if not started:
                    # Check if we should start
                    if wait_for_start(camera, screen, status_label):
                        started = True
                    time.sleep(0.1)
                    continue
                
                run_seg(screen)

        except Exception as e:
            print(f"Error in robot sequence: {e}")
            screen.updateText(status_label, f"Status: Error occurred: {str(e)}")
        finally:
            omi_wheel.Stop()
            countdown_running = False

    # Create a thread for robot control
    robot_thread = None
    
    # Update function to refresh object data and handle countdown
    def update_object_data():
        global countdown_running, countdown_value, robot_step
        global target_object, program_menu_active, sequence_start_time, robot_thread, started
        
        try:
            # Get objects by color - only red and green
            red_objects = [obj for obj in camera.obj if obj.color == 'red']
            green_objects = [obj for obj in camera.obj if obj.color == 'green']
            
            # Update count labels
            screen.updateText(red_count_label, f"Red: {len(red_objects)}")
            screen.updateText(green_count_label, f"Green: {len(green_objects)}")
            
            # Update timer if running
            if countdown_running:
                if countdown_value > 0:
                    countdown_value -= 0.1
                    screen.updateText(timer_label, f"Timer: {int(countdown_value)}")
                    
                    if countdown_value <= 0:
                        countdown_running = False
                        started = False
                        emergency_stop = Omi_Wheel()
                        emergency_stop.Stop()
                        screen.updateText(status_label, "Status: Time's up! Motors stopped")
                        screen.updateText(timer_label, "Timer: FINISHED")
                        robot_thread = None
            
            # Only start new sequence if we're not already running one
            if program_menu_active and screen.getOpenMenu() == 'Program' and robot_step == 0:
                if not countdown_running:
                    print("Starting robot sequence...")
                    countdown_running = True
                    countdown_value = 119.0
                    started = False
                    target_object = None
                    sequence_start_time = time.time()
                    
                    screen.updateText(timer_label, f"Timer: {int(countdown_value)}")
                    screen.updateText(status_label, "Status: Waiting for start conditions")
                    
                    if robot_thread is None or not robot_thread.is_alive():
                        robot_thread = threading.Thread(target=robot_sequence_worker, daemon=True)
                        robot_thread.start()
                        print("Robot thread started")

        except Exception as e:
            print(f"Error in update_object_data: {e}")
            screen.updateText(status_label, f"Status: Error: {str(e)}")
    
    # Start the update cycle immediately
    update_object_data()
    
    # Add a timer callback for frequent updates (100ms)
    screen.addTimerCallback(100, update_object_data)

def wait_for_start(camera, screen, status_label):
    return True

def main():
    screen = Screen()
    screen.init(800, 430, "Simple Robot Interface")
    
    # Initialize camera - just use index 0 for default camera
    try:
        camera = Camera(0)  # Use default camera
        if camera.cap is None or not camera.cap.isOpened():
            print("ERROR: Could not open default camera")
            return
        print("Successfully initialized default camera")
    except Exception as e:
        print(f"ERROR: Failed to initialize camera: {e}")
        return

    screen.addMenu('Main')
    screen.addMenu('ConfigColors')
    screen.addMenu('Program')

    # Main menu
    screen.addText('Main', 'Simple Robot Interface', 400, 60, True, 50, 'center', 'bold')
    screen.addButton('Main', 450, 140, 300, 100, 'Color Configuration', lambda: screen.openMenu('ConfigColors'))
    screen.addButton('Main', 50, 140, 300, 100, 'Program', lambda: [screen.openMenu('Program'), set_program_active()])
    screen.addButton('Main', 50, 300, 300, 100, 'Exit', lambda: screen.cleanup())
    
    # Function to set program_menu_active to True
    def set_program_active():
        global program_menu_active, robot_step, sequence_start_time, target_object, started
        program_menu_active = True
        robot_step = 0
        sequence_start_time = None
        target_object = None
        started = True

    # Setup config colors menu
    setup_config_ui(screen, camera)
    
    # Setup program menu
    setup_program_ui(screen, camera)

    screen.openMenu('Main')
    screen.run()
    
def follow_black_line(camera, omi_wheel, screen, status_label):
    """
    Follow black line with stronger corrections at higher speed
    """
    try:
        # Set ROI to bottom portion of frame
        camera.set_roi(70, 100)
        camera.set_active_color('black')
        
        # Get black objects with strict filtering
        MIN_AREA = 800  # Increased minimum area
        MIN_WIDTH = 30  # Increased minimum width
        black_objects = [
            obj for obj in camera.obj 
            if obj.color == 'black' 
            and obj.area > MIN_AREA
            and (obj.bounding_rect[2] if obj.bounding_rect else 0) > MIN_WIDTH
        ]
        
        if not black_objects:
            screen.updateText(status_label, "Status: No valid line detected")
            return True  # Keep going straight instead of stopping
            
        # Sort objects by y-position (bottom to top)
        black_objects.sort(key=lambda obj: -obj.posy)
        
        # Take bottom-most objects within threshold
        MAX_Y_DIFF = 40  # Reduced y-difference threshold
        bottom_y = black_objects[0].posy
        line_segments = [
            obj for obj in black_objects 
            if bottom_y - obj.posy < MAX_Y_DIFF
        ]
        
        if not line_segments:
            screen.updateText(status_label, "Status: Keep going straight")
            # Keep going straight at full speed
            omi_wheel.motor(omi_wheel.FRONT_LEFT, 100)
            omi_wheel.motor(omi_wheel.FRONT_RIGHT, 100)
            omi_wheel.motor(omi_wheel.REAR_LEFT, 100)
            omi_wheel.motor(omi_wheel.REAR_RIGHT, 100)
            return True
            
        # Calculate weighted center point
        total_area = sum(obj.area for obj in line_segments)
        center = sum(obj.posx * obj.area for obj in line_segments) / total_area
        
        # Maintain moving average of center for smoothing
        if not hasattr(follow_black_line, 'center_history'):
            follow_black_line.center_history = []
        
        HISTORY_SIZE = 5  # Increased history size
        follow_black_line.center_history.append(center)
        if len(follow_black_line.center_history) > HISTORY_SIZE:
            follow_black_line.center_history.pop(0)
            
        smoothed_center = sum(follow_black_line.center_history) / len(follow_black_line.center_history)
        
        # PID Control with stronger parameters for higher speed
        TARGET_X = SCREEN_CENTER_X
        Kp = 0.4    # Increased proportional gain
        Kd = 0.15   # Increased derivative gain
        Ki = 0.002  # Slightly increased integral gain
        
        # Error calculations with smaller deadband
        error = TARGET_X - smoothed_center
        DEADBAND = 10  # Reduced deadband for more responsive corrections
        if abs(error) < DEADBAND:
            error = 0
        
        # Initialize last values if needed
        if not hasattr(follow_black_line, 'last_error'):
            follow_black_line.last_error = error
            follow_black_line.integral = 0
            
        # Update integral with strict limits
        MAX_INTEGRAL = 50  # Reduced integral limit
        follow_black_line.integral = max(-MAX_INTEGRAL, 
                                      min(MAX_INTEGRAL, 
                                          follow_black_line.integral + error))
        
        # Calculate derivative with smoothing
        derivative = error - follow_black_line.last_error
        follow_black_line.last_error = error
        
        # Calculate correction with higher limits
        MAX_CORRECTION = 50  # Increased maximum correction
        correction = int(Kp * error + Kd * derivative + Ki * follow_black_line.integral)
        correction = max(-MAX_CORRECTION, min(correction, MAX_CORRECTION))
        
        # Use higher base speed
        BASE_SPEED = 100  # Increased base speed
        
        # Calculate wheel speeds with more aggressive corrections
        if correction > 0:  # Need to turn right
            left_speed = BASE_SPEED
            right_speed = BASE_SPEED - abs(correction)
        else:  # Need to turn left
            left_speed = BASE_SPEED - abs(correction)
            right_speed = BASE_SPEED
        
        # Ensure minimum speed while allowing for stronger corrections
        MIN_SPEED = 30
        left_speed = max(MIN_SPEED, left_speed)
        right_speed = max(MIN_SPEED, right_speed)
        
        # Apply motor speeds
        omi_wheel.motor(omi_wheel.FRONT_LEFT, left_speed)
        omi_wheel.motor(omi_wheel.FRONT_RIGHT, right_speed)
        omi_wheel.motor(omi_wheel.REAR_LEFT, left_speed)
        omi_wheel.motor(omi_wheel.REAR_RIGHT, right_speed)
        
        # Detailed status update
        status = (f"Line following: center={int(smoothed_center)}, "
                 f"error={int(error)}, corr={correction}")
        screen.updateText(status_label, f"Status: {status}")
        
        return True
        
    except Exception as e:
        print(f"Error in line following: {e}")
        screen.updateText(status_label, f"Status: Line following error: {str(e)}")
        omi_wheel.Stop()
        return False

def run_seg(screen):
    global consecutive_single_object_frames
    global robot_step, sequence_start_time, target_object, status_label
    global countdown_running, countdown_value, program_menu_active, goon_instance
    global drink_color

    CAMERA_WIDTH = 400  # Width of camera view

    # Create single omi_wheel instance
    omi_wheel = Omi_Wheel()
    current_time = time.time()
    
    # Use global goon_instance
    if not goon_instance:
        goon_instance = Goon()
    goon = goon_instance

    try:
        # Get reference to the main camera from the screen's cameras
        camera_view = next(iter(screen.cameras.get('Program', {}).values()))
        if not camera_view or not camera_view.get('camera'):
            raise Exception("Camera not found in Program view")
            
        camera = camera_view['camera']
        visible_objects = [obj for obj in camera.obj if obj.color in ['red', 'green']]

        # State machine for robot control
        if robot_step == 0:
            robot_step = 13
            sequence_start_time = current_time
            omi_wheel.RechtsUp(100)
            screen.updateText(status_label, "Status: Right up")
            camera.set_roi(0, 100)

        # Continue moving forward until an object is in center (with some tolerance)
        elif robot_step == 1 and (current_time - sequence_start_time) >= 3.5:
            # Get all x positions of visible objects
            positions = [obj.posx for obj in visible_objects]  # posx is already an integer
            if any(abs(pos - SCREEN_CENTER_X) < 25 for pos in positions):
                for obj in visible_objects:
                    if abs(obj.posx - SCREEN_CENTER_X) < 25:
                        drink_color = obj.color
                        print(f"Found {drink_color} drink in center")
                        break
                omi_wheel.Stop()
                screen.updateText(status_label, "Status: Object detected in center")
                robot_step = 2
                goon.move( 0, 500)
                goon.move(1, 1300)
                sequence_start_time = current_time
        
        # vor until width is reached and correct object if object is not in center
        elif robot_step == 2:
            robot_step = 3
            Omi_Wheel().Vor(100)

            screen.updateText(status_label, "Status: Moving forward")
            
        elif robot_step == 3 and (current_time - sequence_start_time) >= 1.65: 
            robot_step = 4
            omi_wheel.Rechts()
            screen.updateText(status_label, "Status: Target width reached")
            sequence_start_time = current_time

        elif robot_step == 4 and (current_time - sequence_start_time) >= 0.3: 
            robot_step = 5
            omi_wheel.Back()
            goon.move(0, 0)
            screen.updateText(status_label, "Status: Target width reached")
            sequence_start_time = current_time

        elif robot_step == 5 and (current_time - sequence_start_time) >= 0.2:
            robot_step = 6
            omi_wheel.Stop()
            if countdown_running:  # Only run if not stopped
                goon.GoonStreak()
            screen.updateText(status_label, "Status: Target width reached")
            sequence_start_time = current_time

        elif robot_step == 6:
            robot_step = 7
            omi_wheel.Back()
            screen.updateText(status_label, "Status: linksBack")
            sequence_start_time = current_time

        elif robot_step == 7 and (current_time - sequence_start_time) >= 1:
            robot_step = 8
            omi_wheel.LinksUm()
            screen.updateText(status_label, "Status: linksum")
            sequence_start_time = current_time

        elif robot_step == 8 and (current_time - sequence_start_time) >= 0.2:
            robot_step = 9
            omi_wheel.Links()
            goon.move(0, 700)
            screen.updateText(status_label, "Status: Links")
            sequence_start_time = current_time

        # 1s then check for objects with different color
        elif robot_step == 9 and (current_time - sequence_start_time) >= 0.5:
            different_color_objects = []
            # Only look for objects that are different color than the first drink
            if drink_color == 'red':
                different_color_objects = [obj for obj in camera.obj if obj.color == 'green']
            elif drink_color == 'green':
                different_color_objects = [obj for obj in camera.obj if obj.color == 'red']
            
            # Debug print statements
            print(f"Looking for objects different from {drink_color}")
            print(f"Found {len(different_color_objects)} different color objects")
            for obj in different_color_objects:
                print(f"Object at position x: {obj.posx}")
            
            # Changed center check to use similar logic as first object detection
            if different_color_objects:
                # Find object closest to center
                closest_obj = min(different_color_objects, key=lambda obj: abs(obj.posx - SCREEN_CENTER_X))
                if abs(closest_obj.posx - SCREEN_CENTER_X) < 100:  # Increased detection range
                    # We found an object of different color near center - grab it
                    robot_step = 10
                    goon.move(1, 1400)
                    goon.move(0, 0)
                    omi_wheel.Vor()
                    screen.updateText(status_label, f"Status: Found {closest_obj.color} drink (different from {drink_color})")
                    sequence_start_time = current_time
                else:
                    # Keep turning to find object
                    omi_wheel.Links()
                    screen.updateText(status_label, f"Status: Searching for {closest_obj.color} drink")
            else:
                # Keep turning to search for objects
                omi_wheel.Links()
                screen.updateText(status_label, "Status: Searching for different color drink")

        elif robot_step == 10 and (current_time - sequence_start_time) >= 1.2:
            robot_step = 11
            omi_wheel.Stop()
            # bever greifen
            goon.move(1, 1800)
            screen.updateText(status_label, "Status: Stopped")
            sequence_start_time = current_time
        
        elif robot_step == 11 and (current_time - sequence_start_time) >= .7:
            robot_step = 12  # Fix: was using == instead of =
            omi_wheel.Back(100)
            screen.updateText(status_label, "Status: Back")
            sequence_start_time = current_time
        
        elif robot_step == 12 and (current_time - sequence_start_time) >= .7:
            robot_step = 13  # Increment to next step
            omi_wheel.Stop()  # Stop first
            screen.updateText(status_label, "Status: Stopped and checking for black line")
            sequence_start_time = current_time

        # Move the black line detection to step 13
        elif robot_step == 13:
            robot_step = 14
            omi_wheel.RechtsUm(100)
            sequence_start_time = current_time
            screen.updateText(status_label, "Status: Checking for black line")
            
        elif robot_step == 14 and (current_time - sequence_start_time) >= 1.6:
            robot_step = 15
            omi_wheel.Stop()
            time.sleep(0.1)  # Brief pause
            camera.set_active_color('black')  # Ensure we're looking for black
            sequence_start_time = current_time
            screen.updateText(status_label, "Status: Starting line following")

        elif robot_step == 15:
            # Get camera reference first
            camera_view = next(iter(screen.cameras.get('Program', {}).values()))
            camera = camera_view['camera']
            
            # First check for horizontal stop line in the upper-middle portion of the frame
            camera.set_active_color('black')
            # Use a slightly lower ROI for horizontal line detection
            camera.set_roi(30, 70)  # Check 30-70% of frame for horizontal lines
            
            # Force a frame read to update objects with this ROI
            if camera.cap and camera.cap.isOpened():
                ret, frame = camera.cap.read()
                if ret:
                    # Update camera's internal object detection
                    objects = camera.detect_objects(frame)
                    
                    # Check for horizontal line characteristics with better criteria
                    horizontal_stop_detected = False
                    for obj in objects:
                        # Debug print to help troubleshoot
                        if obj.color == 'black' and obj.bounding_rect and obj.area > 800:
                            w = obj.bounding_rect[2]
                            h = obj.bounding_rect[3]
                            width_height_ratio = w / h if h > 0 else 0
                            print(f"Black object: w={w}, h={h}, ratio={width_height_ratio}, area={obj.area}")
                            
                            # More robust criteria for horizontal line: width at least 3x height
                            if width_height_ratio > 3.0:
                                horizontal_stop_detected = True
                                print("HORIZONTAL LINE DETECTED!")
                                break
                    
                    if horizontal_stop_detected:
                        # Make sure we're actually stopping
                        print("STOPPING ROBOT - HORIZONTAL LINE DETECTED")
                        omi_wheel.Stop()
                        robot_step = 16
                        screen.updateText(status_label, "Status: Horizontal stop line detected - stopping")
                        sequence_start_time = current_time
                        return  # Exit early to prevent further processing
            
            # Reset ROI back to bottom portion for normal line following (as it was before)
            camera.set_roi(70, 100)  # Back to bottom 30% of frame for line following
            camera.set_active_color('black')
            
            # Try to follow line
            line_following = follow_black_line(camera, omi_wheel, screen, status_label)
            
            if not line_following:
                # If we lose the line, increment lost line counter
                if not hasattr(run_seg, 'lost_line_count'):
                    run_seg.lost_line_count = 0
                run_seg.lost_line_count += 1
                
                # If we've lost the line for too long, move to next step or retry
                if run_seg.lost_line_count > 50:  # About 0.5 seconds
                    omi_wheel.Stop()
                    robot_step = 0  # Reset to beginning or handle end of sequence
                    run_seg.lost_line_count = 0
            else:
                # Reset lost line counter when we see the line
                run_seg.lost_line_count = 0

        elif robot_step == 16:
            # Robot has stopped due to horizontal line detection
            omi_wheel.Stop()  # Ensure completely stopped
            screen.updateText(status_label, "Status: Line following complete - stopping before rotation")
            robot_step = 17  # Move to rotation step
            sequence_start_time = current_time
        
        elif robot_step == 17:
            # reset roi
            camera.set_roi(0, 100)
            omi_wheel.Links(100)
            screen.updateText(status_label, "Status: aligning right")
            sequence_start_time = current_time
            robot_step = 18
        
        elif robot_step == 18 and (current_time - sequence_start_time) >= 1.2:
            robot_step = 19
            omi_wheel.Stop()
            goon.move(0, 0)
            screen.updateText(status_label, "Status: Stop")
            sequence_start_time = current_time

        elif robot_step == 19 and (current_time - sequence_start_time) >= 0.5:
            robot_step = 20
            goon.move(1, 1000)
            screen.updateText(status_label, "Status: Stop")
            sequence_start_time = current_time
            


    except Exception as e:
        print(f"Error in run_seg: {e}")
        screen.updateText(status_label, f"Status: Error in run_seg: {str(e)}")
        omi_wheel.Stop()
        countdown_running = False

    time.sleep(0.01)

if __name__ == "__main__":
    main()