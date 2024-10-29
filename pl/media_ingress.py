from pathlib import Path
from exiftool import ExifToolHelper
import hashlib
from uuid import uuid4
import shutil
import json
import csv
import xml.etree.ElementTree as ET
import pandas as pd

EXIF_TOOL_EXECUTABLE = "C:/ExifTool/exiftool.exe"
TARGET_DIRECTORY = "pl/tests"
BASE_URL = "http://127.0.0.1:8000"
MEDIA_ENDPOINT = f"{BASE_URL}/media"
SIDECAR_ENDPOINT = f"{BASE_URL}/sidecar"


class MediaFile:
    def __init__(self, path):
        self.file = path
        self.extension = self.file.suffix.lower()
        self.size = self.file.stat().st_size

        self.uuid = self.generate_uuid()
        self.target_directory = Path(TARGET_DIRECTORY)
        self.new_name = f"{self.uuid}{self.extension}"
        self.new_path = Path(self.target_directory / self.new_name)

        self.source_file = {
            "name": self.file.name,
            "path": self.file.resolve().as_posix(),
        }
        self.sha256 = self.generate_sha256_checksum()
        self.metadata = self.extract_exif_metadata()

        print(f"{self.file} -> {self.new_path}")

    @staticmethod
    def generate_uuid():
        return str(uuid4())

    def extract_exif_metadata(self):
        TARGET_TAGS = ["ExifToolVersion", "*date*", "*gps*", "*make*", "*model*"]
        with ExifToolHelper(executable=EXIF_TOOL_EXECUTABLE) as et:
            metadata = et.get_tags(str(self.file), TARGET_TAGS)
            return metadata[0] if metadata else {}

    def generate_sha256_checksum(self, chunk_size=8192):
        sha256 = hashlib.sha256()
        try:
            with open(self.file, "rb") as f:
                while chunk := f.read(chunk_size):
                    sha256.update(chunk)

            return sha256.hexdigest()

        except Exception as e:
            print(f"Error generating SHA-256 checksum: {e}")
            return ""

    def move(self):
        try:
            self.target_directory.mkdir(parents=True, exist_ok=True)

            source_path = Path(self.source_file["path"])
            target_path = self.new_path
            shutil.move(source_path, target_path)

            print(f"Moved file to {target_path}")

            return target_path

        except Exception as e:
            print(f"Error moving file: {e}")

            return None

    def upload_data(self):
        if isinstance(self.metadata, list):
            for row in self.metadata:
                self._upload_row(row)
        else:
            self._upload_row(self.metadata)

    def _upload_row(self, row):
        payload = {
            "id": self.uuid,
            "name": self.new_name,
            "path": self.new_path.resolve().as_posix(),
            "extension": self.extension,
            "source_path": self.source_file["path"],
            "source_extension": self.extension,
            "size": self.size,
            "sha256": self.sha256,
            "file_metadata": row,
        }
        print(payload)


class SidecarFile:
    def __init__(self, path):
        self.file = path
        self.extension = self.file.suffix.lower()
        self.source_path = self.file.resolve().as_posix()
        self.metadata = self.extract_metadata()

        # print(self.metadata)

    def extract_metadata(self):
        if self.extension == ".json":
            self.metadata = self._load_json()
        elif self.extension == ".csv":
            self.metadata = self._load_csv()
        elif self.extension == ".xmp":
            self.metadata = self._load_xmp()
        return self.metadata

    def _load_json(self):
        try:
            with self.file.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading JSON file: {e}")
            return {}

    def _load_csv(self):
        try:
            csv = pd.read_csv(self.file, encoding="utf-8")

            rows = csv.to_dict(orient="records")

            result = []
            for row in rows:
                combined_row = {
                    "name": self.file.name,
                    "source_path": self.source_path,
                    "source_extension": self.extension,
                    "file_metadata": row,
                }
                result.append(combined_row)

            return result
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return []

    def _load_xmp(self):
        metadata = {}
        try:
            tree = ET.parse(self.file)
            root = tree.getroot()

            def strip_namespace(tag):
                return tag.split("}")[-1] if "}" in tag else tag

            for element in root.iter():
                tag = strip_namespace(element.tag)
                if element.text and element.text.strip():
                    metadata[tag] = element.text.strip()
                for key, value in element.attrib.items():
                    metadata[f"{tag}_{strip_namespace(key)}"] = value

            return metadata
        except (ET.ParseError, FileNotFoundError) as e:
            print(f"Error reading XMP file: {e}")
            return {}

    def upload_data(self):
        if isinstance(self.metadata, list):
            for row in self.metadata:
                self._upload_row(row)
        else:
            self._upload_row(self.metadata)

    def _upload_row(self, row):
        payload = {
            "name": self.file.name,
            "source_path": self.source_path,
            "source_extension": self.extension,
            "file_metadata": row,
        }
        print(payload)


class MediaDirectory:
    def __init__(self, directory_path):
        self.dir = Path(directory_path)
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

        for file in self.dir.iterdir():
            if file.suffix.lower() in MEDIA_EXTENSIONS:
                media_file = MediaFile(file)
                self.media_files.append(media_file)
            elif file.suffix.lower() in SIDECAR_EXTENSIONS:
                sidecar_file = SidecarFile(file)
                self.sidecar_files.append(sidecar_file)

        print(
            f"Found {len(self.media_files)} media files and {len(self.sidecar_files)} sidecar files."
        )

    def import_media_files(self):
        for file in self.media_files:
            file.upload_data()
            file.move()

    def import_sidecar_files(self):
        for file in self.sidecar_files:
            file.upload_data()


if __name__ == "__main__":
    media_dir = MediaDirectory("pl/test")

    media_dir.scan_directory()

    media_dir.import_media_files()

    media_dir.import_sidecar_files()
