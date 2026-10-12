# Capítulo 9: Padrões de Projeto (Cap. 30)

## Core Idea
Os padrões de projeto (GoF e além) reaparecem no TDD, mas com um olhar diferente: muitos *emergem da fase de refatoração*, guiados pela eliminação de duplicação, não são planejados antecipadamente. Beck classifica cada um por quando aparece — na escrita do teste ou na refatoração.

## Frameworks Introduced
- **Command**: represente a invocação de uma computação como objeto (com `run()`), não como mensagem — quando precisar registrar, adiar ou manipular a chamada (ex.: `Runnable`).
- **Value Object**: estado fixo na criação, nunca muda; operações retornam novo objeto. Resolve aliasing; *deve* implementar igualdade/hashing.
- **Null Object**: represente o caso especial com um objeto de mesmo protocolo (ex.: `LaxSecurity` que nunca lança) — elimina checagens `!= null` espalhadas.
- **Template Method**: sequência invariável escrita em termos de outros métodos; subclasses preenchem (`setUp/runTest/tearDown`).
- **Pluggable Object**: substitua condicional explícito repetido por objeto com 2+ implementações (ex.: `SingleSelection`/`MultipleSelection`).
- **Pluggable Selector**: armazene o nome do método e invoque-o por reflexão — evita subclasses gratuitas com um só método. Use com parcimônia.
- **Factory Method**: crie objeto por método em vez de construtor, para flexibilidade de retornar outra classe.
- **Imposter**: nova implementação do mesmo protocolo introduz variação (Null Object e Composite são casos).
- **Composite**: comportamento de uma lista de objetos tratado como um só objeto (ex.: `Account` contendo `Holding`s).
- **Collecting Parameter**: passe um parâmetro para coletar resultados espalhados por vários objetos (ex.: `TestResult`, `ObjectOutput`).
- **Singleton**: "como fornecer variáveis globais? **Não forneça.**"

## Reference Tables
Uso dos padrões no TDD (Tabela 30.1):

| Padrão | Escrita de teste | Refatoração |
|---|---|---|
| Command | X | |
| Value Object | X | |
| Null Object | | X |
| Template Method | | X |
| Pluggable Object | | X |
| Pluggable Selector | | X |
| Factory Method | X | X |
| Imposter | X | X |
| Composite | X | X |
| Collecting Parameter | X | X |

## Code Examples
```java
// Pluggable Object: condicional duplicado vira polimorfismo
SelectionMode mode;
public void mouseDown() {
    selected = findFigure();
    mode = (selected != null) ? new SingleSelection(selected) : new MultipleSelection();
}
public void mouseMove() { mode.mouseMove(); }
public void mouseUp()   { mode.mouseUp(); }
```
```java
// Composite: Account e Transaction implementam Holding.balance()
interface Holding { Money balance(); }
Money balance() {                       // Account
    Money sum = Money.zero();
    for (int i=0; i<holdings.length; i++) sum = sum.plus(holdings[i].balance());
    return sum;
}
```
- **What it demonstrates**: o condicional `selected != null` que se espalhava por 3 métodos colapsa num objeto; `OverallAccount` desaparece — é só uma `Account` de `Account`s.

## Worked Example
**Null Object (`LaxSecurity`)**: `java.io.File` tem 18 checagens `guard != null`. A alternativa é uma classe que nunca lança:
```java
class LaxSecurity { public void canWrite(String path) { } }
public static SecurityManager getSecurityManager() {
    return security == null ? new LaxSecurity() : security;
}
```
Agora `setReadOnly()` chama `security.canWrite(path)` sem checar nulo. Beck conta que Erich Gamma o "nocauteou" calculando que introduzir o Null Object custava 10 linhas para eliminar *um* condicional — o trade-off nem sempre compensa.

## Anti-patterns
- **Singleton/variável global**: não use; pense melhor no projeto.
- **Pluggable Selector em excesso**: dificulta rastrear se o método é invocado; use só quando cada subclasse tem um único método.
- **Cheiro do Composite**: `Transaction` não tem "saldo" no mundo real — desconexão contextual aceita porque simplifica enormemente o código.

## Key Takeaways
1. Em TDD, padrões de *refatoração* emergem ao eliminar duplicação, não são desenhados antes.
2. Value Object exige igualdade; resolve o problema de sinônimos.
3. Pluggable Object cura a "praga" de condicionais explícitos espalhados.
4. Composite + Collecting Parameter andam juntos (vide `TestSuite`/`TestResult`).
5. A pergunta sobre globais tem uma só resposta: não.

## Connects To
- **Ch 1–3**: Value Object, Factory Method, Composite, Template Method, Collecting Parameter foram *vividos* nos exemplos.
- **Ch 10**: refatorações que introduzem estes padrões (Extract Interface, Reconcile Differences).
- **Ch 6**: Mock Object e Self Shunt usam Imposter/Pluggable.
