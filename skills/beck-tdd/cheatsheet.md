# Cheatsheet — TDD (Kent Beck)

## As duas regras (tudo deriva daqui)
1. Escreva um teste automático que **falhe** antes de qualquer código de produção.
2. **Remova duplicação.**

## O ciclo (decore)
`vermelho → verde → refatore` =
1. Adicione um pequeno teste · 2. Rode todos, veja falhar · 3. Mudança mínima (pode ser feia) · 4. Rode todos, veja passar · 5. Refatore p/ remover duplicação.
> Resolva "funciona" **primeiro**, "limpo" **depois**. Um verde rápido perdoa todos os pecados — por um momento.

## Decisão: como chegar ao verde?
| Situação | Faça | Por quê |
|---|---|---|
| Sei digitar a solução simples | **Implementação Óbvia** | rápido (2ª marcha) |
| Não sei a implementação | **Faça de Conta** (constante→expressão) | verde já, generaliza depois |
| Inseguro sobre a abstração | **Triangule** (2+ exemplos) | abstração com prova |
| Ainda perdido | Pausa / Faça de Novo | quebra o laço fadiga→julgamento |

## Decisão: qual o próximo teste?
- Olhe a Lista: "óbvio, óbvio, não sei, óbvio... ah, **esse** eu consigo" → o último (não-óbvio mas factível) = **One Step Test**.
- Primeiro teste de uma operação nova → **Starter Test** (variante que não faz nada, entrada mínima).
- Defeito relatado → **Regression Test** (menor teste que o reproduz).
- Vai usar API externa → **Learning Test** antes.

## Decisão: o teste ficou grande/lento/complicado?
| Tell | Ação |
|---|---|
| Teste exige muitas mudanças p/ passar | **Child Test**: teste menor da parte que falha |
| Depende de recurso caro (BD, rede) | **Mock Object** (constantes) |
| Testar comunicação entre objetos | **Self Shunt** (TestCase é o colaborador) |
| Testar ordem de mensagens | **Log String** |
| Testar código de erro raro | **Crash Test Dummy** |

## O que (não) testar
- Teste: **condicionais, laços, operações, polimorfismo** — mas só do *seu* código.
- "Escreva testes até o **medo virar tédio**."
- Não teste código de terceiros sem desconfiança específica.
- Quantos testes? Calibre pelo **TMEF** desejado, não por permutações. (Beck: 6 no triângulo; Binder: 65.)

## Apagar testes? Só se redundante em AMBOS:
1. **Confiança** — não apague se reduz confiança no comportamento.
2. **Comunicação** — mantenha se contam cenários diferentes a um leitor.

## Testes como canário (sintoma → problema de projeto)
| Sintoma no teste | Projeto |
|---|---|
| Setup de 100 linhas | objetos grandes demais |
| Setup duplicado difícil de fatorar | objetos entrelaçados |
| Teste lento | difícil testar isolado |
| Teste frágil (quebra inesperado) | uma parte afeta outra |
> Meta: suíte completa em **≤ 10 minutos** (o "9,8 m/s²" do TDD).

## Terminar a sessão
- Sozinho → deixe **um teste quebrado** (marca de retomada).
- Em time → **Clean Check-in**: tudo verde. Comentar teste p/ passar = proibido.

## Padrões de projeto: quando emergem
| Na escrita do teste | Na refatoração |
|---|---|
| Command, Value Object | Null Object, Template Method, Pluggable Object/Selector |
| (Factory Method, Imposter, Composite, Collecting Parameter aparecem em ambos) | guiados por eliminar duplicação |

## Heurísticas rápidas (smells)
- 2+ mensagens a outro objeto num método → **Move Method**.
- Condicional explícito se espalhando → **Pluggable Object**.
- "Como faço variável global?" → **não faça** (sem Singleton).
- Duplicação que resiste → projeto latente pedindo para emergir.
- Dependência = problema; duplicação = sintoma. Mate o sintoma e mata a doença.
