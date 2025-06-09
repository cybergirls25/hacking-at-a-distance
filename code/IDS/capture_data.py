import os
import pyautogui
import time
import numpy as np
import csv
import threading
from pynput import mouse, keyboard
from datetime import datetime
import subprocess
import re
from collections import deque
from pynput.keyboard import Key

class MouseJackDataCollector:
    def __init__(self, filename="user_behavior.csv"):
        self.filename = filename
        self.running = False
        self.lock = threading.Lock()
        
        # Initialize tracking variables
        self.prev_pos = pyautogui.position()
        self.prev_time = time.time()
        self.clicks = 0
        self.keystrokes = 0
        self.key_timestamps = []
        self.mouse_positions = deque(maxlen=30)
        self.new_devices_detected = 0
        self.known_devices = set()
        self.active_modifiers = set()
        self.shortcuts_detected = set()
        
        # Enhanced modifier and control character mapping
        self.modifier_keys = {
            Key.ctrl: 'Ctrl',
            Key.ctrl_l: 'Ctrl',
            Key.ctrl_r: 'Ctrl',
            Key.alt: 'Alt',
            Key.alt_l: 'Alt',
            Key.alt_r: 'Alt',
            Key.shift: 'Shift',
            Key.shift_l: 'Shift',
            Key.shift_r: 'Shift',
            Key.cmd: 'Win',
            Key.cmd_l: 'Win',
            Key.cmd_r: 'Win'
        }

        self.control_char_map = {
            1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G',
            8: 'H', 9: 'I', 10: 'J', 11: 'K', 12: 'L', 13: 'M', 14: 'N',
            15: 'O', 16: 'P', 17: 'Q', 18: 'R', 19: 'S', 20: 'T',
            21: 'U', 22: 'V', 23: 'W', 24: 'X', 25: 'Y', 26: 'Z'
        }

        # Configure CSV writer with error handling
        try:
            file_exists = os.path.exists(self.filename)
            self.csv_file = open(self.filename, "a", newline="", encoding='utf-8')
            self.writer = csv.writer(self.csv_file)
            
            if not file_exists:
                self.writer.writerow([
                    "timestamp", 
                    "mouse_speed", 
                    "click_freq", 
                    "keystroke_speed",
                    "keystroke_interval_std",
                    "mouse_jerk",
                    "shortcuts_used",
                    "new_devices_detected"
                ])
        except PermissionError:
            print(f"ERROR: Permission denied for file '{self.filename}'")
            print("1. Close the file in other programs (Excel/Notepad)")
            print("2. Run this script as Administrator")
            print("3. Choose a different save location")
            exit(1)

    def _get_key_name(self, key):
        """Convert key object to human-readable name with control character support"""
        try:
            # Handle control characters (ASCII 0-31)
            if hasattr(key, 'char') and key.char and ord(key.char) < 32:
                return self.control_char_map.get(ord(key.char), 'UNKNOWN')
            
            # Handle regular characters
            if hasattr(key, 'char') and key.char:
                return key.char.upper()
            
            # Handle special keys
            if key in self.modifier_keys:
                return self.modifier_keys[key]
                
            return key.name.capitalize()
        except AttributeError:
            return str(key).replace("Key.", "").capitalize()

    def _calculate_mouse_jerk(self):
        if len(self.mouse_positions) < 3:
            return 0.0
        
        velocities = []
        for i in range(1, len(self.mouse_positions)):
            dx = self.mouse_positions[i][0] - self.mouse_positions[i-1][0]
            dy = self.mouse_positions[i][1] - self.mouse_positions[i-1][1]
            dt = self.mouse_positions[i][2] - self.mouse_positions[i-1][2]
            if dt > 0:
                velocities.append((dx/dt, dy/dt))
        
        accelerations = []
        for i in range(1, len(velocities)):
            dvx = velocities[i][0] - velocities[i-1][0]
            dvy = velocities[i][1] - velocities[i-1][1]
            dt = self.mouse_positions[i+1][2] - self.mouse_positions[i][2]
            if dt > 0:
                accelerations.append((dvx/dt, dvy/dt))
        
        return np.std(accelerations) if accelerations else 0.0

    def _on_click(self, x, y, button, pressed):
        if pressed:
            with self.lock:
                self.clicks += 1

    def _on_press(self, key):
        with self.lock:
            try:
                # Handle modifier keys
                if key in self.modifier_keys:
                    self.active_modifiers.add(self.modifier_keys[key])
                    return
                
                # Get cleaned key name
                key_name = self._get_key_name(key)
                if not key_name:
                    return

                # Detect and store shortcuts
                if self.active_modifiers:
                    shortcut_parts = sorted(self.active_modifiers) + [key_name]
                    self.shortcuts_detected.add('+'.join(shortcut_parts))

                # Track keystrokes
                self.keystrokes += 1
                self.key_timestamps.append(time.time())

            except Exception as e:
                print(f"Key handling error: {str(e)}")

    def _on_release(self, key):
        try:
            if key in self.modifier_keys:
                with self.lock:
                    mod = self.modifier_keys.get(key, None)
                    if mod and mod in self.active_modifiers:
                        self.active_modifiers.remove(mod)
        except Exception as e:
            pass

    def _check_hid_devices(self):
        """Monitor HID devices in background thread"""
        while self.running:
            try:
                output = subprocess.check_output("pnputil /enum-devices /class HIDClass", 
                                                shell=True, stderr=subprocess.STDOUT).decode()
                devices = re.findall(r"Instance ID:\s+(USB\\VID_\w+&PID_\w+)", output)
                
                new_devices = 0
                for device in devices:
                    if device not in self.known_devices:
                        new_devices += 1
                        self.known_devices.add(device)
                
                with self.lock:
                    self.new_devices_detected = new_devices
                
            except Exception as e:
                pass
            
            time.sleep(10)

    def _collect_data(self):
        self.mouse_listener = mouse.Listener(on_click=self._on_click)
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        try:
            while self.running:
                current_pos = pyautogui.position()
                current_time = time.time()
                
                self.mouse_positions.append((current_pos[0], current_pos[1], current_time))
                
                elapsed = current_time - self.prev_time
                
                if elapsed >= 1.0:
                    with self.lock:
                        # Calculate metrics
                        move_speed = np.sqrt((current_pos[0] - self.prev_pos[0])**2 + 
                                      (current_pos[1] - self.prev_pos[1])**2) / elapsed
                        click_freq = self.clicks / elapsed
                        keystroke_speed = self.keystrokes / elapsed
                        
                        # Calculate keystroke intervals
                        if len(self.key_timestamps) > 1:
                            key_intervals = np.diff(self.key_timestamps)
                        else:
                            key_intervals = np.array([0.0])
                            
                        keystroke_interval_std = np.std(key_intervals) if len(key_intervals) > 0 else 0.0
                        mouse_jerk = self._calculate_mouse_jerk()
                        shortcuts = '|'.join(sorted(self.shortcuts_detected))
                        
                        # Write to CSV
                        self.writer.writerow([
                            datetime.now().isoformat(),
                            round(move_speed, 2),
                            round(click_freq, 2),
                            round(keystroke_speed, 2),
                            round(keystroke_interval_std, 4),
                            round(mouse_jerk, 2),
                            shortcuts,
                            self.new_devices_detected
                        ])
                        self.csv_file.flush()
                        
                        # Reset counters
                        self.prev_pos = current_pos
                        self.prev_time = current_time
                        self.clicks = 0
                        self.keystrokes = 0
                        self.key_timestamps = []
                        self.shortcuts_detected = set()
                        self.new_devices_detected = 0
                
                time.sleep(0.1)
        finally:
            self.mouse_listener.stop()
            self.keyboard_listener.stop()
            self.csv_file.close()

    def start(self):
        self.running = True
        hid_thread = threading.Thread(target=self._check_hid_devices)
        hid_thread.daemon = True
        hid_thread.start()
        self._collect_data()

    def stop(self):
        self.running = False
        if not self.csv_file.closed:
            self.csv_file.close()

if __name__ == "__main__":
    try:
        collector = MouseJackDataCollector(filename=r"user_behavior.csv")
        print("Data collection started. Press Ctrl+C to stop...")
        collector.start()
    except KeyboardInterrupt:
        collector.stop()
        print("\nData collection stopped successfully.")
    except Exception as e:
        print(f"Critical error: {str(e)}")
        exit(1)