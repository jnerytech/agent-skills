# Capítulo 7: Comportamento

## Core Idea
Como expressar o fluxo de controle de um programa. A regra central: **expresse claramente o fluxo principal; empurre os fluxos excepcionais para o mais claro possível sem obscurecer o principal.** Mensagens são o mecanismo-chave — cada mensagem é um ponto potencial de variação.

## Frameworks Introduced
### Fluxo
- **Fluxo de controle**: computação como sequência de passos. Java é da família em que a sequência é organização fundamental.
- **Fluxo principal**: o trajeto que será lido/mudado com mais frequência — dê a ele o poder expressivo da linguagem. Use exceções/guardas p/ o resto.

### Mensagens (variação)
- **Mensagem**: `input(); process(); output()` esconde detalhes E abre ponto de variação ("aqui algo interessante acontece, detalhes podem variar").
- **Mensagem de escolha**: mensagem polimórfica escolhe implementação em runtime (`brush.display(subject)`) — substitui `case`. Cada uma é convite à extensão; cada condicional explícito é ponto de modificação futura.
- **Envio duplo (double dispatch)**: duas mensagens de escolha em cascata p/ duas dimensões independentes (`shape.displayWith(brush)` → `brush.displayRectangle(this)`). Introduz duplicação — a dimensão *mais estável* recebe a segunda mensagem.
- **Mensagem de decomposição**: decomposição funcional pura — agrupa passos numa submensagem nomeada. Nome difícil ou lista longa de parâmetros = padrão errado (use objeto método).
- **Mensagem inversa**: torna simétrico o fluxo enviando tudo ao *mesmo* recebedor (`this`) para ler a estrutura numa só classe.
- **Mensagem convidativa**: nomeia mensagem que outros vão querer sobrescrever em subclasse — implementação padrão, ou `abstract` p/ explicitar o convite.
- **Mensagem explicativa**: envia mensagem com o nome do *problema*, que chama outra com o nome da *solução* (`highlight(area)` → `reverse(area)`). Use no lugar de comentar uma linha.

### Fluxo excepcional
- **Cláusula de guarda**: retorno prematuro p/ situação excepcional local (`if (isInitialized()) return;`). Evita `if/else` aninhado — apresenta um *fato*, não empilha condição na cabeça do leitor. Variante: `continue` no laço.
- **Exceção**: saltos que cruzam níveis da pilha (disco cheio, conexão perdida). Custo: "vazamento no projeto" que influencia todos os chamadores até o captor.
- **Exceção verificada**: declarada e checada pelo compilador — garante captura, mas infla declarações (~50%) e dificulta refatoração.
- **Propagação de exceção**: transforme/embrulhe a exceção de nível baixo dentro da de nível alto — preserva info de diagnóstico sem expor `NullPointerException` cru ao usuário.

## Key Concepts
- **Ordem de preferência p/ fluxo**: sequência → mensagens → iteração → condicionais → **exceções** (só quando o resto confundiria).
- **Intenção vs. implementação**: mensagem explicativa e de decomposição materializam essa distinção.
- **Estética como feedback**: impressões estéticas de simetria são sinal válido de qualidade — não é "só" impulso estético.

## Mental Models
- Cada mensagem = "lugar onde posso mudar o recebedor sem mudar o remetente".
- **"Uma entrada, uma saída" é folclore FORTRAN**: desnecessário em Java com métodos pequenos — libera as cláusulas de guarda.
- Expressar todos os caminhos igualmente = "tigela de minhocas" com flags atribuídas aqui, usadas ali.

## Code Examples
Cláusula de guarda desaninha pré-requisitos:
```java
void compute() {
  Server server = getServer();      if (server == null) return;
  Client client = server.getClient(); if (client == null) return;
  Request current = client.getRequest(); if (current == null) return;
  processRequest(current);
}
```
Mensagem explicativa em vez de comentário:
```java
flags |= LOADED_BIT;  // Set the loaded bit   ← evite
setLoadedFlag();      // ← prefira
void setLoadedFlag() { flags |= LOADED_BIT; }
```
Envio duplo:
```java
displayShape(Shape s, Brush b) { s.displayWith(b); }
Oval.displayWith(Brush b)      { b.displayOval(this); }
PostscriptBrush.displayOval(Oval o) { writer.print(...); }
```

## Worked Example — Mensagem inversa revela simetria
Método assimétrico (mensagem do meio vai p/ outro recebedor):
```java
void compute() { input(); helper.process(this); output(); }
```
Introduza auxiliar p/ que todas as mensagens vão a `this` — a estrutura de `compute()` lê-se numa só classe:
```java
void process(Helper helper) { helper.process(this); }
void compute()              { input(); process(helper); output(); }
```
Sinal de excesso: se `input`/`output` também viram mensagens inversas, mova o `compute()` inteiro p/ `Helper` — a funcionalidade quer estar lá:
```java
void compute() { new Helper(this).compute(); }
// Helper: void compute() { input(); process(); output(); }
```

## Anti-patterns
- **Condicional explícito onde caberia mensagem de escolha**: cada um é ponto de modificação futura.
- **Envio triplo+**: Beck tentou uma vez, não durou — sempre há forma mais clara p/ lógica multidimensional.
- **`if/else` aninhado profundo p/ pré-requisitos**: gera erros; use guardas.
- **Fluxo de controle via exceções** onde condicional/mensagem serviria: ilegível.
- **Expor exceção de baixo nível crua ao usuário** (`NullPointerException` na página): inútil, embrulhe-a.
- **Mensagem de escolha sem variação possível**: não crie método só p/ hipótese de variação.

## Key Takeaways
1. Fluxo principal claro; excepcional discreto — guardas p/ local, exceções p/ não-local.
2. Mensagem = variação barata; condicional = modificação cara.
3. Prefira sequência/mensagem/iteração/condicional a exceção, nessa ordem.
4. Guardas > `if/else` aninhado; "uma saída" é dogma obsoleto.
5. Mensagem explicativa substitui comentário de linha; nomeie pelo problema.

## Connects To
- **Ch 3**: simetria (mensagem inversa), expressão declarativa.
- **Ch 5**: mensagem de escolha ↔ implementador/delegação; envio duplo ↔ variação bidimensional.
- **Ch 8 (Métodos)**: objeto método (alternativa à decomposição), tamanho e nomeação de métodos.
