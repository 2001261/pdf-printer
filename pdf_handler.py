import fitz  # PyMuPDF
from PyQt5.QtGui import QPixmap


class PDFHandler:
    """处理PDF文件的类 v2.0"""
    
    def __init__(self):
        self.pdf_document = None
    
    def load_pdf(self, file_path):
        """加载PDF文件"""
        try:
            self.pdf_document = fitz.open(file_path)
            return True
        except Exception as e:
            print(f"无法加载PDF文件: {str(e)}")
            return False
    
    def get_page_count(self):
        """获取PDF页面总数"""
        if self.pdf_document:
            return len(self.pdf_document)
        return 0
    
    def get_page(self, page_index):
        """获取指定页面"""
        if self.pdf_document and 0 <= page_index < len(self.pdf_document):
            return self.pdf_document[page_index]
        return None
    
    def get_page_size(self, page_index):
        """获取指定页面的尺寸 (以点为单位)"""
        page = self.get_page(page_index)
        if page:
            rect = page.rect
            return rect.width, rect.height
        return 0, 0
    
    def render_page(self, page_index, dpi=96):
        """渲染页面为Pixmap，以指定DPI"""
        page = self.get_page(page_index)
        if page:
            # Create a matrix for the desired DPI, without applying user zoom
            zoom_factor = dpi / 72.0  # Default PDF DPI is 72
            mat = fitz.Matrix(zoom_factor, zoom_factor)
            
            pix = page.get_pixmap(matrix=mat)
            img = QPixmap()
            img.loadFromData(pix.tobytes("ppm"))
            return img
        return None
    
    def get_page_orientation(self, page_index):
        """获取指定页面的固有方向 ('portrait' 或 'landscape')"""
        width, height = self.get_page_size(page_index)
        if width > height:
            return "landscape"
        else:
            return "portrait"
    
    def close(self):
        """关闭PDF文件"""
        if self.pdf_document:
            self.pdf_document.close()
            self.pdf_document = None