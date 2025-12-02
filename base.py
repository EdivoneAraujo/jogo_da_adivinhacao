import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import unicodedata
import json
import os
from datetime import datetime

# --- CONFIGURAÇÕES E DADOS ---

ARQUIVO_RANKING = "ranking_harry_potter.json"

CORES = {
    "fundo": "#1a1a1d",
    "texto_ouro": "#d4af37",
    "vermelho": "#740001",
    "verde": "#1a472a",
    "azul": "#0e1a40",
    "pergaminho": "#f3e5ab",
    "tinta": "#2b1b17",
    "cinza": "#333333"
}

PERSONAGENS = [
    {"nome": "Harry Potter", "casa": "Gryffindor", "papel": "O protagonista"},
    {"nome": "Hermione Granger", "casa": "Gryffindor", "papel": "Estudante brilhante"},
    {"nome": "Ron Weasley", "casa": "Gryffindor", "papel": "Melhor amigo"},
    {"nome": "Albus Dumbledore", "casa": "Gryffindor", "papel": "Diretor de Hogwarts"},
    {"nome": "Severus Snape", "casa": "Slytherin", "papel": "Professor de Poções"},
    {"nome": "Sirius Black", "casa": "Gryffindor", "papel": "Padrinho do Harry"},
    {"nome": "Rubeus Hagrid", "casa": "Gryffindor", "papel": "Guarda-caça"},
    {"nome": "Draco Malfoy", "casa": "Slytherin", "papel": "Rival do Harry"},
    {"nome": "Lord Voldemort", "casa": "Slytherin", "papel": "Antagonista"},
    {"nome": "Neville Longbottom", "casa": "Gryffindor", "papel": "Herói improvável"},
    {"nome": "Luna Lovegood", "casa": "Ravenclaw", "papel": "Estudante excêntrica"},
    {"nome": "Ginny Weasley", "casa": "Gryffindor", "papel": "Irmã do Ron"},
    {"nome": "Minerva McGonagall", "casa": "Gryffindor", "papel": "Professora de Transfiguração"},
    {"nome": "Remus Lupin", "casa": "Gryffindor", "papel": "Professor e lobisomem"},
    {"nome": "Bellatrix Lestrange", "casa": "Slytherin", "papel": "Comensal da Morte"},
    {"nome": "Dobby", "casa": "Nenhuma", "papel": "Elfo Doméstico"},
]

# --- FUNÇÕES UTILITÁRIAS ---

def normalizar(texto):
    """Remove acentos e deixa minúsculo para comparação."""
    if not texto:
        return ""
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(ch for ch in texto if not unicodedata.combining(ch))
    return texto.lower().strip()

def carregar_ranking():
    """Lê o ranking do arquivo JSON."""
    if not os.path.exists(ARQUIVO_RANKING):
        return []
    try:
        with open(ARQUIVO_RANKING, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def salvar_ranking(nome, pontos):
    """Salva a nova pontuação no arquivo JSON."""
    ranking = carregar_ranking()
    ranking.append({
        "nome": nome,
        "pontos": pontos,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
    })
    # Ordena do maior para o menor
    ranking.sort(key=lambda x: x["pontos"], reverse=True)
    # Mantém apenas os top 10
    ranking = ranking[:10]
    
    with open(ARQUIVO_RANKING, "w", encoding="utf-8") as f:
        json.dump(ranking, f, ensure_ascii=False, indent=4)

# --- CLASSE PRINCIPAL ---

class HarryPotterGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Adivinhação Mágica - Harry Potter")
        self.root.geometry("600x700")
        self.root.configure(bg=CORES["fundo"])

        # Estado do Jogo
        self.tentativas = 0
        self.pontuacao_atual = 0
        self.personagem_atual = {}
        self.dicas_disponiveis = []
        self.idx_dica = 0
        
        self.criar_interface()
        self.iniciar_jogo()

    def criar_interface(self):
        # Título
        tk.Label(self.root, text="⚡ Mundo Bruxo ⚡", font=("Times New Roman", 28, "bold"), 
                bg=CORES["fundo"], fg=CORES["texto_ouro"]).pack(pady=15)

        # Frame de Controles Superiores
        frame_top = tk.Frame(self.root, bg=CORES["fundo"])
        frame_top.pack(fill="x", padx=20)

        # Seletor de Dificuldade
        self.var_dificuldade = tk.IntVar(value=2)
        frame_dif = tk.LabelFrame(frame_top, text="Nível de Magia", bg=CORES["fundo"], fg="white", font=("Arial", 10))
        frame_dif.pack(side=tk.LEFT, padx=10)
        
        tk.Radiobutton(frame_dif, text="Fácil (8)", variable=self.var_dificuldade, value=1, 
                    bg=CORES["fundo"], fg="white", selectcolor=CORES["cinza"]).pack(anchor="w")
        tk.Radiobutton(frame_dif, text="Médio (6)", variable=self.var_dificuldade, value=2, 
                    bg=CORES["fundo"], fg="white", selectcolor=CORES["cinza"]).pack(anchor="w")
        tk.Radiobutton(frame_dif, text="Difícil (4)", variable=self.var_dificuldade, value=3, 
                    bg=CORES["fundo"], fg="white", selectcolor=CORES["cinza"]).pack(anchor="w")

        # Botões de Controle (Novo Jogo / Ranking)
        frame_btns_top = tk.Frame(frame_top, bg=CORES["fundo"])
        frame_btns_top.pack(side=tk.RIGHT, padx=10)

        tk.Button(frame_btns_top, text="Novo Jogo", command=self.iniciar_jogo, 
                bg=CORES["azul"], fg="white", font=("Arial", 10, "bold"), width=15).pack(pady=2)
        
        tk.Button(frame_btns_top, text="🏆 Ver Ranking", command=self.exibir_ranking_janela, 
                bg=CORES["texto_ouro"], fg="black", font=("Arial", 10, "bold"), width=15).pack(pady=2)

        # Placar (HUD)
        self.frame_hud = tk.Frame(self.root, bg=CORES["fundo"])
        self.frame_hud.pack(pady=15)
        
        self.lbl_tentativas = tk.Label(self.frame_hud, text="Vidas: --", font=("Arial", 16, "bold"), bg=CORES["fundo"], fg=CORES["texto_ouro"])
        self.lbl_tentativas.pack(side=tk.LEFT, padx=20)
        
        self.lbl_pontos = tk.Label(self.frame_hud, text="Pontos: 0", font=("Arial", 16), bg=CORES["fundo"], fg="white")
        self.lbl_pontos.pack(side=tk.LEFT, padx=20)

        # Área de Texto (Pergaminho)
        self.txt_log = tk.Text(self.root, height=10, bg=CORES["pergaminho"], fg=CORES["tinta"], 
                            font=("Courier New", 12, "bold"), padx=10, pady=10)
        self.txt_log.pack(fill="both", padx=30, pady=10)
        self.txt_log.config(state=tk.DISABLED)

        # Área de Input
        tk.Label(self.root, text="Quem é o personagem?", bg=CORES["fundo"], fg="white", font=("Arial", 12)).pack()
        
        self.entrada = tk.Entry(self.root, font=("Arial", 14), justify="center", bg="#333", fg="white", insertbackground="white")
        self.entrada.pack(pady=5, ipadx=50, ipady=5)
        self.entrada.bind('<Return>', lambda e: self.verificar_palpite())

        # Botões de Ação Inferiores
        frame_acao = tk.Frame(self.root, bg=CORES["fundo"])
        frame_acao.pack(pady=20)

        self.btn_chutar = tk.Button(frame_acao, text="🪄 Chutar", command=self.verificar_palpite, 
                                    bg=CORES["vermelho"], fg="white", font=("Arial", 12, "bold"), width=15, height=2)
        self.btn_chutar.pack(side=tk.LEFT, padx=10)

        self.btn_dica = tk.Button(frame_acao, text="🧪 Dica (-1 Vida)", command=self.usar_dica, 
                            bg=CORES["verde"], fg="white", font=("Arial", 12, "bold"), width=15, height=2)
        self.btn_dica.pack(side=tk.LEFT, padx=10)

    def log_pergaminho(self, texto):
        self.txt_log.config(state=tk.NORMAL)
        self.txt_log.insert(tk.END, texto + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state=tk.DISABLED)

    def iniciar_jogo(self):
        escolha = self.var_dificuldade.get()
        if escolha == 1:
            self.tentativas = 8
        elif escolha == 2:
            self.tentativas = 6
        else:
            self.tentativas = 4

        self.personagem_atual = random.choice(PERSONAGENS)
        self.nome_alvo = self.personagem_atual["nome"]
        
        dicas_brutas = [
            f"Casa: {self.personagem_atual['casa']}",
            f"Papel: {self.personagem_atual['papel']}",
            f"Inicial: {self.nome_alvo[0]}",
            f"Letras: {len(self.nome_alvo.replace(' ', ''))}",
        ]
        random.shuffle(dicas_brutas)
        # Garante que a primeira dica seja 'Papel' ou 'Casa' para não ser muito difícil
        melhor_dica = f"Papel: {self.personagem_atual['papel']}"
        if melhor_dica in dicas_brutas:
            dicas_brutas.remove(melhor_dica)
            dicas_brutas.insert(0, melhor_dica)
            
        self.dicas_disponiveis = dicas_brutas
        self.idx_dica = 0
        self.pontuacao_atual = 0

        self.atualizar_hud()
        self.txt_log.config(state=tk.NORMAL)
        self.txt_log.delete(1.0, tk.END)
        self.log_pergaminho("📜 O Cálice de fogo escolheu um nome...")
        self.entrada.delete(0, tk.END)
        self.entrada.config(state=tk.NORMAL)
        self.entrada.focus()
        self.btn_chutar.config(state=tk.NORMAL)
        self.btn_dica.config(state=tk.NORMAL)

    def atualizar_hud(self):
        self.lbl_tentativas.config(text=f"⚡ Vidas: {self.tentativas}")
        
        # Pontuação dinâmica: 100 base + 50 por vida restante
        pts = 100 + (self.tentativas * 50)
        self.lbl_pontos.config(text=f"Pontos Possíveis: {pts}")

    def usar_dica(self):
        if self.tentativas <= 1:
            messagebox.showwarning("Atenção", "Magia insuficiente para usar Veritaserum!")
            return

        if self.idx_dica >= len(self.dicas_disponiveis):
            self.log_pergaminho("⚠️ Não há mais dicas!")
            return

        self.tentativas -= 1
        dica = self.dicas_disponiveis[self.idx_dica]
        self.idx_dica += 1
        self.log_pergaminho(f"🧪 Dica: {dica}")
        self.atualizar_hud()

    def verificar_palpite(self):
        palpite = self.entrada.get()
        if not palpite:
            return

        norm_palpite = normalizar(palpite)
        norm_alvo = normalizar(self.nome_alvo)

        # Cheat code
        if norm_palpite == "revelio":
            self.usar_dica()
            self.entrada.delete(0, tk.END)
            return

        if norm_palpite == norm_alvo or (len(norm_palpite) > 3 and norm_palpite in norm_alvo.split()):
            self.vitoria()
        else:
            self.tentativas -= 1
            self.log_pergaminho(f"❌ '{palpite}' está incorreto.")
            self.entrada.delete(0, tk.END)
            self.atualizar_hud()

            if self.tentativas == 0:
                self.derrota()

    def vitoria(self):
        pontos_finais = 100 + (self.tentativas * 50)
        self.log_pergaminho(f"✨ ACERTOU! É {self.nome_alvo}!")
        self.log_pergaminho(f"🏆 Pontuação: {pontos_finais}")
        
        self.entrada.config(state=tk.DISABLED)
        self.btn_chutar.config(state=tk.DISABLED)
        self.btn_dica.config(state=tk.DISABLED)
        
        messagebox.showinfo("Vitória!", f"Parabéns!\nVocê descobriu: {self.nome_alvo}\nPontos: {pontos_finais}")

        # --- AQUI ESTÁ O USO DO SIMPLEDIALOG ---
        nome = simpledialog.askstring("Recorde Mágico", "Digite seu nome para o Ranking:", parent=self.root)
        
        if nome:
            salvar_ranking(nome, pontos_finais)
            self.exibir_ranking_janela()

    def derrota(self):
        self.log_pergaminho(f"💀 Perdeu. Era {self.nome_alvo}.")
        self.entrada.config(state=tk.DISABLED)
        self.btn_chutar.config(state=tk.DISABLED)
        self.btn_dica.config(state=tk.DISABLED)
        messagebox.showerror("Fim de Jogo", f"Suas vidas acabaram.\nO personagem era: {self.nome_alvo}")

    def exibir_ranking_janela(self):
        # Cria uma nova janela (pop-up)
        top = tk.Toplevel(self.root)
        top.title("🏆 Salão da Fama")
        top.geometry("400x500")
        top.configure(bg=CORES["azul"])

        tk.Label(top, text="Melhores Bruxos", font=("Cinzel", 20, "bold"), 
                bg=CORES["azul"], fg=CORES["texto_ouro"]).pack(pady=20)

        dados = carregar_ranking()

        frame_lista = tk.Frame(top, bg=CORES["azul"])
        frame_lista.pack(fill="both", expand=True, padx=20)

        if not dados:
            tk.Label(frame_lista, text="Nenhum registro ainda.", bg=CORES["azul"], fg="white").pack()
        else:
            for i, reg in enumerate(dados):
                cor = "white"
                prefixo = f"{i+1}."
                if i == 0: 
                    cor = CORES["texto_ouro"]
                    prefixo = "🥇"
                elif i == 1:
                    prefixo = "🥈"
                elif i == 2:
                    prefixo = "🥉"

                texto = f"{prefixo} {reg['nome']} - {reg['pontos']} pts"
                tk.Label(frame_lista, text=texto, font=("Courier New", 12, "bold"), 
                        bg=CORES["azul"], fg=cor, anchor="w").pack(fill="x", pady=2)

        tk.Button(top, text="Fechar", command=top.destroy, bg="#333", fg="white").pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = HarryPotterGame(root)
    root.mainloop()