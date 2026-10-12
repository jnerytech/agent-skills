# Capítulo 12: Lidando com herança

## Ideia central
A herança é um mecanismo poderoso, mas fácil de aplicar de forma indevida — e o uso indevido raramente é óbvio até ser tarde demais. Várias refatorações movem recursos para cima ou para baixo na hierarquia, adicionam/removem classes dela, ou trocam herança por delegação quando o relacionamento deixa de ser adequado (herança só pode ser "usada uma vez" por classe; delegação permite variar por múltiplos eixos).

## Catálogo de refatorações

### Subir método (Pull Up Method)
- inversa de: Descer método (Push Down Method)
- **Motivação**: eliminar código duplicado quando duas subclasses têm métodos com o mesmo corpo (ou equivalente); reduz risco de uma cópia ser alterada e a outra não.
- **Procedimento**:
  - Inspecione os métodos para garantir que sejam idênticos; se não forem, refatore-os primeiro (ex.: Parametrizar função).
  - Verifique se todas as referências do corpo (métodos/campos) são acessíveis a partir da superclasse; se necessário, use Subir campo antes.
  - Se as assinaturas diferirem, use Mudar declaração de função para unificá-las.
  - Crie o método na superclasse copiando o corpo de um dos métodos; teste estaticamente.
  - Apague o método de cada subclasse, um de cada vez, testando após cada remoção.
  - Se o corpo referenciar um recurso presente só nas subclasses, considere um "erro de responsabilidade da subclasse" (método armadilha que lança erro) na superclasse.

### Subir campo (Pull Up Field)
- inversa de: Descer campo (Push Down Field)
- **Motivação**: subclasses desenvolvidas de forma independente costumam duplicar campos (às vezes com nomes diferentes); subir o campo comum remove a duplicação de dados e possibilita depois subir os comportamentos que o usam.
- **Procedimento**:
  - Inspecione todos os usos do campo candidato para garantir uso semelhante.
  - Se os nomes diferirem, use Renomear campo para igualá-los.
  - Crie o campo na superclasse (acessível às subclasses, ex.: protected).
  - Apague os campos nas subclasses; teste.

### Subir corpo do construtor (Pull Up Constructor Body)
- **Motivação**: construtores têm regras especiais (ordem, chamada a super), então mover comportamento comum para a superclasse exige um procedimento próprio em vez do Extrair função + Subir método direto.
- **Procedimento**:
  - Defina um construtor na superclasse (se ainda não existir), chamado pelos construtores das subclasses.
  - Use Deslocar instruções para mover as instruções comuns para logo depois de `super()`.
  - Remova o código comum de cada subclasse, mova-o para a superclasse, passando como parâmetros de `super()` o que for necessário; teste.
  - Se houver código comum que não possa ficar no início do construtor (ex.: depende de campo definido só na subclasse), use Extrair função e depois Subir método nesse trecho.

### Descer método (Push Down Method)
- inversa de: Subir método (Pull Up Method)
- **Motivação**: um método relevante só para uma subclasse (ou poucas) deixa o código mais claro se ficar apenas nela; só se aplica quando quem chama sabe estar lidando com a subclasse específica — senão, use Substituir condicional por polimorfismo com comportamento placebo na superclasse.
- **Procedimento**:
  - Copie o método para toda subclasse que precisar dele.
  - Remova o método da superclasse; teste.
  - Remova das subclasses que não precisarem dele; teste.

### Descer campo (Push Down Field)
- inversa de: Subir campo (Pull Up Field)
- **Motivação**: campo usado só por uma subclasse (ou poucas) deve morar nela.
- **Procedimento**:
  - Declare o campo em todas as subclasses que precisarem dele.
  - Remova da superclasse; teste.
  - Remova das subclasses que não precisarem; teste.

### Substituir código de tipos por subclasses (Replace Type Code with Subclasses)
- incorpora: Substituir enumeração pelo padrão State/Strategy; Extrair subclasse
- inversa de: Remover subclasse (Remove Subclass)
- **Motivação**: um campo de código de tipo (enum/string/número) é suficiente na maioria dos casos, mas subclasses ajudam quando (1) há lógica condicional baseada no tipo que se beneficia de polimorfismo (via Substituir condicional por polimorfismo), ou (2) há campos/métodos válidos só para certos valores do tipo (aplicando Descer campo depois). Decisão-chave: criar subclasses diretas do próprio objeto (mais simples, mas não reutilizável para outro eixo de variação e não serve se o tipo for mutável) ou extrair o código de tipo para uma classe própria (herança indireta, via Substituir primitivo por objeto) e aplicar a refatoração nela.
- **Procedimento**:
  - Autoencapsule o campo do código de tipo (Encapsular variável).
  - Escolha um valor; crie a subclasse; sobrescreva o getter do código de tipo para devolver o literal.
  - Crie lógica de seletor mapeando o parâmetro para a subclasse certa — em herança direta, mova-a para uma factory (Substituir construtor por função de factory); em herança indireta, ela pode ficar no construtor. Teste.
  - Repita para cada valor, testando a cada passo.
  - Remova o campo do código de tipo; teste.
  - Use Descer método + Substituir condicional por polimorfismo em qualquer código que ainda use os acessores do código de tipo; depois remova esses acessores (Remover código morto).

### Remover subclasse (Remove Subclass)
- anteriormente: Substituir subclasse por campos
- inversa de: Substituir código de tipos por subclasses
- **Motivação**: subclasses têm custo de compreensão; se, com a evolução do sistema, uma subclasse passa a fazer muito pouco (ex.: só sobrescrever um getter constante), compensa removê-la e representar a diferença como um campo na superclasse.
- **Procedimento**:
  - Use Substituir construtor por função de factory nos construtores das subclasses (centralizando a lógica de decisão de qual subclasse criar).
  - Extraia e mova para a superclasse qualquer teste de tipo (`instanceof`) via Extrair função + Mover função; teste a cada mudança.
  - Crie um campo para representar o tipo antes guardado pela subclasse.
  - Modifique os métodos que dependiam da subclasse para usar o novo campo.
  - Apague a subclasse; teste.
  - Em grupos de subclasses, encapsule todas primeiro (factory, testes de tipo movidos) e só então remova uma de cada vez.

### Extrair superclasse (Extract Superclass)
- **Motivação**: duas classes fazendo tarefas parecidas podem ter as semelhanças extraídas para uma superclasse comum, usando Subir campo/Subir método. Alternativa: Extrair classe (herança vs. delegação) — Extrair superclasse costuma ser mais simples de começar, sabendo que dá para migrar depois com Substituir superclasse por delegação se necessário. Herança pode ser planejada com base em taxonomias, mas com mais frequência emerge durante a evolução do código, ao perceber elementos comuns.
- **Procedimento**:
  - Crie uma superclasse vazia; faça as classes originais herdarem dela (ajuste construtores com Mudar declaração de função se preciso). Teste.
  - Um a um, use Subir corpo do construtor, Subir método e Subir campo para mover elementos comuns.
  - Nos métodos restantes, procure partes comuns; use Extrair função seguido de Subir método.
  - Avalie clientes das classes originais para que passem a usar a interface da superclasse.

### Condensar Hierarquia (Collapse Hierarchy)
- **Motivação**: ao subir e descer recursos durante refatorações sucessivas, uma classe e sua classe-pai às vezes deixam de ser suficientemente diferentes para justificar existirem separadas.
- **Procedimento**:
  - Escolha a classe a ser removida (pelo nome que fizer mais sentido no futuro; se nenhum for melhor, escolha arbitrariamente).
  - Use Subir campo, Descer campo, Subir método e Descer método para reunir tudo em uma única classe.
  - Ajuste referências à classe removida para apontarem para a que permanece.
  - Remova a classe vazia; teste.

### Substituir subclasse por delegação (Replace Subclass with Delegate)
- **Motivação**: herança é natural quando o comportamento varia por categoria, mas só pode ser usada em um único eixo de variação por vez, e cria acoplamento íntimo (mudanças na superclasse podem quebrar subclasses facilmente, especialmente entre equipes/módulos diferentes). Delegação resolve os dois problemas: permite delegar a várias classes por motivos diferentes, com interface explícita e menos acoplamento. Frequentemente equivalente a substituir subclasses pelos padrões State/Strategy do GoF. Fowler prefere começar com herança (mais simples) e migrar para delegação só quando surgir a necessidade — ex.: mudar dinamicamente de categoria em tempo de execução, o que herança não permite.
- **Procedimento**:
  - Se houver muitas chamadas a construtores, aplique Substituir construtor por função de factory.
  - Crie uma classe de delegação vazia; seu construtor recebe dados específicos da subclasse e, em geral, uma referência de volta ("back-reference") ao host.
  - Adicione um campo na superclasse para guardar a delegação; inicialize-o na criação da subclasse (na factory ou no construtor).
  - Escolha um método da subclasse; use Mover função para movê-lo para a classe de delegação (sem remover ainda o original).
  - Se o método precisar de elementos da superclasse, acrescente referência de volta na classe de delegação.
  - Substitua o corpo original por uma chamada de despacho protegida pela presença da delegação (`this._delegate ? ... : ...`), ou remova como código morto se não houver chamadas externas. Teste.
  - Repita até mover todos os métodos; ao final, ajuste chamadas de construtor para usarem o construtor da superclasse e remova código morto da subclasse.
  - Com múltiplas subclasses repetindo estrutura, aplique Extrair superclasse nas classes de delegação para eliminar duplicação.

### Substituir superclasse por delegação (Replace Superclass with Delegate)
- anteriormente: Substituir herança por delegação
- **Motivação**: herança só é semanticamente válida quando (a) toda função da superclasse se aplica à subclasse e (b) toda instância da subclasse é um objeto válido de superclasse (ex.: erro clássico de fazer Stack herdar de List — operações de lista poluem a interface da pilha, mesmo úteis para reuso interno). Erro relacionado: "homônimo entre tipo e instância" (ex.: modelo de carro herdando de carro físico). Mesmo quando a modelagem é razoável, o acoplamento herança-subclasse é alto o bastante para justificar migrar; o custo é escrever métodos de encaminhamento (tediosos, mas simples e pouco propensos a erro).
- **Procedimento**:
  - Crie um campo na subclasse referenciando uma instância da (antiga) superclasse.
  - Para cada elemento da superclasse usado, crie na subclasse uma função de encaminhamento para essa referência; teste após encaminhar cada grupo coerente (pares get/set só são testáveis juntos).
  - Quando todos os elementos tiverem sido encaminhados, remova o vínculo de herança.

## Exemplo de código
Substituir código de tipos por subclasses (herança direta), a partir de `Employee` com um campo `type` que aceita `"engineer" | "manager" | "salesman"`:

```javascript
// Antes
class Employee {
  constructor(name, type) {
    this.validateType(type);
    this._name = name;
    this._type = type;
  }
  validateType(arg) {
    if (!["engineer", "manager", "salesman"].includes(arg))
      throw new Error(`Employee cannot be of type ${arg}`);
  }
  get type() { return this._type; }
  toString() { return `${this._name} (${this.type})`; }
}
// cliente
new Employee(name, "engineer");

// Depois
class Employee {
  constructor(name) { this._name = name; }
  toString() { return `${this._name} (${this.type})`; }
}
class Engineer extends Employee { get type() { return "engineer"; } }
class Salesman extends Employee { get type() { return "salesman"; } }
class Manager extends Employee { get type() { return "manager"; } }

function createEmployee(name, type) {
  switch (type) {
    case "engineer": return new Engineer(name);
    case "salesman": return new Salesman(name);
    case "manager": return new Manager(name);
    default: throw new Error(`Employee cannot be of type ${type}`);
  }
}
// cliente
createEmployee(name, "engineer");
```

- **O que demonstra**: o passo a passo real — autoencapsular o campo, criar uma subclasse por vez sobrescrevendo o getter com o literal, mover a lógica de seleção para uma factory function (nunca para o construtor, para não misturar inicialização de campos com despacho), testar a cada subclasse adicionada, e só então remover o campo/validação antigos e o parâmetro `type` do construtor (via Mudar declaração de função).

## Modelos mentais
- Herança é uma ferramenta que "só pode ser usada uma vez" por eixo de variação — se surgir um segundo eixo, ou parte da subclasse recusa a interface da superclasse, prefira delegação (composição).
- "Prefira composição de objetos à herança de classe" não significa banir herança; significa usar herança quando as condições semânticas se aplicam e trocar por delegação quando (e se) ela virar problema — não precisa acertar de primeira.
- Ao mover recursos em uma hierarquia, o par Subir/Descer (método, campo, corpo de construtor) é o kit básico; Extrair superclasse e Condensar Hierarquia lidam com adicionar/remover níveis inteiros.
- Construtores exigem tratamento especial (ordem de `super()`, regras da linguagem) — por isso Subir corpo do construtor existe como refatoração própria em vez de simplesmente Extrair função + Subir método.

## Anti-padrões
- **Herança recusada (Refused Bequest)**: a subclasse usa só parte da interface/comportamento herdado, ou o herda mas o interpreta de forma que viola a substituição (o subtipo não pode ser usado em todo lugar em que o supertipo é esperado). Sintoma clássico do erro Stack-extends-List ou carro-modelo-vs-carro-físico. Tratar com Descer método, Descer campo (quando o problema é só posicionamento de recursos na hierarquia) ou Substituir subclasse/superclasse por delegação (quando o problema é o próprio uso de herança).

## Pontos-chave (takeaways)
1. Herança serve bem quando toda função da superclasse se aplica à subclasse e toda instância da subclasse é uma instância válida da superclasse; fora disso, é sinal para delegação.
2. As refatorações Subir/Descer método e campo são a base para reorganizar onde os recursos vivem antes de decidir se a estrutura de herança em si precisa mudar.
3. Substituir código de tipos por subclasses tem duas variantes — herança direta (mais simples) e indireta via objeto de tipo extraído (necessária se o tipo for mutável ou já houver outra hierarquia) — a escolha depende se o "tipo" precisa de vida própria além da distinção de comportamento.
4. Migrar de herança para delegação tem custo real (referências de volta, lógica de despacho, encaminhamentos) — vale a pena quando o ganho (mudança dinâmica de categoria, liberar o eixo de herança para outro uso, remover acoplamento indevido) supera essa complexidade extra.
5. Comece simples (herança) e evolua para delegação apenas quando o problema aparecer — não projete a delegação antecipadamente "por via das dúvidas" (evitar generalidade especulativa).

## Conecta com
- **Cap 3**: cheiro Herança recusada (Refused Bequest) → Descer método, Descer campo, Substituir subclasse por delegação, Substituir superclasse por delegação.
- **Cap 3**: cheiros Classe grande e Switches repetidos → Substituir código de tipos por subclasses e Substituir condicional por polimorfismo.
- **Cap 3**: cheiro Elemento ocioso e Generalidade especulativa → Condensar Hierarquia.
- **Cap 6/7**: Mudar declaração de função, Substituir construtor por função de factory e Mover função são pré-requisitos usados repetidamente neste capítulo.
