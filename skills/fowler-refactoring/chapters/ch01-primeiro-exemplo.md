# Capítulo 1: Refatoração — um primeiro exemplo

## Ideia central
Refatorar é o processo de melhorar a estrutura de um código já funcionando, em uma sequência de passos minúsculos, cada um verificado por testes — o que torna o processo mais rápido e seguro do que parece à primeira vista.

## Frameworks introduzidos
- **Extrair função (Extract Function)**: transformar um trecho de código em sua própria função, nomeada pelo que faz.
  - Quando usar: um comentário ou bloco identificável dentro de uma função longa merece um nome próprio.
  - Como: identifique variáveis fora do escopo após a extração; passe as não-modificadas como parâmetros; para a(s) modificada(s), inicialize-a(s) dentro da nova função e devolva o valor (ou use uma variável "sombra" se houver acumulação em laço).
- **Substituir variável temporária por consulta (Replace Temp with Query)**: eliminar uma variável local extraindo o cálculo do lado direito para uma função e depois internalizando a variável.
  - Quando usar: variáveis temporárias acumulam escopo local e dificultam extrações futuras.
  - Como: Extrair função → Internalizar variável → (se necessário) Mudar declaração de função para remover parâmetros redundantes.
- **Dividir laço (Split Loop) + Deslocar instruções (Slide Statements)**: separar um laço que faz duas coisas em dois laços, e mover a inicialização da variável para perto do laço que a usa.
  - Quando usar: preparação para extrair um acumulador (ex.: total) como função própria.
- **Separar em fases (Split Phase)**: dividir uma função em duas — uma que calcula os dados e outra que os renderiza — conectadas por uma estrutura de dados intermediária.
  - Quando usar: a mesma lógica de cálculo precisa alimentar múltiplas exibições (ex.: texto e HTML) sem duplicação.
  - Como: Extrair função para isolar a fase 2 (render); introduzir objeto de dados intermediário; mover cada dado de entrada da fase 1 para dentro do objeto até a fase 2 depender só dele; por fim extrair a fase 1 inteira.
- **Substituir código de tipos por subclasses (Replace Type Code with Subclasses) + Substituir condicional por polimorfismo (Replace Conditional with Polymorphism)**: trocar um `switch`/`if` sobre um "tipo" por uma hierarquia de classes, cada uma implementando seu próprio comportamento.
  - Quando usar: uma condicional baseada em tipo se repete em várias funções e tende a crescer com novas categorias.
  - Como: crie uma classe base + factory function (`createXCalculator`) que devolve a subclasse certa (construtores JS não retornam subclasses, daí a factory); mova cada `case` para o método correspondente na subclasse, um de cada vez, mantendo o `default` como "lápide" temporária até remover a condicional da base.
- **Mover função (Move Function)**: mover lógica para uma nova classe/módulo em dois passos — copiar e adaptar (ex.: `aPerformance` → `this.performance`) no destino, depois transformar a origem em delegação, e por fim internalizar a chamada.

## Conceitos-chave
- **Compilar-testar-fazer commit**: o ciclo repetido após cada micro-passo de refatoração; é o que torna passos pequenos seguros e reversíveis.
- **Nomear default para parâmetros**: em JS dinamicamente tipado, usar `aPerformance`, `aPlay` (artigo indefinido + tipo) para comunicar o tipo esperado.
- **Estrutura de dados intermediária**: objeto produzido pela fase de cálculo e consumido pela fase de renderização; permite múltiplas visualizações sem duplicar lógica.
- **Calculadora polimórfica (Performance Calculator)**: classe cujo papel é encapsular os cálculos que variam por tipo, expostos via getters.
- **Regra do acampamento (boy scout rule)**: sempre deixe a base de código mais saudável do que a encontrou.
- **Imutabilidade defensiva**: copiar objetos (`Object.assign({}, x)`) em vez de mutar dados recebidos como parâmetro.
- **Lápide (tombstone)**: lançar erro explícito temporário (`throw new Error('subclass responsibility')`) para marcar um caso que ainda será removido, servindo de rede de segurança durante a transição.

## Modelos mentais
- Pense na refatoração como **transferir um insight da sua mente de volta para o código**: ao entender o que um trecho faz, nomeie-o e extraia-o — assim o código passa a comunicar isso sozinho da próxima vez.
- **Passos pequenos são mais rápidos, não mais lentos**: um passo minúsculo que quebra é fácil de depurar (uma única mudança suspeita); passos grandes que quebram geram depuração cara. Combine muitos passos pequenos para obter mudanças substanciais.
- **Desempenho quase sempre é secundário à refatoração**: na dúvida, refatore primeiro e ajuste desempenho depois — código bem fatorado é mais fácil de otimizar.
- **O verdadeiro teste de bom código é a facilidade de alterá-lo** — não estética abstrata.

## Anti-padrões
- **Copiar-colar para variar comportamento** (ex.: duplicar `statement` em `htmlStatement`): qualquer mudança futura na lógica exige atualizar todas as cópias de forma consistente — fonte constante de bugs.
- **Refatorar sem uma suíte de testes automaticamente conferida**: sem "detector de bugs", cada passo vira verificação manual lenta e propensa a erro.
- **Passos grandes demais**: ao tentar fazer "muita coisa de uma vez", um erro força uma sessão de depuração complexa; a correção é sempre recuar para passos menores.
- **Deixar variáveis temporárias e código condicional por tipo crescerem sem estrutura**: viável em programa pequeno, mas em escala (centenas de linhas) torna difícil saber o que e onde alterar.

## Exemplos de código
```javascript
// Antes: switch inline dentro do laço principal
function amountFor(perf, play) {
  let thisAmount = 0;
  switch (play.type) {
    case "tragedy":
      thisAmount = 40000;
      if (perf.audience > 30) thisAmount += 1000 * (perf.audience - 30);
      break;
    case "comedy":
      thisAmount = 30000;
      if (perf.audience > 20) thisAmount += 10000 + 500 * (perf.audience - 20);
      thisAmount += 300 * perf.audience;
      break;
    default:
      throw new Error(`unknown type: ${play.type}`);
  }
  return thisAmount;
}

// Depois: polimorfismo via calculadora de apresentação
class PerformanceCalculator {
  constructor(aPerformance, aPlay) { this.performance = aPerformance; this.play = aPlay; }
  get amount() { throw new Error('subclass responsibility'); }
  get volumeCredits() { return Math.max(this.performance.audience - 30, 0); }
}
class TragedyCalculator extends PerformanceCalculator {
  get amount() {
    let result = 40000;
    if (this.performance.audience > 30) result += 1000 * (this.performance.audience - 30);
    return result;
  }
}
class ComedyCalculator extends PerformanceCalculator {
  get amount() {
    let result = 30000;
    if (this.performance.audience > 20) result += 10000 + 500 * (this.performance.audience - 20);
    result += 300 * this.performance.audience;
    return result;
  }
  get volumeCredits() { return super.volumeCredits + Math.floor(this.performance.audience / 5); }
}
function createPerformanceCalculator(aPerformance, aPlay) {
  switch (aPlay.type) {
    case "tragedy": return new TragedyCalculator(aPerformance, aPlay);
    case "comedy": return new ComedyCalculator(aPerformance, aPlay);
    default: throw new Error(`unknown type: ${aPlay.type}`);
  }
}
```
- **O que demonstra**: como uma condicional por tipo, repetida em várias funções (`amountFor`, `volumeCreditsFor`), converge para uma única fábrica polimórfica — cada subclasse só implementa sua própria variação.

## Exemplo prático (Worked Example)
Ponto de partida: função `statement(invoice, plays)` gera texto de cobrança para uma companhia de teatro, misturando em um só bloco: cálculo de valor por peça (switch tragédia/comédia), acúmulo de créditos por volume e montagem da string de saída.

Passos de refatoração (cada um seguido de compilar-testar-commit):
1. **Extrair função** do `switch` → `amountFor(perf, play)`; renomear variáveis internas para `result`/`aPerformance` (convenção do autor).
2. **Replace Temp with Query** para eliminar `play`: extrai `playFor(perf)`, internaliza a variável, depois usa Mudar declaração de função para remover o parâmetro `play` de `amountFor` (que passa a chamar `playFor` internamente).
3. Extrai `volumeCreditsFor(perf)` do mesmo jeito, usando uma variável "sombra" para o acumulador dentro da função extraída.
4. Elimina a variável `format` transformando-a em função declarada `usd(aNumber)`, renomeada de forma mais clara (Change Function Declaration), movendo a divisão por 100 para dentro dela.
5. Para os totais (`volumeCredits`, `totalAmount`): **Split Loop** → **Slide Statements** → **Extract Function** → **Inline Variable** — quatro passos pequenos que eliminam cada acumulador substituindo-o por uma função de consulta (`totalVolumeCredits()`, `totalAmount()`).
   Resultado intermediário: `statement` cai para ~7 linhas, com todas as funções de cálculo aninhadas dentro dela.
6. **Split Phase**: extrai todo o corpo de `statement` (com as funções aninhadas) para `renderPlainText`, criando um objeto `statementData` que vai carregando `customer`, `performances` (via `enrichPerformance`, que enriquece cada apresentação com `play`, `amount`, `volumeCredits` via **Move Function**), `totalAmount` e `totalVolumeCredits`. A fase de cálculo (`createStatementData`) vai para seu próprio arquivo/módulo.
   Resultado: agora é trivial escrever `htmlStatement`/`renderHtml` reaproveitando `createStatementData` sem duplicar nenhum cálculo.
7. **Polimorfismo**: dentro de `createStatementData`, introduz `PerformanceCalculator` (Move Function traz `amountFor`/`volumeCreditsFor` para dentro da classe como getters `amount`/`volumeCredits`); aplica **Replace Type Code with Subclasses** (via factory `createPerformanceCalculator`, pois construtores JS não retornam subclasses) e depois **Replace Conditional with Polymorphism**, passando cada `case` do switch para a subclasse correspondente (`TragedyCalculator`, `ComedyCalculator`), deixando na base apenas o comportamento default e um "lançamento-lápide" temporário até a condicional sumir por completo.

Ao final, o código tem mais linhas que o original (por causa do encapsulamento), mas cada peça é pequena, nomeada e testável isoladamente — pronta para novas categorias de peça sem duplicação nem edição de condicionais espalhadas.

## Pontos-chave (takeaways)
1. Sempre tenha testes automaticamente conferidos antes de começar a refatorar — eles são o "detector de bugs".
2. Refatore em passos minúsculos, compilando/testando/commitando a cada um; se algo falhar, reduza ainda mais o tamanho do passo.
3. Extrair função + nomear bem é a ferramenta mais básica para transformar entendimento tácito em estrutura explícita no código.
4. Eliminar variáveis temporárias (Replace Temp with Query) facilita extrações subsequentes, pois reduz o escopo local a gerenciar.
5. Use Split Phase quando a mesma lógica de cálculo precisa alimentar múltiplas formas de saída.
6. Prefira polimorfismo a condicionais por tipo quando várias funções dependem do mesmo "tipo" e esse conjunto de tipos tende a crescer.
7. Ignore desempenho durante a refatoração na maioria dos casos; ajuste depois, sobre uma base já bem fatorada.

## Conecta com
- **Cap 2 (Princípios da refatoração)**: este capítulo mostrou o "como" através de um exemplo; o próximo formaliza definições, motivações e quando (não) refatorar.
- **Cap 4 (Escrevendo testes)**: aprofunda a prática de testes automaticamente conferidos, pré-requisito citado aqui como "primeiro passo" de qualquer refatoração.
- **Catálogo de refatorações**: Extract Function, Replace Temp with Query, Split Phase, Replace Conditional with Polymorphism e as demais citadas aqui têm entradas formais de referência (mecânica passo a passo) no catálogo do livro.
