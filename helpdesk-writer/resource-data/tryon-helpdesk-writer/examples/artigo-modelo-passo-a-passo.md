# Como cadastrar produtos no Catálogo

Cadastrar produtos é o primeiro passo para o Tryon mostrar as suas peças nos try-ons da sua loja. Você consegue fazer isso em menos de 2 minutos.

## Antes de começar

- A sua loja precisa estar conectada ao Tryon (se ainda não, veja [Instalando o widget](/widget/instalando)).
- Tenha as imagens dos produtos prontas. <!-- src: recon.md "Limites de imagem" -->
  - Formatos aceitos: **JPG, PNG, WEBP**. Imagens HEIC (do iPhone) são convertidas automaticamente.
  - Tamanho máximo: **5 MB** por imagem.
  - Até **10 imagens** por produto.

## Passo a passo

### 1. Abra o Catálogo

No menu lateral do painel, clique em **Catálogo**:

![Tela inicial do painel com o item Catálogo destacado no menu](assets/step-01-catalogo.png)

### 2. Clique em **Novo produto**

O botão fica no canto superior direito da tela:

![Botão Novo produto no canto superior direito](assets/step-02-novo-produto.png)

### 3. Preencha os campos obrigatórios

Você precisa preencher três campos para criar o produto:

![Formulário com os campos numerados](assets/step-03-form.png)

**1. Nome** — como o produto aparece pro comprador. Entre 3 e 120 caracteres. <!-- src: packages/schemas/src/product.ts:8 -->

**2. SKU** — código único do produto na sua loja. Só letras maiúsculas, números e hífen (ex: `CAM-SOL-001`). <!-- src: packages/schemas/src/product.ts:11 — regex ^[A-Z0-9-]+$ -->

**3. Preço** — em reais, sem o R$. Use vírgula para os centavos (ex: `89,00`). <!-- src: apps/api/src/routes/products.ts:67 — price_cents conversion -->

> **Sobre o SKU:** se você já tem códigos de produto na sua loja, use os mesmos. Isso facilita conectar o Catálogo do Tryon com o seu estoque depois. Se ainda não usa SKU, uma boa convenção é **categoria-modelo-número** (`VES-LUM-002` para o Vestido Lúmen modelo 2).

### 4. Adicione as imagens

Clique em **Adicionar imagens** e selecione as fotos do produto:

![Área de upload com 3 imagens carregadas](assets/step-04-imagens.png)

A primeira imagem é a **principal** — é ela que aparece no botão de try-on da sua loja. As outras viram variações que o comprador pode ver no try-on.

### 5. Salve

Clique em **Salvar produto** no rodapé do formulário. Você vai ver uma confirmação no canto da tela:

![Toast de sucesso "Produto cadastrado"](assets/step-05-toast.png)

### 6. Pronto!

Seu produto agora aparece no Catálogo e já está disponível para try-ons:

![Lista do catálogo com o produto recém-cadastrado destacado](assets/step-06-confirmacao.png)

## Cotas do seu plano

Cada plano tem um limite de quantos produtos você pode manter no Catálogo: <!-- src: recon.md "Quotas por plano" -->

| Plano | Limite de produtos |
|---|---|
| Free | 50 |
| Starter | 500 |
| Growth | 5.000 |
| Pro | Ilimitado |

Quando você se aproxima do limite, aparece um aviso no Catálogo. Você pode fazer upgrade do plano a qualquer momento em **Configurações → Plano**.

## Veja também

- [Formatos de imagem aceitos](/catalogo/formatos-de-imagem)
- [Importar muitos produtos de uma vez](/catalogo/importar-em-lote)
- [Editar ou remover um produto](/catalogo/editar-produto)

## Não funcionou?

- **"SKU já cadastrado"** — você já tem um produto com esse mesmo código. [Saiba o que fazer](/erros/sku-duplicado).
- **"Imagem muito grande"** — alguma imagem passa de 5 MB. [Como reduzir](/erros/imagem-grande).
- **"Limite do plano atingido"** — você chegou na cota de produtos. [Veja as opções](/erros/cota-excedida).
