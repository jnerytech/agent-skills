# Cheatsheet — Refatoração (Fowler 2ª ed.)

Julgamento de Fowler condensado: quando refatorar, o que aplicar, quando parar.

## Regras de decisão — QUANDO refatorar
- **Regra de Três**: 1ª vez, faça; 2ª, incomode-se mas duplique; **3ª vez, refatore**.
- **Preparatória**: vai adicionar feature em código difícil? Refatore *primeiro* para facilitar — "se preciso ir para o oeste, comece dirigindo para o leste".
- **Oportunista / escoteiro**: entendeu algo obscuro? Grave o entendimento no código agora (deixe melhor do que achou).
- **Não refatore quando**: vai reescrever do zero em breve; ou o código funciona e você nunca precisa tocá-lo.
- **Não misture chapéus**: em cada commit, ou adiciona feature **ou** refatora — nunca os dois (Dois Chapéus).

## Ritmo dos pequenos passos
1. Garanta testes verdes (código autotestável).
2. Faça UM passo pequeno da mecânica.
3. Rode os testes. Vermelho → desfaça o último passo, não depure.
4. Verde → commit. Repita.
> Se o código ficou "quebrado por dias", **não era refatoração**.

## Cheiro → refatoração (mapa rápido)
| Cheiro | Aplique |
|---|---|
| Função longa | Extrair função; Substituir temp por consulta; Decompor condicional |
| Nome misterioso | Mudar declaração de função; Renomear variável/campo |
| Código duplicado | Extrair função; Subir método; Separar em fases |
| Lista longa de parâmetros | Introduzir objeto de parâmetros; Preservar objeto inteiro; Substituir parâmetro por consulta |
| Switches repetidos | Substituir condicional por polimorfismo |
| Condicional complexa | Decompor condicional; Cláusulas de guarda; Consolidar expressão |
| Inveja de recursos | Mover função; Extrair função |
| Cirurgia com rifle | Mover função/campo; Combinar funções em classe |
| Alteração divergente | Extrair classe; Separar em fases |
| Obsessão por primitivos | Substituir primitivo por objeto; Introduzir objeto de parâmetros |
| Dados mutáveis | Encapsular variável; Separar variável; Substituir derivada por consulta |
| Classe grande | Extrair classe/superclasse |
| Intermediário | Remover intermediário |
| Herança recusada | Descer método/campo; Substituir subclasse por delegação |
| Comentários (que desculpam código ruim) | Extrair função; Introduzir asserção |

## Escolhas frequentes (if/then)
- **Condição excepcional que impede o resto** → cláusula de guarda (early return). **Dois caminhos igualmente válidos** → if/else simétrico.
- **Switch sobre um campo de tipo, repetido em vários lugares** → polimorfismo (subclasse por tipo). **Aparece uma vez só** → deixe o switch.
- **Herança em que a subclasse recusa parte da herança / precisa mudar de "tipo" em runtime** → prefira delegação (composição).
- **Função retorna valor E muda estado** → Separar consulta de modificador (Command-Query Separation).
- **Argumento booleano de flag** → funções separadas explícitas (o chamador não decifra `true`).
- **Muitos chamadores para mudar assinatura** → procedimento de migração (nova assinatura coexiste, migre aos poucos).

## Desempenho
- Refatore livremente; **otimize depois**, guiado por profiler. Código bem fatorado é mais fácil de otimizar. Só troque clareza por velocidade em hotspots medidos.

## Tells (sinais rápidos)
- Precisa de comentário para explicar um bloco → extraia função com o nome do comentário.
- Rola a tela para ver a função inteira → função longa.
- "Onde mais preciso mudar isto?" → Cirurgia com rifle / duplicação.
- Passa 3+ parâmetros que sempre andam juntos → objeto de parâmetros.
