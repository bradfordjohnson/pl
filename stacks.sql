WITH cte AS
  (SELECT id,
          REGEXP_REPLACE(LOWER(REPLACE(name, source_extension, '')), '\..*$', '') AS name,
          REPLACE(source_path, name, '') AS source_dir
   FROM sidecar),
   hashes AS (
	SELECT
		sha256
	FROM media
	GROUP BY 1
	HAVING(COUNT(DISTINCT id) > 1)
)
SELECT media.id,
	   extension,
       source_dir,
	   CASE WHEN media.sha256 IN (SELECT sha256 FROM hashes) THEN TRUE ELSE FALSE END AS has_duplicate_hashes,
	   CASE WHEN COUNT(media.id) OVER(PARTITION BY cte.name) > 1 THEN TRUE ELSE FALSE END AS has_multiple_files_with_similar_name,
       REPLACE(LOWER(source_name), source_extension, '') AS media_name,
       cte.name,
       cte.id AS sidecar_id
FROM media
LEFT OUTER JOIN cte ON cte.source_dir = REPLACE(source_path, source_name, '')
AND cte.name LIKE CONCAT(REPLACE(LOWER(source_name), source_extension, ''))
WHERE cte.id IS NOT NULL
ORDER BY name
