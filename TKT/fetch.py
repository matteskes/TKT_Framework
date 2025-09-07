"""
Data fetching and caching utilities.

This module provides two main functions:

- `cached_fetch(url: str, name: str, ttl: int = 3600) -> object`
  Fetch JSON data from a URL with transparent caching. The response is
  stored locally under `$XDG_STATE_HOME/TKT` (or `~/.local/state/TKT`
  if not set). Subsequent calls reuse the cached data until the
  specified time-to-live (TTL) expires.

- `download_file(url: str, quiet: bool = False) -> str`
  Download a file from the given URL and save it to the current
  directory. The output filename is derived from the URL.
  By default, progress is shown in the terminal if the server provides a
  `Content-Length` header. If `quiet` is True, no progress is
  displayed. Existing files are never overwritten.

These utilities are designed for simple use cases where lightweight,
file-based caching and reliable downloads are sufficient without
depending on a database or external cache service.
"""

import json
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from os.path import basename
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from TKT.safe import safe


class FileSize(int):
    __match_args__ = ("_bytes",)

    def __init__(self, byte_num: Any, /):
        byte_num = int(byte_num)
        if byte_num < 0:
            raise ValueError("FileSize must be a non-negative number of bytes")

        self._bytes = byte_num

    def __index__(self) -> int:
        return self._bytes

    def __int__(self) -> int:
        return self._bytes

    def __repr__(self) -> str:
        return f"FileSize({self._bytes!r})"

    def __str__(self) -> str:
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = float(self._bytes)
        i = 0

        while size >= 1024.0 and i < len(units) - 1:
            size /= 1024.0
            i += 1

        value = str(round(size, 2)).rstrip("0").rstrip(".")
        return f"{value} {units[i]}"

    def __iadd__(self, other: int):
        self._bytes += other
        return self


@dataclass(frozen=True)
class FileData:
    name: str
    size: FileSize
    updated_at: datetime
    digest: str
    url: str
    version: str
    tag: str
    distro: str = field(init=False)
    scheduler: str = field(init=False)
    compiler: str = field(init=False)

    _pattern = re.compile(r"[-.]")

    def __post_init__(self):
        parts = self._pattern.split(self.name.replace("-diet", ""))
        if len(parts) < 4:
            raise ValueError(f"Unexpected file name format: {self.name}")
        object.__setattr__(self, "distro", parts[0])
        object.__setattr__(self, "scheduler", parts[2])
        object.__setattr__(self, "compiler", parts[3])


def filename_from_url(url: str) -> str:
    path = urlparse(url).path
    name = basename(path)
    return name or "downloaded.file"


@safe
def cached_fetch(url: str, name: str, ttl: int = 3600) -> Any:
    data_home = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    app_dir = data_home / "TKT"
    app_dir.mkdir(parents=True, exist_ok=True)

    cache_file = app_dir / f"{name}.json"

    now = time.time()
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text())
            timestamp = cached.get("timestamp", 0)
            if now - timestamp < ttl:
                return cached["data"]
        except (json.JSONDecodeError, KeyError, TypeError):
            pass  # treat as cache miss

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    cache_file.write_text(
        json.dumps({"timestamp": now, "data": data}, ensure_ascii=False)
    )
    return data


@safe
def download_file(url: str, output: str | None = None, quiet: bool = False) -> str:
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        output_file = output if output else filename_from_url(url)

        total = FileSize(response.headers.get("Content-Length", 0))  # 0 if missing
        downloaded = FileSize(0)
        elapsed = time.time()
        interval = 0.2  # seconds between updates

        with open(output_file, mode="xb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if not chunk:
                    continue

                file.write(chunk)
                downloaded += len(chunk)

                if not quiet:
                    now = time.time()
                    if total and (now - elapsed > interval or downloaded == total):
                        percent = downloaded / total * 100
                        print(
                            f"\rDownloaded {downloaded}/{total} ({percent:5.1f}%)",
                            end="",
                        )
                        elapsed = now
                    elif now - elapsed > interval:
                        print(f"\rDownloaded {downloaded}", end="")
                        elapsed = now

        if not quiet:
            print(f"\nFinished downloading {output_file} ({downloaded})")

    return output_file


def get_files_from_releases(releases: list[dict[str, Any]]) -> list[FileData]:
    """Parse data about releases fetched from the GitHub API."""
    files: list[FileData] = []

    for release in releases:
        for asset in release["assets"]:
            files.append(
                FileData(
                    version=release["name"],
                    tag=release["tag_name"],
                    name=asset["name"],
                    size=FileSize(asset["size"]),
                    updated_at=datetime.fromisoformat(asset["updated_at"]),
                    digest=asset["digest"],
                    url=asset["browser_download_url"],
                )
            )

    return files
