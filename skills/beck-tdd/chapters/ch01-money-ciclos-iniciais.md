# Capítulo 1: Exemplo Financeiro — Ciclos Iniciais (Money, Caps. 1–9)

## Core Idea
Parte I demonstra o **ritmo do TDD** construindo dinheiro multi-moeda do zero: cada teste cobre um incremento minúsculo, a implementação mais feia possível leva à barra verde, e só então se remove duplicação. O objetivo é "código limpo que funciona" (Ron Jeffries), atacado em duas frentes separadas: primeiro *funciona*, depois *limpo*.

## Frameworks Introduced
- **As duas regras do TDD**: (1) Escreva um teste automático que falhe antes de escrever qualquer código. (2) Remova duplicação.
  - When to use: sempre que escrever código de produção.
  - How: nunca digite lógica sem um teste vermelho exigindo-a; nunca avance ao próximo teste com duplicação pendente.
- **Ciclo vermelho/verde/refatore** (red/green/refactor):
  1. Adicione um pequeno teste.
  2. Rode todos os testes e veja o novo falhar.
  3. Faça uma pequena mudança (pode ser feia).
  4. Rode os testes e veja todos passarem.
  5. Refatore para remover duplicação.
- **Os três passos do ciclo geral** (Cap. 2): *Escreva um teste* (invente a interface que deseja) → *Faça-o rodar* ("um verde rápido perdoa todos os pecados") → *Faça direito* (remova a duplicação introduzida).

## Key Concepts
- **Lista de tarefas/testes**: lista viva de testes a escrever; item em **negrito** = em andamento, ~~riscado~~ = feito; novos testes vão para o fim.
- **Dependência vs. duplicação**: dependência é o problema-chave; duplicação é o sintoma. Eliminar duplicação elimina dependência (por isso a regra 2).
- **Value Object**: `Dollar.times()` retorna um *novo* objeto em vez de mutar `self`; valores nunca mudam após criados, evitando o problema de sinônimos (aliasing).
- **Factory Method**: `Money.dollar(5)` no lugar de `new Dollar(5)` para ganhar flexibilidade de retornar subclasse diferente sem tocar nos testes.
- **Igualdade (equals)**: Value Objects precisam implementar `equals()` (e hashing); `5 CHF == 5 CHF` mesmo sendo objetos distintos.

## Mental Models
- Use **Faça de conta (Fake It)** quando não souber a implementação: retorne uma constante (`amount = 10`) e depois generalize trocando constantes por variáveis.
- Use **Triangulação** quando inseguro sobre a abstração: só generalize ao ter dois exemplos (`plus(3,1)==4` e `plus(3,4)==7`).
- Use **Implementação Óbvia** quando souber digitar a solução simples — "segunda marcha"; reduza a marcha se surpreendido por barras vermelhas.
- Pense na duplicação entre **dado do teste e dado do código** (o `10` que veio de `5*2`), não só entre dois trechos de código.

## Code Examples
```java
// Primeiro teste — inventa a interface desejada
public void testMultiplication() {
    Dollar five = new Dollar(5);
    Dollar product = five.times(2);
    assertEquals(10, product.amount);
    product = five.times(3);
    assertEquals(15, product.amount);
}
// Value Object: times() retorna NOVO Dollar, não muta o original
Dollar times(int multiplier) {
    return new Dollar(amount * multiplier);
}
```
- **What it demonstrates**: o salto de objeto mutável → Value Object, forçado por querer reusar `five` após multiplicar.

## Worked Example
A primeira passagem de `testMultiplication` (Cap. 1): o teste nem compila — 4 erros (sem classe `Dollar`, sem construtor, sem `times(int)`, sem campo `amount`). Beck elimina **um erro de cada vez** com stubs vazios até compilar. Roda → **barra vermelha** (esperava 10, veio 0). A menor mudança possível: `int amount = 10;` (constante). Verde. Agora vem a refatoração: o `10` é duplicação de `5*2`. Move o cálculo: `amount = 5 * 2` (verde), depois salva o `5` no construtor (`this.amount = amount`), usa em `times` (`amount = amount * multiplier`), e finalmente `amount *= multiplier`. A constante virou expressão sem nunca sair do verde. Resumo do que fez: lista → história/teste → stubs p/ compilar → rodar cometendo "pecados" → generalizar trocando constantes por variáveis → adicionar itens à lista em vez de resolver tudo.

## Key Takeaways
1. Falha é progresso: transforma "me dê multi-moeda" em "faça este teste passar".
2. TDD não é sobre *dar* passos pequenos; é sobre *poder* dar passos pequenos quando as coisas ficam estranhas.
3. Resolva "funciona" e "limpo" separadamente — o oposto do desenvolvimento guiado por arquitetura.
4. A interface do teste é um palpite; mude-o livremente quando o uso mostrar algo melhor.
5. Value Object resolve aliasing; toda operação retorna objeto novo.

## Connects To
- **Ch 2**: continua o exemplo até Expression/Bank e a retrospectiva financeira.
- **Ch 7**: os padrões Fake It, Triangulate, Obvious Implementation aqui demonstrados.
- **Ch 9**: Value Object e Factory Method formalizados como padrões de projeto.
