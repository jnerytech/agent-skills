# Capítulos 1–3: Risco, Episódio de Desenvolvimento e Economia

## Core Idea
O problema básico do desenvolvimento de software é o **risco**; a XP existe para
atacá-lo em todas as etapas. Software vale mais quando você gasta dinheiro mais
devagar, ganha mais cedo e, sobretudo, **preserva opções** de decisão de negócio.

## Frameworks Introduced
- **Risco como problema central**: liste os riscos concretos (deslize de cronograma,
  cancelamento, sistema "azeda", taxa de erros, negócio mal compreendido, mudança de
  negócio, falsa riqueza de funções, rotatividade) e mostre como cada prática XP ataca um.
  - Quando usar: ao justificar XP a um gerente cético — mapeie prática → risco mitigado.
  - Como: ciclos curtos limitam deslizes; testes contínuos evitam "azedar"; cliente
    presente evita negócio mal compreendido; prioridade por valor evita falsa riqueza.
- **Economia como opções (option value)**: um projeto de software é uma série de opções —
  abandonar, trocar, adiar, crescer. Quanto maior a **incerteza**, mais valiosa a estratégia
  que preserva opções.
  - Quando usar: para decidir "fazer agora vs. esperar" sob requisitos vagos.
  - Como: maximize feedback frequente, capacidade de mudar requisitos, investimento
    inicial baixo e velocidade de avanço. **Use XP quando os requisitos forem vagos ou instáveis.**
- **Episódio de Desenvolvimento (o "pulso" da XP)**: a menor unidade do ritmo diário —
  pegar tarefa → parear → escrever teste → implementar → refatorar → integrar → liberar.

## Key Concepts
- **Opção de abandonar/trocar/adiar/crescer**: quatro formas de valor de um projeto visto como opção.
- **Mortalidade do projeto**: probabilidade de o projeto sobreviver para pagar os fluxos de caixa; multiplica o valor presente.
- **Eliminar risco negativo**: opções "eliminam o lado ruim" — esperar custa pouco quando há incerteza alta.
- **Tarefa de engenharia**: menor unidade do cronograma (1–3 dias ideais).

## Mental Models
- Pense em cada decisão de projeto como **comprar uma opção financeira**: o valor vem da incerteza, não da certeza.
- Veja o desenvolvimento diário como **respiração**: aprender/testar/codificar/entregar, repetidamente.

## Anti-patterns
- **Antecipar funcionalidade por especulação**: gasta capital onde a incerteza torna "esperar" mais valioso.
- **Otimizar só custo** (orçamento anual): ignora que tempo, escopo e qualidade interagem.

## Worked Example
O episódio do Cap. 2: o programador pega o cartão "Exportar retenções do trimestre".
Pede ajuda a um colega (regra: ao ser pedido, diga "sim" → forma-se o par). Perguntam
"quais os casos de teste?" antes de qualquer código. Consultam Eddie 30s sobre os campos.
Abstraem uma superclasse de um teste existente (refatoração), rodam os testes — passam.
Escrevem o novo caso de teste primeiro — ele **falha** (nada implementado ainda). Implementam,
o teste passa; avançam caso a caso; quando o par vê código mais simples, **troca o teclado**
e refatora. Lista de pendências vazia → integram na máquina livre, rodam *todos* os testes,
um falha, corrigem, liberam. Isso é o ciclo XP inteiro em ~uma hora.

## Key Takeaways
1. Venda XP pelo risco: para cada risco do projeto, aponte a prática que o reduz.
2. Sob incerteza alta, **preservar opções vale mais que decidir cedo** — adie decisões caras.
3. Cinco fatores de uma opção; o que domina o valor é a **incerteza**.
4. O teste vem **antes** do código, sempre, no episódio diário.
5. Integração acontece **imediatamente** após o desenvolvimento, com teste de integração.

## Connects To
- **Ch 5 (Custo das Modificações)**: a curva achatada é o que torna "adiar decisões" barato.
- **Ch 15 (Planejamento)**: o Jogo do Planejamento operacionaliza "preservar opções".
- **Teoria de opções reais (real options)**: base econômica externa da XP.
