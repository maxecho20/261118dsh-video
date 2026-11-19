---
name: ai-video-workflow
description: 用编程 Agent 把真人口播、产品动画或音乐 MV 做成可编辑工程和可播放视频。根据素材选择转写剪辑、资料驱动动效或音频节拍驱动流程，留存可复核产物。
version: 0.2.0
metadata:
  hermes:
    category: creative
    tags: [video, editing, remotion, music]
---

# AI 视频工作流

先做环境预检（必过关卡）：运行 `python3 scripts/env_check.py`，探测 faster-whisper / FFmpeg / Node / librosa 并按系统（macOS / Linux / Windows）给出安装命令；必需依赖缺失就停下、给安装命令、等用户补齐确认，再开始正式任务。不同电脑、不同配置都要先过这一关，不假设环境已就绪。

读取 [执行规则](references/workflow.md)，从用户的简报选择真人口播、产品动画或音乐 MV。检查实际输入和可用工具，在当前项目的 `runs/` 下另建案例目录。保留原片，输出工程、MP4 和能定位到文件或时间点的验收记录。

- 真人口播先转写，再让语义剪辑决定保留段落，最后用重映射后的时间线加字幕和素材。复用 [run-talk.py](scripts/run-talk.py)，在剪辑前检查转写和剪辑单。
- 产品动画从官方和原始来源核对事实，在 `sources.md` 保存每个上屏文本和实际素材的来源。先出开头 8–10 秒，随后延展成片。按案例简报自己选择 2D 或 3D。
- 音乐 MV 从实际音轨提取重拍和音头。可以用 [beat-map.py](scripts/beat-map.py)，再将镜头和动作对齐到检测时间点并实际试听。若声明 3D，交付可重新渲染的场景或模型文件。
- 在报告中分别记录 Hermes/模型、实际执行命令、工具版本、人工介入和验收。候选工具的名称不计作调用。片头吸引力、声音和剪辑观感以实际查看为准。
