from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter


class LayoutHandler:
    """处理页面布局的类 v2.0"""
    
    def __init__(self, page_size_handler):
        self.pages_per_sheet = 1
        self.adaptive_mode = False
        self.page_size_handler = page_size_handler # Store page_size_handler
    
    def set_pages_per_sheet(self, count):
        """设置每张纸上的页面数"""
        self.pages_per_sheet = count
    
    def set_adaptive_mode(self, enabled):
        """设置自适应模式"""
        self.adaptive_mode = enabled
    
    def _get_layout_info(self, page_count):
        """根据页面数量获取布局信息"""
        layouts = {
            1: {"rows": 1, "cols": 1, "name": "single"},
            2: {"rows": 1, "cols": 2, "name": "two_horizontal"},
            3: {"rows": 2, "cols": 2, "name": "three_grid"},
            4: {"rows": 2, "cols": 2, "name": "four_grid"},
            6: {"rows": 2, "cols": 3, "name": "six_grid"},
            9: {"rows": 3, "cols": 3, "name": "nine_grid"},
            16: {"rows": 4, "cols": 4, "name": "sixteen_grid"}
        }
        # 总是返回预定义的布局，确保一致性
        return layouts.get(page_count, layouts[1])  # 默认返回单页布局
    
    def _calculate_cell_dimensions(self, target_width, target_height, rows, cols):
        """计算每个单元格的尺寸"""
        cell_width = target_width / cols
        cell_height = target_height / rows
        return cell_width, cell_height
    
    def _calculate_cell_position(self, cell_width, cell_height, col, row):
        """计算单元格的位置"""
        x = col * cell_width
        y = row * cell_height
        return x, y
    
    def draw_adaptive_pages(self, painter, pdf_handler, scaling_handler, target_width, target_height, 
                           current_page_index, page_count):
        """绘制自适应页面布局"""
        # 按照每页页面数分组来处理
        # 计算布局信息（使用固定的每页页面数）
        layout = self._get_layout_info(self.pages_per_sheet)
        rows = layout["rows"]
        cols = layout["cols"]
        
        # 计算每个单元格的尺寸
        cell_width, cell_height = self._calculate_cell_dimensions(target_width, target_height, rows, cols)
        
        # 绘制每个页面（包括空白页）
        for i in range(self.pages_per_sheet):
            # 计算页面在网格中的位置
            row = i // cols
            col = i % cols
            
            # 计算页面位置
            x, y = self._calculate_cell_position(cell_width, cell_height, col, row)
            
            # 检查是否还有实际页面需要绘制
            if i < page_count and current_page_index + i < pdf_handler.get_page_count():
                # 绘制实际页面
                self._draw_single_page(painter, pdf_handler, scaling_handler, cell_width, cell_height, 
                                    x, y, current_page_index + i)
            else:
                # 绘制空白页（只绘制边框或保持空白）
                # 这里我们选择保持空白，不绘制任何内容
                pass
    
    def _draw_single_page(self, painter, pdf_handler, scaling_handler, width, height, x, y, page_index):
        """绘制单个页面"""
        # 检查页面索引是否有效
        if page_index >= pdf_handler.get_page_count():
            return
        
        # 渲染页面为Pixmap (以固定DPI，例如96 DPI)
        # 这里的img是原始PDF页面在96DPI下的渲染结果，不包含用户缩放和旋转
        img = pdf_handler.render_page(page_index, dpi=96)
        if not img:
            return
        
        # 计算内容缩放因子 (用户在UI中设置的缩放)
        content_scale_factor = scaling_handler.scale_factor

        # 计算将原始PDF内容（在96DPI下）缩放到单元格大小所需的比例
        # 考虑用户缩放因子
        scale_x_to_cell = (width / img.width()) * content_scale_factor
        scale_y_to_cell = (height / img.height()) * content_scale_factor
        
        # 保持纵横比，并留一些边距
        final_content_scale = min(scale_x_to_cell, scale_y_to_cell)

        # 保存painter状态
        painter.save()
        
        # 移动到单元格中心
        center_x = x + width / 2
        center_y = y + height / 2
        painter.translate(center_x, center_y)
        
        # 应用旋转 (只使用用户设置的旋转角度)
        painter.rotate(scaling_handler.rotation_angle)
        
        # 应用内容缩放
        painter.scale(final_content_scale, final_content_scale)
        
        # 绘制图像 (现在图像的中心在(0,0)，需要平移回图像的左上角)
        painter.drawPixmap(int(-img.width() / 2), int(-img.height() / 2), img)
        
        # 恢复painter状态
        painter.restore()