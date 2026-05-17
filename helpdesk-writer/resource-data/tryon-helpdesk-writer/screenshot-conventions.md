# Screenshot Conventions

Padrões pra screenshots ficarem consistentes ao longo de toda a central de ajuda. A consistência é o que faz o helpdesk parecer profissional.

## Configurações base do Playwright

Antes de qualquer screenshot, configure o browser via Playwright MCP:

- **Viewport**: 1280 x 800 (cabe a sidebar do dashboard sem cortar)
- **Device scale factor**: 2 (screenshots em alta resolução pra retina)
- **Locale**: `pt-BR`
- **Timezone**: `America/Sao_Paulo`
- **Color scheme**: `light` (modo claro, padrão da maioria dos merchants)

Para o widget que roda na loja do cliente, varie:

- **Mobile**: 390 x 844 (iPhone padrão), DSF 3
- **Desktop**: 1280 x 800, DSF 2

## Naming

Arquivos em `drafts/<slug>/raw/` e `drafts/<slug>/assets/`:

```
step-NN-descricao-curta.png

Exemplos:
step-01-tela-inicial-catalogo.png
step-02-botao-novo-produto.png
step-03-form-preenchido.png
```

Numere com 2 dígitos (`01`, `02`...) pra ordenar bem.

A versão **anotada** vai em `assets/` com o mesmo nome do `raw/`. Nunca sobrescreva o raw — você pode precisar reprocessar com outra anotação.

## Tipos de anotação e quando usar cada

### A. Borda vermelha no elemento (highlight nativo do Playwright)

**Quando usar:** dar contexto da tela inteira mostrando onde está o elemento. É a anotação mais sutil — boa pra primeiro screenshot de cada passo.

**Como aplicar:** antes de tirar o screenshot, chame `browser_highlight` do Playwright MCP no elemento alvo. O highlight injeta CSS na página (`border: 3px solid #E53935; border-radius: 5px;`) e fica visível no screenshot.

Depois do screenshot, chame `browser_remove_highlight` para limpar.

**Exemplo de uso:**
> "Para começar, clique em **Novo produto** no canto superior direito do **Catálogo**:"
> ![tela do catálogo com botão Novo produto destacado](assets/step-01-catalogo.png)

### B. Numeração circular + setas

**Quando usar:** passos com múltiplos sub-elementos em sequência (ex: preencher 3 campos de um form na ordem). Mostra a ordem visualmente.

**Como aplicar:** capture o screenshot limpo, depois chame `scripts/annotate.py`:

```bash
python scripts/annotate.py number \
  --in raw/step-02-form.png \
  --out assets/step-02-form.png \
  --xy 250,180 --n 1

# Aplicar mais números no mesmo arquivo, sobrescrevendo:
python scripts/annotate.py number \
  --in assets/step-02-form.png \
  --out assets/step-02-form.png \
  --xy 250,280 --n 2

python scripts/annotate.py number \
  --in assets/step-02-form.png \
  --out assets/step-02-form.png \
  --xy 250,380 --n 3
```

Coordenadas vêm do bounding box do elemento (`browser_snapshot` retorna isso, ou rode `getBoundingClientRect` via `browser_run_code_unsafe`).

Posicione o círculo **levemente sobreposto** ao canto superior esquerdo do elemento, não em cima do texto/ícone.

### C. Zoom-in recortado

**Quando usar:** detalhes pequenos que sumiriam no screenshot inteiro — toggles, ícones de status, badges no menu, valores numéricos.

**Como aplicar:** capture o screenshot inteiro, depois recorte com padding:

```bash
python scripts/annotate.py crop \
  --in raw/step-04-toggle.png \
  --out assets/step-04-toggle.png \
  --bbox 1080,420,1250,490 \
  --padding 40
```

Sempre deixe pelo menos 30-40px de padding pra não ficar claustrofóbico.

Se quiser destacar dentro do crop, encadeie com `box`:

```bash
python scripts/annotate.py box \
  --in assets/step-04-toggle.png \
  --out assets/step-04-toggle.png \
  --bbox 80,30,180,90
```

### D. Mistura: borda + número

Para passos complexos que precisam destacar o elemento E mostrar ordem. Combine A + B no mesmo screenshot:

1. `browser_highlight` no elemento principal → screenshot
2. `annotate.py number` em cada sub-elemento

### E. Blur (mascarar dados)

**Quando usar SEMPRE:**

- E-mails que pareçam reais (mesmo no sandbox)
- CNPJ, CPF, telefone, endereço
- Nomes de clientes finais (compradores)
- Tokens, IDs longos, chaves de API
- Valores de billing real

Aplicação:

```bash
python scripts/annotate.py blur \
  --in raw/step-05-perfil.png \
  --out assets/step-05-perfil.png \
  --bbox 150,300,500,330
```

**Quando NÃO blurar:** nomes de produto fictícios criados no sandbox (`Camiseta Teste`, `Vestido Demo`). Esses ficam — dão realismo.

### F. Composição lado-a-lado (antes/depois)

Pra mostrar transformações: estado inicial vs. estado final. Útil em artigo conceitual ("o que o try-on faz com a foto do produto").

```bash
python scripts/annotate.py composite \
  --in raw/produto-original.png,raw/produto-tryon.png \
  --out assets/comparacao.png \
  --labels "Foto original,Com try-on"
```

## Capa do artigo

Cada artigo tem uma capa: screenshot da tela principal da feature, **sem anotações**, em 1280 x 640. Recorte pra esse aspect ratio com `crop`:

```bash
python scripts/annotate.py crop \
  --in raw/capa-bruta.png \
  --out assets/cover.png \
  --bbox 0,80,1280,720
```

Nome do arquivo: sempre `cover.png`.

## Dados de teste — o que aparecer nas imagens

No sandbox, popule com produtos de marca fictícia. Sugestão de seed (combine com a Andresa):

- Loja: **Atelier Solis** (fictícia)
- Produtos: `Camiseta Solar`, `Vestido Lúmen`, `Calça Linho Areia`, etc.
- Categoria: Moda
- Variações: 3 tamanhos (P, M, G), 2 cores

Mantenha esses dados estáveis. Screenshots de artigos diferentes ficam coerentes entre si.

## Reprodutibilidade

Se um artigo precisar ser atualizado depois (UI mudou, screenshot ficou velho), o roteiro do playbook deve ser **executável de novo** e gerar screenshots equivalentes. Por isso:

- Use seletores semânticos (`getByRole`, `getByLabel`), não XPath frágil
- Estados de dados via seed reproduzível
- Sempre mesmo viewport e DSF
