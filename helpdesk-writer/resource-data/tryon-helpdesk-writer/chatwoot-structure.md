# Chatwoot Structure

Estrutura do portal de ajuda do Tryon no Chatwoot. Quando a estrutura for definida, atualize este arquivo — ele é a fonte de verdade pra decidir em qual categoria cada artigo vai.

## Portal

- **Slug**: `tryon-ajuda`
- **Idioma principal**: pt-BR
- **URL pública** (a confirmar): `https://ajuda.neuralyn.ai`

## Categorias sugeridas

A estrutura abaixo é uma sugestão inicial. Ajuste com a Andresa na primeira sessão e mantenha aqui depois.

### 1. Começando
**slug:** `comecando`  
Onboarding, primeiros passos, configuração inicial.

Exemplos de artigos:
- O que é o Tryon
- Criando sua conta
- Instalando o widget na sua loja

### 2. Catálogo de produtos
**slug:** `catalogo`  
Tudo sobre cadastrar, editar, organizar produtos.

Exemplos:
- Como cadastrar produtos
- Formatos aceitos de imagem
- Importação em lote

### 3. Widget e integração
**slug:** `widget`  
Como o try-on aparece na loja, integrações com plataformas.

Exemplos:
- Integração com PrestaShop
- Customizando a aparência do widget
- Posicionando o botão de try-on

### 4. Try-on e qualidade da imagem
**slug:** `try-on-qualidade`  
A experiência principal — qualidade, tempos, troubleshooting visual.

Exemplos:
- Por que o try-on demorou tanto?
- A qualidade da imagem não ficou boa, e agora?
- Tipos de produto que funcionam melhor

### 5. Planos, cotas e cobrança
**slug:** `planos-cobranca`  
Billing, upgrade, cotas.

### 6. Erros e solução de problemas
**slug:** `erros`  
Mensagens de erro específicas + troubleshooting.

### 7. Para desenvolvedores
**slug:** `dev`  
Documentação técnica pra integrações customizadas (audiência diferente, tom diferente).

## Convenções de slug de artigo

- Tudo minúsculo, hífen como separador
- Sem stop words desnecessárias ("o", "a", "como" — exceto em "como-fazer-X")
- Mantenha o slug curto mas legível: máx ~50 chars
- Imutável depois de publicado (pra não quebrar links externos)

Exemplos:
- ✅ `como-cadastrar-produtos`
- ✅ `erro-quota-excedida`
- ✅ `integracao-prestashop`
- ❌ `tutorial-passo-a-passo-de-como-voce-pode-cadastrar-os-seus-produtos-no-catalogo`

## Meta description

- Máx 160 caracteres
- Frase completa, faz sentido sozinha
- Tem o termo principal que o merchant buscaria

Exemplo: "Aprenda a cadastrar produtos no Catálogo do Tryon, com os formatos de imagem aceitos e os limites de cada plano."

## Tags

Aplique tags de:

- **Persona**: `merchant-iniciante`, `merchant-tecnico`, `dev`
- **Plano** (se relevante): `free`, `starter`, `growth`, `pro`
- **Plataforma** (se relevante): `prestashop`, `shopify`, `woocommerce`
- **Tipo**: `tutorial`, `referencia`, `troubleshoot`, `conceito`

## Estrutura de URL

```
https://ajuda.neuralyn.ai/<portal>/<categoria-slug>/<artigo-slug>
```

Exemplo: `https://ajuda.neuralyn.ai/tryon-ajuda/catalogo/como-cadastrar-produtos`

## Artigos relacionados (links internos)

No fim de cada artigo, inclua 2-4 links pra artigos próximos. Use links relativos pro slug, não URLs absolutas — facilita migrações:

```markdown
## Veja também

- [Formatos de imagem aceitos](/catalogo/formatos-de-imagem)
- [Limites do seu plano](/planos-cobranca/limites)
```

O MCP do Chatwoot deve resolver esses links na hora da publicação.
