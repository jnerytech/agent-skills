# Capítulo 6: Primeiro conjunto de refatorações

## Ideia central
As refatorações mais fundamentais e mais usadas no dia a dia: extrair/internalizar função e variável, renomear e reorganizar assinaturas de funções, encapsular dados mutáveis, e agrupar funções relacionadas em classes, transformações ou fases sequenciais.

## Catálogo de refatorações (11)

### Extrair função (Extract Function)
- **Motivação**: separar intenção de implementação — se você precisa pensar para saber o que um trecho faz, extraia-o para uma função com nome baseado no "o quê"; funções pequenas e bem nomeadas tornam o código autodocumentado.
- **Procedimento**:
  - Crie uma função nova, nomeada pelo propósito (não pela implementação); se não achar um bom nome, talvez não deva extrair.
  - Se a linguagem aceitar, deixe-a aninhada na função original primeiro (menos variáveis fora de escopo).
  - Copie o código extraído para a nova função.
  - Trate variáveis locais fora do escopo da nova função: passe como parâmetros as que só são lidas; se uma variável recebe novo valor, devolva-a (se houver só uma); com muitas variáveis recebendo valor, considere abortar e usar antes Separar variável ou Substituir variável temporária por consulta.
  - Compile/verifique, substitua o código original por uma chamada à nova função, teste.
  - Procure duplicatas do trecho extraído em outros lugares (Substituir código internalizado por chamada de função).

### Internalizar função (Inline Function)
- **Motivação**: quando o corpo de uma função é tão claro quanto seu nome, o indireto vira ruído; também útil para juntar um grupo de funções mal fatoradas antes de extraí-las de novo, ou para eliminar cadeias excessivas de delegação.
- **Procedimento**:
  - Verifique que não é um método polimórfico (não pode ter sobrescritas em subclasses).
  - Encontre todas as chamadas da função.
  - Substitua cada chamada pelo corpo da função; teste após cada substituição.
  - Remova a definição da função original.

### Extrair variável (Extract Variable)
- **Motivação**: nomear partes de expressões complexas as torna mais fáceis de ler e depurar; se o nome fizer sentido além da função atual, prefira promovê-lo a uma função (ou método de classe) em vez de variável local.
- **Procedimento**:
  - Garanta que a expressão não tem efeitos colaterais.
  - Declare uma variável imutável com uma cópia da expressão.
  - Substitua a expressão original pela variável (repita para cada ocorrência, testando a cada troca).

### Internalizar variável (Inline Variable)
- **Motivação**: inversa de Extrair variável — quando o nome não agrega nada além do que a própria expressão já diz, ou quando a variável atrapalha refatorações vizinhas.
- **Procedimento**:
  - Confirme que o lado direito da atribuição não tem efeitos colaterais; torne a variável imutável e teste (garante atribuição única).
  - Substitua cada referência pela expressão do lado direito, testando a cada troca.
  - Remova a declaração/atribuição original; teste.

### Mudar declaração de função (Change Function Declaration)
- **Motivação**: a assinatura de uma função é a "junção" do sistema — nome e parâmetros corretos comunicam propósito e reduzem acoplamento; nomes ruins devem ser corrigidos assim que se souber um nome melhor.
- **Procedimento (simples)**: altere a declaração; encontre e atualize todas as chamadas; teste. Prefira fazer uma mudança por vez (renomear OU adicionar parâmetro).
- **Procedimento (migração, para casos complicados/API pública/polimorfismo)**:
  - Extraia o corpo para uma nova função (nome temporário se necessário); ajuste parâmetros extras com o procedimento simples; teste.
  - Internalize a função antiga (substituindo chamadas uma a uma); teste a cada uma.
  - Renomeie a nova função para o nome definitivo; teste.
  - Para métodos polimórficos, replique o encaminhamento em cada implementação (ou só na superclasse, se a ligação for lá).

### Encapsular variável (Encapsulate Variable)
- **Motivação**: dados são mais difíceis de mover do que funções (funções permitem encaminhamento transitório); encapsular dados amplamente acessados — sobretudo mutáveis e globais — cria um ponto único para validação, monitoramento e futura reorganização.
- **Procedimento**:
  - Crie funções de leitura/escrita para a variável.
  - Substitua cada referência por uma chamada à função apropriada, testando a cada troca.
  - Restrinja a visibilidade da variável (torne-a privada/local ao módulo); teste.
  - Se não for possível restringir o acesso, renomeie a variável para expor referências esquecidas.
  - Se o valor for um registro, considere também Encapsular registro; para impedir mutação de conteúdo, a leitura pode devolver uma cópia ou um wrapper imutável.

### Renomear variável (Rename Variable)
- **Motivação**: bons nomes são o núcleo de um código claro; quanto mais amplo o escopo de uma variável (campo persistente > parâmetro > variável local), mais cuidado o nome exige.
- **Procedimento**:
  - Se a variável for amplamente usada, encapsule-a primeiro (Encapsular variável).
  - Encontre e altere cada referência (se não puder mudar em um passo só, copie para o novo nome e migre gradualmente, testando a cada mudança); teste.
  - Para constantes, pode-se renomear via cópia (`const novoNome = ...; const nomeAntigo = novoNome;`) sem precisar encapsular.

### Introduzir objeto de parâmetros (Introduce Parameter Object)
- **Motivação**: grupos de dados que sempre aparecem juntos como parâmetros formam um conceito implícito; agrupá-los em uma estrutura torna o relacionamento explícito, encurta listas de parâmetros e — o mais importante — abre caminho para mover comportamento comum para a nova estrutura (elevando-a a uma abstração de domínio).
- **Procedimento**:
  - Crie a estrutura (prefira uma classe, idealmente um objeto de valor), se ainda não existir; teste.
  - Adicione um parâmetro para a nova estrutura via Mudar declaração de função; teste.
  - Adapte cada chamada para passar a instância correta; teste a cada uma.
  - Para cada campo, substitua o uso do parâmetro antigo pelo campo da estrutura e remova o parâmetro antigo; teste.

### Combinar funções em classe (Combine Functions into Class)
- **Motivação**: quando várias funções operam de perto sobre o mesmo conjunto de dados (frequentemente passados repetidamente como argumentos), uma classe explicita esse ambiente compartilhado, elimina argumentos redundantes e serve de unidade coesa para passar adiante no sistema.
- **Procedimento**:
  - Encapsule o registro de dados comuns (Encapsular registro), criando-o antes via Introduzir objeto de parâmetros se ainda não agrupado.
  - Mova cada função que usa o registro comum para dentro da nova classe (Mover função) — argumentos que já são membros da classe somem da lista.
  - Extraia (Extrair função) e mova para a classe qualquer lógica adicional que manipule os mesmos dados.

### Combinar funções em transformação (Combine Functions into Transform)
- **Motivação**: quando dados derivados são calculados repetidamente em vários pontos, uma função de transformação centraliza o cálculo em um único lugar fácil de achar e manter consistente — alternativa a Combinar funções em classe, preferível quando os dados de origem são somente leitura (se forem atualizados depois, a transformação gera inconsistência, pois os derivados ficam "congelados").
- **Procedimento**:
  - Crie a função de transformação que recebe o registro original e devolve os mesmos valores (normalmente via cópia profunda); vale testar que o original não é alterado.
  - Escolha uma lógica derivada, mova seu corpo para a transformação criando um novo campo; ajuste os clientes para usar o novo campo (extraia antes com Extrair função se a lógica for complexa); teste.
  - Repita para as demais lógicas.

### Separar em fases (Split Phase)
- **Motivação**: quando um trecho de código lida com duas responsabilidades diferentes em sequência (ex.: parsing seguido de cálculo, como em um compilador), separá-lo em fases sequenciais permite raciocinar sobre cada uma isoladamente, sem manter os detalhes das duas em mente ao mesmo tempo.
- **Procedimento**:
  - Extraia o código da segunda fase em sua própria função; teste.
  - Introduza uma estrutura de dados intermediária como parâmetro adicional dessa função; teste.
  - Para cada parâmetro da segunda fase: se for produzido pela primeira fase, mova-o para a estrutura intermediária (testando a cada mudança); se um parâmetro não deveria ser usado na 2ª fase, extraia o resultado de cada uso dele para um campo da estrutura e desloque a atribuição para o chamador.
  - Extraia o código da primeira fase em sua própria função, devolvendo a estrutura de dados intermediária.

## Exemplo de código (Extract Function)
```javascript
// antes
function printOwing(invoice) {
  printBanner();
  let outstanding = calculateOutstanding();
  // exibe detalhes
  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${outstanding}`);
}

// depois
function printOwing(invoice) {
  printBanner();
  const outstanding = calculateOutstanding(invoice);
  recordDueDate(invoice);
  printDetails(invoice, outstanding);

  function printDetails(invoice, outstanding) {
    console.log(`name: ${invoice.customer}`);
    console.log(`amount: ${outstanding}`);
  }
}

function calculateOutstanding(invoice) {
  let result = 0;
  for (const o of invoice.orders) { result += o.amount; }
  return result;
}
```
- **O que demonstra**: variáveis somente lidas (`invoice`) viram parâmetros; uma variável que recebe valor dentro do trecho extraído (`outstanding`) é tratada como o retorno da nova função — o passo mais delicado da extração.

## Modelos mentais
- Nomear é o motor da refatoração: extração e renomeação nunca são "só mecânica" — servem para aproximar o código do vocabulário do problema.
- Passos pequenos e reversíveis: extrair, testar, e se não ajudar, internalizar de novo sem culpa — o aprendizado não foi desperdiçado.
- Dados exigem mais cautela que funções, porque não é possível "encaminhar" uma variável movida como se faz com uma função; por isso encapsular vem antes de mover/renomear dados de escopo amplo.
- Agrupar dados relacionados (objeto de parâmetros, classe, transformação, fases) é um investimento: o ganho real aparece quando comportamento passa a migrar para a nova abstração, não apenas quando ela é criada.

## Anti-padrões
- **Deixar nomes ruins "porque já está funcionando"**: o demônio Obfuscatis; todo nome confuso deve ser corrigido assim que um nome melhor for entendido.
- **Autoencapsulamento generalizado** (encapsular até campos internos de uma classe): geralmente é exagero — se a classe é grande a ponto de precisar disso, ela deveria ser dividida.
- **Overloaded Getter Setter** (getter/setter com o mesmo nome, diferenciados por presença de argumento): Fowler evita esse padrão em JavaScript.
- **Extrair função com excesso de variáveis mutadas**: sinal para recuar e simplificar antes (Separar variável / Substituir variável temporária por consulta) em vez de forçar a extração.

## Pontos-chave (takeaways)
1. Extrair/Internalizar função e variável são o par mais usado no dia a dia — a base de tudo o mais no catálogo.
2. Mudar declaração de função tem dois modos: simples (tudo de uma vez) e migração (gradual, via extrair+internalizar) — use o segundo quando há muitas chamadas, polimorfismo ou API pública.
3. Encapsular variável transforma o problema difícil de mover dados no problema fácil de mover funções.
4. Introduzir objeto de parâmetros é o primeiro passo para elevar grupos de dados a abstrações de domínio com comportamento próprio.
5. Combinar funções em classe (dados mutáveis) vs. em transformação (dados imutáveis/somente leitura) vs. Separar em fases (processamento sequencial com preocupações distintas) são três formas complementares de organizar funções relacionadas em um nível acima.

## Conecta com
- **Cap 3**: cheiros Função longa, Nome misterioso, Dados de esquema motivam Extrair função, Mudar declaração de função e Introduzir objeto de parâmetros.
- **Cap 7**: Encapsulamento (Encapsular registro, Encapsular coleção) complementa Encapsular variável e Combinar funções em classe.
