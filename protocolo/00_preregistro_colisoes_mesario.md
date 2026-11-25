# PRÉ-REGISTRO — Colisões de títulos de mesários nos logs de urna 2026

**Status:** Congelado antes da execução nacional.  
**Data:** 2026-11-24  
**Hash SHA-256 deste arquivo (será calculado e registrado antes do censo):** `A_SER_CALCULADO`  
**Autor:** Análise quantitativa independente.  

Este documento congela hipóteses, modelo nulo, regra de decisão e exclusões **antes** de olhar os desfechos de colisão.

## 1. Objetivo e o que o resultado pode dizer

Medir, nos logs públicos das urnas de 2026, se a repetição do mesmo título no registro de presença de mesário em seções diferentes ocorre mais do que um modelo de erro de digitação explica.

**Não se opina sobre fraude.** Entrega-se: observado, esperado, razão, intervalo de confiança e veredito pela regra pré-registrada.

### Mecanismo banal conhecido (três condições encadeadas)
1. O mesário digita o título errado.
2. O número errado passa na validação da urna (apenas estrutural: dígito verificador + prefixo de UF; sem consulta a lista).
3. O número sorteado é o título de **outra pessoa que também é mesária** em outra seção (só títulos de mesários entram nesse campo). Se o erro cair no título de um eleitor comum, não há duplicata.

Com ~2,5 milhões de mesários em ~156 milhões de eleitores (~1,6 %), ~1 % de aprovação no dígito verificador e algo como dezenas de milhares de erros no país, a expectativa é de **poucos casos** (unidades, não milhares).

**Veredito útil:** o volume observado cabe nessa conta? E, se não cabe, o excesso está no volume ou na concentração?

### Três desfechos possíveis
- (a) Observado dentro do IC do nulo → acaso, encerrado.
- (b) Volume acima do IC → mecanismo insuficiente.
- (c) Volume normal mas casos concentrados em poucas seções, mesas ou UFs → o mecanismo existe, mas não é aleatório.

## 2. Dados e escala

- Logs por seção publicados pelo TSE (`resultados.tse.jus.br/oficial/ele2026/arquivo-urna/`), 1º e 2º turno, 27 UFs + exterior.
- Universo: ~499.248 seções.
- Arquivos `.jez` / `.logjez`, Latin-1 (ou UTF-8), mensagens datadas.
- **Regra de escala:** censo completo. Com expectativa de ~5 eventos, amostragem não distingue 4 de 8. Amostra só se o custo for proibitivo; nesse caso o resultado é declarado **inconclusivo por construção**.

## 3. Fase 0 — Vocabulário e regra de validação (antes de contar)

Em 30 seções de 5 UFs, identificar as strings de:
- início do registro de presença de mesário;
- digitação do título;
- erro de título inválido;
- confirmação;
- mensagem de biometria que não coincide com nenhum mesário cadastrado;
- habilitação de eleitor;
- reinício e contingência.

**Determinar empiricamente a regra de validação:** coletar tentativas rejeitadas e verificar se a rejeição depende só de formato (DV/UF) ou da lista da seção. Registrar a conclusão.

Se o log não separar presença de mesário de habilitação de eleitor, declarar e prosseguir só com o campo inequívoco.

## 4. Medição da taxa de erro (não chutar)

Não estimar \( p_1 \) por suposição. Contar as mensagens de **biometria que não coincide com nenhum mesário cadastrado**: elas são o rastro direto de “digitou um título que não é o dele e foi liberado assim mesmo”. Esse é o numerador de erros.

Classificar o tipo de erro observado por posição de dígito:
- substituição no prefixo de UF (aprovação ~27 %);
- no corpo sequencial (~1 %);
- no dígito verificador (~1 %);
- transposição e omissão.

Pesar \( p_2 \) por essa distribuição real, não por média genérica.

## 5. Modelo nulo (corrigido)

### Via 1 — Analítica
- \( N \) = registros de presença de mesário;
- \( p_1 \) = erros medidos / \( N \);
- \( p_2 \) = aprovação por posição, ponderada;
- \( q \) = fração de títulos válidos que pertencem a mesários (~1,6 %).
- Colisões esperadas ≈ \( N \times p_1 \times p_2 \times q \).

### Via 2 — Simulação (preferida)
- O conjunto-alvo da simulação é o **multiconjunto de títulos efetivamente digitados por mesários**. Isso embute automaticamente a condição 3, a geografia e a distribuição real dos títulos.
- Gerar o número de erros medido, com a distribuição de tipos de erro medida, contar quantos caem no conjunto-alvo e em seção diferente. Repetir 10.000 vezes.

### Via 3 — Resíduo de segunda ordem
Dois mesários distintos errando para o mesmo título válido. Calcular à parte (expectativa desprezível); registrar o valor.

## 6. Teste de caso (para cada colisão detectada)

Inspecionar os dois registros e classificar:
- Existe mensagem de biometria não coincidente na seção onde o número foi digitado? Se sim → erro de digitação confirmado no caso.
- O título colidido aparece como presença de mesário na outra seção com biometria coincidente? Se sim → o dono estava lá.
- Distância < 1 km (mesmo prédio, substituição de mesa)? Contar em faixa separada: ali não há anomalia nenhuma.
- Há designação legítima do mesmo mesário para duas seções? Cruzar com a lista de convocados, se pública.

**Colisão sem mensagem de mismatch nas duas pontas** é a que merece atenção: é o único resíduo que o mecanismo não cobre.

## 7. Faixas (não somar)

- Distância: A) < 1 km; B) 1–50 km; C) > 50 km.
- Intervalo: < 60 s; 1–30 min; 30 min–4 h; > 4 h.
- Reportar as duas dimensões cruzadas.

## 8. Testes estatísticos

- Razão observado/esperado por faixa, com IC 95 % (Poisson exato ou bootstrap).
- Índice de dispersão e teste de concentração: os casos se distribuem como Poisson ou se aglomeram em poucas seções/mesas/UFs? Concentração é o sinal mais incriminador, porque não é prevista pelo nulo.
- Mesmo pipeline em 2022 e 2018. Se 2026 ficar dentro da faixa dos anos homologados, é o acaso.
- Sensibilidade com \( p_1 \times 0{,}5 \) e \( \times 2 \): se o veredito virar, o resultado é frágil e deve ser dito.

## 9. Confundidores

- Mesário eleitor de outra seção digitando o próprio título;
- mesário convocado em turnos diferentes;
- substituição no mesmo dia;
- mesa incompleta;
- restart e contingência replicando linhas;
- título digitado para liberar eleitor confundido com título de mesário.

Cada um que não for eliminável entra como ressalva quantificada.

## 10. Regra de decisão (pré-registrada, congelada)

- Observado dentro do IC 95 % do nulo **e** dispersão compatível com Poisson → **acaso, encerrado**.
- Observado acima do limite superior do IC → **excesso de volume**, com magnitude e faixa informadas.
- Observado dentro do IC mas com dispersão acima do esperado, concentrado em < 5 % das seções → **mecanismo insuficiente por concentração**.
- Ausência de excesso é resultado e deve abrir o relatório, não o fechamento.

## 11. Proibições

- Não tratar o título no log como identidade provada.
- Não estimar a taxa de erro por suposição quando o log tem o rastro do erro.
- Não sortear o alvo da simulação do eleitorado inteiro: só mesários geram duplicata.
- Não somar faixas de distância heterogêneas.
- Não usar distância como prova: no nulo, o erro acerta qualquer ponto do país, e a urna não consulta rede.
- Não concluir fraude; concluir excesso, ou ausência dele.
- Não usar amostra para um evento com expectativa de unidade sem declarar a limitação.

## 12. Entregáveis esperados

- `relatorio.md` com método, denominadores, \( p_1 \) e \( p_2 \) medidos, tabela por faixa, IC, veredito e limitações.
- `colisoes.csv` com título (mascarado), seções, UF, zona, timestamps, delta, distância, faixa e classificação do teste de caso.
- `parsing.py` e `simulacao.py` versionados e executáveis do zero.
- Seção de limitações com o que o log não permite saber.
- Uma linha de conclusão em linguagem simples, sem adjetivo.

---

**Este arquivo é imutável após o cálculo do hash e o início do censo.** Qualquer alteração exige emenda formal em `protocolo/`.
