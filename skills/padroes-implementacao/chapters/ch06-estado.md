# Capítulo 6: Estado

## Core Idea
Objetos particionam o estado em pedacinhos discretos, cada um um "computadorzinho" com acesso limitado aos outros — o que torna previsível o efeito de uma mudança. A chave: **estados similares juntos, estados diferentes separados** (mesmo uso + mesmo tempo de vida = similares).

## Frameworks Introduced
### Acesso ao estado
- **Acesso direto** (`x = 10`): claro mas rígido; é detalhe de implementação de baixo nível.
- **Acesso indireto** (getter/setter): flexível mas menos claro; necessário quando dados são acoplados (cache, listener).
  - **Estratégia padrão de Beck**: acesso *direto* dentro da classe (+ classes internas), acesso *indireto* para clientes.

### Onde guardar o estado
- **Estado comum**: campos declarados — todo objeto da classe tem os mesmos dados. Comunica claramente o que é preciso p/ um objeto bem formado. **Prefira sempre que possível.**
- **Estado variável**: `Map<String,Object>` — dados diferem por instância. Flexível mas comunica mal. Use só p/ campos que podem ou não existir por uso.
- **Estado extrínseco**: estado de propósito especial (ex.: posição em disco) guardado *fora* do objeto, num `IdentityMap` mantido por quem usa. Raro (dificulta cópia e debug).

### Variáveis
- **Variável**: leitor precisa de escopo, tempo de vida, função e tipo. Comunique escopo/tipo pelo *contexto*, reserve o *nome* p/ a função.
- **Variável local**: declare pouco antes do uso, no escopo mais interno. Funções: coletor (`result`), contador (`count`), explicação, reúso, elemento (`each`).
- **Campo**: mesmo escopo/tempo de vida do objeto; declare todos juntos (início ou fim). Funções: auxiliar, flag, estratégia, estado, componentes.

### Parâmetros (acoplamento crescente)
- **Parâmetro**: acoplamento mais fraco que referência permanente — prefira sempre que possível. Mas repetir o mesmo parâmetro em vários métodos → vire referência (campo).
- **Parâmetro coletor**: passe um objeto que coleta resultados de várias invocações (`List`, `GraphicsContext`, `TestResult`).
- **Parâmetro opcional**: obrigatórios primeiro, opcionais no fim (padrão telescópico).
- **Var args** (`method(Class... classes)`): nº variável; deve ser o último parâmetro.
- **Objeto parâmetro**: grupo de parâmetros que anda junto → vira objeto com campos (`Rectangle` em vez de `x,y,w,h`). Vira lar p/ lógica (ex.: `bounds.expand(-2)`).

### Nomeação e tipos
- **Constante** (`static final`, MAIÚSCULAS): comunica significado (`Color.WHITE` > `0xFFFFFF`), evita erros de mudança.
- **Nome sugestivo de função**: nomeie pela função na computação, **não** pelo tipo (Java já garante tipo). Não abrevie (lê-se mais que se digita).
- **Tipo declarado**: declare como a variável é *usada*, não como é *implementada* (`Collection` > `ArrayList` quando indexação não importa) — mas priorize consistência sobre generalidade máxima.

### Inicialização
- **Inicialização ansiosa**: inicialize na declaração ou no construtor. Garante variável pronta antes do uso. Padrão default.
- **Inicialização preguiçosa**: getter que inicializa no 1º acesso — quando o cálculo é caro e a variável pode nunca ser usada (ex.: plug-ins do Eclipse). "O desempenho é importante."

## Key Concepts
- **Estado × concorrência**: não combinam — problemas de paralelismo somem sem estado (por isso isole o estado).
- **Campos públicos escurecem os limites entre objetos** — a facilidade não compensa a perda de independência.
- **Prefixo comum em muitas variáveis** (`borderWidth`, `borderColor`) → objeto auxiliar.

## Mental Models
- Cada objeto = um pequeno computador com memória própria isolada.
- **Fios de Gulliver**: um parâmetro é um fio fino de acoplamento; muitos fios finos imobilizam o objeto → troque por uma referência.
- Estado com borda vs. sem borda → melhor expresso por *polimorfismo* (duas classes) que por flag + estado variável.

## Code Examples
Parâmetro coletor (linearizar árvore):
```java
Node asList() { List results = new ArrayList(); addTo(results); return results; }
void addTo(List elements) {
  elements.add(getValue());
  for (Node each : getChildren()) each.addTo(elements);
}
```
Objeto parâmetro encurta e dá lar à lógica:
```java
setOuterBounds(x, y, width, height);
setInnerBounds(x+2, y+2, width-4, height-4);   // antes
setOuterBounds(bounds);
setInnerBounds(bounds.expand(-2));             // depois
```
Reúso — congelar o tempo:
```java
long now = System.currentTimeMillis();
for (Clock each : getClocks()) each.setTime(now);  // não currentTimeMillis() no laço
```

## Reference Tables
| Estado | Comunica | Flexível | Quando |
|---|---|---|---|
| Comum (campos) | ótimo | baixo | padrão |
| Variável (map) | ruim | alto | campos condicionais ao uso |
| Extrínseco | — | — | estado que só um subsistema quer |

| Inicialização | Leitura | Quando |
|---|---|---|
| Ansiosa | fácil | padrão |
| Preguiçosa | 2 lugares | cálculo caro / pode não usar |

## Worked Example — Reduzir acoplamento de parâmetro
Objeto que envia 5 mensagens, cada uma repetindo `this`:
```java
Server s = new Server();
s.a(this); s.b(this); s.c(this); s.d(this); s.e(this);   // acoplamento alto
```
Como o mesmo dado passa em toda mensagem, substitua por uma referência no construtor:
```java
Server s = new Server(this);
s.a(); s.b(); s.c(); s.d(); s.e();                        // acoplamento reduzido
```
Regra: parâmetro repetido em muitos métodos → anexe permanentemente (campo). Um único parâmetro pontual, porém, acopla menos que uma referência permanente — use o mais fraco que serve.

## Anti-patterns
- **Estado variável quando todo objeto tem as mesmas chaves**: devia ser campos declarados.
- **Get/set triviais em excesso**: superam os métodos úteis, escondem onde o cálculo deveria estar.
- **Codificar tipo/escopo no nome** (`fCount`, `lCount`, notação húngara): redundante em Java; use métodos curtos + contexto.
- **Generalizar todo tipo declarado dogmaticamente**: inconsistência atrapalha mais que imprecisão.
- **Campo válido só enquanto um método está na pilha**: feio; use variável local ou objeto auxiliar.

## Key Takeaways
1. Estados similares juntos, diferentes separados; variáveis irmãs com mesmo tempo de vida.
2. Prefira estado comum a variável; parâmetro a referência permanente; ansiosa a preguiçosa — suba só quando justificado.
3. Nome = função; tipo e escopo vêm do contexto (métodos curtos).
4. Tipo declarado comunica *uso*, não implementação — mas consistência vence generalidade.
5. Dados que andam juntos em listas de parâmetros → objeto parâmetro (que vira lar de lógica).

## Connects To
- **Ch 3**: simetria (variáveis irmãs), ritmo de mudança (objeto parâmetro/`Money`).
- **Ch 5**: campo de estratégia/estado ↔ delegação; polimorfismo vs. flag.
- **Ch 7 (Comportamento)**: o outro lado — fluxo de controle.
- **Ch 8 (Métodos)**: métodos curtos e compostos tornam o contexto suficiente p/ nomes simples.
