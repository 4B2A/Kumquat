import sys, os
from pathlib import Path
from PyQt6.QtCore import Qt, QRect, QSize, QPoint
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QShortcut, QKeySequence
from PIL import Image, ImageFilter


class Kumquat(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kumquat — Cozy Blur")
        self.setFixedSize(QSize(950, 730))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.img_path, self.display_pixmap, self.is_selecting = None, None, False
        self.start_p, self.end_p, self.sel_rect = None, None, QRect()
        self.drag_pos, self.mode = QPoint(), "blur"
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget#main { background-color: #F5F7FB; border: 1px solid #D9E2EC; border-radius: 20px; }
            QWidget#title { background-color: #EBF1FA; border-top-left-radius: 19px; border-top-right-radius: 19px; }
            QLabel#t_lbl { color: #5B4E77; font-family: -apple-system, sans-serif; font-size: 13px; font-weight: 600; }
            QPushButton#close { background-color: #FF605C; border: none; border-radius: 6px; max-width: 12px; max-height: 12px; min-width: 12px; min-height: 12px; }
            QLabel#canvas { background-color: #FAF7FF; border: 2px dashed #DCD0FF; border-radius: 24px; color: #5B4E77; font-family: -apple-system, sans-serif; font-size: 16px; }
            QLabel#status { color: #7C6E9F; font-family: -apple-system, sans-serif; font-size: 13px; font-weight: 500; }
            QPushButton.m_btn { background-color: #E6EEF8; border: 1px solid #D0E1F9; border-radius: 12px; color: #4A5568; font-family: -apple-system, sans-serif; font-size: 13px; font-weight: 600; padding: 8px 18px; min-width: 100px; }
            QPushButton.m_btn:hover { background-color: #F3E8FF; border-color: #E9D5FF; color: #6B46C1; }
            QPushButton#active { background-color: #E9D5FF; border-color: #D6BCFA; color: #553C9A; }
        """)

        # Pencere Düzeni
        root = QVBoxLayout(main := QWidget())
        main.setObjectName("main")
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setCentralWidget(main)

        # macOS Tarzı Custom Title Bar
        title = QWidget()
        title.setObjectName("title")
        title.setFixedHeight(40)
        t_lay = QHBoxLayout(title)
        t_lay.setContentsMargins(15, 0, 15, 0)
        close = QPushButton()
        close.setObjectName("close")
        close.clicked.connect(self.close)
        t_lbl = QLabel("Kumquat — Cozy Blur")
        t_lbl.setObjectName("t_lbl")
        t_lay.addWidget(close)
        t_lay.addStretch()
        t_lay.addWidget(t_lbl)
        t_lay.addStretch()
        t_lay.addSpacing(12)
        title.mousePressEvent = lambda e: (
            setattr(
                self,
                "drag_pos",
                e.globalPosition().toPoint() - self.frameGeometry().topLeft(),
            )
            if e.button() == Qt.MouseButton.LeftButton
            else None
        )
        title.mouseMoveEvent = lambda e: (
            self.move(e.globalPosition().toPoint() - self.drag_pos)
            if e.buttons() == Qt.MouseButton.LeftButton
            else None
        )
        root.addWidget(title)

        # İçerik Alanı
        box = QVBoxLayout(content := QWidget())
        box.setContentsMargins(30, 20, 30, 25)
        menu = QHBoxLayout()
        menu.setSpacing(14)

        self.btns = {
            "blur": QPushButton("💧 Yumuşak Blur"),
            "pixel": QPushButton("🧱 Mozaik"),
            "solid": QPushButton("⬛ Siyah Bant"),
        }
        for k, btn in self.btns.items():
            btn.setProperty("class", "m_btn")
            if k == "blur":
                btn.setObjectName("active")
            btn.clicked.connect(lambda ch, m=k, b=btn: self.change_mode(m, b))
            menu.addWidget(btn)

        menu.addStretch()
        box.addLayout(menu)
        box.addSpacing(10)

        # Fotoğraf Alanı
        self.canvas = QLabel(
            '<div style="text-align:center;"><span style="font-size:48px;">🍊</span><br><br><b style="color:#6B46C1;">Fotoğrafı buraya sürükle bırak</b></div>'
        )
        self.canvas.setObjectName("canvas")
        self.canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas.setAcceptDrops(True)
        self.canvas.dragEnterEvent = lambda e: (
            e.acceptProposedAction() if e.mimeData().hasUrls() else None
        )
        self.canvas.dropEvent = self.handle_drop
        self.canvas.mousePressEvent = self.start_sel
        self.canvas.mouseMoveEvent = self.move_sel
        self.canvas.mouseReleaseEvent = self.end_sel
        self.canvas.paintEvent = self.draw_overlay

        self.status = QLabel(
            "✨ Kumquat parmaklarının ucunda. Başlamak için bir fotoğraf bırak."
        )
        self.status.setObjectName("status")

        box.addWidget(self.canvas, stretch=1)
        box.addSpacing(15)
        box.addWidget(self.status)
        root.addWidget(content)
        QShortcut(QKeySequence(Qt.Key.Key_S), self, self.blur_and_save)

    def change_mode(self, mode, button):
        self.mode = mode
        for btn in self.btns.values():
            btn.setObjectName("") or btn.style().unpolish(btn) or btn.style().polish(
                btn
            )
        button.setObjectName("active") or button.style().unpolish(
            button
        ) or button.style().polish(button)

    def load_image(self, path):
        self.img_path = path
        self.display_pixmap = QPixmap(path).scaled(
            self.canvas.size() - QSize(16, 16),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.canvas.setPixmap(self.display_pixmap)
        self.canvas.setCursor(Qt.CursorShape.CrossCursor)
        self.canvas.setStyleSheet(
            "background-color: #FFFFFF; border: 2px solid #E9D5FF; border-radius: 24px;"
        )
        self.status.setText(
            f"📁 {os.path.basename(path)} yüklendi. Alanı seç ve 'S' tuşuna bas."
        )
        self.sel_rect = QRect()

    def handle_drop(self, event):
        for url in event.mimeData().urls():
            if (
                (path := url.toLocalFile())
                .lower()
                .endswith((".png", ".jpg", ".jpeg", ".webp"))
            ):
                self.load_image(path)
                break

    def start_sel(self, event):
        if self.display_pixmap and event.button() == Qt.MouseButton.LeftButton:
            self.start_p = self.end_p = event.pos()
            self.is_selecting = True
            self.sel_rect = QRect()

    def move_sel(self, event):
        if self.is_selecting:
            self.end_p = event.pos()
            self.canvas.update()

    def end_sel(self, event):
        if self.is_selecting and event.button() == Qt.MouseButton.LeftButton:
            self.is_selecting = False
            if not self.canvas.pixmap():
                return
            px, cx = self.canvas.pixmap().rect(), self.canvas.rect()
            ox, oy = (cx.width() - px.width()) // 2, (cx.height() - px.height()) // 2
            x1, y1 = (
                max(ox, min(self.start_p.x(), self.end_p.x())),
                max(oy, min(self.start_p.y(), self.end_p.y())),
            )
            x2, y2 = (
                min(ox + px.width(), max(self.start_p.x(), self.end_p.x())),
                min(oy + px.height(), max(self.start_p.y(), self.end_p.y())),
            )
            if x2 > x1 and y2 > y1:
                self.sel_rect = QRect(x1, y1, x2 - x1, y2 - y1)
            self.canvas.update()

    def draw_overlay(self, event):
        QLabel.paintEvent(self.canvas, event)
        if self.is_selecting or not self.sel_rect.isEmpty():
            p = QPainter(self.canvas)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setPen(QPen(QColor("#9F7AEA"), 1.5, Qt.PenStyle.DashLine))
            p.setBrush(QColor(159, 122, 234, 30))
            p.drawRect(
                QRect(self.start_p, self.end_p) if self.is_selecting else self.sel_rect
            )
            p.end()

    def blur_and_save(self):
        if not self.img_path or self.sel_rect.isEmpty():
            return
        try:
            px, cx = self.canvas.pixmap().rect(), self.canvas.rect()
            lx, ly = (
                self.sel_rect.x() - (cx.width() - px.width()) // 2,
                self.sel_rect.y() - (cx.height() - px.height()) // 2,
            )
            with Image.open(self.img_path) as img:
                sx, sy = img.width / px.width(), img.height / px.height()
                box = (
                    int(lx * sx),
                    int(ly * sy),
                    int((lx + self.sel_rect.width()) * sx),
                    int((ly + self.sel_rect.height()) * sy),
                )
                crop = img.crop(box)

                if self.mode == "blur":
                    proc = crop.filter(ImageFilter.GaussianBlur(35))
                elif self.mode == "pixel":
                    proc = crop.resize(
                        (max(1, crop.width // 16), max(1, crop.height // 16)),
                        Image.Resampling.BILINEAR,
                    ).resize(crop.size, Image.Resampling.NEAREST)
                else:
                    proc = Image.new("RGB", crop.size, (20, 20, 20))

                out = img.copy()
                out.paste(proc, box)
                p = Path(self.img_path)
                c = 1
                while (new_p := p.parent / f"{p.stem}_{c}{p.suffix}").exists():
                    c += 1
                out.save(new_p)

            self.load_image(str(new_p))
            self.status.setText(f"📸 Saved: {new_p.name}")
        except Exception as e:
            self.status.setText(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Kumquat()
    w.show()
    sys.exit(app.exec())
