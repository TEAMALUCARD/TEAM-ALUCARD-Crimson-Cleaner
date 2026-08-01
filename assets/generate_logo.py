"""
Generates the temporary Crimson Cleaner emblem asset (assets/logo.png).
"""
from pathlib import Path
from PySide6.QtGui import QImage, QPainter, QColor, QLinearGradient, QPen, QBrush, QPainterPath
from PySide6.QtCore import Qt

def generate_logo(output_path: Path, size: int = 256) -> None:
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)

    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Background Crimson Glow Gradient Shield / Hexagon
    rect_margin = size * 0.08
    center = size / 2

    # Draw Outer Hexagonal Shield
    path = QPainterPath()
    angle = 60
    import math
    radius = (size / 2) - rect_margin
    for i in range(6):
        rad = math.radians(i * angle - 30)
        x = center + radius * math.cos(rad)
        y = center + radius * math.sin(rad)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.closeSubpath()

    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0.0, QColor("#FF2E55"))  # Vivid Crimson Red
    grad.setColorAt(0.5, QColor("#DC143C"))  # Crimson
    grad.setColorAt(1.0, QColor("#800020"))  # Dark Burgundy Red

    painter.setBrush(QBrush(grad))
    pen = QPen(QColor("#FF4D6D"), 4)
    painter.setPen(pen)
    painter.drawPath(path)

    # Draw Inner Glowing Crimson 'C' / Flame Motif
    inner_path = QPainterPath()
    inner_path.moveTo(center + size * 0.15, center - size * 0.2)
    inner_path.cubicTo(
        center - size * 0.3, center - size * 0.3,
        center - size * 0.3, center + size * 0.3,
        center + size * 0.15, center + size * 0.2
    )
    inner_pen = QPen(
        QColor("#FFFFFF"),
        size * 0.08,
        Qt.PenStyle.SolidLine,
        Qt.PenCapStyle.RoundCap,
        Qt.PenJoinStyle.RoundJoin,
    )
    painter.setPen(inner_pen)
    painter.drawPath(inner_path)

    # Draw Center Accent Spark / Crystal
    spark = QPainterPath()
    spark.moveTo(center + size * 0.08, center)
    spark.lineTo(center + size * 0.2, center - size * 0.08)
    spark.lineTo(center + size * 0.28, center)
    spark.lineTo(center + size * 0.2, center + size * 0.08)
    spark.closeSubpath()

    painter.setBrush(QBrush(QColor("#FFD700")))  # Gold Accent
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawPath(spark)

    painter.end()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "PNG")
    print(f"Logo generated successfully at: {output_path}")

if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "logo.png"
    generate_logo(out)
