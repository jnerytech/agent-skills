# Capítulo 2: Exemplo Financeiro — Expression, Bank e Retrospectiva (Caps. 10–17)

## Core Idea
A segunda metade do exemplo financeiro introduz a metáfora **Expression** (expressão aritmética de dinheiros), que destrava um projeto muito mais limpo do que somar moedas diretamente. Termina com a Retrospectiva Financeira: métricas, número de execuções de teste e as três técnicas centrais para chegar ao verde.

## Frameworks Introduced
- **Metáfora Expression**: trate "soma de dinheiros" como uma expressão (`Sum`, depois reduzida por um `Bank` a uma moeda-alvo). A escolha de metáfora teve "efeito dramático" sobre a estrutura — libertou Beck do problema de mesclar moedas duplicadas.
  - When to use: quando somar/converter tipos heterogêneos vira lógica condicional emaranhada.
  - How: `Money.plus()` retorna uma `Expression`; `Bank.reduce(expression, "USD")` resolve com as taxas de câmbio.
- **Reduce + taxas de câmbio**: `Bank` guarda taxas (`addRate`) e reduz expressões à moeda pedida, aplicando câmbio.

## Key Concepts
- **Expression (interface)**: contrato comum para `Money` e `Sum`; ambos sabem `reduce(bank, currency)`.
- **Sum**: composição de dois `Expression` (augend + addend) — caso do padrão Composite.
- **Bank**: hábitat das taxas e do `reduce`; isola política de conversão.
- **Duplicação duradoura**: sintoma de projeto latente; resta entre `Sum.plus()` e `Money.plus()` ao fim — "não acredito em 'terminado'".
- **Cobertura por comandos**: TDD seguido à risca ⇒ ~100% de cobertura de comandos (medida por JProbe).

## Mental Models
- Trate "qual é o próximo passo?" como recorrente: rode um analisador estático (Small-Lint) quando a lista esvaziar — analisadores não esquecem.
- Pense em **TMEF** (Tempo Médio Entre Falhas) ao decidir quantos testes escrever, não em cobrir permutações cegamente.
- Use **inserção de defeitos** (Jester) para avaliar qualidade de teste: mude uma linha; um teste deve quebrar.

## Code Examples
```java
public void testSimpleAddition() {
    Money five = Money.dollar(5);
    Expression sum = five.plus(five);   // retorna Expression, não Money
    Bank bank = new Bank();
    Money reduced = bank.reduce(sum, "USD");
    assertEquals(Money.dollar(10), reduced);
}
```
- **What it demonstrates**: o cliente fala em `Expression`; a redução à moeda concreta é responsabilidade do `Bank`.

## Reference Tables
Métricas do código resultante (Tabela 17.1):

| | Funcional | Teste |
|---|---|---|
| Classes | 5 | 1 |
| Funções | 22 | 15 |
| Linhas | 91 | 89 |
| Complexidade ciclomática | 1,04 | 1 |
| Linhas/função | 4,1 | 5,9 |

Observação: ~mesma quantidade de linhas em teste e em produção; complexidade baixíssima por uso pesado de polimorfismo no lugar de fluxo explícito.

## Worked Example
Beck registrou o uso de JUnit ao escrever a Parte I: apertou **Run 125 vezes**, rodando os testes cerca de **uma vez por minuto**. Em todo esse tempo foi surpreendido por sucesso/falha **apenas uma vez** — numa refatoração feita às pressas. Isso ilustra o ritmo: feedback constante, raríssimas surpresas, refatoração é onde mora o risco.

## Anti-patterns
- **Refatorar com pressa**: a única surpresa de Beck em 125 execuções veio de uma refatoração apressada — refatore em passos verificados.
- **Perseguir "terminado"**: TDD para buscar perfeição é seu uso menos eficaz; deixe a periferia estável imperfeita.

## Key Takeaways
1. A metáfora certa pode reorganizar todo o projeto — vale buscá-la, não só nomes.
2. Rode os testes obsessivamente (≈1×/min); o custo é baixo, o feedback é alto.
3. Duplicação que resiste é projeto latente pedindo para emergir.
4. As três abordagens para o verde — **Faça de conta, Triangulação, Implementação Óbvia** — são o coração ensinável do TDD.
5. Remover duplicação entre teste e código *guia o projeto*.

## Connects To
- **Ch 1**: primeira metade do mesmo exemplo (Dollar, Value Object).
- **Ch 9**: Composite (`Sum`), Value Object (`Money`) formalizados.
- **Ch 11**: "quantos testes escrever?" e TMEF aprofundados em Dominando TDD.
