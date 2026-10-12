# Patterns — Técnicas da XP

## As 12 Práticas (referência rápida)
**When to use**: implementar XP de verdade — adote uma por vez (Ch 19), mas busque o conjunto (Ch 23).
**How**: Jogo do Planejamento · Entregas frequentes · Metáfora · Projeto simples · Testes · Refatoração · Programação em pares · Propriedade coletiva · Integração contínua · Semana de 40h · Cliente presente · Padrões de codificação.
**Trade-offs**: cada prática isolada tem ponto fraco fatal; só rendem o pleno em sinergia (Ch 11).

## Jogo do Planejamento (Planning Game)
**When to use**: definir/atualizar o escopo de uma entrega ou iteração.
**How**: 3 fases — Exploração (escreva/estime/separe história) → Comprometimento (classifique por valor; por risco; defina velocidade; escolha escopo) → Direcionamento (iteração; recuperação; nova história; reestimativa).
**Trade-offs**: dois jogadores (Negócios/Desenvolvimento) reduzem emoção, mas regras não eliminam conflito — são referência comum.

## Estimativa em Tempo Ideal + Fator de Carga
**When to use**: estimar histórias/tarefas de forma calibrável.
**How**: estime "sem distrações"; meça o fator de carga (ideal/calendário, ~2–4) das últimas iterações; multiplique para obter o calendário. Quem implementa estima; candidata-se à tarefa **antes** de estimar.
**Trade-offs**: estimar coletivo e aceitar depois gera a Síndrome da Primeira Terça.

## Projeto da Coisa Mais Simples (Simplest Thing That Could Work)
**When to use**: a cada incremento de projeto.
**How**: (1) comece por um teste; (2) implemente o mínimo para passar; (3) repita; (4) simplifique ao ver oportunidade. "Mais simples" = comunica · sem duplicação · menos classes · menos métodos (nessa ordem).
**Trade-offs**: contra o instinto de antecipar; difícil sob prazo apertado.

## Projeto Através de Refatoração
**When to use**: evoluir o design sem big design up front.
**How**: ao implementar, pergunte se dá para mudar o existente p/ facilitar a adição; depois simplifique mantendo os testes verdes. Grandes refatorações em **passos pequenos**, sem parar a entrega.
**Trade-offs**: refatorar gasta mais que o mínimo hoje, mas garante adições baratas amanhã. Não refatore por especulação — só quando o sistema pede.

## Test-First (Testes Isolados e Automáticos)
**When to use**: sempre que código pode falhar.
**How**: escreva o teste antes; unidade (programador) a 100%, funcional (cliente) em %; testes isolados (sem cascata) e automáticos. Em legado, teste **sob demanda**.
**Trade-offs**: "testar é apostar" — só vale o teste que pode contrariar sua expectativa; testar tudo desencoraja o hábito.

## Programação em Pares
**When to use**: todo código de produção.
**How**: um digita (tático), o outro pensa estratégico; troque pares ~2x/dia; comece aos poucos (1h por vez).
**Trade-offs**: parece mais lento; ganha em qualidade e mantém as outras práticas vivas sob estresse.

## Integração Contínua
**When to use**: ao fim de cada episódio (poucas horas, máx. 1 dia).
**How**: integre um conjunto de mudanças por vez na máquina de integração; rode todos os testes até 100%; se não chegar a 100%, jogue fora e recomece.
**Trade-offs**: o processo de integração não-paralelo é o gargalo de escala.

## Metáfora do Sistema
**When to use**: dar coesão e vocabulário ao sistema (no lugar de "arquitetura").
**How**: uma única história compartilhada por clientes, programadores e gerentes; nomes técnicos derivam dela; refine via refatoração e feedback do código.
**Trade-offs**: vaga no início — valide com código real cedo.

## Adoção: Pior Problema Primeiro (Don Wells)
**When to use**: introduzir XP em time novo ou existente.
**How**: 1) escolha o pior problema; 2) resolva à moda XP; 3) quando não for mais o pior, repita. Comece por testes ou planejamento; reorganize a mobília.
**Trade-offs**: sob projeto se afogando, a adoção é arriscada — metas humildes.

## Grande e Visível Mural (métricas)
**When to use**: comunicar progresso e necessidade de mudança.
**How**: 3–4 métricas por vez (ex.: razão estimado/calendário, nº de testes); atualize ≥1x/semana; aposente métricas saturadas (perto de 100%).
**Trade-offs**: gerencie pelas sensações também, não só pelos números.

## Contrato como Assinatura
**When to use**: encaixar XP em preço fixo.
**How**: escopo inicial = suposição; preço fixo/data fixa/escopo razoavelmente variável; cliente redireciona por iteração; entregas incrementais permitem encerrar cedo.
**Trade-offs**: exige cliente continuamente engajado, não um documento de requisitos.
