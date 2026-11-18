"""Create a synthetic Mandarin talking-head fixture with macOS say and FFmpeg."""

import argparse
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory


def generate(output):
    if output.exists():
        raise FileExistsError(f"输出已存在: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    phrases = [
        "今天教大家用五个技能，实现人工智能视频自动化的全流程。",
        "嗯。",
        "先提取每个字的时间戳，再剪掉口播里的长停顿，最后加上字幕和镜头动效。",
    ]
    with TemporaryDirectory() as temp:
        inputs = []
        duration = 0
        for index, phrase in enumerate(phrases):
            audio = Path(temp) / f"voice-{index}.aiff"
            subprocess.run(["say", "-v", "Tingting", "-o", str(audio), phrase], check=True)
            inputs.extend(["-i", str(audio)])
            seconds = subprocess.check_output([
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "csv=p=0", str(audio),
            ], text=True)
            duration += float(seconds) + 0.8

        filters = [
            f"[{index + 1}:a]aresample=48000,aformat=channel_layouts=mono,"
            f"apad=pad_dur=0.8[a{index}]"
            for index in range(len(phrases))
        ]
        audio_inputs = "".join(f"[a{i}]" for i in range(len(phrases)))
        filters.append(f"{audio_inputs}concat=n={len(phrases)}:v=0:a=1[voice]")
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-n",
            "-f", "lavfi", "-i", "testsrc2=size=540x960:rate=30",
            *inputs, "-filter_complex", ";".join(filters), "-map", "0:v", "-map", "[voice]",
            "-t", f"{duration:.3f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(output),
        ], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, nargs="?", default=Path("input/raw_video.mp4"))
    generate(parser.parse_args().output)
