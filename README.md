# 用 DeepSeek 和 Hermes Agent 复现 AI 视频工作流

项目编号 C-20261118-01｜2026-11-18｜执行目录 `261118 AI视频dsh`。

按[沟通纪要与逐字记录](https://feishu.doubao.com/docx/TAE7d4qdjo7d51x21iNcThLcnzg)及用户本轮确认推进。借用[已有飞书大纲](https://ycn8ajgnopya.feishu.cn/wiki/EiKYwRUXkiiYHfkrFqHctgKjnjb)的五阶段交接，沿用本地 Whisper、FFmpeg 和 Remotion 工程。运行口径为 **Hermes Agent 接 DeepSeek 模型**。先核对可用于文章首屏的黄金片段，再跑三个案例，随后写飞书图文稿，最后依据实际产物出「字幕｜画面｜备注」视频脚本。周五是沟通中的目标日期。

## 三个案例

| 案例 | 输入与任务 | 过片条件 |
| --- | --- | --- |
| [01 真人口播](cases/01-真人口播.md) | 已收到真人 A-roll、B-roll 和前两分钟脚本，现成一分钟片用于对照 | 开头 8–12 秒先过片，完整执行覆盖原脚本约两分钟。检查内容删留、实际 B-roll、字幕与声音 |
| [02 产品动画](cases/02-ChatGPT四周年.md) | ChatGPT 四周年第三方致敬，40–60 秒、16:9、无旁白、原创音乐。模型自主找真实素材、挑视觉形式 | 前十秒得有可辨识的动效和明确题眼。成片上屏日期、里程碑和数字逐条可溯，源工程可修改 |
| [03 音乐 MV](cases/03-音乐MV.md) | 按两条抖音的卡点与角色一致性借鉴，做原创小鲸角色短片。以实际音轨驱动 | 一段完整 2D 或 3D 动作，实际听拍并复核偏差。3D 声明有可改源场景和多角度画面支撑 |

## 技能包与调用

本项目维护一项技能 `ai-video-workflow`，内含参考流程、路由、逐字稿→粗剪→渲染的可执行脚本及音频分析脚本。 [技能入口](skills/ai-video-workflow/SKILL.md) · [执行规则](skills/ai-video-workflow/references/workflow.md)

技能开局先跑 `scripts/env_check.py` 做环境预检，自动探测 faster-whisper / FFmpeg / Node / librosa 并按系统给出安装命令，必需依赖缺失会停下等你补齐——不同电脑、不同配置都能对齐环境。

打包产物 `dist/ai-video-workflow-v0.1.0.zip` 只含公开可复用的技能文件及运行模板。解压后将整个 `ai-video-workflow` 目录放到当前 Hermes profile 的 skills 目录，或在 Hermes 的 `skills.external_dirs` 指向它的父目录。新会话用 `/ai-video-workflow`，也可用官方模型配置和 CLI 预加载。 [Hermes Skills 指南](https://hermes-agent.nousresearch.com/docs/guides/work-with-skills) · [DeepSeek Hermes 接入](https://api-docs.deepseek.com/quick_start/agent_integrations/hermes/)

```sh
hermes chat --provider deepseek --model deepseek-v4-pro --skills ai-video-workflow
```

一案一条 prompt。例如「用 ai-video-workflow 执行当前项目 cases/01-真人口播.md。先交开场 8–12 秒，回传可播放样片、可编辑工程、剪点表和实际用到的工具。原素材只读，输出保存在 runs/01-口播/hermes-golden-01。」三个案例各自简报内都有完整调用提示。各次运行记模型、版本、素材版本、阶段耗时、实际调用与人工介入。 [本轮验证记录](docs/验证记录.md)

## 写稿入口

先取得 Hermes 的真实样片与三案证据，再复用已有文章大纲的三步结构，压缩为「装一个包 → 用同一入口调用 → 三种素材实测」。第一屏放真实黄金片段，正文放口播剪辑、资料到动效、音乐与镜头时间对齐三张案例结果卡。工具清单说明实际使用的实现。短片按公司当期格式附同段 MP4 与 GIF。最终解释依赖、权限、输入和成本，统一汇报首版、返工版与失败点。
