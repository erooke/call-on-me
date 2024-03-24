import dataclasses
import functools
import hashlib
import pathlib
import shutil

HASH_PREFIX_LENGTH = 8


@dataclasses.dataclass
class FileAsset:
    original_file: str

    @functools.cached_property
    def hash(self) -> str:
        with open(self.original_file, "rb", buffering=0) as f:
            return hashlib.file_digest(f, "sha256").hexdigest()[:HASH_PREFIX_LENGTH]

    @property
    def key(self):
        return pathlib.Path(self.original_file).relative_to("templates/")

    @property
    def relative_path(self) -> str:
        path = pathlib.Path(self.original_file).relative_to("templates/")
        parent = path.parent
        stem = path.stem
        suffix = path.suffix

        return str(parent / f"{stem}.{self.hash}{suffix}")

    def write(self, out_dir: str):
        shutil.copy2(self.original_file, pathlib.Path(out_dir) / self.relative_path)
