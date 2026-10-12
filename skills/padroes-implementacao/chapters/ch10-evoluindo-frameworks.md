# Capítulo 10: Evoluindo Frameworks

## Core Idea
Frameworks **invertem a economia** dos capítulos anteriores: o custo dominante deixa de ser *entender* o código e passa a ser *atualizar o código do cliente* (que os desenvolvedores não controlam). Logo, **complexidade extra vale a pena** se preserva a liberdade de evoluir sem quebrar clientes. Simplicidade cai de prioridade; compatibilidade sobe.

## Frameworks Introduced
### Princípio central
- **Clientes devem depender do mínimo de detalhes, e dos menos suscetíveis a mudança.** Não dá p/ saber antecipadamente o que não vai mudar → jogue com probabilidades: revele pouco, revele o estável.
- No app: campos protegidos, código amplamente aplicável. No framework: campos **privados**, aplicabilidade sacrificada por liberdade de evolução.

### 3 (+1) estilos de uso (usabilidade ↓, flexibilidade/estabilidade ↑)
- **Instanciação** (`new ServerSocket()`): variação só nos *dados*. Mais simples.
- **Configuração** (`new TreeSet(comparator)`): cliente passa objetos chamados em momentos predeterminados; varia lógica+dados, mas poucas dimensões.
- **Implementação** (cliente estende classe / implementa interface do framework): qualquer nº de variações independentes via métodos gancho. Maior poder, **maior restrição futura** — cada detalhe exposto vira promessa.
- **Classe biblioteca** (métodos estáticos, `Collections`): mais à prova de futuro; só adiciona métodos novos. Limite: não conecta variação de lógica, estoura em nº de procedimentos.

### Abstração: Interface vs. Superclasse
- **Interface**: registra pouquíssimos detalhes; mas adicionar método quebra todos os implementadores (a menos que garanta que clientes só *usem*, não implementem). Frágil, mas idiomático em Java.
- **Superclasse**: pode especificar mais; adicionar operação **não** quebra clientes; mas herança única. Campos sempre privados + métodos essenciais protegidos → superclasse expõe quase tão pouco quanto interface, com mais ganchos.
- **Interface versionada** (`LayoutManager2`): estende sem quebrar, mas exige `instanceof` em runtime — compromisso, não solução p/ abstração que muda muito. Abstração mutável → superclasse.

### Criação (generalidade ↑, legibilidade ↓)
- **Sem criação**: proíbe cliente de instanciar (eventos SWT) — garante invariantes, mas bloqueia usos inesperados legítimos.
- **Construtor**: simples, mas promete nome, pacote, parâmetros e **classe concreta** p/ sempre.
- **Fábrica estática** (`ArrayList.create()`): libera nome/pacote/classe concreta; menos rastreável.
- **Objeto fábrica** (`Collections.factory().createArrayList()`): flexibilidade máxima, útil **localmente** (coleção que economiza espaço no mobile) e p/ famílias compatíveis (widgets Windows vs Linux).

### Gerência de atualização incompatível
- Passos pequenos: **depreciação** (mantém funcionando 1+ releases), **arquiteturas paralelas** (`Vector`/`Enumerator`), **pacotes novos** (só troca o `import`), mudar **API ou implementação, não ambas** por release, **ferramentas automáticas** de conversão (Eclipse 2.x→3.0).
- **Parâmetro padrão**: mantenha o método antigo delegando ao novo com valor default.

## Key Concepts
- **Retrocompatível** (clientes chamam métodos/objetos antigos) vs. **compatível com o futuro** (objetos novos funcionam como antigos). JUnit 4 ofereceu ambos → muito mais caro.
- **Pacotes `internal`** (`org.eclipse.jdt.internal...`): meio-termo — cliente escolhe o risco de depender do instável. Contorna a falha do Java de não ter "visível no framework, invisível a clientes".
- **`final`**: aplicado à classe força instanciação/configuração; ao método garante execução — mas frustra clientes (2 dias perdidos com eventos SWT finais). Reserve p/ ganho substancial + pouco prejuízo.

## Mental Models
- **Framework = interseção, não união** das funcionalidades úteis do domínio. 90% comum → cubra; 10% único → deixe o cliente estender. Framework p/ *todos* fica grande demais p/ *qualquer um*.
- **Derive de exemplos concretos**, não do caso geral (JUnit nasceu de repetir o mesmo teste muitas vezes).
- **Metáfora clara** (contabilidade de dupla entrada → cliente procura `Conta`, `Transação`) faz o framework fácil de entender/estender.

## Worked Example — Evitar vazamento via boolean
Widget com setter que vaza "só há 2 estados":
```java
setVisible(boolean);   // e quando surge o 3º estado "inativo"?
```
**Superclasse** — publique intenção; adicionar `inactive()` não quebra clientes:
```java
visible(); invisible();   // + inactive() depois, sem quebrar
```
**Interface** — `inactive()` quebraria implementadores; use enum:
```java
enum State { VISIBLE, INVISIBLE, INACTIVE }
setVisible(State);   // liberdade p/ novos estados
```
Parâmetro padrão mantém método antigo vivo:
```java
public TestResult run(Class... classes) {          // antigo, ainda funciona
  TestResult result = new TestResult();
  run(result, classes);
  return result;
}
public void run(TestResult result, Class... classes) { ... }  // novo
```

## Anti-patterns
- **Campos protegidos/públicos no framework**: travam a representação de dados. Torne-os privados + getters.
- **Get/set que vazam estrutura interna**: setters piores que getters — publique método nomeado pelo *problema*, não pela implementação.
- **`final` gratuito**: frustra clientes com usos legítimos.
- **Framework-união que resolve tudo**: difícil de aprender p/ todos.
- **Começar do caso geral**: derive de exemplos concretos.

## Key Takeaways
1. Economia invertida: custo = atualizar clientes → aceite complexidade que preserva evolução.
2. Exponha o mínimo, e o mais estável; campos privados sempre.
3. Escolha estilo de uso pelo poder necessário (instanciação < configuração < implementação).
4. Abstração mutável → superclasse; estável → interface (com versionamento se preciso).
5. Framework = interseção; derive de exemplos; ancore em metáfora clara.

## Connects To
- **Ch 5**: interface vs. classe abstrata, interface versionada, seletor de estilo de variação.
- **Ch 8**: método fábrica, construtor completo, get/set nomeados por intenção.
- **Ch 3-4**: aqui a hierarquia de valores muda (compatibilidade > simplicidade).
