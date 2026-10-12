"""
pet_window.py
Janela do bichinho: sem borda, transparente, sempre no topo, arrastável,
com clique pra acordar/interagir e menu de botão direito com as ações
(alimentar, brincar, dormir, ver status, sair).

O visual é um fantasminha em pixel art (veja pixel_ghost.py). Cada pixel
do sprite é desenhado como um quadradinho SCALE x SCALE, sem suavização.
"""

import os

from PySide6.QtCore import Qt, QTimer, QPoint, QRect
from PySide6.QtGui import QPainter, QColor, QPixmap, QIcon, QAction
from PySide6.QtWidgets import QWidget, QMenu, QSystemTrayIcon, QToolTip, QApplication

from pet_state import PetState
from pixel_ghost import SPRITE_PX, PALETTE, build_sprite, palette_for

# ---------------- tamanhos ----------------
SCALE = 7                          # cada pixel do sprite vira 7x7 pixels na tela
SPRITE_SIZE = SPRITE_PX * SCALE    # 112
WINDOW_SIZE = 140
SPRITE_X = (WINDOW_SIZE - SPRITE_SIZE) // 2
SPRITE_Y = WINDOW_SIZE - SPRITE_SIZE - 4   # deixa espaço em cima pro pulinho e pros Z

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# Sprites opcionais: se existir um PNG com esse nome dentro de "assets",
# ele é usado no lugar do fantasminha em pixel art (pra você trocar o
# visual por uma arte sua).
SPRITE_FILES = {
    "dormindo": "dormindo.png",
    "normal": "normal.png",
    "feliz": "feliz.png",
    "triste": "triste.png",
    "faminto": "faminto.png",
}

# Letra "Z" em pixel art (3x5), usada na animação de sono
Z_GLYPH = ["XXX", "..X", ".X.", "X..", "XXX"]
Z_COLOR = "#e9d5ff"
Z_SHADOW = "#2a1052"

_color_cache = {}


def _color(hex_code: str) -> QColor:
    if hex_code not in _color_cache:
        _color_cache[hex_code] = QColor(hex_code)
    return _color_cache[hex_code]


def draw_grid(painter, grid, palette, scale, ox, oy):
    """Desenha uma grade de caracteres como pixel art."""
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            painter.fillRect(ox + c * scale, oy + r * scale, scale, scale, _color(palette[ch]))


def draw_glyph(painter, glyph, x, y, px, hex_code):
    for r, row in enumerate(glyph):
        for c, ch in enumerate(row):
            if ch == "X":
                painter.fillRect(x + c * px, y + r * px, px, px, _color(hex_code))


class PetWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.state = PetState.load()

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(WINDOW_SIZE, WINDOW_SIZE)
        self._move_to_bottom_right()

        self._drag_pos = None
        self._was_dragged = False
        self._anim_tick = 0
        self._sprite_cache = {}

        # Relógio do estado (fome, energia...): 1x por segundo
        self.tick_timer = QTimer(self)
        self.tick_timer.timeout.connect(self._on_tick)
        self.tick_timer.start(1000)

        # Relógio da animação: 2 quadros por segundo (visual "retrô")
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._on_anim)
        self.anim_timer.start(500)

        # Autosave, pra não perder progresso se o PC desligar de repente
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
        self.tray.setToolTip("Bichinho virtual")

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
        draw_grid(painter, build_sprite("normal"), PALETTE, 2, 0, 0)
        painter.end()
        return pix

    # ---------------- relógios ----------------
    def _on_tick(self):
        self.state.tick(1.0)

    def _on_anim(self):
        self._anim_tick += 1
        self.update()

    # ---------------- desenho ----------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)

        mood = self.state.mood()
        asleep = self.state.asleep

        # Acordado: pulinho de 1 pixel a cada segundo. Dormindo: parado.
        bob = 0 if asleep else (-SCALE if (self._anim_tick // 2) % 2 else 0)
        ox, oy = SPRITE_X, SPRITE_Y + bob

        custom = self._load_sprite(mood)
        if custom is not None:
            painter.drawPixmap(QRect(ox, oy, SPRITE_SIZE, SPRITE_SIZE), custom)
        else:
            blink = (not asleep) and (self._anim_tick % 12 == 0)
            look = (self._anim_tick // 12) % 2
            grid = build_sprite(mood, blink=blink, look=look)
            draw_grid(painter, grid, palette_for(mood), SCALE, ox, oy)

        if asleep:
            self._draw_zzz(painter)

    def _load_sprite(self, mood: str):
        """Procura um PNG em assets/ pro humor atual. Retorna None se não
        existir, e nesse caso o fantasminha em pixel art é usado."""
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

    def _draw_zzz(self, painter):
        """"Z z" em pixel art subindo do canto da cabeça (ciclo de 4 quadros)."""
        frame = self._anim_tick % 4
        right = SPRITE_X + SPRITE_SIZE

        letras = []
        if frame in (0, 1, 2):
            letras.append((right - 18, SPRITE_Y + 2, 2))   # Z pequeno
        if frame in (1, 2, 3):
            letras.append((right - 10, SPRITE_Y - 16, 3))  # Z médio

        for x, y, px in letras:
            draw_glyph(painter, Z_GLYPH, x + 1, y + 1, px, Z_SHADOW)  # sombra
            draw_glyph(painter, Z_GLYPH, x, y, px, Z_COLOR)

    # ---------------- interação com o mouse ----------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._was_dragged = False
        elif event.button() == Qt.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            self._was_dragged = True
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self._was_dragged:
                self._on_click()
            self._drag_pos = None

    def _on_click(self):
        if self.state.asleep:
            self.state.wake_up()
            self.state.save()
        self.update()

    def _show_context_menu(self, global_pos: QPoint):
        menu = QMenu(self)

        act_feed = QAction("🍖 Alimentar", self)
        act_feed.triggered.connect(self._feed)
        act_play = QAction("🎾 Brincar", self)
        act_play.triggered.connect(self._play)
        act_sleep = QAction("💤 Dormir agora", self)
        act_sleep.triggered.connect(self._sleep_now)
        act_status = QAction("📊 Ver status", self)
        act_status.triggered.connect(self._show_status)
        act_quit = QAction("Sair", self)
        act_quit.triggered.connect(QApplication.quit)

        menu.addAction(act_feed)
        menu.addAction(act_play)
        menu.addAction(act_sleep)
        menu.addSeparator()
        menu.addAction(act_status)
        menu.addSeparator()
        menu.addAction(act_quit)

        menu.exec(global_pos)

    def _feed(self):
        if self.state.asleep:
            self.state.wake_up()
        self.state.feed()
        self.update()

    def _play(self):
        if self.state.asleep:
            self.state.wake_up()
        self.state.play()
        self.update()

    def _sleep_now(self):
        self.state.put_to_sleep()
        self.update()

    def _show_status(self):
        QToolTip.showText(self.mapToGlobal(QPoint(0, 0)), self.state.status_text(), self)

    # ---------------- fechamento ----------------
    def closeEvent(self, event):
        self.state.put_to_sleep()  # já chama save()
        event.accept()