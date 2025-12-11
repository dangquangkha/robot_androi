import os
from openai import OpenAI
from dotenv import load_dotenv

# Load env ngay khi import
load_dotenv()

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Chưa cấu hình OPENAI_API_KEY trong file .env")
        self.client = OpenAI(api_key=api_key)

    def get_chat_response(self, user_text):
        """Gửi text lên GPT-4o-mini và nhận phản hồi"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Bạn là trợ lý ảo hữu ích, trả lời ngắn gọn."},
                    {"role": "user", "content": user_text}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Lỗi OpenAI Chat: {str(e)}"

    def text_to_speech(self, text, filename):
        """
        Lưu file trực tiếp vào đường dẫn được chỉ định (filename).
        filename phải là đường dẫn tuyệt đối an toàn.
        """
        try:
            with self.client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="alloy",
                input=text
            ) as response:
                response.stream_to_file(filename)
            return filename
        except Exception as e:
            print(f"Lỗi TTS: {e}")
            return None