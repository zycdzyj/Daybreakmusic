import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QRect, Property
from PySide6.QtGui import QPainter, QFont, QColor


class AnimatedLabel(QLabel):
    def __init__(self, text="", *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self._tilt = -45.0      # 启动时左倾斜45度（修改为向左倾斜）
        self._rotation = 0.0    # 绕Z轴旋转
        self.text_content = text
        self.setFixedSize(300, 100)

    def get_tilt(self):
        return self._tilt

    def set_tilt(self, value):
        self._tilt = value
        self.update()

    def get_rotation(self):
        return self._rotation

    def set_rotation(self, value):
        self._rotation = value
        self.update()

    tilt = Property(float, get_tilt, set_tilt)
    rotation = Property(float, get_rotation, set_rotation)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        center_x, center_y = w / 2, h / 2

        # 左倾斜，使用左边为轴旋转效果（绕Y轴）
        tilt_rad = self._tilt * 3.14159 / 180
        shear_x = 0.0  # 不使用斜切，直接通过旋转来实现左倾斜

        # 平移到中心
        painter.translate(center_x, center_y)
        
        # 向左倾斜（绕Y轴旋转）
        painter.rotate(self._tilt)  # 以窗口左边为轴，向左倾斜
        
        # 平移回左上角绘制内容
        painter.translate(-w / 2, -h / 2)

        # 绘制圆角矩形背景
        painter.setBrush(QColor("#50c878"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, w, h, 15, 15)  # 注意：不需要反缩放

        # 绘制文字（居中）
        painter.setPen(Qt.white)
        font = QFont("Arial", 22)
        painter.setFont(font)
        text_rect = QRect(0, 0, w, h)  # 垂直居中补偿
        painter.drawText(text_rect, Qt.AlignCenter, self.text_content)

        painter.end()


class AnimatedWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("左倾斜+跳跃旋转")
        self.resize(400, 300)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignCenter)

        self.content_label = AnimatedLabel("✨ 动画窗口 ✨")
        layout.addWidget(self.content_label)

        self.setWindowOpacity(0.0)
        QTimer.singleShot(50, self.start_animation)

    def start_animation(self):
        x, y = self.x(), self.y()
        w, h = self.width(), self.height()

        # 淡入
        self.anim_opacity = QPropertyAnimation(self, b"windowOpacity")
        self.anim_opacity.setDuration(600)  # 更快的淡入效果
        self.anim_opacity.setStartValue(0.0)
        self.anim_opacity.setEndValue(1.0)
        self.anim_opacity.setEasingCurve(QEasingCurve.InQuad)

        # 计算跳跃和倾斜的同步动画（使用QPropertyAnimation控制位置和角度）
        self.anim_jump_and_tilt = QPropertyAnimation(self, b"geometry")
        self.anim_jump_and_tilt.setDuration(600)  # 更快的跳跃动画
        self.anim_jump_and_tilt.setStartValue(QRect(x, y, w, h))
        self.anim_jump_and_tilt.setKeyValueAt(0.4, QRect(x, y - 25, w, h))  # 跳跃到上方
        self.anim_jump_and_tilt.setEndValue(QRect(x, y, w, h))  # 跳跃回原位置
        self.anim_jump_and_tilt.setEasingCurve(QEasingCurve.OutInQuad)

        # 将“倾斜”从-45° → 0°（同时进行）加速动画
        self.anim_tilt = QPropertyAnimation(self.content_label, b"tilt")
        self.anim_tilt.setDuration(600)  # 更快的倾斜动画
        self.anim_tilt.setStartValue(-45.0)
        self.anim_tilt.setEndValue(0.0)
        self.anim_tilt.setEasingCurve(QEasingCurve.OutQuad)

        # 启动所有动画
        self.anim_opacity.start()
        self.anim_jump_and_tilt.start()
        self.anim_tilt.start()

        QTimer.singleShot(700, self.jump_and_rotate)

    def jump_and_rotate(self):
        x, y = self.x(), self.y()
        w, h = self.width(), self.height()

        # 水平旋转（绕Z轴）从-45°旋转回0°（水平位置）
        self.anim_rotate = QPropertyAnimation(self.content_label, b"rotation")
        self.anim_rotate.setDuration(500)  # 更快的旋转动画
        self.anim_rotate.setStartValue(-45)
        self.anim_rotate.setEndValue(0)
        self.anim_rotate.setEasingCurve(QEasingCurve.OutQuint)
        self.anim_rotate.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnimatedWindow()
    window.show()
    sys.exit(app.exec())