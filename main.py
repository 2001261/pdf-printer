import sys
import logging
import tempfile
import os
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QLineEdit, QProgressDialog
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPainter, QPageLayout, QPixmap
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

# 导入我们新创建的模块
from pdf_handler import PDFHandler
from scaling_handler import ScalingHandler
from page_size_handler import PageSizeHandler
from layout_handler import LayoutHandler
from print_handler import PrintHandler
from layout_drawer import LayoutDrawer
from ui_handler import UIHandler
from display_handler import DisplayHandler
from display_refresher import DisplayRefresher



class PDFPrinterApp(UIHandler):
    def __init__(self):
        super().__init__()
        
        # 初始化处理模块
        self.pdf_handler = PDFHandler()
        self.scaling_handler = ScalingHandler()
        self.page_size_handler = PageSizeHandler()
        self.layout_handler = LayoutHandler(self.page_size_handler)
        self.print_handler = PrintHandler()
        self.layout_drawer = LayoutDrawer()
        self.display_handler = DisplayHandler(self.page_label, self.pdf_handler, self.scaling_handler, self.page_size_handler, self.layout_handler, self.scroll_area)
        self.display_refresher = DisplayRefresher(
            self.pdf_handler, self.scaling_handler, self.page_size_handler, 
            self.layout_handler, self.display_handler, self.print_handler)
        
        # 初始化变量
        self.current_page = 0
        self.fit_to_window_active = False # New state variable
        
        # 设置默认的自适应模式
        self.layout_handler.set_adaptive_mode(True)
        
        # 连接信号和槽
        self.load_button.clicked.connect(self.load_pdf)
        self.print_button.clicked.connect(self.print_pdf)
        self.print_preview_button.clicked.connect(self.print_preview)
        self.fit_to_window_button.clicked.connect(self.fit_to_window)  # 新增连接
        self.zoom_combo.currentIndexChanged.connect(self.zoom_changed)
        self.custom_zoom_input.returnPressed.connect(self.custom_zoom_entered)
        self.rotate_combo.currentIndexChanged.connect(self.rotate_changed)
        self.size_combo.currentIndexChanged.connect(self.size_changed)
        self.adaptive_checkbox.stateChanged.connect(self.adaptive_mode_changed)
        self.orientation_combo.currentIndexChanged.connect(self.orientation_changed)
        self.pages_per_sheet_combo.currentIndexChanged.connect(self.pages_per_sheet_changed)
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)
        self.page_scrollbar.valueChanged.connect(self.scrollbar_changed)
        
        # 安装事件过滤器以处理鼠标滚轮事件
        self.scroll_area.installEventFilter(self)
        self.page_label.installEventFilter(self)
        
    def fit_to_window(self):
        """适应窗口大小功能 - 控制新PDF页面在GUI窗口中的显示大小，不影响渲染缩放"""
        if self.pdf_handler.get_page_count() > 0:
            self.fit_to_window_active = not self.fit_to_window_active # Toggle state

            if self.fit_to_window_active:
                self._calculate_and_apply_fit_to_window_scale()
            else:
                # If fit to window is deactivated, revert to default display scale (1.0)
                self.display_refresher.refresh_display(self.current_page, 1.0)

    def _calculate_and_apply_fit_to_window_scale(self):
        if self.pdf_handler.get_page_count() > 0:
            available_width = self.scroll_area.viewport().width() - 40
            available_height = self.scroll_area.viewport().height() - 40
            
            natural_width, natural_height = self.display_handler.get_natural_display_size(self.current_page)

            if natural_width > 0 and natural_height > 0:
                scale_x = available_width / natural_width
                scale_y = available_height / natural_height
                display_scale = min(scale_x, scale_y)
                self.display_refresher.refresh_display(self.current_page, display_scale)
            else:
                self.display_refresher.refresh_display(self.current_page, 1.0)
        
    def eventFilter(self, obj, event):
        # 处理鼠标滚轮事件以调整滚动条
        if event.type() == event.Wheel and (obj is self.scroll_area or obj is self.page_label):
            # 获取滚动条的当前值
            current_value = self.page_scrollbar.value()
            
            # 根据滚轮方向调整滚动条值
            if event.angleDelta().y() > 0:  # 向上滚动
                self.page_scrollbar.setValue(max(0, current_value - 1))
            else:  # 向下滚动
                max_value = self.page_scrollbar.maximum()
                self.page_scrollbar.setValue(min(max_value, current_value + 1))
                
            return True  # 事件已处理
            
        return super().eventFilter(obj, event)
        
    def load_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "打开PDF文件", "", "PDF Files (*.pdf)")
        if file_path:
            if self.pdf_handler.load_pdf(file_path):
                self.current_page = 0
                
                # 设置默认缩放为100%
                self.scaling_handler.set_scale_factor(1.0)
                self.zoom_combo.setCurrentText("100%")
                self.custom_zoom_input.setVisible(False)
                
                # 根据PDF的固有方向设置页面方向
                initial_orientation = self.pdf_handler.get_page_orientation(0) # Get orientation of first page
                self.page_size_handler.set_page_orientation(initial_orientation)
                
                # 更新UI中的方向选择
                # Find the index of the initial_orientation in the combo box data
                index = self.orientation_combo.findData(initial_orientation)
                if index != -1:
                    self.orientation_combo.setCurrentIndex(index)

                # 刷新显示
                if self.fit_to_window_active:
                    self._calculate_and_apply_fit_to_window_scale()
                else:
                    self.display_refresher.refresh_display(self.current_page, 1.0)                
                self.print_button.setEnabled(True)
                self.print_preview_button.setEnabled(True)
                self.prev_button.setEnabled(True)
                self.next_button.setEnabled(True)
                
                # 更新页面信息和滚动条
                self.update_page_info()
            else:
                QMessageBox.critical(self, "错误", "无法加载PDF文件")
    
    def update_page_info(self):
        """更新页面信息和滚动条"""
        if self.pdf_handler.get_page_count() > 0:
            if self.layout_handler.adaptive_mode:
                # 计算自适应布局的页数
                total_pages = (self.pdf_handler.get_page_count() + self.layout_handler.pages_per_sheet - 1) // self.layout_handler.pages_per_sheet  # 根据每页页面数计算
                current_group = (self.current_page // self.layout_handler.pages_per_sheet) + 1
                self.page_info_label.setText(f"第 {current_group} 页，共 {total_pages} 页")
                
                # 更新滚动条
                self.page_scrollbar.setMaximum(max(0, total_pages - 1))
                self.page_scrollbar.setValue(current_group - 1)
            else:
                self.page_info_label.setText(f"第 {self.current_page + 1} 页，共 {self.pdf_handler.get_page_count()} 页")
                
                # 更新滚动条
                self.page_scrollbar.setMaximum(max(0, self.pdf_handler.get_page_count() - 1))
                self.page_scrollbar.setValue(self.current_page)
            
            # 更新按钮状态
            self.update_button_state()
    
    def update_button_state(self):
        """更新按钮状态"""
        if self.layout_handler.adaptive_mode:
            total_pages = (self.pdf_handler.get_page_count() + self.layout_handler.pages_per_sheet - 1) // self.layout_handler.pages_per_sheet  # 根据每页页面数计算
            current_group = self.current_page // self.layout_handler.pages_per_sheet
            self.prev_button.setEnabled(current_group > 0)
            self.next_button.setEnabled(current_group < total_pages - 1)
        else:
            self.prev_button.setEnabled(self.current_page > 0)
            self.next_button.setEnabled(self.current_page < self.pdf_handler.get_page_count() - 1)
    
    def zoom_changed(self, index):
        """处理缩放选项变化"""
        zoom_value = self.zoom_combo.currentData()
        
        if zoom_value == -1:  # 自定义选项
            self.custom_zoom_input.setVisible(True)
            self.custom_zoom_input.setFocus()
        else:
            self.custom_zoom_input.setVisible(False)
            self.scaling_handler.set_scale_factor(zoom_value)
            self.fit_to_window_active = False # Deactivate fit to window
            self.display_refresher.refresh_display(self.current_page, 1.0)
            # 更新页面信息
            self.update_page_info()
    
    def custom_zoom_entered(self):
        """处理自定义缩放值输入"""
        try:
            zoom_value = float(self.custom_zoom_input.text())
            if zoom_value > 0:
                # 设置缩放因子（转换为小数形式）
                self.scaling_handler.set_scale_factor(zoom_value / 100.0)
                self.fit_to_window_active = False # Deactivate fit to window
                self.display_refresher.refresh_display(self.current_page, 1.0)
                # 更新页面信息
                self.update_page_info()
            else:
                QMessageBox.warning(self, "无效输入", "缩放比例必须大于0")
        except ValueError:
            QMessageBox.warning(self, "无效输入", "请输入有效的数字")
    
    def rotate_changed(self, index):
        self.scaling_handler.set_rotation_angle(self.rotate_combo.currentData())
        if self.fit_to_window_active:
            self._calculate_and_apply_fit_to_window_scale()
        else:
            self.display_refresher.refresh_display(self.current_page, 1.0)
        # 更新页面信息
        self.update_page_info()
    
    def size_changed(self, index):
        self.page_size_handler.set_page_size(self.size_combo.currentData())
        self.print_handler.set_page_size(self.size_combo.currentData())
        if self.fit_to_window_active:
            self._calculate_and_apply_fit_to_window_scale()
        else:
            self.display_refresher.refresh_display(self.current_page, 1.0)
        # 更新页面信息
        self.update_page_info()
    
    def adaptive_mode_changed(self, state):
        self.layout_handler.set_adaptive_mode(state == Qt.Checked)
        if self.fit_to_window_active:
            self._calculate_and_apply_fit_to_window_scale()
        else:
            self.display_refresher.refresh_display(self.current_page, 1.0)
        # 更新页面信息
        self.update_page_info()
    
    def orientation_changed(self, index):
        orientation = self.orientation_combo.currentData()
        self.page_size_handler.set_page_orientation(orientation)
        self.print_handler.set_page_orientation(orientation)
        if self.fit_to_window_active:
            self._calculate_and_apply_fit_to_window_scale()
        else:
            self.display_refresher.refresh_display(self.current_page, 1.0)
        # 更新页面信息
        self.update_page_info()
    
    def pages_per_sheet_changed(self, index):
        self.layout_handler.set_pages_per_sheet(self.pages_per_sheet_combo.currentData())
        if self.fit_to_window_active:
            self._calculate_and_apply_fit_to_window_scale()
        else:
            self.display_refresher.refresh_display(self.current_page, 1.0)
        # 更新页面信息（页面数量可能已改变）
        self.update_page_info()
    
    def prev_page(self):
        if self.layout_handler.adaptive_mode:
            # 自适应布局的上一页
            current_group = self.current_page // self.layout_handler.pages_per_sheet
            if current_group > 0:
                self.current_page = (current_group - 1) * self.layout_handler.pages_per_sheet
                if self.fit_to_window_active:
                    self._calculate_and_apply_fit_to_window_scale()
                else:
                    self.display_refresher.refresh_display(self.current_page, 1.0)
        else:
            # 单页布局的上一页
            if self.current_page > 0:
                self.current_page -= 1
                self.display_refresher.refresh_display(self.current_page, 1.0)
        
        # 更新页面信息
        self.update_page_info()
    
    def scrollbar_changed(self, value):
        """处理滚动条值变化"""
        if self.pdf_handler.get_page_count() > 0:
            if self.layout_handler.adaptive_mode:
                # 自适应模式下，按组计算
                total_pages = (self.pdf_handler.get_page_count() + self.layout_handler.pages_per_sheet - 1) // self.layout_handler.pages_per_sheet
                if total_pages > 0:
                    # 计算目标组
                    target_group = value
                    self.current_page = target_group * self.layout_handler.pages_per_sheet
            else:
                # 单页模式下，直接设置页面
                self.current_page = value
            
            if self.fit_to_window_active:
                self._calculate_and_apply_fit_to_window_scale()
            else:
                self.display_refresher.refresh_display(self.current_page, 1.0)
            # 更新按钮状态
            self.update_button_state()
    
    def next_page(self):
        if self.layout_handler.adaptive_mode:
            # 自适应布局的下一页
            current_group = self.current_page // self.layout_handler.pages_per_sheet
            total_pages = (self.pdf_handler.get_page_count() + self.layout_handler.pages_per_sheet - 1) // self.layout_handler.pages_per_sheet  # 根据每页页面数计算
            if current_group < total_pages - 1:
                self.current_page = (current_group + 1) * self.layout_handler.pages_per_sheet
                if self.fit_to_window_active:
                    self._calculate_and_apply_fit_to_window_scale()
                else:
                    self.display_refresher.refresh_display(self.current_page, 1.0)
        else:
            # 单页布局的下一页
            if self.pdf_handler.get_page_count() > 0 and self.current_page < self.pdf_handler.get_page_count() - 1:
                self.current_page += 1
                self.display_refresher.refresh_display(self.current_page, 1.0)
        
        # 更新页面信息
        self.update_page_info()

    def print_pdf(self):
        if self.pdf_handler.get_page_count() > 0:
            # 直接打印
            self._direct_print()

    def print_preview(self):
        """打印预览功能"""
        if self.pdf_handler.get_page_count() > 0:
            preview_dialog = QPrintPreviewDialog()
            preview_dialog.paintRequested.connect(self._preview_paint_requested)
            preview_dialog.exec_()

    def _preview_paint_requested(self, printer):
        """处理打印预览的绘制请求"""
        # 配置打印机
        self.print_handler.configure_printer(printer)
        
        # 开始绘制
        painter = QPainter(printer)
        
        # 获取页面尺寸
        page_rect = printer.pageRect()
        target_width = page_rect.width()
        target_height = page_rect.height()
        
        # 根据页面方向调整目标尺寸
        if self.pdf_handler.get_page_count() > 0:
            pdf_width, pdf_height = self.pdf_handler.get_page_size(0)
            target_width, target_height = self.page_size_handler.adjust_dimensions_for_orientation(
                target_width, target_height, pdf_width, pdf_height)
        
        # 绘制页面
        total_pages = self.pdf_handler.get_page_count()
        pages_per_sheet = self.layout_handler.pages_per_sheet
        total_layout_pages = (total_pages + pages_per_sheet - 1) // pages_per_sheet
        
        for layout_page_index in range(total_layout_pages):
            if layout_page_index > 0:
                printer.newPage()
            
            start_pdf_page = layout_page_index * pages_per_sheet
            remaining_pages = total_pages - start_pdf_page
            page_count = min(pages_per_sheet, remaining_pages)
            
            # 绘制页面（使用缩放）
            self.layout_handler.draw_adaptive_pages(
                painter, self.pdf_handler, self.scaling_handler,
                target_width, target_height, start_pdf_page, page_count)
        
        painter.end()

    def _direct_print(self):
        """直接打印功能"""
        printer = QPrinter(QPrinter.HighResolution)
        print_dialog = QPrintDialog(printer, self)
        self.print_handler.configure_printer(printer)
        
        if print_dialog.exec_() == QPrintDialog.Accepted:


            # 创建进度条
            total_pages = self.pdf_handler.get_page_count()
            pages_per_sheet = self.layout_handler.pages_per_sheet
            total_layout_pages = (total_pages + pages_per_sheet - 1) // pages_per_sheet
            
            self.print_progress.setVisible(True)
            self.print_progress.setRange(0, total_layout_pages)
            self.print_progress.setValue(0)
            
            # 使用 QTimer 来确保 UI 更新
            QTimer.singleShot(100, lambda: self._print_pages(printer, total_layout_pages))

    def _print_pages(self, printer, total_layout_pages):
        """实际打印页面"""
        try:
            page_rect = printer.pageRect()


            painter = QPainter(printer)

            total_pages = self.pdf_handler.get_page_count()
            pages_per_sheet = self.layout_handler.pages_per_sheet

            for layout_page_index in range(total_layout_pages):
                # 更新进度条
                self.print_progress.setValue(layout_page_index + 1)
                QApplication.processEvents()  # 确保 UI 更新

                if layout_page_index > 0:
                    printer.newPage()

                # 使用打印机的pageRect创建pixmap以确保分辨率
                pixmap = QPixmap(page_rect.size())

                pixmap.fill(Qt.white)

                pixmap_painter = QPainter(pixmap)
                target_width = pixmap.width()
                target_height = pixmap.height()

                # 根据页面方向调整目标尺寸
                if self.pdf_handler.get_page_count() > 0:
                    pdf_width, pdf_height = self.pdf_handler.get_page_size(0)
                    target_width, target_height = self.page_size_handler.adjust_dimensions_for_orientation(
                        target_width, target_height, pdf_width, pdf_height)

                start_pdf_page = layout_page_index * pages_per_sheet
                remaining_pages = total_pages - start_pdf_page
                page_count = min(pages_per_sheet, remaining_pages)

                # 打印时使用缩放
                self.layout_handler.draw_adaptive_pages(
                    pixmap_painter, self.pdf_handler, self.scaling_handler, 
                    target_width, target_height, start_pdf_page, page_count)

                pixmap_painter.end()

                # 将高分辨率pixmap绘制到打印机
                painter.drawPixmap(0, 0, pixmap)

            painter.end()
            
            # 隐藏进度条
            self.print_progress.setVisible(False)
            QMessageBox.information(self, "打印", "打印完成！") # Display completion message
            
        except Exception as e:
            # 隐藏进度条
            self.print_progress.setVisible(False)
            logging.error(f"打印过程中出错: {str(e)}")
            QMessageBox.critical(self, "打印错误", f"打印过程中出错: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFPrinterApp()
    window.show()
    sys.exit(app.exec_())