# Capítulo 7: Padrões de Barra Verde (Cap. 28)

## Core Idea
Depois de um teste vermelho, como chegar ao verde *rapidamente* — mesmo que o código resultante seja temporariamente feio. Trate a barra vermelha como condição a corrigir o quanto antes. Estes são os três (mais dois) movimentos centrais do TDD.

## Frameworks Introduced
- **Faça de Conta (Fake It 'Til You Make It)**: primeira implementação = retorne uma constante; depois transforme gradualmente a constante em expressão com variáveis.
  - When to use: você tem um teste vermelho mas não sabe a implementação.
  - How: `return "1 run, 0 failed"` → `return "%d run, 0 failed" % self.runCount` → `return "%d run, %d failed" % (...)`.
  - Why it works: barra verde dá controle psicológico e de escopo; a refatoração depois elimina a duplicação entre teste e código.
- **Triangular (Triangulate)**: só abstraia quando tiver *dois ou mais* exemplos.
  - When to use: muito inseguro sobre a abstração correta.
  - How: `assertEquals(4, plus(3,1))` e `assertEquals(7, plus(3,4))` → generaliza `return augend + addend`.
  - Failure mode: regras criam um laço (poderia apagar uma asserção e voltar à constante) — use só quando realmente inseguro.
- **Implementação Óbvia (Obvious Implementation)**: sabe digitar a operação simples? Apenas digite-a. "Segunda marcha"; reduza para Fake It/Triangulate se barras vermelhas o surpreenderem.
- **Um para Muitos (One to Many)**: implemente a operação primeiro *sem* a coleção, depois faça-a funcionar com a coleção (adicione parâmetro, use Isolar Mudança).

## Key Concepts
- **Controle de escopo**: começar concreto e generalizar evita confusão prematura com problemas futuros.
- **Isolar a Mudança (Isolate Change)**: adicionar o parâmetro-array ao teste libera mudar a implementação sem afetar o teste (e vice-versa).
- **Faz de conta não viola "não escreva código a mais"**: na refatoração você elimina a duplicação de dados entre teste e código.

## Mental Models
- Não há virtude na "natureza intermediária" de Fake It/Triangulate — se sabe e digita rápido, use Implementação Óbvia.
- Implementação Óbvia exige perfeição de você; psicologicamente devastador se errar. Esteja pronto para reduzir a marcha.
- Use Triangulação "até se cansar" e migrar para Fake It ou Implementação Óbvia.

## Code Examples
```java
// Fake It → generalização gradual de yesterday()
public MyDate yesterday() { return new MyDate("28.2.02"); }            // constante
public MyDate yesterday() { return new MyDate(new MyDate("31.3.02").days()-1); }
public MyDate yesterday() { return new MyDate(this.days()-1); }        // generalizado
```
```java
// One to Many: começa escalar, vira coleção via Isolar Mudança
private int sum(int[] values) {
    int sum = 0;
    for (int i = 0; i < values.length; i++) sum += values[i];
    return sum;
}
```
- **What it demonstrates**: a constante `28.2.02` carrega duplicação com o teste; cada passo a substitui por expressão sem sair do verde.

## Worked Example
**Triangulação de `plus()`**: escreve `assertEquals(4, plus(3,1))` e implementa `return 4;` (Fake It). Para triangular o projeto certo, adiciona a segunda asserção `assertEquals(7, plus(3,4))`. Agora a constante `4` não serve para ambos — com *dois* exemplos pode abstrair com segurança: `return augend + addend;`. Beck nota o paradoxo: com a abstração pronta, poderia apagar uma asserção, mas então `plus` poderia voltar a ser constante. Por isso ele só triangula quando genuinamente inseguro; caso contrário confia em Fake It ou Implementação Óbvia.

## Anti-patterns
- **Exigir sempre Implementação Óbvia**: vira perfeccionismo paralisante; mantenha o ritmo, reduza a marcha quando errar.
- **Abstrair com um só exemplo**: prematuro; a regra de Triangulação exige dois.

## Key Takeaways
1. Verde primeiro, beleza depois — "um verde rápido perdoa todos os pecados, por um momento".
2. Fake It: constante → expressão, eliminando duplicação teste↔código na refatoração.
3. Triangulação: abstraia só com 2+ exemplos, e só quando inseguro.
4. Implementação Óbvia é a marcha padrão para operações simples.
5. One to Many: escalar primeiro, coleção depois.

## Connects To
- **Ch 1–2**: estes três padrões são "a última revisão" da Retrospectiva Financeira.
- **Ch 10**: Isolar Mudança e Migrar Dados (usados em One to Many).
- **Ch 5**: a cadeia de escape (sabe→Óbvia; não sabe→Fake It; incerto→Triangule).
