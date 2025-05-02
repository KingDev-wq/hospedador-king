import os
import subprocess
import json
import threading
import requests
from time import sleep
from datetime import datetime

ascii_art = r'''
   ____        _     _     _           
  |  _ \ _   _| |__ | |__ (_)_ __  ___ 
  | |_) | | | | '_ \| '_ \| | '_ \/ __|
  |  __/| |_| | |_) | |_) | | | | \__ \
  |_|    \__,_|_.__/|_.__/|_|_| |_|___/
     Painel de Hospedagem - CLI Bots
'''

BOTS_FOLDER = "bots"
CONFIG_FILE = "bots/config.json"
processos = {}

# Garante que pastas existem
os.makedirs(BOTS_FOLDER, exist_ok=True)
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f:
        json.dump({}, f)

def carregar_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def salvar_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def enviar_log(linha):
    if os.path.exists("webhook.txt"):
        with open("webhook.txt", "r") as w:
            url = w.read().strip()
            if url.startswith("http"):
                try:
                    requests.post(url, json={"content": linha[:1900]})
                except Exception as e:
                    print(f"Erro ao enviar webhook: {e}")

def listar_bots(config):
    print("\nBots disponíveis:")
    for i, nome in enumerate(config, 1):
        print(f"{i}. {nome}")
    return list(config.keys())

def iniciar_bot(config):
    nomes = listar_bots(config)
    escolha = input("Digite o número do bot que deseja iniciar: ")
    if not escolha.isdigit() or int(escolha) not in range(1, len(nomes)+1):
        print("Escolha inválida.")
        sleep(1)
        return
    nome = nomes[int(escolha)-1]
    caminho = config[nome]
    if nome in processos:
        print("Esse bot já está em execução.")
        sleep(1)
        return

    print(f"Iniciando bot '{nome}'...")
    processos[nome] = subprocess.Popen(
        ["python", caminho],
        cwd=os.path.dirname(caminho),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    def monitorar_output(proc, nome):
        for linha in proc.stdout:
            if linha.strip():
                timestamp = datetime.now().strftime('%H:%M:%S')
                log = f"[{timestamp}] [{nome}] {linha.strip()}"
                print(log)
                enviar_log(log)

    threading.Thread(target=monitorar_output, args=(processos[nome], nome), daemon=True).start()
    sleep(1)

def parar_bot():
    if not processos:
        print("Nenhum bot em execução.")
        sleep(1)
        return
    print("\nBots em execução:")
    for i, nome in enumerate(processos, 1):
        print(f"{i}. {nome}")
    escolha = input("Digite o número do bot que deseja parar: ")
    if not escolha.isdigit() or int(escolha) not in range(1, len(processos)+1):
        print("Escolha inválida.")
        sleep(1)
        return
    nome = list(processos.keys())[int(escolha)-1]
    print(f"Parando bot '{nome}'...")
    processos[nome].terminate()
    del processos[nome]
    sleep(1)

def reiniciar_bot(config):
    if not processos:
        print("Nenhum bot em execução.")
        return
    parar_bot()
    iniciar_bot(config)

def adicionar_bot(config):
    os.system("clear" if os.name == "posix" else "cls")
    print(ascii_art)
    nome = input("ADICIONE NOME DO BOT: ").strip()
    if nome in config:
        print("Já existe um bot com esse nome.")
        return
    repo = input("ENVIE REPOSITÓRIO DO BOT (link GitHub): ").strip()
    pasta_destino = os.path.join(BOTS_FOLDER, nome.replace(" ", "_"))
    print(f"Clonando repositório em '{pasta_destino}'...")
    os.system(f"git clone {repo} {pasta_destino}")
    arquivo_principal = input("Digite o nome do arquivo principal do bot (ex: main.py): ").strip()
    caminho = os.path.join(pasta_destino, arquivo_principal)

    # Espera o arquivo aparecer por até 10 segundos
    espera = 0
    while not os.path.exists(caminho) and espera < 10:
        print("Aguardando o repositório terminar de baixar...")
        sleep(1)
        espera += 1

    if not os.path.exists(caminho):
        print("Arquivo principal não encontrado. Verifique o nome e se o repositório foi clonado corretamente.")
        return

    config[nome] = caminho
    salvar_config(config)
    print(f"Bot '{nome}' adicionado com sucesso.")
    sleep(2)

def menu():
    while True:
        os.system("clear" if os.name == "posix" else "cls")
        print(ascii_art)
        print("1. Iniciar Bot")
        print("2. Parar Bot")
        print("3. Reiniciar Bot")
        print("4. Adicionar Bot via GitHub")
        print("5. Sair")
        opcao = input("\nEscolha uma opção: ")

        config = carregar_config()

        if opcao == "1":
            iniciar_bot(config)
        elif opcao == "2":
            parar_bot()
        elif opcao == "3":
            reiniciar_bot(config)
        elif opcao == "4":
            adicionar_bot(config)
        elif opcao == "5":
            print("Saindo...")
            break
        else:
            print("Opção inválida.")
            sleep(1)

if __name__ == "__main__":
    menu()
