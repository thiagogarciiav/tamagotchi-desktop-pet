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

        