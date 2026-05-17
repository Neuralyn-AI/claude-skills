# Code Recon — buscando a verdade no código

Esta é a etapa mais importante da skill, e a que diferencia um artigo bom de um artigo genérico. Antes de escrever, descubra o que o código realmente faz.

## Princípio

**Nenhuma afirmação técnica entra no artigo sem ter sido encontrada no código.** Não escreva "o limite é 100 produtos" se você não viu uma constante `MAX_PRODUCTS = 100` no repositório. Em vez disso, encontre e cite.

Se você não consegue encontrar a evidência, dois caminhos:

1. Reporte ao usuário ("não achei essa constante, você pode me apontar onde fica?")
2. Omita a afirmação do artigo

Nunca chute.

## Onde está cada coisa (mapeie no início do projeto)

Quando esta skill é instalada em um projeto novo, peça ao usuário para preencher `~/.tryon-helpdesk.env` com os caminhos dos repos:

```bash
TRYON_BACKEND_REPO=/home/andresa/code/neuralyn-backend
TRYON_FRONTEND_REPO=/home/andresa/code/tryon-dashboard
TRYON_WIDGET_REPO=/home/andresa/code/tryon-widget
```

A skill assume os patterns abaixo. Se o monorepo tiver outra estrutura, atualize esta seção.

### Backend (Cloudflare Workers + TypeScript)

| O que procurar | Pattern de busca | Por quê |
|---|---|---|
| Schemas de validação (entrada) | `z.object`, `zod` | Define formato exato dos dados aceitos: tipos, tamanhos, obrigatoriedade |
| Constantes de limites | `MAX_`, `LIMIT_`, `_LIMIT`, `const.*=.*\d+` | Limites numéricos hardcoded (quotas, tamanhos) |
| Códigos de erro | `throw new`, `HTTPException`, `ApiError`, `ErrorCode` | Lista exaustiva dos erros que o backend pode emitir |
| Mensagens de erro | `message:`, `errorCode:`, arquivos `errors.ts` ou `messages.ts` | Texto literal que o frontend mostra |
| Defaults | `??`, `defaultValue`, `default:` | Valores padrão que entram quando o campo é omitido |
| Tipos compartilhados | `types/`, `schemas/`, `shared/` | Contratos de API |
| Roteamento | `app.get(`, `app.post(`, `route(`, `Hono` | Mapeia endpoint → handler |
| Quotas/billing | termos como `quota`, `usage`, `plan`, `tier` | Limites por plano (free/starter/growth/pro) |

### Frontend (dashboard + widget)

| O que procurar | Pattern | Por quê |
|---|---|---|
| Strings de UI / i18n | `pt-BR.json`, `translations`, `t(` | Texto literal que o merchant vê — use o mesmo no artigo |
| Validators client-side | `react-hook-form`, `zod`, `validate` | Pode ser mais restritivo que o backend |
| Mensagens de erro renderizadas | grep pela `errorCode` do backend | Como o erro aparece visualmente |
| Feature flags | `flag`, `enabled`, `experimental` | Saber se a feature está liga pra todos os planos |
| Componentes de erro | `Error`, `Toast`, `Alert` | Como o erro é apresentado |

## Estratégia de busca

Não tente ler o repo inteiro. Faça busca dirigida:

1. **Comece pelo nome da feature na UI.** Se o artigo é sobre "cadastrar produto", `grep -rin "cadastrar produto\|create product\|new product"` no frontend te leva ao componente. Do componente, descubra qual endpoint ele chama. Do endpoint, vá pro handler no backend.

2. **Use Glob + Grep agressivamente.** Em vez de ler arquivos inteiros, busque exato:

   ```bash
   # Achar o handler do endpoint
   grep -rn "products.*post\|POST.*products" $TRYON_BACKEND_REPO/src
   
   # Achar o schema de validação
   grep -rn "productSchema\|ProductInput" $TRYON_BACKEND_REPO/src
   
   # Achar todos os erros que esse handler pode lançar
   grep -rn "throw\|ApiError" $TRYON_BACKEND_REPO/src/routes/products/
   ```

3. **Siga as imports.** Achou o schema? Leia ele inteiro. Veja o que ele importa (sub-schemas, regex de validação, enums). Achou a constante? Veja onde é usada.

4. **Conferir tipos compartilhados.** Em monorepo, frontend e backend frequentemente compartilham types. Cheque se o que você está documentando é o tipo compartilhado ou uma transformação.

## Como registrar as evidências

Após o recon, crie `drafts/<slug>/recon.md` com este formato:

```markdown
# Recon: <slug do artigo>

## Endpoint principal
- POST /api/products  
  src: `neuralyn-backend/apps/api/src/routes/products.ts:34`

## Schema de entrada
- `name`: string, 3-120 chars, obrigatório  
  src: `neuralyn-backend/packages/schemas/src/product.ts:8`
- `sku`: string, regex `^[A-Z0-9-]+$`, 1-50 chars, obrigatório  
  src: `packages/schemas/src/product.ts:11`
- `price_cents`: integer ≥ 0, obrigatório  
  src: `packages/schemas/src/product.ts:14`
- `images`: array de URLs, máx 10 itens  
  src: `packages/schemas/src/product.ts:18`

## Limites
- Máximo de produtos por upload em lote: 100  
  src: `apps/api/src/routes/products.ts:42` (const `BATCH_LIMIT`)
- Imagens por produto: 10  
  src: `packages/schemas/src/product.ts:18`
- Tamanho máx por imagem: 5 MB (enforced no Worker)  
  src: `apps/api/src/middleware/upload.ts:23`

## Erros possíveis
| Código | Quando ocorre | Mensagem (i18n PT-BR) |
|---|---|---|
| `PRODUCT_SKU_DUPLICATE` | SKU já existe no tenant | "Esse SKU já está cadastrado..." (src: `frontend/locales/pt-BR.json:142`) |
| `PRODUCT_IMAGE_TOO_LARGE` | Imagem > 5 MB | "A imagem ultrapassa o limite..." |
| `QUOTA_EXCEEDED` | Tenant atingiu limite do plano | depende do plano (ver `plans.ts:18`) |

## Quotas por plano
- Free: 50 produtos  
- Starter (R$99): 500 produtos  
- Growth (R$199): 5.000 produtos  
- Pro (R$399): ilimitado  
  src: `neuralyn-backend/packages/plans/src/limits.ts:8-22`

## Comportamento condicional
- Se imagem for HEIC, é convertida para JPEG antes do storage  
  src: `apps/api/src/services/image-processor.ts:55`
- Se `price_cents` for omitido, default é 0 mas o produto não aparece na vitrine  
  src: `apps/api/src/services/product-visibility.ts:12`
```

Esse `recon.md` é a fonte das afirmações técnicas do artigo. Cada `<!-- src: ... -->` no draft aponta pra uma linha desse recon.

## Quando o código contradiz a UI

Caso comum. Exemplos reais:

- Código diz que aceita 100 produtos, UI mostra "máx. 50" → validação dupla, e a UI tá mais restritiva por uma boa razão (ou por bug). Pare e pergunte.
- Código emite erro `INVALID_FORMAT`, mas o frontend mostra "Erro desconhecido" → falta tradução. Documente a mensagem que o usuário **vai ver** (não a que o código emite), e abra um issue mental para você reportar pro time.
- UI mostra um botão que não tem rota correspondente no backend → feature flag, mocado, ou feature morta.

Em todos os casos: **reporte ao usuário antes de escrever**. Não escolha um dos lados sozinho.

## O que NÃO documentar

Algumas coisas você vai encontrar no código que **não vão no artigo**:

- Endpoints internos (admin, debug)
- Validações que existem mas vão sair (TODO, deprecated)
- Detalhes de implementação que não afetam o usuário (qual fila usa, qual cache, qual provider de IA)
- Códigos de erro internos que nunca chegam ao frontend
- Constantes de teste (`MAX_PRODUCTS_DEV = 999999`)

A regra: **o merchant precisa saber disso para usar o produto?** Se não, fora.
