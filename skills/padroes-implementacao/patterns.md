# Padrões — Padrões de Implementação (catálogo)

Técnicas concretas do livro, agrupadas por capítulo. Formato: **quando** / **como** / **trade-off**.

## Classe (Ch 5)
## Nome simples de superclasse
**Quando**: nomear raiz de hierarquia. **Como**: uma palavra, metáfora forte. **Trade-off**: consome o melhor nome antes das subclasses.

## Objeto valor
**Quando**: dados que agem como valor matemático (imutável). **Como**: todo estado no construtor, operações retornam novos objetos. **Trade-off**: sobrecarga de alocação; delimitar fronteira estado↔valor.

## Subclasse vs. Delegação vs. Condicional
**Quando**: expressar variação de lógica. **Como**: condicional (poucos ramos estáveis) → subclasse (variação fixa unidimensional) → delegação (troca em runtime). **Trade-off**: custo de leitura sobe; só delegação/condicional mudam em runtime.

## Interface versionada
**Quando**: estender interface travada. **Como**: subinterface `extends` + `instanceof`/cast. **Trade-off**: feio; muitas variantes = repensar projeto.

## Classe biblioteca → objeto
**Quando**: funcionalidade sem objeto natural. **Como**: métodos estáticos; converta a instância incrementalmente (delegue estático→instância→construtor). **Trade-off**: não escala (perde namespace privado).

## Estado (Ch 6)
## Estado comum vs. variável
**Quando**: guardar dados. **Como**: campos declarados (comum) vs. `Map` (variável). **Trade-off**: comum comunica bem/rígido; variável flexível/opaco.

## Objeto parâmetro
**Quando**: grupo de parâmetros anda junto em muitos métodos. **Como**: classe com esses campos; mova a lógica que só os usa. **Trade-off**: alocação (raramente problema); vira lar de lógica.

## Parâmetro coletor
**Quando**: mesclar resultados de várias invocações. **Como**: passe objeto acumulador (`List`, `TestResult`). **Trade-off**: acopla via parâmetro (fraco).

## Inicialização ansiosa vs. preguiçosa
**Quando**: pôr variável em estado conhecido. **Como**: declaração/construtor (ansiosa) vs. getter no 1º uso (preguiçosa). **Trade-off**: preguiçosa = 2 lugares p/ ler; use p/ cálculo caro/opcional.

## Comportamento (Ch 7)
## Mensagem de escolha
**Quando**: escolher implementação em runtime. **Como**: mensagem polimórfica (`brush.display(x)`). **Trade-off**: navegação entre classes; não crie sem variação real.

## Envio duplo
**Quando**: 2 dimensões independentes de variação. **Como**: 2 mensagens de escolha em cascata. **Trade-off**: duplicação; dimensão estável recebe a 2ª mensagem. Triplo+ não vale.

## Cláusula de guarda
**Quando**: pré-requisito/situação excepcional local. **Como**: `if (cond) return;` no topo; `continue` em laço. **Trade-off**: viola dogma "uma saída" (obsoleto em Java).

## Exceção
**Quando**: salto que cruza níveis da pilha. **Como**: lance no ponto de descoberta, capture onde tratável; embrulhe baixo→alto nível. **Trade-off**: vazamento no projeto; use só quando condicional confundiria.

## Métodos (Ch 8)
## Método composto + auxiliar
**Quando**: dividir lógica. **Como**: chamadas no mesmo nível de abstração; auxiliares privados escondem detalhe. **Trade-off**: perf de método pequeno é ~irrelevante (20-30% em micro-bench).

## Objeto método
**Quando**: método longo, muitos parâmetros/temporárias. **Como**: 6 passos — classe→campos→construtor→copiar p/ `calculate()`→substituir corpo→colher campos. **Trade-off**: só depois de funcionar; alinhe submétodos antes.

## Construtor completo / Método fábrica
**Quando**: criar objeto. **Como**: construtor mestre que afunila (obrigatórios explícitos) vs. fábrica estática (tipo abstrato, lógica extra). **Trade-off**: fábrica adiciona indireção; use só quando faz mais que criar.

## Método de conversão vs. Construtor de conversão
**Quando**: converter tipos. **Como**: `fonte.asDestino()` (poucas, similares) vs. `new Destino(fonte)` (muitas). **Trade-off**: método incha a fonte + dependência; construtor preferido.

## Método acessador de coleção
**Quando**: expor coleção interna. **Como**: `addX()`/`count()`/iterador que barra `remove()`; **não** retorne crua nem `unmodifiableList`. **Trade-off**: duplicar protocolo = objeto devia agir mais.

## Método booleano / de consulta / igualdade
**Quando**: protocolo booleano / decisão / comparação. **Como**: `valid()`/`invalid()` p/ constantes; prefixo `is`/`has`; `equals()`+`hashCode()` juntos com mesmos dados. **Trade-off**: get/set públicos vazam implementação.

## Coleções (Ch 9)
## Escolha de coleção
**Quando**: expressar variação de número. **Como**: interface geral na declaração (ordem/unicidade/chave), implementação específica; simples primeiro, especialize sob medição. **Trade-off**: consistência > generalidade; desempenho viola consequências locais.

## Delegar a coleção (não herdar)
**Quando**: objeto que contém coleção. **Como**: campo `Collection`, exponha só operações com nome significativo. **Trade-off**: só estenda p/ coleção de uso geral.

## Frameworks (Ch 10)
## Estilos de uso
**Quando**: expor framework. **Como**: instanciação (dados) < configuração (objetos passados) < implementação (subclasse/interface) < classe biblioteca (à prova de futuro). **Trade-off**: poder ↑ = liberdade de evolução ↓.

## Interface vs. Superclasse (framework)
**Quando**: definir abstração. **Como**: interface (estável) / superclasse com campos privados (mutável, +ganchos). **Trade-off**: interface quebra implementadores ao crescer; superclasse = herança única.

## Criação de framework
**Quando**: cliente instancia. **Como**: sem criação / construtor (estável) / fábrica estática ou objeto (mutável). **Trade-off**: generalidade ↑ = legibilidade ↓.

## Parâmetro padrão + arquiteturas paralelas
**Quando**: evoluir sem quebrar clientes. **Como**: mantenha método antigo delegando com default; deprecie; pacotes `internal`; enum em vez de boolean que vaza. **Trade-off**: complexidade extra vale no framework.
