SELECT
    media.id
FROM
    media
LEFT OUTER JOIN
    sidecar ON sidecar.name LIKE CONCAT(REGEXP_REPLACE(media.source_path, '.*\/', ''), '%')
WHERE
    sidecar.id IS NOT NULL;