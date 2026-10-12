"""
pixel_ghost.py
Fantasminha em pixel art (grade 16x16) desenhado a partir de texto.
Cada caractere é um pixel; "." é transparente. Este módulo não depende
do Qt: só guarda os dados do sprite e monta a grade de cada humor.
"""

SPRITE_PX = 16  # largura e altura da grade, em "pixels do sprite"

# Legenda das letras -> cores
PALETTE = {
    "O": "#2a1052",  # contorno
    "P": "#8b5cf6",  # corpo
    "L": "#c4b5fd",  # brilho
    "D": "#6d3fd1",  # sombra
    "W": "#ffffff",  # branco do olho
    "K": "#1e1b2e",  # pupila / olho fechado
    "M": "#2e1065",  # boca
    "R": "#f9a8d4",  # bochecha
    "T": "#60a5fa",  # lágrima / baba
}

# Quando está triste o corpo fica acinzentado
PALETTE_TRISTE = {
    **PALETTE,
    "O": "#2b2b44",
    "P": "#7a7a9c",
    "L": "#a8a8c4",
    "D": "#5f5f82",
}

# Corpo base, ainda sem rosto (16 linhas de 16 caracteres)
BODY = [
    ".....OOOOOO.....",
    "...OOLLPPPPOO...",
    "..OLLPPPPPPPPO..",
    ".OLPPPPPPPPPPPO.",
    ".OPPPPPPPPPPPPO.",
    "OPPPPPPPPPPPPDDO",
    "OPPPPPPPPPPPPDDO",
    "OPPPPPPPPPPPPDDO",
    "OPPPPPPPPPPPPDDO",
    "OPPPPPPPPPPPPDDO",
    "OPPPPPPPPPPPPDDO",
    "OPPPPPPPPPPPPDDO",
    "OPPPPPPPPPPDDDDO",
    "ODDDDDDDDDDDDDDO",
    "ODDDOODDDDOODDDO",
    ".OOO..OOOO..OOO.",
]

assert len(BODY) == SPRITE_PX and all(len(r) == SPRITE_PX for r in BODY), \
    "BODY precisa ter 16 linhas com 16 caracteres cada"


def palette_for(mood: str) -> dict:
    return PALETTE_TRISTE if mood == "triste" else PALETTE


def build_sprite(mood: str, blink: bool = False, look: int = 1) -> list:
    """Monta a grade (lista de 16 strings) para o humor pedido.

    mood:  "dormindo", "normal", "feliz", "triste" ou "faminto"
    blink: True = olhos fechados (piscada)
    look:  0 = pupilas olhando pra esquerda, 1 = pra direita
    """
    grid = [list(row) for row in BODY]

    def put(r, c, ch):
        grid[r][c] = ch

    # ---------- olhos (cada olho tem 3 colunas) ----------
    for c0 in (3, 10):
        if mood == "dormindo" or blink:
            for c in range(c0, c0 + 3):
                put(7, c, "K")  # olho fechado: um traço
        elif mood == "feliz":
            put(6, c0 + 1, "K")  # olhinho em "^"
            put(7, c0, "K")
            put(7, c0 + 2, "K")
        else:
            for r in range(5, 8):
                for c in range(c0, c0 + 3):
                    put(r, c, "W")
            p0 = c0 + (1 if look else 0)
            linhas_pupila = (7,) if mood == "triste" else (6, 7)
            for r in linhas_pupila:
                put(r, p0, "K")
                put(r, p0 + 1, "K")

    # ---------- boca e detalhes ----------
    if mood == "feliz":
        put(9, 5, "M")
        put(9, 10, "M")
        for c in range(6, 10):
            put(10, c, "M")
        for c in (2, 3, 12, 13):
            put(8, c, "R")  # bochechas rosadas
    elif mood == "faminto":
        for r in (10, 11):
            put(r, 7, "M")
            put(r, 8, "M")
        put(12, 8, "T")  # baba
    elif mood == "triste":
        for c in range(6, 10):
            put(10, c, "M")
        put(11, 5, "M")
        put(11, 10, "M")
        put(8, 4, "T")  # lágrima
        put(9, 4, "T")
    elif mood == "dormindo":
        put(10, 7, "M")
        put(10, 8, "M")
    else:  # normal
        for c in range(6, 10):
            put(10, c, "M")

    return ["".join(row) for row in grid]