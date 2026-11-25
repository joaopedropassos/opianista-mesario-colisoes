# opianista-mesario-colisoes

Análise quantitativa pré-registrada de colisões de títulos de mesários nos logs públicos das urnas das Eleições 2026 (TSE).

**Objetivo:** medir se a repetição do mesmo título no registro de presença de mesário em seções diferentes ocorre mais do que um modelo de erro de digitação explica.

Não se conclui fraude. Entrega-se observado, esperado, razão, IC e veredito pela regra congelada.

## Estrutura

```
protocolo/          pré-registro imutável (00_preregistro_colisoes_mesario.md)
codigo/
  parsing.py        extração de presença de mesário e mismatch de biometria
  simulacao.py      modelo nulo Monte Carlo (via preferida)
resultados/         saídas (não versionadas)
dados/              logs brutos (não versionados)
```

## Como executar

1. Baixar os pacotes de arquivos de urna do TSE (`resultados.tse.jus.br/oficial/ele2026/arquivo-urna/`).
2. Fase 0 (vocabulário):
   ```bash
   python codigo/parsing.py catalogo --zip dados/SP_2t.zip --saida resultados/catalogo_sp.csv --data 2026-10-25
   ```
3. Extração nacional (repetir por UF):
   ```bash
   python codigo/parsing.py extrair --zip dados/UF.zip --uf UF --data 2026-10-25 --saida resultados/eventos_UF.csv
   ```
4. Concatenar eventos e rodar o nulo:
   ```bash
   python codigo/simulacao.py --eventos resultados/eventos_todos.csv --saida resultados/nulo.json
   ```

## Regra de decisão (congelada)

- Observado dentro do IC 95 % do nulo **e** dispersão compatível com Poisson → acaso, encerrado.
- Observado acima do limite superior → excesso de volume.
- Dentro do IC mas concentrado em < 5 % das seções → mecanismo insuficiente por concentração.

## Limitações

- O título no log não prova identidade.
- A urna não consulta lista de mesários em tempo real; a validação é estrutural.
- Distância geográfica não é prova de anomalia no modelo nulo.
- Censo completo é obrigatório; amostragem torna o resultado inconclusivo por construção.

## Licença

MIT. Textos e protocolo: CC BY 4.0.
