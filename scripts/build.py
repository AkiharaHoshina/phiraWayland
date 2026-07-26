#!/usr/bin/env python3
import argparse
import os
import platform
import shlex
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRPR_AVC_FFMPEG_VERSION = "20260309_v0"
PRPR_AVC_FFMPEG_URL = (
    f"https://github.com/TeamFlos/prpr-avc-ffmpeg/releases/download/"
    f"{PRPR_AVC_FFMPEG_VERSION}"
)


def run(cmd: list[str], **kwargs) -> None:
    print(f"  \033[36m{shlex.join(cmd)}\033[0m")
    subprocess.run(cmd, check=True, **kwargs)


def get_host_target() -> str:
    result = subprocess.run(["rustc", "-vV"], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if line.startswith("host:"):
            return line.split(":", 1)[1].strip()
    sys.exit("ERROR: could not detect host target via `rustc -vV`")


def download_ffmpeg_libs(target: str) -> None:
    dest = PROJECT_ROOT / "prpr-avc" / "static-lib" / target
    if dest.exists():
        print(f"FFmpeg static libs already present: {dest}")
        return

    url = f"{PRPR_AVC_FFMPEG_URL}/{target}.tar.gz"
    print(f"Downloading FFmpeg static libs for {target} ...")
    print(f"  {url}")

    dest.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as resp:
        with tarfile.open(fileobj=resp, mode="r|gz") as tar:
            tar.extractall(path=dest)
    print(f"  extracted -> {dest}")


def build(release: bool) -> None:
    mode = "--release" if release else "--debug"
    cmd = ["cargo", "build", mode, "-p", "phira-main", "--features", "video"]
    print("Building phira ...")
    run(cmd, cwd=PROJECT_ROOT)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build phira with prpr-avc (FFmpeg) dependencies"
    )
    parser.add_argument(
        "--skip-ffmpeg", action="store_true", help="skip FFmpeg static lib download"
    )
    parser.add_argument(
        "--debug", action="store_true", help="build debug instead of release"
    )
    args = parser.parse_args()

    os.chdir(PROJECT_ROOT)

    target = get_host_target()
    print(f"Host target: {target}")

    if not args.skip_ffmpeg:
        download_ffmpeg_libs(target)

    build(release=not args.debug)
    print("\nBuild finished successfully.")


if __name__ == "__main__":
    # sudo dnf install -y wayland-devel mesa-libEGL-devel libxkbcommon-devel alsa-lib-devel zlib-devel libvorbis-devel libogg-devel python3 git
    main()
