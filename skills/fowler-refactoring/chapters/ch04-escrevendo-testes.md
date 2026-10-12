# Capítulo 4: Escrevendo testes

## Ideia central
A refatoração exige uma suíte de testes robusta e autoexecutável: sem testes que verifiquem os próprios resultados, não há como identificar com segurança os erros inevitáveis introduzidos ao reestruturar o código.

## Frameworks introduzidos
- **Código autotestável (Self-testing code)**: base de código que contém seus próprios testes, executados junto com o código de produção.
  - Quando usar: sempre que for refatorar, e idealmente em qualquer desenvolvimento profissional.
  - Como: escrever testes que comparam a saída esperada com a saída real e reportam "OK"/falha automaticamente (sem inspeção manual de console); executá-los a cada compilação/mudança pequena.
- **Padrão setup-exercise-verify (arrange-act-assert / given-when-then)**: estrutura de um teste de unidade em três fases visíveis.
  - Quando usar: em todo teste de unidade, para manter clareza sobre o que está sendo preparado, exercitado e verificado.
  - Como: configurar o fixture (setup), executar a ação sob teste (exercise), checar o resultado (verify); a quarta fase, teardown, é implícita quando o fixture é recriado em beforeEach.
- **Padrão de placeholder para valor esperado**: técnica para escrever testes sobre código legado já considerado correto.
  - Quando usar: ao acrescentar testes de caracterização a um código existente sem testes.
  - Como: escrever o teste com um valor placeholder, rodar, substituir o placeholder pelo valor real gerado, depois injetar uma falha temporária para confirmar que o teste realmente falha, e por fim remover a falha injetada.

## Conceitos-chave
- **Código autotestável**: testes que verificam a si mesmos e não exigem inspeção visual de saída.
- **Fixture**: os dados e objetos necessários para executar um teste (ex.: um objeto `Province` já carregado).
- **Sondar os limites (boundary conditions)**: testar casos extremos — coleção vazia, zero, negativos, strings vazias — além do "caminho feliz".
- **Caminho feliz (happy path)**: o uso comum e esperado do código, em que tudo funciona conforme previsto.
- **Erro vs. falha**: uma falha é uma verificação cujo valor está fora do esperado; um erro é uma exceção lançada em fase anterior (ex.: setup), sinal de uma situação não prevista pelo código.
- **Barra verde / barra vermelha**: metáfora do estado da suíte de testes — verde quando tudo passa, vermelha quando algo falha; "nunca refatore com uma barra vermelha".
- **TDD (Test-Driven Development)**: técnica de Kent Beck baseada em ciclos rápidos de teste (em falha) → código para passar → refatoração.
- **Cobertura de testes**: métrica útil só para achar áreas não testadas, não para avaliar a qualidade de uma suíte.

## Modelos mentais
- Testes devem ser orientados a risco: concentre esforço onde é mais provável haver bugs, não em todos os métodos públicos (evite testar simples getters/setters).
- É melhor escrever e executar testes incompletos do que não executar testes completos — testar demais leva ao desânimo e a testar de menos.
- Desempenhe o papel de "inimigo" do próprio código: pense ativamente em como fazê-lo falhar (limites, zeros, negativos, strings vazias).
- Ao receber um bug, escreva primeiro o teste de unidade que o expõe, só depois corrija — assim o bug fica permanentemente coberto.
- A melhor medida de "testes suficientes" é subjetiva: o nível de confiança de que um defeito introduzido fará algum teste falhar.

## Anti-padrões
- **Fixture compartilhado mutável entre testes (`const asia` no escopo do describe)**: gera testes não determinísticos, com falhas intermitentes dependentes da ordem de execução — uma "placa de Petri" para os piores bugs de teste; prefira recriar o fixture em `beforeEach`.
- **Múltiplas asserções desconexas em um único `it`**: o teste para na primeira falha, ocultando informações úteis sobre as demais; regra geral é uma verificação por teste, exceto quando as asserções estão intimamente relacionadas.
- **Testar todo método público indiscriminadamente**: dilui o esforço; foque nos pontos de maior risco/complexidade.
- **Deixar de fazer o teste falhar ao menos uma vez**: sem confirmar que o teste realmente captura o bug (via falha injetada), não há garantia de que ele protege algo.

## Exemplos de código
```javascript
describe('province', function() {
  let asia;
  beforeEach(function() {
    asia = new Province(sampleProvinceData());
  });

  it('shortfall', function() {
    expect(asia.shortfall).equal(5);
  });

  it('profit', function() {
    expect(asia.profit).equal(230);
  });

  it('change production', function() {
    asia.producers[0].production = 20;
    expect(asia.shortfall).equal(-6);
    expect(asia.profit).equal(292);
  });

  it('zero demand', function() {
    asia.demand = 0;
    expect(asia.shortfall).equal(-25);
    expect(asia.profit).equal(0);
  });

  it('negative demand', function() {
    asia.demand = -1;
    expect(asia.shortfall).equal(-26);
    expect(asia.profit).equal(-10);
  });

  it('empty string demand', function() {
    asia.demand = "";
    expect(asia.shortfall).NaN;
    expect(asia.profit).NaN;
  });
});

describe('no producers', function() {
  let noProducers;
  beforeEach(function() {
    const data = { name: "No producers", producers: [], demand: 30, price: 20 };
    noProducers = new Province(data);
  });
  it('shortfall', function() {
    expect(noProducers.shortfall).equal(30);
  });
  it('profit', function() {
    expect(noProducers.profit).equal(0);
  });
});
```
- **O que demonstra**: uso do Mocha (`describe`/`it`/`expect`) com `beforeEach` recriando o fixture a cada teste para evitar interação entre testes; cobertura do caminho feliz, de mudanças no fixture e de condições limites (coleção vazia, zero, negativo, string vazia).

## Exemplo prático (Worked Example)
1. **Teste inicial isolado**: primeiro teste único cobrindo `shortfall`, com fixture criado inline dentro do próprio `it` — `const asia = new Province(sampleProvinceData()); assert.equal(asia.shortfall, 5);`. Fowler injeta uma falha temporária (`* 2` no cálculo) só para confirmar que o teste realmente acusa erro, depois remove a falha.
2. **Segundo teste com duplicação**: acrescenta-se `profit`, repetindo a linha de criação do fixture em cada `it` — duplicação percebida como suspeita, igual a código duplicado em produção.
3. **Tentativa errada de compartilhar fixture**: mover `const asia = new Province(...)` para o escopo do `describe` parece eliminar a duplicação, mas `const` só protege a referência, não o conteúdo — um teste futuro que altere `asia` corromperia os demais. Marcado explicitamente como "NÃO FAÇA ISSO".
4. **Fixture correto via beforeEach**: solução final usa `let asia;` no escopo externo e recria `asia = new Province(sampleProvinceData())` dentro de `beforeEach`, garantindo um fixture novo e isolado antes de cada teste, sem sacrificar a leitura comum do fixture padrão.
5. **Sondando os limites**: a partir do fixture padrão em `beforeEach`, acrescentam-se testes de limite — produção vazia (`no producers`, fixture próprio), demanda zero, demanda negativa e demanda como string vazia (`NaN`) — cada um revelando perguntas sobre o comportamento esperado do domínio (ex.: demanda negativa deveria ser permitida?).
6. **Caso de erro genuíno**: passar `producers: ""` no lugar de um array gera um `TypeError` (`doc.producers.forEach is not a function`) durante o setup — não uma falha de asserção comum, mas um erro de execução; decide-se que, por não afetar o comportamento observável relevante à refatoração, não precisa necessariamente de tratamento, embora `Introduzir asserção` seja uma opção se o erro puder corromper dados silenciosamente.

## Pontos-chave (takeaways)
1. Garanta que os testes sejam totalmente automatizados e verifiquem os próprios resultados — sem isso não há código autotestável.
2. Sempre confirme que um teste falha quando deveria falhar (injete uma falha temporária e depois remova-a).
3. Execute os testes com frequência — a cada poucos minutos no código em que se está trabalhando, e todos pelo menos uma vez por dia.
4. Nunca compartilhe um fixture mutável entre testes; recrie-o em `beforeEach` para evitar não determinismo.
5. Concentre os testes nas condições limites (vazio, zero, negativo, string vazia) além do caminho feliz — é ali que os bugs se escondem.
6. Não deixe o medo de não capturar todos os bugs impedir de escrever testes que capturam a maioria deles; é melhor ter testes incompletos do que nenhum.
7. Ao receber um relatório de bug, escreva primeiro o teste de unidade que o expõe, só depois corrija o código.

## Conecta com
- **Cap 2**: testes habilitam pequenos passos seguros — a refatoração descrita nos princípios do Cap 2 depende diretamente da suíte de testes construída aqui; sem "barra verde" confiável, não se pode refatorar com segurança.
