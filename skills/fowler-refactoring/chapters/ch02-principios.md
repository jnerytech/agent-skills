# Capítulo 2: Princípios da refatoração

## Ideia central
Refatoração é uma disciplina de passos pequenos e comportamento-preservante que melhora o design interno do código para deixá-lo mais fácil de entender e mais barato de alterar — e sua justificativa é sempre econômica (programar mais rápido), nunca estética ou moral.

## Frameworks introduzidos
- **Refatoração como substantivo vs. verbo (Refactoring: noun vs. verb)**: "Refatoração (substantivo): uma modificação feita na estrutura interna do software para deixá-lo mais fácil de compreender e menos custoso para alterar, sem que seu comportamento observável seja alterado." "Refatorar (verbo): reestruturar um software por meio da aplicação de uma série de refatorações, sem alterar o seu comportamento observável."
  - Quando usar: para distinguir uma refatoração nomeada individual (ex.: Extrair Função) de uma sessão de trabalho que encadeia várias.
  - Como: cada passo individual preserva o comportamento observável; o código nunca fica "quebrado" por muito tempo, permitindo parar a qualquer momento.
- **Dois chapéus (Two Hats)**: metáfora de Kent Beck — dividir o tempo entre "acrescentar funcionalidade" (não altera código existente, progresso medido por testes que passam) e "refatorar" (não acrescenta funcionalidade nem testes, exceto casos esquecidos).
  - Quando usar: o tempo todo durante o desenvolvimento; a troca pode ocorrer várias vezes em minutos.
  - Como: perceber conscientemente qual chapéu está usando antes de cada mudança, para não misturar as duas intenções na mesma edição.
- **Regra dos Três (Rule of Three)**: orientação de Don Roberts — "na primeira vez você simplesmente faz; na segunda vez você torce o nariz mas duplica; na terceira vez você refatora."
  - Quando usar: como heurística para decidir o momento de eliminar duplicação.
  - Como: tolerar a primeira duplicação, mas agir na terceira ocorrência semelhante.
- **Refatoração preparatória (Preparatory Refactoring)**: refatorar *antes* de acrescentar uma funcionalidade, para que a mudança nova se encaixe facilmente.
  - Quando usar: quando percebe, ao tentar implementar algo, que o código existente "quase" serve mas está estruturado de forma inconveniente.
  - Como: aplicar refatorações (ex.: Parametrizar Função) até que a nova função seja trivial de adicionar; analogia do autor: desviar para a rodovia em vez de atravessar a floresta em linha reta.
- **Refatoração para compreensão (Refactoring for Understanding)**: transformar a compreensão que está "na cabeça" em código explícito (citação de Ward Cunningham).
  - Quando usar: sempre que for preciso pensar para entender o que um código faz.
  - Como: renomear variáveis, dividir funções longas; a clareza resultante revela detalhes de design antes invisíveis (Ralph Johnson: "limpar a sujeira da janela para enxergar além").
- **Refatoração para coleta de lixo (Litter-Pickup Refactoring)**: variação da anterior — quando já se entende o código, mas ele está malfeito.
  - Quando usar: ao notar lógica confusa ou duplicação evitável durante outra tarefa.
  - Como: corrigir na hora se for simples; anotar e corrigir depois se exigir mais esforço; princípio do acampamento — "deixe o código um pouco melhor do que encontrou."
- **Yagni (You Aren't Going to Need It)**: design simples/incremental — não adicionar flexibilidade especulativa; resolver apenas as necessidades atuais com excelência, e usar refatoração depois para adaptar a arquitetura.
  - Quando usar: ao tentar prever necessidades futuras de flexibilidade (parâmetros extras, abstrações genéricas).
  - Como: só adicionar um recurso de flexibilidade que complique o código se houver evidência de necessidade comprovada; caso contrário, confiar que uma refatoração futura (ex.: Parametrizar Função) resolverá quando for realmente preciso.
- **Três abordagens para desempenho**: time budgeting (provisão fixa de recursos por componente, para sistemas de tempo real rígido), atenção constante (todo programador otimiza o tempo todo — geralmente contraproducente), e "fatorar bem, depois otimizar com profiler" (a abordagem recomendada pelo autor).
  - Quando usar: a terceira, para a maioria dos sistemas (ex.: sistemas corporativos); a primeira só em contextos de tempo real rígido (ex.: marcapassos).
  - Como: construir bem fatorado sem se preocupar com desempenho; medir com profiler; otimizar apenas os pontos determinantes (hot spots, ~90% do tempo concentrado em pouco código); mudar em passos pequenos, testando a cada passo.

## Conceitos-chave
- **Comportamento observável**: o que deve permanecer idêntico após a refatoração — não a pilha de chamadas ou interfaces internas, mas nada que "o usuário deva se importar."
- **Reestruturação (restructuring)**: termo genérico do autor para qualquer limpeza de código; refatoração é um tipo específico e disciplinado dela.
- **Hipótese da Estamina no Design (Design Stamina Hypothesis)**: investir em bom design interno aumenta a "estamina" do esforço de software, permitindo avançar rápido por mais tempo (não é prova, é hipótese apoiada por experiência).
- **Dono do código (code ownership)**: fronteiras de propriedade (equipe, API publicada) limitam quais refatorações podem ser feitas sem quebrar clientes — força o uso de pontes de compatibilidade (ex.: manter a declaração antiga como wrapper).
- **Código autotestável (self-testing code)**: suíte de testes automatizada e rápida, pré-requisito prático para refatorar com segurança.
- **Integração Contínua / CI (Continuous Integration / Trunk-Based Development)**: integrar com a linha principal ao menos uma vez por dia, reduzindo o custo dos merges semânticos que a refatoração provoca.
- **Mudança em paralelo / expansão-contração (Parallel Change / expand-contract)**: técnica para refatorar bancos de dados — introduzir o novo campo, popular ambos, migrar leituras, só então remover o antigo.
- **Branch por Abstração (Branch by Abstraction)**: introduzir uma interface comum antes de trocar uma biblioteca por outra, permitindo migração gradual sem quebrar o build.

## Modelos mentais
- Use **refatoração preparatória** quando a tarefa nova parecer difícil só porque o código existente está malposicionado — refatorar primeiro é o "desvio" que acelera o trajeto final.
- Use **Yagni** quando estiver tentado a generalizar/parametrizar "para o futuro" sem evidência concreta de necessidade — confie que a refatoração futura será barata o suficiente.
- Use a lente **econômica, não estética** para justificar refatoração a gestores: o critério é "isso nos torna mais rápidos", não "código limpo" como valor moral.
- Use **profiler antes de otimizar**: nunca especule sobre desempenho; meça, encontre o ponto determinante, ajuste, teste, remeça.

## Anti-padrões
- **Reservar semanas de "refatoração pura" no cronograma**: geralmente não é refatoração cuidadosa, mas reestruturação descuidada que quebra a base de código; e reforça a crença errada de que refatoração é "atraso."
- **Justificar refatoração por "código limpo" ou moralismo**: o autor considera isso o modo "mais perigoso" de argumentar — a justificativa correta é sempre econômica (mais rápido para entregar funcionalidades e corrigir bugs).
- **Otimização por atenção constante**: cada programador tentando manter desempenho o tempo todo, com visão local e sem medição — em geral piora a manutenibilidade sem ganho real de velocidade.
- **Branches de funcionalidade longos**: quanto mais tempo um branch isolado vive, mais caro (exponencialmente) fica o merge semântico — inimigo direto da refatoração frequente.
- **Refatorar sistema legado sem testes de uma só vez**: perigoso; a resposta correta é criar "linhas de junção" (seams) aos poucos, como ensina Feathers, aceitando o risco calculado.
- **Definição rígida de "dono único do código"**: gera burocracia circular entre equipes; preferível ownership por equipe, com responsabilidade de monitorar (não bloquear) mudanças.

## Exemplo prático (Worked Example)
**A Regra dos Três aplicada, na prática do "chapéu" de refatoração**: imagine que você escreve uma função para calcular um desconto (1ª vez — "você simplesmente faz"). Semanas depois, precisa de uma variação quase igual para outro tipo de cliente; sente o desconforto da duplicação mas copia e cola mesmo assim, pois o refatorar antecipadamente seria especulação (2ª vez — Yagni em ação: ainda não há evidência suficiente de que vale a pena generalizar). Na 3ª vez que uma necessidade similar aparece, o padrão já está claro: agora você troca para o "chapéu de refatoração" e aplica **Parametrizar Função** para unificar as três variações em uma única função parametrizada, eliminando a duplicação. Note a orquestração dos frameworks do capítulo: (1) a Regra dos Três decide o *quando*; (2) o fato de ser feito antes de escrever a nova funcionalidade que motivou a 3ª ocorrência é **refatoração preparatória** — "consultar o mapa" antes de seguir em linha reta; (3) o motivo de não ter generalizado nas vezes 1 e 2 é **Yagni** — o custo de manter flexibilidade especulativa (parâmetros nunca usados) teria sido maior que o custo de refatorar depois; (4) todo o processo só é seguro porque há **código autotestável** rodando após cada pequeno passo, permitindo reverter rapidamente se algo quebrar.

## Pontos-chave (takeaways)
1. Refatoração é uma técnica de passos pequenos e comportamento-preservante — não um sinônimo genérico de "limpar código."
2. A justificativa de peso é sempre econômica: refatoração existe para tornar o desenvolvimento mais rápido, não para satisfazer estética.
3. A maior parte da refatoração deve ser oportunista (preparatória, para compreensão, para coleta de lixo) embutida no fluxo normal de trabalho, não planejada em blocos dedicados.
4. Yagni e refatoração se reforçam mutuamente: só é seguro adiar decisões de design porque a refatoração garante que dá para corrigir depois.
5. Código autotestável e Integração Contínua são pré-requisitos práticos — sem eles, refatorar em equipe é arriscado e os merges semânticos se tornam caros.
6. Desempenho e refatoração não são inimigos: fatorar bem primeiro e otimizar depois com profiler (focando no ~10% do código que consome 90% do tempo) supera tanto o time budgeting quanto a atenção constante para a maioria dos sistemas.
7. Fronteiras de propriedade de código (APIs publicadas, equipes diferentes) não impedem a refatoração, mas exigem táticas de compatibilidade (wrappers, deprecação gradual).

## Conecta com
- **Cap 1** (Um exemplo de refatoração): fornece a demonstração concreta cujos princípios gerais este capítulo sistematiza.
- **Cap 3** (Guardando um mau cheiro no código): detalha os sinais (code smells) que disparam a decisão "quando refatorar" discutida aqui.
- **Cap 4** (Construindo testes): expande o pré-requisito de "código autotestável" mencionado como base essencial para refatorar com segurança.
