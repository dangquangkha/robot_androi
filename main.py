import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from views.chat_view import ChatView
from views.home_view import HomeView # Import màn hình Home
from controllers.chat_controller import ChatController

# Tạo thư mục assets nếu chưa có
if not os.path.exists("assets"):
    os.makedirs("assets")

class ChatApp(App):
    def build(self):
        # 1. Khởi tạo ScreenManager (Quản lý màn hình)
        sm = ScreenManager()

        # 2. Khởi tạo Controller & ChatView như cũ
        controller = ChatController()
        chat_view = ChatView(controller=controller)
        controller.set_view(chat_view) # Gán view vào controller

        # 3. Khởi tạo HomeView
        home_view = HomeView()

        # 4. Thêm các màn hình vào Manager
        sm.add_widget(home_view) # Màn hình nào add trước sẽ hiện trước
        sm.add_widget(chat_view)

        return sm

if __name__ == '__main__':
    ChatApp().run()