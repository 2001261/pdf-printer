from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

class DisplayHandler:
    """处理页面显示的类 v2.0"""
    
    def __init__(self, page_label, pdf_handler, scaling_handler, page_size_handler, layout_handler, scroll_area):
        self.page_label = page_label
        self.pdf_handler = pdf_handler
        self.scaling_handler = scaling_handler
        self.page_size_handler = page_size_handler
        self.layout_handler = layout_handler
        self.scroll_area = scroll_area # Assign scroll_area here
        self.display_scale_factor = 1.0 # New attribute for display-specific scaling

    def display_single_page(self, current_page):
        # 获取页面原始尺寸 (以点为单位)
        pdf_width_pts, pdf_height_pts = self.pdf_handler.get_page_size(current_page)

        # 获取输出页面尺寸 (例如A4, Letter) 在点为单位
        output_page_width_pts, output_page_height_pts = self.page_size_handler.get_page_size_points()
        print(f"[display_single_page] Initial output_page_pts: {output_page_width_pts}x{output_page_height_pts}, Orientation: {self.page_size_handler.page_orientation}")
        
        # 根据页面方向调整输出页面尺寸 (仍然是点为单位)
        output_page_width_pts, output_page_height_pts = \
            self.page_size_handler.adjust_dimensions_for_orientation(
                output_page_width_pts, output_page_height_pts, pdf_width_pts, pdf_height_pts)
        print(f"[display_single_page] Adjusted output_page_pts: {output_page_width_pts}x{output_page_height_pts}")
        
        # 将调整后的输出页面尺寸从点转换为像素 (使用96 DPI)
        output_page_width_px = int(output_page_width_pts * (96/72))
        output_page_height_px = int(output_page_height_pts * (96/72))
        print(f"[display_single_page] Final output_page_px: {output_page_width_px}x{output_page_height_px}")

        # 创建一个QPixmap作为输出页面，用于绘制PDF内容
        output_pixmap = QPixmap(output_page_width_px, output_page_height_px)
        output_pixmap.fill(Qt.white) # 填充白色背景

        painter = QPainter(output_pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # 渲染原始PDF页面为96DPI的QPixmap
        pdf_page_img = self.pdf_handler.render_page(current_page, dpi=96)
        if not pdf_page_img:
            painter.end()
            return

        # 计算内容缩放因子 (用户在UI中设置的缩放)
        content_scale_factor = self.scaling_handler.scale_factor

        # 计算将原始PDF内容（在96DPI下）缩放到输出页面尺寸所需的比例
        scale_x_to_output = (output_page_width_px / pdf_page_img.width()) * content_scale_factor
        scale_y_to_output = (output_page_height_px / pdf_page_img.height()) * content_scale_factor
        
        # 保持纵横比，并留一些边距
        final_content_scale = min(scale_x_to_output, scale_y_to_output) * 0.9

        painter.save()
        
        # 移动到输出页面中心
        center_x = output_page_width_px / 2
        center_y = output_page_height_px / 2
        painter.translate(center_x, center_y)
        
        # 应用旋转
        painter.rotate(self.scaling_handler.rotation_angle)
        
        # 应用内容缩放
        painter.scale(final_content_scale, final_content_scale)
        
        # 绘制图像 (现在图像的中心在(0,0)，需要平移回图像的左上角)
        painter.drawPixmap(int(-pdf_page_img.width() / 2), int(-pdf_page_img.height() / 2), pdf_page_img)
        
        painter.restore()
        painter.end()

        # 应用显示缩放因子
        if self.display_scale_factor != 1.0:
            scaled_width = int(output_pixmap.width() * self.display_scale_factor)
            scaled_height = int(output_pixmap.height() * self.display_scale_factor)
            output_pixmap = output_pixmap.scaled(scaled_width, scaled_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # 设置标签大小以适应图像
        self.page_label.setPixmap(output_pixmap)
        # Force layout update for scroll area
        self.page_label.adjustSize() # Adjust size of the label itself
        self.scroll_area.widget().adjustSize() # Adjust size of the widget inside scroll area
        self.scroll_area.updateGeometry() # Request a layout update for the scroll area
        
        # Force Qt to process events immediately
        QApplication.processEvents()

    def display_adaptive_pages(self, current_page):
        # 获取页面原始尺寸 (以点为单位)
        pdf_width_pts, pdf_height_pts = self.pdf_handler.get_page_size(current_page)

        # 获取输出页面尺寸 (例如A4, Letter) 在点为单位
        output_page_width_pts, output_page_height_pts = self.page_size_handler.get_page_size_points()
        print(f"[display_adaptive_pages] Initial output_page_pts: {output_page_width_pts}x{output_page_height_pts}, Orientation: {self.page_size_handler.page_orientation}")
        
        # 根据页面方向调整输出页面尺寸 (仍然是点为单位)
        adjusted_output_width_pts, adjusted_output_height_pts = \
            self.page_size_handler.adjust_dimensions_for_orientation(
                output_page_width_pts, output_page_height_pts, pdf_width_pts, pdf_height_pts)
        print(f"[display_adaptive_pages] Adjusted output_page_pts: {adjusted_output_width_pts}x{adjusted_output_height_pts}")
        
        # 将调整后的输出页面尺寸从点转换为像素 (使用96 DPI)
        target_width = int(adjusted_output_width_pts * (96/72))
        target_height = int(adjusted_output_height_pts * (96/72))
        print(f"[display_adaptive_pages] Final target_px: {target_width}x{target_height}")
        
        # 创建一个大的pixmap来容纳页面
        combined_img = QPixmap(target_width, target_height)
        combined_img.fill(Qt.white)
        
        # 创建绘图设备
        painter = QPainter(combined_img)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # 计算当前组实际的页面数量（不超过剩余页面数）
        remaining_pages = self.pdf_handler.get_page_count() - current_page
        page_count = min(self.layout_handler.pages_per_sheet, remaining_pages)
        
        # 使用布局处理器绘制自适应页面
        self.layout_handler.draw_adaptive_pages(\
            painter, self.pdf_handler, self.scaling_handler, \
            target_width, target_height, current_page, page_count)
        
        # 结束绘制
        painter.end()
        
        # 应用显示缩放因子
        if self.display_scale_factor != 1.0:
            scaled_width = int(combined_img.width() * self.display_scale_factor)
            scaled_height = int(combined_img.height() * self.display_scale_factor)
            combined_img = combined_img.scaled(scaled_width, scaled_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # 显示组合图像
        self.page_label.setPixmap(combined_img)
        self.page_label.setFixedSize(combined_img.width(), combined_img.height())
        
        # Force layout update for scroll area
        self.page_label.adjustSize() # Adjust size of the label itself
        self.scroll_area.widget().adjustSize() # Adjust size of the widget inside scroll area
        self.scroll_area.updateGeometry() # Request a layout update for the scroll area
        
        # Force Qt to process events immediately
        QApplication.processEvents()

    def get_natural_display_size(self, current_page):
        # 获取页面原始尺寸 (以点为单位)
        pdf_width_pts, pdf_height_pts = self.pdf_handler.get_page_size(current_page)

        # 获取输出页面尺寸 (例如A4, Letter) 在点为单位
        output_page_width_pts, output_page_height_pts = self.page_size_handler.get_page_size_points()
        
        # 根据页面方向调整输出页面尺寸 (仍然是点为单位)
        output_page_width_pts, output_page_height_pts = \
            self.page_size_handler.adjust_dimensions_for_orientation(
                output_page_width_pts, output_page_height_pts, pdf_width_pts, pdf_height_pts)
        
        # 将调整后的输出页面尺寸从点转换为像素 (使用96 DPI)
        natural_width = int(output_page_width_pts * (96/72))
        natural_height = int(output_page_height_pts * (96/72))
        
        return natural_width, natural_height