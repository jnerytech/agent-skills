# Capítulo 18: Estratégia de Testes

## Core Idea
Escreva os testes **antes** de codificar, minuto a minuto; preserve-os para sempre e execute
todos juntos com frequência. Testes são **instrumentação** da confiança — não o trabalho de
quem ama testar, mas de quem ama fazer o programa funcionar. Teste só o que **pode falhar**.

## Frameworks Introduced
- **Testes isolados e automáticos**: nenhum teste interage com outro (evita falsas negativas
  em cascata); rodam sem intervenção humana, dando indicador "polegar para cima/baixo".
- **Testar é apostar**: você ganha quando um teste contraria sua expectativa (passa quando
  você achou que falharia → o código é mais esperto que você; falha quando achou que passaria
  → aprendeu algo). Escreva os testes que **podem** valer a pena; refine com a experiência.
- **Dois testes, duas fontes**:
  - **Testes de unidade** (programador): executam sempre a **100%**; se um falha, nada é mais
    importante que consertá-lo. Escritos método a método.
  - **Testes funcionais** (cliente): medidos em **porcentagem**; sobem rumo a ~100% com o tempo;
    perto da entrega, o cliente categoriza os que falham por importância.
- **Quando o programador escreve um teste**: interface pouco clara; implementação complicada;
  circunstância inusitada; bug descoberto (isole-o); antes de refatorar sem teste do comportamento.

## Key Concepts
- **"Infectado por testes"** (Gamma): não escrever código sem um teste.
- **Nível de erros tolerável**: invista em testes até atingir a taxa de defeitos que você suporta.
- **Testador dedicado**: todo time XP de qualquer tamanho tem ao menos um; traduz ideias vagas do cliente em testes reais, automatizados e isolados — e cria variações que fazem o software falhar.
- **Outros testes** (eventuais): **paralelo** (novo vs. antigo), **de estresse** (pior carga), **do macaco** (entradas sem sentido).

## Mental Models
- Toda vez que você imagina que um código vai funcionar, transforme essa confiança num **artefato** dentro do programa — disponível para todos.
- "Faça-o executar, faça-o certo, faça-o rápido" → ajuste de desempenho é tardio (Cap. 21).

## Anti-patterns
- **Testar absolutamente tudo**: a maioria dos testes não terá valor; você perceberá isso e parará de escrever ("testar é bobagem").
- **Voltar e escrever testes para todo o código legado de uma vez**: escreva **sob demanda** (ao adicionar função, corrigir bug, refatorar).
- **Testes interdependentes**: uma falha dispara centenas → falsas negativas matam o hábito.

## Worked Example
Massimo Arnoldi: "testar vai contra a natureza humana. Se você libera o porco que existe em
você, programa sem testes. Depois, quando sua parte racional vence, você para e começa a
escrever testes. A programação em pares reduz a probabilidade de **ambos** os parceiros
liberarem seus porcos no mesmo momento." Ilustra por que a estratégia se apoia no princípio
"trabalhe a favor da natureza humana": pares + a satisfação de ver o verde sustentam o hábito
melhor do que qualquer argumento de longo prazo.

## Key Takeaways
1. Teste primeiro, minuto a minuto; preserve e rode tudo junto com frequência.
2. Teste apenas o que **pode falhar**; testar é apostar contra suas expectativas.
3. Unidade (programador) = 100% binário; funcional (cliente) = porcentagem crescente.
4. Em código legado, escreva testes **sob demanda**, não em massa.
5. Tenha um testador dedicado, focado no cliente, traduzindo testes funcionais.

## Connects To
- **Ch 5 (Custo das Modificações)**: testes automatizados são uma das três alavancas da curva achatada.
- **Ch 11 (Desenvolvimento)**: propriedade coletiva e integração contínua dependem dos testes a 100%.
- **Ch 22 (Papéis: Testador)**: papel focado no cliente, não em humilhar programadores.
