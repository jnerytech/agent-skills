# Capítulo 1: Introdução

## Core Idea
O objetivo do livro é ajudar a **comunicar intenções por meio do código**. Padrões de implementação são as decisões táticas que se tomam vários vezes por minuto ao codificar (nomear variável, estruturar laço, dividir método) — não os padrões de projeto (GoF), que se tomam poucas vezes ao dia.

## Frameworks Introduced
- **Padrão de implementação**: decisão recorrente de codificação + suas forças/restrições recorrentes.
  - When to use: toda tarefa de codificação comum (nomear, iterar, decompor).
  - How: reconheça o problema comum → aplique a solução recomendada → adapte à especificidade local.
- **Os três passos para comunicar via código** (jornada do autor):
  1. **Desacelerar** até ter consciência do que se faz por instinto (parar de "codar por instinto").
  2. **Reconhecer a importância das outras pessoas** — decisão deliberada, requer prática.
  3. **Demonstrar na prática** — programar conscientemente para os outros e para si.

## Key Concepts
- **Comunicação por código**: leitor consegue entender, modificar ou usar o código.
- **Nível do livro**: fica entre padrões de projeto e manual da linguagem Java.
- **77 padrões nomeados** + muitos menores de passagem.
- **Subconjunto conservador de Java**: autor evita funcionalidades de ponta deliberadamente.
- **Fora de escopo**: concorrência (isole-a), processo de software (padrões funcionam em qualquer processo).

## Mental Models
- **Programa deve ler-se como um livro** (Literate Programming, Knuth): enredo, ritmo, trocas de frase.
- Pense "programar dificilmente é comunicação solitária homem-máquina".
- **Como ferramenta de consulta**: pule direto para o Cap 5, folheie até o fim, mantenha o livro ao lado enquanto programa; volte à teoria depois.

## Anti-patterns
- **Fingir que codifica por instinto**: impede consciência e comunicação.
- **Egocentrismo ao programar**: escrever só para si e para a máquina; perde a cor rápido.

## Key Takeaways
1. O código é lido muito mais vezes do que é escrito → otimize para leitura.
2. A maior parte do custo do software vem *após* a implantação → código barato = código fácil de ler.
3. Pensar "como outra pessoa veria isso?" ativa neurônios diferentes e melhora o raciocínio.
4. Aplica-se vários padrões de implementação *por minuto*; padrão de projeto, poucos *por dia*.

## Connects To
- **Ch 2**: o que é um padrão (padrão de forças).
- **Ch 3**: os valores/princípios por trás dos padrões.
- **Ch 4**: a justificativa econômica.
