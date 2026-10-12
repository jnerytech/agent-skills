# Capítulo 16: Estratégia de Desenvolvimento

## Core Idea
Desvio radical da sabedoria convencional: **crie hoje a solução para os problemas de hoje** e
confie que resolverá os de amanhã quando chegarem. A estratégia amarra três práticas —
integração contínua, propriedade coletiva e programação em pares.

## Frameworks Introduced
- **Integração contínua**: nenhum código fica não-integrado por mais de algumas horas (no
  máximo um dia). Ao fim de cada episódio, integra-se com a última entrega e **todos** os
  testes executam a 100%.
  - Por que não "instantânea": você quer fingir que é o único programador enquanto desenvolve;
    integrar a cada poucas horas dá os benefícios de "programador único" + "integração instantânea".
- **Propriedade coletiva**: qualquer um muda qualquer trecho a qualquer hora. Só funciona com
  **testes** + integração de poucas horas por vez.
  - Efeitos: código complexo não sobrevive (alguém o encontra e simplifica); previne complexidade
    (você sabe que outro verá seu código); espalha conhecimento; aumenta a sensação de poder pessoal.
- **Programação em pares**: dois papéis — quem digita pensa no *como* deste método; o outro
  pensa estratégico (essa abordagem funciona? que testes faltam? dá para simplificar o todo?).

## Key Concepts
- **Episódio de desenvolvimento como ritmo**: aprenda/teste/codifique/entregue — "é quase como respirar".
- **Refatoração constante quebra o sistema em objetos/métodos pequenos** → minimiza colisões de integração.
- **Par ≠ tutoria, ≠ assistir, ≠ gêmeos siameses**: é diálogo em vários níveis, com troca livre de parceiros (geralmente 2x/dia).
- **Difusão de conhecimento (analogia do tanque)**: informação nova é gota de corante; trocar pares a espalha por todo o time, enriquecida.

## Mental Models
- Sob estresse, as pessoas regridem (param de testar, refatorar, integrar). **O parceiro ao lado** é o que mantém as práticas vivas.
- "Assistir alguém programar é tão interessante quanto ver grama morrer no deserto" — par é colaboração ativa, não plateia.

## Anti-patterns
- **Integrar só de tempos em tempos**: conflitos crescem, custo de integração dispara, bugs ficam dias escondidos.
- **Propriedade individual**: códigos complexos sobrevivem; conhecimento fica refém de uma pessoa.
- **Parear como tutoria permanente**: em meses a diferença sênior/júnior deve diminuir, com o júnior digitando mais.

## Worked Example
Por que a programação em pares funciona para a XP? O **primeiro valor é comunicação**, e
poucas formas são mais intensas que face a face. Mesmo que não fosse mais produtiva (o autor
afirma que é), você ainda quereria parear pela **qualidade**: enquanto um digita, o outro
pensa estrategicamente — "essa linha de desenvolvimento é válida? leva a um beco sem saída?
há oportunidade de refatorar?". E sob estresse, o parceiro impede que você abandone testes,
refatoração e integração. Quem se recusa a parear: aprende a trabalhar como o time, ou procura
trabalho fora — mas comece aos poucos, uma hora por vez.

## Key Takeaways
1. Resolva os problemas de **hoje**; confie em resolver os de amanhã quando chegarem.
2. Integre a cada poucas horas, com 100% dos testes passando.
3. Propriedade coletiva só funciona com testes + integração curta — e mata código complexo.
4. No par: um digita (tático), o outro pensa (estratégico); trocas frequentes espalham conhecimento.
5. O par é a "rede de segurança social" que mantém as outras práticas vivas sob pressão.

## Connects To
- **Ch 13 (Testes)**: propriedade coletiva e integração contínua dependem de testes a 100%.
- **Ch 12 (Projeto)**: refatoração constante é o que torna a integração barata.
- **Ch 7 (Sinergia)**: aqui se vê na prática o reforço mútuo das práticas de desenvolvimento.
