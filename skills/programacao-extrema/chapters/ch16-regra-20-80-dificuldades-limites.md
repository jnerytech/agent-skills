# Capítulos 23–27: Regra 20-80, Dificuldades, Limites, XP em Ação e Conclusão

## Core Idea
O valor total da XP só vem quando **todas** as práticas operam juntas (sinergia > soma das
partes). A XP é **simples, mas não fácil** — o que a torna difícil são as emoções, sobretudo
o **medo**. Há ambientes onde ela não deve ser usada. E toda metodologia, no fundo, baseia-se
no medo.

## Frameworks Introduced
- **A Regra 20-80 aplicada à XP** (Cap. 23): coloque os 20% de funcionalidades/projeto mais
  valiosos primeiro; adie otimizações. Mas, como no esqui (*The Athletic Skier*), os últimos
  ajustes é que melhoram drasticamente — práticas só rendem o pleno quando quase todas estão presentes.
- **O que torna a XP difícil** (Cap. 24): fazer coisas simples; admitir que está errado;
  colaborar; destruir barreiras emocionais; ir contra o que deu certo no passado; pequenos
  problemas com efeitos gigantescos; redirecionar em culturas que exigem "apontar o carro".
- **Quando NÃO usar a XP** (Cap. 25) — os "estraga-prazeres":
  cultura empresarial de "apontar o carro" / especificação gigante; cultura de horas extras;
  programadores brilhantes resistentes; **tamanho grande** (>~20 programadores); tecnologia
  de **curva de custo exponencial**; feedback lento (compilar/certificar leva dias); impossível
  testar realisticamente; **ambiente físico errado** (andares/cubículos separados).
- **XP em Ação / Contratos** (Cap. 26): preço fixo/escopo fixo → **preço fixo/data fixa/escopo
  razoavelmente variável**. O time XP oferece algo como uma **assinatura**: trabalha à velocidade
  máxima por um período; o cliente redireciona a cada iteração.

## Key Concepts
- **Simples ≠ fácil**: as práticas se aprendem; o difícil é mantê-las equilibradas — por isso "sacrifica-se" um técnico experiente para virar treinador.
- **Síndrome da Primeira Terça**: pequeno desvio de processo (estimar coletivo e depois aceitar tarefa → quem aceita não é dono da estimativa) custou 1–2 dias por iteração no C3.
- **Gargalo de escala**: o processo de **integração não-paralelo** (uma máquina de integração).
- **Terceirização**: o cliente fica com código que não sabe manter; a XP mitiga via testes + cultura comunicada, mas o problema persiste.

## Mental Models
- "Toda metodologia se baseia no medo" (Cap. 27): a XP reflete os medos *do autor* — trabalho inútil, decisões erradas, não ter orgulho do trabalho, não ver os filhos.
- **Expectativa** (parábola do espadachim): ao se preparar para *tudo* que imagina, você fica vulnerável ao que **não** imagina. Desistir de se preparar para mudanças específicas prepara-o, paradoxalmente, para qualquer mudança.

## Anti-patterns
- **Forçar XP onde ela está fadada a falhar**: tão importante quanto usá-la onde traz vantagem real.
- **Contrato de preço/escopo fixos puro**: puxa fornecedor e cliente em direções opostas; termina em "os requisitos não estavam claros".
- **Segunda semana seguida de hora extra**: sinal certo de processo quebrado.
- **Bebê aos berros na sala**: "não há como executar XP" (humor do autor sobre ambiente).

## Worked Example
Contrato de preço fixo à moda XP: "Por 5 milhões de marcos, **acreditamos** poder produzir
estas histórias em 12 meses." O escopo inicial é uma **suposição**; o cliente decide se vale
o preço. É mais provável que ele **troque** histórias por outras de maior valor — "ninguém
reclama se recebe algo de maior valor do que esperava". Em vez de preço/data/escopo fixos, o
time entrega uma **assinatura**: velocidade máxima por um período, com o cliente redirecionando
formalmente no início de cada iteração, e entregas incrementais que permitem encerrar o
contrato cedo se o progresso ou o negócio mudarem.

## Key Takeaways
1. Valor pleno exige quase todas as práticas juntas (regra 20-80 / efeito esqui).
2. XP é simples, **não fácil**: o difícil é manter o equilíbrio sob medo e pressão.
3. Conheça os limites: cultura "apontar o carro", >20 devs, curva exponencial, feedback lento, ambiente errado.
4. Contratos viram preço fixo/data fixa/escopo variável — uma "assinatura" com redirecionamento por iteração.
5. Pequenos problemas de processo têm grandes efeitos — aceite a responsabilidade de detectá-los e consertá-los.

## Connects To
- **Ch 7 (Sinergia)** e **Ch 6 (12 Práticas)**: a regra 20-80 é a face econômica da sinergia.
- **Ch 5 (Custo das Modificações)**: tecnologia de curva exponencial é a contraindicação técnica central.
- **Ch 2/13 (Ambiente/Testes)**: ambiente errado e feedback lento aparecem como limites práticos.
