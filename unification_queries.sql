SELECT
    DISTINCT key
FROM 
    media, LATERAL jsonb_each_text(file_metadata::jsonb) AS metadata;

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

SELECT
    id,
    COALESCE(file_metadata->>'Composite:DateTimeCreated', NULL) AS Composite_DateTimeCreated,
    COALESCE(file_metadata->>'Composite:DigitalCreationDateTime', NULL) AS Composite_DigitalCreationDateTime,
    COALESCE(file_metadata->>'Composite:GPSAltitude', NULL) AS Composite_GPSAltitude,
    COALESCE(file_metadata->>'Composite:GPSAltitudeRef', NULL) AS Composite_GPSAltitudeRef,
    COALESCE(file_metadata->>'Composite:GPSDateTime', NULL) AS Composite_GPSDateTime,
    COALESCE(file_metadata->>'Composite:GPSLatitude', NULL) AS Composite_GPSLatitude,
    COALESCE(file_metadata->>'Composite:GPSLongitude', NULL) AS Composite_GPSLongitude,
    COALESCE(file_metadata->>'Composite:GPSPosition', NULL) AS Composite_GPSPosition,
    COALESCE(file_metadata->>'Composite:SubSecCreateDate', NULL) AS Composite_SubSecCreateDate,
    COALESCE(file_metadata->>'Composite:SubSecDateTimeOriginal', NULL) AS Composite_SubSecDateTimeOriginal,
    COALESCE(file_metadata->>'Composite:SubSecModifyDate', NULL) AS Composite_SubSecModifyDate,
    COALESCE(file_metadata->>'EXIF:CreateDate', NULL) AS EXIF_CreateDate,
    COALESCE(file_metadata->>'EXIF:DateTimeOriginal', NULL) AS EXIF_DateTimeOriginal,
    COALESCE(file_metadata->>'EXIF:GPSAltitude', NULL) AS EXIF_GPSAltitude,
    COALESCE(file_metadata->>'EXIF:GPSAltitudeRef', NULL) AS EXIF_GPSAltitudeRef,
    COALESCE(file_metadata->>'EXIF:GPSDOP', NULL) AS EXIF_GPSDOP,
    COALESCE(file_metadata->>'EXIF:GPSDateStamp', NULL) AS EXIF_GPSDateStamp,
    COALESCE(file_metadata->>'EXIF:GPSDestBearing', NULL) AS EXIF_GPSDestBearing,
    COALESCE(file_metadata->>'EXIF:GPSDestBearingRef', NULL) AS EXIF_GPSDestBearingRef,
    COALESCE(file_metadata->>'EXIF:GPSHPositioningError', NULL) AS EXIF_GPSHPositioningError,
    COALESCE(file_metadata->>'EXIF:GPSImgDirection', NULL) AS EXIF_GPSImgDirection,
    COALESCE(file_metadata->>'EXIF:GPSImgDirectionRef', NULL) AS EXIF_GPSImgDirectionRef,
    COALESCE(file_metadata->>'EXIF:GPSLatitude', NULL) AS EXIF_GPSLatitude,
    COALESCE(file_metadata->>'EXIF:GPSLatitudeRef', NULL) AS EXIF_GPSLatitudeRef,
    COALESCE(file_metadata->>'EXIF:GPSLongitude', NULL) AS EXIF_GPSLongitude,
    COALESCE(file_metadata->>'EXIF:GPSLongitudeRef', NULL) AS EXIF_GPSLongitudeRef,
    COALESCE(file_metadata->>'EXIF:GPSSpeed', NULL) AS EXIF_GPSSpeed,
    COALESCE(file_metadata->>'EXIF:GPSSpeedRef', NULL) AS EXIF_GPSSpeedRef,
    COALESCE(file_metadata->>'EXIF:GPSTimeStamp', NULL) AS EXIF_GPSTimeStamp,
    COALESCE(file_metadata->>'EXIF:GPSTrack', NULL) AS EXIF_GPSTrack,
    COALESCE(file_metadata->>'EXIF:GPSTrackRef', NULL) AS EXIF_GPSTrackRef,
    COALESCE(file_metadata->>'EXIF:GPSVersionID', NULL) AS EXIF_GPSVersionID,
    COALESCE(file_metadata->>'EXIF:LensMake', NULL) AS EXIF_LensMake,
    COALESCE(file_metadata->>'EXIF:LensModel', NULL) AS EXIF_LensModel,
    COALESCE(file_metadata->>'EXIF:Make', NULL) AS EXIF_Make,
    COALESCE(file_metadata->>'EXIF:Model', NULL) AS EXIF_Model,
    COALESCE(file_metadata->>'EXIF:ModifyDate', NULL) AS EXIF_ModifyDate,
    COALESCE(file_metadata->>'ExifTool:ExifToolVersion', NULL) AS ExifTool_ExifToolVersion,
    COALESCE(file_metadata->>'File:FileAccessDate', NULL) AS File_FileAccessDate,
    COALESCE(file_metadata->>'File:FileCreateDate', NULL) AS File_FileCreateDate,
    COALESCE(file_metadata->>'File:FileModifyDate', NULL) AS File_FileModifyDate,
    COALESCE(file_metadata->>'ICC_Profile:DeviceModel', NULL) AS ICC_Profile_DeviceModel,
    COALESCE(file_metadata->>'ICC_Profile:DeviceModelDesc', NULL) AS ICC_Profile_DeviceModelDesc,
    COALESCE(file_metadata->>'ICC_Profile:ProfileDateTime', NULL) AS ICC_Profile_ProfileDateTime,
    COALESCE(file_metadata->>'IPTC:DateCreated', NULL) AS IPTC_DateCreated,
    COALESCE(file_metadata->>'IPTC:DigitalCreationDate', NULL) AS IPTC_DigitalCreationDate,
    COALESCE(file_metadata->>'MakerNotes:DateDisplayFormat', NULL) AS MakerNotes_DateDisplayFormat,
    COALESCE(file_metadata->>'MakerNotes:DateStampMode', NULL) AS MakerNotes_DateStampMode,
    COALESCE(file_metadata->>'MakerNotes:MakerNoteVersion', NULL) AS MakerNotes_MakerNoteVersion,
    COALESCE(file_metadata->>'MakerNotes:ModelReleaseYear', NULL) AS MakerNotes_ModelReleaseYear,
    COALESCE(file_metadata->>'MakerNotes:SonyDateTime', NULL) AS MakerNotes_SonyDateTime,
    COALESCE(file_metadata->>'MakerNotes:SonyDateTime2', NULL) AS MakerNotes_SonyDateTime2,
    COALESCE(file_metadata->>'MakerNotes:SonyModelID', NULL) AS MakerNotes_SonyModelID,
    COALESCE(file_metadata->>'QuickTime:ContentCreateDate', NULL) AS QuickTime_ContentCreateDate,
    COALESCE(file_metadata->>'QuickTime:CreateDate', NULL) AS QuickTime_CreateDate,
    COALESCE(file_metadata->>'QuickTime:CreationDate', NULL) AS QuickTime_CreationDate,
    COALESCE(file_metadata->>'QuickTime:CreationDate-und-US', NULL) AS QuickTime_CreationDate_und_US,
    COALESCE(file_metadata->>'QuickTime:DateTimeOriginal', NULL) AS QuickTime_DateTimeOriginal,
    COALESCE(file_metadata->>'QuickTime:GPSCoordinates', NULL) AS QuickTime_GPSCoordinates,
    COALESCE(file_metadata->>'QuickTime:GPSCoordinates-und-US', NULL) AS QuickTime_GPSCoordinates_und_US,
    COALESCE(file_metadata->>'QuickTime:Make', NULL) AS QuickTime_Make,
    COALESCE(file_metadata->>'QuickTime:Make-und-US', NULL) AS QuickTime_Make_und_US,
    COALESCE(file_metadata->>'QuickTime:MediaCreateDate', NULL) AS QuickTime_MediaCreateDate,
    COALESCE(file_metadata->>'QuickTime:MediaModifyDate', NULL) AS QuickTime_MediaModifyDate,
    COALESCE(file_metadata->>'QuickTime:Model', NULL) AS QuickTime_Model,
    COALESCE(file_metadata->>'QuickTime:Model-und-US', NULL) AS QuickTime_Model_und_US,
    COALESCE(file_metadata->>'QuickTime:ModifyDate', NULL) AS QuickTime_ModifyDate,
    COALESCE(file_metadata->>'QuickTime:TrackCreateDate', NULL) AS QuickTime_TrackCreateDate,
    COALESCE(file_metadata->>'QuickTime:TrackModifyDate', NULL) AS QuickTime_TrackModifyDate,
    COALESCE(file_metadata->>'SourceFile', NULL) AS SourceFile,
    COALESCE(file_metadata->>'XMP:CreateDate', NULL) AS XMP_CreateDate,
    COALESCE(file_metadata->>'XMP:DateCreated', NULL) AS XMP_DateCreated,
    COALESCE(file_metadata->>'XMP:LensModel', NULL) AS XMP_LensModel,
    COALESCE(file_metadata->>'XMP:MetadataDate', NULL) AS XMP_MetadataDate,
    COALESCE(file_metadata->>'XMP:ModifyDate', NULL) AS XMP_ModifyDate,
    COALESCE(file_metadata->>'XMP:PantryCreateDate', NULL) AS XMP_PantryCreateDate,
    COALESCE(file_metadata->>'XMP:PantryDate', NULL) AS XMP_PantryDate,
    COALESCE(file_metadata->>'XMP:PantryDateTimeOriginal', NULL) AS XMP_PantryDateTimeOriginal,
    COALESCE(file_metadata->>'XMP:PantryMetadataDate', NULL) AS XMP_PantryMetadataDate,
    COALESCE(file_metadata->>'XMP:PantryModifyDate', NULL) AS XMP_PantryModifyDate,
    COALESCE(file_metadata->>'XMP:PantryOriginationDate', NULL) AS XMP_PantryOriginationDate
FROM media
