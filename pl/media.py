from uuid import uuid4
from pathlib import Path
from datetime import datetime
from exiftool import ExifToolHelper
import hashlib
import mmap


def generate_uuid():
    return str(uuid4())


def get_exif_metadata(file_path):
    TARGET_TAGS = ["ExifToolVersion", "*date*", "*gps*", "*make*", "*model*"]
    with ExifToolHelper(executable="C:/ExifTool/exiftool.exe") as et:
        metadata_list = et.get_tags(file_path, TARGET_TAGS)
        return metadata_list[0]


def sha256_checksum(file_path, chunk_size=8192):
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                for offset in range(0, mm.size(), chunk_size):
                    sha256.update(mm[offset : offset + chunk_size])
        return sha256.hexdigest()
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def generate_media_dimensions(file_path):
    IMPORT_VERSION = "0.0.3"
    IMPORT_TIMESTAMP = int(datetime.now().timestamp())
    IMPORT_MEDIA_DIRECTORY = "D:/"

    file = Path(file_path)

    id = generate_uuid()
    extension = file.suffix.lower()

    return {
        "id": id,
        "name": id + extension,
        "extension": extension,
        "path": IMPORT_MEDIA_DIRECTORY + id + extension,
        "size": file.stat().st_size,
        "source_file": {"name": file.name, "path": file.resolve().as_posix()},
        "extracted_attributes": get_exif_metadata(file),
        "import_timestamp": IMPORT_TIMESTAMP,
        "import_version": IMPORT_VERSION,
        "sha256_hash": sha256_checksum(file),
    }


def move_file(media_dimensions):
    source_path = Path(media_dimensions["source_file"]["path"])
    destination_path = Path(media_dimensions["path"])
    print(destination_path, source_path)
    source_path.rename(destination_path)


# need to make it so only images and videos of specific exts are processed here
# make another script for sidecar files
# and another that is a higher level for both

if __name__ == "__main__":
    dims = generate_media_dimensions(
        "C:/Users/Bradf/OneDrive/Documents/apps/pl/source/IMG_0441_Original.JPEG"
    )

    move_file(dims)
