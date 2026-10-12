# Capítulo 8: Movendo recursos

## Ideia central
Além de criar, remover e renomear, refatorar é mover elementos — funções, campos, instruções, laços inteiros — para o contexto onde pertencem, à medida que a compreensão do domínio melhora e o design "certo" muda com o tempo.

## Catálogo de refatorações

### Mover função (Move Function)
*anteriormente: Mover método (Move Method)*
- **Motivação**: modularidade = agrupar elementos relacionados; uma função deve morar perto dos elementos que ela mais referencia. Mover é indicado quando a função referencia mais coisas de outro contexto do que do próprio, quando um helper aninhado merece visibilidade própria, ou quando o local de chamada sugere um lar melhor.
- **Procedimento**:
  - Analise os elementos usados pela função no contexto atual; considere movê-los também (comece pela função com menor dependência do grupo).
  - Se for método polimórfico, considere super/subclasses.
  - Copie a função para o contexto final, adaptando-a (params/referência ao contexto original); pode exigir nome novo.
  - Rode análise estática; descubra como referenciar a função final a partir do contexto original.
  - Transforme a função original em delegação; teste.
  - Considere Internalizar função (Inline Function) na função original se o intermediário não agregar valor.

### Mover campo (Move Field)
- **Motivação**: a força de um programa está em suas estruturas de dados; um campo sempre passado junto com outro registro, ou que muda em uníssono com um campo de outra classe, está no lugar errado — mover deixa o relacionamento explícito e evita atualizações duplicadas.
- **Procedimento**:
  - Garanta que o campo original esteja encapsulado (Encapsular variável/registro); teste.
  - Crie campo e métodos de acesso no destino; verificações estáticas.
  - Garanta referência do objeto original para o final (crie campo/método se preciso, mesmo que temporário).
  - Adapte os métodos de acesso para usar o campo final (se compartilhado entre originais, atualize setter em ambos + Introduzir asserção antes de cortar o campo original).
  - Teste; remova o campo original; teste.

### Mover instruções para uma função (Move Statements into Function)
*inversa de: Mover instruções para os pontos de chamada*
- **Motivação**: se o mesmo código sempre acompanha a chamada de uma função, junte-o na própria função — remove duplicação e centraliza mudanças futuras.
- **Procedimento**:
  - Se o código repetido não estiver adjacente à chamada, use Deslocar instruções para aproximá-lo.
  - Se a função só é chamada por um lugar, corte/cole direto e teste (fim).
  - Senão, use Extrair função em um ponto de chamada (nome temporário fácil de buscar) incluindo a chamada da função final + as instruções a mover.
  - Converta as demais chamadas para a nova função, testando a cada conversão.
  - Internalize a função original na nova (Inline Function); renomeie a nova função para o nome original (ou um melhor).

### Mover instruções para os pontos de chamada (Move Statements to Callers)
*inversa de: Mover instruções para uma função*
- **Motivação**: quando um comportamento antes coeso passa a variar em algumas chamadas, a parte variável deve sair da função e ir para cada chamador.
- **Procedimento**:
  - Casos simples (1-2 chamadas): corte a primeira/última linha da função e cole nos pontos de chamada; teste.
  - Senão, aplique Extrair função no que deve permanecer (nome temporário buscável); se for método sobrescrito, extraia em todas as subclasses até o remanescente ficar idêntico, depois remova das subclasses.
  - Internalize a função original (Inline Function).
  - Use Mudar declaração de função para renomear a extraída de volta ao nome original (ou melhor).

### Substituir código internalizado por chamada de função (Replace Inline Code with Function Call)
- **Motivação**: código duplicado que já existe como função nomeada deve virar chamada — melhora legibilidade (o nome explica o propósito) e centraliza manutenção; exceção: quando a semelhança é coincidência e os comportamentos devem poder divergir.
- **Procedimento**:
  - Substitua o código internalizado por uma chamada à função existente.
  - Teste.

### Deslocar instruções (Slide Statements)
*anteriormente: Consolidar fragmentos condicionais duplicados*
- **Motivação**: código relacionado deve ficar junto (ex.: declarar variável perto do primeiro uso); costuma ser passo preparatório para Extrair função, que exige que o código-alvo já esteja contíguo.
- **Procedimento**:
  - Identifique a posição final; verifique interferência no caminho — não pode passar por declaração/uso/modificação de elemento que o fragmento referencia (regra geral: não mova um fragmento sobre outro se ambos referenciam um dado que um deles modifica).
  - Corte o fragmento e cole na posição final.
  - Teste; se falhar, quebre o deslocamento em passos menores.

### Dividir laço (Split Loop)
- **Motivação**: laços que fazem duas tarefas na mesma passagem obrigam a entender ambas sempre que se mexe nele; separar permite entender só o comportamento que muda e simplifica o retorno (valor único vs. estrutura). Refatoração, não otimização — junte de novo depois se medir gargalo real.
- **Procedimento**:
  - Copie o laço.
  - Identifique e elimine os efeitos colaterais duplicados.
  - Teste.
  - Considere Extrair função em cada laço resultante (e possivelmente Substituir laço por pipeline / Substituir algoritmo em seguida).

### Substituir laço por pipeline (Replace Loop with Pipeline)
- **Motivação**: pipelines de coleção (map/filter/reduce) expressam o processamento como uma série de transformações lidas de cima para baixo — mais fácil de entender que um laço imperativo equivalente.
- **Procedimento**:
  - Crie uma nova variável para a coleção do laço (pode ser cópia de uma existente).
  - De cima para baixo, substitua cada porção de comportamento do laço por uma operação de pipeline (slice/filter/map/...) encadeada na variável de coleção; teste após cada mudança.
  - Quando todo comportamento sai do laço, remova-o; se havia atribuição a acumulador, atribua o resultado do pipeline a ele.

### Remover código morto (Remove Dead Code)
- **Motivação**: código não usado não pesa em produção, mas pesa na compreensão — não sinaliza que pode ser ignorado, então continua consumindo tempo de quem lê. Controle de versão elimina a necessidade de comentar/guardar "por via das dúvidas".
- **Procedimento**:
  - Se o código morto for referenciável de fora (ex.: função pública), busque por chamadas restantes.
  - Remova o código morto.
  - Teste.

## Exemplo de código
```javascript
// Antes: laço imperativo filtrando linhas da Índia de um CSV
function acquireData(input) {
  const lines = input.split("\n");
  let firstLine = true;
  const result = [];
  for (const line of lines) {
    if (firstLine) { firstLine = false; continue; }
    if (line.trim() === "") continue;
    const record = line.split(",");
    if (record[1].trim() === "India") {
      result.push({ city: record[0].trim(), phone: record[2].trim() });
    }
  }
  return result;
}

// Depois: pipeline de coleção (slice/filter/map)
function acquireData(input) {
  const lines = input.split("\n");
  return lines
    .slice(1)
    .filter(line => line.trim() !== "")
    .map(line => line.split(","))
    .filter(fields => fields[1].trim() === "India")
    .map(fields => ({ city: fields[0].trim(), phone: fields[2].trim() }));
}
```
- **O que demonstra**: cada responsabilidade do laço (ignorar cabeçalho, descartar linhas em branco, parsear, filtrar por país, remodelar) vira um estágio nomeado do pipeline — fatiamento com `slice`, seleção com `filter`, transformação com `map` — eliminando o acumulador (`result.push`) e as variáveis de controle (`firstLine`). A migração é feita operação por operação, testando a cada passo, exatamente como no procedimento de Substituir laço por pipeline.

## Modelos mentais
- **Mover é aprendizado tardio**: a decisão de onde algo pertence raramente é óbvia de início; é normal deixar algo em um contexto provisório e mover depois, quando o design real se revela.
- **Copiar antes de cortar**: mover com segurança = copiar para o destino, adaptar, validar (estática + testes), só então apagar o original como delegação — nunca um corte-e-cola cego em código não trivial.
- **Efeitos colaterais ditam o que pode deslizar**: um fragmento sem efeitos colaterais pode ser reordenado livremente; um com efeitos colaterais só pode se mover até onde não colidir com dados compartilhados — daí o valor de Separação entre Comandos-Consultas.
- **Pipeline = leitura de cima para baixo do fluxo de dados**: cada estágio (filter/map/reduce) documenta uma transformação, substituindo a necessidade de simular mentalmente o laço.

## Anti-padrões
- **Comentar código morto "para o caso de precisar depois"**: com controle de versão, isso só adiciona ruído; o histórico já preserva o código.
- **Dividir laço apenas por medo de performance**: separar refatoração de otimização — só reunir loops se um profiler comprovar gargalo real.
- **Mover uma função por capricho de organização sem checar dependências**: pular a análise de quem chama/quem é chamado/quais dados são usados leva a acoplamentos ocultos ou quebras sutis.
- **Deslocar instruções sobre código com efeitos colaterais desconhecidos**: assumir "não deve ter efeito colateral" sem verificar (ou sem testes confiáveis) é como apostar no comportamento observável do programa.

## Pontos-chave (takeaways)
1. Mover elementos entre contextos é tão parte da refatoração quanto criar/remover/renomear — reflete o entendimento crescente do domínio.
2. Toda função/campo tem um contexto "certo"; sinais de que está errado: referencia mais o outro contexto, muda em conjunto com dados de outro registro, ou é sempre passado junto com outro dado.
3. O padrão seguro é sempre: copiar para o destino → adaptar → validar (estática/teste) → transformar original em delegação → opcionalmente internalizar.
4. Deslocar instruções tem regras precisas de interferência (declaração, referência, modificação) — e é quase sempre pré-requisito de Extrair função.
5. Dividir laço + Extrair função + Substituir laço por pipeline formam uma sequência natural para simplificar laços que fazem mais de uma coisa.
6. Código morto deve ser apagado, não comentado — o sistema de controle de versão já é a rede de segurança.

## Conecta com
- **Cap 3**: cheiros Inveja de recursos (motiva Mover função/campo), Cirurgia com rifle (Mover instruções para uma função concentra a mudança em um lugar), Laços (motiva Substituir laço por pipeline), Elemento ocioso (motiva Remover código morto e Internalizar função como parte do procedimento de mover).
