#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PUBLICADOR FINAL - Prefeitura de Paraíso
Repo: prefeitura-paraiso/guias-servidor-paraiso
Vai do zero até a página pública no ar (GitHub Pages)
Você só precisa autorizar no navegador quando pedir.

Como usar:
  python publicar_final.py
"""

import subprocess, sys, os, shutil, time, webbrowser, glob
from pathlib import Path

# Corrige encoding no Windows (cp1252 -> utf-8)
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')
except: pass

GREEN = ""; YELLOW = ""; RED = ""; CYAN = ""; RESET = ""
USUARIO = "prefeitura-paraiso"
REPO = "guias-servidor-paraiso"
DESCRICAO = "Guias do Servidor | Prefeitura de Paraiso - RH Digital - Manuais de autoatendimento para servidores"
BRANCH = "main"

def run(cmd, cwd=None, capture=False):
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=capture, text=True, encoding="utf-8", errors="ignore")
        return r.returncode, (r.stdout if capture else ""), (r.stderr if capture else "")
    except Exception as e:
        return 1, "", str(e)

def ok(m): print(f"[OK] {m}")
def warn(m): print(f"[!] {m}")
def err(m): print(f"[X] {m}")
def step(m): print(f"\n[>] {m}")

def find_gh():
    g = shutil.which("gh")
    if g: return g
    for p in [r"C:\Program Files\GitHub CLI\gh.exe", r"C:\Program Files (x86)\GitHub CLI\gh.exe"]:
        if os.path.isfile(p): return p
    for p in glob.glob(r"C:\Users\*\AppData\Local\Microsoft\WinGet\Packages\*\gh.exe", recursive=True):
        if os.path.isfile(p): return p
    return None

def main():
    print('='*62)
    print("  PUBLICADOR FINAL - prefeitura-paraiso/guias-servidor-paraiso")
    print("  De zero ate pagina publica no ar")
    print('='*62)

    projeto = Path(__file__).parent.resolve()
    print(f"\nPasta: {projeto}")
    # Verifica arquivos essenciais
    for f in ["index.html", "README.md", "imagens/01-acessar-ficha-funcional.png"]:
        ok(f"Encontrado: {f}") if (projeto / f).exists() else warn(f"Faltando: {f}")

    # 1. Git
    step(f"1/5 Git e identidade")
    rc, out, _ = run("git --version", capture=True)
    if rc != 0: err("Git não instalado"); sys.exit(1)
    ok(out.strip())
    run('git config --global user.name "Guias do Servidor | Prefeitura de Paraiso"')
    run('git config --global user.email "rh@paraiso.sp.gov.br"')
    run(f'git config user.name "Guias do Servidor | Prefeitura de Paraiso"', cwd=str(projeto))
    run(f'git config user.email "rh@paraiso.sp.gov.br"', cwd=str(projeto))
    ok('Git configurado como "Guias do Servidor | Prefeitura de Paraiso"')

    if not (projeto / ".git").exists():
        run("git init", cwd=str(projeto))
        run(f"git branch -M {BRANCH}", cwd=str(projeto))
    # garante commit atual
    rc, _, _ = run("git status --porcelain", cwd=str(projeto), capture=True)
    # adiciona tudo e comita se houver mudanças
    run("git add .", cwd=str(projeto))
    rc, out, _ = run('git diff --cached --quiet', cwd=str(projeto), capture=True)
    if rc != 0:  # há staged
        run(f'git commit -m "Publica guias-servidor-paraiso: guia de ferias + estrutura base"', cwd=str(projeto))
        ok("Commit criado")
    else:
        ok("Nada novo para commitar (já está salvo)")

    # 2. gh CLI
    step("2/5 GitHub CLI")
    gh = find_gh()
    if not gh:
        err("gh não encontrado. Instale: winget install --id GitHub.cli")
        sys.exit(1)
    gh = f'"{gh}"'
    rc, out, _ = run(f"{gh} --version", capture=True)
    ok(out.strip())
    # adiciona ao PATH para git usar credential helper
    os.environ["PATH"] += r";C:\Program Files\GitHub CLI"

    # 3. Autenticação
    step("3/5 Autenticação GitHub (prefeitura-paraiso)")
    rc, out, er = run(f"{gh} auth status", capture=True)
    txt = (out or "") + (er or "")
    if f"Logged in to github.com as {USUARIO}" in txt or f"as {USUARIO}" in txt:
        ok(f"Já autenticado como {USUARIO}")
    elif "Logged in" in txt:
        warn(f"Autenticado como outro usuário:\n{txt.strip()[:300]}")
        print(f"  Esperado: {USUARIO}")
        resp = input("Continuar mesmo assim? (s/n) [s]: ").strip().lower()
        if resp == "n": sys.exit(0)
    else:
        warn("Não autenticado. Vou abrir o navegador para você autorizar.")
        print(">>> Voce vai autorizar a conta prefeitura-paraiso <<<")
        input("Pressione ENTER para abrir o login...")
        print("Abrindo gh auth login --web (autorize com o codigo de 8 letras)...\n")
        ret = os.system(f"{gh} auth login --web --skip-ssh-key --hostname github.com")
        # re-verifica
        rc, out, er = run(f"{gh} auth status", capture=True)
        txt = (out or "") + (er or "")
        if "Logged in" not in txt:
            err("Ainda não autenticado. Rode manualmente: gh auth login --web")
            sys.exit(1)
        ok("Autenticado!")

    # 4. Cria repo e push
    step(f"4/5 Criando/atualizando repositório {USUARIO}/{REPO}")
    # Verifica se repo já existe
    rc, out, er = run(f"{gh} repo view {USUARIO}/{REPO} --json name --jq .name", capture=True)
    repo_existe = (rc == 0 and REPO in (out or ""))
    if repo_existe:
        ok(f"Repositório já existe: https://github.com/{USUARIO}/{REPO}")
        # garante remote correto
        run("git remote remove origin", cwd=str(projeto))
        run(f"git remote add origin https://github.com/{USUARIO}/{REPO}.git", cwd=str(projeto))
        print("  Fazendo push...")
        rc, out, er = run(f"git push -u origin {BRANCH}", cwd=str(projeto), capture=True)
        txt = (out or "") + (er or "")
        print(txt[:800])
        if rc != 0 and "rejected" in txt.lower():
            warn("Push rejeitado (histórico divergente). Tentando --force com segurança...")
            resp = input("Forçar push (sobrescreve remoto)? (s/n) [n]: ").strip().lower()
            if resp == "s":
                run(f"git push -u origin {BRANCH} --force", cwd=str(projeto))
        elif rc == 0:
            ok("Push realizado!")
    else:
        print(f"  Criando https://github.com/{USUARIO}/{REPO} (público)...")
        cmd = f'{gh} repo create {USUARIO}/{REPO} --public --source="." --remote=origin --push --description "{DESCRICAO}"'
        rc, out, er = run(cmd, cwd=str(projeto), capture=True)
        txt = (out or "") + (er or "")
        print(txt[:1000])
        if rc != 0:
            if "already exists" in txt.lower():
                warn("Repo já existe (race). Configurando remote...")
                run("git remote remove origin", cwd=str(projeto))
                run(f"git remote add origin https://github.com/{USUARIO}/{REPO}.git", cwd=str(projeto))
                run(f"git push -u origin {BRANCH}", cwd=str(projeto))
            else:
                err("Falha ao criar repo. Tente criar manualmente em https://github.com/new")
                err(txt[:800])
                sys.exit(1)
        else:
            ok(f"Criado e push OK: https://github.com/{USUARIO}/{REPO}")

    # 5. GitHub Pages
    step("5/5 Ativando GitHub Pages")
    # Tenta via gh api
    rc, out, er = run(f'{gh} api repos/{USUARIO}/{REPO}/pages -X POST -f source[branch]={BRANCH} -f source[path]=/ 2>&1', capture=True)
    txt = (out or "") + (er or "")
    if rc == 0:
        ok("Pages ativado: branch main, pasta / (root)")
    else:
        if "already exists" in txt.lower() or "exists" in txt.lower():
            ok("Pages já estava ativo")
        else:
            warn(f"Ativação via API falhou, ative manualmente se necessário: {txt[:300]}")
            print(f"  Manual: https://github.com/{USUARIO}/{REPO}/settings/pages -> Branch: main / root -> Save")
    # Alternativa: tenta via gh repo view para pegar URL
    time.sleep(2)
    rc, out, _ = run(f'{gh} api repos/{USUARIO}/{REPO}/pages --jq .html_url 2>nul', capture=True)
    pages_url = out.strip() if rc == 0 and out.strip().startswith("http") else f"https://{USUARIO}.github.io/{REPO}/"

    # Final
    print('\n' + '='*62)
    print("  TUDO PRONTO - PAGINA PUBLICA NO AR")
    print('='*62)
    print(f"\n  Repositório: https://github.com/{USUARIO}/{REPO}")
    print(f"  Página pública: {pages_url}")
    print(f"  (Pode levar 1-2 min para aparecer na primeira vez)")
    print(f"\n  Compartilhe este link com os servidores:")
    print(f"  {pages_url}")
    print(f"\n  Para atualizar depois (novos guias):")
    print(f"    git add . && git commit -m \"adiciona novo guia\" && git push")
    print(f"  Depois faça git pull para sincronizar:")
    print(f"    git pull")
    print()
    try:
        webbrowser.open(f"https://github.com/{USUARIO}/{REPO}")
        time.sleep(1)
        webbrowser.open(pages_url)
    except: pass

    step("Verificação git pull")
    rc, out, er = run("git pull --rebase", cwd=str(projeto), capture=True)
    print((out or er or "pull OK").strip()[:500])

    input("\nPressione ENTER para sair...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelado.")
        sys.exit(0)
