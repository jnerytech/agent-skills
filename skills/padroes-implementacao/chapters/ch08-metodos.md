# Capítulo 8: Métodos

## Core Idea
Dividir lógica em métodos sinaliza "estes pedaços não estão intimamente conectados", permite reúso e comunica intenção pelo nome. O padrão-mãe é **método composto**: métodos feitos de chamadas a outros, todos aproximadamente no **mesmo nível de abstração**.

## Frameworks Introduced
### Estrutura
- **Método composto**: chamadas a outros métodos no mesmo nível de abstração. Mistura de níveis (`input(); flags|=0x0080; output()`) soa dissonante.
- **Objeto método**: método longo com muitos parâmetros/temporárias → vira classe própria. Depois de extraído, refatorar é trivial (todo dado é campo). Padrão favorito de Beck (usa pouco, resultado espetacular).
- **Método auxiliar**: métodos privados pequenos que a composição gera; escondem detalhe e eliminam subexpressão comum. Podem ser curtos demais.

### Nomeação
- **Nome revelador de intenção**: nomeie pelo *propósito do invocador*, não pela implementação (`find()` > `linearCustomerSearch()`). Pense em como o nome aparece no código chamador — deve contar uma história.
- **Comentário de método**: só p/ o que o código não diz; muitos comentários são redundantes e ficam desatualizados sem feedback. Teste automatizado comunica melhor restrições.

### Visibilidade
- **Visibilidade de método**: limite ao máximo; revele aos poucos. `private` = máxima flexibilidade futura; `public` = compromisso de manutenção. `package` = mova a funcionalidade ou torne público; `protected` = reúso por subclasse.

### Variação e retorno
- **Método sobrescrito**: expressa variação; `super.method()` só p/ mesmo nome. Método bem composto = ganchos p/ sobrescrever inteiro.
- **Método sobrecarregado**: mesmos nome/propósito, tipos de parâmetro alternativos. Nunca varie o *tipo de retorno* entre sobrecargas — dê outro nome.
- **Tipo de retorno de método**: mais abstrato que expresse a intenção (`Collection` esconde ordem que `List` implicaria).

### Conversão
- **Método de conversão**: `polar.asCartesian()` — no objeto fonte; poucas conversões, tipos similares. Introduz dependência fonte→destino.
- **Construtor de conversão**: `new File(String)` — no objeto destino; muitas conversões (evita inchar a fonte). Preferido por Beck.

### Criação
- **Construtor completo**: retorna objeto pronto p/ computar; `new Rectangle(0,0,50,200)` comunica os 4 obrigatórios (vs. série de setters que não). Afunile todos os construtores num construtor mestre.
- **Método fábrica**: estático; retorna tipo abstrato, nome por intenção (cache, subclasse runtime). Só quando faz *mais* que criar — leitor curioso.
- **Fábrica interna**: método que cria/retorna objeto auxiliar complexo (ex.: `computeX()` na inicialização preguiçosa); convida refinamento por subclasse.

### Acessores
- **Método acessador de coleção**: **não** retorne a coleção crua nem `unmodifiableList` (erro só em runtime); ofereça `addBook()`, `bookCount()`, ou um `Iterator` que barra `remove()`.
- **Método de atribuição booleana**: `valid()`/`invalid()` mais legível que `setValid(bool)` — quando as chamadas são constantes. Se há expressão booleana, volte a `setValidity(bool)`.
- **Método de consulta**: booleanos com prefixo `is`/`has`/`was` (`isVisible()`).
- **Método de igualdade**: `equals()` + `hashCode()` juntos; hash só com dados usados na igualdade.
- **Método get/set**: nomeados pela implementação → relute em torná-los públicos. Get público = sinal de que a lógica deveria estar aqui. `set` interno serve de mecanismo de restrição.
- **Cópia de segurança**: copie coleção antes de retornar/armazenar p/ evitar sinônimos — paliativo, não semântica principal.
- **Método de impressão para depuração**: `toString()` p/ formato amigável ao programador; não sobrecarregue com múltiplos propósitos.

## Key Concepts
- **Desempenho de métodos pequenos é não-problema**: benchmark de Beck deu 20-30% entre 1M laço e 1M mensagens — irrelevante p/ a maioria.
- **Escreva métodos com fatos, não especulação**: faça funcionar, depois estruture. Se a divisão piora, alinhe tudo num método gigante e reparticione.
- **Ação a distância**: A depende da representação interna de B → mudança em B quebra A. Mova lógica e dados juntos.

## Mental Models
- Objeto = "estado harmoniza-se p/ apoiar uma computação cujos detalhes por ora são irrelevantes".
- **Tamanho de método**: grande favorece navegação/orientação; pequeno favorece entender detalhes. Método composto resolve os dois.
- **Get público perdido**: `if (widget.isVisible()) widget.doSomething()` → o método provavelmente pertence ao widget.

## Reference Tables
| Conversão | Onde | Quando |
|---|---|---|
| Método de conversão | objeto fonte | poucas, tipos similares |
| Construtor de conversão | objeto destino | muitas conversões |
| Método fábrica | classe (estático) | precisa tipo abstrato/lógica extra |

| Criação | Comunica obrigatórios? | Tipo retornado |
|---|---|---|
| Construtor completo | sim | classe concreta |
| Setters após `new()` | não | concreta |
| Método fábrica | via construtor abaixo | abstrato |

## Worked Example — Extrair objeto método
`complexCalculation()` longo, muitos parâmetros/temporárias, submétodos difíceis de nomear. Passos:
1. Classe com nome do método: `ComplexCalculator`.
2. Um **campo** p/ cada parâmetro, variável local e campo usado (mesmos nomes).
3. **Construtor** recebendo os parâmetros do método original + campos do objeto original usados.
4. Copie o corpo p/ `calculate()` na nova classe; refs viram refs a campos.
5. Corpo do original vira:
```java
complexCalculation() { new ComplexCalculator().calculate(); }
```
6. Se o original atribuía campos, colha após `calculate()`:
```java
complexCalculation() {
  ComplexCalculator calculator = new ComplexCalculator();
  calculator.calculate();
  mean = calculator.mean; variance = calculator.variance;
}
```
Agora extrair métodos é trivial (dados são campos) → variáveis viram locais, subexpressões viram auxiliares nomeados. Se precisar chamar o objeto original, alinhe mais antes.

Acessador de coleção seguro (barra `remove`):
```java
Iterator<Book> getBooks() {
  final Iterator<Book> reader = books.iterator();
  return new Iterator<Book>() {
    public boolean hasNext() { return reader.hasNext(); }
    public Book next() { return reader.next(); }
    public void remove() { throw new UnsupportedOperationException(); }
  };
}
```

## Anti-patterns
- **Estratégia de implementação no nome** (`linearCustomerSearch`): esconda, use `find()`/`fastFind()`.
- **Tipo de retorno variando entre sobrecargas**: ilegível.
- **Retornar coleção crua ou `unmodifiableList`**: quebra invariantes / erro só em runtime.
- **Abuso de cópia de segurança**: sistema bancário lento → clientes usam versão insegura → defeitos de sinônimo; o problema real era protocolo pobre.
- **`toString()` multipropósito**: corretor, DB e programador querem coisas diferentes.
- **Get/set público como interface**: vaza implementação (`setJustification(CENTERED)` → prefira `centered()`).

## Key Takeaways
1. Método composto no mesmo nível de abstração é a base; auxiliares o completam.
2. Nomeie por intenção do invocador; a implementação fica no corpo.
3. Limite visibilidade e revele aos poucos — `private` primeiro.
4. Construtor completo comunica obrigatórios; fábrica só quando faz mais que criar.
5. Get/set públicos são cheiro de lógica mal localizada — mova lógica+dados juntos.

## Connects To
- **Ch 3**: consequências locais (ação a distância), lógica e dados em harmonia (get/set).
- **Ch 6**: inicialização preguiçosa (fábrica interna), objeto parâmetro (objeto método).
- **Ch 7**: mensagem de decomposição (alternativa ao objeto método), cláusula de guarda (`equals`).
- **Ch 9**: método acessador de coleção → interfaces de coleção.
