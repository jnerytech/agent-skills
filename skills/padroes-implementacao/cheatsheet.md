# Cheatsheet — Padrões de Implementação (Kent Beck)

## A pergunta-mãe
**"Um futuro leitor entenderá minha intenção aqui?"** Se não, o padrão está errado. Programar = comunicar com humanos.

## Hierarquia de decisão (valores em conflito)
- App: **Comunicação > Simplicidade > Flexibilidade**. Flexibilidade só onde o código muda de fato.
- Framework: **Compatibilidade > Simplicidade**. Aceite complexidade que preserva evolução.
- Simplificação prejudica leitura? → escolha **comunicação** (raro; sinaliza simplificação maior invisível).

## Expressar variação de LÓGICA (escolha por custo crescente)
| Situação | Use |
|---|---|
| Poucos ramos, estáveis, tudo numa classe | Condicional |
| Variação unidimensional fixa na criação | Subclasse |
| Comportamento muda em runtime | **Delegação** |
| 1-2 métodos, problema difícil isolado | Seletor plugável |
| Sobrescrever 1-2 métodos inline, API simples | Classe interna anônima |
| 2 dimensões independentes | Envio duplo (não triplo) |

## Expressar variação de DADOS
- 0 = ausência de campo · 1 = campo · **muitos = coleção**.
- Dado comum a todo objeto → **estado comum** (campos). Difere por instância → estado variável (`Map`). Só um subsistema quer → estado extrínseco.

## Fluxo de controle — ordem de preferência
`sequência → mensagem → iteração → condicional → exceção`. Exceção só quando o resto confundiria. Guarda > `if/else` aninhado.

## Onde guardar / como acessar
- **Acesso**: direto dentro da classe, indireto p/ clientes.
- Muitos get/set públicos = **lógica no lugar errado** → mova lógica p/ perto dos dados.
- Parâmetro repetido em N métodos → vire campo. Parâmetro pontual acopla menos que referência permanente.

## Nomeação
- Classe: **nome primeiro** (âncora), 1 palavra, metáfora forte, na raiz.
- Método: pela **intenção do invocador** (`find`, não `linearSearch`). Conta uma história no código chamador.
- Variável: pela **função**; tipo e escopo vêm do contexto (métodos curtos). Não abrevie, não codifique tipo no nome.

## Tamanho de método
- Grande → orienta (navegação); pequeno → detalhe. **Método composto** (mesmo nível de abstração) resolve os dois.
- Perf de métodos pequenos ≈ irrelevante (20-30% micro-bench). **Fatos antes de estrutura**: funcione, depois componha. Piorou? Alinhe num método gigante e reparticione.

## Criação
| Precisa | Use |
|---|---|
| Comunicar obrigatórios | Construtor completo (afunile no mestre) |
| Tipo abstrato / cache / lógica extra | Método fábrica |
| Conversão poucas/similares | `fonte.asDestino()` |
| Conversão muitas | `new Destino(fonte)` |

## Coleções — desempenho
- Default: **ArrayList**. `contains` gargalo → **HashSet** (se sem duplicatas importa).
- add/remove pesado → **LinkedList**. Ordenado → TreeSet/TreeMap (log n). Ordem de inserção → LinkedHash*.
- Regra: **simples primeiro, meça, especialize, concentre a decisão, pare.** Perf viola consequências locais (efeito distante).
- **Delegue** a coleção; não `extends ArrayList`.

## Interface vs. Classe abstrata
- Interface estável, múltiplas visões → **interface Java** (mas crescer quebra implementadores).
- Interface **vai crescer** → **classe abstrata** (nova operação c/ default não quebra). Herança única.

## Framework — inverte a economia
- Custo = **atualizar clientes**, não entender código.
- Exponha **o mínimo e o mais estável**; campos **privados**.
- Estilo de uso: instanciação < configuração < implementação (poder ↑, liberdade ↓).
- Boolean que vaza "só 2 estados" → **enum** + método de intenção (`visible()`, não `setVisible(true)`).
- Evoluir sem quebrar: parâmetro padrão, depreciação, arquiteturas paralelas, pacotes `internal`.
- **Framework = interseção** das necessidades comuns (90%), não união. Derive de exemplos concretos + metáfora clara.

## Tells & smells
- Comentário numa linha → **mensagem explicativa**.
- Muitas variáveis com prefixo comum → **objeto auxiliar**.
- Hierarquias paralelas → duplicação; mova a variação p/ um objeto.
- Mistura de níveis de abstração num método → "o que é aquilo enroscado ali?".
- `if (x.isVisible()) x.doA()` → método perdido; mova p/ `x`.
- Abuso de cópia de segurança → protocolo pobre (o problema real).

## Princípios (todos corolários de Consequências Locais)
Minimizar repetição · Lógica e dados em harmonia · Simetria · Expressão declarativa · Ritmo de mudança.
