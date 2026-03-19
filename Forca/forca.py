import pygame
import random
from palavras import lista_palavras

# === INICIALIZAÇÃO DO PYGAME ===
pygame.init()

# --- CONFIGURAÇÕES DE TELA ---
LARGURA = 1200
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo da Forca de PROGRAMAÇÃO")

# --- CORES ---
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (0, 200, 0)
VERMELHO = (200, 0, 0)
AZUL = (0, 0, 255)
CINZA_CLARO = (220, 220, 220)

# --- FONTES ---
fonte_grande = pygame.font.SysFont("arial", 48, bold=True)
fonte_media = pygame.font.SysFont("arial", 36)
fonte_pequena = pygame.font.SysFont("arial", 28)

# --- VARIÁVEIS INICIAIS ---
palavra_anterior = ""  # <- armazena a última palavra usada
palavra = random.choice(lista_palavras).upper()
palavra_anterior = palavra  # define como a primeira palavra
letras_descobertas = ["_"] * len(palavra)
letras_tentadas = []
tentativas = 6
rodando = True
fim_de_jogo = False

# --- FUNÇÃO PARA DESENHAR O BONECO ---
def desenhar_forca(tentativas):
    """Desenha o boneco da forca alinhado corretamente no lado esquerdo."""
    base_x = 350  # posição central da corda
    base_y = 200  # topo da corda

    # CABEÇA
    if tentativas <= 5:
        pygame.draw.circle(TELA, PRETO, (base_x, base_y + 25), 25, 3)
    # CORPO
    if tentativas <= 4:
        pygame.draw.line(TELA, PRETO, (base_x, base_y + 50), (base_x, base_y + 130), 3)
    # BRAÇO ESQUERDO
    if tentativas <= 3:
        pygame.draw.line(TELA, PRETO, (base_x, base_y + 70), (base_x - 30, base_y + 100), 3)
    # BRAÇO DIREITO
    if tentativas <= 2:
        pygame.draw.line(TELA, PRETO, (base_x, base_y + 70), (base_x + 30, base_y + 100), 3)
    # PERNA ESQUERDA
    if tentativas <= 1:
        pygame.draw.line(TELA, PRETO, (base_x, base_y + 130), (base_x - 25, base_y + 180), 3)
    # PERNA DIREITA
    if tentativas <= 0:
        pygame.draw.line(TELA, PRETO, (base_x, base_y + 130), (base_x + 25, base_y + 180), 3)

# --- FUNÇÃO PARA MOSTRAR TEXTO ---
def mostrar_texto(texto, fonte, cor, x, y):
    """Renderiza texto na tela em uma posição (x, y)."""
    imagem = fonte.render(texto, True, cor)
    TELA.blit(imagem, (x, y))

# --- FUNÇÃO PARA ESCOLHER UMA NOVA PALAVRA DIFERENTE ---
def nova_palavra():
    """Seleciona uma nova palavra diferente da última usada."""
    global palavra_anterior
    nova = random.choice(lista_palavras).upper()
    while nova == palavra_anterior and len(lista_palavras) > 1:
        nova = random.choice(lista_palavras).upper()
    palavra_anterior = nova
    return nova

# --- LOOP PRINCIPAL DO JOGO ---
while rodando:
    TELA.fill(CINZA_CLARO)

    # --- DIVISÃO VISUAL (linhas) ---
    pygame.draw.line(TELA, PRETO, (450, 0), (450, ALTURA), 3)

    # --- DESENHA A ESTRUTURA DA FORCA (lado esquerdo) ---
    pygame.draw.line(TELA, PRETO, (150, 500), (350, 500), 6)     # base
    pygame.draw.line(TELA, PRETO, (250, 500), (250, 150), 6)     # haste vertical
    pygame.draw.line(TELA, PRETO, (250, 150), (350, 150), 6)     # barra superior
    pygame.draw.line(TELA, PRETO, (350, 150), (350, 200), 3)     # corda

    # --- DESENHA O BONECO ---
    desenhar_forca(tentativas)

    # --- MOSTRA AS INFORMAÇÕES (lado direito) ---
    mostrar_texto("JOGO DA FORCA: PROGRAMAÇÃO", fonte_grande, AZUL, 520, 50)
    mostrar_texto(" ".join(letras_descobertas), fonte_grande, PRETO, 520, 180)
    mostrar_texto(f"Tentativas restantes: {tentativas}", fonte_media, AZUL, 520, 260)
    mostrar_texto(f"Letras usadas: {' '.join(letras_tentadas)}", fonte_pequena, PRETO, 520, 320)

    # --- CONDIÇÕES DE VITÓRIA / DERROTA ---
    if "_" not in letras_descobertas:
        fim_de_jogo = True
        mostrar_texto("Você venceu!", fonte_grande, VERDE, 520, 400)
        mostrar_texto("Pressione ENTER para jogar novamente", fonte_pequena, AZUL, 520, 460)
    elif tentativas == 0:
        fim_de_jogo = True
        mostrar_texto(f"Você perdeu!", fonte_grande, VERMELHO, 520, 400)
        mostrar_texto(f"A palavra era: {palavra}", fonte_media, PRETO, 520, 450)
        mostrar_texto("Pressione ENTER para reiniciar", fonte_pequena, AZUL, 520, 500)

    # --- EVENTOS DO JOGADOR ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN and not fim_de_jogo:
            letra = pygame.key.name(evento.key).upper()
            if len(letra) == 1 and letra.isalpha() and letra not in letras_tentadas:
                letras_tentadas.append(letra)
                if letra in palavra:
                    for i, l in enumerate(palavra):
                        if l == letra:
                            letras_descobertas[i] = letra
                else:
                    tentativas -= 1

        elif evento.type == pygame.KEYDOWN and fim_de_jogo:
            if evento.key == pygame.K_RETURN:  # Reinicia o jogo ao pressionar Enter
                palavra = nova_palavra()  # ← agora garante palavra diferente!
                letras_descobertas = ["_"] * len(palavra)
                letras_tentadas = []
                tentativas = 6
                fim_de_jogo = False

    pygame.display.update()

pygame.quit()