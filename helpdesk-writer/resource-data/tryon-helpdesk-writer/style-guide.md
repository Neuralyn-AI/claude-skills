# Style Guide — voz do Tryon Helpdesk

A persona-alvo é um **lojista** (merchant) usando o Tryon na loja dele. Ele não é dev. Ele tem pressa. Ele só quer entender o que fazer.

## Regras de voz

### Use "você", sempre
Nunca "o usuário", "o lojista", "a pessoa". Conversa direta.

### Verbo no imperativo, ação primeiro
- ✅ "Clique em **Cadastrar produto**."
- ❌ "O usuário deve clicar no botão de cadastrar produto localizado no canto superior direito da tela."

### Uma ação por parágrafo (em passo-a-passo)
Não empilhe três cliques em uma frase. Cada parágrafo curto, uma ação, um screenshot se necessário.

### Frases curtas
Limite de respiração: se a frase não cabe em um respiro, quebra. 

### Antecipe a dúvida antes do screenshot, não depois
- ✅ "Se você nunca cadastrou um produto, comece pela aba **Catálogo**:" → [screenshot]
- ❌ [screenshot] → "Acima você pode ver a aba Catálogo, que fica..."

### Não explique o óbvio
Não diga "clique no botão azul à direita que tem escrito Salvar". O leitor está vendo o screenshot. Diga "Clique em **Salvar**".

### Bold em nomes de botões e telas
Tudo que o merchant vê escrito na interface vira **bold**. Facilita o scan.

## Termos do Tryon (glossário)

Esses são os termos canônicos. Use **sempre o mesmo**, mesmo que o time use variações internamente.

| Use | Não use |
|---|---|
| **Try-on** (ou "provador virtual" na primeira menção) | "experimentação virtual", "AR try-on" |
| **Catálogo** | "lista de produtos", "inventário" |
| **Widget** | "plugin", "embed", "iframe" (exceto em doc técnica) |
| **Loja** | "site", "store", "e-commerce" |
| **Plano** | "assinatura", "subscription", "tier" |
| **Cota** ou **limite do plano** | "quota" |
| **Sandbox** | "ambiente de testes" (em doc pra dev tudo bem, pro merchant não) |
| **Painel** | "dashboard", "console" |
| **Imagem do produto** | "foto do produto", "thumb", "mídia" |

Se um termo novo aparecer, registre aqui antes de publicar.

## "Você" carioca vs paulista

A Andresa é de SP e usa "você" — **nunca "tu"**. Mesmo em tom casual. "Tu" soa carioca/sulista e quebra a marca.

## Estruturas padrão

### Artigo passo-a-passo

```markdown
# Como [verbo no infinitivo] [objeto]

Uma frase explicando quando você faz isso e por quê. Máximo duas frases.

## Antes de começar

Pré-requisitos em bullets curtos. Pular essa seção se não houver.

## Passo a passo

### 1. [Ação curta]

Texto introduzindo o passo (1-2 frases). 

![descrição da imagem](assets/step-01.png)

Texto de fechamento se necessário (1 frase).

### 2. [Ação curta]
...

## Pronto!

Frase curta de fechamento. Link para o próximo artigo relacionado.

## Não funcionou?

Lista de 2-3 problemas comuns + link pro artigo de troubleshoot.
```

### Artigo de erro / troubleshoot

```markdown
# Mensagem: "[texto exato do erro]"

## O que aconteceu

1-2 frases explicando, sem jargão.

## Por que aconteceu

A causa real. Use o `recon.md` pra ser preciso.

## Como resolver

Passos numerados. Curtos. Cada um termina com resultado esperado.

## Ainda não funciona?

Bullet com canais de suporte e o que mandar (logs, IDs).
```

### Artigo conceitual / "o que é"

```markdown
# O que é [conceito]

Definição em uma frase. Como se você explicasse pra alguém no elevador.

## Como funciona, na prática

Exemplo concreto, com nomes reais. Sem "imagine que..."

## Quando usar

Bullets de casos de uso.

## Quando NÃO usar

Limitações. Importante. Salva ticket de suporte depois.

## Próximos passos

Links pra artigos de how-to relacionados.
```

## Explicando erros — fórmula

**O que aconteceu → Por que aconteceu → O que fazer.** Nessa ordem. Sem jargão técnico.

### Exemplo ruim
> "Erro 429: Rate limit exceeded. O usuário atingiu o limite de requisições por minuto da API do plano contratado."

### Exemplo bom
> ## O que aconteceu  
> Você fez muitos try-ons em pouco tempo e o Tryon precisou pausar por alguns segundos.
>
> ## Por que aconteceu  
> Cada plano tem um limite de quantos try-ons podem ser feitos por minuto, pra garantir que o serviço fique rápido pra todo mundo.
>
> ## O que fazer  
> 1. Aguarde 1 minuto e tente de novo — na maioria dos casos, é só isso.  
> 2. Se acontece toda hora, talvez seja hora de subir de plano. Veja os limites em [Planos e cotas](link).

## Limitações que merchants ODEIAM descobrir só depois

Sempre que documentar uma feature, **lista limites e formatos antes** do passo-a-passo. Surpresa no meio do tutorial gera ticket.

Exemplos:

- "Tamanho máximo da imagem: 5 MB."
- "Formatos aceitos: JPG, PNG, WEBP. HEIC do iPhone é convertido automaticamente."
- "Você pode cadastrar até 100 produtos por vez."
- "Disponível no plano Growth e Pro."

## Tom

- Direto, não bajulador. Sem "Que ótimo que você está aqui aprendendo sobre nosso incrível produto!"
- Empático em erros. "Isso costuma acontecer quando..." em vez de "Você fez errado".
- Confiante. Sem "talvez", "provavelmente", "acreditamos que".
- Sem emoji em artigos (exceto se o produto usar emoji na UI — aí cita).

## Capa do artigo

Toda capa segue o formato: screenshot da tela principal da feature, sem anotações, em 1280x640. O `screenshot-conventions.md` detalha.
