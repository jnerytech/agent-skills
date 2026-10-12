# Capítulo 8: Padrões xUnit (Cap. 29)

## Core Idea
Padrões para *usar* um framework da família xUnit: como afirmar resultados, criar e liberar objetos comuns, representar um caso de teste, testar exceções e rodar tudo junto.

## Frameworks Introduced
- **Asserção (Assertion)**: escreva expressões booleanas que automatizam seu julgamento. Decisões devem ser booleanas; seja *específico* — `assertEquals(50, rect.area())`, não `assertTrue(area() != 0)`.
- **Fixture**: objetos comuns a vários testes → converta variáveis locais em variáveis de instância e inicialize em `setUp()`.
- **Fixture Externa (External Fixture)**: recursos externos (arquivos, conexões) → libere em `tearDown()`, garantido a rodar após o teste.
- **Método de Teste (Test Method)**: um caso de teste = um método cujo nome começa com `test`; ferramentas o descobrem por convenção. Nome deve dizer *por que* o teste existe.
- **Teste de Exceção (Exception Test)**: pegue a exceção *esperada* e ignore-a; chame `fail()` se ela *não* for lançada. Capture só o tipo esperado.
- **Todos os Testes (All Tests)**: faça uma suíte de suítes — uma por pacote, e uma agregando tudo (`AllTests.suite()`).

## Key Concepts
- **Caixa-preta > caixa-branca**: teste pelo protocolo público; querer espiar variáveis privadas é problema de *projeto*, não de teste.
- **Relação classe-de-teste × classe-de-modelo**: uma subclasse de `TestCase` por *tipo de fixture*, não por classe de modelo; tende a empatar em número, mas não 1:1.
- **Failure vs. error**: asserção com mensagem (`assertTrue("msg", cond)`) ajuda quando o build roda em batch.
- **Esboço (outline) de teste**: comentários hierárquicos viram contrato/documentação da classe testada (ideia de Patrick Logan / McConnell).

## Code Examples
```java
// Fixture: setUp() centraliza criação comum
private Rectangle empty;
public void setUp() { empty = new Rectangle(0,0,0,0); }
public void testEmpty() { assertTrue(empty.isEmpty()); }
public void testWidth() { assertEquals(0.0, empty.getWidth(), 0.0); }
```
```java
// External Fixture: tearDown libera o recurso
public void setUp(self): self.file = File("foobar").open()
public void testMethod(self): ...run the test...
public void tearDown(self): self.file.close()
```
- **What it demonstrates**: `setUp` remove duplicação de criação; `tearDown` remove o ruído de `try/finally/close` do corpo do teste.

## Reference Tables
Ciclo de chamada garantido pelo framework (Template Method `runBare`):

| Etapa | Quando roda | Falha de setUp? |
|---|---|---|
| `setUp()` | antes do teste | se falhar, `tearDown` **não** roda |
| método `test*()` | corpo do teste | — |
| `tearDown()` | sempre após o teste | só se `setUp` passou |

## Worked Example
**Exception Test** — buscar uma taxa inexistente deve lançar exceção:
```java
public void testMissingRate() {
    try {
        exchange.findRate("USD", "GBP");
        fail();                                  // se chegou aqui, não lançou — falha
    } catch (IllegalArgumentException expected) { // pega SÓ o tipo esperado
    }
}
```
Capturar apenas `IllegalArgumentException` garante que outro tipo de erro (inclusive falha de asserção) também seja reportado, em vez de silenciosamente engolido.

## Anti-patterns
- **`assertTrue(x != 0)`**: qualquer não-nulo passa; pouco útil. Diga o valor exato esperado.
- **Teste baseado na implementação atual** (`assertEquals(Running.class, contract.status.class)`): quebra se a representação muda; teste comportamento observável.
- **Catch genérico em Exception Test**: capture o tipo específico, senão mascara falhas.

## Key Takeaways
1. Asserções booleanas e específicas; valor esperado primeiro em `assertEquals`.
2. Fixture (`setUp`) remove duplicação de criação; `tearDown` libera recursos.
3. Um tipo de fixture = uma subclasse de `TestCase`.
4. Exception Test: `fail()` após a chamada, catch só do tipo esperado.
5. Teste pelo protocolo público; desejo de caixa-branca sinaliza falha de projeto.

## Connects To
- **Ch 3**: estes padrões são extraídos da construção do xUnit na Parte II.
- **Ch 9**: Template Method (`runBare`), Composite (`AllTests`/`TestSuite`).
- **Ch 6**: Crash Test Dummy (gera as exceções para o Exception Test).
