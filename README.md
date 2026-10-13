# 👻 Tamagotchi Desktop Pet

Um bichinho virtual estilo Tamagotchi que vive no seu desktop (Windows), sempre por cima das outras janelas. Ele **dorme quando o PC liga**, **acorda quando você clica nele** e **volta a dormir quando você desliga o computador**. Dá pra alimentar, brincar, arrastar pela tela e acompanhar fome, energia e felicidade.

Feito em Python com PySide6 (Qt).

## ✨ Funcionalidades

- Janela transparente, sem borda e sempre no topo
- Começa dormindo toda vez que o programa inicia (ligou o PC, ele ainda está dormindo)
- Clique pra acordar, arraste pra mover pela tela
- Fome, energia e felicidade que mudam com o tempo
- Tempo com o PC desligado conta como tempo de sono (a fome sobe devagar e a energia se recupera)
- Menu de clique direito: alimentar, brincar, dormir agora, ver status e sair
- Ícone na bandeja do sistema
- Progresso salvo automaticamente (a cada 30 s e ao fechar)
- Inicialização automática com o Windows
- Visual trocável: use suas próprias sprites PNG

## 📋 Pré-requisitos

- Windows 10 ou superior
- Python 3.9+

## 🚀 Instalação

```bash
git clone https://github.com/thiagogarciiav/tamagotchi-desktop-pet.git
cd tamagotchi-desktop-pet
pip install -r requirements.txt
python main.py
```

O bichinho aparece dormindo no canto inferior direito da tela. Clique nele pra acordar.

## 🔁 Iniciar junto com o Windows

Rode uma única vez:

```bash
python install_autostart.py
```

Isso cria um pequeno iniciador `.vbs` na pasta de Inicialização do Windows, que abre o `main.py` em segundo plano (sem janela de terminal) toda vez que você liga o PC.

Pra desfazer:

```bash
python uninstall_autostart.py
```

> ⚠️ O iniciador guarda o caminho completo do projeto. Se você mover a pasta de lugar, rode `python install_autostart.py` de novo.

## 🎮 Como interagir

| Ação | O que acontece |
|---|---|
| Clique esquerdo | Acorda o bichinho |
| Segurar e arrastar | Move o bichinho pela tela |
| Clique direito | Abre o menu de ações |
| 🍖 Alimentar | Reduz a fome |
| 🎾 Brincar | Aumenta a felicidade (gasta energia e dá um pouco de fome) |
| 💤 Dormir agora | Coloca o bichinho pra dormir |
| 📊 Ver status | Mostra fome, energia e felicidade |
| Sair | Fecha o programa (salva já dormindo) |

O ícone da bandeja do sistema também tem "Mostrar/ocultar", "Ver status" e "Sair".

## 🧠 Como funciona

- **Sempre começa dormindo:** toda vez que o programa inicia, o bichinho está dormindo até você clicar nele.
- **Tempo offline:** o intervalo desde o último salvamento é aplicado ao iniciar, usando as taxas de sono.
- **Salvamento:** ao fechar pelo menu "Sair" ou quando o Windows encerra a sessão, o estado é salvo dormindo. Além disso, há autosave a cada 30 segundos como proteção contra desligamentos bruscos.
- **Onde fica salvo:** `%APPDATA%\DesktopPetGengar\state.json` (apague esse arquivo pra reiniciar o bichinho do zero).

## 🎨 Personalização

### Visual (sprites)

O projeto vem com um fantasminha roxo original, desenhado por código. Pra usar suas próprias imagens, coloque PNGs com estes nomes na pasta `assets/`:

```
assets/dormindo.png
assets/normal.png
assets/feliz.png
assets/triste.png
assets/faminto.png
```

Cada arquivo que existir substitui o desenho correspondente. Não precisa ter todos.

> As sprites **não** fazem parte deste repositório. Se você usar arte de terceiros (por exemplo, personagens de franquias), confira se tem direito de uso e não a publique no repositório.

### Taxas e comportamento

As constantes no topo de `pet_state.py` controlam a velocidade com que tudo muda (valores por minuto):

| Constante | Efeito |
|---|---|
| `AWAKE_HUNGER_RATE` / `ASLEEP_HUNGER_RATE` | Velocidade com que a fome sobe acordado / dormindo |
| `AWAKE_ENERGY_DECAY` / `ASLEEP_ENERGY_GAIN` | Perda de energia acordado / ganho dormindo |
| `AWAKE_HAPPINESS_DECAY` / `ASLEEP_HAPPINESS_DECAY` | Queda de felicidade acordado / dormindo |
| `HAPPINESS_HUNGRY_PENALTY` | Queda extra de felicidade com muita fome |

## 🗂️ Estrutura

```
tamagotchi-desktop-pet/
├── assets/                  # sprites opcionais (PNG)
├── main.py                  # ponto de entrada
├── pet_state.py             # estado + persistência
├── pet_window.py            # janela, desenho, mouse, menu e bandeja
├── install_autostart.py     # ativa início automático no Windows
├── uninstall_autostart.py   # desativa início automático
└── requirements.txt
```

## 🛠️ Problemas comuns

- **O bichinho não aparece:** confira se ele não está oculto (ícone da bandeja → "Mostrar/ocultar") e se `pip install -r requirements.txt` rodou sem erros.
- **Não abre com o Windows:** rode `python install_autostart.py` de novo e verifique se o arquivo `bichinho_virtual.vbs` está na pasta de Inicialização (`Win + R` → `shell:startup`).
- **Quero zerar o progresso:** feche o programa e apague `%APPDATA%\DesktopPetGengar\state.json`.

## 🗺️ Ideias pro futuro

- Sprites animadas (GIF ou spritesheet)
- Sons ao acordar e comer
- Fases de vida (bebê → adulto)
- "Modo doente" quando a fome fica no máximo por muito tempo
- Movimento livre pela tela

## 📄 Licença

Distribuído sob a licença MIT. Veja o arquivo `LICENSE` pra mais detalhes.

## Contribuição

- Se você quiser contribuir para este projeto, fique à vontade para fazer um fork, criar um branch e enviar um pull request com suas melhorias.

## Autor

Este projeto foi desenvolvido por **Thiago Garcia**.