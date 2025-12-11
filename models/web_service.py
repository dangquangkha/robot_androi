import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

class WebService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.cse_id = os.getenv("GOOGLE_CSE_ID")

    def search_google(self, query):
        """Tìm kiếm trên Google và trả về URL đầu tiên"""
        if not self.api_key or not self.cse_id:
            return None, "Chưa cấu hình Google API Key."

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.api_key,
            'cx': self.cse_id,
            'q': query,
            'num': 1 # Chỉ lấy 1 kết quả đầu tiên cho nhanh
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'items' in data and len(data['items']) > 0:
                first_result = data['items'][0]
                link = first_result['link']
                snippet = first_result['snippet']
                return link, snippet
            else:
                return None, "Không tìm thấy kết quả nào."
        except Exception as e:
            return None, f"Lỗi Google API: {e}"

    def get_website_content(self, url):
        """Đọc nội dung văn bản từ một URL"""
        try:
            # Giả lập trình duyệt để tránh bị chặn
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Lấy toàn bộ thẻ <p> (đoạn văn)
            paragraphs = soup.find_all('p')
            text_content = "\n".join([p.get_text() for p in paragraphs])
            
            # Giới hạn 5000 ký tự đầu để không quá tải GPT
            return text_content[:5000]
        except Exception as e:
            return f"Không thể đọc trang web này. Lỗi: {e}"