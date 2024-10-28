from pathlib import Path
from exiftool import ExifToolHelper
import hashlib
from uuid import uuid4
import shutil

EXIF_TOOL_EXECUTABLE = "C:/ExifTool/exiftool.exe"
TARGET_DIRECTORY = "pl/tests"

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
        

        # print(self.source_file)
        # print(self.extract_exif_metadata())
        # print(self.generate_sha256_checksum())
        print(f"{self.file} -> {self.new_path}")
        
        
        # self.upload_data()
    
    def generate_uuid(self):
        return str(uuid4())

    def extract_exif_metadata(self):
        TARGET_TAGS = ["ExifToolVersion", "*date*", "*gps*", "*make*", "*model*"]
        with ExifToolHelper(executable=EXIF_TOOL_EXECUTABLE) as et:
            metadata = et.get_tags(str(self.file), TARGET_TAGS)
            return metadata[0] if metadata else {}
    
    def generate_sha256_checksum(self, chunk_size = 8192):
        sha256 = hashlib.sha256()
        try:
            with open(self.file, "rb") as f:
                while chunk := f.read(chunk_size):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            print(f"Error generating SHA-256 checksum: {e}")
            return ""

    def move(self): # need to add call for move method in script for import
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
        payload = {
            "id": self.uuid,
            "name": self.new_name,
            "path": self.new_path.resolve().as_posix(),
            "exif_metadata": self.extract_exif_metadata(),
            "sha256_checksum": self.generate_sha256_checksum()
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
                self.sidecar_files.append(file)
                
        print(f"Found {len(self.media_files)} media files and {len(self.sidecar_files)} sidecar files.")
        
    # def import_media_files(self):
    #     for file in self.media_files:
    #         MediaFile

if __name__ == "__main__":
    media_dir = MediaDirectory("pl/test")
    
    media_dir.scan_directory()
    
    