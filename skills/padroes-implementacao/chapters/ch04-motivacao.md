# Capítulo 4: Motivação

## Core Idea
A economia é o condutor fundamental do projeto de software (Yourdon & Constantine, *Structured Design*). Escreve-se código para **reduzir o custo global**, e o custo de manutenção domina o custo de desenvolvimento — por isso o foco em comunicação compensa.

## Frameworks Introduced
- **Equação de custo do software**:
  - `custo_total = custo_inicial + custo_manutenção`
  - `custo_manutenção = custo_entender + custo_mudar + custo_testar + custo_implantar`
  - When to use: para justificar investir em legibilidade em vez de flexibilidade especulativa.
  - Insight: a parte cara da manutenção é **entender o código existente** — mudar é fácil quando se sabe o que mudar.
- **Dois princípios econômicos que punem o superinvestimento inicial**:
  - **Valor temporal do dinheiro**: um dólar hoje > um dólar amanhã → adie custos.
  - **Incerteza do futuro**: prefira benefício imediato a possível benefício de longo prazo.

## Key Concepts
- **Custo de manutenção > custo de desenvolvimento**: descoberta que surpreendeu a indústria.
- **Benefícios imediatos do código limpo**: menos defeitos, compartilhamento mais fácil, desenvolvimento mais suave.
- **Necessidades humanas**: orgulho do trabalho bem feito, ser membro confiável da comunidade — não só econômicas.

## Mental Models
- **Otimize para o entendimento futuro, agora**: durante o desenvolvimento, tenha em mente o custo de *entender* o código na manutenção.
- Padrões de implementação buscam benefício imediato *estabelecendo código limpo que facilita o futuro* — não sacrificam o hoje pelo amanhã.

## Worked Example — Curva de aprendizado dos padrões
Ao escrever *Smalltalk Best Practice Patterns*, Beck se impôs: nenhum caractere de código sem antes ter o padrão no papel.
- **Semana 1**: cada minuto de código precedido de 1 hora de escrita — frustrante, "dedos amarrados".
- **Semana 2**: maioria dos padrões básicos definidos; seguindo padrões existentes.
- **Semana 3**: codificava **muito mais rápido que antes** — estilo assimilado, sem tempo perdido em dúvidas.
Lição: internalizar um conjunto de padrões acelera a programação e reduz pensamento dispersivo.

## Anti-patterns
- **Superinvestir no design inicial para eliminar manutenção**: geralmente falha em reduzir custo global; prepara para necessidades que não chegam e atrapalha as inesperadas que chegam.
- **Preparação prematura para o futuro**: interfere nas mudanças reais que se revelam necessárias.

## Key Takeaways
1. Escreva para reduzir o custo *global*, dominado pela manutenção.
2. Entender é caro; mudar é barato — logo, otimize a legibilidade.
3. Adie custos e prefira benefícios imediatos (economia básica).
4. Projetos com pouca/nenhuma manutenção precisam de um conjunto de padrões *diferente* deste livro.

## Connects To
- **Ch 3**: "consequências locais" e "minimizar repetição" reduzem diretamente o custo de manutenção.
- **Ch 10**: frameworks têm prioridades econômicas distintas → padrões variam.
