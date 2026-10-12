# Capítulo 24: Imposto de Renda

> ATENÇÃO: as informações podem conter erros ou estar desatualizadas e servem apenas como referência. Consulte as leis, regulamentos ou um profissional antes de declarar. (Base: IN RFB nº 1.585/2015 e "Perguntão 2019" da Receita Federal.)

## Ideia Central
Quem compra, vende ou possui cotas de FII em um ano deve fazer a Declaração Anual do IR; o ganho de capital nas vendas é tributado em 20%, apurado mensalmente, com imposto pago via DARF até o último dia útil do mês seguinte.

## Frameworks Apresentados
- **Apuração mensal de ganho de capital**: cálculo por preço médio, com compensação de prejuízos.
  - Quando usar: a cada mês em que houver venda de cotas.
  - Como: taxas somam ao total da compra e subtraem do total da venda; calcular preço médio de compra (total investido ÷ nº de cotas); ganho = total recebido na venda − (cotas vendidas × preço médio); subtrair prejuízos do(s) mês(es) anterior(es); aplicar 20% sobre o ganho compensado.
- **Preenchimento da DARF**: documento de pagamento do imposto.
  - Quando usar: quando houver imposto a pagar; prazo é o último dia útil do mês seguinte ao da apuração. Use o programa SICALCWEB.
- **Declaração Anual (4 lançamentos)**: Lucros/prejuízos (Renda Variável > Operações Fundos Invest. Imob.); cotas em custódia (Bens e Direitos, código "Fundo de Investimento Imobiliário"); Rendimentos (Rendimentos Isentos e Não Tributáveis > Outros); Amortizações (abatidas em Bens e Direitos).

## Conceitos-Chave
- **Ganho de capital**: total recebido na venda menos o total pago (via preço médio); base do imposto.
- **Preço médio**: total investido dividido pelo número de cotas, recalculado a cada nova compra.
- **Compensação de prejuízo**: prejuízo de um mês abate o lucro do mês seguinte (e prejuízo do ano abate o ano seguinte, se declarado).
- **DARF**: Documento de Arrecadação de Receitas Federais; código de receita 6015 para FII.
- **IRRF (dedo-duro)**: 0,005% retido na fonte pela corretora na venda; compensável do imposto do mês; não retido se ≤ R$ 1,00.
- **Isenção de rendimentos**: rendimentos de FII a pessoa física são isentos se atendidos os critérios (a maioria dos casos atende).
- **Amortização**: devolução de capital; não é rendimento; abate o valor das cotas em Bens e Direitos.

## Modelos Mentais
- **Imposto sobre ganho, isenção no rendimento**: o lucro da venda é tributado (20%); os rendimentos mensais (dividendos) são normalmente isentos para PF.
- **Custos a seu favor**: taxas aumentam o custo (compra) e reduzem a venda, diminuindo o ganho tributável.
- **Prejuízo é crédito**: registrar prejuízos preserva o direito de compensação futura.

## Anti-padrões
- **Não apurar/pagar mês a mês**: o imposto vence no mês seguinte; atraso gera multa e juros (campos 08 e 09 da DARF).
- **Não declarar prejuízos**: perde-se o direito de compensar no ano seguinte (exige o Demonstrativo na anual).
- **Achar que isento de rendimento dispensa declaração**: quem opera/possui FII deve declarar, ainda que isento por outros motivos.

## Regras e Tabelas

**Alíquota e isenção:**

| Item | Regra |
|------|-------|
| Ganho de capital em FII | 20% sobre o lucro |
| Isenção sobre ganho de capital | Não há isenção para FII |
| IRRF na venda ("dedo-duro") | 0,005% sobre o valor total da operação; não retido se ≤ R$ 1,00 |
| Valor mínimo da DARF | R$ 10,00 (se devido < R$ 10,00: acumular ou pagar R$ 10,00) |
| Prazo de pagamento | Último dia útil do mês seguinte ao da apuração |
| Código da DARF (campo 04) | 6015 |

**Isenção de rendimentos (PF) — todos os critérios (Lei 11.196/2005):**
- Fundo: cotas negociadas exclusivamente em bolsa/balcão organizado E no mínimo 50 cotistas.
- Cotista: possuir < 10% do total de cotas; receber < 10% do total de rendimentos; ser pessoa física.

**Exemplo 1 — compra e venda simples:**

| Data | Operação | Ação | Qtd | Preço | Taxas | Total |
|------|----------|------|-----|-------|-------|-------|
| 03/04/2019 | Compra | INVE11 | 10 | R$ 100,00 | R$ 2,00 | R$ 1.002,00 |
| 05/04/2019 | Venda | INVE11 | 10 | R$ 120,00 | R$ 2,00 | R$ 1.198,00 |

Ganho = R$ 1.198,00 − R$ 1.002,00 = R$ 196,00. Imposto = 20% × R$ 196,00 = **R$ 39,20**.

**Exemplo 2 — preço médio com compras em meses diferentes:**

| Data | Operação | Ação | Qtd | Preço | Taxas | Total |
|------|----------|------|-----|-------|-------|-------|
| 03/04/2019 | Compra | INVE11 | 10 | R$ 100,00 | R$ 2,00 | R$ 1.002,00 |
| 14/05/2019 | Compra | INVE11 | 10 | R$ 120,00 | R$ 2,00 | R$ 1.202,00 |
| 16/05/2019 | Venda | INVE11 | 10 | R$ 150,00 | R$ 2,00 | R$ 1.498,00 |

Preço médio = (1.002,00 + 1.202,00) ÷ 20 = R$ 110,20. Total pago (10 cotas) = R$ 1.102,00. Ganho = R$ 1.498,00 − R$ 1.102,00 = R$ 396,00. Imposto = 20% × R$ 396,00 = **R$ 79,20**.

**Exemplo 3 — compensação de prejuízo (ver Exemplo Prático abaixo).**

**DARF — campos principais:** 01 nome/telefone; 02 último dia do mês da apuração; 03 CPF; 04 código 6015; 05 em branco; 06 último dia do mês seguinte ao da apuração; 07 valor do imposto; 08 multa por atraso; 09 juros por atraso; 10 valor total a pagar.

## Exemplo Prático
Compensação de prejuízo (Exemplo 3): em abril o investidor compra 10 INVE11 a R$ 100,00 (R$ 1.002,00 com taxa) e vende 5 a R$ 80,00 (R$ 398,00 líquido). Preço médio de abril = R$ 100,20; custo das 5 vendidas = R$ 501,00; resultado de abril = R$ 398,00 − R$ 501,00 = **−R$ 103,00 (prejuízo)**. Em maio compra 10 a R$ 120,00 (R$ 1.202,00) e vende 10 a R$ 150,00 (R$ 1.498,00). Novo preço médio = (R$ 501,00 + R$ 1.202,00) ÷ 15 = R$ 113,53; custo das 10 vendidas = R$ 1.135,33; ganho de maio = R$ 1.498,00 − R$ 1.135,33 = R$ 362,67. Compensando o prejuízo de abril: R$ 362,67 − R$ 103,00 = R$ 259,67. Imposto = 20% × R$ 259,67 = **R$ 51,93**, pago via DARF (código 6015) até o último dia útil de junho.

## Principais Lições
1. Ganho de capital em FII é tributado em 20%, sem isenção; rendimentos a PF são normalmente isentos.
2. Apuração é mensal por preço médio; imposto vence no mês seguinte via DARF (mín. R$ 10,00).
3. Taxas somam à compra e subtraem da venda, reduzindo o ganho tributável.
4. Prejuízos compensam lucros futuros, desde que declarados.
5. Mesmo isento de rendimentos, quem opera/possui FII declara: operações, custódia, rendimentos e amortizações.
6. IRRF de 0,005% na venda é compensável do imposto do mês.

## Conecta Com
- **Cap 23**: o controle mensal e o rateio de taxas fornecem os dados para a apuração.
- **Cap 22**: notas de corretagem trazem preços, taxas e IRRF usados no cálculo.
- **Cap 21**: a custódia e os comprovantes da corretora sustentam a declaração de Bens e Direitos.
