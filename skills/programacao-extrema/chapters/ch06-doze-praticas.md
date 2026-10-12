# Capítulo 10: Uma Rápida Visão Geral — As 12 Práticas

## Core Idea
O coração da XP: doze práticas simples (muitas abandonadas décadas atrás por "simplórias")
que, combinadas, se reforçam mutuamente. Onde uma é fraca, as outras compensam.

## Frameworks Introduced — As 12 Práticas
1. **O Jogo do Planejamento (Planning Game)** — determine o escopo da próxima versão
   combinando prioridades de negócio + estimativas técnicas. Quando a realidade contraria o
   plano, atualize o plano.
2. **Entregas frequentes (Small Releases)** — coloque um sistema simples em produção
   rápido; depois libere versões em ciclos curtos. Cada entrega faz sentido como um todo
   (nunca meia função).
3. **Metáfora (Metaphor)** — guie o desenvolvimento com uma única história compartilhada de
   como o sistema funciona como um todo. Substitui boa parte do que outros chamam de "arquitetura".
4. **Projeto simples (Simple Design)** — o sistema deve ser o mais simples possível a cada
   momento; complexidade desnecessária é removida assim que descoberta.
5. **Testes (Testing)** — programadores escrevem testes de unidade continuamente (devem
   passar 100%); clientes escrevem testes funcionais que demonstram funcionalidades prontas.
6. **Refatoração (Refactoring)** — reestruture sem mudar comportamento para remover
   duplicação, melhorar comunicação, simplificar, acrescentar flexibilidade.
7. **Programação em pares (Pair Programming)** — todo código de produção é escrito por dois
   programadores numa máquina.
8. **Propriedade coletiva (Collective Ownership)** — qualquer um pode mudar qualquer código,
   em qualquer lugar, a qualquer momento (na verdade, é **obrigado** a melhorar o que vê).
9. **Integração contínua (Continuous Integration)** — integre e teste várias vezes ao dia,
   a cada tarefa concluída.
10. **Semana de 40 horas (40-Hour Week)** — no máximo 40h/semana; **nunca** hora extra em
    duas semanas seguidas (sintoma de problema sério).
11. **Cliente presente (On-site Customer)** — um cliente real no time, disponível o tempo
    todo para responder perguntas.
12. **Padrões de codificação (Coding Standards)** — código segue regras que enfatizam
    comunicação; deve ser impossível dizer quem escreveu o quê.

## Key Concepts
- **Decisões dos Negócios no Planning Game**: escopo, prioridade, composição das versões, datas de entrega.
- **Decisões do Desenvolvimento**: estimativas, consequências técnicas, processo, cronograma detalhado.
- **Regra "uma e somente uma vez" (once and only once)**: sem lógica duplicada — base do projeto simples e dos padrões.
- **Projeto correto (4 critérios, em ordem)**: passa todos os testes; sem lógica duplicada; expressa toda intenção; menor nº de classes e métodos.

## Mental Models
- "Onde uma prática é fraca, os pontos fortes das outras compensam" — pense em rede, não em lista.
- Exercício de Tufte para projeto: desenhe à vontade, depois **apague tudo que não remove informação**; o que resta é o design certo.

## Anti-patterns
- **Adotar uma prática isolada e esperar todo o valor**: o valor vem da sinergia (ver Ch 11 e regra 20-80).
- **Propriedade individual de código**: gargala evolução; quando o dono sai, o conhecimento vai junto.
- **Hora extra recorrente**: mascara problema de processo e destrói o vigor que sustenta as outras práticas.

## Worked Example — Projeto Simples (4 critérios)
"O projeto correto em qualquer momento é aquele que: (1) executa todos os testes; (2) não
tem lógica duplicada — cuidado com duplicações escondidas, como hierarquias paralelas; (3)
expressa todas as intenções importantes para os programadores; (4) tem o menor número
possível de classes e métodos." Cada elemento do projeto precisa justificar sua existência
nesses termos, ou é removido.

## Key Takeaways
1. Decore as 12 práticas — são o vocabulário operacional da XP.
2. Planning Game separa decisões de **negócio** (o quê/quando) das de **desenvolvimento** (quanto custa/como).
3. Projeto simples = 4 critérios em ordem de prioridade.
4. Testes de unidade a 100%; sem código duplicado (once and only once).
5. As práticas só entregam valor pleno quando atuam **juntas**.

## Connects To
- **Ch 11 (Sinergia)**: por que cada prática "impossível" funciona graças às outras.
- **Ch 12–18**: cada estratégia detalha um subconjunto destas práticas.
- **Ch 23 (Regra 20-80)**: valor total só com todas as práticas operando.
