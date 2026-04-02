# 🎮 Ultimate Pygame Repository

Bem-vindo ao **Ultimate Pygame Repository**, uma coletânea super rica de minigames projetados totalmente em Python, variando de casuais Wordles até um impressionante atirador Raycasting 3D imersivo nos moldes dos anos 90! 

A ideia deste repositório é concentrar lógicas completas de games divertidos desenvolvidos desde a estaca zero, para brincar, estudar código e aprender mecânicas de manipulação de janela e matemática vetorial na engine Pygame.

---

## 🚀 Como Rodar os Jogos
A enorme maioria dos jogos funciona sobre dois pilares simples nativos de Python. 

### Pré-requisitos
Para garantir que tudo funcione perfeitamente no seu computador, certifique-se de instalar as bibliotecas de engine com apenas comandos pip no terminal (PowerShell, CMD, ou terminal Mac/Linux):

```sh
# Instala as bibliotecas de Jogos e Gráficos necessárias:
pip install pygame
pip install Pillow
```

### Rodando na Prática
Cada pasta deste repositório é um "universo à parte" contendo seu próprio `.py` de entrada (`main.py` ou `<NomeDoJogo>.py`).
Para rodar qualquer um, abra o seu terminal na pasta raiz e chame o interpretador Python.

**Exemplo jogando o nosso clássico Doom:**
```sh
# Entra na pasta do Repositório (caso já não esteja)
cd \UltimatePygameRepository

# Inicia a bruxaria tridimensional:
python Doom/Doom.py
```

---

## 🕹️ Catálogo de Jogos Inclusos

Navegue visualmente pelas pastas para escolher o seu desafio do dia. Abaixo está a visão completa do nosso fliperama nativo:

### 💀 1. Doom (Pygame 2.5D Raycaster)
**Onde rodar:** `python Doom/Doom.py`
A joia brutal do repositório. Criamos do zero um autêntico FPS baseado na engine visual ilusória (Raycasting) usada no Doom original de 1993, 100% no Python.
* **Sobrevivência Infinita:** Entre em um imenso labirinto e acabe com Hordas de caveiras animadas que ganham vida a cada Nível sem limite.
* **Sistema de Chefões:** Múltiplos da fase 5 invocam autênticos monstros blindados gigantes ("Scale Bosses").
* **O Arsenal:** O desenho geométrico do zero das armas. Suba de Fase e de vida pra ver sua pistola prateada evoluir naturalmente para _Shotgun_ de cano duplo, _Miniguns_ de 3 canos rotativos, Rifles de _Plasma_ abissal e claro, varrer o chão do Inferno com as esferas da *BFG 9000*!

### 👑 2. ClashDle (Adivinhe a Carta)
**Onde rodar:** Aponte para seu App de inicialização na pasta `ClashDle`
O Wordle tático do universo de Clash Royale, 100% traduzido para o Português do Brasil!
Conta com um Banco de Dados robusto com mais de 116 cartas ativas puxadas da internet. Esqueça de vez a dependência do ClashDle Web: um sistema orgânico embassa as fotografias em agressivos blocos de Pixel-Art. A cada nome adivinhado errado, a imagem fica sutilmente melhor, forçando suas sinapses em conhecimento Clash para matar a charada no menor número de lances possível.

### 🎤 3. Eminem Jumps
O nosso jogo em plataformas verticais e _momentum_. Conduza a gravidade num estilo ágil e engenhoso mantendo a coordenação em pulos cronometrados contra cenários impiedosos baseados no ídolo do rap!

### 🕵️ 4. Forca
Uma repaginação amigável em UI de um dos jogos de linguagem e suposição mais clássicos do universo. Ótimo estudo sobre manipulação de Strings e Inputs!

### 🥊 5. Jogo de Luta
Pura mecânica de gravidade 2D, Hitboxes ("caixas de dano dinâmico") e controle elástico de personagem. Ótimo para brincar testando combinações e limites gravitacionais lado-a-lado usando Pygame.

### 🐲 6. Pokedle
Descubra Quem é Esse Pokémon baseando-se por gerações, blocos geográficos e descrições elementais cruas! Seu banco de dados em Python é o seu principal treinador de Pokémon aqui, operando ao estilo Termo clássico.

### 🟩 7. Termo
Nosso Clone raiz e minimalista para tentar queimar um pouco as unhas descobrindo as letras em amabientes limitados. Se o seu PC está sem internet e sua vontade de Wordles em PT-BR ataca, o `termo` de fundo de quintal vai salvar seus dedos!

---

> _Diverta-se fuçando nos códigos-fontes, eles estão inteiramente legíveis e sem travas de empacotamento exe, para abrigar curiosos para sempre!_
