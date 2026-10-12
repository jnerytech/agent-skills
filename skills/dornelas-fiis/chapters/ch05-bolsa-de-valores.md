# Capítulo 5: Bolsa de Valores

## Ideia Central
A Bolsa de Valores (B3) é a empresa que conecta emissores e investidores e dá liquidez, segurança e padronização à negociação das cotas de FII — operando como um leilão (pregão) com mercados primário/secundário, leilões de abertura/fechamento, custódia e mecanismos de proteção.

## Frameworks Apresentados
- **Mercado primário vs. secundário**: emissão (fundo↔investidor) vs. negociação (investidor↔investidor).
  - Quando usar: para saber de quem você compra/vende e o que esperar de preço.
  - Como: primário = IPO/emissão de cotas; secundário = negociação entre investidores na Bolsa, sem envolver o FII.
- **Leitura do ticker (XXXXY)**: 4 letras do nome do FII + número do tipo de título.
  - Quando usar: para identificar a cota a negociar.
  - Como: XXXX = nome do FII; Y = 11 para cotas de FII; 12/13/14 = direitos de subscrição; sufixo "B" = negociado em mercado de balcão.
- **Fluxo de operação na Bolsa**: corretora → homebroker → sistema B3 → contraparte → liquidação.
  - Quando usar: ao operar.
  - Como: abrir conta na corretora, transferir dinheiro, enviar ordem pelo homebroker; a B3 acha a contraparte e liquida (transfere dinheiro e cotas).

## Conceitos-Chave
- **B3**: única Bolsa de Valores do Brasil; reúne investidores em sistema confiável e seguro.
- **Pregão**: funcionamento da Bolsa na forma de leilão.
- **IPO (Oferta Pública Inicial)**: primeira emissão de cotas (mercado primário).
- **Homebroker**: programa que envia ordens de compra/venda à corretora pela internet.
- **Ticker / código de negociação**: identificador da cota (ex.: PQDP11).
- **Prazo de liquidação**: tempo da transferência efetiva — 2 dias úteis (D+2) para cotas de FII.
- **Conta de Custódia**: "caixinha" digital atrelada ao CPF na B3 onde ficam as cotas; movimentada pela corretora.
- **Mercado à vista / fracionário / balcão / a termo**: ambientes de negociação com graus de padronização diferentes.
- **Leilão (call) de abertura/fechamento**: determinam preço de abertura e de fechamento maximizando cotas negociadas.
- **Circuit breaker**: proteção que interrompe a negociação em variações excessivas ou fato relevante.
- **MRP (Mecanismo de Ressarcimento de Prejuízos)**: ressarce prejuízos por erros fora do controle do investidor (apurado pela BSM).
- **Especulador**: quem se importa só com a variação de preço, não com o ativo.

## Modelos Mentais
- **Pense no pregão como um leilão contínuo**: compradores e vendedores postam ofertas; o sistema casa pelo melhor preço.
- **Use o ticker como "etiqueta"**: o "11" sinaliza cota de FII; "B" indica balcão; "12+" são direitos de subscrição.
- **Trate a Bolsa como infraestrutura, não cassino**: ela dá segurança; o risco vem das suas escolhas e do humor de curto prazo.

## Anti-padrões
- **Começar querendo ser especulador**: iniciantes buscando ganho rápido viram presa dos "tubarões" e saem achando que é cassino.
- **Entrar em IPO sem histórico**: no IPO o preço embute custos (propaganda, taxas) e tende a ajustar para baixo no secundário; falta resultado passado para avaliar o fundo.
- **Vender em pânico durante circuit breaker / alta volatilidade**: variações de curto prazo são emocionais.

## Tabelas de Referência

| Item | Cotas de FII |
|------|--------------|
| Mercado de negociação | À vista, múltiplos de 1 unidade |
| Ticker | XXXX + 11 (ex.: PQDP11) |
| Direitos de subscrição | 12, 13, 14 |
| Balcão | Sufixo "B" (ex.: CXCE11B) |
| Liquidação | D+2 (2 dias úteis) |
| Custódia | Conta atrelada ao CPF na B3 |

| Leilão | Quando | Para quê |
|--------|--------|----------|
| Abertura | 15 min antes do pregão | Define preço de abertura |
| Fechamento | 5 min antes do encerramento | Define preço de fechamento (referência) |
| Durante o pregão | Ordens atípicas/oscilação | Reorganiza a negociação |

## Exemplo Prático
Você quer comprar o FII PARQUE DOM PEDRO SHOPPING CENTER. Identifica o ticker pela regra XXXXY: "PQDP" (nome) + "11" (cota de FII) = **PQDP11**. Pelo homebroker da sua corretora, envia uma ordem de compra com quantidade e preço. A ordem vai ao sistema da B3, que no pregão (leilão) casa sua oferta com um vendedor. Em D+2, a liquidação retira o dinheiro da sua conta na corretora e transfere a cota para sua Conta de Custódia na B3, atrelada ao seu CPF. Se fosse PQDP12, você estaria negociando direitos de subscrição, não a cota.

## Principais Lições
1. A Bolsa dá liquidez ao mercado secundário — sem ela seria difícil achar comprador/vendedor de cotas.
2. Aprenda a ler o ticker: "11" = cota de FII, "B" = balcão, "12/13/14" = direitos de subscrição.
3. Liquidação de FII é D+2; custódia fica atrelada ao seu CPF na B3.
4. O grande desafio do pequeno investidor é escolher bons FII resilientes e reduzir riscos, não especular.
5. IPO tende a sair caro (custos embutidos) e sem histórico — avalie se cabe na sua estratégia.

## Conecta Com
- **Cap 2**: por ser condomínio fechado, a venda só acontece no mercado secundário da Bolsa.
- **Cap 4**: a B3 e seu autorregulador (BSM), a corretora e a Clearing que liquida as operações.
- **Cap 9**: direitos de subscrição (tickers 12/13/14).
- **Cap 22**: homebroker em detalhe.
