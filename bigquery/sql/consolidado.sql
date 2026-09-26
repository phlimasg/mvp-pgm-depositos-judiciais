SELECT
  data_djo AS data_referencia,
  SUM(CASE WHEN UPPER(TRIM(tipo_arquivo)) = 'RESGATES A FAVOR DO GOVERNO' THEN valor_atualizado ELSE 0 END) AS total_a_receber,
  SUM(CASE WHEN UPPER(TRIM(tipo_arquivo)) = 'RESGATES CONTRA O GOVERNO' THEN valor_atualizado ELSE 0 END) AS total_a_pagar,
  SUM(CASE WHEN UPPER(TRIM(tipo_arquivo)) = 'RESGATES A FAVOR DO GOVERNO' THEN valor_atualizado ELSE 0 END)
    - SUM(CASE WHEN UPPER(TRIM(tipo_arquivo)) = 'RESGATES CONTRA O GOVERNO' THEN valor_atualizado ELSE 0 END) AS saldo_diario
FROM `pgm-datalake-prod.pgmconnect.dados_djo`
WHERE UPPER(TRIM(tipo_arquivo)) IN ('RESGATES CONTRA O GOVERNO', 'RESGATES A FAVOR DO GOVERNO')
  AND data_djo >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
GROUP BY data_referencia
ORDER BY data_referencia;