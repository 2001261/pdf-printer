class DisplayRefresher:
    """负责刷新显示的模块 v2.0"""
    
    def __init__(self, pdf_handler, scaling_handler, page_size_handler, 
                 layout_handler, display_handler, print_handler):
        self.pdf_handler = pdf_handler
        self.scaling_handler = scaling_handler
        self.page_size_handler = page_size_handler
        self.layout_handler = layout_handler
        self.display_handler = display_handler
        self.print_handler = print_handler
        
    def refresh_display(self, current_page, display_scale_factor=1.0):
        # Set the display_scale_factor in display_handler
        self.display_handler.display_scale_factor = display_scale_factor

        if self.pdf_handler.get_page_count() == 0:
            self.display_handler.page_label.clear()
            return

        if self.layout_handler.adaptive_mode:
            self.display_handler.display_adaptive_pages(current_page)
        else:
            self.display_handler.display_single_page(current_page)
                
    def refresh_all(self, current_page=0):
        """刷新所有相关组件"""
        # 刷新显示
        self.refresh_display(current_page)
        
        # 刷新打印设置
        self.print_handler.set_page_size(self.page_size_handler.page_size)
        self.print_handler.set_page_orientation(self.page_size_handler.page_orientation)