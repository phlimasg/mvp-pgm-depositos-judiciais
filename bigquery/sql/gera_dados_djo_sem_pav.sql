WITH processos AS (
  -- Traz os números judiciais padrão
  SELECT REGEXP_REPLACE(CAST(numeroJudicialouEmbargo AS STRING), r'\D', '') AS num_processo
  FROM `pgm-datalake-prod.bdia.pbprocessosjudiciaissimp`
  WHERE numeroJudicialouEmbargo IS NOT NULL
  
  UNION ALL 
  
  -- Traz os números judiciais até 2009
  SELECT REGEXP_REPLACE(CAST(numeroJudicialouEmbargoAte2009 AS STRING), r'\D', '') AS num_processo
  FROM `pgm-datalake-prod.bdia.pbprocessosjudiciaissimp`
  WHERE numeroJudicialouEmbargoAte2009 IS NOT NULL
)

SELECT d.* FROM `pgm-datalake-prod.pgmconnect.dados_djo` d 
WHERE REGEXP_REPLACE(CAST(d.num_processo AS STRING), r'\D', '') NOT IN (
  -- A cláusula IS NOT NULL garante que o NOT IN funcione corretamente, 
  -- evitando bugs silenciosos caso algum valor nulo passe pela limpeza
  SELECT num_processo FROM processos WHERE num_processo IS NOT NULL
);