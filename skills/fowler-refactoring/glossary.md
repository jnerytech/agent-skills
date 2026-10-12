# Glossário — Refatoração (Fowler, 2ª ed.)

Termos conceituais. Para o catálogo completo de refatorações veja [patterns.md](patterns.md); para regras de decisão, [cheatsheet.md](cheatsheet.md).

**Alteração divergente (Divergent Change)** — um módulo é alterado por razões diferentes e independentes; sinal de baixa coesão (Ch 3).

**Cadeias de mensagens (Message Chains)** — cliente navega `a.b().c().d()`, acoplando-se à estrutura de navegação (Ch 3).

**Campo temporário (Temporary Field)** — atributo só preenchido em certas circunstâncias; confunde o leitor (Ch 3).

**Cirurgia com rifle (Shotgun Surgery)** — uma mudança exige editar muitos módulos; oposto de Alteração divergente (Ch 3).

**Cláusula de guarda (Guard Clause)** — verificação no início da função que retorna cedo em caso excepcional, evitando aninhamento (Ch 10).

**Código autotestável (Self-testing code)** — base com suíte de testes automatizados que dá confiança para refatorar; pré-requisito da refatoração (Ch 4).

**Comportamento observável** — o que o programa faz do ponto de vista externo; a refatoração o preserva. Interfaces e desempenho podem mudar; comportamento visível ao usuário, não (Ch 2).

**Dois chapéus (Two Hats)** — metáfora de Kent Beck: em cada momento você ou *acrescenta funcionalidade* ou *refatora*, nunca as duas ao mesmo tempo (Ch 2).

**Cheiro / Mau cheiro (Code Smell)** — heurística que indica *onde* e *quando* refatorar; não um erro, mas um sinal (Ch 3).

**Encapsulamento** — ocultar detalhes internos de um módulo, controlando acesso a dados e estrutura (Ch 7).

**Fixture** — estado/objetos comuns preparados antes de cada teste, tipicamente em `beforeEach` (Ch 4).

**Generalidade especulativa (Speculative Generality)** — abstração criada para necessidade futura hipotética que nunca chega (Ch 3).

**Herança recusada (Refused Bequest)** — subclasse herda dados/métodos que não quer nem usa; candidata a delegação (Ch 3, Ch 12).

**Inveja de recursos (Feature Envy)** — método interessa-se mais pelos dados de outra classe que pela sua própria (Ch 3).

**Intermediário (Middle Man)** — classe que só delega para outra; considere Remover intermediário (Ch 3, Ch 7).

**Mecânica / Procedimento** — sequência de passos pequenos e verificáveis de uma refatoração; testar entre passos (Ch 5).

**Obsessão por primitivos (Primitive Obsession)** — usar tipos primitivos onde um pequeno objeto de valor serviria melhor (Ch 3).

**Refatoração (substantivo)** — modificação na estrutura interna do software para deixá-lo mais fácil de entender e barato de alterar, **sem** mudar o comportamento observável (Ch 2).

**Refatorar (verbo)** — reestruturar via uma série de refatorações, sem alterar o comportamento observável (Ch 2).

**Refatoração oportunista** — limpar o código "de passagem" enquanto se faz outra coisa (regra do escoteiro) (Ch 2).

**Refatoração preparatória (Preparatory Refactoring)** — reestruturar primeiro para tornar a próxima funcionalidade fácil de adicionar (Ch 2).

**Refatoração para compreensão (Comprehension Refactoring)** — refatorar para entender um trecho, gravando o entendimento no código (Ch 2).

**Reestruturação (Restructuring)** — termo genérico para qualquer reorganização de código; refatoração é um tipo específico (passos que preservam comportamento) (Ch 2).

**Regra de Três (Rule of Three)** — na terceira vez que algo se repete, refatore/elimine a duplicação (Ch 2).

**Regra do escoteiro** — deixe o código um pouco melhor do que o encontrou (Ch 2).

**Sondar limites (Boundary conditions)** — testar casos extremos: vazio, zero, negativo, nulo (Ch 4).

**Switches repetidos (Repeated Switches)** — o mesmo `switch`/condicional sobre tipo espalhado; candidato a polimorfismo (Ch 3, Ch 10).

**Trocas escusas / Insider Trading** — módulos que trocam dados privados demais entre si; alto acoplamento (Ch 3).

**Yagni (You Aren't Going to Need It)** — não construa flexibilidade especulativa; adicione quando a necessidade real surgir (Ch 2).
