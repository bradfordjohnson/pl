SELECT
    media.id
FROM
    media
LEFT OUTER JOIN
    sidecar ON sidecar.name LIKE CONCAT(REGEXP_REPLACE(media.source_path, '.*\/', ''), '%')
WHERE
    sidecar.id IS NOT NULL;

SELECT
    file_metadata->>'SourceFile'
FROM
    media;

SELECT
    *
FROM
    media
WHERE
    jsonb_typeof(file_metadata::jsonb) = 'object'
    AND EXISTS (
        SELECT 1
        FROM jsonb_each(file_metadata::jsonb) AS kv(key, value)
        WHERE kv.key ILIKE '%date%'
    );

SELECT 
    id,
    file_metadata->>'SourceFile' AS source_file,
    file_metadata->>'ExifTool:ExifToolVersion' AS exif_tool_version,
    file_metadata->>'File:FileModifyDate' AS file_modify_date,
    file_metadata->>'File:FileAccessDate' AS file_access_date,
    file_metadata->>'File:FileCreateDate' AS file_create_date,
    file_metadata->>'EXIF:DateTimeOriginal' AS exif_datetime_original,
    file_metadata->>'ICC_Profile:ProfileDateTime' AS icc_profile_datetime,
    file_metadata->>'IPTC:DateCreated' AS iptc_date_created,
    file_metadata->>'Composite:DateTimeCreated' AS composite_datetime_created,
    file_metadata->>'ICC_Profile:DeviceModel' AS icc_profile_device_model
FROM
    media;