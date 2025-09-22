from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter


class ScalingHandler:
    """处理缩放功能的类 v2.0"""
    
    def __init__(self):
        self.scale_factor = 1.0
        self.rotation_angle = 0
    
    def set_scale_factor(self, scale_factor):
        """设置缩放因子"""
        self.scale_factor = scale_factor
    
    def set_rotation_angle(self, angle):
        """设置旋转角度"""
        self.rotation_angle = angle
    