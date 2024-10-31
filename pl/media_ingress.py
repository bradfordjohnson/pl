import requests
import json
import csv
import hashlib
import logging
import shutil
import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
from uuid import uuid4
from exiftool import ExifToolHelper
import os


EXIF_TOOL_EXECUTABLE = "C:/ExifTool/exiftool.exe"
TARGET_DIRECTORY = "D:/media"
BASE_URL = "http://127.0.0.1:8000"
MEDIA_ENDPOINT = f"{BASE_URL}/media"
SIDECAR_ENDPOINT = f"{BASE_URL}/sidecar"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("media-ingress.log"), logging.StreamHandler()],
)


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

        logging.info(f"{self.file} -> {self.new_path}")

    @staticmethod
    def generate_uuid():
        return str(uuid4())

    def extract_exif_metadata(self):
        TARGET_TAGS = ["ExifToolVersion", "*date*", "*gps*", "*make*", "*model*"]
        try:
            with ExifToolHelper(executable=EXIF_TOOL_EXECUTABLE) as et:
                metadata = et.get_tags(str(self.file), TARGET_TAGS)
                return metadata[0] if metadata else {}
        except Exception as e:
            logging.error(f"Error extracting EXIF metadata: {e}")
            return {}

    def generate_sha256_checksum(self, chunk_size=8192):
        sha256 = hashlib.sha256()
        try:
            with open(self.file, "rb") as f:
                while chunk := f.read(chunk_size):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logging.error(f"Error generating SHA-256 checksum: {e}")
            return ""

    def move(self):
        try:
            self.target_directory.mkdir(parents=True, exist_ok=True)
            shutil.move(self.source_file["path"], self.new_path)
            logging.info(f"Moved file to {self.new_path}")
            return self.new_path
        except Exception as e:
            logging.error(f"Error moving file: {e}")
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
            "source_name": self.source_file["name"],
            "source_extension": self.extension,
            "size": self.size,
            "sha256": self.sha256,
            "file_metadata": row,
        }
        try:
            response = requests.post(MEDIA_ENDPOINT, json=payload, timeout=10)
            response.raise_for_status()
            logging.info(f"Upload successful: {response.json()}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Upload failed: {e} | Payload: {json.dumps(payload)}")


class SidecarFile:
    def __init__(self, path: Path):
        self.file = path
        self.extension = self.file.suffix.lower()
        self.source_path = self.file.resolve().as_posix()
        self.metadata = self.extract_metadata()

    def extract_metadata(self):
        """Extract metadata based on file extension."""
        try:
            if self.extension == ".json":
                return self._load_json()
            elif self.extension == ".csv":
                return self._load_csv()
            elif self.extension == ".xmp":
                return self._load_xmp()
        except Exception as e:
            logging.error(f"Error extracting metadata: {e}")
            return {}

    def _load_json(self):
        try:
            with self.file.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logging.error(f"Error reading JSON file: {e}")
            return {}

    def _load_csv(self):
        try:
            csv_data = pd.read_csv(self.file, encoding="utf-8")
            rows = csv_data.to_dict(orient="records")
            return [
                {
                    "name": self.file.name,
                    "source_path": self.source_path,
                    "source_extension": self.extension,
                    "file_metadata": row,
                }
                for row in rows
            ]
        except Exception as e:
            logging.error(f"Error reading CSV file: {e}")
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
            logging.error(f"Error reading XMP file: {e}")
            return {}

    def upload_data(self):
        success = True

        if isinstance(self.metadata, list):
            for row in self.metadata:
                if not self._upload_row(row):
                    success = False
        else:
            success = self._upload_row(self.metadata)

        if success:
            self.cleanup()

    def _upload_row(self, row):
        payload = {
            "id": MediaFile.generate_uuid(),
            "name": self.file.name,
            "source_path": self.source_path,
            "source_extension": self.extension,
            "file_metadata": row,
        }
        try:
            response = requests.post(SIDECAR_ENDPOINT, json=payload, timeout=10)
            response.raise_for_status()
            logging.info(f"Upload successful: {response.json()}")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(
                f"Sidecar upload failed: {e} | Payload: {json.dumps(payload, indent=2)}"
            )
            return False

    def cleanup(self):
        try:
            os.remove(self.file)
            logging.info(f"Removed sidecar file: {self.file}")
        except Exception as e:
            logging.error(f"Failed to remove sidecar file: {e}")


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

        logging.info(
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
    media_dir = MediaDirectory("D:/all/all/all")
    media_dir.scan_directory()
    media_dir.import_media_files()
    media_dir.import_sidecar_files()
