# Cheatsheet — Accelerate

## Decision rules
- **Speed vs stability trade-off?** False dichotomy — high performers win on both; pursue tempo and stability together. (Ch 2)
- **Choosing a metric?** Must be a *global outcome* (dev and ops share it) and *outcome, not output*. Reject lines of code, velocity, utilization. (Ch 2)
- **Transformation plan?** Use a capabilities model, not a maturity model; never "done". (Ch 1)
- **Want to change culture?** Change practices (CD, Lean management) — culture follows. (Ch 3)
- **Change approval?** Replace CAB with peer review + deployment pipeline; CABs hurt tempo with no stability gain. (Ch 7)
- **Architecture choice?** Coupling matters more than technology; aim for teams that test and deploy without coordination. (Ch 5)
- **Tool standardization?** Let teams choose; make the preferred platform the easy path. (Ch 5)
- **Security bottleneck?** Shift left: infosec in design, preapproved libraries, automated security tests. (Ch 6)
- **Burnout?** Fix the system (deployment pain, workload, fairness, values) — not the individual. (Ch 9)
- **"Does X cause Y?"** The book shows *inferential prediction* (theory + regression), not causation; say "predicts/drives", not "proves". (Ch 12)
- **Measuring culture or across the full stack?** Survey; for system internals use system data; triangulate. (Ch 14)

## Performance benchmark (2017, Table 2.3)
| Metric | High | Medium | Low |
|---|---|---|---|
| Deployment frequency | On demand (multiple/day) | Weekly–monthly | Weekly–monthly* |
| Lead time for changes | < 1 hour | 1 week–1 month | 1 week–1 month* |
| Time to restore service | < 1 hour | < 1 day | 1 day–1 week |
| Change fail rate | 0–15% | 0–15% | 31–45% |
*Same median as medium; difference statistically significant.

## High vs low performers (2017)
| Measure | High performers |
|---|---|
| Deployment frequency | 46× more frequent |
| Lead time | 440× faster |
| Time to restore | 170× faster |
| Change fail rate | 5× lower (1/5 as likely) |
| Unplanned work/rework | 21% vs 27% (low) |
| Organizational performance | 2× as likely to exceed goals |

## Thresholds & defaults
| Item | Value |
|---|---|
| Trunk-based development | < 3 active branches; branches live < 1 day; no code freezes |
| Small batch | Completable in ≤ 1 week |
| Culture survey | 7 Westrum items, 1–7 Likert, mean score |
| eNPS | % 9–10 − % 0–6; high performers 2.2× more likely to recommend org |
| Construct validity | AVE > 0.50; composite reliability / Cronbach's α ≥ 0.70 |

## Westrum culture quick-diagnosis
| Pathological | Bureaucratic | Generative |
|---|---|---|
| Low cooperation | Modest cooperation | High cooperation |
| Messengers shot | Messengers neglected | Messengers trained |
| Responsibilities shirked | Narrow responsibilities | Risks are shared |
| Bridging discouraged | Bridging tolerated | Bridging encouraged |
| Failure → scapegoating | Failure → justice | Failure → inquiry |
| Novelty crushed | Novelty → problems | Novelty implemented |

## Tells & smells
- Deployments scheduled off-hours with fear → deployment pain; automate and shrink batches. (Ch 9)
- Dev measured on throughput, ops on stability → wall of confusion. (Ch 2)
- "We did Agile" but specs need outside approval → faux Agile; enable team experimentation. (Ch 8)
- Teams wait on integrated staging to test → tight coupling. (Ch 5)
- Medium performers doing more manual work than low → J-curve; push through with automation. (Ch 17)
- Metrics used to punish → numbers become fiction (Deming). (Ch 2)
- Copying Spotify/ING model wholesale → implementation thinking; experiment instead. (Ch 16)
