from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
import os

# Load file kv của home (sẽ tạo ở bước sau)
Builder.load_file(os.path.join(os.path.dirname(__file__), 'home.kv'))

class HomeView(Screen):
    pass