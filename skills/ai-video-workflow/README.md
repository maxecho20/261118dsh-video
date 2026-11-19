# 安装 AI 视频工作流 Skill

把整个 `ai-video-workflow` 目录复制至当前 Hermes profile 的 skills 目录，或设置 `skills.external_dirs` 指向它的父目录。打开新会话后调用 `/ai-video-workflow`。在 Codex 等编程 Agent 中也可以直接让它读本技能的 SKILL.md 和目标案例文档。具体模型在宿主配置中选择。

## ZIP 短样

在解压目录的 `runtime/` 中运行 `npm ci`，再运行 `python3 scripts/repro_demo.py talk`。将 talk 换成 product 或 mv 可以运行另外两案的合成短样。读者提示词在 `runtime/cases/`。

## 本地依赖

- 开局先跑 `python3 scripts/env_check.py` 做环境预检：自动探测 faster-whisper / FFmpeg / Node / librosa 并按你的系统给出安装命令，必需依赖缺失会停下等你补齐，不同电脑、不同配置都能对齐环境。
- 口播运行器依赖 FFmpeg、Python 的 `faster-whisper==1.2.1`，及打包在 `runtime/` 的 Node 工程。Node 依赖在 `runtime/` 运行 `npm ci` 按锁文件安装。首次转写需要下载模型，首次渲染可能安装 Chromium。
- 音乐分析脚本使用 `librosa==0.11.0`，建议安装在专用 Python 环境并用该环境的解释器运行。已有 NumPy 与 SciPy 时也可用 `--onsets-only` 分析 WAV 候选音头，拍点仍需试听确认。
- 填写本案简报并放入你有权使用的素材。用同一工作流配置过短样后再延展。

```text
使用 ai-video-workflow，把我放在当前项目的素材按 brief.md 做成对应的视频。
先输出短样、可编辑工程和验证记录，再延展整片。原素材只读，输出放在 runs/ 下。
```

工具与流程验证状态见项目交付说明。产品动画与 MV 的素材、画面及音轨由 Agent 根据当次任务选择并制作。
