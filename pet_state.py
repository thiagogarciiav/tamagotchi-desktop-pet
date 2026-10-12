"""
pet_state.py

Gerencia o estado (fome, energia, felicidade, sono) do pet virtual e
cuida de salvar/carregar esse estado em disco, para que ele "continue
existindo" mesmo depois que o programa é fechado ou o PC é desligado.
"""


import json
import os
import time
from dataclasses import dataclass, asdict

# Pasta onde o estado do pet fica salvo (%APPDATA%\DesktopTamagotchi)
APPDATA = os.environ.get("APPDATA", os.path.expanduser("~"))
DATA_DIR = os.path.join(APPDATA, "DesktopTamagotchi")
STATE_FILE = os.path.join(DATA_DIR, "state.json")


# --- Taxas de variação (por minuto) ---
AWAKE_HUNGER_RATE = 0.6          # fome sobe rápido enquanto acordado
ASLEEP_HUNGER_RATE = 0.15        # fome sobe devagar enquanto dorme
AWAKE_ENERGY_DECAY = 0.4         # energia cai enquanto acordado
ASLEEP_ENERGY_GAIN = 1.2         # energia recupera enquanto dorme
AWAKE_HAPPINESS_DECAY = 0.3      # felicidade cai enquanto acordado
ASLEEP_HAPPINESS_DECAY = 0.05    # felicidade cai bem devagar dormindo
HAPPINESS_HUNGRY_PENALTY = 0.4   # penalidade extra de felicidade se estiver com muita fome


@dataclass
class PetState:
    hunger: float = 30.0        # 0 = satisfeito, 100 = faminto
    energy: float = 80.0        # 0 = exausto, 100 = descansado
    happiness: float = 70.0     # 0 = triste, 100 = feliz
    asleep: bool = True
    last_update: float = None

    def __post_init__(self):
        if self.last_update is None:
            self.last_update = time.time()


    # ---------- Persistência ----------
    @classmethod
    def load(cls) -> "PetState":
        """Carrega o estado salvo (Se existir) e aplica o tempo que passou 
        desde o último salvamento - inclusive o tempo em que o PC esteve
        desligado."""
        state = cls()
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                state = cls(**data)
            except (json.JSONDecodeError, TypeError, ValueError):
                state = cls()

        now = time.time()
        elapsed_minutes = max(0.0, (now - state.last_update) / 60.0)


        # O pet SEMPRE começa dormindo quando o programa é iniciado
        # de novo — é assim que simulamos "ele estava dormindo enquanto
        # o PC estava desligado, e continua dormindo até eu clicar nele".
        state.asleep = True

        state._apply_decay(elapsed_minutes, asleep=True)
        state.last_update = now
        state.save()
        return state

    def save(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.last_update = time.time()
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)


    # ---------- Simulação ----------
    def _apply_decay(self, elapsed_minutes: float, asleep: bool):
        if elapsed_minutes <= 0:
            return
        if asleep:
            self.hunger += ASLEEP_HUNGER_RATE * elapsed_minutes
            self.energy += ASLEEP_ENERGY_GAIN * elapsed_minutes
            self.happiness -= ASLEEP_HAPPINESS_DECAY * elapsed_minutes
        else:
            self.hunger += AWAKE_HUNGER_RATE * elapsed_minutes
            self.energy -= AWAKE_ENERGY_DECAY * elapsed_minutes
            penalty = HAPPINESS_HUNGRY_PENALTY if self.hunger > 70 else 0.0
            self.happiness -= (AWAKE_HAPPINESS_DECAY + penalty) * elapsed_minutes


        self._clamp()

    def tick(self, elapsed_seconds: float):
        """Chamado periodicamente enquanto o programa está rodando (a cada
        1 segundo, no relógio principal da janela)."""
        self._apply_decay(elapsed_seconds / 60.0, self.asleep)

    def _clamp(self):
        self.hunger = min(100.0, max(0.0, self.hunger))
        self.energy = min(100.0, max(0.0, self.energy))
        self.happiness = min(100.0, max(0.0, self.happiness))

    # ---------- Ações ----------
    def wake_up(self):
        self.asleep = False

    def put_to_sleep(self):
        self.asleep = True
        self.save()

    def feed(self):
        if self.asleep:
            return
        self.hunger = max(0.0, self.hunger - 35.0)
        self.happiness = min(100.0, self.happiness + 5.0)
        self.save()

    def play(self):
        if self.asleep:
            return
        self.happiness = min(100.0, self.happiness + 20.0)
        self.energy = max(0.0, self.energy - 10.0)
        self.hunger = min(100.0, self.hunger + 5.0)
        self.save()

    # ---------- Estado / humor ----------
    def mood(self) -> str:
        """Retorna uma string simples com o humor atual, usada tanto pro
        desenho do pet quanto pra escolher a sprite certa."""
        if self.asleep:
            return "dormindo"
        if self.hunger > 75:
            return "faminto"
        if self.happiness < 30:
            return "triste"
        if self.happiness > 70 and self.hunger < 40:
            return "feliz"
        return "normal"

    def status_text(self) -> str:
        def bar(value, size=10):
            filled = int(round(value / 100 * size))
            return "█" * filled + "░" * (size - filled)

        estado = "Dormindo 💤" if self.asleep else "Acordado"
        return (
            f"Estado: {estado}\n"
            f"Fome:       {bar(self.hunger)} {self.hunger:.0f}%\n"
            f"Energia:    {bar(self.energy)} {self.energy:.0f}%\n"
            f"Felicidade: {bar(self.happiness)} {self.happiness:.0f}%"
        )