from kivy.uix.screenmanager import Screen # <--- Thay đổi import
from kivy.lang import Builder
import os

Builder.load_file(os.path.join(os.path.dirname(__file__), 'chat.kv'))

# Đổi từ BoxLayout sang Screen
class ChatView(Screen): 
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