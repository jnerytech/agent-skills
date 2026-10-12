# Capítulos 19–21: Adotando, Ajustando e o Ciclo de Vida da XP

## Core Idea
Adote a XP **uma prática por vez**, sempre atacando o pior problema do time. Em código já
existente, ajuste prática a prática (comece por testes ou planejamento). Um projeto XP ideal
passa por exploração curta → anos de produção/refinamento → aposentadoria graciosa.

## Frameworks Introduced
- **Adoção (Don Wells)** — receita simples:
  1. escolha seu pior problema;
  2. resolva-o da maneira XP;
  3. quando não for mais o pior, repita.
  (+ reorganize a mobília para parear e sentar o cliente; + compre salgadinhos.)
- **Ajustando a XP (retrofitting)** — capítulo organizado **prática a prática**: testes,
  projeto, planejamento, gerenciamento, desenvolvimento. Adote só as práticas que ainda não faz.
  - **Testes sob demanda**: ao adicionar função / corrigir bug / refatorar, escreva testes primeiro — nunca todos de uma vez.
  - **Projeto**: refatore antes de implementar; defina poucos objetivos de refatoração de larga escala, cartões visíveis, e celebre ao concluir.
- **Ciclo de vida ideal — 5 fases**: **Exploração** → **Planejamento** → **Iterações para a
  primeira entrega** → **Produção** → **Manutenção** → **Morte**.

## Key Concepts
- **Exploração**: cliente pratica escrever histórias; programadores praticam a tecnologia (construindo um sistema parecido de 3–4 formas). Tecnologia que não funciona em 1 semana = arriscada.
- **Primeira entrega**: 2–6 meses; a primeira iteração define a **arquitetura** (esqueleto do sistema todo).
- **Produção**: ciclo de feedback mais apertado (iterações de 1 semana, reunião em pé diária); testes paralelos; ajuste de desempenho aqui ("faça-o executar, certo, rápido").
- **Manutenção**: o estado **normal** da XP — produzir novas funções, manter produção, entrar/sair pessoas, tudo ao mesmo tempo; meça o impacto do suporte na velocidade (não adivinhe).
- **Morte**: boa (cliente satisfeito, sem novas histórias → escreva um tour de 5–10 páginas) ou ruim (morte entrópica, custo de mudar insustentável). Celebre o adeus e aprenda com a queda.

## Mental Models
- "Ir para produção é morrer" (medo comum) → a XP inverte: **não estar em produção é gastar sem ganhar**.
- Rotação gradual do time: em menos de um ano você substitui todo o time original sem perturbar produção — comunicar a **cultura** importa tanto quanto os detalhes técnicos.

## Anti-patterns
- **Meias medidas em projeto problemático**: deixam todos onde estavam — se a base de código atual é pior que nada, queime-a e recomece (gesto dramático).
- **Escrever testes para todo o legado de uma vez**: faça sob demanda.
- **Evitar o código velho**: traga tudo à tona — "coisas terríveis crescem no escuro".
- **Contar com a XP para salvar um projeto se afogando**: sob estresse você regride a hábitos antigos; defina metas humildes.

## Worked Example
Transição de testes em código legado: o código escrito antes dos testes "é assustador — você
nunca sabe onde está". Regra: **não** volte e teste tudo. Escreva **sob demanda** — ao
adicionar função em código não testado, teste a funcionalidade atual primeiro; ao corrigir
bug, teste primeiro; ao refatorar, teste primeiro. No início parece lento, mas as partes mais
usadas do sistema (as que atraem mudanças) ficam completamente testadas rápido — e logo
parecem ter sido escritas em XP desde o começo.

## Key Takeaways
1. Adoção: pior problema → resolva à moda XP → repita.
2. Retrofitting é prática a prática; pule o que já faz; comece por testes ou planejamento.
3. Cinco fases do ciclo de vida; manutenção é o estado **normal**.
4. Primeira iteração define a arquitetura; primeira entrega em 2–6 meses.
5. Morra bem: documente um tour ao fim e celebre; aprenda com a entropia que venceu.

## Connects To
- **Ch 13 (Testes)**: "testes sob demanda" detalha a transição.
- **Ch 15 (Planejamento)**: as fases Exploração/Planejamento usam o Jogo do Planejamento.
- **Ch 24/25 (Dificuldades/Limites)**: por que adoção sob estresse é arriscada.
