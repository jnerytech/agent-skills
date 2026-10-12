# Capítulo 3: Uma Teoria de Programação (Valores e Princípios)

## Core Idea
Padrões não cobrem toda situação. Acima deles há **valores** (temas universais) e **princípios** (pontes entre valores e padrões). A equação equilibrada: **padrões = o que fazer; valores = motivação; princípios = traduzem motivação em ação.**

## Frameworks Introduced
### Os 3 Valores
- **Comunicação**: o código comunica quando o leitor consegue entendê-lo, modificá-lo ou usá-lo. Base econômica: a maior parte do custo é pós-implantação, e lê-se muito mais do que se escreve.
- **Simplicidade**: eliminar complexidade *em excesso* (não a essencial). Simplicidade está no olho de quem vê — escreva para o público-alvo. Aplique em todos os níveis.
  - Failure mode: complexidade = "marcas de unhas na luta para fazer rodar a qualquer custo".
- **Flexibilidade**: seja flexível **apenas onde o programa muda**. É o valor mais usado para *justificar* código ruim.
  - Why it works: flexibilidade de **simplicidade + testes** > flexibilidade de projeto especulativo.

### Os 6 Princípios
- **Consequências locais**: estruture o código para que mudanças tenham efeito local ("mudar aqui não quebra lá"). É o princípio-raiz que gera a maioria dos padrões.
- **Minimizar repetição**: código repetido espalha as consequências da mudança. Remova dividindo em pedaços pequenos (declarações, métodos, objetos, pacotes).
- **Lógica e dados em harmonia**: mantenha lógica junto dos dados que ela opera (mesmo método/objeto/pacote) → a mudança fica local.
- **Simetria**: a mesma ideia expressa da mesma forma em todo lugar (`add()`/`remove()`; campos com mesmo tempo de vida). Simetria é conceitual, não gráfica.
- **Expressão declarativa**: expresse a intenção declarativamente quando possível — não exige seguir fluxo de execução (ex.: anotação `@RunWith(Suite.class)` no JUnit 4 vs. método imperativo `suite()`).
- **Ritmo de mudança**: una lógica/dados que mudam no mesmo ritmo; separe os que mudam em ritmos diferentes (simetria *temporal*). Campos que mudam juntos → objeto auxiliar.

## Key Concepts
- **Valor**: tema universal e amplo; motiva mas é difícil de aplicar direto.
- **Princípio**: mais específico que valor, presente em muitos padrões; guia quando nenhum padrão se aplica ou dois se aplicam em conflito.
- **Custo pós-implantação**: domina o custo total → foco em leitura barateia o software.

## Mental Models
- **Nível de desacordo**: quando dois programadores discordam, identifique se é sobre padrão, princípio ou valor — discutir chaves quando o conflito é de princípio é perda de tempo.
- **Princípios como tabela periódica**: princípios claros levam a *novos* padrões, como a tabela levou a novos elementos.
- **"É possível escrever FORTRAN em qualquer linguagem, mas não se deve"**: use princípios para criar um estilo *nativo* da linguagem nova, não importe o estilo de outra.

## Worked Example — Refatorar por simetria
Ponto de partida sem simetria (mistura mensagens abstratas com operação concreta):
```java
void process() { input(); count++; output(); }
```
`count++` é mais concreto que `input()`/`output()`. Torne simétrico extraindo método:
```java
void process() { input(); incrementCount(); output(); }
```
Ainda viola simetria: `input`/`output` nomeiam **intenção**, `incrementCount` nomeia **implementação**. Pergunte *por que* incrementar o contador → nomeie pela intenção:
```java
void process() { input(); tally(); output(); }
```
Lição: expressar simetria costuma ser o passo preliminar para depois remover duplicação.

Ritmo de mudança aplicado — `value` e `currency` mudam juntos, fora de sincronia com o resto → viram objeto `Money`:
```java
setAmount(int value, String currency) { this.value=value; this.currency=currency; }
// → setAmount(int value, String currency){ this.value=new Money(value,currency); }
// → setAmount(Money value){ this.value=value; }
```

## Anti-patterns
- **Flexibilidade especulativa**: variável de ambiente → arquivo → constante, para algo que nunca muda. Custo sem benefício.
- **Investir pesado no design inicial para evitar manutenção**: falha — o valor temporal do dinheiro e a incerteza do futuro punem isso.
- **Simplificar ao ponto de prejudicar leitura**: raro, mas aí prefira **comunicação a simplicidade** (sinaliza simplificação maior ainda invisível).

## Key Takeaways
1. Ordem de prioridade em conflito: comunicação geralmente vence simplicidade; flexibilidade só onde há mudança real.
2. Os 6 princípios são todos corolários ou aplicações de **consequências locais**.
3. Simetria e ritmo de mudança são a mesma ideia em espaço vs. tempo.
4. Declarativo > imperativo para "fatos simples" sem sequência/condicional.
5. Princípios guiam em situação nova (linguagem nova) onde não há padrão pronto.

## Connects To
- **Ch 1-2**: fecha a seção teórica; padrões concretizam esses princípios.
- **Ch 4**: a base econômica (custo de manutenção) que motiva "consequências locais".
- **Todos os capítulos de catálogo (5-9)**: cada padrão expressa 1+ destes valores/princípios.
