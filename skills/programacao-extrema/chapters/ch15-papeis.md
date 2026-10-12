# Capítulo 22: Papéis para Pessoas

## Core Idea
Como num time esportivo, certos papéis precisam ser preenchidos para um time eXtremo
funcionar — **Programador, Cliente, Testador, Rastreador, Treinador, Consultor, Chefão**.
Mas papéis são costume, não lei: se as pessoas não se encaixam, **mude os papéis**, não as pessoas.

## Frameworks Introduced — Os Papéis
- **Programador** (o coração da XP): analisa, projeta, testa, programa, integra. Primeiro
  valor é **comunicação** — o trabalho não acaba quando o computador entende. Habilidades:
  parear, hábito da simplicidade, refatorar, testar, abrir mão de posse individual, **reconhecer os próprios medos**.
- **Cliente**: a outra metade da dualidade — "o programador sabe **como** programar; o cliente
  sabe **o quê** programar". Escreve histórias e testes funcionais; **toma decisões** com
  confiança ("isto é mais importante que aquilo"); influencia sem controlar.
- **Testador**: focado no cliente — ajuda a escolher e escrever testes funcionais, executa-os
  e divulga resultados em local visível. Não é alguém separado para humilhar programadores.
- **Rastreador**: a "consciência do time" (Grilo Falante). Fecha o ciclo de feedback das
  estimativas ("2/3 das estimativas passadas estavam 50% acima da realidade"); dá a visão
  global do andamento; é o **historiador** (escores de testes, defeitos, casos adicionados).
- **Treinador**: responsável pelo processo como um todo. Trabalha **indiretamente** — cada
  direcionamento torna o time menos autoconfiante; interfira só quando o problema justifica o
  risco, e da forma menos impertinente possível (ex.: sugira um teste que force a correção).
- **Consultor**: conhecimento técnico profundo pontual. O time **não** deixa ele resolver
  sozinho — o objetivo é aprender a resolver. Provavelmente refarão o que ele fez.
- **O Chefão (Big Boss)**: o time precisa de **coragem, confiança e insistência** ocasional.
  Recebe comunicação franca (consequências de mudanças), não choradeira.

## Key Concepts
- **Papéis = costume, não lei da natureza**: grandes treinadores criam posições novas e moldam o sistema tático aos jogadores, não o inverso.
- **Trabalhar indiretamente** (treinador): direção demais → time perde a habilidade de trabalhar sem ele → cai produtividade, qualidade e moral.
- **O papel do treinador diminui** com o amadurecimento do time (controle distribuído).
- **Medos do programador**: parecer bobo, ser inútil, tornar-se obsoleto, não ser bom o bastante — sem coragem para reconhecê-los, a XP não funciona.

## Mental Models
- "Se um papel exige alguém disposto a correr riscos e você não tem essa pessoa, **redivida as responsabilidades**" — não finja que não há problema.
- Cliente confiável é raro: muitos clientes "aprenderam a não confiar na TI" — a XP não funciona com esse cliente passivo.

## Anti-patterns
- **Mudar as pessoas para caber nos papéis** (em vez de o contrário).
- **Treinador que conserta o projeto ele mesmo**: rouba autoconfiança do time.
- **Consultor que resolve sozinho**: o time precisará dele de novo; o objetivo é capacitar.

## Worked Example
Um gerente defende um arranjo "proibido": um programador que também é o **cliente**. O autor
diz que não pode funcionar (o programador precisa executar o processo e delegar decisões de
negócio). O gerente argumenta: "ele é um negociante de contratos de verdade que também sabe
programar; os outros negociantes confiam nele; os programadores sabem quando ele fala como
cliente e quando decide tecnicamente." Veredito: **as regras dizem que não pode, mas aqui não
se aplicam** — o que continua valendo é a **separação das decisões técnicas e de negócio**, e
todos (especialmente o treinador) precisam estar cientes de qual papel ele assume a cada momento.

## Key Takeaways
1. Sete papéis: Programador, Cliente, Testador, Rastreador, Treinador, Consultor, Chefão.
2. Programador é o coração; Cliente é a outra metade da dualidade (sabe "o quê").
3. Testador e Rastreador são focados no cliente / na medição — não em punir.
4. Treinador trabalha indiretamente e seu papel encolhe com a maturidade do time.
5. Papéis são costume: ajuste-os às pessoas, preservando a separação negócio/técnica.

## Connects To
- **Ch 14 (Responsabilidades)**: a dualidade Programador/Cliente operacionaliza a divisão de poder.
- **Ch 8 (Gerenciamento)**: Treinador e Rastreador dividem o que normalmente é "gerência".
- **Ch 24 (Dificuldades)**: reconhecer medos é central para os papéis funcionarem.
