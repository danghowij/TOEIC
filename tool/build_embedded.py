from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import tempfile
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = PROJECT_DIR / "data"
DEFAULT_MARKED_DIR = PROJECT_DIR / "marked"
DEFAULT_TRANSLATIONS = PROJECT_DIR / "translations.json"
DEFAULT_TEMPLATE = Path(__file__).resolve().parent / "template.html"
DEFAULT_OUTPUT = PROJECT_DIR / "index.html"
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
BOOK_NAMES = {"h2": "Hacker 2", "h3": "Hacker 3", "others": "Khác"}
IMAGE_NAME_PATTERN = re.compile(
    r"^(?P<start>\d+)_(?P<answers>[ABCDX]+)"
    r"(?P<extension>\.png|\.jpe?g|\.webp|\.gif)$",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a standalone TOEIC study page with embedded images."
    )
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--marked", type=Path, default=DEFAULT_MARKED_DIR)
    parser.add_argument("--translations", type=Path, default=DEFAULT_TRANSLATIONS)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def make_data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def discover_images(data_dir: Path) -> tuple[list[Path], list[str]]:
    if not data_dir.exists():
        return [], []
    if not data_dir.is_dir():
        return [], [f"{data_dir}: data path is not a directory"]

    images = []
    errors = []
    for path in sorted(data_dir.rglob("*"), key=lambda item: item.as_posix().lower()):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if not IMAGE_NAME_PATTERN.fullmatch(path.name):
            relative = path.relative_to(data_dir).as_posix()
            errors.append(
                f"{relative}: expected <start>_<answers>.<ext>, "
                "for example 156_AXCD.png"
            )
            continue
        images.append(path)
    return images, errors


def load_translations(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    translations = payload.get("translations", {})
    if not isinstance(translations, dict):
        raise SystemExit(f"{path}: 'translations' must be an object")
    return translations


def build_items(
    data_dir: Path,
    marked_dir: Path,
    image_paths: list[Path],
    translations: dict[str, dict],
) -> list[dict]:
    items = []
    for image_path in image_paths:
        relative_path = image_path.relative_to(data_dir).as_posix()
        marked_path = marked_dir / Path(relative_path)
        match = IMAGE_NAME_PATTERN.fullmatch(image_path.name)
        assert match is not None
        start = int(match.group("start"))
        answer_string = match.group("answers").upper()
        questions = {
            str(start + offset): answer
            for offset, answer in enumerate(answer_string)
        }
        folder_path = image_path.parent.relative_to(data_dir)
        folder = folder_path.as_posix() if folder_path.parts else "data"
        book = folder_path.parts[0] if folder_path.parts else "data"
        test = folder_path.parts[1] if len(folder_path.parts) > 1 else "__all__"
        book_label = BOOK_NAMES.get(book.lower(), book)
        test_match = re.search(r"(?:^|-)(?:t|test)(\d+)$", test, re.IGNORECASE)
        if test == "__all__":
            test_label = "Bài tổng hợp"
        else:
            test_label = f"Test {test_match.group(1)}" if test_match else test
        end = start + len(answer_string) - 1
        translation = translations.get(relative_path, {})
        items.append(
            {
                "id": relative_path,
                "folder": folder,
                "book": book,
                "bookLabel": book_label,
                "test": test,
                "testLabel": test_label,
                "title": f"{book_label} · {test_label} · Câu {start}–{end}",
                "questions": questions,
                "image": make_data_uri(image_path),
                "markedImage": make_data_uri(marked_path)
                if marked_path.is_file()
                else make_data_uri(image_path),
                "translation": translation.get("translation", ""),
                "translationStatus": translation.get("status", ""),
            }
        )
    return items


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def main() -> None:
    args = parse_args()
    data_dir = args.data.resolve()
    marked_dir = args.marked.resolve()
    translations = load_translations(args.translations.resolve())
    image_paths, errors = discover_images(data_dir)
    if errors:
        formatted = "\n".join(f"  - {error}" for error in errors)
        raise SystemExit(
            f"Build stopped: {len(errors)} invalid image file(s):\n{formatted}\n"
            "index.html was not changed."
        )

    items = build_items(data_dir, marked_dir, image_paths, translations)
    template = args.template.resolve().read_text(encoding="utf-8")
    payload = json.dumps(
        {"items": items}, ensure_ascii=False, separators=(",", ":")
    ).replace("</", "<\\/")
    if "__TOEIC_DATA__" not in template:
        raise SystemExit("Template is missing the __TOEIC_DATA__ placeholder.")

    output_path = args.output.resolve()
    write_atomic(output_path, template.replace("__TOEIC_DATA__", payload))
    size_mb = output_path.stat().st_size / (1024 * 1024)
    question_count = sum(len(item["questions"]) for item in items)
    folder_count = len({item["folder"] for item in items})
    print(f"Built {output_path}")
    print(
        f"Included {folder_count} folder(s), {len(items)} image(s), "
        f"{question_count} question(s), {size_mb:.2f} MB"
    )


if __name__ == "__main__":
    main()
