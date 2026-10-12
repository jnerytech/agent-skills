# Glossário — TDD: Desenvolvimento Guiado por Testes (Kent Beck)

Nomes de padrões mantêm o original em inglês entre parênteses (convenção da edição PT-BR, para consulta a bibliografia em inglês).

**Adicionar Parâmetro (Add Parameter)** — refatoração: adiciona parâmetro a método; use erros do compilador para achar chamadores (Ch 10).
**All Tests (Todos os Testes)** — suíte de suítes: uma por pacote + uma agregando tudo via `suite()` (Ch 8).
**Asserção (Assertion)** — expressão booleana que automatiza o julgamento sobre se o código funcionou; seja específico (Ch 8).
**Assert First (Defina uma Asserção Primeiro)** — escreva a asserção antes do resto do teste; trabalhe de trás para frente (Ch 4).
**ATDD (Application TDD)** — TDD em nível de aplicação, testes escritos por/com usuários; vs. TDD de programador (Ch 11).
**Atrator** — ponto de convergência: testes+refatoração+features incrementais aproximam a corretude como função limite (Phlip) (Ch 11).
**Bank** — guarda taxas de câmbio e reduz `Expression`s à moeda-alvo (`reduce`) no exemplo financeiro (Ch 2).
**Barra verde/vermelha** — feedback visual do xUnit: verde = testes passam, vermelho = falha (Ch 1).
**Collecting Parameter** — parâmetro passado para coletar resultados espalhados por vários objetos (ex.: `TestResult`) (Ch 3, 9).
**Command** — invocação de computação como objeto com `run()`, não como mensagem (Ch 9).
**Composite** — comportamento de uma lista de objetos tratado como um só objeto (ex.: `TestSuite`) (Ch 3, 9).
**Crash Test Dummy (Modelo de Teste de Acidentes)** — objeto que lança exceção em vez de trabalhar, para testar código de erro raro (Ch 6).
**Dados Evidentes (Evident Data)** — incluir esperado, real e a relação entre eles no teste (Ch 4).
**Dados de Teste (Test Data)** — dados escolhidos para tornar o teste legível; nunca a mesma constante para duas coisas (Ch 4).
**Dados Realistas** — dados do mundo real; úteis em tempo real, teste paralelo, refatoração de simulação (Ch 4).
**Dependência** — acoplamento que impede mudar um trecho sem mudar outro; problema-chave do software (Ch 1).
**Diagrama de Influência** — modelo de Weinberg de como atividades se afetam; conexões +/− e laços de feedback (Ch 12).
**Do Over (Faça de Novo)** — jogue o código fora e recomece quando estiver perdido (Ch 5).
**Duplicação** — sintoma da dependência; removê-la (regra 2) elimina dependência (Ch 1).
**Equivalência observacional** — refatoração TDD preserva a semântica só quanto aos testes que já passam (Ch 10).
**Exception Test (Teste de Exceção)** — `fail()` se a exceção esperada não for lançada; capture só o tipo esperado (Ch 8).
**Explanation Test (Teste de Explicação)** — difundir TDD pedindo/dando explicações como casos de teste (Ch 5).
**Expression** — metáfora: soma de dinheiros como expressão aritmética, reduzida pelo `Bank` (Ch 2).
**Extract Interface (Extrair Interface)** — criar interface com operações compartilhadas para 2ª implementação (Ch 10).
**Extract Method (Extrair Método)** — transformar parte de método longo em método separado (Ch 10).
**Factory Method** — criar objeto por método em vez de construtor, para flexibilidade (`Money.dollar(5)`) (Ch 1, 9).
**Fake It ('Til You Make It) (Faça de Conta)** — retornar constante e gradualmente transformá-la em expressão (Ch 7).
**Fixture** — objetos comuns a vários testes, criados em `setUp()` (Ch 8).
**Fixture Externa** — recursos externos liberados em `tearDown()` (Ch 8).
**Holding** — interface comum de `Account`/`Transaction` no exemplo de Composite (Ch 9).
**Imposter** — nova implementação do mesmo protocolo para introduzir variação (Ch 9).
**Inline Method (Método em uma Linha)** — substituir invocação pelo corpo do método, para ver o fluxo (Ch 10).
**Isolated Test (Teste Isolado)** — testes independentes entre si e de ordem; um teste quebrado = um problema (Ch 4).
**Isolate Change (Isolar Mudança)** — isolar a parte que muda antes de mudá-la (metáfora cirúrgica) (Ch 7, 10).
**Learning Test (Teste de Aprendizado)** — testar uma API/lib externa antes de usá-la pela primeira vez (Ch 5).
**Lista de Testes (Test List)** — lista viva de testes a escrever antes de começar (Ch 4).
**Log String (String de Registro)** — registrar mensagens numa string para testar a ordem das chamadas (Ch 6).
**Method Object (Objeto Método)** — transformar método complicado num objeto com `run()` (Ch 10).
**Migrate Data (Migrar Dados)** — trocar representação duplicando dados temporariamente (Ch 10).
**Mock Object (Objeto Simulado)** — versão faz-de-conta de recurso caro que responde com constantes (Ch 6).
**Money** — Value Object central do exemplo financeiro; implementa igualdade (Ch 1–2).
**Move Method (Mover Método)** — mover método para a classe à qual pertence (gatilho: 2+ mensagens a outro objeto) (Ch 10).
**Null Object** — objeto que representa o caso especial com o mesmo protocolo (ex.: `LaxSecurity`) (Ch 9).
**Obvious Implementation (Implementação Óbvia)** — digitar a solução simples quando você a conhece (Ch 7).
**One Step Test (Teste de Um Só Passo)** — pegar o teste que ensina algo e que você confia que consegue (Ch 5).
**One to Many (Um para Muitos)** — implementar sem coleção primeiro, depois com coleção (Ch 7).
**Pausa (Break)** — parar quando cansado/travado; quebra o laço fadiga→julgamento (Ch 5).
**Pluggable Object** — substituir condicional repetido por objeto com 2+ implementações (Ch 9).
**Pluggable Selector** — invocar método dinamicamente pelo nome (reflexão); usar com parcimônia (Ch 3, 9).
**Princípio Aberto/Fechado** — aberto para uso, fechado para modificação; satisfeito gradualmente pelo TDD (Ch 11).
**Refatoração** — mudar projeto preservando comportamento (no TDD, quanto aos testes que passam) (Ch 10).
**Reconcile Differences (Reconciliar Diferenças)** — aproximar trechos similares até idênticos, então fundir (Ch 10).
**Regression Test (Teste de Regressão)** — menor teste que reproduz um defeito relatado (Ch 5).
**Self Shunt (Autodesvio)** — o próprio `TestCase` atua como colaborador/mock (Ch 6).
**Singleton** — padrão que Beck recomenda *não* usar (variáveis globais disfarçadas) (Ch 9).
**Starter Test (Teste Inicial)** — começar por uma variante da operação que não faz nada (Ch 5).
**Sum** — `Expression` que compõe dois dinheiros (augend+addend); caso de Composite (Ch 2).
**TestCase / TestResult / TestSuite** — peças do xUnit construídas na Parte II (Ch 3).
**Test First (Teste Primeiro)** — escrever o teste antes do código; controle de escopo e projeto (Ch 4).
**Test Method (Método de Teste)** — caso de teste como método com nome iniciado por `test` (Ch 8).
**Teste (substantivo)** — procedimento automático de aceitação/rejeição (Ch 4).
**Template Method** — sequência invariável em termos de outros métodos; subclasses preenchem (Ch 8, 9).
**TMEF (Tempo Médio Entre Falhas)** — guia para decidir quantos testes escrever (Ch 11).
**Triangulação (Triangulate)** — abstrair só com dois ou mais exemplos (Ch 7).
**Value Object** — estado fixo na criação; operações retornam novo objeto; implementa igualdade (Ch 1, 9).
**Vermelho/Verde/Refatore** — ciclo central: teste falha → faça passar → remova duplicação (Ch 1).
**WasRun** — caso de teste-cobaia do bootstrap do xUnit, registra se um método rodou (Ch 3).
