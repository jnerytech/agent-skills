# Capítulo 10: Refatoração (Cap. 31)

## Core Idea
Refatorações usadas no TDD têm uma definição relaxada: preservam a semântica *com respeito aos testes que já passam* ("equivalência observacional"). Isso autoriza trocar constante por variável e chamar de refatoração — mas obriga você a ter testes suficientes.

## Frameworks Introduced
- **Reconciliar Diferenças (Reconcile Differences)**: para unificar dois trechos similares, aproxime-os gradualmente; só unifique quando *idênticos*. Vale para laços, ramos de condicional, métodos e classes.
- **Isolar Mudança (Isolate Change)**: para mudar parte de um método/objeto, primeiro *isole* a parte (metáfora cirúrgica). Formas: Extract Method, Extract Object, Method Object.
- **Migrar Dados (Migrate Data)**: para trocar de representação, duplique os dados temporariamente — adicione novo formato, popule junto, use, apague o antigo, exponha externamente.
- **Extrair Método (Extract Method)**: transforme parte de um método longo em método separado e chame-o.
- **Método em uma Linha (Inline Method)**: substitua a invocação pelo corpo do método — útil para "rebobinar" e ver o fluxo real.
- **Extrair Interface (Extract Interface)**: crie interface com as operações compartilhadas para introduzir uma segunda implementação.
- **Mover Método (Move Method)**: mova o método para a classe à qual pertence (gatilho: ver 2+ mensagens enviadas a outro objeto).
- **Objeto Método (Method Object)**: método complicado com muitos parâmetros/locais → vire um objeto com `run()`.
- **Adicionar Parâmetro / Parâmetro de Método → de Construtor**: passos de extensão e de migração de representação.

## Key Concepts
- **Equivalência observacional**: refatoração TDD preserva *os testes atuais*; "todos passaram" não é desculpa — escreva mais testes.
- **Refatoração com "salto de fé"**: longas cadeias de raciocínio são as que "aumentam sua calvície"; passos pequenos e feedback concreto as reduzem.
- **Trabalhar invertido**: para remover subclasses, pense no último passo trivial (subclasse vazia ⇒ superclasse a substitui) e trabalhe de trás para frente.

## Code Examples
```java
// Move Method: bounds recebe 4 mensagens -> mova o cálculo para Rectangle
// Shape (antes): width = bounds.right() - bounds.left(); ... area = width*height;
public int area() {                      // agora em Rectangle
    int width  = this.right() - this.left();
    int height = this.bottom() - this.top();
    return width * height;
}
// Shape (depois): int area = bounds.area();
```
- **What it demonstrates**: gatilho de Move Method = "mais de uma mensagem a outro objeto"; resultado costuma iluminar o projeto.

## Worked Example
**Migrar Dados em Um para Muitos** (do xUnit): `TestSuite` guardava um único `test`; queremos uma coleção. Duplica-se temporariamente:
```python
def __init__(self):  self.tests = []          # 1. novo formato
def add(self, test):
    self.test = test                          # antigo
    self.tests.append(test)                   # 2. popula os dois
def run(self, result):                        # 3. usa o novo (refatoração: só há 1 elemento)
    for test in self.tests: test.run(result)
def add(self, test): self.tests.append(test)  # 4. apaga o antigo
```
Enquanto há um só elemento na coleção, o passo 3 preserva a semântica — logo é uma refatoração legítima.

## Anti-patterns
- **Unificar trechos ainda diferentes**: só unifique quando absolutamente idênticos.
- **Extrair método com 5–6 temporárias arrastadas**: assinatura fica pior que o original; use Objeto Método para ganhar um namespace.
- **Refatoração saltada sem testes**: o salto de fé sem rede é exatamente o que TDD evita.

## Key Takeaways
1. No TDD, "refatoração" = preservar os testes que passam (equivalência observacional).
2. Aproxime trechos similares até serem idênticos antes de fundi-los.
3. Migrar Dados = duplicar a representação temporariamente.
4. Move Method dispara quando um método fala demais com outro objeto.
5. Inline Method é ferramenta de *exploração* do fluxo, não só de simplificação.

## Connects To
- **Ch 9**: estas refatorações introduzem Null Object, Composite, Pluggable, etc.
- **Ch 3 / Ch 7**: Migrar Dados e Isolar Mudança aparecem em One to Many.
- **Ch 6**: Extract Interface viabiliza Self Shunt em Java.
