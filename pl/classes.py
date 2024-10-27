from pathlib import Path
from uuid import uuid4
from exiftool import ExifToolHelper
import hashlib
from datetime import datetime
import shutil


class APIClient:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.media_endpoint = "/media"
        self.sidecar_endpoint = "/sidecar"

    def post_media(self, media_handler: "MediaFileHandler"):
        url = f"{self.base_url}{self.media_endpoint}"

        payload = {
            "id": media_handler.id,
            "name": media_handler.name,
            "extension": media_handler.extension,
            "path": media_handler.path,
            "size": media_handler.size,
            "source_file": media_handler.source_file,
            "metadata": media_handler.metadata,
            "import_version": media_handler.import_version,
        }
        print(url, payload) # need to add post request
        
    def post_sidecar(self):
        pass


class MediaFileHandler:
    def __init__(self, media_file: "MediaFile"):
        self.import_version = "0.0.1"
        self.import_timestamp = int(datetime.now().timestamp())
        self.target_directory = Path("test/target")

        self.id = self.generate_uuid()
        self.extension = media_file.extension
        self.name = f"{self.id}{self.extension}"
        self.path = self.target_directory / self.name
        self.size = media_file.size
        self.source_file = media_file.source_file

        self.metadata = self.extract_exif_metadata(media_file.file)
        self.sha256 = self.generate_sha256_checksum(media_file.file)

    def generate_uuid(self) -> str:
        return str(uuid4())

    def extract_exif_metadata(self, file_path):
        TARGET_TAGS = ["ExifToolVersion", "*date*", "*gps*", "*make*", "*model*"]

        with ExifToolHelper(executable="C:/ExifTool/exiftool.exe") as et:
            metadata_list = et.get_tags(str(file_path), TARGET_TAGS)
            return metadata_list[0] if metadata_list else {}

    def generate_sha256_checksum(self, file_path: Path, chunk_size: int = 8192) -> str:
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            print(f"Error generating SHA-256 checksum: {e}")
            return ""

    def move_file(self):
        try:
            self.target_directory.mkdir(parents=True, exist_ok=True)

            source_path = Path(self.source_file["path"])
            target_path = self.path

            shutil.move(str(source_path), str(target_path))
            print(f"Moved file to {target_path}")
            return target_path
        except Exception as e:
            print(f"Error moving file: {e}")
            return None


class MediaFile:
    def __init__(self, file_path: str):
        self.file = Path(file_path)
        self.extension = self.file.suffix.lower()
        self.size = self.file.stat().st_size
        self.source_file = {
            "name": self.file.name,
            "path": self.file.resolve().as_posix(),
        }


class MediaLibrary:
    def __init__(self, source_dir: str):
        self.source_dir = Path(source_dir)
        self.media_files = []
        self.sidecar_files = []

    def scan_directory(self) -> str:
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
        api_client = APIClient()
        for media_file in self.media_files:
            media_handler = MediaFileHandler(media_file)
            api_client.post_media(media_handler)

            moved_file_path = media_handler.move_file()
            if moved_file_path:
                media_handler.path = moved_file_path

        print(f"Imported {len(self.media_files)} media files.")
        pass

    def import_sidecars(self):
        pass


if __name__ == "__main__":
    media_library = MediaLibrary("test/source")
    media_library.scan_directory()
    media_library.import_media()
