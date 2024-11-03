WITH Hashes AS (
  SELECT
    sha256
	FROM
    media
	GROUP BY
    1
	HAVING(COUNT(DISTINCT id) > 1)
)
SELECT
	Hashes.sha256,
	media.id
FROM
  Hashes
LEFT OUTER JOIN
  media ON Hashes.sha256 = media.sha256
