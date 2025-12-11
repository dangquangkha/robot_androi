import os
from kivy.app import App
from views.chat_view import ChatView
from controllers.chat_controller import ChatController

# Tạo thư mục assets nếu chưa có
if not os.path.exists("assets"):
    os.makedirs("assets")

class ChatApp(App):
    def build(self):
        # Khởi tạo Controller
        controller = ChatController()
        
        # Khởi tạo View và tiêm Controller vào
        view = ChatView(controller=controller)
        
        # Gán ngược View vào Controller (để Controller cập nhật UI)
        controller.set_view(view)
        
        return view

if __name__ == '__main__':
    ChatApp().run()