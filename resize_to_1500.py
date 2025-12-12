import sys
from pathlib import Path
from PIL import Image

# Max widths for different orientations
MAX_WIDTH_LANDSCAPE = 1500
MAX_WIDTH_PORTRAIT = 900  # tweak this to taste

VALID_EXTS = (".jpg", ".jpeg", ".png")
JPEG_QUALITY = 75  # lower = smaller file, try 70–80


def save_as_jpeg(img: Image.Image, out_path: Path):
    """Save an image as compressed JPEG, handling alpha if needed."""
    # Handle transparency (PNG with alpha) by compositing on white
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        bg = Image.new("RGB", img.size, (255, 255, 255))  # white background
        bg.paste(img, mask=img.split()[-1])  # last channel is alpha
        img = bg
    else:
        img = img.convert("RGB")

    img.save(
        out_path,
        quality=JPEG_QUALITY,
        optimize=True,
        progressive=True,
    )

def resize_image_file(path: Path):
    if not path.is_file():
        return
    if path.suffix.lower() not in VALID_EXTS:
        return

    with Image.open(path) as img:
        width, height = img.size

        # Determine if image is portrait (vertical) or landscape
        is_portrait = height > width

        # Choose max width based on orientation
        max_width = MAX_WIDTH_PORTRAIT if is_portrait else MAX_WIDTH_LANDSCAPE

        # Output filename: <name>_<max_width>.jpg in SAME folder (always JPEG)
        out_path = path.with_name(f"{path.stem}_{max_width}.jpg")

        if width <= max_width:
            # No resize, just recompress as JPEG (and convert PNG -> JPEG)
            save_as_jpeg(img, out_path)
            orientation = "portrait" if is_portrait else "landscape"
            print(f"{path.name}: {orientation}, <= {max_width}px, saved as {out_path.name}")
            return

        scale = max_width / width
        new_width = int(width * scale)
        new_height = int(height * scale)

        resized = img.resize((new_width, new_height), Image.LANCZOS)
        save_as_jpeg(resized, out_path)

        orientation = "portrait" if is_portrait else "landscape"
        print(
            f"{path.name} ({orientation}): "
            f"{width}x{height} -> {new_width}x{new_height} ({out_path.name})"
        )


def process_path(p: Path):
    if p.is_dir():
        for child in p.iterdir():
            resize_image_file(child)
    else:
        resize_image_file(p)


def main():
    if len(sys.argv) < 2:
        print("Usage: run this with one or more files/folders as arguments.")
        return

    for arg in sys.argv[1:]:
        process_path(Path(arg))


if __name__ == "__main__":
    main()
