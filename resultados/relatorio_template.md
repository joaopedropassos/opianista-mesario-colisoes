# Relatório — Colisões de títulos de mesários (Eleições 2026)

**Status:** Template. Preencher após o censo.
**Protocolo:** `protocolo/00_preregistro_colisoes_mesario.md`
**Hash do protocolo no momento da execução:** `A_SER_PREENCHIDO`

## 1. Método (resumo)

Censo dos logs públicos de urna (1º e 2º turno, 27 UFs + exterior). Extração de registros de presença de mesário e mensagens de biometria que não coincide com nenhum mesário cadastrado. Modelo nulo por simulação Monte Carlo sobre o multiconjunto real de títulos digitados por mesários (10.000 réplicas). Regra de decisão congelada no pré-registro.

## 2. Denominadores e taxas medidas

| Quantidade | Valor |
|------------|-------|
| Seções processadas | |
| Registros de presença de mesário (N) | |
| Mensagens de mismatch de biometria | |
| p1 medido | |
| Títulos únicos de mesários | |

## 3. Resultado principal

| Métrica | Valor |
|---------|-------|
| Colisões observadas | |
| Esperado (simulação) | |
| Razão obs/esp | |
| IC 95 % do esperado | |
| Dentro do IC? | |
| Índice de dispersão | |

## 4. Veredito (pela regra pré-registrada)

**[acaso, encerrado | excesso de volume | mecanismo insuficiente por concentração | inconclusivo]**

Uma linha em linguagem simples, sem adjetivo:

> 

## 5. Limitações

- O título no log não prova identidade da pessoa.
- A urna valida apenas estrutura (DV + prefixo de UF); não consulta lista de mesários.
- Distância geográfica não constitui prova de anomalia sob o modelo nulo.
- Confundidores não elimináveis (substituição de mesa, restart, designação legítima) entram como ressalva quantificada.
- Censo completo é obrigatório; qualquer amostragem torna o resultado inconclusivo por construção.

## 6. Arquivos de saída

- `colisoes.csv` — título mascarado, seções, UF, zona, timestamps, delta, distância, faixa, classificação do teste de caso.
- `nulo.json` — resultado da simulação.
