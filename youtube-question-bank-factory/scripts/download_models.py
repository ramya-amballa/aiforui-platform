#!/usr/bin/env python3
"""One-time downloader for local TTS model weights.

Internet access is used ONLY here, at install time. After this script
completes, audio synthesis runs fully offline with no external API calls.

Usage:
    python scripts/download_models.py --engine kokoro
    python scripts/download_models.py --engine piper --piper-voice en_US-lessac-medium
    python scripts/download_models.py --engine all
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

KOKORO_FILES = {
    "kokoro-v1.0.onnx": (
        "https://github.com/thewh1teagle/kokoro-onnx/releases/download/"
        "model-files-v1.0/kokoro-v1.0.onnx"
    ),
    "voices-v1.0.bin": (
        "https://github.com/thewh1teagle/kokoro-onnx/releases/download/"
        "model-files-v1.0/voices-v1.0.bin"
    ),
}

PIPER_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main"


def _download(url: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  already present: {dest.name} ({dest.stat().st_size:,} bytes)")
        return
    print(f"  downloading {dest.name} ...")
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url) as resp, open(tmp, "wb") as f:
        total = int(resp.headers.get("Content-Length", 0))
        written = 0
        while chunk := resp.read(1 << 20):
            f.write(chunk)
            written += len(chunk)
            if total:
                pct = written * 100 // total
                print(f"\r  {dest.name}: {pct}%", end="", flush=True)
    print()
    tmp.rename(dest)


def download_kokoro() -> None:
    print("Kokoro (primary local TTS engine):")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in KOKORO_FILES.items():
        _download(url, MODELS_DIR / name)
    print("  Kokoro model files ready in", MODELS_DIR)


def download_piper(voice: str) -> None:
    print(f"Piper (fallback local TTS engine), voice={voice}:")
    # voice id format: <lang>_<REGION>-<name>-<quality>, e.g. en_US-lessac-medium
    parts = voice.split("-")
    if len(parts) != 3:
        print(f"  invalid piper voice id: {voice}", file=sys.stderr)
        sys.exit(1)
    lang_region, name, quality = parts
    lang = lang_region.split("_")[0]
    piper_dir = MODELS_DIR / "piper"
    piper_dir.mkdir(parents=True, exist_ok=True)
    base = f"{PIPER_BASE}/{lang}/{lang_region}/{name}/{quality}/{voice}"
    for ext in (".onnx", ".onnx.json"):
        _download(f"{base}{ext}", piper_dir / f"{voice}{ext}")
    print("  Piper voice ready in", piper_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--engine", choices=["kokoro", "piper", "all"], default="kokoro"
    )
    parser.add_argument(
        "--piper-voice",
        default="en_US-lessac-medium",
        help="Piper voice id (see https://github.com/rhasspy/piper/blob/master/VOICES.md)",
    )
    args = parser.parse_args()

    if args.engine in ("kokoro", "all"):
        download_kokoro()
    if args.engine in ("piper", "all"):
        download_piper(args.piper_voice)

    print("\nDone. All local TTS synthesis from here on requires no network access.")


if __name__ == "__main__":
    main()
