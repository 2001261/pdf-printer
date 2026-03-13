from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter


class LayoutHandler:
    """处理页面布局的类 v2.0"""

    def __init__(self, page_size_handler):
        self.pages_per_sheet = 1
        self.adaptive_mode = False
        self.auto_swap_by_source_orientation = True
        self.page_size_handler = page_size_handler  # Store page_size_handler

    def set_pages_per_sheet(self, count):
        """设置每张纸上的页面数"""
        self.pages_per_sheet = count

    def set_adaptive_mode(self, enabled):
        """设置自适应模式"""
        self.adaptive_mode = enabled

    def set_auto_swap_by_source_orientation(self, enabled):
        """设置是否根据原始页面方向自动翻转拼版网格方向"""
        self.auto_swap_by_source_orientation = enabled

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

    def _calculate_fit_scale(self, source_width, source_height, cell_width, cell_height):
        """计算源页面放入目标单元格时的等比缩放倍率"""
        if source_width <= 0 or source_height <= 0:
            return 0
        return min(cell_width / source_width, cell_height / source_height)

    def _resolve_layout_info(self, pdf_handler, current_page_index, target_width, target_height):
        """根据当前批次首页尺寸，自适应选择更合适的行列方向"""
        layout = self._get_layout_info(self.pages_per_sheet).copy()
        rows = layout["rows"]
        cols = layout["cols"]

        if not self.auto_swap_by_source_orientation:
            return layout

        # 正方形网格没有翻转收益，直接返回。
        if rows == cols or current_page_index >= pdf_handler.get_page_count():
            return layout

        source_width, source_height = pdf_handler.get_page_size(current_page_index)
        if source_width <= 0 or source_height <= 0:
            return layout

        default_cell_width, default_cell_height = self._calculate_cell_dimensions(
            target_width, target_height, rows, cols
        )
        swapped_cell_width, swapped_cell_height = self._calculate_cell_dimensions(
            target_width, target_height, cols, rows
        )

        default_scale = self._calculate_fit_scale(
            source_width, source_height, default_cell_width, default_cell_height
        )
        swapped_scale = self._calculate_fit_scale(
            source_width, source_height, swapped_cell_width, swapped_cell_height
        )

        if swapped_scale > default_scale:
            layout["rows"], layout["cols"] = cols, rows
            layout["name"] = f'{layout["name"]}_swapped'

        return layout

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
                           current_page_index, page_count, dpi=96):
        """绘制自适应页面布局
        
        Args:
            dpi: 渲染 DPI，默认 96（显示用），打印时可使用 300 或更高
        """
        # 按照每页页面数分组来处理
        # 根据当前批次第一页尺寸，自适应决定网格方向。
        layout = self._resolve_layout_info(
            pdf_handler, current_page_index, target_width, target_height
        )
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
                # 绘制实际页面（传入 DPI）
                self._draw_single_page(painter, pdf_handler, scaling_handler, cell_width, cell_height,
                                    x, y, current_page_index + i, dpi)
            else:
                # 绘制空白页（只绘制边框或保持空白）
                # 这里我们选择保持空白，不绘制任何内容
                pass

    def _draw_single_page(self, painter, pdf_handler, scaling_handler, width, height, x, y, page_index, dpi=96):
        """绘制单个页面
        
        Args:
            dpi: 渲染 DPI，默认 96（显示用），打印时可使用 300 或更高
        """
        # 检查页面索引是否有效
        if page_index >= pdf_handler.get_page_count():
            return

        # 渲染页面为 Pixmap (使用指定 DPI)
        img = pdf_handler.render_page(page_index, dpi=dpi)
        if not img:
            return

        # 计算内容缩放因子 (用户在 UI 中设置的缩放)
        content_scale_factor = scaling_handler.scale_factor

        # 计算将原始 PDF 内容（在指定 DPI 下）缩放到单元格大小所需的比例
        # 考虑用户缩放因子
        scale_x_to_cell = (width / img.width()) * content_scale_factor
        scale_y_to_cell = (height / img.height()) * content_scale_factor

        # 保持纵横比，并留一些边距
        final_content_scale = min(scale_x_to_cell, scale_y_to_cell)

        # 保存 painter 状态
        painter.save()

        # 移动到单元格中心
        center_x = x + width / 2
        center_y = y + height / 2
        painter.translate(center_x, center_y)

        # 应用旋转 (只使用用户设置的旋转角度)
        painter.rotate(scaling_handler.rotation_angle)

        # 应用内容缩放
        painter.scale(final_content_scale, final_content_scale)

        # 绘制图像 (现在图像的中心在 (0,0)，需要平移回图像的左上角)
        painter.drawPixmap(int(-img.width() / 2), int(-img.height() / 2), img)

        # 恢复 painter 状态
        painter.restore()
