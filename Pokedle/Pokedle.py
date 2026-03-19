import pygame
import random
import requests
import io
from BD_POKEMON import BD_POKEMON

# --- Configurações de Cores ---
VERDE, VERMELHO, AMARELO, BRANCO, PRETO = (80, 200, 120), (220, 60, 60), (255, 215, 0), (255, 255, 255), (30, 30, 30)
CINZA_ESCURO, CINZA_CLARO = (50, 50, 50), (220, 220, 220)

class PokedleGame:
    def __init__(self):
        pygame.init()
        # Aumentei a largura para 1300 para acomodar as colunas maiores
        self.tela = pygame.display.set_mode((1300, 850))
        pygame.display.set_caption("Pokedle Online - Imagens Grandes")
        self.fonte = pygame.font.SysFont("Arial", 16, bold=True)
        self.alvo = random.choice(BD_POKEMON)
        self.tentativas = []
        self.texto_input = ""
        self.sugestoes = []
        self.venceu = False
        self.cache_imgs = {}

    def carregar_img_api(self, poke_id, tamanho):
        """Puxa a imagem e guarda no cache com o tamanho solicitado"""
        chave_cache = f"{poke_id}_{tamanho[0]}"
        if chave_cache in self.cache_imgs:
            return self.cache_imgs[chave_cache]
        
        try:
            url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{poke_id}.png"
            response = requests.get(url, timeout=3)
            img_bytes = io.BytesIO(response.content)
            img = pygame.image.load(img_bytes).convert_alpha()
            img = pygame.transform.scale(img, tamanho)
            self.cache_imgs[chave_cache] = img
            return img
        except:
            temp = pygame.Surface(tamanho)
            temp.fill(CINZA_CLARO)
            return temp

    def atualizar_sugestoes(self):
        if self.texto_input:
            self.sugestoes = [p for p in BD_POKEMON if p["nome"].lower().startswith(self.texto_input.lower())][:5]
        else:
            self.sugestoes = []

    def enviar_palpite(self, p=None):
        if not p:
            nome = self.texto_input.strip().capitalize()
            p = next((x for x in BD_POKEMON if x["nome"] == nome), None)
        
        if p and not any(t["id"] == p["id"] for t in self.tentativas):
            # (Lógica de comparação simplificada para o exemplo)
            res = {
                "id": p["id"], "nome": p["nome"],
                "t1": (p["tipo1"], VERDE if p["tipo1"] == self.alvo["tipo1"] else VERMELHO),
                "t2": (p["tipo2"], VERDE if p["tipo2"] == self.alvo["tipo2"] else VERMELHO),
                "cor": ("/".join(p["cor"]), VERDE if set(p["cor"]) == set(self.alvo["cor"]) else VERMELHO),
                "hab": (p["habitat"], VERDE if p["habitat"] == self.alvo["habitat"] else VERMELHO),
                "alt": (f"{p['altura']}m", VERDE if p["altura"] == self.alvo["altura"] else VERMELHO),
                "pes": (f"{p['peso']}kg", VERDE if p["peso"] == self.alvo["peso"] else VERMELHO)
            }
            self.tentativas.insert(0, res)
            if p["id"] == self.alvo["id"]: self.venceu = True
        
        self.texto_input = ""
        self.sugestoes = []

    def desenhar(self):
        self.tela.fill(BRANCO)
        
        # Input e Sugestões
        pygame.draw.rect(self.tela, CINZA_CLARO, (50, 40, 350, 45), border_radius=5)
        self.tela.blit(self.fonte.render(self.texto_input, True, PRETO), (65, 52))

        rects_clicaveis = []
        for i, s in enumerate(self.sugestoes):
            r = pygame.Rect(50, 85 + (i*55), 350, 50)
            pygame.draw.rect(self.tela, (250, 250, 250), r, border_radius=5)
            pygame.draw.rect(self.tela, PRETO, r, 1, border_radius=5)
            # Imagem na sugestão aumentada para 45x45
            self.tela.blit(self.carregar_img_api(s["id"], (45, 45)), (55, 88 + (i*55)))
            self.tela.blit(self.fonte.render(s["nome"], True, PRETO), (110, 100 + (i*55)))
            rects_clicaveis.append((r, s))

        # Tabela (Cabeçalho)
        # Ajustei o espaçamento (agora 155px entre colunas)
        headers = ["Pokémon", "Nome", "Tipo 1", "Tipo 2", "Cor", "Habitat", "Altura", "Peso"]
        for i, h in enumerate(headers):
            self.tela.blit(self.fonte.render(h, True, CINZA_ESCURO), (50 + i*155, 360))

        # Renderização das Tentativas (Imagens Grandes)
        for idx, t in enumerate(self.tentativas[:5]):
            y = 400 + idx * 95 # Aumentei a distância entre linhas para 95px
            itens = [t["id"], t["nome"], t["t1"], t["t2"], t["cor"], t["hab"], t["alt"], t["pes"]]
            
            for i, item in enumerate(itens):
                rect = pygame.Rect(45 + i*155, y, 145, 85) # Box maior
                
                if i == 0: # Coluna da FOTO GRANDE
                    pygame.draw.rect(self.tela, PRETO, rect, border_radius=10)
                    # Imagem aumentada para 80x80
                    img_grande = self.carregar_img_api(item, (80, 80))
                    self.tela.blit(img_grande, (rect.x + 32, rect.y + 2))
                else:
                    cor = item[1] if isinstance(item, tuple) else CINZA_ESCURO
                    txt = item[0] if isinstance(item, tuple) else item
                    pygame.draw.rect(self.tela, cor, rect, border_radius=10)
                    txt_surf = self.fonte.render(str(txt), True, BRANCO)
                    self.tela.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - 8))

        if self.venceu:
            btn = pygame.Rect(550, 40, 200, 50)
            pygame.draw.rect(self.tela, PRETO, btn, border_radius=10)
            self.tela.blit(self.fonte.render("ACERTOU! PRÓXIMO", True, BRANCO), (btn.x+25, btn.y+15))
            return rects_clicaveis, btn
        
        return rects_clicaveis, None

    def executar(self):
        clock = pygame.time.Clock()
        while True:
            rects_sug, btn_prox = self.desenhar()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: return
                if ev.type == pygame.KEYDOWN and not self.venceu:
                    if ev.key == pygame.K_RETURN and self.sugestoes: self.enviar_palpite(self.sugestoes[0])
                    elif ev.key == pygame.K_BACKSPACE: self.texto_input = self.texto_input[:-1]
                    else: self.texto_input += ev.unicode
                    self.atualizar_sugestoes()
                
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    for r, p in rects_sug:
                        if r.collidepoint(ev.pos): self.enviar_palpite(p)
                    if self.venceu and btn_prox and btn_prox.collidepoint(ev.pos):
                        self.alvo = random.choice(BD_POKEMON)
                        self.tentativas, self.venceu = [], False

            pygame.display.flip()
            clock.tick(30)

if __name__ == "__main__":
    PokedleGame().executar()
