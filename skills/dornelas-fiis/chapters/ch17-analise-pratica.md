# Capítulo 17: Análise Prática

## Ideia Central
Demonstração ponta a ponta de como analisar um FII real (KNRI11 — Kinea Renda Imobiliária) usando informes oficiais, regulamento, fatos relevantes e sites públicos, extraindo liquidez, ativos, vacância, resultados, taxas e comparação com pares.

## Frameworks Apresentados
- **Roteiro de análise de um FII**: Sequência ordenada de etapas para conhecer um Fundo.
  - Quando usar: ao avaliar qualquer FII, especialmente os sem relatório gerencial de boa qualidade.
  - Como: (1) Liquidez e valor de mercado (IFIX, boletim diário); (2) P/VP; (3) Características gerais (informe mensal); (4) Regulamento (estratégia, taxas, conflito de interesse); (5) Ativos e contratos (informe trimestral); (6) Vacância; (7) Resultados (rendimentos, receitas, despesas, taxas); (8) Passivos e demandas judiciais; (9) Gestão; (10) Perspectivas futuras; (11) Comparação com pares.
- **Estimativa de aluguel por m² via participação na receita**: Reconstrói o aluguel de um imóvel quando o dado não é divulgado.
  - Quando usar: o administrador não revela preço/m² por contrato (dado estratégico).
  - Como: Receita do imóvel = % de participação nas receitas × receita total de aluguéis do mês; depois divida pela ABL locada do imóvel; compare com médias de consultorias (ex.: Buildings).
- **Análise de proporção distribuída vs. receitas**: Detecta se o FII "queima caixa" para manter rendimento.
  - Quando usar: avaliar sustentabilidade dos rendimentos no informe trimestral.
  - Como: %Resultado Distribuído > 100% indica distribuição acima das receitas (consumo de caixa).

## Conceitos-Chave
- **IFIX**: índice que pondera FII por valor de mercado; participação alta indica liquidez e tamanho.
- **Mandato de Renda**: objetivo de auferir renda com imóveis; gestor pode comprar/vender sem assembleia.
- **Gestão ativa**: política de investimentos abrangente; gestor seleciona/aliena ativos.
- **Contratos típicos vs. atípicos**: atípicos costumam ter longa duração e multas, comuns em logística.
- **Revisional vs. vencimento de contrato**: revisional = renegociação de preço; vencimento = fim do contrato.
- **Renda Mínima Garantida (RMG)**: garantia de renda; KNRI11 não possuía no período.
- **Fato relevante**: aviso oficial (B3/gestor) de eventos como aquisições e emissões.

## Modelos Mentais
- "Devo conhecer cada detalhe?" — em FII de gestão ativa diversificado, o gestor é pago para analisar imóveis; foque se ele entrega bons resultados (rendimento, vacância) em vez de esquadrinhar cada imóvel. Em FII mono-imóvel ou gestão passiva, vale aprofundar nos detalhes.
- Maus imóveis e maus negócios se refletem em indicadores fáceis (rendimento, vacância) — deixe-os fazer a triagem.
- Compare sempre com pares ajustando por características (qualidade do imóvel, contratos atípicos justificam P/VP maior).

## Anti-padrões
- **Confiar só no relatório gerencial**: não é obrigatório nem padronizado; cruze com informes oficiais e fatos relevantes.
- **Esquecer o impacto das taxas**: taxa de administração sobre valor de mercado pode crescer só pela alta da cota, sem melhora de performance; no KNRI11 absorve fatia considerável das receitas.
- **Tratar receita/m² média como exata**: em FII multi-segmento o cálculo médio é "deceptivo"; sirva-se dele só como parâmetro grosseiro.

## Fórmulas e Indicadores
- **Valor de Mercado** = Preço de Fechamento × Nº total de cotas emitidas
  - Ex.: R$152,40 × 23.600.802 = R$3.596.762.224,80 (~R$3,6 bi)
- **P/VP** = R$152,40 / R$150,69 ≈ 1,01
- **Receita do imóvel** = %participação × receita total de aluguéis
- **Receita/m²** = Receita do imóvel / ABL locada

## Tabelas de Referência
Comparação com pares (preço de 25/07/2019, informe 1ºT/2019):

| FII | Segmento | Taxas/Receita | Yield 12m | P/VP |
|-----|----------|---------------|-----------|------|
| RBRD11 | Híbrido | 2% | 8,63% | 1,32 |
| HGLG11 | Logístico | 9% | 5,67% | 1,31 |
| HGRE11 | Lajes Corp. | 14% | 5,45% | 1,08 |
| FIIP11B | Logístico | 1% | 8,37% | 1,06 |
| KNRI11 | Híbrido | 17% | 6,13% | 1,01 |
| FFCI11 | Lajes Corp. | 24% | 3,92% | 1,01 |
| EURO11 | Logístico | 10% | 5,32% | 0,52 |

Média de DY 12m da lista: 6,21% (KNRI11 na média). Média de P/VP sem o EURO11: 1,13.

## Exemplo Prático
Estimando o aluguel/m² do Edifício Bela Paulista (3,7562% das receitas, ABL 6.520,56 m², sem vacância), usando a receita de aluguéis de jun/19 (R$14.295.943,30):
Receita do imóvel = 3,7562% × R$14.295.943,30 = R$536.984,22.
Receita/m² = R$536.984,22 / 6.520,56 m² = R$82,34/m². Como a média regional da Buildings para imóveis dessa categoria é ~R$115,51/m², conclui-se que o FII cobra abaixo do mercado e tem espaço para reajustes positivos nas revisionais. O EURO11, com P/VP discrepante de 0,52, é explicado por vacância de 31,85% e um inquilino inadimplente cuja dívida (R$3,67 mi) supera a receita trimestral (R$1,22 mi).

## Principais Lições
1. Siga um roteiro: liquidez → P/VP → regulamento → ativos → vacância → resultados → pares.
2. Ajuste a profundidade da análise à natureza do FII (ativo/diversificado vs. mono-imóvel/passivo).
3. Cruze informe mensal, trimestral, regulamento e fatos relevantes — eles se complementam e revelam mudanças.
4. Distribuir acima de 100% das receitas significa queimar caixa; verifique a origem de receitas extras (vendas, adiantamentos).
5. Taxa de administração sobre valor de mercado é um risco silencioso, sobretudo em ciclo econômico negativo.
6. P/VP discrepante quase sempre tem uma causa concreta (vacância, inadimplência) — investigue antes de concluir.

## Conecta Com
- **Cap 16**: aplica P/VP, DY, vacância e comparação por pares aqui demonstrados.
- **Cap 18**: os eventos (emissões, RMG, fatos relevantes) aparecem na narrativa do ciclo de vida.
- **Cap 24**: tributação dos valores amortizados (referenciado na conclusão sobre ganho de capital).
