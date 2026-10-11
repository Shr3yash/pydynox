"""Generate site/llms.txt from the documentation navigation after building the site."""

from __future__ import annotations

import re
import tomllib
from collections.abc import Iterator
from pathlib import Path, PurePosixPath
from typing import TypeAlias
from urllib.parse import urljoin, urlsplit, urlunsplit

Navigation: TypeAlias = str | list["Navigation"] | dict[str, "Navigation"]


def pages(navigation: Navigation, title: str | None = None) -> Iterator[tuple[str | None, str]]:
    """Yield the page paths and explicit titles in a navigation section."""
    if isinstance(navigation, str):
        yield title, navigation
    elif isinstance(navigation, list):
        for entry in navigation:
            yield from pages(entry)
    else:
        for label, entry in navigation.items():
            yield from pages(entry, label)


def page_link(
    title: str | None,
    source: str,
    docs_dir: Path,
    site_dir: Path,
    site_url: str,
    directory_urls: bool,
) -> str:
    """Create a link, checking that local pages exist in the built site."""
    url = urlsplit(source)
    if url.scheme in {"http", "https"}:
        return f"- [{title or source}]({source})"

    path = PurePosixPath(url.path)
    target = path
    if path.suffix == ".md":
        if title is None:
            markdown = (docs_dir / path).read_text(encoding="utf-8")
            heading = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
            title = heading[1].strip() if heading else path.stem.replace("-", " ").title()
        target = path.with_suffix(".html")
        if directory_urls and path.name != "index.md":
            target = path.with_suffix("") / "index.html"

    if not (site_dir / target).is_file():
        raise FileNotFoundError(
            f"Navigation page {source!r} has no built file: {site_dir / target}"
        )

    public_path = target.as_posix()
    if directory_urls and path.suffix == ".md" and target.name == "index.html":
        public_path = public_path.removesuffix("index.html")
    public_url = urljoin(
        site_url.rstrip("/") + "/",
        urlunsplit(("", "", public_path, url.query, url.fragment)),
    )
    return f"- [{title or path.stem}]({public_url})"


def generate_llms(config_path: Path) -> Path:
    """Write an index using the configured site URL, directories, and navigation."""
    with config_path.open("rb") as config_file:
        config = tomllib.load(config_file)
    # Accept both the repository's flat configuration and Zensical's project table.
    config = config.get("project", config)
    root = config_path.parent
    docs_dir = root / config.get("docs_dir", "docs")
    site_dir = root / config.get("site_dir", "site")
    lines = [f"# {config['site_name']}", "", f"> {config['site_description']}"]

    for section in config["nav"]:
        for heading, navigation in section.items():
            lines.extend(["", f"## {heading}", ""])
            for title, source in pages(navigation, heading):
                lines.append(
                    page_link(
                        title,
                        source,
                        docs_dir,
                        site_dir,
                        config["site_url"],
                        config.get("use_directory_urls", True),
                    )
                )

    output = site_dir / "llms.txt"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    print(generate_llms(Path(__file__).resolve().parents[1] / "zensical.toml"))
