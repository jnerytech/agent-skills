# Capítulo 5: Classe

## Core Idea
Uma classe declara: "esta **lógica** harmoniza-se e muda mais lentamente que os **dados** sobre os quais opera". Padrões de classe têm o maior alcance de todos. O núcleo do capítulo é **como expressar variação na lógica** — 5 técnicas com custos crescentes.

## Frameworks Introduced
### Nomeação
- **Nome simples de superclasse**: raízes de hierarquia recebem nome curto de uma só palavra, de uma metáfora forte (`Figura`, não `ObjetoDesenhado`). É o conceito-âncora — nomeada a classe, as operações vêm naturais.
- **Nome qualificado de subclasse**: modificador + nome da superclasse (`StretchyHandle`). Exceção: subclasse que é raiz de sua própria hierarquia → nome simples.

### Interface abstrata (separar interface de implementação)
- **Interface (Java `interface`)**: use quando a *implementação* muda mas a interface é estável, ou precisa de múltiplas visões da mesma classe. Custo: qualquer mudança na interface quebra todos os implementadores.
- **Classe abstrata**: use quando a interface **provavelmente mudará** — novas operações com implementação padrão não quebram subclasses. Limite: fidelidade a uma só superclasse.
- **Interface versionada**: para estender uma interface que não pode mudar → declare subinterface que a estende (`ReversibleCommand extends Command`). Feio, mas evolui interfaces travadas.
- **Objeto valor**: objeto imutável que age como valor matemático — operações retornam *novos* objetos. Defina todo estado no construtor, sem outras atribuições. Delimite a fronteira estado↔valor.

### Expressar variação na lógica (5 técnicas, custo crescente)
- **Subclasse**: "como aquele, exceto por...". Variação *unidimensional*, conhecida na criação, imutável. Fatore a superclasse em métodos de tarefa única para sobrescrever exatamente um.
- **Implementador**: sobrescreve método p/ variante; mensagem polimórfica abre o sistema para variações futuras.
- **Condicional (`if`/`switch`)**: mais simples e local, mas não muda sem editar a classe; proliferação reduz confiabilidade e duplica.
- **Delegação**: lógica comum na classe de referência, variação nos delegates; permite trocar comportamento *em runtime*.
- **Seletor plugável**: guarda nome de método em campo, invoca por reflexão. Custo alto — uso limitado.
- **Classe interna anônima**: sobrescreve 1-2 métodos inline. Só p/ API simples (`Runnable.run()`); curta, sem lógica testável.
- **Classe interna**: empacota computação local sem custo de novo arquivo; captura a instância envolvente (use `static` p/ desacoplar).
- **Comportamento específico de instância**: atribua na criação, não altere depois.
- **Classe biblioteca**: métodos estáticos num contêiner sem instâncias. Não escala — transforme em objeto quando possível.

## Key Concepts
- **Classes são caras**: reduza o nº delas (sem inchar as restantes).
- **Herança é compressão**: precisa entender a superclasse p/ entender a subclasse.
- **Codifique para interfaces, não implementações**, mas cada camada de interface custa — gaste só onde precisa de flexibilidade.

## Mental Models
- **"Sou como aquela superclasse, porém diferente"** = subclasse.
- **Micromundos matemáticos**: crie ilhas de valores imutáveis, gerencie-as a partir de um objeto de estado mutável (Fig 5.2: estado no centro, valores nas pontas).
- **Troque de estratégia à vontade**: visualize o mesmo código como condicional, subclasse e delegação; dê passos na direção que melhora o código.

## Code Examples
Interface versionada — estender sem quebrar:
```java
interface Command { void run(); }
interface ReversibleCommand extends Command { void undo(); }
// uso:
if (recent instanceof ReversibleCommand)
    ((ReversibleCommand) recent).undo();
```
Objeto valor imutável (contabilidade):
```java
class Transaction {
  final int value;
  Transaction(int value, Account credit, Account debit) {
    this.value = value; credit.addCredit(this); debit.addDebit(this);
  }
  int getValue() { return value; }
}
```
Estilo valor vs. mutável:
```java
bounds.translateBy(10, 20);            // mutável
bounds = bounds.translateBy(10, 20);   // valor: reatribui
```

## Reference Tables
| Técnica | Muda em runtime? | Custo de leitura | Quando |
|---|---|---|---|
| Condicional | não | baixo (tudo numa classe) | poucos ramos, estáveis |
| Subclasse | não (fixo na criação) | médio (entender super) | variação unidimensional |
| Delegação | **sim** | alto (navegação) | ferramenta/estratégia muda |
| Seletor plugável | sim | alto (o "truque") | 1-2 métodos, problema difícil |
| Interface vs Classe abstrata | — | — | interface estável vs interface que mudará |

## Worked Example — Condicional duplicado → delegação
Editor gráfico com `switch (getTool())` em `mouseDown()`, `mouseUp()`, `mouseMove()` — cada nova ferramenta exige editar todos e coordenar mudanças numa só classe:
```java
public void mouseDown() {
  switch (getTool()) {
    case SELECTING: /*...*/ break;
    case CREATING_RECTANGLE: /*...*/ break;
    default: break;
  }
}
```
Delegar para o objeto-ferramenta elimina os condicionais duplicados:
```java
// GraphicEditor
public void mouseDown() { tool.mouseDown(this); }
// RectangleTool
public void mouseDown(GraphicEditor editor) { editor.add(new RectangleFigure()); }
```
Truque: passar o delegador (`this`) como parâmetro resolve o "si mesmo" ambíguo — a ferramenta adiciona a figura *no editor*, não em si. Alternativa: guardar `editor` em campo no construtor (mais simples se a ferramenta não é reusada em vários editores).

## Anti-patterns
- **Hierarquias paralelas**: p/ cada subclasse aqui precisa de uma lá → acoplamento implícito, mudança em ambas. (Caso do sistema de seguros — levou 1 ano p/ resolver movendo a variação p/ um objeto de fluxos de caixa.)
- **Copiar-e-editar método grande da superclasse**: acoplamento implícito terrível.
- **Maioria de objetos valor num sistema de estado**: pior dos dois mundos.
- **Superabstração**: torne a raiz instanciável se houver qualquer chance — elimina abstrações inúteis.
- **Deletar código "morto" invocado por seletor plugável**: quebra o sistema silenciosamente.

## Key Takeaways
1. Dados mudam mais que lógica — é isso que faz as classes funcionarem.
2. Escolha a técnica de variação pelo custo: condicional < subclasse < delegação < seletor plugável.
3. Só delegação e condicional expressam lógica *mutável* em runtime; subclasse é fixa na criação.
4. Prefira classe abstrata quando a interface pode crescer; interface Java quando precisa de múltiplas visões.
5. Nomeie a classe primeiro — é o conceito-âncora; invista tempo (até anos) no nome certo.

## Connects To
- **Ch 3**: nomeação e objeto valor aplicam simetria e expressão declarativa.
- **Ch 6 (Estado)**: classes agrupam estado relacionado.
- **Ch 7 (Comportamento)**: fluxo de controle e mensagens polimórficas.
- **Ch 10**: interfaces versionadas e evolução em frameworks.
