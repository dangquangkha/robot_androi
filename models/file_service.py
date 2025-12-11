import os
from pypdf import PdfReader
from docx import Document

class FileService:
    def read_file(self, file_path):
        """Đọc nội dung từ file .txt, .pdf, .docx và trả về string"""
        if not os.path.exists(file_path):
            return None

        ext = file_path.split('.')[-1].lower()
        content = ""

        try:
            if ext == 'txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            elif ext == 'pdf':
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        content += text + "\n"
            
            elif ext == 'docx':
                doc = Document(file_path)
                for para in doc.paragraphs:
                    content += para.text + "\n"
            
            else:
                return "Định dạng file không hỗ trợ."

            return content.strip()
            
        except Exception as e:
            print(f"Lỗi đọc file: {e}")
            return None