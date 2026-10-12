# Capítulos 4–6: Quatro Variáveis, Custo das Modificações e Aprendendo a Dirigir

## Core Idea
Controle quatro variáveis — **custo, tempo, qualidade, escopo** — sendo o **escopo** a
mais valiosa, porque é a mais maleável. Tudo isso só é possível porque a XP aposta que
a **curva de custo das modificações pode ser achatada**; e dirige-se o projeto como um
carro: muitos pequenos ajustes guiados por feedback, não poucos ajustes grandes.

## Frameworks Introduced
- **As Quatro Variáveis de Controle**: forças externas (clientes, gerentes) fixam três;
  o time recebe a quarta como resultado. Tentar fixar as quatro destrói a qualidade.
  - Quando usar: em toda negociação de prazo/escopo — torne as quatro **visíveis**.
  - Como: deixe Negócios fixarem custo, tempo e qualidade; ajuste **escopo** continuamente.
- **Curva de custo das modificações achatada**: a grande premissa técnica da XP. Se o custo
  de mudar não cresce exponencialmente, você toma decisões grandes o mais tarde possível.
  - Como achatar: (1) projeto simples, sem extras especulativos; (2) testes automatizados;
    (3) prática constante de refinar o projeto (refatoração).
- **Metáfora da Condução (Learning to Drive)**: "dirigir não é apontar o carro na direção
  certa; é prestar atenção constante e fazer pequenas correções para os dois lados."
  - O motorista do projeto é o **cliente**. Seu trabalho é dar a ele um volante e feedback de posição.

## Key Concepts
- **Escopo como variável maleável**: sempre há algo que pode ir para a próxima versão.
- **Qualidade interna vs. externa**: sacrificar qualidade interna por prazo é ganho de curtíssimo prazo que cobra caro.
- **Custo é a variável mais restrita**: dinheiro demais cedo cria mais problemas que resolve ("9 mulheres não geram um bebê em 1 mês").
- **Assíntota do custo**: meta da curva achatada — custo cresce devagar e estabiliza.

## Mental Models
- "Escopo é o seu volante." Quando faltar tempo, gire-o: corte ou adie funcionalidade, não qualidade.
- Trate qualidade não como variável livre, mas como **"excelente" ou "insanamente excelente"**.

## Anti-patterns
- **Fixar as quatro variáveis**: "qualidade some" — ninguém faz bom trabalho sob estresse extremo.
- **Sacrificar qualidade interna por prazo**: problemas internos "te alcançam" e encarecem manutenção.
- **Contratar 40 programadores no dia 1**: investimento precisa começar pequeno e crescer.

## Worked Example
O autor descobre às 17:00 que uma função complexa (transação multi-conta) nunca é usada.
17:02 — chama Massimo, escrevem uma consulta: das 300 mil transações, todas têm 1 débito e
1 crédito. 17:05 — mudam interface + implementação, 4 métodos, começam testes. 17:15 — +1.000
testes ainda passam 100%; iniciam migração do banco. 17:20 — backup feito, instalam, migram.
17:30 — testes de sanidade OK, vão para casa. Dia seguinte: log limpo, sem reclamações.
Uma mudança que a curva exponencial diria custar "milhares" levou **30 minutos** após 2 anos
em produção — porque havia projeto simples, testes e prática de refinar.

## Key Takeaways
1. Torne as quatro variáveis **visíveis**; deixe escolherem conscientemente qual controlar.
2. Negócios fixam custo/tempo/qualidade; o time entrega o **escopo** resultante.
3. A curva achatada (projeto simples + testes + refatoração) é o que viabiliza toda a XP.
4. Curva íngreme de custo torna XP **impossível** — não force XP onde mudar é desastroso.
5. Dirija com pequenas correções contínuas guiadas por feedback; a mudança é a única constante.

## Connects To
- **Ch 3 (Economia)**: adiar decisões caras só compensa se mudar for barato (curva achatada).
- **Ch 12 (Projeto Simples)**: simplicidade é uma das três alavancas que achatam a curva.
- **Ch 25 (Quando não usar XP)**: tecnologia de curva exponencial é contraindicação.
