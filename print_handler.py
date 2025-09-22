from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QPageLayout, QPageSize
from PyQt5.QtCore import QMarginsF

class PrintHandler:
    """处理打印功能的类 v2.0"""
    
    def __init__(self):
        self.page_size = "A4"
        self.page_orientation = "portrait"
    
    def set_page_size(self, size):
        """设置页面大小"""
        self.page_size = size

    def set_page_orientation(self, orientation):
        """设置页面方向"""
        self.page_orientation = orientation

    def configure_printer(self, printer):
        """配置打印机"""
        sizes = {
            "A0": QPageSize.A0, "A1": QPageSize.A1, "A2": QPageSize.A2,
            "A3": QPageSize.A3, "A4": QPageSize.A4, "A5": QPageSize.A5,
            "A6": QPageSize.A6, "Letter": QPageSize.Letter,
            "Legal": QPageSize.Legal, "Tabloid": QPageSize.Tabloid
        }
        page_size_id = sizes.get(self.page_size, QPageSize.A4)
        page_size = QPageSize(page_size_id)
        
        # 根据方向设置页面布局
        if self.page_orientation == "landscape":
            page_layout = QPageLayout(page_size, QPageLayout.Landscape, QMarginsF(0, 0, 0, 0))
        else:
            page_layout = QPageLayout(page_size, QPageLayout.Portrait, QMarginsF(0, 0, 0, 0))
        
        printer.setPageLayout(page_layout)
        
    def get_orientation(self):
        """获取当前设置的页面方向"""
        return self.page_orientation
    