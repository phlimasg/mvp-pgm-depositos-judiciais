SELECT
  b.id,
  a.num_processo,
  a.cod_agencia,
  a.unidade_judiciaria,
  a.nome_autor AS autor,
  a.cpf_cnpj_autor AS cpf_cnpj_autor,
  a.nome_reu AS reu,
  a.cpf_cnpj_reu AS cpf_cnpj_reu,
  CONCAT(b.cod_banco, b.cod_agencia) AS conta,
  b.valor_principal,
  b.juros,
  b.correcao,
  b.valor_atualizado,
  b.valor_resgatado,
  b.data_deposito,
  b.parcela,
  a.especializada, 
  REGEXP_EXTRACT(COLLATE(a.especializada, ''), r'^([^-]+)') AS sigla,
  bp.classeProcessual, 
  f.data AS data_djo,
  f.tipo_arquivo 
FROM
  `pgm-datalake-prod.pgmconnect.djoretfiletipoa` a
JOIN 
  `pgm-datalake-prod.pgmconnect.djoretfiletipob` b ON b.retfiletipoa_id = a.id
JOIN 
  `pgm-datalake-prod.pgmconnect.djoretfile` f ON a.retfile_id = f.id  
LEFT JOIN 
  `pgm-datalake-prod.bdia.pbprocessosjudiciaissimp` bp ON 
  REGEXP_REPLACE(COLLATE(bp.numeroJudicialouEmbargo, ''), r'\D', '') = REGEXP_REPLACE(COLLATE(a.num_processo, ''), r'\D', '');