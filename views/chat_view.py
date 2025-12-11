from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
import os

# Load file .kv
Builder.load_file(os.path.join(os.path.dirname(__file__), 'chat.kv'))

class ChatView(BoxLayout):
    def __init__(self, controller=None, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

    def on_mic_press(self):
        if self.controller:
            self.controller.start_listening()

    def update_status(self, text):
        self.ids.status_label.text = text

    def update_chat_log(self, role, text):
        self.ids.chat_history.text += f"\n[{role}]: {text}"
    
    def on_file_press(self):
        if self.controller:
            self.controller.select_file()