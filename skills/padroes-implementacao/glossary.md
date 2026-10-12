# Glossário — Padrões de Implementação

**Ação a distância** — A depende da representação interna de B; mudar B quebra A. Mova lógica e dados juntos (Ch 8).
**Acesso direto** — ler/gravar variável diretamente (`x=10`): claro, rígido (Ch 6).
**Acesso indireto** — acesso via getter/setter: flexível, menos claro; necessário p/ dados acoplados (Ch 6).
**Cláusula de guarda** — retorno prematuro p/ situação excepcional local, evita `if/else` aninhado (Ch 7).
**Comportamento específico de instância** — instâncias da mesma classe com lógica diferente; atribua na criação (Ch 5).
**Comunicação** — valor: código que o leitor entende, modifica ou usa (Ch 3).
**Condicional** — `if`/`switch` p/ variação; simples e local, mas proliferação reduz confiabilidade (Ch 5).
**Configuração** — estilo de uso de framework: cliente passa objetos chamados em momentos fixos (Ch 10).
**Consequências locais** — princípio-raiz: mudança aqui não afeta lá (Ch 3).
**Construtor completo** — retorna objeto pronto p/ computar; comunica parâmetros obrigatórios (Ch 8).
**Construtor de conversão** — `new File(String)`: converte no objeto destino; p/ muitas conversões (Ch 8).
**Delegação** — variação delegada a um objeto; permite troca em runtime (Ch 5).
**Envio duplo (double dispatch)** — duas mensagens de escolha em cascata p/ 2 dimensões (Ch 7).
**Especialização** — comunicar similaridades/diferenças de computações relacionadas (Ch 5).
**Estado comum** — dados como campos declarados; todo objeto tem os mesmos (Ch 6).
**Estado extrínseco** — estado de propósito especial guardado fora do objeto, num `IdentityMap` (Ch 6).
**Estado variável** — dados como `Map`; diferem por instância; comunica mal (Ch 6).
**Expressão declarativa** — expressar intenção sem seguir fluxo (`@RunWith` vs. `suite()`) (Ch 3).
**Fábrica interna** — método que cria/retorna objeto auxiliar complexo (Ch 8).
**Flexibilidade** — valor: só onde o programa muda; melhor de simplicidade+testes (Ch 3).
**Fluxo excepcional** — caminhos raros; expresse sem obscurecer o fluxo principal (Ch 7).
**Fluxo principal** — o trajeto lido/mudado com mais frequência; dê a ele o poder expressivo (Ch 7).
**Interface (abstrata)** — conjunto de operações sem implementação (interface Java ou superclasse) (Ch 5).
**Interface versionada** — subinterface que estende uma interface travada (`ReversibleCommand`) (Ch 5, 10).
**Lógica e dados em harmonia** — mantenha próximos; a mudança fica local (Ch 3).
**Mensagem** — mecanismo de fluxo; cada uma é ponto potencial de variação (Ch 7).
**Mensagem de decomposição** — decomposição funcional pura via submensagem nomeada (Ch 7).
**Mensagem de escolha** — mensagem polimórfica escolhe implementação em runtime (Ch 7).
**Mensagem explicativa** — mensagem com nome do problema que chama outra com nome da solução (Ch 7).
**Mensagem inversa** — todas as mensagens ao mesmo recebedor (`this`) p/ revelar simetria (Ch 7).
**Método composto** — método feito de chamadas no mesmo nível de abstração (Ch 8).
**Método de conversão** — `polar.asCartesian()`: converte no objeto fonte; poucas conversões (Ch 8).
**Método fábrica** — estático; retorna tipo abstrato, nome por intenção (Ch 8).
**Minimizar repetição** — código repetido espalha consequências da mudança (Ch 3).
**Motivação (econômica)** — custo total dominado pela manutenção → foco em comunicação (Ch 4).
**Nome revelador de intenção** — nomeie método pelo propósito do invocador, não implementação (Ch 8).
**Nome simples de superclasse** — raiz de hierarquia: nome curto de metáfora forte (`Figura`) (Ch 5).
**Nome sugestivo de função** — nomeie variável pela função, não pelo tipo (Ch 6).
**Objeto método** — método longo vira classe própria; refatoração fica trivial (Ch 8).
**Objeto parâmetro** — grupo de parâmetros vira objeto; vira lar de lógica (Ch 6).
**Objeto valor** — objeto imutável que age como valor matemático (Ch 5).
**Padrão de implementação** — decisão recorrente de codificação + suas forças recorrentes (Ch 1, 2).
**Padrão de forças** — as restrições recorrentes que definem um padrão (Ch 2).
**Parâmetro coletor** — objeto passado p/ coletar resultados de várias invocações (Ch 6).
**Princípio** — ponte entre valores (universais) e padrões (específicos) (Ch 3).
**Propagação de exceção** — embrulhe exceção de baixo nível na de alto nível (Ch 7).
**Ritmo de mudança** — una o que muda junto, separe o que muda em ritmos diferentes (simetria temporal) (Ch 3).
**Seletor plugável** — nome de método em campo, invocado por reflexão; custo alto (Ch 5).
**Simetria** — mesma ideia expressa da mesma forma em todo lugar (Ch 3).
**Simplicidade** — valor: eliminar complexidade em excesso, não a essencial (Ch 3).
**Subclasse** — "como aquele, exceto por..."; variação unidimensional, fixa na criação (Ch 5).
**Tipo declarado** — declare como a variável é usada, não como é implementada (Ch 6).
**Valor** — tema universal da programação: comunicação, simplicidade, flexibilidade (Ch 3).
**Var args** — nº variável de argumentos (`method(Class...)`); deve ser o último (Ch 6).
**Variação de número** — 0/1/muitos; expressa por coleções (Ch 9).
**Visibilidade de método** — público/pacote/protegido/privado; limite ao máximo, revele aos poucos (Ch 8).
