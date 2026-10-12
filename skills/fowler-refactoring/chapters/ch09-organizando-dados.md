# Capítulo 9: Organizando dados

## Ideia central
Estruturas de dados são "o segredo para entender o que está acontecendo" em um programa. Este capítulo trata de dar a cada variável/campo uma única responsabilidade clara, dar nomes corretos, eliminar dados derivados redundantes e escolher conscientemente entre semântica de valor (imutável, cópias independentes) e semântica de referência (compartilhada, uma única fonte de verdade).

## Catálogo de refatorações (5)

### Separar variável (Split Variable)
- **Motivação**: uma variável que recebe valor mais de uma vez (fora do padrão acumulador) tem mais de uma responsabilidade e confunde o leitor; cada responsabilidade merece sua própria variável.
- **Procedimento**:
  - Verifique se não é uma variável de laço ou acumuladora (padrão `i = i + algo`); essas não devem ser separadas.
  - Renomeie a variável na declaração e na primeira atribuição; se possível, declare-a como imutável (`const`).
  - Atualize todas as referências até a segunda atribuição.
  - Teste.
  - Repita a cada atribuição subsequente (novo nome + `const`), até a última.

### Renomear campo (Rename Field)
- **Motivação**: nomes de campos em estruturas de registro (e getters/setters equivalentes em classes) são cruciais para a compreensão do programa; a compreensão melhora com o tempo e deve ser refletida no código.
- **Procedimento**:
  - Se o registro tiver escopo limitado, apenas renomeie todos os acessos e teste — pronto.
  - Caso contrário, aplique Encapsular registro (Encapsulate Record) primeiro.
  - Renomeie o campo privado internamente; ajuste os métodos internos; teste.
  - Se o construtor usa o nome antigo, aplique Mudar declaração de função para renomeá-lo (suportando ambos os nomes temporariamente, com precedência para o novo, até migrar todos os chamadores).
  - Aplique Renomear função nos métodos de acesso (getter/setter).

### Substituir variável derivada por consulta (Replace Derived Variable with Query)
- **Motivação**: dados mutáveis são fonte de bugs por acoplamento e efeitos em cascata; se um valor pode ser calculado a partir de outros dados, eliminá-lo como variável reduz o escopo de mutabilidade (exceto quando os dados de origem já são imutáveis ou o derivado é muito transiente — aí ambas as abordagens são aceitáveis).
- **Procedimento**:
  - Identifique todos os pontos de atualização da variável; se houver mais de um, aplique Separar variável antes, para isolar cada ponto.
  - Crie uma função que calcule o valor.
  - Use Introduzir asserção para garantir, em tempo de teste, que a variável e o cálculo coincidem sempre (encapsulando a variável se necessário para ter onde colocar a asserção).
  - Teste; substitua as leituras da variável pela chamada à nova função; teste novamente.
  - Aplique Remover código morto na declaração e nas atualizações da variável original.

### Mudar referência para valor (Change Reference to Value)
- **Motivação**: um objeto aninhado pode ser tratado como referência (atualiza-se a propriedade, mantendo a mesma instância) ou como valor (substitui-se o objeto inteiro por um novo). Valores são objetos de valor (Value Object) imutáveis, mais fáceis de raciocinar, seguros para replicar e passar entre partes do programa — especialmente úteis em sistemas distribuídos/concorrentes. Não usar quando é necessário que alterações no objeto compartilhado sejam vistas por todos os colaboradores.
- **Procedimento**:
  - Verifique que a classe candidata é (ou pode se tornar) imutável.
  - Para cada setter, aplique Remover método de escrita.
  - Forneça um método de igualdade baseado em valor (e o correspondente método de hash), usando os campos do objeto.

### Mudar valor para referência (Change Value to Reference)
- **Motivação**: quando vários registros representam logicamente a mesma entidade (ex.: vários pedidos do mesmo cliente) e essa entidade precisa ser atualizada, manter cópias em valor obriga a atualizar todas as cópias — arriscado e propenso a inconsistência. Convertendo para referência única (via repositório), qualquer atualização fica visível a todos.
- **Procedimento**:
  - Crie um repositório para instâncias do objeto relacionado (se ainda não houver um).
  - Garanta que o construtor tenha como consultar a instância correta no repositório.
  - Modifique os construtores para obter o objeto relacionado através do repositório, em vez de criar uma nova instância; teste após cada mudança.

## Exemplo de código

Separar variável — a variável `acc` tinha duas responsabilidades (aceleração da primeira força e aceleração combinada):

```javascript
// Antes
function distanceTravelled(scenario, time) {
  let result;
  let acc = scenario.primaryForce / scenario.mass;
  let primaryTime = Math.min(time, scenario.delay);
  result = 0.5 * acc * primaryTime * primaryTime;
  let secondaryTime = time - scenario.delay;
  if (secondaryTime > 0) {
    let primaryVelocity = acc * scenario.delay;
    acc = (scenario.primaryForce + scenario.secondaryForce) / scenario.mass;
    result += primaryVelocity * secondaryTime + 0.5 * acc * secondaryTime * secondaryTime;
  }
  return result;
}

// Depois
function distanceTravelled(scenario, time) {
  let result;
  const primaryAcceleration = scenario.primaryForce / scenario.mass;
  let primaryTime = Math.min(time, scenario.delay);
  result = 0.5 * primaryAcceleration * primaryTime * primaryTime;
  let secondaryTime = time - scenario.delay;
  if (secondaryTime > 0) {
    let primaryVelocity = primaryAcceleration * scenario.delay;
    const secondaryAcceleration = (scenario.primaryForce + scenario.secondaryForce) / scenario.mass;
    result += primaryVelocity * secondaryTime + 0.5 * secondaryAcceleration * secondaryTime * secondaryTime;
  }
  return result;
}
```

- **O que demonstra**: `acc` era reaproveitada para dois conceitos distintos. Separando em `primaryAcceleration` (const) e `secondaryAcceleration`, cada nome expressa exatamente um significado, o compilador ajuda a garantir imutabilidade e o código fica autoexplicativo sem precisar rastrear reatribuições.

## Modelos mentais
- **Uma variável, uma responsabilidade**: se uma variável recebe valor mais de uma vez para representar coisas diferentes, ela deveria ser duas variáveis.
- **Valor vs. referência é uma escolha deliberada**: valor = imutável, cópias independentes, fácil de raciocinar; referência = compartilhado, uma fonte de verdade, necessário quando atualizações devem propagar a todos os colaboradores.
- **Dados calculáveis não deveriam ser armazenados**: se um valor pode ser derivado de outros dados, prefira uma consulta (query/getter) a uma variável mutável mantida em sincronia manualmente.
- **Passos pequenos com rede de segurança**: renomear/separar em etapas graduais (com suporte temporário a nome antigo/novo, asserções de equivalência) reduz o risco de erro em estruturas de dados amplamente usadas.

## Anti-padrões
- **Variável reaproveitada para dois propósitos**: como `acc` no exemplo ou `inputValue` usado tanto para entrada quanto para resultado — obriga o leitor a rastrear mentalmente "qual significado essa variável tem agora?", e mudanças em uma responsabilidade acidentalmente afetam a outra.
- **Dado derivado duplicado e mantido manualmente em sincronia** (como `_production` atualizado a cada `applyAdjustment`): cada ponto de atualização é uma chance de esquecer e gerar inconsistência; melhor calcular sob demanda.
- **Objetos de valor com igualdade por referência**: um Value Object que não sobrescreve igualdade/hash não é realmente um valor — comparações e coleções (Map/Set) se comportam de forma incorreta.
- **Cópias de entidade compartilhada com atualização manual**: múltiplos objetos "cliente" representando o mesmo ID, exigindo atualizar todos ao mudar um dado — fonte de inconsistência silenciosa.

## Pontos-chave (takeaways)
1. Separe variáveis no momento em que percebe mais de uma responsabilidade nelas; use `const` para travar cada uso.
2. Renomear campos amplamente usados exige encapsular primeiro, depois migrar getter, setter, construtor e dado interno em passos independentes e testáveis.
3. Prefira consultas (queries) a variáveis derivadas mutáveis; use Introduzir asserção para validar a equivalência antes de eliminar o dado antigo.
4. Escolha valor (imutável, Value Object com igualdade por valor) quando cada colaborador pode ter sua própria cópia; escolha referência (repositório) quando a atualização precisa ser visível a todos que compartilham a entidade.
5. Globais (como um repositório estático) resolvem o problema de referência compartilhada, mas devem ser usados com moderação — considere passá-los como parâmetro se o acoplamento incomodar.

## Conecta com
- **Cap 3**: cheiros Dados mutáveis, Campo temporário — motivam Separar variável e Substituir variável derivada por consulta.
- **Cap 6/7**: Encapsular registro, Encapsular variável, Mudar declaração de função e Renomear função são pré-requisitos usados dentro dos procedimentos deste capítulo.
- **Cap 11**: Remover método de escrita e Remover código morto são aplicados como subpassos de Mudar referência para valor e Substituir variável derivada por consulta.
