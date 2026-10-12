# Capítulo 12: Apêndices e Posfácio (Ap. I, Ap. II, Posfácio de Fowler)

## Core Idea
Material de apoio: a ferramenta de **diagramas de influência** (sistemas de Weinberg) usada por todo o livro, um exemplo completo de **Fibonacci dirigido por testes** para "cair a ficha", e a reflexão de **Martin Fowler** sobre o estado mental do TDD ("uma bola no ar por vez").

## Frameworks Introduced
- **Diagramas de Influência (Ap. I)**: modelo de Gerald Weinberg (*Quality Software Management*) para ver como elementos de um sistema se afetam.
  - Elementos: **atividades** (palavra/frase), **conexões positivas** (flecha: mais origem → mais destino), **conexões negativas** (flecha com círculo: mais origem → menos destino).
  - **Feedback**: ciclo no diagrama. Conte conexões negativas no ciclo: nº **par** = feedback positivo (amplifica); nº **ímpar** = feedback negativo (estabiliza).
- **Fibonacci dirigido por testes (Ap. II)**: derivação completa de `fib` por casos especiais + tabela de casos, generalizando `return 1+1` → `fib(n-1)+fib(n-2)`.
- **Modos monológicos (Posfácio, Fowler)**: programar trocando rápido entre modos elementares — adicionar feature (test-first), refatorar, e o "padrão cópia" — concentrando em *uma coisa por vez* sem a monotonia da linha de montagem.

## Key Concepts
- **Chaves de projeto de sistemas (Weinberg)**: criar ciclos virtuosos (feedback positivo de boas atividades), evitar espirais da morte, e criar feedback negativo para conter atividades que cresceram demais.
- **Tabela de casos**: fatorar asserções repetidas dirigindo o teste por uma tabela `{{entrada, esperado}, ...}` reduz o custo de cada novo caso a "seis teclas".
- **"Uma bola no ar por vez" (Fowler)**: ao adicionar feature, não se preocupe com projeto; ao refatorar, não se preocupe com feature — concentração total em cada modo reduz o estresse.

## Code Examples
```java
// Fibonacci derivado por testes: tabela de casos
public void testFibonacci() {
    int cases[][] = {{0,0},{1,1},{2,1},{3,2}};
    for (int i = 0; i < cases.length; i++)
        assertEquals(cases[i][1], fib(cases[i][0]));
}
int fib(int n) {
    if (n == 0) return 0;
    if (n == 1) return 1;
    return fib(n-1) + fib(n-2);
}
```
- **What it demonstrates**: a tabela elimina duplicação entre asserções; a generalização `2 → 1+1 → fib(n-1)+fib(n-2)` mostra Fake It + Triangulação em miniatura.

## Worked Example
**Derivando Fibonacci (Ap. II)**: `fib(0)=0` → `return 0`. `fib(1)=1` → trata 0 como caso especial, `return 1` para o resto. `fib(2)` passa por acidente (constante 1). `fib(3)=2` falha → `if (n<=2) return 1; return 2`. Generaliza: `2` é na verdade `1+1`; o primeiro `1` é `fib(n-1)`, o segundo `fib(n-2)` → `return fib(n-1)+fib(n-2)`. Limpa estreitando `n<=2` para `n==1`. Fibonacci inteiramente derivado de testes.

## Key Takeaways
1. Diagramas de influência tornam visíveis os laços de feedback que TDD explora (estresse, fadiga, confiança).
2. Conte conexões negativas: par = amplificador (vicioso ou virtuoso), ímpar = estabilizador.
3. Tabela de casos remove duplicação entre asserções por poucos centavos por caso.
4. TDD = trocar rápido entre modos monológicos; cada modo, uma preocupação só.
5. O ganho central, segundo Fowler, é manter "uma bola no ar por vez" — menos estresse, mais foco.

## Connects To
- **Ch 4–5**: diagramas de influência (espiral da morte do estresse, fadiga) introduzidos nos padrões.
- **Ch 7**: Fake It e Triangulação, vistos em miniatura no Fibonacci.
- **Ch 1**: "código limpo que funciona" — a meta que o posfácio reflete.
