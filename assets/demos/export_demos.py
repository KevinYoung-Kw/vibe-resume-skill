#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

DEMOS = {
    "hero": {"duration": 11, "fps": 12},
    "qa": {"duration": 7, "fps": 12},
}


def run(command: list[str]) -> None:
    process = subprocess.run(command, capture_output=True, text=True)
    if process.returncode != 0:
        print(" ".join(command))
        print(process.stdout)
        print(process.stderr)
        raise subprocess.CalledProcessError(process.returncode, command)


def require_tools() -> None:
    missing = []
    if not CHROME.exists():
        missing.append(str(CHROME))
    for tool in ("ffmpeg", "gifsicle"):
        if not shutil.which(tool):
            missing.append(tool)
    if missing:
        raise SystemExit("Missing required tools: " + ", ".join(missing))


def capture_frames(name: str, frames_dir: Path, *, duration: int, fps: int) -> None:
    total = duration * fps
    html = ROOT / f"{name}.html"
    if not html.exists():
        raise SystemExit(f"Missing demo HTML: {html}")

    for frame in range(total):
        if frame % max(1, fps) == 0:
            print(f"  capturing {name}: frame {frame + 1}/{total}")
        progress = frame / total
        out = frames_dir / f"frame_{frame:04d}.png"
        url = f"{html.resolve().as_uri()}?capture=1&p={progress:.6f}"
        run(
            [
                str(CHROME),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--window-size=1200,675",
                f"--screenshot={out}",
                url,
            ]
        )


def build_gif(name: str, frames_dir: Path, *, fps: int, width: int, colors: int) -> Path:
    raw_gif = ROOT / f"{name}.raw.gif"
    final_gif = ROOT / f"{name}.gif"
    palette = frames_dir / "palette.png"

    run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(fps),
            "-i",
            str(frames_dir / "frame_%04d.png"),
            "-vf",
            f"fps={fps},scale={width}:-1:flags=lanczos,palettegen=max_colors={colors}",
            str(palette),
        ]
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(fps),
            "-i",
            str(frames_dir / "frame_%04d.png"),
            "-i",
            str(palette),
            "-lavfi",
            f"fps={fps},scale={width}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
            str(raw_gif),
        ]
    )
    run(["gifsicle", "-O3", "--colors", str(colors), str(raw_gif), "-o", str(final_gif)])
    raw_gif.unlink(missing_ok=True)
    return final_gif


def main() -> int:
    parser = argparse.ArgumentParser(description="Export README demo HTML files to optimized GIFs.")
    parser.add_argument("names", nargs="*", default=list(DEMOS), help="Demo names to export.")
    parser.add_argument("--width", type=int, default=960, help="Final GIF width.")
    parser.add_argument("--colors", type=int, default=96, help="GIF palette colors.")
    parser.add_argument("--keep-frames", action="store_true", help="Keep generated PNG frames.")
    args = parser.parse_args()

    require_tools()
    for name in args.names:
        if name not in DEMOS:
            raise SystemExit(f"Unknown demo: {name}. Expected one of: {', '.join(DEMOS)}")
        config = DEMOS[name]
        with tempfile.TemporaryDirectory(prefix=f"vibe-resume-{name}-frames-") as temp:
            frames_dir = Path(temp)
            print(f"Exporting {name}...")
            capture_frames(name, frames_dir, duration=config["duration"], fps=config["fps"])
            final = build_gif(name, frames_dir, fps=config["fps"], width=args.width, colors=args.colors)
            print(f"Created {final} ({final.stat().st_size / 1024 / 1024:.2f} MB)")
            if args.keep_frames:
                keep_dir = ROOT / f"{name}-frames"
                if keep_dir.exists():
                    shutil.rmtree(keep_dir)
                shutil.copytree(frames_dir, keep_dir)
                print(f"Kept frames in {keep_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
