#!/usr/bin/env python3
"""Package only the reusable skill and video runtime."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    root = Path(__file__).resolve().parents[1]
    skill_name = "ai-video-workflow"
    skill = root / "skills" / skill_name
    files = [
        "SKILL.md", "README.md", "references/workflow.md",
        "scripts/run-talk.py", "scripts/beat-map.py", "scripts/env_check.py",
    ]
    runtime_files = [
        "package.json", "package-lock.json", "tsconfig.json",
        "scripts/stage2_whisper.py", "scripts/stage3_video_use.py",
        "src/index.ts", "src/Root.tsx", "src/MainVideo.tsx", "public/storyboard.json",
    ]
    dest = root / "dist/ai-video-workflow-v0.1.0.zip"
    dest.parent.mkdir(exist_ok=True)
    temp = dest.with_suffix(".tmp")
    with ZipFile(temp, "w", compression=ZIP_DEFLATED) as bundle:
        for file in files:
            bundle.write(skill / file, f"{skill_name}/{file}")
        for file in runtime_files:
            bundle.write(root / file, f"{skill_name}/runtime/{file}")
    with ZipFile(temp) as bundle:
        if bundle.testzip() is not None or len(bundle.namelist()) != len(files) + len(runtime_files):
            raise RuntimeError("技能包完整性检查失败")
    temp.replace(dest)
    print(dest)


if __name__ == "__main__":
    main()
