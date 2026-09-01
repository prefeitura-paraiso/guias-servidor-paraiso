#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publicador GitHub - Guia Visual de Férias
------------------------------------------------
Executa:
  1. Verifica git e gh CLI
  2. Verifica autenticação no GitHub (gh auth status)
  3. Se não autenticado, abre o navegador para login (você autoriza)
  4. Cria repositório público e faz push
  5. Ativa GitHub Pages (index.html na raiz)

Uso:
  python publicar_github.py
  ou duplo clique no arquivo

Pasta do projeto: esta mesma pasta (onde está este .py)
"""

import subprocess
import sys
import os
import shutil
import time
import webbrowser
from pathlib import Path

# Cores para terminal (opcional)
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"

def run(cmd, cwd=None, check=False, capture=False):
    """Executa comando e retorna (returncode, stdout, stderr)"""
    try:
        if isinstance(cmd, str):
            # shell=True para comandos com pipe/&& no Windows
            result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=capture, text=True, encoding="utf-8", errors="ignore")
        else:
            result = subprocess.run(cmd, cwd=cwd, capture_output=capture, text=True, encoding="utf-8", errors="ignore")
        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        return result.returncode, result.stdout if capture else "", result.stderr if capture else ""
    except Exception as e:
        return 1, "", str(e)

def print_step(msg):
    print(f"\n{CYAN}▶ {msg}{RESET}")

def print_ok(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_warn(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")

def print_err(msg):
    print(f"{RED}✗ {msg}{RESET}")

def find_gh():
    """Encontra gh.exe"""
    gh = shutil.which("gh")
    if gh:
        return gh
    # caminhos comuns no Windows
    candidatos = [
        r"C:\Program Files\GitHub CLI\gh.exe",
        r"C:\Program Files (x86)\GitHub CLI\gh.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\*\gh.exe"),
    ]
    for c in candidatos:
        if os.path.isfile(c):
            return c
    # busca em WinGet Packages
    import glob
    for p in glob.glob(r"C:\Users\*\AppData\Local\Microsoft\WinGet\Packages\*\gh.exe", recursive=True):
        if os.path.isfile(p):
            return p
    for p in glob.glob(r"C:\Program Files\GitHub CLI\gh.exe"):
        if os.path.isfile(p):
            return p
    return None

def main():
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}  PUBLICADOR GITHUB - Guia Visual de Férias{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")

    projeto = Path(__file__).parent.resolve()
    print(f"\nPasta do projeto: {projeto}")
    print(f"Arquivos: {', '.join([p.name for p in projeto.iterdir() if p.is_file()][:6])} ...")
    imagens = projeto / "imagens"
    if imagens.exists():
        print(f"Imagens: {len(list(imagens.glob('*.png')))} encontradas")
    else:
        print_warn("Pasta 'imagens' não encontrada!")

    # 1. Verifica git
    print_step("1/5 Verificando Git...")
    rc, out, err = run("git --version", capture=True)
    if rc != 0:
        print_err("Git não encontrado. Instale https://git-scm.com/downloads")
        sys.exit(1)
    print_ok(out.strip() if out else "Git OK")

    # Verifica/define git config
    rc, name, _ = run("git config --global user.name", capture=True)
    rc2, email, _ = run("git config --global user.email", capture=True)
    if not name.strip() or not email.strip():
        print_warn("Configurando git user.name e user.email temporário...")
        run('git config --global user.name "RH Guia"', capture=False)
        run('git config --global user.email "guia@prefeitura.local"', capture=False)
    else:
        print_ok(f"Git user: {name.strip()} <{email.strip()}>")

    # Garante que a pasta é um repositório git
    if not (projeto / ".git").exists():
        print_step("Inicializando repositório git...")
        run("git init", cwd=str(projeto))
        run("git branch -M main", cwd=str(projeto))
        run("git add .", cwd=str(projeto))
        run('git commit -m "Publica guia visual: como consultar periodo de ferias no holerite"', cwd=str(projeto))
    else:
        print_ok("Repositório git já inicializado")
        # garante branch main
        run("git branch -M main", cwd=str(projeto))

    # 2. Verifica gh
    print_step("2/5 Verificando GitHub CLI (gh)...")
    gh = find_gh()
    if not gh:
        print_err("GitHub CLI (gh) não encontrado.")
        print("Instale por: winget install --id GitHub.cli")
        print("Ou baixe em: https://cli.github.com/")
        # tenta instalar via winget
        resp = input("Tentar instalar via winget agora? (s/n): ").strip().lower()
        if resp == "s":
            print("Instalando gh... (pode demorar 1 min)")
            run("winget install --id GitHub.cli --accept-package-agreements --accept-source-agreements", capture=False)
            gh = find_gh()
            if not gh:
                gh = r"C:\Program Files\GitHub CLI\gh.exe"
        if not gh or not os.path.isfile(gh):
            print_err("Não foi possível encontrar gh.exe. Instale manualmente e rode novamente.")
            sys.exit(1)
    print_ok(f"gh encontrado: {gh}")
    rc, out, _ = run(f'"{gh}" --version', capture=True)
    print(f"  {out.strip()}")

    # 3. Verifica autenticação
    print_step("3/5 Verificando autenticação no GitHub...")
    rc, out, err = run(f'"{gh}" auth status', capture=True)
    combinado = (out or "") + (err or "")
    if "Logged in" in combinado or "logged in" in combinado:
        print_ok("Você já está autenticado no GitHub!")
        print(f"  {combinado.strip()[:300]}")
    else:
        print_warn("Você NÃO está autenticado no GitHub.")
        print("  Para publicar, preciso que você autorize no navegador (1 clique).")
        print(f"\n{YELLOW}>>> VOU ABRIR O NAVEGADOR PARA LOGIN <<< {RESET}")
        print("  Se o navegador não abrir, copie o código que aparecer no terminal")
        print("  e cole no link: https://github.com/login/device\n")
        input(f"{CYAN}Pressione ENTER para iniciar o login...{RESET}")

        # Executa gh auth login --web interativo (precisa de interação real)
        print(f"\n{CYAN}Executando: gh auth login --web{RESET}")
        print(f"{YELLOW}>>> ATENÇÃO: Uma janela do navegador vai abrir. Autorize com o código exibido. <<<{RESET}\n")
        # Usa os.system para permitir interatividade total no terminal
        ret = os.system(f'"{gh}" auth login --web --skip-ssh-key')
        if ret != 0:
            print_warn("Login pode não ter completado. Verificando novamente...")
        # verifica de novo
        rc, out, err = run(f'"{gh}" auth status', capture=True)
        combinado = (out or "") + (err or "")
        if "Logged in" not in combinado:
            print_err("Ainda não autenticado.")
            print("Tente manualmente no PowerShell: gh auth login --web")
            print("Depois rode este script novamente: python publicar_github.py")
            sys.exit(1)
        print_ok("Autenticado com sucesso!")
        print(f"  {combinado.strip()[:300]}")

    # 4. Pergunta nome do repositório
    print_step("4/5 Criando repositório público no GitHub...")
    # tenta pegar usuário logado
    rc, out, _ = run(f'"{gh}" api user --jq .login', capture=True)
    usuario = out.strip() if rc == 0 and out.strip() else "SEU-USUARIO"
    print(f"  Usuário detectado: {usuario}")

    nome_default = "como-consultar-periodo-de-ferias"
    nome = input(f"Nome do repositório [{nome_default}]: ").strip()
    if not nome:
        nome = nome_default
    # sanitiza
    nome = nome.replace(" ", "-").lower()

    descricao = "Guia visual: como consultar periodo de ferias no holerite (passo a passo com imagens)"

    # Verifica se remote já existe
    rc, out, _ = run("git remote get-url origin", cwd=str(projeto), capture=True)
    if rc == 0 and out.strip():
        print_warn(f"Remote 'origin' já existe: {out.strip()}")
        resp = input("Deseja remover e recriar? (s/n) [n]: ").strip().lower()
        if resp == "s":
            run("git remote remove origin", cwd=str(projeto))
        else:
            print("Mantendo remote existente. Tentando apenas push...")
            # tenta push direto
            print_step("Fazendo git push...")
            rc, out, err = run("git push -u origin main", cwd=str(projeto), capture=True)
            if rc == 0:
                print_ok("Push realizado!")
            else:
                print_warn(f"Push falhou: {err or out}")
                print("Tente: gh repo create --push ou crie manualmente em https://github.com/new")
            # segue para Pages
            nome = out.strip().split("/")[-1].replace(".git","") if out else nome

    # Cria repo se não existe
    if not (run("git remote get-url origin", cwd=str(projeto), capture=True)[0] == 0):
        print(f"  Criando repositório '{nome}' como público...")
        # gh repo create com --source=. --push já faz tudo
        cmd = f'"{gh}" repo create {nome} --public --source="." --remote=origin --push --description "{descricao}"'
        print(f"  Executando: gh repo create {nome} --public --source=. --remote=origin --push")
        rc, out, err = run(cmd, cwd=str(projeto), capture=True)
        combinado = (out or "") + (err or "")
        print(combinado)
        if rc != 0:
            if "already exists" in combinado.lower() or "already_exists" in combinado.lower():
                print_warn("Repositório já existe no GitHub. Configurando remote...")
                # tenta pegar URL correta
                rc2, url, _ = run(f'"{gh}" repo view {usuario}/{nome} --json url --jq .url', capture=True)
                if rc2 == 0 and url.strip():
                    remote_url = f"https://github.com/{usuario}/{nome}.git"
                    run(f'git remote add origin "{remote_url}"', cwd=str(projeto))
                    run("git push -u origin main", cwd=str(projeto), capture=False)
                else:
                    print_err("Não foi possível configurar remote. Crie manualmente em https://github.com/new")
                    sys.exit(1)
            else:
                print_err("Falha ao criar repositório.")
                print("Detalhe:", combinado[:800])
                print("\nAlternativa manual:")
                print(f"  1. Crie em https://github.com/new com nome '{nome}' (público, vazio)")
                print(f"  2. Depois execute:")
                print(f'     git remote add origin https://github.com/{usuario}/{nome}.git')
                print(f'     git push -u origin main')
                sys.exit(1)
        else:
            print_ok(f"Repositório criado e push realizado: https://github.com/{usuario}/{nome}")

    # 5. Ativa GitHub Pages
    print_step("5/5 Ativando GitHub Pages (página pública)...")
    # gh api para criar Pages
    rc, out, err = run(f'"{gh}" api repos/{usuario}/{nome}/pages -X POST -f source[branch]=main -f source[path]=/ 2>&1', capture=True)
    combinado = (out or "") + (err or "")
    if rc == 0:
        print_ok("GitHub Pages ativado (branch main, pasta /)")
    else:
        if "already exists" in combinado.lower() or "exists" in combinado.lower():
            print_ok("Pages já estava ativo")
        else:
            print_warn(f"Não foi possível ativar Pages via API (pode ativar manualmente). Detalhe: {combinado[:400]}")
            print(f"  Ative manualmente em: https://github.com/{usuario}/{nome}/settings/pages")
            print(f"  Branch: main  /  Pasta: / (root)  -> Save")

    # Abre no navegador
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}  ✓ PUBLICADO COM SUCESSO!{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    url_repo = f"https://github.com/{usuario}/{nome}"
    url_pages = f"https://{usuario}.github.io/{nome}/"
    print(f"\n  Repositório: {url_repo}")
    print(f"  Página pública (GitHub Pages): {url_pages}")
    print(f"  (Pages pode levar 1-2 minutos para ficar no ar na primeira vez)")
    print(f"\n  Para atualizar depois, basta:")
    print(f"    git add . && git commit -m \"atualiza guia\" && git push")
    print(f"\n  Para compartilhar, envie o link da página: {url_pages}")
    print()

    try:
        webbrowser.open(url_repo)
        time.sleep(1)
        webbrowser.open(url_pages)
    except:
        pass

    # Verifica status final
    print_step("Git pull de verificação...")
    rc, out, err = run("git pull --rebase", cwd=str(projeto), capture=True)
    print(out or err or "pull OK")

    input(f"\n{CYAN}Pressione ENTER para sair...{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelado pelo usuário.")
        sys.exit(0)
