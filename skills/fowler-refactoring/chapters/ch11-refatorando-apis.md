# Capítulo 11: Refatorando APIs

## Ideia central
Módulos e funções se conectam por meio de APIs; uma boa API separa claramente o que atualiza dados (comando) do que apenas os lê (consulta), mantém listas de parâmetros pequenas e sem flags disfarçadas, e prefere objetos imutáveis sempre que possível.

## Catálogo de refatorações (10)

### 1. Separar consulta de modificador (Separate Query from Modifier)
- **Motivação**: uma função que devolve valor não deveria ter efeitos colaterais observáveis (command-query separation); isso permite chamá-la livremente, movê-la e testá-la com facilidade.
- **Procedimento**:
  - Copie a função e nomeie-a como consulta, com base no que ela devolve.
  - Remova qualquer efeito colateral da nova função de consulta; verificações estáticas.
  - Em cada chamada que use o retorno, substitua pela consulta seguida da chamada ao método original.
  - Remova os valores de retorno do método original (modificador). Teste após cada mudança.
  - Se sobrar duplicação, use Substituir algoritmo para o modificador reusar a consulta.

### 2. Parametrizar função (Parameterize Function)
- **Motivação**: funções quase idênticas, diferindo só em valores literais, podem virar uma única função parametrizada, mais reutilizável.
- **Procedimento**:
  - Selecione um dos métodos similares.
  - Use Mudar declaração de função para acrescentar os literais como parâmetros; ajuste cada chamador para passar o literal.
  - Modifique o corpo para usar os novos parâmetros, testando a cada passo.
  - Substitua as chamadas às funções similares pela função parametrizada, adaptando-a se necessário.

### 3. Remover argumento de flag (Remove Flag Argument)
- **Motivação**: um argumento de flag (booleano, enum ou string literal) que só direciona qual lógica interna executar obscurece a API — quem lê a chamada não sabe o que o valor significa; funções explícitas são mais claras.
- **Procedimento**:
  - Crie uma função explícita para cada valor do parâmetro (via Decompor condicional se houver uma condicional clara no topo, senão crie encapsuladores).
  - Para cada chamada com valor literal, substitua pela função explícita correspondente.
  - Se algumas chamadas usarem dado real (não literal) para a flag, mantenha essas com a função original.

### 4. Preservar objeto inteiro (Preserve Whole Object)
- **Motivação**: extrair vários valores de um registro só para passá-los como parâmetros é "inveja de recursos" (Cap. 3); passar o objeto inteiro reduz a lista de parâmetros e absorve mudanças futuras sem alterar a assinatura.
- **Procedimento**:
  - Crie uma função vazia com o parâmetro-objeto desejado, com nome fácil de pesquisar (ex.: prefixo `xxNEW`).
  - Preencha o corpo delegando para a função antiga, mapeando o novo parâmetro para os antigos.
  - Adapte cada chamador para usar a nova função, testando a cada mudança; remova código morto resultante.
  - Internalize a função original na nova e renomeie removendo o prefixo.

### 5. Substituir parâmetro por consulta (Replace Parameter with Query)
- **Motivação**: se quem chama passa um valor que a própria função pode determinar facilmente (ex.: derivado de outro parâmetro), isso é duplicação desnecessária que complica o chamador.
- **Procedimento**:
  - Se necessário, extraia a lógica de cálculo do parâmetro em sua própria função (Extrair função).
  - Substitua as referências ao parâmetro, no corpo, por chamadas à expressão/consulta equivalente. Teste a cada mudança.
  - Use Mudar declaração de função para remover o parâmetro.
  - Evite quando isso introduzir dependência indesejada ou quebrar transparência referencial (ex.: acesso a variável global mutável).

### 6. Substituir consulta por parâmetro (Replace Query with Parameter)
- **Motivação**: inversa da anterior — quando o corpo de uma função acessa algo indesejado no seu escopo (variável global, elemento a mover), transformar isso em parâmetro transfere a responsabilidade para o chamador e ganha transparência referencial.
- **Procedimento**:
  - Extraia a variável do código da consulta (Extrair variável) para isolá-la do resto do corpo.
  - Extraia o restante do corpo em nova função (nome fácil de pesquisar).
  - Internalize a variável extraída; depois internalize a função original na nova.
  - Renomeie a nova função com o nome original.
  - Há tensão: parametrizar demais gera listas longas e repetitivas; não parametrizar aumenta acoplamento por escopo compartilhado.

### 7. Remover método de escrita/setter (Remove Setting Method)
- **Motivação**: se um campo não deve mudar após a criação do objeto, oferecer um setter sugere o contrário; removê-lo e tornar o campo imutável deixa a intenção explícita.
- **Procedimento**:
  - Se o valor não for passado ao construtor, use Mudar declaração de função para acrescentá-lo lá; chame o setter dentro do construtor.
  - Remova cada chamada externa ao setter, usando o valor via construtor. Teste a cada mudança (aborte se o objeto for referência compartilhada e não puder ser recriado).
  - Internalize o setter (Internalizar função); torne o campo imutável quando possível.

### 8. Substituir construtor por função de factory (Replace Constructor with Factory Function)
- **Motivação**: construtores (ex.: em Java) têm limitações — devem devolver instância da própria classe, nome fixo, exigem operador especial (`new`); uma função de factory não tem essas amarras e pode decidir o que devolver.
- **Procedimento**:
  - Crie a função de factory, cujo corpo apenas chama o construtor.
  - Substitua cada chamada ao construtor pela chamada à factory, testando a cada mudança.
  - Restrinja ao máximo a visibilidade do construtor.
  - Pode-se criar factories nomeadas por caso de uso (ex.: `createEngineer`) para evitar passar códigos-tipo como string literal.

### 9. Substituir função por comando (Replace Function with Command)
- **Motivação**: encapsular uma função complexa em um "objeto de comando" dá mais flexibilidade (undo, construção de parâmetros em etapas, hooks) e facilita dividir uma função grande em métodos menores que compartilham estado via campos — mas tem custo de complexidade; prefira função simples na maioria das vezes (~95%).
- **Procedimento**:
  - Crie classe vazia nomeada a partir da função; use Mover função para movê-la para dentro, mantendo a função original como encaminhamento.
  - Nomeie o método de execução seguindo convenção da linguagem (ex.: `execute`).
  - Considere transformar cada argumento em campo, movendo-os para o construtor.
  - Depois, mova variáveis locais para campos, uma a uma, permitindo então Extrair função no corpo sem lidar com escopo.

### 10. Substituir comando por função (Replace Command with Function)
- **Motivação**: inversa da anterior — quando o processamento não é complexo o bastante para justificar o objeto de comando, seu custo supera o benefício; volte a uma função simples.
- **Procedimento**:
  - Extraia a criação do comando e a chamada ao método de execução em uma nova função (que substituirá o comando).
  - Internalize cada método auxiliar chamado pelo método de execução (Extrair variável antes, se houver retorno, depois Internalizar função).
  - Use Mudar declaração de função para levar os parâmetros do construtor para o método de execução; troque referências de campos por parâmetros, testando a cada passo.
  - Internalize a chamada do construtor e do método de execução no ponto de chamada; remova código morto da classe de comando.

## Exemplo de código
**Separar consulta de modificador** — antes:
```javascript
function alertForMiscreant (people) {
  for (const p of people) {
    if (p === "Don") { setOffAlarms(); return "Don"; }
    if (p === "John") { setOffAlarms(); return "John"; }
  }
  return "";
}
```
Depois (consulta pura + modificador que a reusa):
```javascript
function findMiscreant (people) {
  for (const p of people) {
    if (p === "Don") return "Don";
    if (p === "John") return "John";
  }
  return "";
}

function alertForMiscreant (people) {
  if (findMiscreant(people) !== "") setOffAlarms();
}
```

**Remover argumento de flag** — antes:
```javascript
aShipment.deliveryDate = deliveryDate(anOrder, true);   // rush
aShipment.deliveryDate = deliveryDate(anOrder, false);  // regular
```
Depois:
```javascript
aShipment.deliveryDate = rushDeliveryDate(anOrder);
aShipment.deliveryDate = regularDeliveryDate(anOrder);
```

- **O que demonstra**: em ambos os casos, a API fica autoexplicativa — `findMiscreant`/`alertForMiscreant` separam leitura de efeito colateral; `rushDeliveryDate`/`regularDeliveryDate` eliminam a necessidade de decifrar o que `true`/`false` significam na chamada.

## Modelos mentais
- **Command-Query Separation**: uma função devolve valor OU causa efeito colateral observável, nunca as duas coisas — simplifica raciocínio, teste e reuso.
- **Transparência referencial**: uma função referencialmente transparente sempre devolve o mesmo resultado para os mesmos parâmetros; mover dependências do corpo para parâmetros (ou vice-versa) é a alavanca central de várias refatorações deste capítulo.
- **Flags escondem intenção**: literais booleanos/enum/string em uma chamada obrigam quem lê a "decifrar" o comportamento; nomes de função explícitos comunicam a intenção diretamente.
- **Alocação de responsabilidade**: toda decisão de parâmetro é uma escolha entre facilitar a vida de quem chama (função resolve internamente) ou reduzir acoplamento (chamador resolve e passa) — não há resposta universal, apenas trade-off consciente.

## Anti-padrões
- **Argumento de flag booleano**: obscurece a chamada porque `true`/`false` não comunica significado por si só; também esconde do leitor e das ferramentas de análise que duas lógicas distintas estão sendo escolhidas.
- **Inveja de recursos via parâmetros desempacotados**: passar múltiplos campos derivados de um mesmo objeto em vez do objeto inteiro duplica lógica de extração e amplia a lista de parâmetros desnecessariamente.
- **Setter chamado só uma vez no construtor ou só durante um script de criação**: sinaliza campo que deveria ser imutável; manter o setter é uma promessa de mutabilidade que não se pretende cumprir.
- **Comando para tudo**: usar objeto de comando quando uma função simples bastaria adiciona complexidade sem necessidade — reserve comandos para casos com ciclo de vida rico, hooks ou linguagens sem funções de primeira classe.

## Pontos-chave (takeaways)
1. Separe sempre que possível o que lê do que modifica — funções puras são mais fáceis de testar, mover e reutilizar.
2. Elimine argumentos de flag substituindo-os por funções explícitas nomeadas pela intenção.
3. Prefira passar o objeto inteiro a desempacotar vários campos como parâmetros separados.
4. A escolha entre parâmetro e consulta interna é sempre uma troca de responsabilidade entre função e chamador — decida com base em acoplamento e transparência referencial desejados.
5. Remova setters para tornar objetos imutáveis sempre que a mutação pós-construção não fizer sentido.
6. Construtores têm limitações rígidas (nome fixo, tipo de retorno, operador especial); funções de factory são mais flexíveis.
7. Objetos de comando valem o custo extra apenas quando a complexidade da função (ou a necessidade de undo/hooks/construção em etapas) justifica — do contrário, volte a uma função simples.

## Conecta com
- **Cap 3**: cheiros Lista longa de parâmetros, Inveja de recursos, Trocas escusas (dados desempacotados/flags são sintomas tratados aqui).
- **Refatorações citadas neste capítulo**: Extrair função, Extrair variável, Internalizar função, Internalizar variável, Mudar declaração de função, Mover função, Decompor condicional, Substituir algoritmo, Substituir variável temporária por consulta, Introduzir objeto de parâmetros, Extrair classe, Remover código morto (todas do catálogo principal, aplicadas como passos dos procedimentos deste capítulo).
