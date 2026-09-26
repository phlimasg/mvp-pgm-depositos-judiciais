WITH valor_dia AS (
  SELECT 
    data_deposito,
    SUM(valor_atualizado) AS valor
  FROM `pgm-datalake-prod.pgmconnect.dados_djo`
  WHERE tipo_arquivo = 'DEPOSITOS ACOLHIDOS'
    AND data_deposito >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
  GROUP BY data_deposito
),
calculo_geral AS (
  SELECT 
    data_deposito,
    valor,
    AVG(valor) OVER() AS media_periodo,
    MAX(data_deposito) OVER() AS data_maxima
  FROM valor_dia
)
SELECT 
  media_periodo,
  valor AS valor_ultimo_dia,
  data_maxima
FROM calculo_geral
WHERE data_deposito = data_maxima