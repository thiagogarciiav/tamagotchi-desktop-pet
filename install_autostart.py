"""
install_autostart.py

Configura o pet para abrir sozinho toda vez que o Windows iniciar,
sem precisar rodar "python main.py" na mão.

Funciona criando um pequeno arquivo .vbs na pasta de Inicialização do
Windows, que roda o main.py em segundo plano (sem janela de terminal
aparecendo) usando o pythonw.exe.

Rode uma vez:
    python install_autostart.py
"""


import os
import sys

STARTUP_DIR = os.path.join(
    os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
)
LAUNCHER_NAME = "tamagotchi_virtual.vbs"



def find_pythonw():
    """Tenta achar o pythonw.exe (versão do Python sem janela de console)
    a partir do interpretador atual."""
    exe = sys.executable
    pythonw = os.path.join(os.path.dirname(exe), "pythonw.exe")
    if os.path.exists(pythonw):
        return pythonw
    return exe  # se não achar, usa o python.exe normal mesmo


def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(project_dir, "main.py")
    pythonw = find_pythonw()

    vbs_content = (
        'Set WshShell = CreateObject("WScript.Shell")\n'
        f'WshShell.Run """{pythonw}"" ""{main_py}""", 0, False\n'
    )

    os.makedirs(STARTUP_DIR, exist_ok=True)
    vbs_path = os.path.join(STARTUP_DIR, LAUNCHER_NAME)
    with open(vbs_path, "w", encoding="utf-8") as f:
        f.write(vbs_content)

    print("Pronto! Criado o iniciador automático em:")
    print(f"  {vbs_path}")
    print()
    print("Da próxima vez que o Windows ligar, o bichinho vai abrir sozinho")
    print("(dormindo, até você clicar nele).")
    print()
    print(f"pythonw usado: {pythonw}")
    print(f"script do pet: {main_py}")



if __name__ == "__main__":
    main()