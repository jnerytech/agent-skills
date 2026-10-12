# Capítulo 8: Princípios Básicos

## Core Idea
Os quatro valores são vagos demais para decidir entre práticas. A partir deles derivam-se
~uma dúzia de **princípios concretos** que servem de critério de escolha: prefira a
alternativa que melhor atende aos princípios.

## Frameworks Introduced
- **Cinco princípios fundamentais**:
  - **Feedback rápido** — reduza ao máximo o tempo entre ação e feedback (segundos/minutos para programadores; dias/semanas para o negócio).
  - **Simplicidade presumida** — trate cada problema como se tivesse solução ridiculamente simples; o tempo economizado nos 98% paga os 2% difíceis.
  - **Mudanças incrementais** — grandes mudanças de uma vez não funcionam; resolva com a menor série de mudanças que faz diferença (projeto, plano, time, adoção).
  - **Aceitação das mudanças** — a melhor estratégia preserva o máximo de opções enquanto resolve o problema mais urgente.
  - **Alta qualidade** — qualidade não é variável livre; só há "excelente" ou "insanamente excelente".
- **Princípios menos fundamentais** (auxiliam em situações específicas):
  ensinar aprendendo; investimento inicial pequeno; jogar para ganhar; experimentação
  concreta; comunicação honesta e franca; trabalhar a favor dos instintos do pessoal;
  aceitação de responsabilidades; adaptação local; viajar com pouca bagagem; métricas genuínas.

## Key Concepts
- **Jogar para ganhar vs. jogar para não perder**: fazer só o que ajuda o time a vencer, não papelada defensiva ("CYA").
- **Experimentação concreta**: toda decisão abstrata (projeto ou requisito) deve virar um experimento/teste — não um documento pronto.
- **Aceitação de responsabilidades**: responsabilidade é **aceita, não dada** — base do planejamento bottom-up.
- **Viajar com pouca bagagem**: artefatos mantidos devem ser **poucos, simples e valiosos** (essencialmente testes e código).
- **Métricas genuínas**: meça no nível de precisão que seus instrumentos suportam ("2 semanas", não "14.176 horas").

## Mental Models
- "Trabalhe a favor da natureza humana, não contra ela": se uma prática não dá retorno de curto prazo, será abandonada sob pressão.
- Time XP como **nômades intelectuais**: prontos para mudar de direção, carregando só o essencial.

## Anti-patterns
- **Projetar para o reúso especulativo**: contraria simplicidade presumida; pague a complexidade só quando precisar.
- **Métricas que se aproximam de 100%**: tornam-se inúteis — substitua por outra que comece bem abaixo (exceto testes de unidade, que são pressuposto, não métrica).
- **Dominação (mandar fazer)**: gera cooperação aparente e sabotagem velada.

## Worked Example
Greg Hutchinson: um programador queria um diálogo de texto "inteligente" (ajustava tamanho
e quebras de linha por fonte). Hutchinson perguntou quantas pessoas precisavam — só ele —
e sugeriu a versão de 20 minutos que funcionava para o caso dele, deixando a interface
pronta para evoluir. O programador insistiu, gastou **2 dias**. No terceiro dia, os
requisitos dele mudaram e a função não era mais necessária. Ilustra **simplicidade presumida**
+ **investimento inicial pequeno**: 2 dias-homem desperdiçados num projeto já apertado.

## Key Takeaways
1. Os cinco fundamentais: feedback rápido, simplicidade presumida, mudanças incrementais, aceitação das mudanças, alta qualidade.
2. Use princípios como **critério de desempate** entre práticas alternativas.
3. Responsabilidade é aceita, não imposta → sem planejamento top-down.
4. Toda decisão abstrata vira experimento concreto.
5. Escolha métricas honestas e poucas; descarte as saturadas.

## Connects To
- **Ch 7 (Valores)**: cada princípio incorpora um ou mais valores em forma concreta.
- **Ch 12 (Projeto)** e **Ch 13 (Testes)**: "experimentação concreta" e "simplicidade presumida" guiam as estratégias.
- **Ch 8 cont. (Gerenciamento)**: "aceitação de responsabilidades" e "viajar leve" moldam o papel do gerente.
