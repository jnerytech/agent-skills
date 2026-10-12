# Capítulo 3: Exemplo xUnit — Construindo o Framework de Testes (Caps. 18–24)

## Core Idea
Parte II constrói um framework de testes (xUnit) em Python, *guiado por testes pelo próprio framework* ("cirurgia cerebral em si mesmo"). Mais complexo que o exemplo financeiro, demonstra TDD em código "real" e o problema de inicialização (bootstrap): testar a ferramenta que ainda não existe.

## Frameworks Introduced
- **Lista de tarefas do xUnit** (guia o capítulo inteiro):
  1. Invoque o método teste
  2. Invoque `setUp` primeiro
  3. Invoque `tearDown` depois
  4. Invoque `tearDown` mesmo se o teste falhar
  5. Rode múltiplos testes
  6. Informe resultados coletados
- **Bootstrap manual**: sem framework ainda, o primeiro "prototeste" é verificado à mão (flag `wasRun`) antes de automatizar.
- **Template Method** (`run`): `setUp()` → `runTest()` → `tearDown()` em sequência invariável; subclasses preenchem os passos.
- **TestResult + Collecting Parameter**: um único `TestResult` é alocado pelo chamador e passado por todos os testes para coletar "2 run, 1 failed".
- **Composite (TestSuite)**: `TestSuite` responde às mesmas mensagens (`run(result)`) que um `TestCase`, tratando um teste e um grupo de forma idêntica.

## Key Concepts
- **WasRun**: caso de teste que registra se um método rodou (flag); vira a cobaia do bootstrap.
- **Pluggable Selector**: invoca dinamicamente o método pelo nome (`getattr(self, self.name)`) — usado uma vez e "prometido não repetir por 4 meses" (dificulta análise estática).
- **Mitose**: separar `WasRun` em superclasse `TestCase` + subclasse, movendo `name` e `run` para cima.
- **Falha vs. erro**: asserções que falham levam mais tempo para depurar; xUnit distingue *failures* (asserção) de *errors* e os exibe diferente.

## Code Examples
```python
class TestCase:
    def __init__(self, name):
        self.name = name
    def run(self, result):
        result.testStarted()
        self.setUp()
        try:
            method = getattr(self, self.name)
            method()
        except:
            result.testFailed()
        self.tearDown()

class TestSuite:
    def __init__(self): self.tests = []
    def add(self, test): self.tests.append(test)
    def run(self, result):
        for test in self.tests:
            test.run(result)   # Composite: mesma interface
```
- **What it demonstrates**: `TestCase.run` e `TestSuite.run` compartilham assinatura `run(result)` — eis o Composite + Collecting Parameter.

## Worked Example
**Bootstrap (Cap. 18)**: como testar um framework inexistente? Beck cria `WasRun` com flag `wasRun=None`. Roda código Python solto: `print test.wasRun` (espera `None`), chama o método, `print test.wasRun` (espera `1`). Falha porque a classe nem existe → define `class WasRun: pass` → falta atributo → `__init__` com `self.wasRun=None` → falta método → `testMethod` que faz `self.wasRun=1`. Verde manual. Depois substitui a chamada direta por `run()`, depois invocação dinâmica via `getattr`, depois mitose em `TestCase`. Por fim escreve o primeiro teste *de verdade* usando o próprio framework:
```python
class TestCaseTest(TestCase):
    def testRunning(self):
        test = WasRun("testMethod")
        assert(not test.wasRun)
        test.run()
        assert(test.wasRun)
```

## Anti-patterns
- **Escrever implementação antes do teste verde** (Cap. 23): Beck escreveu parte do `TestSuite` sem fazer o teste passar — "violação da Regra"; havia um Fake It simples disponível.
- **Passos grandes no bootstrap**: tentou com passos maiores, gastou ~6h e *pensou* ter código funcionando duas vezes quando não tinha.

## Key Takeaways
1. Implemente seu próprio xUnit ao aprender uma linguagem nova: os 8 de 10 primeiros testes exercitam quase todas as habilidades do dia a dia.
2. Os *casos de teste* importam mais que os detalhes de implementação do framework.
3. xUnit foi portado para 30+ linguagens — "tantos deveram tanto a tão poucas linhas" (Fowler).
4. Composite + Collecting Parameter surgem naturalmente da remoção de duplicação.
5. JUnit declara uma interface `Test` (`countTestCases()`, `run(TestResult)`) implementada por `TestCase` e `TestSuite`.

## Connects To
- **Ch 8**: padrões xUnit (Assertion, Fixture, Test Method, Exception Test, All Tests) formalizados.
- **Ch 9**: Template Method, Composite, Collecting Parameter, Pluggable Selector.
- **Ch 10**: Migrar Dados (usado ao transformar `test` único em coleção `tests`).
