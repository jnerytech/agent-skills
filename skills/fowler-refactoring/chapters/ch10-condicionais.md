
# Capítulo 10: Simplificando lógicas condicionais

## Ideia central
Lógica condicional complexa é uma das maiores fontes de dificuldade de leitura em um programa. As refatorações deste capítulo dão nome e estrutura às condições (decompondo, consolidando, usando cláusulas de guarda, polimorfismo ou casos especiais) e tornam pressupostos implícitos explícitos (asserções).

## Catálogo de refatorações (6)

### 1. Decompor condicional (Decompose Conditional)
- **Motivação**: Uma condicional complexa (a checagem e cada ramo) diz *o que* acontece, mas esconde *por quê*; extrair funções nomeadas pela intenção esclarece ambos.
- **Procedimento**:
  - Aplique Extrair função na expressão da condição, dando um nome que revele a intenção (ex.: `summer()`).
  - Aplique Extrair função em cada ramo (then/else), nomeando pelo que o ramo representa (ex.: `summerCharge()`, `regularCharge()`).
  - Teste após cada extração.
  - Opcionalmente, reescreva o if/else resultante como operador ternário (`charge = summer() ? summerCharge() : regularCharge();`).

### 2. Consolidar expressão condicional (Consolidate Conditional Expression)
- **Motivação**: Uma sequência de checagens condicionais distintas que levam ao mesmo resultado sugere, na verdade, uma única verificação combinada — deixando isso explícito evita a falsa impressão de checagens independentes e prepara o terreno para extrair uma função com nome significativo.
- **Procedimento**:
  - Garanta que nenhuma condicional tenha efeito colateral (senão, aplique antes Separar consulta de modificador).
  - Combine duas condições com um operador lógico: sequências de `if` (mesmo resultado, um atrás do outro) usam `or`; `if`s aninhados usam `and`.
  - Teste.
  - Repita até restar uma única condição consolidada.
  - Considere aplicar Extrair função na condição resultante (ex.: `isNotEligableForDisability()`).
  - Não aplique se as verificações forem conceitualmente independentes e não devam ser lidas como uma única checagem.

### 3. Substituir condicional aninhada por cláusulas de guarda (Replace Nested Conditional with Guard Clauses)
- **Motivação**: Condicionais existem em dois estilos — ambos os ramos são comportamento normal (usa-se if/else, com pesos iguais) ou um ramo é normal e o outro é um caso incomum (usa-se cláusula de guarda: verifica e sai cedo). Aninhar tudo em if/else mascara qual é o caminho essencial; a regra de "um único ponto de saída" não é útil por si só — clareza é o critério.
- **Procedimento**:
  - Selecione a condição mais externa e transforme-a em cláusula de guarda (retorno antecipado).
  - Teste.
  - Repita para as demais condições aninhadas.
  - Se todas as cláusulas de guarda devolverem o mesmo resultado, aplique Consolidar expressão condicional.
  - Ao converter, é comum inverter a condição (de "se X, faça o cálculo normal" para "se não-X, retorne cedo").

### 4. Substituir condicional por polimorfismo (Replace Conditional with Polymorphism)
- **Motivação**: Um `switch`/`if-else` complexo que se repete em várias funções, todos ramificando pelo mesmo código de tipo, esconde estrutura; criar classes por caso (ou uma classe base com variantes em subclasses) usa o polimorfismo para tornar cada comportamento explícito e remove duplicação — mas não é recomendável substituir *toda* condicional por polimorfismo; if/else e switch simples continuam sendo a maioria dos casos legítimos.
- **Procedimento**:
  - Se não houver classes para o comportamento polimórfico, crie-as, com uma função de factory que devolva a instância correta (use Extrair função antes, se a lógica condicional não for autocontida).
  - Substitua as chamadas para usarem a função de factory.
  - Mova a função condicional (com o `switch`) para a superclasse (caso base).
  - Escolha uma subclasse, sobrescreva o método e copie/adapte o ramo correspondente do `switch`.
  - Repita para cada ramo/subclasse.
  - Deixe um caso `default` na superclasse (ou torne-a abstrata/lance erro, se não houver caso base sensato).

### 5. Introduzir caso especial (Introduce Special Case) — antes: Introduzir objeto nulo (Introduce Null Object)
- **Motivação**: Quando muitas partes do código verificam o mesmo valor especial (ex.: `"unknown"`, `null`) e reagem da mesma forma, essa reação duplicada deve ser centralizada em um único elemento (o padrão Caso Especial). Objeto Nulo é apenas o caso mais comum de Caso Especial — a mesma técnica vale para qualquer valor "excepcional" recorrente.
- **Procedimento**:
  - Adicione ao objeto normal uma propriedade de verificação (ex.: `isUnknown`) devolvendo falso.
  - Crie a classe/objeto de caso especial com a mesma propriedade devolvendo verdadeiro.
  - Aplique Extrair função no código de comparação do caso especial; garanta que todos os clientes usem essa função em vez de comparar diretamente.
  - Faça o ponto de origem devolver o objeto de caso especial (via chamada de função ou transformação), e ajuste a função de comparação para usar a nova propriedade.
  - Teste; então use Combinar funções em classe (ou em transformação) para mover todo comportamento comum do caso especial para o novo elemento — substituindo checagens espalhadas por chamadas polimórficas simples.
  - Se restarem clientes com reação diferente do comum, mantenha ali uma checagem explícita (via Internalizar função).
  - Caso o caso especial seja só leitura, um objeto/registro literal (imutável) substitui a classe.

## Exemplo de código (Cláusulas de guarda)
```javascript
// antes: condicionais aninhadas — mascaram qual é o caminho essencial
function payAmount(employee) {
  let result;
  if (employee.isSeparated) {
    result = { amount: 0, reasonCode: "SEP" };
  } else {
    if (employee.isRetired) {
      result = { amount: 0, reasonCode: "RET" };
    } else {
      // lógica normal para calcular o valor
      result = someFinalComputation();
    }
  }
  return result;
}

// depois: cláusulas de guarda (early return) — casos excepcionais saem logo,
// o caminho normal fica no final, sem aninhamento nem variável mutável
function payAmount(employee) {
  if (employee.isSeparated) return { amount: 0, reasonCode: "SEP" };
  if (employee.isRetired) return { amount: 0, reasonCode: "RET" };
  return someFinalComputation();
}
```
- **O que demonstra**: cada condição excepcional (funcionário desligado ou aposentado) vira uma cláusula de guarda com retorno imediato, deixando claro que o cálculo principal só roda quando nenhuma dessas exceções se aplica. A variável mutável `result` desaparece como bônus, e o aninhamento dá lugar a uma sequência plana de checagens.

## Modelos mentais
- Um ramo é caso excepcional e o outro é o caminho normal → cláusula de guarda (retorno cedo); os dois ramos são igualmente válidos/normais → if/else.
- "Único ponto de saída" não é uma regra útil por si só — a clareza é que decide se vale a pena ter vários returns.
- Muitas condicionais repetindo o mesmo `switch` sobre um código de tipo → sinal para extrair classes e usar polimorfismo.
- Muitos lugares testando o mesmo valor especial e reagindo igual → sinal para Introduzir caso especial, centralizando a reação num só lugar.
- Uma asserção comunica um pressuposto ao leitor; deve ser removível sem alterar o comportamento correto do programa.

## Anti-padrões
- **Switch/condicional repetido sobre tipo em várias funções**: sinal de duplicação de lógica de alternância — use Substituir condicional por polimorfismo em vez de manter o mesmo `switch(type)` espalhado.
- **Checagem duplicada do mesmo valor especial em muitos lugares** (ex.: `if (x === "unknown")`): centralize com Introduzir caso especial em vez de repetir a mesma reação por toda a base de código.
- **Uso excessivo de polimorfismo**: nem toda condicional deveria virar hierarquia de classes; if/else e switch simples continuam sendo a forma correta na maioria dos casos.
- **Uso excessivo de asserções**: asserções servem para pressupostos que devem sempre ser verdadeiros (erro do programador), não para validar dados de fontes externas nem para checar "tudo que parece verdade".

## Pontos-chave (takeaways)
1. Decompor condicional separa "o quê" (a ramificação) do "por quê" (a intenção), dando nome à condição e a cada ramo.
2. Consolidar expressão condicional deixa explícito que várias checagens são, na prática, uma única verificação — e prepara para extrair uma função nomeada.
3. Cláusulas de guarda comunicam que um ramo é excepcional, não uma alternativa de mesmo peso que o caminho normal.
4. Polimorfismo é uma ferramenta poderosa para lógica condicional repetida por tipo, mas não deve substituir toda condicional.
5. Introduzir caso especial elimina a duplicação de reações a um valor excepcional (como `null` ou `"unknown"`) centralizando-a num objeto/classe dedicado.
6. Asserções são, acima de tudo, comunicação sobre o estado esperado do programa — não apenas uma ferramenta de depuração.

## Conecta com
- **Cap 3**: cheiros Switches repetidos, Condicional complexa.
