# Capítulo 15: Estratégia de Planejamento — O Jogo do Planejamento

## Core Idea
Planeje rápido e barato em horizontes cada vez mais curtos (anos→meses→semanas→dias), de
modo que haja **pouca inércia** para mudar. O **Jogo do Planejamento** é um jogo de dois
jogadores — Negócios e Desenvolvimento — com regras claras de quem decide o quê e quando.

## Frameworks Introduced
- **Jogo do Planejamento (nível de entrega)** — três fases:
  - **Exploração**: Escreva uma história · Estime uma história · Separe a história em partes.
  - **Comprometimento**: Classificação por valor (3 pilhas) · Classificação por risco (3 pilhas) · Definição de velocidade · Escolha do escopo.
  - **Direcionamento**: Iteração · Recuperação · Nova história · Reestimativa.
- **Planejamento de Iteração** — mesma estrutura, mas peças = **cartões de tarefas**,
  jogadores = todos os programadores, escala = 1 iteração:
  - **Exploração**: escreva tarefa · combine/separe tarefas.
  - **Comprometimento**: aceite tarefa · estime tarefa · defina fator de carga · faça o balanceamento.
  - **Direcionamento**: implemente tarefa · registre progresso · recuperação · verifique a história.
- **Tempo Ideal de Programação**: "quanto levaria se eu só fizesse isto, sem interrupções nem reuniões?" — base de toda estimativa.

## Key Concepts
- **Princípios de planejamento**: planeje só o próximo período; aceitação de responsabilidades (sem top-down); quem implementa estima; ignore interdependências (faça as prioridades primeiro); planejar-para-prioridades ≠ planejar-para-implementação.
- **Velocidade do time**: tempo ideal de programação por mês de calendário — calibra o compromisso.
- **Fator de carga de trabalho (load factor)**: razão dias ideais/calendário, tipicamente 2–4; calculado da média das últimas iterações, não chutado.
- **Recuperação**: preserva a data reduzindo escopo quando a velocidade caiu.
- **Diferença inter vs. intra-iteração**: tolera-se mais desvio dentro da iteração (até parar um dia para refatorar) do que no cronograma de comprometimento.

## Mental Models
- O Jogo abstrai o planejamento em **dois jogadores** para tirar emoção desnecessária ("Joe, seu idiota, você prometeu para sexta" → "o Desenvolvimento aprendeu algo; precisa da ajuda dos Negócios").
- "Cartões como peças": histórias e tarefas físicas tornam o plano manipulável e visível.

## Anti-patterns
- **Planejar as 6 versões em detalhe de uma vez**: não traz mais valor que um esboço dos itens futuros.
- **Programador estimar sem se candidatar à tarefa**: gera a "Síndrome da Primeira Terça" (estimar coletivo, depois aceitar → quem aceita não é dono da estimativa).
- **Fator de carga > 7–8 dias ideais por iteração**: sobra pouco tempo para ajudar os outros.

## Worked Example — Fase de Comprometimento
**Classificação por valor** (Negócios, 3 pilhas): (1) sem isso o sistema não funciona; (2)
menos essencial mas valor significativo; (3) seria interessante ter. **Classificação por
risco** (Desenvolvimento, 3 pilhas): (1) estimo com precisão; (2) estimo razoavelmente; (3)
não consigo estimar. **Definição de velocidade**: dev diz quanto Tempo Ideal por mês o time
produz. **Escolha do escopo**: Negócios escolhem os cartões — fixando data e pegando cartões
pela velocidade, ou escolhendo cartões e calculando a data.

## Key Takeaways
1. Três fases, em qualquer nível: **Exploração → Comprometimento → Direcionamento** (cíclicas).
2. Negócios classificam por **valor**; Desenvolvimento por **risco**; juntos escolhem o escopo.
3. Estime em **Tempo Ideal de Programação**; converta via **fator de carga** medido (2–4).
4. Quem implementa, estima — e se candidata à tarefa **antes** de estimá-la.
5. Plano é barato de mudar: reestime e recupere em vez de defender o plano antigo.

## Connects To
- **Ch 14 (Responsabilidades)**: o Jogo é a mecânica da divisão Negócios/Desenvolvimento.
- **Ch 8 (Gerenciamento)**: a velocidade é a métrica básica que o gerente faz acontecer.
- **Ch 26 (XP em Ação)**: contratos de preço fixo/data fixa/escopo variável saem do Jogo.
