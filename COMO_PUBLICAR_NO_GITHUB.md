# Como publicar este guia no GitHub

## Opção 1 - Pelo site do GitHub (mais fácil)

1. Crie um novo repositório em https://github.com/new
   - Nome sugerido: `como-consultar-periodo-de-ferias`
   - Marque como Público
   - Não marque "Add a README"

2. Clique em `uploading an existing file` ou `Add file > Upload files`

3. Arraste TODA a pasta `como-consultar-periodo-de-ferias`:
   - `README.md`
   - pasta `imagens` com as 4 imagens dentro

4. Clique em `Commit changes`

Pronto! O link do seu repositório será algo como:
`https://github.com/SEU-USUARIO/como-consultar-periodo-de-ferias`
É só enviar esse link para quem perguntar.

## Opção 2 - Pelo Git no computador

Abra o PowerShell dentro desta pasta e execute:

```powershell
git init
git add .
git commit -m "Adiciona guia visual de consulta de férias"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/como-consultar-periodo-de-ferias.git
git push -u origin main
```

> Substitua `SEU-USUARIO` pelo seu usuário do GitHub.
