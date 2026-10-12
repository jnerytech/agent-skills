# Cheatsheet — XP (decisões à moda Kent Beck)

## Quando usar XP vs. quando NÃO usar
| Use XP quando… | NÃO use XP quando… |
|---|---|
| Requisitos vagos/instáveis (incerteza alta) | Curva de custo de modificação é exponencial |
| Time pequeno-médio (≤ ~10–12; até ~20 difícil) | Time grande (50–100 programadores) |
| Feedback rápido possível (build/testes em minutos) | Feedback lento (build 24h, certificação 2 meses) |
| Pode testar realisticamente | Impossível testar (hardware de US$1M em capacidade máxima) |
| Cliente disponível e disposto a decidir | Cliente desconfiado/passivo; exige spec gigante |
| Espaço físico aberto possível | Programadores em andares/salas separadas |

## Decisão: projetar/implementar agora ou adiar?
- **Adie** (regra geral): custo de decidir hoje = custo + juros + inércia; sob incerteza, o valor de **esperar** é alto.
- **Decida hoje SE**: custo de mudar amanhã é altíssimo, OU você é comprovadamente ótimo adivinho, OU a inércia adicionada é baixíssima.
- Default: "Os problemas de hoje já são suficientes" → projete hoje p/ hoje, amanhã p/ amanhã.

## "Mais simples" — 4 critérios EM ORDEM (once and only once)
1. Comunica tudo o que você quer comunicar.
2. Sem lógica duplicada (cuidado: hierarquias paralelas).
3. Menor nº de classes.
4. Menor nº de métodos.
> Teste de eliminação: apague tudo sem propósito comunicacional/computacional → o que resta é o design.

## Quatro variáveis: quem fixa o quê
- Negócios fixam **3** (custo, tempo, qualidade); time entrega a **4ª** (escopo).
- Nunca fixe as quatro → "a qualidade some".
- Falta tempo? Gire o **escopo**, nunca a qualidade.

## O que testar (testar é apostar)
- Teste **só o que pode falhar**. Código simples demais p/ falhar → sem teste.
- Unidade (programador): **100% binário** — se falha, é a prioridade nº 1.
- Funcional (cliente): **porcentagem** crescente; perto da entrega, categorize os que falham.
- Legado: teste **sob demanda** (ao adicionar função / corrigir bug / refatorar), nunca tudo de uma vez.

## Estimativa
- Unidade base: **Tempo Ideal de Programação** ("sem distrações nem acidentes").
- História: 1–5 semanas ideais. Tarefa de engenharia: 1–3 dias ideais.
- Calendário = ideal × **fator de carga** (medido, ~2–4) — não chute.
- Regra: **quem implementa estima**; candidata-se à tarefa **antes** de estimar (evita Síndrome da Primeira Terça).

## Tells & smells (sinais de problema)
- 2ª semana seguida de hora extra → processo quebrado (conserte, não trabalhe mais).
- "Nó no estômago ao entrar no carro de manhã" → algo errado no projeto; é função do gerente agir.
- Métrica perto de 100% → inútil; troque (exceto testes de unidade = pressuposto).
- Querer manter o quadro branco sem apagar → o projeto não foi bem comunicado ao código/time.
- Você evita olhar o código velho → "coisas terríveis crescem no escuro"; traga tudo à tona.
- Diagramas: gaste **só 10–15 min**, depois volte ao código; não mantenha diagramas sincronizados.

## Ritmos / horizontes
| Horizonte | Duração | Quem dirige |
|---|---|---|
| Tarefa de engenharia | 1–3 dias | Programador |
| Iteração | 1–4 semanas | Cliente escolhe histórias |
| Entrega (release) | 2–6 meses (1ª) | Negócios (escopo/data) |
| Integração | poucas horas (máx 1 dia) | Par que integra |

## Adoção (Don Wells)
1. Escolha o **pior** problema. 2. Resolva à moda XP. 3. Quando não for mais o pior, repita.
Comece por **testes** ou **planejamento**. Reorganize a mobília. Compre salgadinhos.

## Os 4 valores → 5 princípios fundamentais
Comunicação · Simplicidade · Feedback · Coragem (+ Respeito).
→ Feedback rápido · Simplicidade presumida · Mudanças incrementais · Aceitação das mudanças · Alta qualidade.
