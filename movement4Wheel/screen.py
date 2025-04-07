import pygame
import cv2
import numpy as np
from typing import Dict, List, Tuple, Callable
import time
import uuid

class Screen:
    def __init__(self):
        pygame.init()
        self.screen = None
        self.menus: Dict[str, Dict] = {}  # Store surfaces and elements for each menu
        self.current_menu = None
        self.buttons: Dict[str, List[Dict]] = {}  # Store button info
        self.cameras: Dict[str, Dict] = {}
        self.text_labels: Dict[str, List[Dict]] = {}
        self.button_callbacks: Dict[str, Callable] = {}
        self._destroyed = False
        self.sliders = {}
        self.width = 0
        self.height = 0
        self.clock = pygame.time.Clock()
        self.running = True
        self.timer_callbacks = {}  # Store timer callbacks
        self.last_time = time.time()  # For tracking timer events

    def init(self, width: int, height: int, title: str = ""):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        if title:
            pygame.display.set_caption(title)
        return self

    def addMenu(self, name: str):
        self.menus[name] = {
            'surface': pygame.Surface((self.width, self.height)),
            'elements': []
        }
        if not self.current_menu:
            self.current_menu = name
        if name not in self.text_labels:
            self.text_labels[name] = []

    def addCamera(self, menu: str, camera, posx: int, posy: int, width: int, height: int, display_type='rgb'):
        if menu not in self.cameras:
            self.cameras[menu] = {}

        view_id = str(uuid.uuid4())
        camera_info = {
            'camera': camera,
            'pos': (posx, posy),
            'width': width,
            'height': height,
            'display_type': display_type,
            'surface': pygame.Surface((width, height))
        }

        self.cameras[menu][view_id] = camera_info
        return camera_info

    def _update_camera(self, menu: str, view_id: str):
        if menu == self.current_menu and not self._destroyed and pygame.get_init():
            try:
                camera_info = self.cameras[menu][view_id]
                result = camera_info['camera'].get_frame(
                    mask_type=camera_info['display_type'] if camera_info['display_type'] == 'mask' else None
                )

                if result is None:
                    return

                frame, mask_overlay = result
                if frame is None:
                    return

                # Determine which display to use based on settings
                display = None
                if camera_info['display_type'] == 'mask' and mask_overlay is not None:
                    display = mask_overlay
                else:
                    display = frame
                
                # Ensure display is not None and has valid content
                if display is None or not isinstance(display, np.ndarray) or display.size == 0:
                    return
                    
                # Try to resize the display
                try:
                    display = cv2.resize(display, (camera_info['width'], camera_info['height']))
                except Exception:
                    # If resize fails, create a blank image
                    display = np.zeros((camera_info['height'], camera_info['width'], 3), dtype=np.uint8)

                # Ensure display has proper dimensions for color conversion
                if len(display.shape) < 3 or display.shape[2] < 3:
                    # Convert to 3-channel if needed
                    display = cv2.cvtColor(display, cv2.COLOR_GRAY2BGR)
                    
                # Convert color space based on display type
                try:
                    if camera_info['display_type'] == 'mask' and len(display.shape) == 3 and display.shape[2] == 4:
                        display = cv2.cvtColor(display, cv2.COLOR_BGRA2RGBA)
                    else:
                        # Ensure we have proper RGB image (3 channels)
                        if len(display.shape) == 3 and display.shape[2] != 3:
                            display = cv2.cvtColor(display, cv2.COLOR_GRAY2RGB)
                        else:
                            display = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
                except Exception:
                    # If color conversion fails, create a blank RGB image
                    display = np.zeros((camera_info['height'], camera_info['width'], 3), dtype=np.uint8)

                # Create the surface safely - FIXED METHOD
                try:
                    # More reliable conversion method: create surface first, then blit the array
                    surface = pygame.Surface((camera_info['width'], camera_info['height']))
                    
                    # Convert numpy array to the right format and create a pygame surface
                    # Ensure array is uint8 and contiguous
                    display = np.ascontiguousarray(display, dtype=np.uint8)
                    
                    # Create a temporary surface from the array, ensuring proper dimensions
                    if display.shape[2] == 3:  # RGB
                        img_surface = pygame.image.frombuffer(
                            display.tobytes(), 
                            (camera_info['width'], camera_info['height']), 
                            'RGB'
                        )
                    elif display.shape[2] == 4:  # RGBA
                        img_surface = pygame.image.frombuffer(
                            display.tobytes(), 
                            (camera_info['width'], camera_info['height']), 
                            'RGBA'
                        )
                    else:
                        # Fallback for unexpected number of channels
                        raise ValueError(f"Unexpected number of channels: {display.shape[2]}")
                        
                    # Blit the image onto our surface
                    surface.blit(img_surface, (0, 0))
                    
                    # Store the new surface
                    camera_info['surface'] = surface
                    
                except Exception as e:
                    print(f"Error creating surface: {e}")
                    # If surface creation fails, create a blank surface
                    camera_info['surface'] = pygame.Surface((camera_info['width'], camera_info['height']))
            except Exception as e:
                print(f"Error in _update_camera: {e}")

    def addButton(self, menu: str, posx: int, posy: int, width: int, height: int, text: str, command=None):
        if command:
            self.button_callbacks[text] = command

        button_info = {
            'rect': pygame.Rect(posx, posy, width, height),
            'text': text,
            'pos': (posx, posy),
            'size': (width, height)
        }

        if text not in self.buttons:
            self.buttons[text] = []
        self.buttons[text].append(button_info)
        self.menus[menu]['elements'].append(('button', button_info))
        return button_info

    def addText(self, menu: str, text: str, x: int = 10, y: int = None, clear=False, fontSize=13, align="left", style="regular"):
        if clear and menu in self.text_labels:
            self.text_labels[menu].clear()

        if y is None:
            y = 10 + len(self.text_labels[menu]) * 25 if menu in self.text_labels else 10

        font_style = pygame.font.SysFont(None, fontSize)
        text_info = {
            'text': text,
            'pos': (x, y),
            'font': font_style,
            'align': align,  # Store alignment information
            'color': (255, 255, 255)
        }

        if menu not in self.text_labels:
            self.text_labels[menu] = []
        self.text_labels[menu].append(text_info)
        self.menus[menu]['elements'].append(('text', text_info))
        return text_info  # Return the text_info for reference

    def addSlider(self, menu: str, x: int, y: int, width: int, from_val: int, to_val: int, start_val: int, command=None):
        slider_info = {
            'rect': pygame.Rect(x, y, width, 10),
            'value': start_val,
            'range': (from_val, to_val),
            'callback': command,
            'dragging': False,
            'label_rect': pygame.Rect(x + width + 10, y - 5, 50, 20)  # Area for displaying value
        }

        if menu not in self.sliders:
            self.sliders[menu] = []
        self.sliders[menu].append(slider_info)
        self.menus[menu]['elements'].append(('slider', slider_info))
        return slider_info

    def setSliderValue(self, slider_info: Dict, new_value: int):
        """Set a slider to a specific value and trigger its callback"""
        if isinstance(slider_info, dict) and 'value' in slider_info and 'range' in slider_info:
            # Ensure value is within range
            new_value = max(slider_info['range'][0], min(slider_info['range'][1], new_value))
            slider_info['value'] = new_value
            
            # Trigger callback if it exists
            if slider_info['callback']:
                slider_info['callback'](new_value)
        
        return slider_info

    def openMenu(self, menu: str):
        if menu in self.menus:
            self.current_menu = menu

    def _draw_menu(self):
        if not self.current_menu:
            return
            
        # Check if pygame is still initialized and screen exists
        if self._destroyed or not pygame.get_init() or self.screen is None:
            return

        try:
            # Fill background
            self.screen.fill((20, 20, 25))  # Dark background

            # Draw all elements for current menu
            menu_data = self.menus[self.current_menu]

            # Draw cameras
            if self.current_menu in self.cameras:
                for camera_id, camera_info in self.cameras[self.current_menu].items():
                    # Fix: Use the correct camera_id instead of always taking the first one
                    self._update_camera(self.current_menu, camera_id)
                    if 'surface' in camera_info:
                        self.screen.blit(camera_info['surface'], camera_info['pos'])

            # Draw buttons
            for element_type, element_info in menu_data['elements']:
                if element_type == 'button':
                    pygame.draw.rect(self.screen, (100, 100, 100), element_info['rect'])
                    font = pygame.font.SysFont(None, 24)
                    text_surface = font.render(element_info['text'], True, (255, 255, 255))
                    text_rect = text_surface.get_rect(center=element_info['rect'].center)
                    self.screen.blit(text_surface, text_rect)

                elif element_type == 'text':
                    text_surface = element_info['font'].render(element_info['text'], True, element_info['color'])
                    pos = list(element_info['pos'])
                    
                    # Adjust position based on alignment
                    if element_info.get('align') == 'center':
                        pos[0] -= text_surface.get_width() // 2
                    elif element_info.get('align') == 'right':
                        pos[0] -= text_surface.get_width()
                    
                    self.screen.blit(text_surface, pos)

                elif element_type == 'slider':
                    # Draw slider background
                    pygame.draw.rect(self.screen, (100, 100, 100), element_info['rect'])
                    
                    # Draw slider handle
                    value_pos = element_info['rect'].x + (element_info['value'] - element_info['range'][0]) / (element_info['range'][1] - element_info['range'][0]) * element_info['rect'].width
                    pygame.draw.circle(self.screen, (200, 200, 200), (int(value_pos), element_info['rect'].centery), 8)
                    
                    # Draw slider value text
                    font = pygame.font.SysFont(None, 20)
                    value_text = str(int(element_info['value']))
                    text_surface = font.render(value_text, True, (255, 255, 255))
                    text_rect = element_info['label_rect']
                    self.screen.blit(text_surface, (text_rect.x, text_rect.y))

            pygame.display.flip()
        except pygame.error:
            # Handle case where display was quit
            self._destroyed = True
            self.running = False

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.cleanup()
                return False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                # Handle button clicks
                for element_type, element_info in self.menus[self.current_menu]['elements']:
                    if element_type == 'button':
                        if element_info['rect'].collidepoint(pos):
                            if element_info['text'] in self.button_callbacks:
                                self.button_callbacks[element_info['text']]()

                # Handle slider clicks
                if self.current_menu in self.sliders:
                    for slider in self.sliders[self.current_menu]:
                        if slider['rect'].collidepoint(pos):
                            slider['dragging'] = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.current_menu in self.sliders:
                    for slider in self.sliders[self.current_menu]:
                        slider['dragging'] = False

            elif event.type == pygame.MOUSEMOTION:
                if self.current_menu in self.sliders:
                    for slider in self.sliders[self.current_menu]:
                        if slider['dragging']:
                            pos = pygame.mouse.get_pos()
                            value = (pos[0] - slider['rect'].x) / slider['rect'].width
                            value = max(0, min(1, value))
                            slider['value'] = slider['range'][0] + value * (slider['range'][1] - slider['range'][0])
                            if slider['callback']:
                                slider['callback'](slider['value'])

        return True

    def run(self):
        while self.running and not self._destroyed:
            # Process events first - if it returns False, exit immediately
            if not self._handle_events():
                break
                
            # Double-check that we didn't get destroyed during event handling
            if self._destroyed or not pygame.get_init():
                break
                
            self._check_timers()  # Check timer callbacks
            
            # Final check before drawing
            if not self._destroyed and pygame.get_init():
                self._draw_menu()  # Added missing call to draw the menu
    
    def addTimerCallback(self, interval_ms: int, callback: Callable):
        """Add a timer callback that will be called at the specified interval"""
        timer_id = str(uuid.uuid4())
        self.timer_callbacks[timer_id] = {
            'interval': interval_ms / 1000.0,  # Convert to seconds
            'callback': callback,
            'last_call': time.time()
        }
        return timer_id
    
    def removeTimerCallback(self, timer_id: str):
        """Remove a timer callback"""
        if timer_id in self.timer_callbacks:
            del self.timer_callbacks[timer_id]
    
    def _check_timers(self):
        """Check and execute timer callbacks"""
        current_time = time.time()
        for timer_id, timer_info in list(self.timer_callbacks.items()):
            if current_time - timer_info['last_call'] >= timer_info['interval']:
                timer_info['callback']()
                timer_info['last_call'] = current_time

    def updateText(self, text_info: Dict, new_text: str):
        """Update the text of a text label"""
        if isinstance(text_info, dict) and 'text' in text_info:
            text_info['text'] = new_text
            return text_info
        return None

    def cleanup(self):
        """Clean up pygame resources and close the application"""
        self._destroyed = True
        self.running = False
        
        # Stop any active cameras
        for menu_name, cameras in self.cameras.items():
            for camera_id, camera_info in cameras.items():
                if hasattr(camera_info['camera'], 'release'):
                    try:
                        camera_info['camera'].release()
                    except Exception as e:
                        print(f"Error releasing camera: {e}")
        
        # Quit pygame if it's initialized
        if pygame.get_init():
            pygame.quit()
            
        # Extra cleanup to ensure proper exit
        import sys
        sys.exit(0)

    def getOpenMenu(self) -> str:
        """Get the currently open menu"""
        return self.current_menu if self.current_menu else ""