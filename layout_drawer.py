from PyQt5.QtGui import QPainter
from PyQt5.QtPrintSupport import QPrinter

class LayoutDrawer:
    """在给定的QPainter上绘制布局的类 v2.0"""

    def draw_layout(self, painter, pdf_handler, layout_handler, scaling_handler, page_size_handler, target_width, target_height):
        """在给定的QPainter上绘制布局"""
        try:
            # 设置渲染提示以获得更好的质量
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.TextAntialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

            # 计算总共有多少个重排后的页面
            total_pages = pdf_handler.get_page_count()
            total_layout_pages = (total_pages + layout_handler.pages_per_sheet - 1) // layout_handler.pages_per_sheet

            # 为每个重排页面绘制内容
            for layout_page_index in range(total_layout_pages):
                if layout_page_index > 0:
                    # 如果是打印机，则需要新起一页
                    if isinstance(painter.device(), QPrinter):
                        painter.device().newPage()

                # 计算当前重排页面的起始PDF页面索引
                start_pdf_page = layout_page_index * layout_handler.pages_per_sheet

                # 计算当前重排页面包含的PDF页面数量
                remaining_pages = total_pages - start_pdf_page
                page_count = min(layout_handler.pages_per_sheet, remaining_pages)

                # 绘制自适应页面布局
                layout_handler.draw_adaptive_pages(
                    painter, pdf_handler, scaling_handler, 
                    target_width, target_height, start_pdf_page, page_count)

        except Exception as e:
            print(f"绘制布局时出错: {str(e)}")