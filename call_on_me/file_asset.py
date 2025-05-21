import dataclasses
import functools
import hashlib
import pathlib
import shutil

HASH_PREFIX_LENGTH = 8


@dataclasses.dataclass
class FileAsset:
    original_file: pathlib.Path

    @functools.cached_property
    def hash(self) -> str:
        with open(self.original_file, "rb", buffering=0) as f:
            return hashlib.file_digest(f, "sha256").hexdigest()[:HASH_PREFIX_LENGTH]

    @property
    def key(self) -> str:
        return str(pathlib.Path(self.original_file).relative_to("templates/"))

    @property
    def relative_path(self) -> pathlib.Path:
        path = pathlib.Path(self.original_file).relative_to("templates/")
        parent = path.parent
        stem = path.stem
        suffix = path.suffix

        return parent / f"{stem}.{self.hash}{suffix}"

    @property
    def absolute_path(self) -> pathlib.Path:
        return pathlib.Path("/") / self.relative_path

    def write(self, out_dir: pathlib.Path):
        (out_dir / self.relative_path.parent).mkdir(exist_ok=True, parents=True)
        shutil.copy2(self.original_file, out_dir / self.relative_path)
