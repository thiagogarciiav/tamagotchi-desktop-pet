"""
uninstaall_autostart.py

Remove a inicialização automática criada pelo install_autostart.py.

Rode:
    python uninstall_autostart.py
"""


import os


STARTUP_DIR = os.path.join(
    os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
)
LAUNCHER_NAME = "tamaagotchi_virtual.vbs"



def main():
    vbs_path = os.path.join(STARTUP_DIR, LAUNCHER_NAME)
    if os.path.exists(vbs_path):
        os.remove(vbs_path)
        print(f"Removido: {vbs_path}")
    else:
        print("Nenhum iniciador automático encontrado (já estava desinstalado).")


if __name__ == "__main__":
    main()