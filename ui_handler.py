import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                             QPushButton, QComboBox, QCheckBox, QSlider, 
                             QVBoxLayout, QHBoxLayout, QScrollArea, QGroupBox,
                             QFileDialog, QMessageBox, QProgressDialog, QSpinBox,
                             QDoubleSpinBox, QStackedWidget, QLineEdit, QSizePolicy,
                             QProgressBar)
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap

class UIHandler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # 设置窗口属性
        self.setWindowTitle("PDF Printer v2.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # 初始化所有控件
        self.load_button = QPushButton("加载PDF")
        self.fit_to_window_button = QPushButton("适应窗口")  # 移动到这里
        self.fit_to_window_button.setToolTip("调整页面大小以适应当前窗口")
        self.print_button = QPushButton("打印")
        self.print_button.setEnabled(False)
        self.print_preview_button = QPushButton("打印预览")
        self.print_preview_button.setEnabled(False)
        self.print_progress = QProgressBar() # Initialize print_progress here
        self.print_progress.setVisible(False) # Set initial visibility here
        
        self.zoom_combo = QComboBox()
        zoom_options = [
            ("25%", 0.25),
            ("50%", 0.5),
            ("75%", 0.75),
            ("100%", 1.0),
            ("125%", 1.25),
            ("150%", 1.5),
            ("200%", 2.0),
            ("自定义", -1)  # -1表示自定义
        ]
        for text, value in zoom_options:
            self.zoom_combo.addItem(text, value)
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.setFixedWidth(100)  # 设置固定宽度
        
        self.custom_zoom_input = QLineEdit("100")
        self.custom_zoom_input.setFixedWidth(60)
        self.custom_zoom_input.setVisible(False)
        
        self.rotate_combo = QComboBox()
        self.rotate_combo.addItem("0°", 0)
        self.rotate_combo.addItem("90°", 90)
        self.rotate_combo.addItem("180°", 180)
        self.rotate_combo.addItem("270°", 270)
        self.rotate_combo.setFixedWidth(100)  # 设置固定宽度与缩放下拉框一致
        
        self.size_combo = QComboBox()
        sizes = ["A0", "A1", "A2", "A3", "A4", "A5", "A6", "Letter", "Legal", "Tabloid"]
        for size in sizes:
            self.size_combo.addItem(size, size)
        self.size_combo.setCurrentText("A4")
        
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItem("纵向", "portrait")
        self.orientation_combo.addItem("横向", "landscape")
        
        self.pages_per_sheet_combo = QComboBox()
        pages_per_sheet_options = [1, 2, 4, 6, 9, 16]
        for count in pages_per_sheet_options:
            self.pages_per_sheet_combo.addItem(f"{count}页/张", count)
        self.pages_per_sheet_combo.setCurrentText("1页/张")
        
        self.adaptive_checkbox = QCheckBox("自适应模式")
        self.adaptive_checkbox.setChecked(True)  # 默认勾选自适应模式
        
        self.prev_button = QPushButton("上一页")
        self.prev_button.setEnabled(False)
        
        self.next_button = QPushButton("下一页")
        self.next_button.setEnabled(False)
        
        self.page_info_label = QLabel("第 0 页，共 0 页")
        
        self.page_scrollbar = QSlider(Qt.Horizontal)
        self.page_scrollbar.setRange(0, 0)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局（垂直布局，包含左右布局和导航面板）
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)  # 设置控件间距
        main_layout.setContentsMargins(10, 10, 10, 10)  # 设置边距
        
        # 创建左右布局
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setSpacing(10)
        
        # 创建控制面板区域（左侧）
        control_panel = self.create_control_panel()
        horizontal_layout.addLayout(control_panel, 1)  # 左侧占1份空间
        
        # 创建右侧区域（包含页面显示和导航面板）
        right_layout = QVBoxLayout()
        right_layout.setSpacing(5)
        
        # 创建页面显示区域
        page_display = self.create_page_display()
        right_layout.addLayout(page_display, 1)  # 占据大部分空间
        
        # 创建导航面板
        navigation_panel = self.create_navigation_panel()
        right_layout.addLayout(navigation_panel)
        
        horizontal_layout.addLayout(right_layout, 3)  # 右侧占3份空间
        
        main_layout.addLayout(horizontal_layout)
        
    def create_control_panel(self):
        # 控制面板布局（垂直布局）
        control_layout = QVBoxLayout()
        control_layout.setSpacing(10)  # 设置控件间距
        
        # 文件操作组
        file_group = QGroupBox("文件操作")
        file_layout = QVBoxLayout(file_group)
        
        # New horizontal layout for load and fit_to_window buttons
        load_fit_layout = QHBoxLayout()
        load_fit_layout.addWidget(self.load_button)
        load_fit_layout.addWidget(self.fit_to_window_button)
        file_layout.addLayout(load_fit_layout) # Add the horizontal layout to the vertical file_layout
        
        file_layout.addWidget(self.print_preview_button)
        self.print_button.setText("直接打印")
        file_layout.addWidget(self.print_button)
        
        # 缩放组
        zoom_group = QGroupBox("缩放")
        zoom_layout = QVBoxLayout(zoom_group)
        
        # 第一行：缩放控件
        zoom_row1 = QHBoxLayout()
        self.zoom_combo = QComboBox()
        zoom_options = [
            ("25%", 0.25),
            ("50%", 0.5),
            ("75%", 0.75),
            ("100%", 1.0),
            ("125%", 1.25),
            ("150%", 1.5),
            ("200%", 2.0),
            ("自定义", -1)  # -1表示自定义
        ]
        for text, value in zoom_options:
            self.zoom_combo.addItem(text, value)
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.setFixedWidth(100)  # 设置固定宽度
        
        self.custom_zoom_input = QLineEdit("100")
        self.custom_zoom_input.setFixedWidth(60)
        self.custom_zoom_input.setVisible(False)
        self.custom_zoom_input.setValidator(QDoubleValidator(0.1, 10000.0, 2))  # 允许输入0.1到10000.0之间的数字，最多2位小数
        
        zoom_row1.addWidget(QLabel("缩放:"))
        zoom_row1.addWidget(self.zoom_combo)
        zoom_row1.addWidget(self.custom_zoom_input)
        zoom_row1.addWidget(QLabel("%"))
        zoom_row1.addStretch()  # 添加弹性空间
        
        # 第二行：空行保持布局一致性
        zoom_row2 = QHBoxLayout()
        zoom_row2.addStretch()
        
        zoom_layout.addLayout(zoom_row1)
        zoom_layout.addLayout(zoom_row2)
        
        # 旋转组
        rotate_group = QGroupBox("旋转")
        rotate_layout = QHBoxLayout(rotate_group)
        
        self.rotate_combo = QComboBox()
        self.rotate_combo.addItem("0°", 0)
        self.rotate_combo.addItem("90°", 90)
        self.rotate_combo.addItem("180°", 180)
        self.rotate_combo.addItem("270°", 270)
        self.rotate_combo.setFixedWidth(100)  # 设置固定宽度与缩放下拉框一致
        
        rotate_layout.addWidget(QLabel("旋转:"))
        rotate_layout.addWidget(self.rotate_combo)
        rotate_layout.addStretch()  # 添加弹性空间
        
        # 页面设置组
        page_group = QGroupBox("页面设置")
        page_layout = QVBoxLayout(page_group)  # 改为垂直布局以容纳更多控件
        
        # 第一行：页面尺寸和方向
        page_row1 = QHBoxLayout()
        page_row1.addWidget(QLabel("页面尺寸:"))
        page_row1.addWidget(self.size_combo)
        page_row1.addWidget(QLabel("页面方向:"))
        page_row1.addWidget(self.orientation_combo)
        
        # 第二行：每张页数和自适应模式
        page_row2 = QHBoxLayout()
        page_row2.addWidget(QLabel("每张页数:"))
        page_row2.addWidget(self.pages_per_sheet_combo)
        page_row2.addWidget(self.adaptive_checkbox)
        page_row2.addStretch()  # 添加弹性空间
        
        page_layout.addLayout(page_row1)
        page_layout.addLayout(page_row2)
        
        # 添加到控制布局
        control_layout.addWidget(file_group)
        control_layout.addWidget(zoom_group)
        control_layout.addWidget(rotate_group)
        control_layout.addWidget(page_group)
        
        # 添加进度条组
        progress_group = QGroupBox("打印进度")
        progress_layout = QHBoxLayout(progress_group)
        progress_layout.addWidget(self.print_progress)
        control_layout.addWidget(progress_group)
        
        # 添加弹性空间
        control_layout.addStretch()
        
        return control_layout
        
    def create_page_display(self):
        # 页面显示布局
        display_layout = QVBoxLayout()
        display_layout.setSpacing(5)  # 设置控件间距
        display_layout.setContentsMargins(5, 5, 5, 5)  # 设置边距
        
        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)  # 移除边框以获得更好的外观
        
        # 创建页面标签
        self.page_label = QLabel("请加载PDF文件")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setMinimumSize(400, 600)
        self.page_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.scroll_area.setWidget(self.page_label)
        display_layout.addWidget(self.scroll_area)
        
        # 设置滚动区域的尺寸策略
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        return display_layout
        
    def create_navigation_panel(self):
        # 导航面板布局（垂直布局）
        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(5)  # 设置控件间距
        
        # 第一行：上一页、下一页和页码计数（居中对齐）
        row1_layout = QHBoxLayout()
        row1_layout.addStretch()  # 左侧弹性空间
        row1_layout.addWidget(self.prev_button)
        row1_layout.addWidget(self.next_button)
        row1_layout.addWidget(self.page_info_label)
        row1_layout.addStretch()  # 右侧弹性空间
        
        # 第二行：滑动条
        row2_layout = QHBoxLayout()
        row2_layout.addWidget(QLabel("页面:"))
        row2_layout.addWidget(self.page_scrollbar)
        
        nav_layout.addLayout(row1_layout)
        nav_layout.addLayout(row2_layout)
        
        return nav_layout