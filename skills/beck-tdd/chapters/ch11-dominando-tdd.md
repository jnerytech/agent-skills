# Capítulo 11: Dominando TDD (Cap. 32)

## Core Idea
Capítulo de questões abertas sobre integrar TDD à prática: tamanho dos passos, o que (não) testar, qualidade de testes, como TDD gera frameworks, escalabilidade, e a relação com padrões e com a Programação Extrema (XP).

## Frameworks Introduced
- **"Escreva testes até o medo virar tédio"** (Phlip): critério prático para *o quê* testar — condicionais, laços, operações, polimorfismo, mas só do *seu* código.
- **TMEF como guia**: decida quantos testes pelo Tempo Médio Entre Falhas desejado. Marca-passo (10→100 anos) justifica testes de condições extremas; problema do triângulo, não. (Beck: 6 testes; Bob Binder: 65, para o mesmo problema.)
- **Critérios para apagar testes**: (1) **confiança** — nunca apague se reduz sua confiança no comportamento; (2) **comunicação** — mantenha se contam cenários diferentes a um leitor. Só apague redundantes em ambos.
- **"Codifique para amanhã, projete para hoje"**: TDD inverte o conselho clássico — não projetar o futuro torna o código mais adaptável (satisfaz o Princípio Aberto/Fechado nos pontos que realmente variam).

## Key Concepts
- **Atrator (Phlip)**: testes + refatoração + features uma a uma criam um "atrator" matemático — todos os fluxos convergem para a corretude como função limite.
- **Passos adaptáveis**: você deve *saber* dar passos grandes e pequenos; a tendência ao longo do tempo é passos menores, mas o domínio é a escolha consciente.
- **ATDD (Application TDD)**: testes em nível de aplicação escritos por/com usuários; tem problema técnico (fixturing de feature inexistente) e social (nova responsabilidade, antes da implementação).
- **Suíte de 10 minutos**: o "9,8 m/s²" do TDD — suítes acima disso são inevitavelmente podadas.

## Reference Tables
Sinais de teste que revelam problema de *projeto* (testes como canário na mina):

| Sintoma no teste | Problema de projeto |
|---|---|
| Código de setup longo (100 linhas) | objetos grandes demais; divida-os |
| Duplicação de setup difícil de fatorar | objetos fortemente entrelaçados |
| Testes de execução longa | partes difíceis de testar isoladamente |
| Testes frágeis (quebram inesperado) | uma parte afeta outra surpreendentemente |

## Worked Example
**Quanto feedback você precisa? (problema do triângulo)**: dados 3 lados, retornar 1=equilátero, 2=isósceles, 3=escaleno, e lançar exceção se malformado. Beck resolve com **6 testes** (equilátero, isósceles, escaleno, irracional/desigualdade triangular, negativo, strings) e uma implementação que ordena os lados, falha se ≤0 ou se viola a desigualdade triangular, e retorna `sides asSet size`. Bob Binder escreveu **65** testes para o mesmo problema. A lição: o número de testes depende de quão cuidadosamente você mede o TMEF — não há resposta única.

## Anti-patterns
- **Testar código de terceiros sem motivo**: não teste o que não escreveu, salvo desconfiança específica.
- **Começar TDD pela aplicação inteira + mudança organizacional**: combina ritmo, fixturing e política — improvável dar certo. Domine vermelho/verde/refatore sozinho primeiro (regra do Teste de Um Só Passo).
- **Reescrever tudo ao adotar TDD em código legado**: meses sem feature nova; em vez disso, limite o escopo às partes que mudam.

## Key Takeaways
1. Teste até o medo virar tédio; teste só o seu código.
2. Quantos testes? Calibre pelo TMEF, não por permutações.
3. Apague testes só quando redundantes em confiança *e* comunicação.
4. Testes ruins são sintoma de projeto ruim — o teste é o canário.
5. TDD relaciona-se com XP: par, integração contínua, projeto simples, refatoração, entrega contínua — cada prática reforça as outras.

## Connects To
- **Ch 1**: as duas regras e o ritmo que este capítulo amplia.
- **Ch 9–10**: como TDD gera frameworks/padrões via Aberto/Fechado.
- **programacao-extrema** (skill): TDD é uma das 12 práticas de XP de Kent Beck.
