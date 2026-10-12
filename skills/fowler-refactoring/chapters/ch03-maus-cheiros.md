# Capítulo 3: Maus cheiros no código

## Ideia central
Cheiros de código não são regras exatas nem métricas — são heurísticas que apontam onde a intuição humana deve desconfiar do design e considerar refatorar. O capítulo não diz "quando" refatorar em termos absolutos; ensina a reconhecer sintomas e liga cada um às refatorações-cura correspondentes.

## Frameworks introduzidos
- **Catálogo de maus cheiros**: 24 estruturas recorrentes de código problemático, cada uma com sinais de reconhecimento e uma lista de refatorações que a resolvem. Uso: leia a lista (ou passe os olhos na tabela), identifique o cheiro sentido, aplique as refatorações sugeridas; se o cheiro exato não bater, a lista ainda aponta a direção certa.

## Conceitos-chave
- **Cheiro de código**: sintoma superficial que geralmente indica um problema mais profundo de design, não um defeito em si.
- **Distância semântica**: diferença entre o que uma função faz (a intenção) e como ela faz (a implementação) — quanto maior, mais forte o cheiro de Função Longa/Nome Misterioso.
- **Contexto (bounded context, avant la lettre)**: agrupamento de responsabilidades que mudam pela mesma razão; a mistura de contextos causa Alteração Divergente.
- **Acoplamento por dados compartilhados**: a raiz comum de Inveja de Recursos, Trocas Escusas e Cirurgia com Rifle — dados e comportamento que deveriam morar juntos, mas estão separados.

## Tabela de referência: 24 maus cheiros
| Mau cheiro (PT / EN) | Sinal / como reconhecer | Refatorações que curam |
|---|---|---|
| Nome misterioso (Mysterious Name) | Função, variável, classe ou módulo cujo nome não comunica claramente o que faz | Mudar declaração de função; Renomear variável; Renomear campo |
| Código duplicado (Duplicated Code) | Mesma estrutura de código repetida em mais de um lugar | Extrair função; Deslocar instruções (para alinhar antes de extrair); Subir método (duplicação em subclasses) |
| Função longa (Long Function) | Função extensa, difícil de entender sem ler tudo | Extrair função; Substituir variável temporária por consulta; Introduzir objeto de parâmetros; Preservar objeto inteiro; Substituir função por comando; Decompor condicional; Substituir condicional por polimorfismo; Dividir laço |
| Lista longa de parâmetros (Long Parameter List) | Função com muitos parâmetros, confusa de chamar e entender | Substituir parâmetro por consulta; Preservar objeto inteiro; Introduzir objeto de parâmetros; Remover argumento de flag; Combinar funções em classe |
| Dados globais (Global Data) | Variáveis globais, variáveis de classe ou singletons modificáveis de qualquer ponto do código | Encapsular variável (sempre o primeiro passo); limitar escopo movendo para classe/módulo |
| Dados mutáveis (Mutable Data) | Atualizações de dados que geram efeitos colaterais inesperados e bugs difíceis de rastrear | Encapsular variável; Separar variável; Deslocar instruções + Extrair função; Separar consulta de modificador; Remover método de escrita; Substituir variável derivada por consulta; Combinar funções em classe/transformação; Mudar referência para valor |
| Alteração divergente (Divergent Change) | Um módulo precisa ser alterado de formas diferentes por motivos diferentes | Separar em fases; Mover função; Extrair função (antes de mover); Extrair classe |
| Cirurgia com rifle (Shotgun Surgery) | Uma única alteração exige pequenas modificações espalhadas por várias classes | Mover função; Mover campo; Combinar funções em classe; Combinar funções em transformação; Separar em fases; Internalizar função/classe (reunir antes de reorganizar) |
| Inveja de recursos (Feature Envy) | Função que interage mais com dados/funções de outro módulo do que com o seu próprio | Mover função; Extrair função + Mover função (quando só parte da função inveja) |
| Agrupamentos de dados (Data Clumps) | Os mesmos dados (3-4 itens) aparecem juntos repetidamente como campos ou parâmetros | Extrair classe (campos); Introduzir objeto de parâmetros / Preservar objeto inteiro (parâmetros) |
| Obsessão por primitivos (Primitive Obsession) | Uso de tipos primitivos (int, string) para representar conceitos de domínio (moeda, telefone, intervalo) | Substituir primitivo por objeto; Substituir código de tipos por subclasses + Substituir condicional por polimorfismo; Extrair classe + Introduzir objeto de parâmetros (grupos de primitivos) |
| Switches repetidos (Repeated Switches) | A mesma lógica condicional switch/if-else aparece em múltiplos lugares do código | Substituir condicional por polimorfismo |
| Laços (Loops) | Laços tradicionais (for/while) processando coleções | Substituir laço por pipeline |
| Elemento ocioso (Lazy Element) | Função ou classe que não agrega valor além do que seu nome já diz (estrutura sem propósito real) | Internalizar função; Internalizar classe; Condensar hierarquia |
| Generalidade especulativa (Speculative Generality) | Hooks, casos especiais e abstrações criados para necessidades futuras que nunca chegam | Condensar hierarquia; Internalizar função/classe; Mudar declaração de função (remover parâmetros não usados); Remover código morto (se só testes usam) |
| Campo temporário (Temporary Field) | Campo de uma classe que só é definido/usado em certas circunstâncias | Extrair classe; Mover função; Introduzir caso especial |
| Cadeias de mensagens (Message Chains) | Cliente navega a.getB().getC().getD() — acoplado à estrutura intermediária | Ocultar delegação; Extrair função + Mover função (mover o uso para dentro da cadeia) |
| Intermediário (Middle Man) | Classe cuja maioria dos métodos apenas delega para outra classe | Remover intermediário; Internalizar função; Substituir superclasse/subclasse por delegação |
| Trocas escusas / Insider Trading (Insider Trading) | Módulos que trocam dados/se conhecem demais, acoplamento excessivo, inclusive via herança | Mover função; Mover campo; Ocultar delegação; Substituir subclasse/superclasse por delegação |
| Classe grande (Large Class) | Classe com campos ou métodos demais, tentando fazer muita coisa | Extrair classe; Extrair superclasse; Substituir código de tipos por subclasses |
| Classes alternativas com interfaces diferentes (Alternative Classes with Different Interfaces) | Classes que fazem a mesma coisa mas têm assinaturas/protocolos diferentes, impedindo substituição | Mudar declaração de função; Mover função; Extrair superclasse |
| Classe de dados (Data Class) | Classe só com campos e getters/setters, sem comportamento próprio | Encapsular registro; Remover método de escrita; Mover função; Extrair função (para depois mover) |
| Herança recusada (Refused Bequest) | Subclasse usa só parte do que herda da superclasse, ou rejeita a interface do pai | Descer método; Descer campo; Substituir subclasse/superclasse por delegação (quando recusa a interface) |
| Comentários (Comments) | Comentário usado como "desodorante" para código ruim, explicando o que o código deveria explicar sozinho | Extrair função; Mudar declaração de função (renomear); Introduzir asserção |

## Modelos mentais
- Se você sente que precisa **comentar** um trecho, primeiro tente **extrair uma função** com nome que substitua o comentário — isso normalmente resolve Função Longa e Comentários ao mesmo tempo.
- Se uma alteração de negócio força mudanças em **vários lugares espalhados**, é Cirurgia com Rifle; se força mudanças **por motivos diferentes no mesmo módulo**, é Alteração Divergente — a cura é sempre reagrupar o que muda junto.
- Se você não consegue **dar um bom nome** a algo (função, laço, classe), geralmente há um problema de design mais profundo escondido atrás do Nome Misterioso.
- Dados e comportamento que sempre são usados juntos (Agrupamentos de Dados, Obsessão por Primitivos, Inveja de Recursos) devem ganhar uma classe própria — a regra geral é "colocar junto aquilo que muda junto".

## Anti-padrões
- **Tratar o catálogo como checklist mecânica**: os autores explicitamente rejeitam métricas exatas; cheiros pedem julgamento humano, não contagem de linhas ou parâmetros.
- **Guerra religiosa contra switch/condicionais**: nem todo switch é ruim — o problema é o switch *repetido* em vários lugares, não a condicional isolada.
- **Extrair classes pequenas demais cedo**: ao resolver Cirurgia com Rifle, às vezes vale internalizar tudo primeiro (criando temporariamente uma Classe Grande) para depois extrair de forma mais limpa.
- **Confundir recusar implementação com recusar interface** em Herança Recusada: recusar comportamento é aceitável na maioria das vezes; recusar a interface do pai é o cheiro mais grave e pede Substituir Subclasse/Superclasse por Delegação.

## Pontos-chave (takeaways)
1. Cheiros são heurísticas de "quando refatorar", não regras matemáticas — a intuição bem fundamentada supera métricas exatas.
2. Muitos cheiros compartilham a mesma cura raiz: Extrair Função/Classe e Mover Função resolvem a maioria dos 24 casos.
3. Dados e o comportamento que os manipula devem estar no mesmo lugar; quando não estão, surgem Inveja de Recursos, Trocas Escusas e Classe de Dados.
4. Comentários não são um mau cheiro — são um "desodorante": se o código exigir comentário para ser entendido, refatore o código antes.
5. O objetivo final do capítulo é servir de índice prático: sinta o cheiro, consulte a tabela, aplique a refatoração indicada.

## Conecta com
- **Cap 2**: princípios de refatoração (o "como") que este capítulo complementa com o "quando".
- **Cap 6–12**: catálogo completo das refatorações citadas nesta tabela (Extrair Função, Mover Função, Substituir Condicional por Polimorfismo, etc.).
