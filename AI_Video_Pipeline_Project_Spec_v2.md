# AGENTS.md / PROJECT_SPEC.md — AI 自动化口播视频制作流水线规范

> **文件用途**：本文件是直接投喂给 DeepSeek Harness (DC HerMAS) / Codex 等 Agent 工具的**项目全局规范说明书**。请将本文件保存在项目根目录（命名为 `AGENTS.md` 或 `PROJECT_SPEC.md`），让 Agent 读取本文件即可自动完成全部 5 个阶段脚本、组件与流水线的搭建和执行。

---

## 1. 项目目录结构规范 (Directory Structure)

Agent 在初始化或执行任务时，必须严格维护以下目录结构与数据契约：

```text
my-ai-video-pipeline/
├── AGENTS.md                   # 本项目规范文档（Agent 全局记忆与操作手册）
├── input/
│   ├── raw_video.mp4           # 原始口播视频素材
│   ├── script_outline.txt      # 用户提供的视频大纲或脚本文案
│   └── test_case_generator.py  # [自检用] 自动生成测试口播视频的脚本
├── public/
│   ├── assets/                 # 存放 B-roll 视频、配图、音效素材
│   ├── rough_cut.mp4           # [Stage 3 产物] 切除气口与调色后的粗剪视频
│   ├── aligned_captions.json   # [Stage 3 产物] 重映射时间轴后的字级字幕数据
│   └── storyboard.json         # [Stage 1 产物] 分镜与视觉包装配置表
├── workspace_data/
│   ├── transcript.json         # [Stage 2 产物] Whisper 原始毫秒级字词时间戳
│   └── edl_cuts.json           # [Stage 3 产物] 保留片段裁剪时间表 (Edit Decision List)
├── scripts/
│   ├── stage2_whisper.py       # [Stage 2 执行脚本] 语音转写与字级时间戳提取
│   └── stage3_video_use.py     # [Stage 3 执行脚本] 气口清洗、时间轴重映射与 FFmpeg 调色合成
├── src/                        # Remotion 视频代码工程目录
│   ├── index.ts                # Remotion 入口注册文件
│   ├── Root.tsx                # 合成容器配置（自动匹配 rough_cut.mp4 时长）
│   └── MainVideo.tsx           # [Stage 4 & 5 核心组件] 动态字幕 + Shotcraft 镜头动效
└── out/
    └── final_video.mp4         # [最终产物] 渲染导出的成品视频
```

---

## 2. 五大阶段详细规范与完整复刻实现 (5-Stage Implementation Spec)

### Stage 1: `Hyperframes`（视觉分镜与节奏规划）
* **职责**：结合 `input/script_outline.txt`、`workspace_data/transcript.json`（若已生成）和 `public/assets/` 下的素材，生成结构化分镜配置 `public/storyboard.json`。
* **核心规则**：
  1. **黄金前3秒（Hook）**：第 1 个分镜必须设置为 `A-roll_zoom_hook`（快速推镜 + 顶部醒目痛点标题卡）。
  2. **5-8秒视觉变化定律**：每间隔 5~8 秒必须切换一次视觉状态（切换景别 `scale: 1.0` <-> `1.15`、弹出核心词卡片 `keyword_card`、或叠加 `B-roll_overlay`）。
  3. **高亮词提取**：从每个句子中提取 1~2 个高价值核心词写入 `highlight_keywords` 数组。
* **`public/storyboard.json` 标准 Schema**：
```json
{
  "video_title": "AI视频自动化全流程",
  "fps": 30,
  "width": 1080,
  "height": 1920,
  "segments": [
    {
      "segment_id": 1,
      "match_text": "今天教大家用5个Skill实现AI做视频全流程",
      "shot_type": "A-roll_zoom_hook",
      "camera_scale": [1.0, 1.15],
      "b_roll_asset": null,
      "info_card": {
        "title": "5个Skill全自动剪辑",
        "subtitle": "告别手拉时间线"
      },
      "highlight_keywords": ["5个Skill", "全流程"]
    }
  ]
}
```

---

### Stage 2: `Whisper`（高精度语音转写与毫秒级字词对齐）
* **职责**：将 `input/raw_video.mp4` 转换为包含**精确到毫秒的字/词级时间戳（Word-level Timestamps）**的逐字稿 `workspace_data/transcript.json`。
* **为什么不能省**：后续 Stage 3 切气口、切废话，以及 Stage 4 做卡拉 OK 逐字弹跳字幕，100% 依赖此阶段产出的字级时间戳。
* **标准实现代码 (`scripts/stage2_whisper.py`)**：
```python
import os
import json
import sys
from faster_whisper import WhisperModel

def transcribe_video(video_path="input/raw_video.mp4", output_path="workspace_data/transcript.json", model_size="base"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"[Stage 2: Whisper] 正在加载模型 ({model_size}) 并转写: {video_path} ...")
    
    # 自动检测设备，优先使用 GPU/CPU int8 加速
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        video_path,
        beam_size=5,
        word_timestamps=True,
        initial_prompt="以下是普通话口播视频的逐字稿，请准确识别标点符号与专业术语。"
    )

    transcript_data = {
        "language": info.language,
        "duration": round(info.duration, 3),
        "segments": []
    }

    for idx, seg in enumerate(segments):
        words_list = []
        if seg.words:
            for w in seg.words:
                words_list.append({
                    "word": w.word.strip(),
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "probability": round(w.probability, 3)
                })
        transcript_data["segments"].append({
            "id": idx,
            "text": seg.text.strip(),
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "words": words_list
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcript_data, f, ensure_ascii=False, indent=2)
    print(f"[Stage 2: Whisper] 转写完成！共识别 {len(transcript_data['segments'])} 句，已保存至 {output_path}")

if __name__ == "__main__":
    video_in = sys.argv[1] if len(sys.argv) > 1 else "input/raw_video.mp4"
    transcribe_video(video_in)
```

---

### Stage 3: `video-use`（语义粗剪、气口切除、时间轴重映射与 FFmpeg 调色）
* **职责**：
  1. **语义去重与废话清洗**：Agent 审查 `workspace_data/transcript.json`，识别口误重录句（如前一句说一半卡壳、后一句完整重说）、纯语气词片段（“呃”、“啊”、“那个”），生成保留片段决策表 `workspace_data/edl_cuts.json`。
  2. **气口切除与呼吸缓冲**：自动切掉句与句之间大于 `0.4s` 的静音气口，但在每个保留片段首尾各留 `0.10s` 的自然呼吸缓冲，防止声音截断生硬。
  3. **时间轴重映射（Timeline Remapping）**：计算裁剪拼接后，每个字在新视频 `rough_cut.mp4` 中的全新时间戳，输出 `public/aligned_captions.json`。
  4. **FFmpeg 调色与响度标准化**：调用 FFmpeg `filter_complex` 一次性完成多段无损切片拼接、色彩增强（对比度 `1.06`、饱和度 `1.10`、轻微暗角修饰）与音频响度标准化（`loudnorm`）。
* **标准实现代码 (`scripts/stage3_video_use.py`)**：
```python
import os
import json
import subprocess

def process_rough_cut(
    raw_video="input/raw_video.mp4",
    transcript_path="workspace_data/transcript.json",
    edl_path="workspace_data/edl_cuts.json",
    output_video="public/rough_cut.mp4",
    aligned_captions_path="public/aligned_captions.json",
    max_silence_gap=0.4,
    padding=0.08
):
    os.makedirs("public", exist_ok=True)
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = json.load(f)

    # 如果 Agent 已经生成了剔除废话后的 edl_cuts.json，则优先读取；否则自动按静音气口规则生成
    if os.path.exists(edl_path):
        with open(edl_path, "r", encoding="utf-8") as f:
            keep_segments = json.load(f)["keep_segments"]
    else:
        keep_segments = []
        filler_words = {"呃", "啊", "嗯", "那个", "就是说"}
        for seg in transcript["segments"]:
            clean_text = seg["text"].strip()
            if not clean_text or clean_text in filler_words:
                continue
            keep_segments.append(seg)

    # 计算精确裁剪区间并重映射字级时间轴
    cut_intervals = []
    aligned_Captions = []
    current_timeline_cursor = 0.0

    for seg in keep_segments:
        seg_start = max(0.0, round(seg["start"] - padding, 3))
        seg_end = min(transcript["duration"], round(seg["end"] + padding, 3))
        clip_duration = round(seg_end - seg_start, 3)
        if clip_duration <= 0.1:
            continue

        offset = current_timeline_cursor - seg_start
        remapped_words = []
        for w in seg.get("words", []):
            remapped_words.append({
                "word": w["word"],
                "start": round(max(current_timeline_cursor, w["start"] + offset), 3),
                "end": round(min(current_timeline_cursor + clip_duration, w["end"] + offset), 3)
            })

        aligned_Captions.append({
            "segment_id": seg["id"],
            "text": seg["text"],
            "start": round(current_timeline_cursor, 3),
            "end": round(current_timeline_cursor + clip_duration, 3),
            "words": remapped_words
        })

        cut_intervals.append({"orig_start": seg_start, "orig_end": seg_end, "duration": clip_duration})
        current_timeline_cursor = round(current_timeline_cursor + clip_duration, 3)

    # 保存重映射后的字幕与总时长
    aligned_output = {
        "total_duration": current_timeline_cursor,
        "captions": aligned_Captions
    }
    with open(aligned_captions_path, "w", encoding="utf-8") as f:
        json.dump(aligned_output, f, ensure_ascii=False, indent=2)

    # 构建 FFmpeg 复杂滤镜图：切片 + 拼接 + 调色 + 音频响度均衡
    filter_parts = []
    concat_inputs = []
    for i, interval in enumerate(cut_intervals):
        s, e = interval["orig_start"], interval["orig_end"]
        filter_parts.append(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}];")
        filter_parts.append(f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS[a{i}];")
        concat_inputs.append(f"[v{i}][a{i}]")

    n = len(cut_intervals)
    filter_str = "".join(filter_parts)
    filter_str += f"{''.join(concat_inputs)}concat=n={n}:v=1:a=1[vcat][acat];"
    # 画面调色：提升对比度1.06，饱和度1.10，微提亮度0.02
    filter_str += "[vcat]eq=contrast=1.06:saturation=1.10:brightness=0.02,format=yuv420p[vout];"
    # 音频处理：响度标准化
    filter_str += "[acat]loudnorm=I=-16:TP=-1.5:LRA=11[aout]"

    cmd = [
        "ffmpeg", "-y", "-i", raw_video,
        "-filter_complex", filter_str,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        output_video
    ]
    print(f"[Stage 3: video-use] 正在执行 FFmpeg 粗剪与调色，共合并 {n} 个有效片段...")
    subprocess.run(cmd, check=True)
    print(f"[Stage 3: video-use] 输出完成：{output_video} (新时长: {current_timeline_cursor}s)")

if __name__ == "__main__":
    process_rough_cut()
```

---

### Stage 4 & Stage 5: `Remotion` + `video-shotcraft`（动态字幕包装与高阶镜头动效）
* **职责**：
  * **Stage 4 (`Remotion`)**：读取 `public/rough_cut.mp4`、`public/aligned_captions.json` 和 `public/storyboard.json`，渲染逐字高亮弹跳字幕与左上角/居中信息卡片。
  * **Stage 5 (`video-shotcraft`)**：注入镜头呼吸感与视觉层次：
    1. **动态推拉镜头（Dynamic Zoom）**：普通段落 `scale` 缓慢从 `1.0` 推至 `1.04`；匹配到重点分镜或高亮词时，通过 `spring()` 物理曲线平滑切至近景 `scale: 1.14`。
    2. **空间景深层次（Depth Layering）**：当有悬浮信息卡（`info_card`）出现时，底层视频自动施加柔和压暗与轻微模糊，前景卡片带毛玻璃（`backdropFilter: blur(16px)`）与投影，彻底摆脱单调感。
* **标准组件代码 (`src/MainVideo.tsx`)**：
```tsx
import React from 'react';
import {
  AbsoluteFill,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from 'remotion';
import alignedData from '../public/aligned_captions.json';
import storyboardData from '../public/storyboard.json';

export const MainVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  // 查找当前时间所在的字幕句
  const activeCaption = alignedData.captions.find(
    (c) => currentTime >= c.start && currentTime <= c.end
  );

  // 查找当前时间对应的分镜配置
  const activeSegment =
    storyboardData.segments.find(
      (s, idx) => activeCaption && idx === activeCaption.segment_id % storyboardData.segments.length
    ) || storyboardData.segments[0];

  const highlightSet = new Set(activeSegment?.highlight_keywords || []);

  // [Stage 5: Shotcraft] 计算镜头缩放：重点句自动快速推近景，普通句缓慢呼吸推镜
  const isHookOrZoom = activeSegment?.shot_type === 'A-roll_zoom_hook';
  const zoomSpring = spring({
    frame: activeCaption ? frame - Math.floor(activeCaption.start * fps) : 0,
    fps,
    config: { damping: 14, stiffness: 120 },
  });

  const baseScale = isHookOrZoom
    ? interpolate(zoomSpring, [0, 1], [1.0, 1.14])
    : interpolate(
        frame % (fps * 6),
        [0, fps * 6],
        [1.0, 1.05],
        { extrapolateRight: 'clamp' }
      );

  const hasInfoCard = Boolean(activeSegment?.info_card && currentTime - (activeCaption?.start || 0) < 2.8);

  return (
    <AbsoluteFill style={{ backgroundColor: '#0a0a0c', overflow: 'hidden' }}>
      {/* 主视频层 + Shotcraft 推拉镜头与景深模糊 */}
      <AbsoluteFill
        style={{
          transform: `scale(${baseScale})`,
          filter: hasInfoCard ? 'brightness(0.72) blur(3px)' : 'brightness(1.0)',
          transition: 'filter 0.25s ease-out',
        }}
      >
        <OffthreadVideo src={staticFile('rough_cut.mp4')} />
      </AbsoluteFill>

      {/* 底部渐变压暗遮罩，保证字幕高可读性 */}
      <AbsoluteFill
        style={{
          background: 'linear-gradient(to top, rgba(0,0,0,0.82) 0%, rgba(0,0,0,0) 35%)',
          pointerEvents: 'none',
        }}
      />

      {/* [Stage 5: Shotcraft] 悬浮毛玻璃信息卡片 */}
      {hasInfoCard && activeSegment.info_card && (
        <div
          style={{
            position: 'absolute',
            top: '14%',
            left: '8%',
            right: '8%',
            padding: '28px 36px',
            borderRadius: '24px',
            background: 'rgba(20, 24, 36, 0.78)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(255, 255, 255, 0.18)',
            boxShadow: '0 24px 48px rgba(0, 0, 0, 0.45)',
            transform: `translateY(${interpolate(zoomSpring, [0, 1], [40, 0])}px)`,
            opacity: zoomSpring,
          }}
        >
          <div style={{ color: '#00F5D4', fontSize: 30, fontWeight: 700, marginBottom: 8 }}>
            {activeSegment.info_card.subtitle}
          </div>
          <div style={{ color: '#FFFFFF', fontSize: 52, fontWeight: 900, letterSpacing: '1px' }}>
            {activeSegment.info_card.title}
          </div>
        </div>
      )}

      {/* [Stage 4: Remotion] 逐字卡拉OK弹跳高亮字幕 */}
      {activeCaption && (
        <div
          style={{
            position: 'absolute',
            bottom: '12%',
            left: '6%',
            right: '6%',
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'center',
            alignItems: 'baseline',
            gap: '6px',
            textAlign: 'center',
          }}
        >
          {activeCaption.words.map((w, idx) => {
            const isSpeaking = currentTime >= w.start && currentTime <= w.end + 0.12;
            const isKeyword = highlightSet.has(w.word) || Array.from(highlightSet).some(k => k.includes(w.word));
            const wordPop = spring({
              frame: Math.max(0, frame - Math.floor(w.start * fps)),
              fps,
              config: { damping: 10, stiffness: 220 },
            });

            const scale = isSpeaking ? interpolate(wordPop, [0, 1], [1.0, isKeyword ? 1.28 : 1.14]) : 1.0;
            const color = isKeyword
              ? '#FFD700'
              : isSpeaking
              ? '#00F5D4'
              : '#FFFFFF';

            return (
              <span
                key={idx}
                style={{
                  display: 'inline-block',
                  fontSize: isKeyword ? 60 : 52,
                  fontWeight: 900,
                  color,
                  transform: `scale(${scale})`,
                  textShadow: '0 4px 16px rgba(0,0,0,0.85)',
                  padding: '0 2px',
                }}
              >
                {w.word}
              </span>
            );
          })}
        </div>
      )}
    </AbsoluteFill>
  );
};
```
