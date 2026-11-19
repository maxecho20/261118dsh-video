#!/usr/bin/env python3
"""Build release ZIPs from explicitly listed reader-facing files."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.2.0"
SKILL = "ai-video-workflow"
CASE_FILES = [
    "README.md", "cases/README.md", "cases/01-真人口播.md", "cases/02-苹果手机进化.md", "cases/03-音乐MV.md",
    "docs/项目复盘.md", "docs/歌词剧情MV复现.md",
]
SKILL_FILES = [
    "SKILL.md", "README.md", "references/workflow.md",
    "scripts/run-talk.py", "scripts/beat-map.py", "scripts/env_check.py",
]
RUNTIME_FILES = [
    *CASE_FILES,
    "package.json", "package-lock.json", "tsconfig.json",
    "scripts/stage2_whisper.py", "scripts/stage3_video_use.py", "scripts/prepare_mv_timeline.py",
    "scripts/repro_demo.py", "examples/index.tsx", "examples/mv-plan.json",
    "src/index.ts", "src/Root.tsx", "src/MainVideo.tsx", "public/storyboard.json",
]


def build_zip(name, files):
    dest = ROOT / "dist" / name
    dest.parent.mkdir(exist_ok=True)
    temp = dest.with_suffix(".tmp")
    with ZipFile(temp, "w", compression=ZIP_DEFLATED) as bundle:
        for source, target in files:
            bundle.write(source, target)
    with ZipFile(temp) as bundle:
        if bundle.testzip() is not None or len(bundle.namelist()) != len(files):
            raise RuntimeError("发布包完整性检查失败")
    temp.replace(dest)
    print(dest)


def main():
    build_zip(f"{SKILL}-v{VERSION}.zip", [
        *((ROOT / "skills" / SKILL / file, f"{SKILL}/{file}") for file in SKILL_FILES),
        *((ROOT / file, f"{SKILL}/runtime/{file}") for file in RUNTIME_FILES),
    ])
    build_zip(f"video-case-prompts-v{VERSION}.zip", [(ROOT / file, file) for file in CASE_FILES])


if __name__ == "__main__":
    main()
