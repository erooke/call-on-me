import dataclasses
import hashlib
import itertools
import pathlib

from PIL import Image, ImageOps

SRCSET_WIDTHS = [
    320,
    480,
    640,
    800,
    960,
    1120,
    1280,
]


@dataclasses.dataclass
class ImageAsset:
    original_name: str
    resized_images: list[Image]

    def _resized_name(self, img: Image):
        basename = pathlib.Path(self.original_name).stem
        hashed = hashlib.sha256(img.tobytes()).hexdigest()[:8]
        return f"/assets/{basename}/{basename}-{img.size[0]}w.{hashed}.webp"

    def tag(self, **kwargs) -> str:
        srcset = [
            f"{self._resized_name(img)} {img.size[0]}w" for img in self.resized_images
        ]
        srcset_str = ", ".join(srcset)

        sizes = []
        for smaller, bigger in itertools.pairwise(self.resized_images):
            smaller_width = smaller.size[0]
            bigger_width = bigger.size[0]

            size = f"(max-width: {bigger_width}px) {smaller_width}px"
            sizes.append(size)

        size_str = ", ".join(sizes) + f", {self.resized_images[-1].size[0]}px"

        biggest_image = self.resized_images[-1]
        src_str = self._resized_name(biggest_image)

        aspect_ratio = f"{biggest_image.size[0]} / {biggest_image.size[1]}"

        attrs = {
            "src": src_str,
            "srcset": srcset_str,
            "sizes": size_str,
            "width": biggest_image.size[0],
            "height": biggest_image.size[1],
            "style": f"aspect-ratio: {aspect_ratio}; max-width: 100%; height: auto",
            **kwargs,
        }

        attr_str = " ".join(f'{key}="{val}"' for key, val in attrs.items())
        tag = f"<img {attr_str} />"
        return tag

    def write(self, out_dir: str):
        for img in self.resized_images:
            file_name = out_dir + self._resized_name(img)
            pathlib.Path(file_name).parent.mkdir(parents=True, exist_ok=True)
            img.save(file_name, "webp")


def resize(image_name: str) -> ImageAsset:
    im = Image.open(image_name)
    original_width, _ = im.size

    resized_images = []
    for size in SRCSET_WIDTHS:
        if size > original_width:
            break

        resized = ImageOps.contain(im, (size, size))
        resized_images.append(resized)

    return ImageAsset(image_name, resized_images)
