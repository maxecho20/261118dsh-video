#!/usr/bin/env python3
"""AI 视频工作流 —— 环境预检（Pre-flight Check）。

在跑正式任务前先执行本脚本，自动探测依赖并按案例类型标注是否必需：
  口播 / 产品动画 / 音乐 MV 三类共同依赖 FFmpeg、Node；
  口播额外要 faster-whisper；音乐 MV 额外要 librosa（可用 NumPy+SciPy 的 --onsets-only 兜底）。

只依赖标准库，任何 Python 3 都能运行（即使某个库未安装也能报告缺项）。
按操作系统（macOS / Linux / Windows）给出对应的安装提示。

退出码：0 = 必需依赖就绪；1 = 存在必需依赖缺失（Agent 应停下并提示用户补齐）。
"""

import os
import platform
import shutil
import subprocess
from pathlib import Path

COMMON_PYTHON_PATHS = [
    "/usr/local/bin/python3",
    "/opt/homebrew/bin/python3",
    "/usr/bin/python3",
    "/usr/bin/python",
]
COMMON_TOOL_DIRS = ["/opt/homebrew/bin", "/usr/local/bin"]


def _run(cmd, timeout=20, env=None):
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        out = (proc.stdout or "").strip() or (proc.stderr or "").strip()
        return proc.returncode == 0, out.splitlines()[0] if out else ""
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def _find_pythons():
    candidates = ["python3", "python", "python3.13", "python3.12", "python3.11", "python3.10"]
    seen, paths = set(), []
    for name in candidates:
        path = shutil.which(name)
        if path and path not in seen:
            seen.add(path)
            paths.append(path)
    for path in COMMON_PYTHON_PATHS:
        if Path(path).is_file() and path not in seen:
            seen.add(path)
            paths.append(path)
    uv = shutil.which("uv")
    if uv:
        try:
            proc = subprocess.run([uv, "python", "find"], capture_output=True, text=True, timeout=20)
            if proc.returncode == 0:
                for line in proc.stdout.splitlines():
                    line = line.strip()
                    if line and line not in seen:
                        seen.add(line)
                        paths.append(line)
        except Exception:  # noqa: BLE001
            pass
    return paths


def _tool(name):
    path = shutil.which(name)
    if path:
        return path
    for d in COMMON_TOOL_DIRS:
        candidate = Path(d) / name
        if candidate.is_file():
            return str(candidate)
    return None


def _system():
    system = platform.system()
    return {"Darwin": "macOS", "Linux": "Linux", "Windows": "Windows"}.get(system, system)


def _install_hints():
    return {
        "macOS": {
            "faster-whisper": "python3 -m pip install faster-whisper",
            "librosa": "python3 -m pip install 'librosa==0.11.0'",
            "ffmpeg": "brew install ffmpeg",
            "node": "brew install node",
        },
        "Linux": {
            "faster-whisper": "python3 -m pip install --user faster-whisper",
            "librosa": "python3 -m pip install --user 'librosa==0.11.0'",
            "ffmpeg": "sudo apt-get update && sudo apt-get install -y ffmpeg",
            "node": "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs",
        },
        "Windows": {
            "faster-whisper": "py -m pip install faster-whisper",
            "librosa": "py -m pip install 'librosa==0.11.0'",
            "ffmpeg": "scoop install ffmpeg   # 或: winget install Gyan.FFmpeg",
            "node": "winget install OpenJS.NodeJS.LTS",
        },
    }


def main():
    os_name = _system()
    hints = _install_hints().get(os_name, _install_hints()["macOS"])
    problems = []       # 必需依赖缺失（faster-whisper / ffmpeg / node）
    soft_problems = []  # 可选依赖缺失（librosa，仅音乐 MV）

    pythons = _find_pythons()

    print("[AI 视频工作流] 环境预检")
    print(f"操作系统: {os_name} ({platform.system()})")
    print()

    # 1. Python + faster-whisper（口播必需）
    print("[1/4] Python + faster-whisper（口播必需）")
    good_python = None
    for py in pythons:
        ok, ver = _run([py, "-c", "import faster_whisper; print(faster_whisper.__version__)"])
        if ok:
            good_python = py
            print(f"  可用解释器: {py}  (faster-whisper {ver})")
            break
    if not good_python:
        problems.append("faster-whisper")
        print("  未找到可 import faster-whisper 的 Python 解释器")
        print(f"  安装提示: {hints['faster-whisper']}")
    print()

    # 2. FFmpeg（所有案例必需）
    print("[2/4] FFmpeg（所有案例必需）")
    ffmpeg = _tool("ffmpeg")
    ffprobe = _tool("ffprobe")
    if ffmpeg and ffprobe:
        _, ff_ver = _run([ffmpeg, "-version"])
        print(f"  ffmpeg: {ff_ver}  ({ffmpeg})")
        print(f"  ffprobe: {ffprobe}")
    else:
        problems.append("ffmpeg")
        print("  缺少 ffmpeg / ffprobe")
        print(f"  安装提示: {hints['ffmpeg']}")
    print()

    # 3. Node + npm（所有案例必需）
    print("[3/4] Node.js（所有案例必需）")
    node = _tool("node")
    npm = _tool("npm")
    if node and npm:
        _, node_ver = _run([node, "--version"])
        # npm/npx 的 shebang 是 "#!/usr/bin/env node"，node 不在 PATH 时即使找到 npm 也跑不起来。
        node_dir = str(Path(node).parent)
        env = os.environ.copy()
        env["PATH"] = node_dir + os.pathsep + env.get("PATH", "")
        npm_ok, npm_ver = _run([npm, "--version"], env=env)
        print(f"  node: {node_ver}  ({node})")
        if npm_ok:
            print(f"  npm: {npm_ver}")
        else:
            problems.append("npm")
            print(f"  npm 找到但无法运行（{npm_ver}），请把 node 所在目录加入 PATH")
    else:
        problems.append("node")
        print("  缺少 node / npm")
        print(f"  安装提示: {hints['node']}")
    print()

    # 4. librosa（音乐 MV 可选，有 numpy/scipy 兜底）
    print("[4/4] librosa（音乐 MV 可选）")
    if good_python:
        lib_ok, lib_ver = _run([good_python, "-c", "import librosa; print(librosa.__version__)"])
    else:
        lib_ok, lib_ver = False, ""
    if lib_ok:
        print(f"  librosa: {lib_ver}  ({good_python})")
    else:
        soft_problems.append("librosa")
        print("  未安装 librosa（音乐 MV 需要；可用 numpy+scipy 的 --onsets-only 兜底）")
        hint = f"{good_python} -m pip install 'librosa==0.11.0'" if good_python else hints["librosa"]
        print(f"  安装提示: {hint}")
    print()

    if problems:
        print(f"结论: 必需依赖缺失 {len(problems)} 项（{', '.join(problems)}），请先补齐再运行对应案例 ❌")
        if soft_problems:
            print(f"  可选依赖缺失（不影响口播/产品动画）: {', '.join(soft_problems)}")
        return 1
    print("结论: 必需依赖就绪，可以开始正式任务 ✅")
    if soft_problems:
        print(f"  提示: 音乐 MV 案例还缺 {', '.join(soft_problems)}，可用 --onsets-only 兜底，或补齐后再用节拍分析")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
