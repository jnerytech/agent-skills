# Capítulo 14: Dividindo as Responsabilidades Técnicas e de Negócios

## Core Idea
Mantenha o pessoal técnico focado em problemas técnicos e o pessoal de negócios em problemas
de negócio. O projeto é **dirigido por decisões de negócio**, mas elas precisam ser
**informadas por decisões técnicas** de custo e risco. Nenhum lado decide unilateralmente.

## Frameworks Introduced
- **Divisão de responsabilidade e poder**: cada lado decide o que lhe cabe; cada decisão é
  informada à outra parte.
  - **Negócios decidem**: escopo/tempo das entregas; prioridades relativas das funções; escopo exato de cada função.
  - **Desenvolvimento contribui**: estimativas de tempo; consequências de alternativas técnicas; processo de trabalho; conjunto de práticas a usar e como revisá-las.
- **Tecnologia é decisão de negócio informada pela técnica**: a escolha de banco/linguagem é
  vivida por anos pelo cliente — o papel do dev é apontar consequências e estimar "dos dois jeitos".
- **Analogia constitucional**: como a Constituição dos EUA — uma filosofia básica, um conjunto
  de regras (Bill of Rights) e regras para mudar as regras (emendas).

## Key Concepts
- **Os dois modos de errar**: "Negócios no comando" (define demais, requisitos menos importantes carregam mais risco) e "Desenvolvimento no comando" (adota tecnologia nova/moderna = arriscada por status). Ambos: muito esforço, risco altíssimo, retorno baixo.
- **Custo total da tecnologia**: inclui construir e preservar a competência que a mantém viva, não só o desenvolvimento inicial.
- **Cliente como membro do time**: como decisões de negócio ocorrem o tempo todo, o cliente fica junto e disponível em tempo integral.

## Mental Models
- "Ferrari ou minivan?" → todos escolhem a Ferrari **até** saberem o preço (200k vs. 40k francos) e os requisitos ("levar 5 crianças"). Decisão boa exige conhecer recursos, limitações e custos.
- Programadores são bons em "enxergar os monstros escondidos em cada história" → exponha-os para o negócio decidir.

## Anti-patterns
- **Negócios definindo as quatro variáveis**: sem poder de contraponto técnico, o dev trabalha "de cabeça baixa" na tarefa impossível.
- **Desenvolvimento escolhendo tecnologia por modismo**: modernismo implica risco.
- **Usar a divisão de poder como desculpa para fugir do trabalho duro**: o objetivo é separar o que é genuinamente difícil do que ainda não foi simplificado.

## Worked Example
"Eu não sabia que isso iria sair tão caro. Reduza para um terço do trabalho — vai ser
suficiente por enquanto." Na maioria das vezes, quando os programadores expõem o custo real
de uma história, a pessoa de negócios **espontaneamente** corta ou adia escopo. Quando a
parte mais valiosa **é** genuinamente grande e arriscada, aí não se pisca: reduz-se escopo,
reduz-se risco ao máximo, e "parte-se para a luta" — porque é para isso que se é pago.

## Key Takeaways
1. Negócio dirige; técnica informa custo e risco. Ninguém decide sozinho.
2. Negócios: escopo, prioridade, datas. Desenvolvimento: estimativas, consequências, processo.
3. Escolha de tecnologia é decisão **de negócio** — o dev estima alternativas e aponta consequências.
4. Cliente faz parte do time, em tempo integral.
5. A divisão de poder separa o difícil de verdade do ainda-não-simplificado — não é desculpa para fugir do trabalho.

## Connects To
- **Ch 4 (Quatro Variáveis)**: a divisão impede Negócios de fixar todas as quatro.
- **Ch 15 (Planejamento)**: o Jogo do Planejamento é a mecânica dessa divisão (dois jogadores).
- **Ch 11 (Cliente Presente)** e **Ch 22 (Papéis: Cliente)**: o cliente no time é consequência direta.
