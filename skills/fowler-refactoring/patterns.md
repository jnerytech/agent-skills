# Catálogo de refatorações — Fowler 2ª ed. (61 refatorações)

Cada verbete: **Nome PT (English)** — quando usar → mecânica em uma frase. Detalhe e código nos capítulos linkados.

## Ch 6 — Primeiro conjunto (as mais usadas)
- **Extrair função (Extract Function)** — trecho tem propósito próprio → mova para função nomeada pela *intenção*; passe variáveis usadas como parâmetros.
- **Internalizar função (Inline Function)** — corpo tão claro quanto o nome → substitua chamadas pelo corpo. Inversa de Extract.
- **Extrair variável (Extract Variable)** — expressão complexa → nomeie subexpressões em variáveis explicativas.
- **Internalizar variável (Inline Variable)** — nome não diz mais que a expressão → remova a variável. Inversa de Extract.
- **Mudar declaração de função (Change Function Declaration)** — nome/parâmetros ruins → renomeie ou altere assinatura; use *procedimento de migração* (assinatura nova coexiste) quando houver muitos chamadores.
- **Encapsular variável (Encapsulate Variable)** — dado com alcance amplo → envolva em funções get/set para controlar acesso.
- **Renomear variável (Rename Variable)** — nome obscuro → renomeie (encapsule antes se for muito usada).
- **Introduzir objeto de parâmetros (Introduce Parameter Object)** — grupo de parâmetros anda junto → agrupe em objeto/estrutura.
- **Combinar funções em classe (Combine Functions into Class)** — funções operam sobre o mesmo dado → agrupe numa classe.
- **Combinar funções em transformação (Combine Functions into Transform)** — deriva vários valores do mesmo dado → função de transformação que enriquece o registro.
- **Separar em fases (Split Phase)** — código faz duas coisas em sequência → separe em fases distintas (ex.: parse → calcular).

## Ch 7 — Encapsulamento
- **Encapsular registro (Encapsulate Record)** — registro mutável exposto → troque por classe com acessadores.
- **Encapsular coleção (Encapsulate Collection)** — getter devolve coleção crua → devolva cópia/só-leitura; forneça add/remove.
- **Substituir primitivo por objeto (Replace Primitive with Object)** — primitivo ganhou comportamento/validação → crie objeto de valor.
- **Substituir variável temporária por consulta (Replace Temp with Query)** — temp guarda resultado de expressão → extraia para método de consulta.
- **Extrair classe (Extract Class)** — classe faz trabalho de duas → separe responsabilidades em nova classe.
- **Internalizar classe (Inline Class)** — classe não faz mais o suficiente → funda-a em outra. Inversa de Extract Class.
- **Ocultar delegação (Hide Delegate)** — cliente navega servidor→delegado → crie método que oculta a delegação.
- **Remover intermediário (Remove Middle Man)** — classe só delega → deixe o cliente chamar o delegado direto. Inversa de Hide Delegate.
- **Substituir algoritmo (Substitute Algorithm)** — existe forma mais clara → troque o corpo por outro algoritmo.

## Ch 8 — Movendo recursos
- **Mover função (Move Function)** — função usa mais outro contexto → mova para onde pertence.
- **Mover campo (Move Field)** — campo é mais usado por outra classe → mova-o.
- **Mover instruções para uma função (Move Statements into Function)** — mesmas linhas antes de toda chamada → mova para dentro.
- **Mover instruções para os chamadores (Move Statements to Callers)** — comportamento diverge entre chamadores → suba as linhas para os pontos de chamada.
- **Substituir código internalizado por chamada de função (Replace Inline Code with Function Call)** — código replica função existente → chame a função.
- **Deslocar instruções (Slide Statements)** — código relacionado disperso → aproxime declaração do uso.
- **Dividir laço (Split Loop)** — um laço faz duas coisas → dois laços, cada um com um propósito.
- **Substituir laço por pipeline (Replace Loop with Pipeline)** — laço itera/filtra/transforma → use `filter`/`map`/`reduce`.
- **Remover código morto (Remove Dead Code)** — código nunca executado → apague (o histórico guarda).

## Ch 9 — Organizando dados
- **Separar variável (Split Variable)** — variável recebe valor para dois fins → uma variável por responsabilidade.
- **Renomear campo (Rename Field)** — nome de campo obscuro → renomeie (encapsule antes).
- **Substituir variável derivada por consulta (Replace Derived Variable with Query)** — dado derivado mutável → calcule sob demanda.
- **Mudar referência para valor (Change Reference to Value)** — subobjeto pequeno e imutável → trate como objeto de valor (compare por valor).
- **Mudar valor para referência (Change Value to Reference)** — cópias que deveriam compartilhar estado → use referência única.

## Ch 10 — Simplificando condicionais
- **Decompor condicional (Decompose Conditional)** — if/then/else complexo → extraia condição e ramos em funções nomeadas.
- **Consolidar expressão condicional (Consolidate Conditional Expression)** — vários testes, mesmo resultado → combine em um, extraia para função.
- **Substituir condicional aninhada por cláusulas de guarda (Replace Nested Conditional with Guard Clauses)** — aninhamento profundo → retornos antecipados para casos excepcionais.
- **Substituir condicional por polimorfismo (Replace Conditional with Polymorphism)** — switch sobre tipo repetido → uma subclasse por caso.
- **Introduzir caso especial (Introduce Special Case / Null Object)** — muitos clientes tratam o mesmo valor especial → crie objeto de caso especial.
- **Introduzir asserção (Introduce Assertion)** — suposição implícita → torne-a explícita com asserção.

## Ch 11 — Refatorando APIs
- **Separar consulta de modificador (Separate Query from Modifier)** — função retorna valor E causa efeito colateral → divida em duas (CQS).
- **Parametrizar função (Parameterize Function)** — funções quase idênticas diferindo em literais → um parâmetro.
- **Remover argumento de flag (Remove Flag Argument)** — booleano seleciona comportamento → funções explícitas separadas.
- **Preservar objeto inteiro (Preserve Whole Object)** — extrai vários valores para passar → passe o objeto inteiro.
- **Substituir parâmetro por consulta (Replace Parameter with Query)** — parâmetro derivável de outro → remova-o, consulte internamente.
- **Substituir consulta por parâmetro (Replace Query with Parameter)** — dependência interna incômoda → receba por parâmetro (empurra decisão ao chamador).
- **Remover método de escrita/setter (Remove Setting Method)** — campo só deveria ser fixado na criação → remova o setter.
- **Substituir construtor por função de factory (Replace Constructor with Factory Function)** — construtor limita nome/subtipo → use factory.
- **Substituir função por comando (Replace Function with Command)** — função complexa precisa de estado/desfazer → objeto-comando.
- **Substituir comando por função (Replace Command with Function)** — comando é simples demais → volte a ser função. Inversa.

## Ch 12 — Herança
- **Subir método (Pull Up Method)** — método idêntico em subclasses → mova para a superclasse.
- **Subir campo (Pull Up Field)** — campo repetido em subclasses → suba-o.
- **Subir corpo do construtor (Pull Up Constructor Body)** — construtores de subclasse compartilham código → suba para o super.
- **Descer método (Push Down Method)** — método só interessa a uma subclasse → desça-o.
- **Descer campo (Push Down Field)** — campo usado por uma subclasse só → desça-o.
- **Substituir código de tipos por subclasses (Replace Type Code with Subclasses)** — campo de tipo dirige comportamento → subclasses por tipo.
- **Remover subclasse (Remove Subclass)** — subclasse faz pouco → troque por campo na superclasse. Inversa.
- **Extrair superclasse (Extract Superclass)** — duas classes com partes comuns → superclasse com o comum.
- **Condensar hierarquia (Collapse Hierarchy)** — super e subclasse quase iguais → funda-as.
- **Substituir subclasse por delegação (Replace Subclass with Delegate)** — herança rígida/recusada → delegue a um objeto (favoreça composição).
- **Substituir superclasse por delegação (Replace Superclass with Delegate)** — herança viola "é-um" → delegue à ex-superclasse.
