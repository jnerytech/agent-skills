# Capítulo 7: Encapsulamento

## Ideia central
Módulos existem para ocultar segredos (estruturas de dados, conexões entre classes, algoritmos) do resto do sistema; encapsular reduz o quanto cada parte do código precisa saber sobre as outras, tornando mudanças futuras mais baratas.

## Catálogo de refatorações (9)

### Encapsular registro (Encapsulate Record)
- **Motivação**: registros brutos (objetos/hashmaps) misturam dados armazenados e calculados e não escondem a estrutura interna; objetos permitem ocultar o que é armazenado e oferecer métodos de acesso, facilitando renomear campos gradualmente.
- **Procedimento**:
  - Aplique Encapsular variável na variável que guarda o registro, com nomes fáceis de procurar.
  - Substitua o conteúdo por uma classe simples que envolva o registro, com um acessor que devolva o registro bruto.
  - Disponibilize novas funções que devolvam o objeto em vez do registro bruto; teste.
  - Para cada uso, troque a função que devolve o registro bruto pela que devolve o objeto, usando métodos de acesso para os campos.
  - Remova o acesso aos dados brutos e as funções antigas; teste.
  - Se os campos forem, eles próprios, estruturas/coleções, aplique Encapsular registro/Encapsular coleção recursivamente.

### Encapsular coleção (Encapsulate Collection)
- **Motivação**: um getter que devolve a coleção bruta permite que clientes a alterem sem que a classe dona perceba — o campo está encapsulado, mas o conteúdo não.
- **Procedimento**:
  - Aplique Encapsular variável se a coleção ainda não estiver encapsulada.
  - Acrescente métodos de adicionar/remover elemento na classe dona.
  - Se houver setter da coleção inteira, remova-o (Remove Setting Method) ou faça-o copiar a coleção recebida.
  - Localize todas as referências à coleção e troque modificações diretas pelos novos métodos; teste a cada mudança.
  - Faça o getter devolver uma visão protegida (proxy somente leitura ou cópia), nunca a coleção original; teste.

### Substituir primitivo por objeto (Replace Primitive with Object)
- **Motivação**: dados simples (números, strings) tendem a crescer em comportamento (formatação, validação, comparação); criar uma classe cedo dá um lugar natural para esse comportamento evoluir.
- **Procedimento**:
  - Aplique Encapsular variável no dado, se ainda não estiver.
  - Crie uma classe de valor simples que aceite o valor no construtor e exponha um getter.
  - Modifique o setter para instanciar a nova classe e o getter para devolver o resultado do getter dela; teste.
  - Considere Renomear função nos acessores originais e aplicar Mudar referência para valor/Mudar valor para referência conforme o papel do objeto.

### Substituir variável temporária por consulta (Replace Temp with Query)
- **Motivação**: transformar variáveis temporárias em funções facilita extrair partes de uma função grande (sem precisar passar a variável como parâmetro) e evita duplicar a lógica de cálculo em outros lugares.
- **Procedimento**:
  - Confirme que a variável é atribuída uma única lógica de cálculo e não gera valor diferente a cada uso; torne-a `const`/somente leitura se possível; teste.
  - Extraia a atribuição para uma função (nome temporário se houver conflito); garanta ausência de efeitos colaterais (Separar consulta de modificador se necessário); teste.
  - Aplique Internalizar variável para remover a temporária.

### Extrair classe (Extract Class)
- **Motivação**: classes crescem organicamente até acumular responsabilidades demais; um subconjunto de dados/métodos que muda junto ou depende fortemente entre si é sinal de que deveria virar sua própria classe.
- **Procedimento**:
  - Decida como separar as responsabilidades; crie uma classe-filha para a parte extraída (renomeie a classe-pai se o nome não fizer mais sentido).
  - Crie uma instância da classe-filha no construtor da classe-pai, com uma referência entre elas.
  - Use Mover campo em cada campo a mover, testando a cada passo.
  - Use Mover função para mover métodos (dos níveis mais baixos aos mais altos), testando a cada passo.
  - Revise as interfaces das duas classes; decida se expõe a nova classe (considere Mudar referência para valor).

### Internalizar classe (Inline Class)
- **Motivação**: inversa de Extrair classe; usada quando uma classe perdeu a razão de existir (pouca responsabilidade restante) ou quando é mais fácil fundir duas classes antes de reparti-las de outro jeito.
- **Procedimento**:
  - Na classe destino, crie funções de delegação para todos os métodos públicos da classe original.
  - Redirecione todas as referências para os métodos de delegação; teste a cada mudança.
  - Mova todos os campos e funções da classe original para a classe destino até esvaziá-la, testando a cada passo.
  - Apague a classe original.

### Ocultar delegação (Hide Delegate)
- **Motivação**: se o cliente chama um objeto delegado obtido de um servidor, o cliente conhece a estrutura interna do servidor; mudanças no delegado se propagam a todos os clientes. Um método de delegação no servidor isola essa mudança.
- **Procedimento**:
  - Para cada método do objeto delegado usado por clientes, crie um método de delegação equivalente no servidor.
  - Adapte os clientes para chamar o servidor em vez do delegado; teste a cada mudança.
  - Se nenhum cliente mais precisar acessar o delegado diretamente, remova o acessor do servidor para ele; teste.

### Remover intermediário (Remove Middle Man)
- **Motivação**: inversa de Ocultar delegação; ocultar demais transforma o servidor num "intermediário" cheio de métodos de encaminhamento — a cada novo recurso do delegado é preciso adicionar mais um wrapper. Quando isso incomoda, deixe o cliente acessar o delegado diretamente.
- **Procedimento**:
  - Crie um getter para o objeto delegado.
  - Para cada uso de um método de delegação, substitua pela chamada encadeada via esse getter; teste a cada substituição.
  - Quando todas as chamadas a um método de delegação forem substituídas, apague esse método.

### Substituir algoritmo (Substitute Algorithm)
- **Motivação**: às vezes existe um jeito mais claro, simples ou baseado em biblioteca de resolver o mesmo problema; vale trocar o algoritmo inteiro em vez de tentar remendar o antigo.
- **Procedimento**:
  - Organize o código a ser trocado de modo que preencha uma função isolada e completa.
  - Prepare testes que capturem o comportamento atual dessa função.
  - Escreva o algoritmo alternativo; rode verificações estáticas.
  - Compare a saída do algoritmo novo com a do antigo nos testes; se coincidirem, terminou — senão, use o antigo como referência para depurar.

## Exemplo de código
```javascript
// Antes: getter devolve a coleção bruta — cliente pode alterá-la sem controle
class Person {
  constructor(name) { this._name = name; this._courses = []; }
  get courses() { return this._courses; }
  set courses(aList) { this._courses = aList; }
}
// cliente burla o encapsulamento:
aPerson.courses.push(new Course(name, false));

// Depois: métodos dedicados de adicionar/remover + getter devolve cópia
class Person {
  constructor(name) { this._name = name; this._courses = []; }
  addCourse(aCourse) { this._courses.push(aCourse); }
  removeCourse(aCourse, fnIfAbsent = () => { throw new RangeError(); }) {
    const index = this._courses.indexOf(aCourse);
    if (index === -1) fnIfAbsent();
    else this._courses.splice(index, 1);
  }
  get courses() { return this._courses.slice(); } // cópia protege o original
}
// cliente agora usa a API controlada:
aPerson.addCourse(new Course(name, false));
```
- **O que demonstra**: Encapsular coleção — o campo já estava "encapsulado" (acessado via getter/setter), mas isso não bastava porque o getter expunha a referência interna. A correção real exige métodos de mutação explícitos (`addCourse`/`removeCourse`) e um getter que nunca devolve a estrutura mutável original.

## Modelos mentais
- Encapsular != apenas esconder o campo atrás de getter/setter; é preciso garantir que o conteúdo (coleções, registros aninhados) também não escape para modificação descontrolada.
- O nível certo de ocultação muda com o tempo — Ocultar delegação e Remover intermediário são movimentos inversos e reversíveis; "refatoração significa nunca ter de se arrepender", basta corrigir depois.
- Um valor primitivo humilde é candidato natural a virar classe assim que ganhar qualquer comportamento além de exibição — os efeitos colaterais na base de código costumam ser desproporcionalmente grandes.
- Variáveis temporárias atrapalham extração de função porque criam dependência de ordem de cálculo; transformá-las em consultas (métodos) resolve isso e elimina duplicação entre funções semelhantes.

## Anti-padrões
- **Intermediário (Middle Man) excessivo vs delegação oculta**: Ocultar delegação evita que clientes conheçam objetos internos do servidor, mas cada novo uso do delegado exige mais um método de encaminhamento — se isso se acumula, o servidor vira um mero repassador (cheiro Intermediário) e compensa aplicar Remover intermediário para o cliente acessar o delegado diretamente. Não há regra fixa: a escolha depende do quanto a mudança futura no delegado deve ficar isolada versus o custo de manter muitos wrappers finos.

## Pontos-chave (takeaways)
1. Estruturas de registro/coleção simples devem ser encapsuladas em classes assim que o escopo de uso crescer, para não depender de convenção implícita sobre seus campos.
2. Para coleções, a defesa real está no getter: nunca devolver a coleção mutável original, e sim uma cópia ou proxy somente leitura.
3. Primitivos com comportamento latente (formatação, validação, comparação) merecem virar objetos de valor cedo.
4. Variáveis temporárias somente-atribuídas-uma-vez são boas candidatas a virar métodos de consulta, o que ajuda a dividir funções grandes.
5. Extrair/Internalizar classe são movimentos recíprocos usados tanto para separar responsabilidades quanto para reagrupar antes de reparticionar de outro jeito.
6. Ocultar delegação e Remover intermediário formam um par de ajuste fino: o nível ideal de ocultação é situacional e deve ser revisitado conforme o sistema evolui.
7. Substituir algoritmo exige primeiro isolar o código antigo numa função testável, comparando saídas antes de aceitar a troca.

## Conecta com
- **Cap 3**: cheiros Dados globais, Obsessão por primitivos, Intermediário, Classe grande — motivam diretamente Encapsular registro/coleção, Substituir primitivo por objeto, Remover intermediário e Extrair classe, respectivamente.
