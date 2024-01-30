from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QRectF, Qt, pyqtSignal, QSize, QRect
from PyQt5.QtGui import QPainter, QPen, QFont, QColor
import sys

class CircularProgressBar(QWidget):
    # Create a signal to emit when the value changes
    valueChanged = pyqtSignal(int)

    def __init__(self, time_required,parent=None):
        super().__init__(parent)
        self.value = 0
        self.setMaximumWidth(200)
        self.setMaximumHeight(200)
        self.maxValue = time_required
    
    def sizeHint(self):
        return QSize(200, 200)  # Provide a default size

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate the size for the circle and the position
        lineWidth = 5
        padding = 10
        diameter = min(self.width(), self.height()) - 2 * padding
        x = (self.width() - diameter) // 2
        y = (self.height() - diameter) // 2
        rect = QRect(x, y, diameter, diameter)

        # Draw the background circle
        background_pen = QPen(Qt.gray, lineWidth)
        background_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(background_pen)
        painter.drawEllipse(rect)

        # Draw the progress arc
        full_circle = 360 * 16
        span_angle = int((self.value / self.maxValue) * full_circle)
        start_angle = 90 * 16
        progress_pen = QPen(Qt.green, lineWidth)
        progress_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(progress_pen)
        painter.drawArc(rect, start_angle, -span_angle)

        # Draw the percentage text
        percentage_filled = (self.value / self.maxValue) * 100
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(Qt.white)
        painter.drawText(rect, Qt.AlignCenter, f"{percentage_filled:.0f}%")

    def setValue(self, value):
        # Ensure value is between 0 and 3000
        self.value = max(0, min(self.maxValue, value))
        self.update()  # Trigger a repaint
    def reset(self):
        self.value = 0
        