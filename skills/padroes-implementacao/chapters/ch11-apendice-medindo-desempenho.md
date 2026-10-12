# Apêndice: Medindo Desempenho

## Core Idea
Um framework de cronometragem (usado no Cap 9) que mede o tempo de operações **conforme escalam** (tamanho 1, 10, ..., 100.000). Serve de estudo de caso: aplica quase todos os padrões do livro e ensina a **medir antes de acreditar**. Contorna a baixa precisão do relógio repetindo a operação até passar 1 segundo.

## Frameworks Introduced
- **Operação como método** (estilo JUnit): cada operação a cronometrar é um método; a classe recebe um `int size` no construtor p/ escalar.
- **Adaptação de precisão**: invoca o método 1, 2, 4, ... vezes até acumular ~1s; tempo = total / iterações.
- **Cancelamento de sobrecarga**: mede o custo da invocação por reflexão (~150 ns) com um `nothing()` vazio e subtrai — `getMethodTime() = (totalTime - overhead) / iterations`.
- **Cache de instância**: cria a instância de teste **uma vez** (não por invocação). Criar lista de 100k por invocação levaria ~1,5 semana; com cache, ~1 segundo.

## Key Concepts
- **O otimizador Java pode eliminar sua medição**: `for(String each: set){}` com corpo vazio foi removido pelo JIT → verifique sempre se os resultados fazem sentido.
- **Diferença de cache vs. JUnit**: JUnit cria instância nova por teste (isolamento); o cronômetro reusa → cada método **deve deixar o estado inalterado** (`add("b"); remove("b")`).
- **Sonda no meio da coleção** (`size/2`): cenário de pior caso p/ busca linear.
- **`getDeclaredMethods()`** não vê superclasses → o framework não suporta herança de métodos de cronometragem (limitação assumida conscientemente).

## Code Examples
Operação escalável:
```java
public class ListSearch {
  private List<Integer> numbers; private int probe;
  public ListSearch(int size) {
    numbers = new ArrayList<Integer>();
    for (int i = 0; i < size; i++) numbers.add(i);
    probe = size / 2;
  }
  public void search() { numbers.contains(probe); }
}
```
Coração do cronômetro:
```java
void run() throws Exception {
  iterations = 1;
  while (true) {
    totalTime = computeTotalTime();
    if (totalTime > MethodsTimer.ONE_SECOND) break;
    iterations *= 2;
  }
  overhead = overheadTimer(iterations).computeTotalTime();
}
```

## Worked Example — Crenças que a medição derruba
- **"Pré-alocar o tamanho do conjunto melhora o desempenho"**: medição mostrou que pré-alocar **zero** fica dentro de 10% de pré-alocar o tamanho final. Crença amplamente difundida, refutada.
- **`ArrayList.add(0,x)` seria linear?** ArrayList otimiza inserção *no final* (constante); no início é linear. `LinkedList.get(size/2)` parece linear, mas LinkedList otimiza busca de trás p/ frente p/ índices > metade.
- Lição: antes de tornar o código complexo, **meça** se a complexidade traz benefício.

## Reference Tables
Padrões do livro exemplificados no apêndice:
| Padrão | Onde |
|---|---|
| Construtor completo | `MethodTimer(size, method)` |
| Nome revelador de intenção | `overheadTimer()`, `getMethodTime()` |
| Objeto método / comando | `MethodTimer` (calcula tempo de 1 método) |
| Constante | `ONE_SECOND`, `MAXIMUM_SIZE` agrupadas |
| Método fábrica estático | `overheadTimer(iterations)` |
| Cache (estado) | instância reusada entre invocações |

## Anti-patterns
- **Confiar em "sabedoria" de desempenho sem medir** (pré-alocação).
- **Construtor fazendo trabalho pesado**: Beck resistiu — separar criação do trabalho permite serializar/enviar `MethodTimer` pela rede sem custo.
- **Conselho dogmático**: "sempre inclua toda flexibilidade" E "codifique só p/ hoje" estão *ambos* errados — ajuste ao contexto (público, nº de testes).

## Key Takeaways
1. Meça; não acredite em folclore de desempenho.
2. Ajuste o estilo ao contexto — simplificações reduziram o esforço aqui, aceitáveis p/ público pequeno.
3. Repetição adaptativa + cancelamento de sobrecarga = medida precisa com relógio impreciso.
4. Cuidado com o otimizador eliminando a operação medida.
5. **A grande lição do livro**: programar é comunicar-se com humanos, não só com a máquina.

## Connects To
- **Ch 9**: gerou todas as tabelas de desempenho de coleções.
- **Ch 4**: economia — só adicione complexidade se o benefício for medido.
- **Ch 8**: construtor completo, objeto método, nome revelador de intenção, fábrica estática.
