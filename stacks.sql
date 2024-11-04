WITH cte AS
  (SELECT id,
          regexp_replace(lower(replace(name, source_extension, '')), '\..*$', '') AS name,
          replace(source_path, name, '') AS source_dir
   FROM sidecar)
SELECT media.id,
       source_dir,
       replace(lower(source_name), source_extension, '') AS media_name,
       cte.name,
       cte.id AS sidecar_id
FROM media
LEFT OUTER JOIN cte ON cte.source_dir = replace(source_path, source_name, '')
AND cte.name LIKE concat(replace(lower(source_name), source_extension, ''))
WHERE cte.id IS NOT NULL
