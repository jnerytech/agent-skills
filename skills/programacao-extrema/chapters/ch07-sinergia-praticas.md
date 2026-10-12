# Capítulo 11: Como Isso Poderia Dar Certo? — A Sinergia das Práticas

## Core Idea
Cada prática XP, isolada, foi abandonada no passado por ter um ponto fraco fatal. A tese do
capítulo: **"Seria impossível… A não ser que…"** — o ponto fraco de cada prática é
compensado pelos pontos fortes das outras. Nenhuma prática se sustenta sozinha (exceto testes).

## Frameworks Introduced
- **Padrão "Seria impossível… A não ser que…"**: para cada prática, liste por que ela
  normalmente falha e quais outras práticas neutralizam essa falha.
  - Quando usar: ao defender uma prática que "parece ingênua" — mostre suas muletas.
- **Rede de reforço mútuo** (Figura 4 do livro): práticas conectadas reforçam-se; a riqueza
  vem da **interação**, não das peças individuais.

## Key Concepts — pares de reforço (exemplos do capítulo)
- **Jogo do Planejamento** funciona porque: cliente atualiza o plano, ciclos curtos limitam erros, cliente presente acelera ajustes.
- **Ciclos de entrega curtos** funcionam porque: planning prioriza valor, integração contínua barateia empacotar, testes reduzem erros, projeto simples basta para *esta* versão.
- **Metáfora** funciona porque: feedback do código real valida, refatoração refina o entendimento.
- **Projeto simples** funciona porque: refatoração desfaz o medo de mudar, metáfora dá convergência, par evita "simples burro".
- **Testes** funcionam porque: projeto simples facilita escrevê-los, par cobre o que você não imagina, sentir-se bem com o verde motiva.
- **Refatoração** funciona porque: propriedade coletiva libera mudar tudo, padrões evitam reformatar, par dá coragem, integração frequente pega conflitos cedo.
- **Programação em pares** funciona porque: padrões reduzem brigas, descanso reduz atrito, par escreve testes juntos, metáfora apoia nomeação.
- **Propriedade coletiva** funciona porque: integração curta reduz conflito, testes evitam estragar, par espalha conhecimento, padrões evitam guerra de estilo.
- **Integração contínua** funciona porque: testes rápidos confirmam, par reduz pela metade o que integrar, refatoração quebra em pedaços pequenos.
- **Semana de 40h** funciona porque: planning dá trabalho valioso e o conjunto de práticas já roda na velocidade máxima.
- **Cliente presente** funciona porque: ele agrega valor escrevendo testes funcionais e decidindo escopo/prioridade de pequena escala.
- **Padrões de codificação** funcionam porque: a XP como um todo faz querer pertencer a um time vencedor.

## Mental Models
- Pense em cada prática como uma perna de banquinho: tirar uma derruba; juntas, sustentam.
- "Testes é a única que se mantém quase sozinha" — por isso é o melhor ponto de partida.

## Anti-patterns
- **Implementar uma prática e descartar suas muletas**: ex.: refatorar sem testes nem integração frequente = risco alto.
- **Achar a XP complicada pelo diagrama**: as peças são simples; só a interação parece complexa.

## Worked Example
"Seria impossível escrever todo o código de produção em pares — será muito lento, e se duas
pessoas não se entenderem? **A não ser que**: os padrões de codificação reduzam brigas
mesquinhas; todos estejam descansados, reduzindo discussões; os pares escrevam testes juntos,
sintonizando antes de implementar; tenham a metáfora para apoiar nomeação; e trabalhem com
projeto simples, para os dois entenderem. **Dessa forma**, talvez seja possível parear todo
o código — e ainda evitar os erros e o desrespeito às práticas que surgem quando se programa só."

## Key Takeaways
1. Toda prática "ingênua" tem muletas — identifique-as antes de adotá-la sozinha.
2. Use o template "Seria impossível… a não ser que…" para auditar adoções parciais.
3. Testes é a prática mais autossuficiente → melhor ponto de entrada.
4. A riqueza da XP está na **interação**, não nas peças.
5. Remover uma prática enfraquece várias outras — pondere os efeitos de segunda ordem.

## Connects To
- **Ch 10 (12 Práticas)**: este capítulo é o "porquê funciona" daquele "o quê".
- **Ch 19–20 (Adotando/Ajustando)**: adoção uma prática por vez precisa respeitar as muletas.
- **Ch 23 (20-80)** e **Ch 24 (Dificuldades)**: sinergia explica o "tudo ou quase tudo".
