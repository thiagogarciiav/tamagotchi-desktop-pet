"""
main.py
Ponto de entrada do pet virtual (Tamagtchi de desktop).

Como rodar:
pip install - r requirements.txt
python main.py

Para ele iniciar sozinho junto com o Windows (e você não precisar rodar
esse comando toda vez), veja install_autostart.py.
"""


import sys
from PySide6.QtWidgets import QApplication

from pet_window import PetWindow


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) #continua rodando mesmo com a janela escondida

    pet = PetWindow()
    pet.show()

    # Rede de segurança: se o app for encerrado normalmente (menu "Sair")
    # ou fechamento do Windows chegando até aqui), garante que o pet é salvo já dormindo
    app.aboutToQuit.connect(pet.state.put_to_sleep)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()