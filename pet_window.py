"""
pet_window.py

Janela do pet: sem borda, transparente, sempre no topo, arrastável,
com clique pra acordar/interagir e menu de botão direito com as ações
(alimentar, brincar, dormir, ver status, sair).
"""


import os
import math

from PySide6.QtCore import Qt, QTimer, QPoint, QRectF
from PySide6.QtGui import (
    QPainter, QColor, QPainterPath, QPixmap, QIcon, QFont, QAction,
    QLinearGradient, QBrush, QPen,
)
from PySide6.QtWidgets import QWidget, QMenu, QSystemTrayIcon, QToolTip, QApplication

from pet_state import PetState


WINDOW_SIZE = 140
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# Nome do arquivo de sprite (opcional) pra cada humor. Se você colocar um
# PNG com esse nome dentro da pasta "assets", ele passa a ser usado no
# lugar do fantasminha desenhado por código — é assim que você troca o
# visual por uma arte real (por exemplo, uma sprite do pet que você
# já tenha os direitos de usar).
SPRITE_FILES = {
    "dormindo": "dormindo.png",
    "normal": "normal.png",
    "feliz": "feliz.png",
    "triste": "triste.png",
    "faminto": "faminto.png",
}



class PetWindow(QWidget):
    def __ini__(self):
        super().__init__()
        self.state = PetState.load()

        self.setWindowFlag(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(WINDOW_SIZE, WINDOW_SIZE)
        self._move_to_bottom_right()

        self._drag_pos = None
        self._was_dragged = False
        self._bounce_phase = 0.0
        self._sprite_cache = {}

        # Loop principal: atualiza estado + redesenha, 1x por segundo
        self.tick_timer = QTimer(self)
        self.tick_timer.timeout.connect(self._on_tick)
        self.tick_timer.start(1000)

        # Autosave, para não perder progresso se o PC desligar de repente
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.state.save)
        self.autosave_timer.start(30_000)

        self._build_tray_icon()


        # ---------------- posicionamento ----------------
        def _move_to_bottom_right(self):
            screen = QApplication.primaryScreen().availableGeometry()
            x = screen.right() - WINDOW_SIZE - 30
            y = screen.bottom() - WINDOW_SIZE - 30
            self.move(x, y)

        # ---------------- bandeja do sistema ----------------
        def _build_tray_icon(self):
            icon = QIcon(self._make_icon_pixmap())
            self.tray = QSystemTrayIcon(icon, self)
            self.tray.setToolTip("Pet Tamagotchi Virtual")

            menu = QMenu()
            act_show = QAction("Mostrar/ocultar", self)
            act_show.triggered.connect(self._toggle_visible)
            act_status = QAction("Ver status", self)
            act_status.triggered.connect(self._show_status)
            act_quit = QAction("Sair", self)
            act_quit.triggered.connect(QApplication.quit)

            menu.addAction(act_show)
            menu.addAction(act_status)
            menu.addSeparator()
            menu.addAction(act_quit)

            self.tray.setContextMenu(menu)
            self.tray.show()

        def _toggle_visible(self):
            self.setVisible(not self.isVisible())
        
        def _make_icon_pixmap(self) -> QPixmap:
            pix = QPixmap(32, 32)
            pix.fill(Qt.transparent)
            painter = QPainter(pix)
            painter.setRenderHint(QPainter.Antialiasing)
            self._draw_ghost(painter, QRectF(2, 2, 28, 28), mood="normal")
            painter.end()
            return pix

        # ---------------- loop principal ----------------
        def _on_tick(self):
            self.state.tick(1.0)
            self._bounce_phase += 0.3
            self.update()

        # ---------------- desenho do pet ----------------
        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            mood = self.state.mood()
            sprite = self._load_sprite(mood)

            bounce = 0 if self.state.asleep else int(4 * math.sin(self._bounce_phase))
            rect = QRectF(10, 10 + bounce, WINDOW_SIZE - 20, WINDOW_SIZE - 20)

            if sprite is not None:
                painter.drawPixmap(rect.toRect(), sprite)
            else:
                self._draw_ghost(painter, rect, mood)

            if self.state.asleep:
                self._draw_zzz(painter, rect)

        def _load_sprite(self, mood: str):
            """Procura um PNG em assets/ pro humor atual. Retorna None se não
            existir, e nesse caso o fantasminha é desenhado por código."""
            if mood in self._sprite_cache:
                return self._sprite_cache[mood]

            filename = SPRITE_FILES.get(mood)
            pixmap = None
            if filename:
                path = os.path.join(ASSETS_DIR, filename)
                if os.path.exists(path):
                    candidate = QPixmap(path)
                    if not candidate.isNull():
                        pixmap = candidate

            self._sprite_cache[mood] = pixmap
            return pixmap

        def _draw_ghost(self, painter: QPainter, rect: QRectF, mood: str):
            """Fantasminha original desenhado via código ( Dá pra trocar
            por uma sprite real colocando um PNG em assets/, veja SPRITE_FILES)."""
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

            body_color = QColor("#8b5cf6") if mood != "triste" else QColor("#6d6d8f")

            path = QPainterPath()
            path.moveTo(x, y + h * 0.55)
            path.cubicTo(x, y - h * 0.1, x + w, y - h * 0.1, x + w, y + h * 0.55)
            path.lineTo(x + w, y + h)
            # barriga em ondas (estilo fantasma)
            wave_count = 4
            seg = w / wave_count
            for i in range(wave_count):
                fx = x + w - seg * i
                path.quadTo(fx - seg / 2, y + h * 0.85, fx - seg, y + h)
            path.closeSubpath()

            gradient = QLinearGradient(x, y, x, y + h)
            gradient.setColorAt(0, body_color.lighter(120))
            gradient.setColorAt(1, body_color.darker(110))
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(body_color.darker(150), 2))
            painter.drawPath(path)

            eye_y = y + h * 0.38
            eye_dx = w * 0.22
            eye_w, eye_h = w * 0.16, h * 0.2

            if mood == "dormindo":
                pen = QPen(QColor("#330547"), 3)
                painter.setPen(pen)
                painter.drawArc(int(x + w / 2 - eye_dx - eye_w / 2), int(eye_y), int(eye_w), int(eye_h), 0, 180 * 16)
                painter.drawArc(int(x + w / 2 + eye_dx - eye_w / 2), int(eye_y), int(eye_w), int(eye_h), 0, 180 * 16)
                return

            painter.setBrush(QColor("white"))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(x + w / 2 - eye_dx - eye_w / 2, eye_y, eye_w, eye_h))
            painter.drawEllipse(QRectF(x + w / 2 + eye_dx - eye_w / 2, eye_y, eye_w, eye_h))

            pupil_w = eye_w * 0.45
            pupil_dy = eye_h * 0.15 if mood != "triste" else eye_h * 0.35
            painter.setBrush(QColor("#1e1b2e"))
            painter.drawEllipse(QRectF(x + w / 2 - eye_dx - pupil_w / 2, eye_y + pupil_dy, pupil_w, pupil_w))
            painter.drawEllipse(QRectF(x + w / 2 + eye_dx - pupil_w / 2, eye_y + pupil_dy, pupil_w, pupil_w))

            mouth_y = y + h * 0.62
            painter.setPen(QPen(QColor("#330547"), 3))
            painter.setBrush(Qt.NoBrush)
            mouth_w = w * 0.3
            if mood == "feliz":
                painter.drawArc(int(x + w / 2 - mouth_w / 2), int(mouth_y), int(mouth_w), int(h * 0.15), 180 * 16, 180 * 16)
            elif mood == "faminto":
                painter.setBrush(QColor("#330547"))
                painter.drawEllipse(QRectF(x + w / 2 - mouth_w * 0.18, mouth_y, mouth_w * 0.36, h * 0.16))
            elif mood == "triste":
                painter.drawArc(int(x + w / 2 - mouth_w / 2), int(mouth_y + h * 0.08), int(mouth_w), int(h * 0.15), 0, 180 * 16)
            else:
                painter.drawLine(int(x + w / 2 - mouth_w / 2), int(mouth_y + h * 0.05), int(x + w / 2 + mouth_w / 2), int(mouth_y + h * 0.05))

        def _draw_zzz(self, painter: QPainter, rect: QRectF):
            font = QFont("Arial", 12)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor("#4c1d95"))
            offset = int(3 * math.sin(self._bounce_phase))
            painter.drawText(int(rect.right() - 30), int(rect.top() - 5 + offset), "Z z z")            