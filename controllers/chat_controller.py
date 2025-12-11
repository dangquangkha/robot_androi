import threading
import shutil 
import os
from kivy.app import App
from kivy.clock import Clock
from kivy.utils import platform 
from kivy.core.audio import SoundLoader
from models.openai_service import OpenAIService
from models.speech_service import SpeechService
from models.file_service import FileService
from models.web_service import WebService # <--- Import mới
from plyer import filechooser

class ChatController:
    def __init__(self):
        self.view = None
        # Khởi tạo các dịch vụ
        self.openai_service = OpenAIService()
        self.speech_service = SpeechService()
        self.file_service = FileService()
        self.web_service = WebService() # <--- Khởi tạo dịch vụ Web
        
        # Khởi tạo biến
        self.file_context = ""
        self.memory_path = ""
        self.assets_dir = "" 

        # Dùng Clock chờ App load xong để lấy đường dẫn an toàn
        Clock.schedule_once(self._setup_storage_path, 0)

    def _setup_storage_path(self, dt):
        """Thiết lập đường dẫn lưu trữ (Chạy 1 lần khi mở app)"""
        if platform == 'android':
            # Android: Lưu vào /data/user/0/com.app/files/ (Được phép ghi)
            storage_path = App.get_running_app().user_data_dir
        else:
            # PC: Lưu vào thư mục hiện tại
            storage_path = os.getcwd()
        
        # Tạo folder assets trong vùng an toàn
        self.assets_dir = os.path.join(storage_path, "assets")
        if not os.path.exists(self.assets_dir):
            os.makedirs(self.assets_dir)

        # Định nghĩa đường dẫn file nhớ
        self.memory_path = os.path.join(self.assets_dir, "memory.txt")
        
        # Nạp kiến thức cũ
        self.file_context = self._load_memory_from_disk()
        
        # Cập nhật UI
        if self.file_context and self.view:
             self.view.update_status(f"Đã nhớ kiến thức cũ ({len(self.file_context)} ký tự)")

    def set_view(self, view):
        self.view = view
        # Nếu load xong trước khi set view thì update luôn ở đây
        if self.file_context:
            self.view.update_status(f"Đã nhớ tài liệu cũ ({len(self.file_context)} ký tự)")

    # --- QUẢN LÝ BỘ NHỚ ---
    def _load_memory_from_disk(self):
        if self.memory_path and os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                return ""
        return ""

    def _save_memory_to_disk(self, content):
        if not self.memory_path: return
        try:
            with open(self.memory_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"Lỗi lưu bộ nhớ: {e}")

    # --- XỬ LÝ FILE ---
    def select_file(self):
        try:
            filechooser.open_file(on_selection=self._on_file_selected)
        except Exception as e:
            self.view.update_status(f"Lỗi chọn file: {e}")

    def _on_file_selected(self, selection):
        if selection and len(selection) > 0:
            original_path = selection[0]
            filename = os.path.basename(original_path)
            
            # Dùng self.assets_dir để tránh lỗi Permission trên Android
            safe_path = os.path.join(self.assets_dir, "temp_" + filename)
            
            self.view.update_status(f"Đang học: {filename}...")
            threading.Thread(target=self._process_file_thread, args=(original_path, safe_path)).start()

    def _process_file_thread(self, original_path, safe_path):
        msg = ""
        try:
            shutil.copy2(original_path, safe_path)
            content = self.file_service.read_file(safe_path)
            
            if content:
                self.file_context = content
                self._save_memory_to_disk(content)
                msg = f"Đã học xong & Lưu bộ nhớ! ({len(content)} ký tự)"
            else:
                msg = "File rỗng hoặc lỗi đọc."
            
            if os.path.exists(safe_path):
                os.remove(safe_path)

        except Exception as e:
            msg = f"Lỗi xử lý file: {e}"

        Clock.schedule_once(lambda dt: self.view.update_status(msg))
        Clock.schedule_once(lambda dt: self.view.update_chat_log("Hệ thống", msg))

    # --- XỬ LÝ MIC & AI ---
    def start_listening(self):
        self.view.update_status("Đang nghe...")
        self.speech_service.start_listening(on_result_callback=self.process_user_input)

    def process_user_input(self, user_text):
        if not user_text:
            Clock.schedule_once(lambda dt: self.view.update_status("Không nghe thấy gì."))
            return
        
        Clock.schedule_once(lambda dt: self.view.update_chat_log("Bạn", user_text))
        threading.Thread(target=self._process_ai_response, args=(user_text,)).start()

    def _process_ai_response(self, user_text):
        Clock.schedule_once(lambda dt: self.view.update_status("Đang suy nghĩ..."))

        # --- LOGIC MỚI: TỰ ĐỘNG NHẬN DIỆN LỆNH TÌM KIẾM ---
        keywords = ["tìm kiếm", "tra cứu", "google", "tìm giúp", "web"]
        is_web_search = any(k in user_text.lower() for k in keywords)

        prompt_context = ""

        if is_web_search:
            Clock.schedule_once(lambda dt: self.view.update_status("Đang tìm trên Google..."))
            
            # 1. Gọi Google API
            link, snippet = self.web_service.search_google(user_text)
            
            if link:
                Clock.schedule_once(lambda dt: self.view.update_status(f"Đang đọc: {link[:20]}..."))
                
                # 2. Đọc nội dung bài viết
                web_content = self.web_service.get_website_content(link)
                
                # 3. Tạo ngữ cảnh cho GPT
                prompt_context = f"""
                Tôi đã tìm thấy thông tin này trên internet từ đường dẫn {link}:
                Nội dung trang web:
                '''{web_content}'''
                
                Hãy trả lời câu hỏi của người dùng dựa trên thông tin trên.
                """
            else:
                prompt_context = f"Tôi đã thử tìm kiếm nhưng gặp lỗi hoặc không có kết quả: {snippet}"
        
        # --- LOGIC CŨ: DÙNG FILE CONTEXT (Nếu không tìm web) ---
        elif self.file_context:
            prompt_context = f"Dựa vào kiến thức trong bộ nhớ:\n'''{self.file_context[:10000]}'''"

        # --- GHÉP PROMPT HOÀN CHỈNH ---
        full_prompt = f"{prompt_context}\n\nNgười dùng hỏi: {user_text}"

        try:
            # Gọi GPT
            gpt_response = self.openai_service.get_chat_response(full_prompt)
            Clock.schedule_once(lambda dt: self.view.update_chat_log("AI", gpt_response))

            # Gọi TTS
            Clock.schedule_once(lambda dt: self.view.update_status("Đang tạo giọng nói..."))
            
            # --- TỐI ƯU: LUÔN DÙNG 1 TÊN FILE DUY NHẤT ĐỂ GHI ĐÈ ---
            audio_filename = os.path.join(self.assets_dir, "cache_audio.mp3")
            
            # Xóa file cũ nếu có để tránh lỗi
            if os.path.exists(audio_filename):
                try:
                    os.remove(audio_filename)
                except Exception:
                    pass

            # Lưu file mới
            audio_file = self.openai_service.text_to_speech(gpt_response, filename=audio_filename)

            if audio_file:
                Clock.schedule_once(lambda dt: self._play_audio(audio_file))
        
        except Exception as e:
            Clock.schedule_once(lambda dt: self.view.update_status(f"Lỗi AI: {e}"))

    def _play_audio(self, filename):
        # Dừng âm thanh cũ nếu đang phát
        if hasattr(self, 'current_sound') and self.current_sound:
            try:
                self.current_sound.stop()
                self.current_sound.unload()
            except:
                pass

        self.view.update_status("Đang nói...")
        
        # Load file mới
        self.current_sound = SoundLoader.load(filename)
        
        if self.current_sound:
            self.current_sound.bind(on_stop=lambda instance: self.view.update_status("Sẵn sàng"))
            self.current_sound.play()
        else:
            self.view.update_status("Lỗi phát âm thanh")