# Capítulo 22: Homebroker

## Ideia Central
O homebroker é o programa (via site ou software instalado) usado para negociar ativos na Bolsa; apesar de parecer confuso, é apenas um pequeno conjunto de informações apresentadas de várias formas, organizado em áreas funcionais.

## Frameworks Apresentados
- **Áreas do homebroker**: mapa das 6 regiões da tela.
  - Quando usar: ao se orientar na interface antes de operar.
  - Como: identificar (1) Carteira de Ativos, (2) Saldo da Conta Corrente, (3) Gráfico do preço, (4) Livro de Ofertas, (5) Formulário/boleto de ordens, (6) Cesta de Ordens.
- **Processo de compra de uma cota (7 passos)**:
  - Quando usar: ao enviar qualquer ordem de compra (venda é análoga).
  - Como: 1) decidir qual FII; 2) decidir o valor a investir; 3) verificar o preço de negociação no momento; 4) decidir entre comprar a mercado ou por preço específico; 5) preencher o boleto; 6) checar o envio na cesta de ordens; 7) acompanhar a execução.
- **Leitura de candlestick**: vela com 4 preços (abertura, máximo, mínimo, fechamento).
  - Quando usar: para ler a variação de preço por período.
  - Como: corpo entre abertura e fechamento; pavios até máximo/mínimo; vermelho/preto quando abertura > fechamento (queda), verde/branco quando abertura < fechamento (alta).

## Conceitos-Chave
- **Homebroker**: programa de negociação de ativos na Bolsa, acessado via site da corretora ou software instalado.
- **Carteira de Ativos (janela)**: mostra último preço, variação, melhores ofertas de compra/venda, preços médio/máximo/mínimo do dia, fechamento anterior e volume em R$.
- **Saldo da Conta Corrente**: dinheiro disponível para comprar; pode divergir do saldo real por crédito da corretora, garantias de derivativos ou liquidação pendente.
- **Livro de Ofertas**: todas as ordens de compra/venda registradas, com quantidade, preço e corretora.
- **Spread**: diferença entre a melhor oferta de venda e a de compra; pequeno em FII líquidos, grande em ilíquidos.
- **Boleto (boleta)**: formulário de envio de ordens de compra/venda.
- **Cesta de Ordens**: mostra a situação das ordens (aceita, quanto executado, preço e horário).
- **Comprar a mercado**: pagar o preço da melhor oferta de venda do momento.
- **Validade VAC**: ordem "Válida Até Cancelar".
- **Nota de Corretagem**: documento diário com quantidade, preço, código e taxas/impostos das operações.
- **Ordens start/stop**: ordens condicionadas a um preço-gatilho do ativo.

## Modelos Mentais
- **Use o saldo real como referência, não o exibido**: o número do homebroker pode incluir crédito/garantias; sempre confira contra o saldo efetivo antes de operar.
- **Liquidez se lê no livro e no spread**: spread de um centavo indica alta liquidez; spread largo indica fundo pouco líquido.
- **A ordem é um pedido, não uma certeza**: pode ser executada parcialmente, em preço melhor, ou em outro dia.

## Anti-padrões
- **Operar nos leilões de abertura/fechamento**: alta volatilidade; prefira o meio do pregão.
- **Confiar no saldo exibido**: pode estar inflado por crédito ou garantias, levando a ordens sem lastro real.
- **Não conferir a cesta de ordens após enviar**: a ordem pode ter sido rejeitada ou ter erro despercebido.
- **Não guardar as notas de corretagem**: são os comprovantes das operações e base do cálculo de IR.

## Exemplo Prático
Compra de R$ 1.000,00 em HGRE11: (1-2) decide-se o FII e o valor; (3) abre-se o livro de ofertas — último negócio a R$ 159,53 e melhor oferta de venda a R$ 159,97; (4) em vez de comprar a mercado (R$ 159,97), opta-se por ordem ao preço do último negócio, R$ 159,53; com R$ 1.000,00 cabem 6 cotas; (5) preenche-se o boleto com 6 cotas a R$ 159,53, validade VAC, conferindo o total do débito (já incluindo taxas) antes de clicar ENVIAR; (6) confirma-se na cesta de ordens que a ordem foi aceita; (7) acompanha-se a execução conforme surgem ofertas de venda. Se executada parcialmente em VAC, o restante permanece para outro dia — atenção: algumas corretoras cobram corretagem por dia de execução, outras só uma vez.

## Principais Lições
1. O homebroker é só um conjunto de informações reapresentadas; dominar as 6 áreas desmistifica a tela.
2. Comprar a mercado paga a melhor oferta de venda; definir preço dá controle, mas pode não executar.
3. Spread e livro de ofertas revelam a liquidez do FII.
4. Ordens podem executar parcial/parcelado, afetando a corretagem cobrada conforme a corretora.
5. Confira e guarde todas as notas de corretagem — são comprovantes e base do IR.

## Conecta Com
- **Cap 21**: o acesso ao homebroker e a custódia vêm da corretora escolhida.
- **Cap 23**: notas de corretagem e dados de execução alimentam o controle mensal de patrimônio.
- **Cap 24**: preços, taxas e IRRF do boleto/nota entram no cálculo de ganho de capital.
