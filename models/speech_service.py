import threading
from kivy.utils import platform

# Chỉ import thư viện PC nếu không phải là Android/iOS
if platform != 'android' and platform != 'ios':
    import speech_recognition as sr
else:
    # Import thư viện cho Android
    from plyer import stt

class SpeechService:
    def __init__(self):
        self.is_android = (platform == 'android')
        self.callback_function = None # Hàm sẽ được gọi khi có kết quả

        if not self.is_android:
            # Cấu hình cho PC
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
        else:
            # Cấu hình cho Android (Plyer)
            try:
                stt.init()
            except Exception as e:
                print(f"Lỗi khởi tạo STT Android: {e}")

    def start_listening(self, on_result_callback):
        """
        Hàm này bắt đầu nghe.
        :param on_result_callback: Hàm sẽ nhận text kết quả (vd: func(text))
        """
        self.callback_function = on_result_callback

        if self.is_android:
            self._listen_android()
        else:
            # Trên PC phải chạy luồng riêng để không đơ ứng dụng
            threading.Thread(target=self._listen_pc).start()

    # --- XỬ LÝ CHO ANDROID ---
    def _listen_android(self):
        try:
            if self.callback_function:
                # Plyer yêu cầu gán hàm xử lý kết quả
                stt.on_results = self._on_android_results
                stt.on_errors = self._on_android_errors
                stt.start() # Gọi UI nhận diện giọng nói của Google trên Android
        except Exception as e:
            if self.callback_function:
                self.callback_function(f"Lỗi Android STT: {e}")

    def _on_android_results(self, results, partial=False):
        # Kết quả trả về là một list, lấy phần tử đầu tiên chính xác nhất
        if results and len(results) > 0:
            text = results[0]
            if self.callback_function:
                self.callback_function(text)

    def _on_android_errors(self, errors):
        if self.callback_function:
            self.callback_function("Không nghe rõ hoặc lỗi mạng.")

    # --- XỬ LÝ CHO PC ---
    def _listen_pc(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # Giả lập trạng thái "đang nghe" (bạn có thể update UI ở controller)
            
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio, language='vi-VN')
                
                # Gọi callback trả kết quả về Controller
                if self.callback_function:
                    self.callback_function(text)
                    
            except sr.WaitTimeoutError:
                if self.callback_function: self.callback_function(None) # Hết giờ
            except sr.UnknownValueError:
                if self.callback_function: self.callback_function("Không nghe rõ.")
            except Exception as e:
                if self.callback_function: self.callback_function(f"Lỗi PC: {e}")