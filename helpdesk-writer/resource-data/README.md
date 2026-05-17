# Tryon Helpdesk Writer (skill do Claude Code)

Skill do Claude Code para criar artigos da central de ajuda do Tryon (Neuralyn) cruzando três fontes de verdade — **código**, **UI real no sandbox** e **guia de voz** — antes de publicar no Chatwoot via MCP.

## Instalação

```bash
# 1. Copiar a skill para o diretório global do Claude Code
cp -r tryon-helpdesk-writer ~/.claude/skills/

# 2. Instalar os MCPs necessários
claude mcp add playwright npx @playwright/mcp@latest
# (o MCP do Chatwoot da Neuralyn você já tem)

# 3. Instalar a dependência Python
pip install Pillow

# 4. Configurar o .env (NÃO comitar)
cat > ~/.tryon-helpdesk.env <<'EOF'
TRYON_SANDBOX_URL=https://sandbox.neuralyn.ai
TRYON_SANDBOX_EMAIL=helpdesk-bot@neuralyn.ai
TRYON_SANDBOX_PASSWORD=...
TRYON_BACKEND_REPO=/caminho/para/neuralyn-backend
TRYON_FRONTEND_REPO=/caminho/para/tryon-dashboard
TRYON_WIDGET_REPO=/caminho/para/tryon-widget
CHATWOOT_HELPDESK_PORTAL_SLUG=tryon-ajuda
EOF

chmod 600 ~/.tryon-helpdesk.env
```

## Como usar

Dentro do Claude Code, basta pedir:

> "Crie um artigo de ajuda sobre como cadastrar produtos no Tryon."

A skill é ativada automaticamente. O Claude Code vai:

1. Fazer **code recon** no monorepo (limites, formatos, erros possíveis)
2. **Logar no sandbox** via Playwright MCP
3. **Capturar e anotar** screenshots
4. **Escrever o markdown** com rastros de evidência em comentários
5. **Mostrar o draft** pra você revisar
6. **Publicar como rascunho** no Chatwoot via MCP após aprovação

## Estrutura

```
tryon-helpdesk-writer/
├── SKILL.md                  # ponto de entrada — workflow mestre
├── code-recon.md             # como buscar verdade no código
├── style-guide.md            # voz, "você", glossário
├── screenshot-conventions.md # padrões de imagem
├── test-environment.md       # config do sandbox
├── chatwoot-structure.md     # estrutura do portal
├── publishing-rules.md       # quando rascunho vs. publicar direto
├── scripts/
│   └── annotate.py           # anotações em imagens (Pillow CLI)
├── playbooks/
│   └── cadastrar-produto.md  # roteiro reutilizável (exemplo)
└── examples/
    └── artigo-modelo-passo-a-passo.md  # output esperado
```

## Princípios

1. **Verdade do código > verdade da UI > impressão.**
2. **Toda afirmação técnica tem rastro** (path:linha).
3. **Nunca publica sem revisão humana.**
4. **Se código e UI discordam, pare e reporte.**
5. **Linguagem é do merchant, não do dev.**

## Customizando

Pra adicionar um novo tipo de artigo: crie um playbook em `playbooks/`. Pra ajustar a voz: edite `style-guide.md`. Pra mudar o estilo das anotações: ajuste `screenshot-conventions.md` e/ou os defaults em `scripts/annotate.py`.

A skill foi desenhada pra ser editada — não é um produto fechado.
