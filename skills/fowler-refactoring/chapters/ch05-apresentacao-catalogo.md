# Capítulo 5: Apresentação do catálogo

## Ideia central
O restante do livro é um catálogo de refatorações, nascido das anotações pessoais do autor para lembrar como fazer refatorações de modo seguro e eficaz. Este capítulo explica o formato padrão usado para descrever cada refatoração do catálogo e como o leitor deve usá-lo — mais como referência de consulta do que como leitura corrida.

## Frameworks introduzidos
- **Formato de verbete do catálogo**: Nome (+ aliases) → Esboço (sketch/diagrama) → Motivação → Procedimento/Mecânica (passo a passo) → Exemplos

## Conceitos-chave
- **Nome da refatoração**: é o vocabulário comum usado no resto do livro; nomes diferentes (aliases) atuais também são listados, pois o mesmo refatoramento pode circular sob rótulos distintos.
- **Esboço (sketch)**: um pequeno exemplo de código antes/depois, mais um diagrama. Não serve para explicar ou ensinar a refatoração — serve para *lembrar* rapidamente dela caso o leitor já a conheça. Se for a primeira vez, é preciso ler o exemplo completo.
- **Motivação**: descreve por que fazer a refatoração e, igualmente importante, as circunstâncias em que ela *não* deve ser feita.
- **Procedimento/Mecânica**: descrição concisa e passo a passo, escrita como anotação pessoal do autor para relembrar refatorações pouco usadas recentemente. É deliberadamente enxuta (pouca explicação do "porquê" — isso fica no exemplo) e projetada para que cada passo seja o menor possível, enfatizando segurança: passos pequenos, testar após cada passo. Na prática, o autor costuma dar passos maiores, mas recua para os passos miúdos ao esbarrar em um bug. Os passos incluem referências a casos especiais, funcionando também como checklist. O procedimento listado não é a única forma de fazer a refatoração — é a que funciona bem na maioria dos casos; variações surgem com a prática.
- **Exemplos**: deliberadamente simples ("de livro didático"), para explicar a refatoração básica com o mínimo de distração — não são exemplos de bom modelo de negócio. Cada exemplo é autocontido (o código não é levado adiante para "corrigir" outros problemas, que exigiriam outras refatorações), exceto quando refatorações costumam ocorrer juntas. Cores destacam trechos de código alterados quando difícil de identificar visualmente, sem exagero para não perder o propósito. Algumas refatorações muito simples não têm exemplo.

## Como usar o catálogo (Cap 6–12)
- O catálogo não é completo: reúne as refatorações mais "úteis" — comuns e que valem a pena nomear e descrever — por terem procedimentos interessantes (desenvolvem habilidade geral) e/ou grande efeito na melhoria do design.
- Refatorações pequenas/simples demais (ex.: Deslocar instruções, ausente na 1ª edição) podem não aparecer, embora o critério evolua entre edições.
- Nem toda refatoração lógica inversa é descrita: toda refatoração tem uma inversa lógica, mas só as consideradas interessantes/relevantes ganham verbete (ex.: a inversa de Encapsular variável não tem entrada própria).
- Use o catálogo como referência: escolha o verbete pelo cheiro de código ou objetivo de design, siga o procedimento em passos pequenos e teste entre passos, recorrendo ao exemplo completo na primeira vez que aplicar aquela refatoração.

## Pontos-chave (takeaways)
1. Cada verbete segue sempre a mesma estrutura: Nome → Esboço → Motivação → Procedimento → Exemplos.
2. O esboço e o procedimento são ajudas de memória para quem já conhece a refatoração; os exemplos são para quem está aprendendo.
3. Segurança vem de passos pequenos com testes frequentes; o tamanho do passo se ajusta à complexidade da situação.
4. O catálogo é seletivo e não exaustivo — prioriza refatorações comuns, com procedimentos didáticos ou alto impacto no design.

## Conecta com
- **Cap 3**: cheiros de código apontam qual verbete do catálogo consultar.
- **Cap 6–12**: os verbetes propriamente ditos, organizados no formato aqui apresentado.
