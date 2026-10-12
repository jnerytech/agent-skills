# Patterns — Técnicas de TDD (Kent Beck)

Padrões agrupados como no livro. Nomes em inglês mantidos para consulta cruzada.

## — Padrões de TDD (Ch 4 / Cap. 25) —

## Lista de Testes (Test List)
**When**: antes de começar uma sessão. **How**: liste exemplos de cada operação, versões nulas e refatorações previstas; novos testes vão para o fim. **Trade-off**: evita perder o fio; não escreva todos os testes de uma vez (inércia + barra vermelha prolongada).

## Test First / Assert First
**When**: sempre. **How**: teste antes do código; comece o teste pela asserção e preencha de trás para frente. **Trade-off**: controle de escopo e projeto > verificação tardia.

## Isolated Test
**When**: sempre. **How**: testes rápidos, independentes de ordem, sem estado compartilhado. **Trade-off**: força alta coesão/baixo acoplamento; custa esforço para dividir o problema.

## Evident Data / Test Data
**When**: ao escolher entradas. **How**: embuta a relação esperado↔real (`100/2*(1-0.015)`); use o menor dado significativo; nunca a mesma constante para duas coisas.

## — Padrões de Barra Vermelha (Ch 5 / Cap. 26) —

## One Step Test
**When**: escolher o próximo teste. **How**: pegue o que ensina algo *e* que você confia que implementa. **Trade-off**: nem óbvio demais, nem impossível.

## Starter Test
**When**: o primeiro teste de uma operação. **How**: teste uma variante que não faz nada (saída=entrada, entrada mínima). **Trade-off**: encurta o laço de feedback vs. teste realista.

## Regression Test
**When**: defeito relatado. **How**: escreva o menor teste que falha e que, ao passar, conserta. **Trade-off**: pergunte como saberia escrevê-lo antes — melhora sua intuição de teste.

## Learning Test
**When**: antes de usar API/lib externa pela 1ª vez. **How**: teste que a API funciona como você espera. **Trade-off**: roda primeiro a cada nova versão da lib.

## — Padrões de Barra Verde (Ch 7 / Cap. 28) —

## Fake It ('Til You Make It)
**When**: teste vermelho, implementação desconhecida. **How**: retorne constante → troque por expressão com variáveis. **Trade-off**: verde imediato (controle psicológico/escopo); a refatoração remove a duplicação teste↔código.

## Triangulate
**When**: muito inseguro sobre a abstração. **How**: só generalize com 2+ exemplos. **Trade-off**: regras claras, mas mais lento; abandone para Fake It/Óbvia quando confiante.

## Obvious Implementation
**When**: você sabe a solução simples. **How**: apenas digite-a ("segunda marcha"). **Trade-off**: rápido, mas exige perfeição; reduza a marcha se surpreendido por vermelho.

## One to Many
**When**: operação sobre coleção. **How**: implemente para um item; adicione parâmetro-coleção (Isolate Change); migre para a coleção; apague o escalar.

## — Padrões de Teste (Ch 6 / Cap. 27) —

## Child Test
**When**: o teste ficou grande demais. **How**: escreva um teste menor da parte que falha, passe-o, reintroduza o maior. **Trade-off**: preserva o ritmo vermelho/verde/refatore.

## Mock Object / Self Shunt / Log String
**When**: recurso caro / testar comunicação / testar ordem de mensagens. **How**: Mock responde com constantes; Self Shunt = o próprio TestCase é o colaborador; Log String anexa cada chamada a uma string. **Trade-off**: legibilidade ↑; Mock pode divergir do real (rode testes contra ambos).

## Crash Test Dummy
**When**: testar código de erro raro. **How**: objeto/classe anônima que lança exceção em vez de trabalhar. **Trade-off**: código de erro não testado não funciona.

## Broken Test / Clean Check-in
**When**: terminar sessão solo / em time. **How**: solo = deixe um teste quebrado (marca de retomada); time = deixe tudo verde antes do check-in. **Trade-off**: comentar testes para passar o check-in é proibido.

## — Padrões de Projeto no TDD (Ch 9 / Cap. 30) —

## Value Object
**When**: objetos compartilhados sem identidade importante. **How**: estado fixo na criação; operações retornam novo objeto; implemente igualdade. **Trade-off**: resolve aliasing; alocações podem custar desempenho.

## Null Object
**When**: caso especial representado por ausência. **How**: objeto de mesmo protocolo que não faz nada (`LaxSecurity`). **Trade-off**: elimina checagens de nulo, mas pode custar mais linhas do que economiza.

## Pluggable Object / Pluggable Selector
**When**: condicional explícito repetido / muitas subclasses de um método só. **How**: objeto com 2+ implementações / invocação dinâmica por nome de método. **Trade-off**: Pluggable Selector dificulta rastrear invocações — use com parcimônia.

## Composite + Collecting Parameter
**When**: lista de objetos tratada como um só / coletar resultados espalhados. **How**: composto responde às mesmas mensagens que o primitivo; passe um coletor (`TestResult`). **Trade-off**: "cheiro" de Composite (Transaction não tem saldo) compensado pela simplicidade.

## Template Method / Command / Factory Method
**When**: sequência invariável / invocação como objeto / criação flexível. **How**: método em termos de outros (`runBare`) / objeto com `run()` / criar via método (`Money.dollar`). **Trade-off**: Factory Method adiciona indireção — só quando precisar da flexibilidade.

## — Refatorações (Ch 10 / Cap. 31) —

## Reconcile Differences
**How**: aproxime trechos similares gradualmente; funda só quando idênticos. Vale para laços, condicionais, métodos, classes.

## Isolate Change / Migrate Data
**How**: isole a parte que muda antes de mudá-la; troque representação duplicando dados temporariamente (novo formato → popula ambos → usa novo → apaga antigo).

## Extract Method / Inline Method / Extract Interface / Move Method / Method Object
**How**: extrair trecho em método; inline para ver o fluxo; extrair interface para 2ª implementação; mover método (gatilho: 2+ mensagens a outro objeto); virar objeto quando há muitos parâmetros/temporárias.
