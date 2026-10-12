# Capítulo 2: Padrões

## Core Idea
Um padrão é um **padrão de forças**: as mesmas restrições reincidem de modo previsível em decisões técnicas de codificação, então a solução também pode reincidir. Padrões liberam tempo e energia das partes mundanas para os problemas verdadeiramente únicos.

## Frameworks Introduced
- **Padrão de forças**: cada decisão técnica (ex.: como escrever um laço) carrega um conjunto recorrente de forças — fácil de ler, escrever, verificar, modificar, e eficiente.
  - When to use: quando as questões de domínio já estão resolvidas e restam só as puramente técnicas.
  - How: liste as forças → escolha a prioridade entre elas → cada priorização diferente gera uma solução diferente.
- **Padrões trabalham juntos**: um padrão introduz o problema que outro resolve (o laço `for` levanta a questão do nome da variável do laço → outro padrão cobre nomes).

## Key Concepts
- **Forças**: as restrições que afetam como cada instância do código é escrita.
- **Semente de solução**: cada padrão sugere uma solução concreta ("use o `for` de Java5 para iterar").
- **Regras gerais dos programadores** (base dos padrões):
  - Lê-se programas mais do que se escreve.
  - Não existe "terminado" — mais investimento em modificação que em criação.
  - Programas se estruturam em conceitos de estado e fluxo de controle.
  - Leitores precisam entender detalhes E conceito (ora do detalhe ao conceito, ora o inverso).

## Mental Models
- **Analogia da cama arrumada**: um padrão habitual economiza energia; adapta-se à situação (parede, lençol pequeno) sem re-planejar cada etapa. Padrão vira hábito → mente livre para o único.
- Pense em cada padrão como "ponto de vista sobre prioridades relativas das forças" + ensaio das alternativas.

## Anti-patterns
- **Copiar cegamente o estilo de alguém**: menos eficaz que pensar, praticar e discutir o próprio estilo com a equipe.
- **Debater cada laço do zero**: se a equipe está insatisfeita com um padrão, discuta e troque o *padrão*, não cada instância.

## Key Takeaways
1. Padrão = problema comum + discussão das forças + recomendação concreta.
2. O valor está em decidir mais rápido e barato as partes tediosas, liberando criatividade para o único.
3. Revelar o *raciocínio* do padrão convida o leitor a decidir por si — padrão não é regra cega.
4. Quase nada em codificação é inédito; a decisão se repete mesmo que o resultado varie.

## Connects To
- **Ch 3**: valores e princípios que fundamentam e resolvem conflitos entre padrões.
- **Ch 5-9**: o catálogo de padrões propriamente dito.
