# Capítulo 6: Padrões de Teste (Cap. 27)

## Core Idea
Técnicas mais detalhadas para *escrever* os testes: como quebrar um teste grande, como isolar dependências caras, como verificar comunicação e ordem de mensagens, como testar erros raros, e como começar/terminar sessões.

## Frameworks Introduced
- **Teste Filho (Child Test)**: o teste ficou grande demais? Escreva um teste *menor* que cobre a parte que não funciona, faça-o passar, e reintroduza o maior. Preserva o ritmo vermelho/verde/refatore.
- **Objeto Simulado (Mock Object)**: para recurso caro/complicado (ex.: banco de dados), crie uma versão faz-de-conta que responde com constantes e lança exceção se chamada de forma inesperada.
- **Autodesvio (Self Shunt)**: para testar se um objeto se comunica com outro, faça o *próprio caso de teste* ser o colaborador — o `TestCase` vira uma espécie de Mock.
- **String de Registro (Log String)**: para testar a *ordem* das mensagens, mantenha um log em string e anexe a cada chamada (`"setUp testMethod tearDown "`).
- **Modelo de Teste de Acidentes (Crash Test Dummy)**: para testar código de erro raro, invoque-o com um objeto especial que lança exceção em vez de fazer trabalho real (ex.: `File` cujo `createNewFile()` lança `IOException`).
- **Teste Quebrado (Broken Test)**: programando *sozinho*, termine a sessão deixando um teste falhando — marca onde retomar (truque de Richard Gabriel).
- **Check-in Limpo (Clean Check-in)**: programando *em time*, deixe todos os testes passando antes do check-in.

## Key Concepts
- **Legibilidade do Mock**: um teste com Mock se lê de ponta a ponta; com BD real cheio de dados, "14 respostas" não diz por que 14.
- **Self Shunt + Extract Interface**: pode exigir extrair uma interface para o caso de teste implementar.
- **Comentar testes para passar o check-in = proibido** (multa: cervejas na sexta).

## Code Examples
```python
# Self Shunt: o próprio TestCase é o listener
def testNotification(self):
    self.count = 0
    result = TestResult()
    result.addListener(self)          # <- self, não um objeto separado
    WasRun("testMethod").run(result)
    assert 1 == self.count
def startTest(self):
    self.count = self.count + 1
```
```java
// Crash Test Dummy anônimo: sabota só o método certo
public void testFileSystemError() {
    File f = new File("foo") {
        public boolean createNewFile() throws IOException { throw new IOException(); }
    };
    try { saveAs(f); fail(); } catch (IOException e) { }
}
```
- **What it demonstrates**: Self Shunt elimina a classe-listener extra; Crash Test Dummy simula só a falha desejada.

## Worked Example
**Mock Object para banco de dados**: BDs demoram a subir, são difíceis de manter limpos e amarram testes a uma rede. Em vez disso:
```java
public void testOrderLookup() {
    Database db = new MockDatabase();
    db.expectQuery("select order_no from Order where cust_no is 123");
    db.returnResult(new String[] {"Order 2", "Order 3"});
    ...
}
```
Se a consulta esperada não vier, o `MockDatabase` lança exceção; se vier, devolve um resultado de strings constantes. Ganhos: desempenho, confiabilidade e **legibilidade**. Risco: o mock pode divergir do objeto real — mitigue com um conjunto de testes que rode contra ambos.

## Anti-patterns
- **Recursos caros em variáveis globais/Singletons**: dificultam Mock; prefira passar o recurso como parâmetro.
- **Deixar dois testes vermelhos "só por uns minutos"**: Beck confessa fazer ao usar Child Test, mas alerta que é resquício do "teste-depois".

## Key Takeaways
1. Teste grande → quebre num Teste Filho, não sofra na barra vermelha.
2. Mock troca recurso caro por constantes legíveis e confiáveis.
3. Self Shunt + Log String testam comunicação e ordem sem dublês extras.
4. Código de erro não testado não funciona — use Crash Test Dummy.
5. Termine sessão solo com teste quebrado; sessão em time com tudo verde.

## Connects To
- **Ch 9**: Pluggable Object e outros padrões surgem ao remover condicionais.
- **Ch 10**: Extract Interface (necessário para Self Shunt em Java).
- **Ch 8**: Exception Test (parente do Crash Test Dummy).
