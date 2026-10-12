# Capítulo 5: Padrões de Barra Vermelha (Cap. 26)

## Core Idea
Quando, onde e por quanto tempo escrever testes — e como sustentar o ritmo. Trata da escolha do próximo teste, do primeiro teste, de espalhar a prática e de cuidar do corpo/mente do programador.

## Frameworks Introduced
- **Teste de Um Só Passo (One Step Test)**: pegue da lista o teste que *ensina algo* e que você *confia* que consegue implementar. Não o óbvio demais nem o impossível — "do conhecido ao desconhecido".
- **Teste Inicial (Starter Test)**: comece testando uma variante da operação que *não faz nada* (entrada mínima, saída = entrada). Encurta o laço quando o teste realista exigiria "ler teses de doutorado".
- **Teste de Explicação (Explanation Test)**: difunda TDD pedindo e dando explicações em termos de testes ("se tenho um Foo assim e um Bar assim, a resposta é 76?").
- **Teste de Aprendizado (Learning Test)**: antes de usar uma API/lib externa pela primeira vez, escreva um teste que verifica que ela funciona como você espera.
- **Outro Teste (Another Test)**: ideia tangencial na discussão? Adicione um teste à lista e volte ao assunto — não desvie.
- **Teste de Regressão (Regression Test)**: ao receber um defeito, escreva o *menor* teste que falha e que, ao passar, conserta o bug.

## Key Concepts
- **Pausa (Break)**: cansado ou travado? Faça uma pausa ("Metodologia do Chuveiro" de Ungar). Fadiga → pior julgamento → mais fadiga; quebre o laço com elemento externo (água, compromissos, férias).
- **Faça de Novo (Do Over)**: perdido? Jogue o código fora e recomece — trocar de par motiva recomeços produtivos.
- **Mesa barata, cadeira legal**: invista no que afeta o corpo (cadeira, máquina de dev), economize no resto.

## Mental Models
- Ao olhar a Lista de Testes: "óbvio, óbvio, não faço ideia, óbvio... ah, esse eu consigo" → o *último* (não-óbvio mas factível) é o próximo.
- Teste Inicial > Teste Realista no começo: realista resolve muitos problemas de uma vez e deixa você sem feedback por tempo demais.
- Cadeia de escape: sabe o que digitar → Implementação Óbvia; não sabe → Faça de Conta; projeto incerto → Triangule; ainda perdido → tome um banho.

## Code Examples
```java
// Starter Test para um redutor de polígonos: a menor entrada possível
Reducer r = new Reducer(new Polygon());
assertEquals(0, reducer.result().npoints);
```
- **What it demonstrates**: saída = entrada normalizada; entrada mínima (polígono vazio) torna o primeiro teste trivial de fazer passar.

## Worked Example
**Difundindo TDD num time hostil (Explanation Test)**: você é o único praticante. Não enfie TDD na cara — comece pedindo explicações em forma de exemplo: "Deixa ver se entendi: se eu tenho um Foo assim e um Bar assim, então a resposta deveria ser 76?". Depois, dê suas próprias explicações no mesmo formato: "Quando tenho Foo assim e Bar assim, a resposta é 76; mas se Foo for aquele e Bar este, eu gostaria que fosse 67." Você converteu uma conversa de design num caso de teste sem pregar.

## Anti-patterns
- **Entusiasmo do recém-convertido**: nada mata a disseminação de TDD mais rápido que forçá-lo nos outros.
- **"Espírito macho"**: avançar exausto destruindo saúde e família — Beck recusa-se a incentivar.

## Key Takeaways
1. Escolha o próximo teste pela combinação aprende-algo + confio-que-consigo.
2. Comece pela degeneração (operação que não faz nada), não pelo caso realista.
3. Defeito → primeiro um teste mínimo que o reproduz; pergunte como saberia escrevê-lo antes.
4. Capture tangentes como testes na lista; mantenha a trilha.
5. Cuide do laço fadiga/julgamento: pausa, recomeço, ergonomia.

## Connects To
- **Ch 4**: Lista de Testes (de onde se pega o One Step Test).
- **Ch 7**: Faça de Conta / Triangulação / Implementação Óbvia (a cadeia de escape).
- **Ch 6**: Teste Quebrado / Check-in Limpo (como *terminar* uma sessão).
