# Test Environment — sandbox do Tryon

A skill assume um ambiente sandbox dedicado da Neuralyn (não a produção). O Claude Code loga aqui, navega e tira screenshots sem afetar nenhum cliente real.

## Credenciais e configuração

Credenciais **nunca** ficam no chat ou no código. Ficam em `~/.tryon-helpdesk.env`, lido pelo Claude Code via `dotenv` ou diretamente:

```bash
# ~/.tryon-helpdesk.env

# URLs
TRYON_SANDBOX_URL=https://sandbox.neuralyn.ai
TRYON_SANDBOX_WIDGET_DEMO_URL=https://demo-loja.sandbox.neuralyn.ai

# Conta merchant de teste
TRYON_SANDBOX_EMAIL=helpdesk-bot@neuralyn.ai
TRYON_SANDBOX_PASSWORD=...

# Repos locais (pra code recon)
TRYON_BACKEND_REPO=/home/andresa/code/neuralyn-backend
TRYON_FRONTEND_REPO=/home/andresa/code/tryon-dashboard
TRYON_WIDGET_REPO=/home/andresa/code/tryon-widget

# Chatwoot (do MCP)
CHATWOOT_BASE_URL=...
CHATWOOT_API_TOKEN=...
CHATWOOT_HELPDESK_PORTAL_SLUG=tryon-ajuda
```

Permissões do arquivo: `chmod 600 ~/.tryon-helpdesk.env`

## Conta de teste

Use uma conta dedicada, **separada da sua conta pessoal de admin**. Plano sugerido: o mais alto (Pro), porque dá pra documentar todas as features sem esbarrar em cota.

Para artigos sobre limitação por plano (ex: "o que acontece quando atinjo a cota do Free"), tenha uma segunda conta no plano relevante.

## Login automático via Playwright MCP

A skill faz login no início de cada walkthrough. Padrão:

```
1. browser_navigate -> $TRYON_SANDBOX_URL/login
2. browser_fill (email field) -> $TRYON_SANDBOX_EMAIL
3. browser_fill (password field) -> $TRYON_SANDBOX_PASSWORD
4. browser_click -> botão "Entrar"
5. browser_wait -> URL contém "/dashboard"
```

Se houver MFA na conta de teste, **desative** — sandbox é pra isso. Não tente automatizar MFA.

## Estado de dados (seed)

A documentação fica coerente entre artigos se os dados forem estáveis. Defina um seed e mantenha:

### Loja fictícia
- Nome: **Atelier Solis**
- Domínio demo: `demo-loja.sandbox.neuralyn.ai`
- Categoria: Moda
- Idioma: pt-BR

### Catálogo inicial (sempre presente)
| SKU | Nome | Preço | Categoria | Imagens |
|---|---|---|---|---|
| SOL-001 | Camiseta Solar | R$ 89,00 | Camisetas | 3 |
| SOL-002 | Vestido Lúmen | R$ 249,00 | Vestidos | 4 |
| SOL-003 | Calça Linho Areia | R$ 189,00 | Calças | 2 |

Mantenha esses produtos sempre lá. Se a UI mudar e o nome de campo virar outro, o artigo é regenerável.

### Reset do sandbox

Antes de uma sessão de produção de artigos, vale resetar o estado. Crie um script `scripts/reset-sandbox.sh` (fora desta skill, no projeto) que:

1. Limpa produtos extras criados em sessões anteriores
2. Reseta a vitrine
3. Restaura o catálogo seed

## Browser config

```
viewport: 1280x800
device_scale_factor: 2
locale: pt-BR
timezone: America/Sao_Paulo
color_scheme: light
```

## O que NÃO fazer no sandbox

- Nunca clicar em **Apagar conta** ou ações destrutivas reais (pode quebrar dados seed)
- Nunca fazer upgrade/downgrade de plano (deixa pra teste manual em conta dedicada)
- Nunca enviar e-mails reais (transactional emails do sandbox devem ir pra inbox de teste)
- Nunca testar webhooks apontando pra produção
- Nunca subir imagens com pessoas reais (use as do seed ou geradas)

## Se algo der errado

Se o login falhar 2x, **pare**. Não fique tentando — pode ser:

- Conta de teste bloqueada (rate limit)
- Senha foi rotacionada e env tá desatualizado
- Sandbox fora do ar

Reporte ao usuário e espere instrução.
