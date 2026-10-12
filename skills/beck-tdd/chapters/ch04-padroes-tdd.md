# Capítulo 4: Padrões de Desenvolvimento Guiado por Testes (Cap. 25)

## Core Idea
Responde às questões estratégicas antes dos detalhes: o que é "testar", quando testar, que lógica e que dados testar. O fio condutor é a **espiral da morte do estresse**: mais estresse → menos teste → mais erros → mais estresse; testes automáticos quebram o laço, transmutando "medo em tédio".

## Frameworks Introduced
- **Teste (substantivo)**: um procedimento automático de aceitação/rejeição. Escreva um teste automático — pressione um botão, sem julgamento humano.
- **Teste Isolado (Isolated Test)**: testes não devem afetar uns aos outros; rápidos, independentes de ordem. *Um teste quebrado = um problema.*
- **Lista de Testes (Test List)**: antes de começar, liste todos os testes que sabe que precisará — exemplos de cada operação, versões nulas, e refatorações previstas.
- **Teste Primeiro (Test First)**: escreva o teste antes do código testado — ferramenta de controle de escopo e projeto, não só verificação.
- **Defina uma Asserção Primeiro (Assert First)**: comece o teste pela asserção que passará quando pronto; trabalhe de trás para frente (autossimilaridade: sistema←história, feature←teste, teste←asserção).
- **Dados de Teste (Test Data)**: use dados que tornem o teste fácil de ler; se 1 e 2 não diferem conceitualmente, use 1. Nunca use a mesma constante para duas coisas.
- **Dados Evidentes (Evident Data)**: inclua resultado esperado e real *e a relação entre eles* no teste (`100/2*(1-0.015)` em vez de `49.25`).

## Key Concepts
- **Diagrama de influência**: seta = mais origem ⇒ mais destino; seta com círculo = mais origem ⇒ menos destino. Laço de feedback positivo amplifica.
- **Conhecido-a-desconhecido**: programas crescem do que você sabe para o que vai aprender — nem top-down nem bottom-up.
- **Dados Realistas**: alternativa aos Dados de Teste — útil em tempo real, teste paralelo (comparar saída nova × antiga), e refatorar simulações com ponto flutuante.

## Mental Models
- Pense em testes como a **Pedra Filosofal**: rode-os quando o estresse subir; "ainda verdes" reduz o medo.
- Use **Lista de Testes** para nunca dar um passo "sem que o pé vá para terra firme".
- Regra do alpinista: 3 dos 4 membros sempre fixos = TDD puro nunca está a mais de uma mudança da barra verde.

## Code Examples
```java
// Assert First: começa pela asserção, depois preenche de trás para frente
testCompleteTransaction() {
    Server writer = Server(defaultPort(), "abc");
    Socket reader = Socket("localhost", defaultPort());
    Buffer reply = reader.contents();
    assertTrue(reader.isClosed());
    assertEquals("abc", reply.contents());   // asserção escrita PRIMEIRO
}
```
- **What it demonstrates**: cada linha acima da asserção foi adicionada para suprir o que a asserção exigia.

## Worked Example
**Dados Evidentes** — converter moeda com 1,5% de comissão, taxa USD→GBP de 2:1, trocar $100 → 50 GBP − 1,5% = 49,25 GBP. Em vez de cravar `49.25`, escreva a relação explícita:
```java
Bank bank = new Bank();
bank.addRate("USD", "GBP", 2);
bank.commission(0.015);
Money result = bank.convert(new Note(100, "USD"), "GBP");
assertEquals(new Note(100 / 2 * (1 - 0.015), "GBP"), result);
```
O leitor (e o futuro você) vê de onde o número veio — e já sabe o que programar.

## Anti-patterns
- **Escrita em massa de testes**: dez testes vermelhos = caminho longo até o verde + inércia para refatorar. Implemente um por vez.
- **Manter a lista só na cabeça**: laço de feedback positivo — quanto mais você sabe que falta, menos atenção dá ao que faz.

## Key Takeaways
1. Testar (verbo) ≠ ter testes (substantivo automático).
2. Isolamento de testes força alta coesão e baixo acoplamento.
3. Test First é controle de escopo, não cerimônia.
4. Dados de teste existem para um *leitor*; diferença nos dados deve ser significativa.
5. Dados Evidentes embutem a derivação do resultado no próprio teste.

## Connects To
- **Ch 5**: quando/onde escrever testes (Padrões de Barra Vermelha).
- **Ch 6**: técnicas detalhadas de escrita (Mock, Self Shunt, Log String).
- **Ap. I**: diagramas de influência detalhados.
