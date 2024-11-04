WITH cte AS
  (SELECT id,
          REGEXP_REPLACE(LOWER(REPLACE(name, source_extension, '')), '\..*$', '') AS name,
          REPLACE(source_path, name, '') AS source_dir
   FROM sidecar)
SELECT media.id,
       source_dir,
       REPLACE(LOWER(source_name), source_extension, '') AS media_name,
       cte.name,
       cte.id AS sidecar_id
FROM media
LEFT OUTER JOIN cte ON cte.source_dir = REPLACE(source_path, source_name, '')
AND cte.name LIKE CONCAT(REPLACE(LOWER(source_name), source_extension, ''))
WHERE cte.id IS NOT NULL
