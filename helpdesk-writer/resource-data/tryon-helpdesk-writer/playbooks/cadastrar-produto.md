# Playbook: Cadastrar produto

Roteiro reutilizável para gerar o artigo "Como cadastrar produtos no Catálogo". Quando rodar este playbook, ele executa o passo-a-passo no sandbox, captura screenshots e produz o draft do artigo.

## Metadata

- **Categoria Chatwoot**: `catalogo`
- **Slug**: `como-cadastrar-produtos`
- **Persona**: merchant iniciante
- **Tipo**: passo-a-passo
- **Fluxo de publicação**: rascunho → revisão visual → publicar manualmente

## Code recon — onde olhar

Antes do walkthrough, vasculhe (resultados vão pra `recon.md`):

1. **Endpoint**: `grep -rn "products.*post\|router.*products" $TRYON_BACKEND_REPO/src`
2. **Schema de entrada**: procure por `productSchema`, `ProductInput`, `CreateProductDto`
3. **Validações de imagem**: procure por `image`, `upload`, `multipart`, limites em MB
4. **Códigos de erro**: `grep -rn "PRODUCT_\|throw new.*Product" $TRYON_BACKEND_REPO/src`
5. **Quotas por plano**: `$TRYON_BACKEND_REPO/packages/plans` ou similar

Extraia para o recon: nome obrigatório (min/max chars), SKU (regex), preço, formato de imagem (extensões e tamanho), número máximo de imagens, limites por plano.

## Walkthrough no sandbox

Pré-condição: logado como conta de teste, no painel da loja Atelier Solis, com o catálogo seed presente.

### Passo 1 — Tela inicial do Catálogo

- Navegar para `/dashboard/produtos`
- Capturar screenshot da página inteira (`step-01-catalogo.png`)
- Anotação: borda vermelha no botão **Novo produto** (canto superior direito)
  - Use `browser_highlight` antes do screenshot
- No artigo: introdução curta sobre quando criar um produto

### Passo 2 — Abrir o formulário

- Clicar em **Novo produto**
- Aguardar form abrir (timeout 3s)
- Capturar screenshot (`step-02-form-vazio.png`)
- Anotação: nenhuma (o form em branco já se explica)

### Passo 3 — Campos obrigatórios

- Preencher Nome: `Camiseta Solar`
- Preencher SKU: `SOL-001-TEST`
- Preencher Preço: `89,00`
- Capturar screenshot (`step-03-form-preenchido.png`)
- Anotação: **numeração circular** em cada campo na ordem (1=Nome, 2=SKU, 3=Preço)
  - Posições vêm de `getBoundingClientRect` de cada input

### Passo 4 — Upload de imagens

- Clicar em **Adicionar imagens**
- Fazer upload de 3 imagens fictícias (do seed em `fixtures/`)
- Capturar screenshot da galeria preenchida (`step-04-imagens.png`)
- Anotação: borda vermelha em volta da galeria
- **Importante**: aqui, citar do recon os formatos aceitos e tamanho máximo

### Passo 5 — Salvar

- Clicar em **Salvar produto**
- Aguardar toast de sucesso (timeout 5s)
- Capturar screenshot do toast (`step-05-toast.png`)
- Anotação: **zoom-in recortado** no toast de sucesso
  - bbox aproximado: canto inferior direito, padding 40

### Passo 6 — Confirmação no Catálogo

- Aguardar redirect pro catálogo
- Capturar screenshot do produto recém-criado na lista (`step-06-catalogo-com-produto.png`)
- Anotação: borda vermelha na linha do produto novo

## Capa

Use o screenshot do passo 1 (catálogo cheio), recortado para 1280x640.

## Estrutura do artigo

Seguir template `passo-a-passo` do `style-guide.md`:

```
# Como cadastrar produtos no Catálogo

[1-2 frases sobre o objetivo]

## Antes de começar

- Você precisa estar com sua loja conectada ao Tryon
- Tenha as imagens dos produtos prontas (formatos: JPG, PNG, WEBP — máx X MB)
  <!-- src: recon.md, seção "Limites" -->

## Passo a passo

### 1. Abra o Catálogo
[texto] → [screenshot step-01]

### 2. Clique em "Novo produto"
[texto] → [screenshot step-02]

### 3. Preencha os campos obrigatórios
[texto explicando Nome, SKU, Preço]
[screenshot step-03 com numeração]

> **Sobre o SKU:** [explicação do regex em linguagem amigável]
> <!-- src: packages/schemas/src/product.ts:11 — regex ^[A-Z0-9-]+$ -->

### 4. Adicione as imagens
[texto explicando os limites de imagem]
[screenshot step-04]

> **Limites de imagem** <!-- src: recon.md -->
> - Formatos: JPG, PNG, WEBP (HEIC do iPhone é convertido automaticamente)
> - Tamanho máximo: 5 MB por imagem
> - Até 10 imagens por produto

### 5. Salve
[texto] → [screenshot step-05]

### 6. Pronto!
Seu produto aparece no Catálogo:
[screenshot step-06]

## Cotas do seu plano

<!-- src: recon.md, seção "Quotas por plano" -->
| Plano | Produtos |
|---|---|
| Free | 50 |
| Starter | 500 |
| Growth | 5.000 |
| Pro | Ilimitado |

## Veja também
- [Formatos de imagem aceitos](/catalogo/formatos-de-imagem)
- [Importar produtos em lote](/catalogo/importar-em-lote)

## Não funcionou?
- "SKU já cadastrado" → [link]
- "Imagem muito grande" → [link]
```

## Erros possíveis a documentar separadamente

Cada um vira um artigo na categoria `erros`:

- `PRODUCT_SKU_DUPLICATE` → artigo "SKU já cadastrado"
- `PRODUCT_IMAGE_TOO_LARGE` → artigo "Imagem ultrapassa o tamanho máximo"
- `QUOTA_EXCEEDED` → artigo "Limite de produtos atingido"

Cada um desses tem seu próprio playbook.
