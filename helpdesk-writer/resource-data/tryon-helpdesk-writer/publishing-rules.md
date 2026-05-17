# Publishing Rules

Quando publicar direto vs. quando deixar como rascunho. A regra é: quanto mais sensível o conteúdo, mais rígida a revisão.

## Matriz de decisão

| Tipo de artigo | Fluxo padrão | Por quê |
|---|---|---|
| **Passo-a-passo / how-to novo** | Rascunho → revisão visual no Chatwoot → publicar manualmente | Screenshots precisam ser conferidos por humano. Imagem errada gera ticket. |
| **Troubleshoot / explicação de erro** | Rascunho sempre | Texto sobre erro mal escrito piora a experiência. Sempre revisar antes. |
| **Conceitual / "o que é" / FAQ** | Publicar direto após aprovação no chat | Baixo risco, sem screenshots críticos. |
| **Update de artigo existente** | Rascunho com diff vs. versão atual | Precisa comparar antes de sobrescrever. |
| **Referência de formato / limite** | Rascunho | Erro num número (limite errado) cria expectativa errada. |
| **Artigo com dados de billing/plano** | Rascunho com aprovação obrigatória | Compromisso comercial — palavra errada vira problema. |

"Rascunho" = `status: draft` ou equivalente no Chatwoot. Não aparece pro público até virar `published`.

## Antes de qualquer publicação (rascunho ou direto)

Cheque obrigatoriamente:

1. **Todos os comentários HTML de evidência foram removidos.** Faça grep no markdown final: `grep -n '<!--' article.md` deve retornar zero linhas.
2. **Todos os screenshots foram processados** (em `assets/`, não `raw/`).
3. **Dados sensíveis foram blurrados** (rode visualmente: abra cada asset, escaneie).
4. **Glossário foi respeitado** (rode `grep -in "experimentação virtual\|AR try-on\|quota"` e troque pelos termos canônicos do `style-guide.md`).
5. **Sem "tu"**: `grep -in '\btu\b\|\bteu\b\|\btua\b'` — todos devem ser "você", "seu", "sua".
6. **Sem placeholders esquecidos**: `grep -in 'TODO\|FIXME\|XXX\|\[\.\.\.\]'`.

Se qualquer um falhar, volte e conserte. Só então publique.

## Chamada ao MCP do Chatwoot

O payload exato depende do MCP customizado, mas a estrutura mínima:

```json
{
  "portal_slug": "tryon-ajuda",
  "category_slug": "...",
  "title": "...",
  "slug": "...",
  "content": "<markdown limpo, sem comentários HTML>",
  "meta": {
    "description": "...",
    "tags": ["..."]
  },
  "status": "draft" | "published",
  "cover_image": "<path para assets/cover.png>",
  "inline_assets": ["<paths para todas as imagens referenciadas>"]
}
```

Se o MCP da Neuralyn aceitar upload de imagens junto ou exigir upload prévio em CDN, ajuste o fluxo aqui. Documente a decisão neste arquivo na primeira vez que rodar.

## Após publicar (ou criar rascunho)

Devolva ao usuário no chat:

- Status final (`draft` ou `published`)
- URL de edição no painel do Chatwoot
- URL pública (se published)
- Lista de imagens incluídas (com paths locais para referência futura)
- Resumo de **o que foi verificado no código** (pra confiança)

Exemplo de retorno:

```
✓ Artigo criado como rascunho no Chatwoot.

Título: Como cadastrar produtos no Catálogo
Slug: como-cadastrar-produtos
URL edição: https://app.chatwoot.com/portals/tryon-ajuda/categories/.../articles/.../edit
Imagens: 6 anexadas em assets/

Verificações feitas no código:
- Limite de 100 produtos por upload (apps/api/.../products.ts:42)
- Formatos JPG, PNG, WEBP, HEIC convertido (image-processor.ts:55)
- Tamanho máx 5 MB (upload.ts:23)
- 3 códigos de erro documentados (PRODUCT_SKU_DUPLICATE, etc)

Próximo passo: revisar visualmente no Chatwoot e mudar status pra Published.
```

## Atualizações automáticas (futuro)

Não implementar agora, mas planejar: a skill pode rodar em modo "verificação" periodicamente — re-executar o playbook do artigo, comparar screenshots antigos vs. novos via pixelmatch, e abrir issue no GitHub quando a UI mudou o suficiente pra invalidar o artigo. Deixar isso pra v2.
