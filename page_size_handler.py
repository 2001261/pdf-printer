from PyQt5.QtGui import QPageLayout, QPageSize
from PyQt5.QtCore import Qt

class PageSizeHandler:
    """处理页面大小的类 v2.0"""
    
    def __init__(self):
        self.page_size = "A4"
        self.page_orientation = "portrait"
    
    def _get_qpagesize_id(self, size_name):
        """将页面尺寸名称字符串映射到QPageSize.PageSizeId"""
        # This mapping needs to be comprehensive for all supported sizes
        # For now, let's add the ones used in the UI
        mapping = {
            "A0": QPageSize.A0,
            "A1": QPageSize.A1,
            "A2": QPageSize.A2,
            "A3": QPageSize.A3,
            "A4": QPageSize.A4,
            "A5": QPageSize.A5,
            "A6": QPageSize.A6,
            "Letter": QPageSize.Letter,
            "Legal": QPageSize.Legal,
            "Tabloid": QPageSize.Tabloid,
            # Add other sizes as needed
        }
        return mapping.get(size_name, QPageSize.A4) # Default to A4 if not found

    def set_page_size(self, size):
        """设置页面大小"""
        self.page_size = size
    
    def set_page_orientation(self, orientation):
        """设置页面方向"""
        self.page_orientation = orientation
    
    def get_page_size_info(self):
        """获取当前页面尺寸的宽度和高度（像素，基于DPI）"""
        page_layout = QPageLayout()
        page_layout.setPageSize(QPageSize(self._get_qpagesize_id(self.page_size))) # Use helper
        
        if self.page_orientation == "portrait":
            page_layout.setOrientation(QPageLayout.Portrait) # Revert here
        else:
            page_layout.setOrientation(QPageLayout.Landscape)  # Revert here
        width_px = page_layout.pageSize().size(QPageSize.Point).width() * (96 / 72.0)
        height_px = page_layout.pageSize().size(QPageSize.Point).height() * (96 / 72.0)
        
        return {"width": int(width_px), "height": int(height_px)}
    
    def adjust_dimensions_for_orientation(self, width, height, pdf_width=None, pdf_height=None):
        """根据页面方向调整尺寸"""
        if self.page_orientation == "portrait":
            # 强制纵向
            if width > height:
                width, height = height, width
        elif self.page_orientation == "landscape":
            # 强制横向
            if width < height:
                width, height = height, width
                
        return width, height



    def get_page_size_points(self):
        """获取当前页面尺寸的宽度和高度（点）"""
        page_layout = QPageLayout()
        page_layout.setPageSize(QPageSize(self._get_qpagesize_id(self.page_size))) # Use helper
        
        if self.page_orientation == "portrait":
            page_layout.setOrientation(QPageLayout.Portrait) # Revert here
        else:
            page_layout.setOrientation(QPageLayout.Landscape)  # Revert here
            
        # 获取点尺寸
        width_pts = page_layout.pageSize().size(QPageSize.Point).width()
        height_pts = page_layout.pageSize().size(QPageSize.Point).height()
        
        return width_pts, height_pts