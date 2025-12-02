import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import unicodedata
import json
import os
from datetime import datetime
from PIL import Image, ImageTk

# --- CONFIGURAÇÕES E DADOS ---

ARQUIVO_RANKING = "ranking_harry_potter.json"

CORES = {
    "texto_ouro": "#d4af37",
    "vermelho": "#740001",
    "verde": "#1a472a",
    "azul": "#0e1a40",
    "tinta": "#f3e5ab",
    "cinza": "#333333",
    "branco": "#FFFFFF"
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
    if not texto:
        return ""
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(ch for ch in texto if not unicodedata.combining(ch))
    return texto.lower().strip()

def carregar_ranking():
    if not os.path.exists(ARQUIVO_RANKING):
        return []
    try:
        with open(ARQUIVO_RANKING, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return dados if isinstance(dados, list) else []
    except:
        return []

def salvar_ranking(nome, pontos):
    ranking = carregar_ranking()
    ranking.append({"nome": nome, "pontos": pontos, "data": datetime.now().strftime("%d/%m/%Y %H:%M")})
    ranking.sort(key=lambda x: x["pontos"], reverse=True)
    ranking = ranking[:10]
    with open(ARQUIVO_RANKING, "w", encoding="utf-8") as f:
        json.dump(ranking, f, ensure_ascii=False, indent=4)

# --- CLASSE PRINCIPAL ---

class HarryPotterGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Adivinhação Mágica - Harry Potter")
        self.root.geometry("800x900")

        # --- Canvas com imagem de fundo ---
        self.canvas = tk.Canvas(root, width=800, height=900, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        imagem_fundo = Image.open("animacoes/castello-di-harry-potter.jpg")
        imagem_fundo = imagem_fundo.resize((800, 900), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(imagem_fundo)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_img)

        # Estado do jogo
        self.tentativas = 0
        self.pontuacao_atual = 0
        self.personagem_atual = {}
        self.dicas_disponiveis = []
        self.idx_dica = 0

        self.var_dificuldade = tk.IntVar(value=2)  # padrão Médio
        self.criar_interface()
        self.iniciar_jogo()

    def criar_interface(self):
        # Título
        self.canvas.create_text(400, 40, text="⚡ Mundo Bruxo ⚡", font=("Times New Roman", 28, "bold"), fill=CORES["texto_ouro"])

        # Nível de dificuldade
        tk.Label(self.root, text="Escolha o nível de magia:", bg="#000000", fg="white", font=("Arial", 12, "bold")).place(x=20, y=90)
        tk.Radiobutton(self.root, text="Fácil (8)", variable=self.var_dificuldade, value=1, bg="#000000", fg="white", selectcolor=CORES["cinza"]).place(x=20, y=120)
        tk.Radiobutton(self.root, text="Médio (6)", variable=self.var_dificuldade, value=2, bg="#000000", fg="white", selectcolor=CORES["cinza"]).place(x=20, y=150)
        tk.Radiobutton(self.root, text="Difícil (4)", variable=self.var_dificuldade, value=3, bg="#000000", fg="white", selectcolor=CORES["cinza"]).place(x=20, y=180)

        # HUD
        self.lbl_tentativas = self.canvas.create_text(400, 220, text="⚡ Vidas: --", font=("Arial", 16, "bold"), fill=CORES["texto_ouro"])
        self.lbl_pontos = self.canvas.create_text(400, 260, text="Pontos Possíveis: 0", font=("Arial", 16), fill=CORES["branco"])

        # Log
        self.log_textos = []
        self.log_y = 300

        # Entrada do usuário
        self.entrada_var = tk.StringVar()
        self.entrada = tk.Entry(self.root, font=("Arial", 14), justify="center", textvariable=self.entrada_var, fg="white", bg="#000000", insertbackground="white", bd=0)
        self.entrada_window = self.canvas.create_window(400, 700, window=self.entrada, width=400, height=30)
        self.entrada.bind('<Return>', lambda e: self.verificar_palpite())

        # Botões
        self.btn_chutar = tk.Button(self.root, text="🪄 Chutar", command=self.verificar_palpite, bg=CORES["vermelho"], fg="white", font=("Arial", 12, "bold"), width=15, height=2)
        self.btn_chutar_window = self.canvas.create_window(250, 750, window=self.btn_chutar)
        self.btn_dica = tk.Button(self.root, text="🧪 Dica (-1 Vida)", command=self.usar_dica, bg=CORES["verde"], fg="white", font=("Arial", 12, "bold"), width=15, height=2)
        self.btn_dica_window = self.canvas.create_window(550, 750, window=self.btn_dica)

        # Botões de Novo Jogo e Ranking
        self.btn_novo = tk.Button(self.root, text="Novo Jogo", command=self.iniciar_jogo, bg=CORES["azul"], fg="white", font=("Arial", 10, "bold"), width=15)
        self.btn_novo_window = self.canvas.create_window(150, 800, window=self.btn_novo)
        self.btn_ranking = tk.Button(self.root, text="🏆 Ver Ranking", command=self.exibir_ranking_janela, bg=CORES["texto_ouro"], fg="black", font=("Arial", 10, "bold"), width=15)
        self.btn_ranking_window = self.canvas.create_window(650, 800, window=self.btn_ranking)

    # --- Funções de jogo ---
    def log_pergaminho(self, texto):
        self.log_textos.append(texto)
        if len(self.log_textos) > 10:
            self.log_textos.pop(0)
        self.canvas.delete("log")
        y = self.log_y
        for msg in self.log_textos:
            self.canvas.create_text(400, y, text=msg, font=("Courier New", 12, "bold"), fill=CORES["tinta"], tags="log")
            y += 20

    def iniciar_jogo(self):
        # Define tentativas baseado no nível
        escolha = self.var_dificuldade.get()
        self.tentativas = 8 if escolha == 1 else 6 if escolha == 2 else 4

        self.personagem_atual = random.choice(PERSONAGENS)
        self.nome_alvo = self.personagem_atual["nome"]

        dicas_brutas = [
            f"Casa: {self.personagem_atual['casa']}",
            f"Papel: {self.personagem_atual['papel']}",
            f"Inicial: {self.nome_alvo[0]}",
            f"Letras: {len(self.nome_alvo.replace(' ', ''))}",
        ]
        random.shuffle(dicas_brutas)
        melhor_dica = f"Papel: {self.personagem_atual['papel']}"
        if melhor_dica in dicas_brutas:
            dicas_brutas.remove(melhor_dica)
            dicas_brutas.insert(0, melhor_dica)
        self.dicas_disponiveis = dicas_brutas
        self.idx_dica = 0
        self.pontuacao_atual = 0

        self.atualizar_hud()
        self.log_textos.clear()
        self.log_pergaminho("📜 O Cálice de fogo escolheu um nome...")
        self.entrada_var.set("")
        self.entrada.config(state=tk.NORMAL)
        self.btn_chutar.config(state=tk.NORMAL)
        self.btn_dica.config(state=tk.NORMAL)
        self.entrada.focus()

    def atualizar_hud(self):
        self.canvas.itemconfig(self.lbl_tentativas, text=f"⚡ Vidas: {self.tentativas}")
        pts = 100 + (self.tentativas * 50)
        self.canvas.itemconfig(self.lbl_pontos, text=f"Pontos Possíveis: {pts}")

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
        palpite = self.entrada_var.get()
        if not palpite:
            return
        norm_palpite = normalizar(palpite)
        norm_alvo = normalizar(self.nome_alvo)

        if norm_palpite == "revelio":
            self.usar_dica()
            self.entrada_var.set("")
            return

        if norm_palpite == norm_alvo or (len(norm_palpite) > 3 and norm_palpite in norm_alvo.split()):
            self.vitoria()
        else:
            self.tentativas -= 1
            self.log_pergaminho(f"❌ '{palpite}' está incorreto.")
            self.entrada_var.set("")
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
        top = tk.Toplevel(self.root)
        top.title("🏆 Salão da Fama")
        top.geometry("400x500")
        top.configure(bg=None)
        tk.Label(top, text="Melhores Bruxos", font=("Cinzel", 20, "bold"), bg=None, fg=CORES["texto_ouro"]).pack(pady=20)
        dados = carregar_ranking()
        frame_lista = tk.Frame(top, bg=None)
        frame_lista.pack(fill="both", expand=True, padx=20)
        if not dados:
            tk.Label(frame_lista, text="Nenhum registro ainda.", bg=None, fg="white").pack()
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
                tk.Label(frame_lista, text=texto, font=("Courier New", 12, "bold"), bg=None, fg=cor, anchor="w").pack(fill="x", pady=2)
        tk.Button(top, text="Fechar", command=top.destroy, bg="#333", fg="white").pack(pady=20)

# --- EXECUÇÃO ---
if __name__ == "__main__":
    root = tk.Tk()
    app = HarryPotterGame(root)
    root.mainloop()
