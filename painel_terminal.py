import os
import subprocess
import json
from time import sleep

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
        return
    print(f"Iniciando bot '{nome}'...")
    processos[nome] = subprocess.Popen(
        ["python", caminho],
        cwd=os.path.dirname(caminho),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    import threading
    import requests

    def enviar_log(linha):
        if os.path.exists("webhook.txt"):
            with open("webhook.txt", "r") as w:
                url = w.read().strip()
                if url.startswith("http"):
                    try:
                        requests.post(url, json={"content": linha[:1900]})
                    except:
                        pass

    def monitorar_output(proc, nome):
        for linha in proc.stdout:
            print(f"[{nome}] {linha}", end="")
            enviar_log(f"[{nome}] {linha}")

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
    parar_bot()
    iniciar_bot(config)

def adicionar_bot(config):
    os.system("clear" if os.name == "posix" else "cls")
    print(ascii_art)
    
    nome = input("ADICIONE NOME DO BOT: ").strip()
    if nome in config:
        print("Já existe um bot com esse nome.")
        return
    
    # Caminho manual do bot no iPhone
    pasta_destino = input("Digite o caminho da pasta do bot (ex: /mnt/Meu iPhone/Arquivos/BotFolder): ").strip()
    
    if not os.path.isdir(pasta_destino):
        print(f"A pasta '{pasta_destino}' não existe.")
        return

    arquivo_principal = input("Digite o nome do arquivo principal do bot (ex: main.py): ").strip()
    caminho = os.path.join(pasta_destino, arquivo_principal)

    if not os.path.exists(caminho):
        print("Arquivo principal não encontrado. Verifique o nome e o caminho.")
        return

    # Adiciona o bot no config
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
        print("4. Adicionar Bot Manualmente")
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
