---
name: tryon-helpdesk-writer
description: Writes user-facing helpdesk articles for the Tryon SaaS product and publishes them to Chatwoot. Use when the user asks to create, update, or draft documentation, a tutorial, a how-to, a step-by-step guide, or an article explaining a Tryon feature, error message, format, limit, or workflow. The skill cross-references three sources of truth (the backend/frontend codebase, the live UI via Playwright MCP, and the Tryon voice guide), captures annotated screenshots, and publishes to Chatwoot via MCP only after the user reviews the draft. Articles are written in PT-BR using "você".
---

# Tryon Helpdesk Writer

Cria artigos da central de ajuda do **Tryon** (Neuralyn) com informações tecnicamente verificadas: cruza o código do produto, a UI real no sandbox e o guia de voz antes de escrever uma única linha. Publica como rascunho no Chatwoot via MCP.

## Quando ativar

Solicitações para escrever, atualizar ou rascunhar:

- Tutorial / passo-a-passo / how-to do Tryon
- Explicação de feature, fluxo ou conceito do produto
- Artigo de troubleshoot / explicação de erro
- Referência de formato de dado, limite ou requisito
- FAQ ou artigo conceitual

## Pré-requisitos esperados no ambiente

- **Playwright MCP** instalado: `claude mcp add playwright npx @playwright/mcp@latest`
- **Chatwoot MCP** já configurado (o customizado da Neuralyn)
- Repos do Tryon clonados localmente (front + backend monorepo) — caminhos em `~/.tryon-helpdesk.env`
- Credenciais do sandbox em `~/.tryon-helpdesk.env` (nunca hardcoded)
- Python 3 com Pillow: `pip install Pillow`

## Workflow mestre

Para qualquer pedido de artigo, execute nesta ordem. **Não pule etapas.** A regra dura é: **nenhuma afirmação técnica entra no artigo sem evidência rastreada — do código ou da UI.**

### 1. Briefing

Pergunte ao usuário, em uma única rodada:

- Tema do artigo e categoria do helpdesk
- Persona-alvo (merchant iniciante, merchant técnico, dev integrando)
- Se é artigo novo ou atualização (se update, qual o ID/slug do artigo existente)

Se o tipo do artigo for óbvio do pedido, infira em vez de perguntar.

### 2. Code recon (ler `code-recon.md`)

Antes de tocar na UI, faça reconhecimento no código:

- Identifique os arquivos relevantes (handlers, schemas, validators, error maps, constantes)
- Extraia: formatos aceitos, limites numéricos, lista exaustiva de erros possíveis, defaults, fluxos condicionais
- Salve as descobertas em `drafts/<slug>/recon.md` com path:linha de cada evidência

Se a feature não tiver código correspondente, **avise o usuário** e não invente.

### 3. UI walkthrough (ler `test-environment.md` e `screenshot-conventions.md`)

Login no sandbox via Playwright MCP usando credenciais do env. Para cada passo do roteiro:

- Navegar até a tela
- Capturar screenshot (página inteira ou elemento, conforme convenção)
- Para anotações nativas: usar `browser_highlight` antes do screenshot quando aplicável
- Salvar em `drafts/<slug>/raw/step-NN.png`

Se a UI contradisser o código (ex: o código diz que aceita até 100 produtos mas a UI mostra "máx. 50"), **pare e reporte ao usuário**. Pode ser bug, validação dupla, ou doc obsoleta.

### 4. Pós-processamento de imagens (ler `screenshot-conventions.md`)

Chame `scripts/annotate.py` para aplicar a anotação certa em cada passo:

- **Borda vermelha** (overlay sutil via highlight nativo): visão geral da tela com elemento destacado
- **Numeração circular + setas**: quando o passo tem múltiplos sub-elementos em sequência
- **Zoom-in recortado**: detalhes pequenos (toggles, ícones, badges)
- **Blur**: sempre que aparecer dado de teste que pareça real (e-mail, CNPJ, nome de cliente)

Salve as imagens processadas em `drafts/<slug>/assets/step-NN.png`.

### 5. Escrita do artigo (ler `style-guide.md`)

Componha o markdown seguindo a estrutura padrão do tipo de artigo. Regras invioláveis:

- Linguagem PT-BR, "você"
- Cada afirmação técnica precisa de comentário HTML com a fonte: `<!-- src: backend/api/products.ts:42 — limite 100 -->`
- Cada screenshot tem texto antes (introduz o que vai ver) e texto depois (o que fazer)
- Erros são explicados como **o que aconteceu, por que aconteceu, o que fazer** — nessa ordem

### 6. Revisão humana

Mostre o draft no chat (markdown renderizado + lista de screenshots gerados). **Nunca publique direto.** Espere aprovação explícita.

Se o usuário pedir ajustes, refaça e mostre de novo.

### 7. Publicação (ler `publishing-rules.md`)

Com base no tipo do artigo, escolha o modo (rascunho vs. publicar direto). Antes do upload, remova **todos os comentários HTML de evidência** do markdown final. Eles são para auditoria, não para o leitor.

Chame o MCP do Chatwoot com: título, slug, categoria, corpo (markdown limpo), meta description, anexos de imagem.

## Arquivos de referência

| Arquivo | Quando ler |
|---|---|
| `code-recon.md` | Antes da etapa 2 |
| `test-environment.md` | Antes da etapa 3 |
| `screenshot-conventions.md` | Etapas 3 e 4 |
| `style-guide.md` | Etapa 5 |
| `chatwoot-structure.md` | Etapas 1 e 7 |
| `publishing-rules.md` | Etapa 7 |
| `playbooks/*.md` | Quando o usuário pedir um artigo cujo tema já tenha playbook |
| `examples/*.md` | Para referência de formato final |

## Scripts

- `scripts/annotate.py` — anotações em imagens (number, arrow, box, crop, blur, composite). Rode `python scripts/annotate.py --help`.

## Estrutura de drafts

```
drafts/<slug>/
├── recon.md              # evidências do código (etapa 2)
├── outline.md            # roteiro com passos (etapa 1+2)
├── raw/                  # screenshots crus do Playwright
├── assets/               # screenshots anotados (final)
└── article.md            # markdown do artigo (com comentários de evidência)
```

Mantenha a pasta `drafts/<slug>/` mesmo após publicar — serve de histórico e fonte pra updates futuros.

## Princípios

1. **Verdade do código > verdade da UI > impressão.** Nesta ordem.
2. **Toda afirmação técnica tem rastro** (path:linha) no draft.
3. **Nunca publica sem revisão humana.** Mesmo aprovação prévia não vale para um artigo novo.
4. **Se contradição entre código e UI, pare e reporte.** Não escolha um lado.
5. **Linguagem é do merchant, não do dev.** O artigo final não pode parecer issue do GitHub.
