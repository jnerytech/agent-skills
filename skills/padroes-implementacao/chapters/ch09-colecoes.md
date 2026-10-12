# Capítulo 9: Coleções

## Core Idea
Coleções expressam a **variação de número** (0, 1, muitos) — o tipo mais fundamental de variação de *dados*, assim como condicionais/mensagens expressam variação de *lógica*. A escolha precisa de interface + implementação comunica a intenção do programador e governa o desempenho.

## Frameworks Introduced
### 3 metáforas
- **Variável multivalorada**: a coleção "desaparece", só os elementos importam.
- **Objeto**: coleção tem identidade, é transferível (→ risco de chamada por referência e sinônimos).
- **Conjunto matemático**: `size()` (cardinalidade), `contains()` (inclusão). União/interseção só via `addAll`/`retainAll`/`removeAll` (que *mutam* o recebedor).

### Regra de declaração
- **Interface mais geral possível na declaração, implementação mais específica na criação** — mas **consistência vence generalidade** (Beck generalizou tudo em JUnit e virou bagunça; declarar tudo como `List` ficou mais legível).

### 4 questões que a coleção expressa
- **Tamanho** (fixo p/ vetor, variável p/ maioria)
- **Ordem** importa? → `List`/`SortedSet`
- **Unicidade**? → `Set`
- **Acesso** por iteração ou por chave? → `Map`

### Estender coleções
- **Prefira delegação a herança**: `class Library { Collection<Book> books; }` — não `class Library extends ArrayList`. Herdar mistura metáforas, força deserdar operações inválidas (`clear`, `toArray`) e desperdiça a herança única. Só estenda p/ criar coleção de uso geral (algo p/ `java.util`).

## Key Concepts
- **Desempenho viola consequências locais**: trocar `ArrayList`→`HashSet` num lugar pode tornar lento um método distante que depende de `contains()` rápido.
- **Estratégia de desempenho**: implementação simples primeiro; especialize sob medição; concentre a decisão; pare quando bom.
- **Map implementa estado extrínseco e estado variável** (Ch 6).
- **Vetor**: ~10× mais rápido que `ArrayList.get(i)`, mas protocolo incompatível e tamanho fixo — use só em gargalo pequeno.

## Reference Tables
Interfaces (do menos p/ o mais capaz):
| Interface | Ordem | Duplicatas | Acesso por chave |
|---|---|---|---|
| Array | fixa (índice) | sim | índice int |
| Iterable | — | — | só iterar |
| Collection | não garante | sim | não |
| List | estável (índice) | sim | índice int |
| Set | não | **não** | não |
| SortedSet | ordenada (Comparator) | não | não |
| Map | não | valores sim, chaves não | chave qualquer |

Implementações (escolha = desempenho):
| Interface | Rápida/simples | Preserva ordem inserção | Ordenada |
|---|---|---|---|
| Collection/List | ArrayList | — | — |
| List | ArrayList (acesso) | LinkedList (add/remove) | — |
| Set | HashSet | LinkedHashSet (+30%) | TreeSet (log n) |
| Map | HashMap | LinkedHashMap | TreeMap (log n) |

Perfis espelhados: **ArrayList** rápida p/ acesso, lenta p/ add/remove; **LinkedList** o inverso. `ArrayList` domina (~3400 usos vs ~800 `HashSet` no Eclipse+JDK).

Utilitários `Collections`:
- `binarySearch(lista, elem)` → log₂n, mas só em lista ordenada com acesso aleatório (ArrayList).
- `reverse` / `shuffle` / `sort` (copia p/ vetor, ordena, copia de volta → mesmo custo em Array/Linked).
- `unmodifiableCollection/List/Set/Map` → lança exceção em runtime na modificação.
- `singleton(x)` → Set imutável de 1 elemento; `emptyList()` → coleção vazia imutável.

## Worked Example — Autores únicos e ordenados
Set descarta contagem — só quero *quem* são os autores, não quantos livros:
```java
printAuthors(new HashSet<Author>(getAuthors()));  // remove duplicatas
```
Únicos E ordenados → `SortedSet` com `Comparator`:
```java
public Collection<String> getAlphabeticalAuthors() {
  Comparator<Author> sorter = new Comparator<Author>() {
    public int compare(Author a, Author b) {
      if (a.getLastName().equals(b.getLastName()))
        return a.getFirstName().compareTo(b.getFirstName());
      return a.getLastName().compareTo(b.getLastName());
    }
  };
  SortedSet<Author> results = new TreeSet<Author>(sorter);
  for (Book each : getBooks()) results.add(each.getAuthor());
  return results;
}
```

## Anti-patterns
- **`class X extends ArrayList`** p/ ganhar comportamento de coleção: mistura metáforas, desperdiça herança → delegue.
- **Generalizar toda declaração dogmaticamente**: inconsistência (`Iterable` aqui, `Collection` ali, `List` lá) atrapalha mais.
- **Retornar coleção crua** de acessor: `Iterable`/`Iterator` permitem `remove()` sem avisar o dono.
- **Otimizar coleção sem medição**: desempenho tem consequências distantes.
- **Duplicar quase todo o protocolo da coleção** no objeto: sinal de que o objeto devia *agir* mais pelos clientes.

## Key Takeaways
1. Coleção = variação de número; interface escolhida comunica ordem/unicidade/acesso.
2. Interface geral + implementação específica — mas consistência primeiro.
3. Desempenho: comece simples, meça, especialize, concentre, pare.
4. ArrayList é o default; HashSet p/ `contains` rápido; LinkedList p/ add/remove pesado.
5. Delegue a uma coleção; não herde dela.

## Connects To
- **Ch 3**: consequências locais (desempenho as viola).
- **Ch 5**: extensão via delegação vs. herança; classe interna anônima (Comparator).
- **Ch 6**: Map implementa estado extrínseco/variável.
- **Ch 8**: método acessador de coleção (acesso seguro).
- **Apêndice**: ferramenta que gerou as medições de desempenho.
