from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
<<<<<<< HEAD
from my_utils import config_manager
from language_support import language_manager

# Import screens
from src.screens.login_screen import LoginScreen
from src.screens.main_screen import MainScreen
from src.screens.settings_screen import SettingsScreen
from src.screens.object_identification_screen import ObjectIdentificationScreen

class VoiceBotGUI(App):
    def build(self):
        try:
            # Set window size and title
            Window.size = (400, 600)
            self.title = 'VoiceBot Assistant'
            
            # Create screen manager with transition
            self.sm = ScreenManager(transition=SlideTransition())
            from my_utils import config_manager
            from language_support import language_manager
        
            saved_lang = config_manager.get('app.language', 'en')
            language_manager.set_language(saved_lang)
            # Create and add all screens
            screens = [
                LoginScreen(name='login'),
                MainScreen(name='main'),
                SettingsScreen(name='settings'),
                ObjectIdentificationScreen(name='object_identification')
            ]
            
            # Add screens to manager
            for screen in screens:
                print(f"Adding screen: {screen.name}")
                self.sm.add_widget(screen)
            
            # Set initial screen
            self.sm.current = 'login'
            
            return self.sm
            
        except Exception as e:
            print(f"Error in build: {e}")
            raise

=======
from kivy.uix.popup import Popup
from kivy.animation import Animation
from Speech_Reco import listen_for_command
from my_utils import verify_credentials, speak, tts
from enum import Enum
import time
import serial
import serial.tools.list_ports
from threading import Thread
import cv2
from kivy.core.image import Texture
import os
import requests
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget

try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"Bluetooth not available: {e}")
    BLUETOOTH_AVAILABLE = False
    bluetooth = None

COLORS = {
    'primary': (0.2, 0.6, 0.9, 1),
    'secondary': (0.95, 0.95, 0.95, 1),
    'accent': (0.2, 0.7, 0.3, 1),
    'warning': (0.9, 0.3, 0.1, 1),
    'background': (1, 1, 1, 1),
    'text': (0.1, 0.1, 0.1, 1),
    'text_light': (1, 1, 1, 1)
}

class BotState(Enum):
    IDLE = 'idle'
    LISTENING = 'listening'
    PROCESSING = 'processing'
    ERROR = 'error'

class BluetoothManager:
    def __init__(self):
        self.socket = None
        self.target_device = None

    def discover_devices(self):
        devices = bluetooth.discover_devices(lookup_names=True)
        return [{"name": name, "address": addr} for addr, name in devices]

    def connect(self, device_address):
        try:
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((device_address, 1))  # HC-05 uses channel 1
            return True
        except Exception as e:
            print(f"Bluetooth connection error: {e}")
            return False

    def send_command(self, command):
        if self.socket:
            try:
                self.socket.send(command.encode())
                return True
            except Exception as e:
                print(f"Failed to send command: {e}")
                return False
        return False

    def close(self):
        if self.socket:
            self.socket.close()

class ArduinoRadarManager:
    def __init__(self, app):
        self.app = app
        self.serial_connection = None
        self.running = False
        self.detection_threshold = 20  # Same as Arduino threshold (cm)
        self.current_distance = 0
        self.current_angle = 0
        self.object_detected = False
        self.connect_to_arduino()

    def connect_to_arduino(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                self.serial_connection = serial.Serial(port.device, 9600, timeout=1)
                time.sleep(2)  # Wait for connection
                print(f"Connected to Arduino on {port.device}")
                self.start_monitoring()
                return
            except (serial.SerialException, OSError):
                continue
        print("Could not find Arduino. Please check connection.")

    def start_monitoring(self):
        if self.serial_connection and not self.running:
            self.running = True
            self.monitor_thread = Thread(target=self.monitor_radar, daemon=True)
            self.monitor_thread.start()

    def monitor_radar(self):
        while self.running and self.serial_connection:
            try:
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    print(f"Received from Arduino: {line}")  # Debug print
                    
                    if "Angle:" in line and "Distance:" in line:
                        parts = line.split('|')
                        angle_part = parts[0].split(':')[1].split('°')[0].strip()
                        distance_part = parts[1].split(':')[1].split('cm')[0].strip()
                        
                        try:
                            self.current_angle = int(angle_part)
                            self.current_distance = int(distance_part)
                            print(f"Parsed data - Angle: {self.current_angle}, Distance: {self.current_distance}")
                            
                            if self.current_distance <= self.detection_threshold and not self.object_detected:
                                self.object_detected = True
                                print("Object detected - triggering identification")
                                self.trigger_object_detection()
                            elif self.current_distance > self.detection_threshold:
                                self.object_detected = False
                                
                        except ValueError:
                            print(f"Error parsing data: {line}")
                    
                    elif ">> Object detected at" in line or "Object detected at" in line:
                        self.object_detected = True
                        print("Object detected message received - triggering identification")
                        self.trigger_object_detection()
                        
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                self.running = False
                break
            except UnicodeDecodeError:
                print("Unicode decode error - skipping line")
                continue

    def trigger_object_detection(self):
        """Called when radar detects an object"""
        if self.app and hasattr(self.app, 'root'):
            current_screen = self.app.root.current
            print(f"Current screen: {current_screen}")
            
            if current_screen == 'object_identification':
                print("Already on object identification screen")
                return
                
            try:
                obj_screen = self.app.root.get_screen('object_identification')
                if obj_screen:
                    print("Starting object detection from radar")
                    Clock.schedule_once(lambda dt: obj_screen.start_detection_from_radar())
                    speak("Object detected nearby")
            except Exception as e:
                print(f"Error getting object screen: {e}")

    def send_command(self, command):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(command.encode())
                print(f"Sent command to Arduino: {command}")
            except serial.SerialException as e:
                print(f"Failed to send command to Arduino: {e}")
                return False
            return True
        return False

    def close(self):
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()

class VoiceInputButton(Button):
    def __init__(self, target_input, hint_text, **kwargs):
        super().__init__(**kwargs)
        self.target_input = target_input
        self.hint_text = hint_text
        self.background_normal = ''
        self.background_color = COLORS['accent']
        self.size_hint = (None, None)
        self.size = (40, 40)
        self.text = '🎤'
        self.font_size = '20sp'

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.logo = Image(
            source='voicebot_logo.png',
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        
        form_layout = GridLayout(cols=3, spacing=10, size_hint_y=None, height=100)
        
        username_label = Label(text='Username:', color=COLORS['primary'])
        self.username_input = TextInput(multiline=False)
        self.username_voice_button = VoiceInputButton(
            self.username_input,
            "Say your Username"
        )
        self.username_voice_button.bind(on_press=self.get_voice_username)
        
        password_label = Label(text='Password:', color=COLORS['primary'])
        self.password_input = TextInput(multiline=False, password=True)
        self.password_voice_button = VoiceInputButton(
            self.password_input,
            "say your password"
        )
        self.password_voice_button.bind(on_press=self.get_voice_password)
        
        form_layout.add_widget(username_label)
        form_layout.add_widget(self.username_input)
        form_layout.add_widget(self.username_voice_button)
        form_layout.add_widget(password_label)
        form_layout.add_widget(self.password_input)
        form_layout.add_widget(self.password_voice_button)
        
        language_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=10,
            padding=[0, 10, 0, 10]
        )
        
        self.language_spinner = StyledSpinner(
            text='English',
            values=('English', 'Français', 'Español', 'العربية'),
            size_hint=(None, None),
            size=(150, 40),
            pos_hint={'center_x': 0.5}
        )
        self.language_spinner.bind(text=self.on_language_select)
        
        language_layout.add_widget(Widget())
        language_layout.add_widget(self.language_spinner)
        language_layout.add_widget(Widget())
        
        self.error_label = Label(text="", color=COLORS['warning'])
        
        self.login_button = CustomButton(
            text="Se connecter",
            background_color=COLORS['accent'],
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5}
        )
        self.login_button.bind(on_press=self.verify_credentials)
        
        layout.add_widget(self.logo)
        layout.add_widget(form_layout)
        layout.add_widget(self.error_label)
        layout.add_widget(language_layout)
        layout.add_widget(self.login_button)
        
        self.add_widget(layout)

    def get_voice_username(self, instance):
        speak("Say your username")
        Clock.schedule_once(lambda dt: self.process_voice_input(self.username_input), 0.5)

    def get_voice_password(self, instance):
        speak("Say your password")
        Clock.schedule_once(lambda dt: self.process_voice_input(self.password_input), 0.5)

    def process_voice_input(self, target_input):
        try:
            text = listen_for_command()
            if text and text != "Commande non comprise" and text != "Erreur de reconnaissance":
                target_input.text = text.lower().strip()
                if target_input == self.password_input:
                    speak("Password saved")
                else:
                    speak(f"I recorded: {text}")
            else:
                speak("I didn't understand, please try again.")
        except Exception as e:
            speak("An error has occurred")
            self.error_label.text = str(e)

    def show_welcome_popup(self, username):
        message = f'Welcome, {username}!'
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        popup = Popup(
            title='Connection Successful',
            content=content,
            size_hint=(None, None),
            size=(300, 200),
            auto_dismiss=True
        )
        Clock.schedule_once(lambda dt: popup.dismiss(), 3)
        popup.open()
        Clock.schedule_once(lambda dt: speak(message), 0.5)

    def verify_credentials(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        if verify_credentials(username, password):
            self.username_input.text = ""
            self.password_input.text = ""
            self.error_label.text = ""
            self.show_welcome_popup(username)
            Clock.schedule_once(lambda dt: self.switch_to_main(), 3)
        else:
            self.error_label.text = "Invalid login!"
            speak("Invalid login!")

    def switch_to_main(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'main'

    def on_language_select(self, spinner, text):
        from language_support import language_manager
        from my_utils import config_manager, speak
        
        lang_map = {
            'Français': 'fr',
            'English': 'en',
            'Español': 'es',
            'العربية': 'ar'
        }
        
        lang_code = lang_map.get(text, 'fr')
        language_manager.set_language(lang_code)
        
        if 'app' not in config_manager._config:
            config_manager._config['app'] = {}
        config_manager._config['app']['language'] = lang_code
        config_manager.load_config()
        
        welcome_messages = {
            'fr': 'Bienvenue',
            'en': 'Welcome',
            'es': 'Bienvenido',
            'ar': 'مرحبا'
        }
        
        self.login_button.text = {
            'fr': 'Se connecter',
            'en': 'Login',
            'es': 'Iniciar sesión',
            'ar': 'تسجيل الدخول'
        }.get(lang_code, 'Login')
        
        speak(welcome_messages.get(lang_code, welcome_messages['en']))

class CustomButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.original_background = kwargs.get('background_color', COLORS['primary'])
        self.background_color = self.original_background
        
        with self.canvas.before:
            self.bg_color = Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[10,]
            )
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(state=self._on_state)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        self.bg_color.rgba = self.background_color

    def _on_state(self, instance, value):
        if value == 'down':
            self.background_color = [
                c * 0.8 for c in self.original_background[:3]
            ] + [self.original_background[3]]
        else:
            self.background_color = self.original_background
        self.bg_color.rgba = self.background_color

    def on_background_color(self, instance, value):
        if hasattr(self, 'bg_color'):
            self.bg_color.rgba = value

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = Label(
            text="Setting",
            font_size='24sp',
            size_hint_y=None,
            height=50
        )
        
        volume_layout = BoxLayout(size_hint_y=None, height=50)
        volume_label = Label(text="Volume:")
        self.volume_slider = Slider(min=0, max=1, value=0.8)
        self.volume_slider.bind(value=self.on_volume_change)
        volume_layout.add_widget(volume_label)
        volume_layout.add_widget(self.volume_slider)
        
        rate_layout = BoxLayout(size_hint_y=None, height=50)
        rate_label = Label(text="Vitesse:")
        self.rate_slider = Slider(min=100, max=200, value=150)
        self.rate_slider.bind(value=self.on_rate_change)
        rate_layout.add_widget(rate_label)
        rate_layout.add_widget(self.rate_slider)
        
        feedback_layout = BoxLayout(size_hint_y=None, height=50)
        feedback_label = Label(text="Retour vocal:")
        self.feedback_switch = Switch(active=True)
        self.feedback_switch.bind(active=self.on_feedback_change)
        feedback_layout.add_widget(feedback_label)
        feedback_layout.add_widget(self.feedback_switch)
        
        back_button = CustomButton(
            text="Back",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            color=(1, 1, 1, 1),
            background_color=(0.2, 0.2, 0.2, 1)
        )
        back_button.bind(on_press=self.go_back)
        
        layout.add_widget(title)
        layout.add_widget(volume_layout)
        layout.add_widget(rate_layout)
        layout.add_widget(feedback_layout)
        layout.add_widget(back_button)
        
        self.add_widget(layout)

    def on_volume_change(self, instance, value):
        tts.engine.setProperty('volume', value)

    def on_rate_change(self, instance, value):
        tts.engine.setProperty('rate', value)

    def on_feedback_change(self, instance, value):
        from my_utils import config_manager
        config_manager._config['app']['voice_feedback'] = value

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'

class ObjectIdentificationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_detecting = False
        self.cap = None
        self.model = None
        self.event = None
        self.build_ui()
        # Removed auto-start on enter
        # self.bind(on_enter=self.auto_start_detection)

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        title = Label(
            text="Object Identification",
            font_size='24sp',
            size_hint_y=None,
            height=50
        )

        self.camera_view = Image(
            size_hint=(1, 0.7),
            allow_stretch=True,
            keep_ratio=True
        )

        self.result_label = Label(
            text="Waiting for radar detection...",
            font_size='16sp',
            size_hint_y=None,
            height=100
        )

        self.identify_button = CustomButton(
            text="Identify",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            color=(1, 1, 1, 1),
            background_color=COLORS['accent']
        )
        self.identify_button.bind(on_press=self.toggle_detection)

        back_button = CustomButton(
            text="Back",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            color=(1, 1, 1, 1),
            background_color=(0.2, 0.2, 0.2, 1)
        )
        back_button.bind(on_press=self.go_back)

        layout.add_widget(title)
        layout.add_widget(self.camera_view)
        layout.add_widget(self.result_label)
        layout.add_widget(self.identify_button)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def start_detection_from_radar(self):
        """Called when radar detects an object"""
        if not self.is_detecting:
            self.is_detecting = True
            self.identify_button.text = "Stop"
            self.identify_button.background_color = COLORS['warning']
            self.start_detection()
            speak("Starting object identification")

    def toggle_detection(self, instance):
        """Manual toggle (if user presses the button)"""
        if not self.is_detecting:
            self.start_detection_from_radar()
        else:
            self.stop_detection()
            speak("Stopping object identification")

    def start_detection(self):
        try:
            if self.cap is None:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    raise Exception("Could not open camera")

            ret, frame = self.cap.read()
            if not ret or frame is None:
                raise Exception("Could not read from camera")

            self.event = Clock.schedule_interval(self.update_camera, 1.0/30.0)
            self.update_status_label("Camera initialized. Loading model...")

            import threading
            self.model_thread = threading.Thread(target=self.load_model, daemon=True)
            self.model_thread.start()

        except Exception as e:
            self.update_error_label(f"Camera Error: {str(e)}")
            self.stop_detection()

    def stop_detection(self):
        try:
            if self.event:
                self.event.cancel()
                self.event = None

            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
                self.cap = None

            self.model = None
            self.is_detecting = False
            self.identify_button.text = "Identify"
            self.identify_button.background_color = COLORS['accent']
            self.camera_view.texture = None
            
        except Exception as e:
            print(f"Error in stop_detection: {str(e)}")

    def update_camera(self, dt):
        if not self.is_detecting or self.cap is None:
            return False

        try:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.update_error_label("Error: Could not read frame")
                return False

            frame = cv2.flip(frame, 1)
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.camera_view.texture = texture

            if self.model is not None:
                try:
                    self.process_frame(frame)
                except Exception as e:
                    self.update_error_label(f"Detection error: {str(e)}")
                    return False

            return True

        except Exception as e:
            self.update_error_label(f"Camera error: {str(e)}")
            return False

    def process_frame(self, frame):
        if self.model is None:
            return

        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.model(frame_rgb)
            detected_objects = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf.cpu().numpy()[0]
                    cls = int(box.cls.cpu().numpy()[0])
                    
                    if conf > 0.25:
                        label = f"{result.names[cls]} {conf:.2f}"
                        detected_objects.append(label)
                        
                        c1 = (int(x1), int(y1))
                        c2 = (int(x2), int(y2))
                        
                        cv2.rectangle(frame, c1, c2, (0, 255, 0), 3)
                        
                        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
                        cv2.rectangle(frame, (c1[0], c1[1] - text_size[1] - 4),
                                    (c1[0] + text_size[0], c1[1]), (0, 255, 0), -1)
                        cv2.putText(frame, label, (c1[0], c1[1] - 2),
                                  cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

            if detected_objects:
                self.update_status_label("Detected: " + ", ".join(detected_objects))
            else:
                self.update_status_label("No objects detected")

            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.camera_view.texture = texture

        except Exception as e:
            import traceback
            error_msg = f"Processing error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            self.update_error_label(error_msg)

    def on_leave(self):
        self.stop_detection()

    def go_back(self, instance):
        self.stop_detection()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'

    def update_error_label(self, error_message):
        def update(dt):
            self.result_label.text = error_message
            if self.is_detecting:
                self.stop_detection()
        Clock.schedule_once(update)

    def update_status_label(self, status_message):
        def update(dt):
            self.result_label.text = status_message
        Clock.schedule_once(update)

    def load_model(self):
        try:
            import torch
            import sys
            import logging
            import os
            from ultralytics import YOLO
            
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)
            
            self.update_status_label("Loading YOLOv5 model...")
            logger.info("Starting model load")
            
            try:
                model_path = os.path.join(os.path.dirname(__file__), 'yolov5s.pt')
                logger.info(f"Loading model from: {model_path}")
                self.model = YOLO(model_path)
                logger.info("Model loaded successfully")
                self.update_status_label("Model loaded successfully. Starting detection...")
                
            except Exception as model_error:
                logger.error(f"Error loading model: {str(model_error)}")
                logger.error(f"Python path: {sys.path}")
                raise model_error
                
        except Exception as e:
            error_msg = f"Error in load_model: {str(e)}"
            logger.error(error_msg)
            self.update_error_label(error_msg)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state_manager = StateManager()
        self.bluetooth_manager = BluetoothManager()  
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.logo = Image(
            source='voicebot_logo.png',
            size_hint=(1, 1.2),
            allow_stretch=True,
            keep_ratio=True
        )
        
        status_layout = BoxLayout(size_hint_y=None, height=40)
        self.status_label = Label(
            text="Status: Ready",
            color=(0, 0.8, 0.8, 1)
        )
        status_layout.add_widget(self.status_label)
        
        buttons_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=120)
        
        self.start_button = CustomButton(
            text="Start",
            background_color=COLORS['accent'],
            color=COLORS['text_light'],
            size_hint=(None, None),
            size=(200, 50)
        )
        self.start_button.bind(on_press=self.start_voice_recognition)
        
        self.distance_button = CustomButton(
            text="Object Identification",
            background_color=COLORS['primary'],
            color=COLORS['text_light'],
            size_hint=(None, None),
            size=(200, 50)
        )
        self.distance_button.bind(on_press=self.measure_distance)

        self.settings_button = CustomButton(
            text="Settings",
            background_color=COLORS['secondary'],
            color=COLORS['text'],
            size_hint=(None, None),
            size=(200, 50)
        )
        
        self.logout_button = CustomButton(
            text="Logout",
            background_color=COLORS['warning'],
            color=COLORS['text_light'],
            size_hint=(None, None),
            size=(200, 50)
        )
        self.logout_button.bind(on_press=self.logout)
        
        self.settings_button.bind(on_press=self.show_settings)
        
        buttons_layout.add_widget(self.start_button)
        buttons_layout.add_widget(self.distance_button)
        buttons_layout.add_widget(self.settings_button)
        buttons_layout.add_widget(self.logout_button)

        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=30
        )
        
        main_layout.add_widget(self.logo)
        main_layout.add_widget(status_layout)
        main_layout.add_widget(buttons_layout)
        main_layout.add_widget(self.progress)
        
        self.add_widget(main_layout)
        
        self.state_manager.add_observer(self)

    def measure_distance(self, instance):
        print("Measure distance called")
        if isinstance(instance, CustomButton):
            original_color = instance.background_color
            Animation(background_color=[c * 0.8 for c in original_color[:3]] + [original_color[3]], duration=0.1).start(instance)
            Animation(background_color=original_color, duration=0.3).start(instance)
        
        print("Switching to object identification screen")
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'object_identification'
        speak("Opening object identification")

    def on_state_change(self, new_state):
        state_messages = {
            BotState.IDLE: "Status: Ready",
            BotState.LISTENING: "Status: Listening...",
            BotState.PROCESSING: "Status: Processing...",
            BotState.ERROR: "Status: Error"
        }
        self.status_label.text = state_messages.get(new_state, "Status: Unknown")
        speak(self.status_label.text)

    def send_arduino_command(self, command):
        if self.bluetooth_manager.send_command(command):
            print(f"Sent command: {command}")
            speak(f"Command sent: {command}")
        else:
            print("Bluetooth not connected")
            speak("Bluetooth error")

    def show_bluetooth_devices(self):
        devices = self.bluetooth_manager.discover_devices()
        layout = BoxLayout(orientation='vertical')
        
        for device in devices:
            btn = Button(text=f"{device['name']} ({device['address']})")
            btn.bind(on_press=lambda x, addr=device['address']: self.connect_bluetooth(addr))
            layout.add_widget(btn)
        
        popup = Popup(title="Select Bluetooth Device", content=layout)
        popup.open()

    def connect_bluetooth(self, device_address):
        if self.bluetooth_manager.connect(device_address):
            speak("Bluetooth connected")
        else:
            speak("Connection failed")

    def start_voice_recognition(self, instance):
        try:
            if not self.check_microphone():
                self.status_label.text = "Microphone not available"
                speak("Microphone not available")
                return
            
            self.state_manager.change_state(BotState.LISTENING)
            speak("I'm listening speak_now'..")
        
            import threading
            threading.Thread(
                target=self.process_voice_command_thread,
                daemon=True
            ).start()
        
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"
            self.state_manager.change_state(BotState.ERROR)
            speak("Error starting voice recognition")

    def check_microphone(self):
        try:
            import speech_recognition as sr
            print("Available microphones:", sr.Microphone.list_microphone_names())
            with sr.Microphone() as source:
                print("Microphone test successful!")
                return True
        except Exception as e:
            print(f"Microphone error: {e}")
            return False

    def process_voice_command_thread(self):
        try:
            command = listen_for_command()
            Clock.schedule_once(lambda dt: self.handle_voice_command(command))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.handle_voice_error(e))

    def handle_voice_command(self, command):
        try:
            self.state_manager.change_state(BotState.PROCESSING)
            
            command = command.lower()
            
            if command in ['go', 'forward']:
                self.send_arduino_command('F')
                self.status_label.text = "Moving forward"
            elif command == 'backward':
                self.send_arduino_command('B')
                self.status_label.text = "Moving backward"
            elif command == 'left':
                self.send_arduino_command('L')
                self.status_label.text = "Turning left"
            elif command == 'right':
                self.send_arduino_command('R')
                self.status_label.text = "Turning right"
            elif command in ['stop', 'halt']:
                self.send_arduino_command('S')
                self.status_label.text = "Stopping"
            else:
                self.status_label.text = f"Command: {command}"
            
            speak(self.status_label.text)
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"
            speak("Command processing error")
        finally:
            self.state_manager.change_state(BotState.IDLE)

    def handle_voice_error(self, error):
        self.status_label.text = f"Error: {str(error)}"
        speak("Voice recognition failed")
        self.state_manager.change_state(BotState.ERROR)

    def send_arduino_command(self, command):
        if hasattr(self, 'radar_manager') and hasattr(self.radar_manager, 'send_command'):
            if self.radar_manager.send_command(command):
                print(f"Sent command to Arduino: {command}")
            else:
                print("Failed to send command to Arduino")
                self.status_label.text = "Arduino not connected"
                speak("Arduino not connected")
        else:
            print("Radar manager not available")
            self.status_label.text = "Arduino not connected"
            speak("Arduino not connected")

    def logout(self, instance):
        speak("GOOD BYE!")
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'login'

    def show_settings(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'settings'

class StateManager:
    def __init__(self):
        self.current_state = BotState.IDLE
        self.observers = []
        
    def change_state(self, new_state):
        self.current_state = new_state
        self.notify_observers()
        
    def add_observer(self, observer):
        self.observers.append(observer)
        
    def notify_observers(self):
        for observer in self.observers:
            observer.on_state_change(self.current_state)

class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLORS['button_normal']
        self.color = COLORS['text_light']
        self.border = (0, 0, 0, 0)
        with self.canvas.before:
            Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[10,]
            )
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def on_press(self):
        self.background_color = COLORS['button_down']
        Animation(background_color=COLORS['button_normal'], duration=0.3).start(self)

class StyledLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = COLORS['text']
        self.padding = [10, 10]
        with self.canvas.before:
            Color(*COLORS['secondary'])
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[5,]
            )
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = COLORS['secondary']
        self.foreground_color = COLORS['text']
        self.cursor_color = COLORS['primary']
        self.padding = [10, 10, 10, 10]
        self.multiline = False

class StyledSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLORS['primary']
        self.color = COLORS['text_light']
        self.font_size = '16sp'
        self.option_cls = SpinnerOption
        
        with self.canvas.before:
            Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[8,]
            )
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

class SpinnerOption(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLORS['primary']
        self.color = COLORS['text_light']
        self.font_size = '14sp'
        
        with self.canvas.before:
            Color(*self.background_color)
            Rectangle(pos=self.pos, size=self.size)

    def on_press(self):
        self.background_color = [
            c * 0.8 for c in COLORS['primary'][:3]
        ] + [COLORS['primary'][3]]

class VoiceBotGUI(App):
    def build(self):
        Window.size = (400, 600)
        self.title = 'VoiceBot Assistant'
        
        sm = ScreenManager()
        
        from my_utils import config_manager
        from language_support import language_manager
        
        saved_lang = config_manager.get('app.language', 'en')
        language_manager.set_language(saved_lang)
        
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(ObjectIdentificationScreen(name='object_identification'))
        
        self.radar_manager = ArduinoRadarManager(self)
        
        return sm

    def on_stop(self):
        if hasattr(self, 'radar_manager'):
            self.radar_manager.close()

>>>>>>> f02ac2d (test)
if __name__ == '__main__':
    VoiceBotGUI().run()