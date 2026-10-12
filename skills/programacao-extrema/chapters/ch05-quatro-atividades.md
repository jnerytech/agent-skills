# Capítulo 9: De Volta ao Básico — As Quatro Atividades

## Core Idea
Antes de prescrever práticas, defina o **escopo** da disciplina: as quatro atividades
básicas que a XP precisa estruturar são **Codificar, Testar, Ouvir e Projetar**. Nada extra.

## Frameworks Introduced
- **Codificar**: a atividade inevitável — no fim do dia precisa haver um programa.
  - Por que importa: código é o artefato sem o qual o desenvolvimento não vive; é meio de
    comunicação preciso (você vê a forma real das ideias, não a imaginada) e de aprendizado.
- **Testar**: "funções que não podem ser demonstradas por testes automatizados não existem."
  - Como: "infectado por testes" (Erich Gamma) — não escreva código sem um teste. Testes
    dizem **quando você terminou**. Teste só o que **pode falhar**.
- **Ouvir**: programadores "não sabem nada" do domínio — precisam perguntar e estar
  preparados para ouvir as respostas (e ouvir ativamente, ajudando o cliente a entender o que é difícil/fácil).
- **Projetar**: ouvir+testar+codificar em loop eterno não funciona — a **entropia** cobra.
  Projetar = criar uma estrutura que organiza a lógica para que uma mudança não force mudanças
  em toda parte (lógica com uma e só uma origem; lógica perto dos dados).

## Key Concepts
- **Entropia do sistema**: sem projeto, chega o dia em que fazer um teste passar exige quebrar outro.
- **Bom projeto vs. projeto ruim**: bom → mudança local, sem duplicação; ruim → mudança conceitual exige alterar muitas partes e duplicar lógica.
- **Dois públicos dos testes**: programadores (testes de unidade) e clientes (testes funcionais).
- **Nível de erros tolerável**: invista em testes até atingir a taxa de defeitos que você suporta — e então confie no verde.

## Mental Models
- "Você codifica porque senão não tem nada; testa porque senão não sabe quando terminou; ouve porque senão não sabe o que codificar/testar; projeta para poder fazer os três indefinidamente."
- Testes como **instrumentação**: o que importa é o comportamento do sistema, não os testes em si.

## Anti-patterns
- **Testes malfeitos**: dão falsa confiança — armadilha pronta para a próxima passagem.
- **Falsas negativas** (testes interdependentes): um falha e dispara centenas, desencorajando o hábito de testar.
- **"Codificar até terminar"**: sem projetar, a entropia trava a evolução.

## Worked Example
A história do BASIC: o autor resolvia exercícios "olhando o problema por minutos, digitando
o código, e corrigindo o que aparecesse". Ao tentar escrever um jogo tipo Star Trek (>20
linhas), **nada lhe ocorreu** — não sabia escrever uma aplicação maior. Tentou escrever
tudo no papel antes: travou na terceira linha. Conclusão: era preciso fazer **algo além de
codificar** — as outras três atividades (testar, ouvir, projetar) que estruturam o trabalho
quando o problema cresce.

## Key Takeaways
1. Quatro atividades a estruturar: **codificar, testar, ouvir, projetar**.
2. Funcionalidade sem teste automatizado "não existe".
3. Teste apenas o que pode falhar; o teste sinaliza o fim do trabalho.
4. Projetar é inevitável — é o que evita a entropia travar a evolução.
5. Testes de unidade (programador) executam a 100%; funcionais (cliente) são medidos em porcentagem.

## Connects To
- **Ch 10 (12 Práticas)**: cada prática estrutura uma dessas quatro atividades.
- **Ch 12 (Projeto)** e **Ch 13 (Testes)**: detalham "projetar" e "testar".
- **Ch 7 (Valores)**: código como meio de **comunicação** e **feedback**.
