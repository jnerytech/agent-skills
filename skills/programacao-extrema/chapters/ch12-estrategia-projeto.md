# Capítulo 17: Estratégia de Projeto

## Core Idea
Sempre tenha **o projeto mais simples que execute o conjunto de testes atual**. Projete hoje
para os problemas de hoje; refine continuamente a partir de um começo muito simples, retirando
toda flexibilidade que não se provar útil. Projeto acontece **através de refatoração**.

## Frameworks Introduced
- **A Coisa Mais Simples que Poderia Funcionar** — estratégia em 4 passos:
  1. Comece por um teste (saber quando terminou).
  2. Projete e implemente só o suficiente para esse teste (e os anteriores) passar.
  3. Repita 1 e 2.
  4. Sempre que vir oportunidade de simplificar, simplifique.
- **Definição de "mais simples" — 4 restrições em ordem de prioridade**:
  1. comunica tudo que você quer comunicar (código + testes);
  2. não tem código duplicado (1+2 = regra **once and only once**);
  3. menor número possível de classes;
  4. menor número possível de métodos.
- **Projeto por eliminação (exercício de Tufte)**: parta de um sistema que passa os testes e
  **apague tudo sem propósito** (comunicacional ou computacional); o que resta é o projeto mais simples.
- **Grandes refatorações em pequenos passos**: desembaralhe hierarquias ao longo de semanas/
  meses, um método/variável por vez, enquanto continua entregando histórias.

## Key Concepts
- **Projeto através de refatoração**: primeiro reestrutura, roda o teste anterior para garantir, depois implementa o próximo.
- **Primeiro uso → simples; segundo uso → generalize**: nunca pague por flexibilidade que não usa.
- **Papel dos diagramas**: ótimos para velocidade e detectar maus projetos (muitas linhas, assimetria), mas **não dão feedback concreto** — gaste 10–15 min, depois volte ao código. Não mantenha diagramas sincronizados com o código.
- **Arquitetura via metáfora + primeira iteração**: escolha histórias básicas que forcem a criar o "sistema todo" (esqueleto) e implemente-as da forma mais simples — a arquitetura emerge.

## Mental Models
- Custo de decidir hoje = custo + juros sobre ele + **inércia** que adiciona ao sistema. Benefício = valor esperado de a decisão ser usada no futuro.
- "Pegar problemas emprestados" (antecipar) é hábito que quanto mais esperto você é, mais difícil de desaprender.

## Anti-patterns
- **Projetar para o amanhã sob incerteza**: ou o amanhã não chega (função descartada) ou você aprende um jeito melhor — em ambos, paga para remover ou carregar excesso.
- **"Mais simples = menos classes/linhas" isolado**: leva a objetos grandes, métodos enormes ou compressão sem comunicação. Use as 4 restrições **na ordem**.
- **Manter múltiplos formatos da mesma informação sincronizados** (diagramas + código).

## Worked Example
Sistema de gestão de contratos de seguro: havia hierarquia de Contrato com subclasses
paralelas a Produto (viola once and only once — Figura 10). Em vez de parar um mês, o autor
avançou **um passo por vez** durante um ano, passando responsabilidades das subclasses de
Contrato para subclasses de Função ou de Produto, **sem nunca parar de entregar funcionalidade
em produção**. Ao fim do contrato, as subclasses de Contrato ainda existiam, mas muito mais
enxutas e perto de serem eliminadas (rumo à Figura 11: Contrato refere-se a uma Função, sem subclasses).

## Key Takeaways
1. Tenha sempre o projeto mais simples que passa os testes atuais.
2. "Mais simples" = 4 restrições em ordem: comunica · sem duplicação · menos classes · menos métodos.
3. Projete via refatoração: teste → mínimo para passar → simplifique → repita.
4. Primeiro uso rende o necessário; segundo uso rende flexibilidade.
5. Grandes refatorações em passos pequenos, sem parar a entrega; diagramas só 10–15 min e descarte.

## Connects To
- **Ch 5 (Custo das Modificações)**: o projeto simples é uma das três alavancas da curva achatada.
- **Ch 6 (Refatoração)** e **Ch 11 (Desenvolvimento)**: refatoração constante viabiliza esta estratégia.
- **Ch 10 (Metáfora)**: a metáfora dá a coesão que substitui a "arquitetura" tradicional.
