from pathlib import Path
from uuid import uuid4
from exiftool import ExifToolHelper
import hashlib


class MediaFile:
    IMPORT_MEDIA_DIRECTORY = "D:/"

    def __init__(self, file_path):
        self.file_path = Path(file_path)

        self.id = self.generate_uuid()
        self.extension = self.file_path.suffix.lower()
        self.name = f"{self.id}{self.extension}"
        self.path = f"{self.IMPORT_MEDIA_DIRECTORY}{self.name}"

        self.metadata = self.get_exif_metadata(self.file_path)
        self.size = self.file_path.stat().st_size
        self.sha256_hash = self.sha256_checksum(self.file_path)

        self.source_file = {
            "name": self.file_path.name,
            "path": self.file_path.resolve().as_posix(),
        }

    @staticmethod
    def generate_uuid():
        return str(uuid4())

    @staticmethod
    def get_exif_metadata(file_path):
        TARGET_TAGS = ["ExifToolVersion", "*date*", "*gps*", "*make*", "*model*"]

        with ExifToolHelper(executable="C:/ExifTool/exiftool.exe") as et:
            metadata_list = et.get_tags(str(file_path), TARGET_TAGS)
            return metadata_list[0] if metadata_list else {}

    @staticmethod
    def sha256_checksum(file_path, chunk_size=8192):
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()

    def generate_media_dimensions(self):
        return {
            "id": self.id,
            "name": self.name,
            "extension": self.extension,
            "path": self.path,
            "size": self.size,
            "source_file": self.source_file,
            "extracted_attributes": self.metadata,
            "sha256_hash": self.sha256_hash,
        }


class MediaLibrary:
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)
        self.media_files = []
        self.sidecar_files = []

    def scan_directory(self):
        MEDIA_EXTENSIONS = {
            ".jpg",
            ".jpeg",
            ".png",
            ".heic",
            ".raw",
            ".arw",
            ".img",
            ".mp4",
            ".mov",
        }
        SIDECAR_EXTENSIONS = {".xmp", ".json", ".csv"}

        for file in self.source_dir.iterdir():
            if file.suffix.lower() in MEDIA_EXTENSIONS:
                media_file = MediaFile(file)
                self.media_files.append(media_file)
            elif file.suffix.lower() in SIDECAR_EXTENSIONS:
                self.sidecar_files.append(file)

        print(
            f"Found {len(self.media_files)} media files and {len(self.sidecar_files)} sidecar files."
        )

    def import_media(self):
        self.scan_directory()
        for media_file in self.media_files:
            print(media_file.generate_media_dimensions())

    def import_sidecars(self):
        pass

    def report_results(self):
        pass


if __name__ == "__main__":
    media_lib = MediaLibrary("test/source")
    media_lib.import_media()