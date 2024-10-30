# PL - Photo Library

PL is a personal photo unifier designed to streamline the processing and management of media files for effective personal data backup.

---

## Media Ingress

The `media_ingress.py` script is designed for efficiently extracting, processing, and uploading media file metadata and associated sidecar files. This script leverages ExifTool to extract metadata from various media file types and organizes the extracted data into a structured format for further processing.

### Data Extraction

The script focuses on the following types of media files:

- **Media Files**: Common formats such as JPEG, PNG, HEIC, RAW, MP4, and MOV.
- **Sidecar Files**: Metadata files in JSON, CSV, and XMP formats.

### Extracted Data

**Metadata Extraction**: Utilizes ExifTool to retrieve key tags, including:

- ExifTool version
- Date and time information
- GPS coordinates
- Camera make and model

**Checksum Generation**: Computes a SHA-256 checksum for each media file, ensuring data integrity during transfers.

**UUID Generation**: Generates a unique identifier (UUID) for each media file, facilitating easy reference and tracking within the system.

### Schema

Each media file is represented by the following attributes:

| Attribute        | Type       | Description                                     |
| ---------------- | ---------- | ----------------------------------------------- |
| id               | UUID       | Unique identifier for the media file.           |
| name             | Text       | Name of the media file.                         |
| path             | Text       | Path to the media file in the target directory. |
| extension        | String(10) | File extension of the media file.               |
| source_path      | Text       | Original path of the media file.                |
| source_extension | String(10) | File extension of the original media file.      |
| size             | BigInteger | Size of the media file in bytes.                |
| sha256           | Text       | SHA-256 checksum of the media file.             |
| file_metadata    | JSONB      | Extracted metadata from the media file.         |

### Sidecar Files

Sidecar files are additional metadata files associated with media files. They store supplementary information that can enhance the understanding and context of the primary media content. Supported formats include JSON, CSV, and XMP.

**Sidecar Schema**: Each sidecar file is represented by the following attributes:

| Attribute        | Type       | Description                               |
| ---------------- | ---------- | ----------------------------------------- |
| name             | Text       | Name of the sidecar file.                |
| source_path      | Text       | Original path of the sidecar file.       |
| source_extension | String(10) | File extension of the sidecar file.      |
| file_metadata    | JSONB      | Extracted metadata from the sidecar file. |

The `file_metadata` attribute can contain various types of information depending on the format of the sidecar file. For example, JSON and CSV files can hold structured data, while XMP files can include a wide range of metadata tags.

### Classes Overview

**MediaFile**: The `MediaFile` class is responsible for handling individual media files. It extracts metadata, generates checksums and UUIDs, and moves files to the target directory. Key methods include:

- `generate_uuid()`: Generates a new UUID for the media file.
- `extract_exif_metadata()`: Extracts relevant metadata tags using ExifTool.
- `generate_sha256_checksum()`: Calculates the SHA-256 checksum for the media file.
- `move()`: Moves the media file to a designated target directory.
- `upload_data()`: Prepares and outputs the data for uploading, structured as a JSON-like payload.

**SidecarFile**: The `SidecarFile` class manages metadata files associated with media files. It extracts data from JSON, CSV, and XMP formats, allowing the user to maintain a cohesive structure across media and its metadata. Key methods include:

- `extract_metadata()`: Determines the file type and extracts metadata accordingly.
- `_load_json(), _load_csv(), _load_xmp()`: Methods for loading metadata from respective file types.
- `upload_data()`: Prepares and outputs the sidecar data for uploading.
- `cleanup()`: Deletes the sidecar file after successful upload to free up space and maintain organization.

**MediaDirectory**: The `MediaDirectory` class is responsible for scanning a specified directory for media and sidecar files. It organizes the files into appropriate classes and manages the import process. Key methods include:

- `scan_directory()`: Scans the directory and populates lists of media and sidecar files.
- `import_media_files()`: Imports and processes media files.
- `import_sidecar_files()`: Imports and processes sidecar files.

### Upcoming Features

- [ ] **Duplicate Identification**: Mechanisms to identify and manage duplicate media files.
- [ ] **Stacks**: Support for organizing related media files into stacks for easier management.
- [ ] **Metadata Repair**: Tools to fix and enhance metadata accuracy across media files.
- [ ] **Backup Pipeline**: A systematic approach for creating backups and ensuring data redundancy for media files.
