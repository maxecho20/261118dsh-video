# AI 视频工作流｜卡尔的 AI 沃茨

一套可在本地复刻的 AI 视频制作流程，包含真人口播、产品动画和音乐 MV 三个案例。有三份能直接复制给编程 Agent 的提示词，也有三个用合成素材跑通的短样。

[三案复刻与提示词](cases/README.md) · [项目复盘](docs/项目复盘.md) · [版本与下载](https://github.com/maxecho20/261118dsh-video/releases/latest)

## 先出一支片

需要 Node.js、Python 3、FFmpeg。首跑会安装 Node 依赖，Remotion 可能下载渲染用浏览器。下面的短样只用本地合成素材和音轨，不需要模型密钥。请在仓库根目录执行。

```sh
git clone https://github.com/maxecho20/261118dsh-video.git
cd 261118dsh-video
npm ci
python3 scripts/repro_demo.py talk
```

输出在 `out/demo-talk.mp4`。六秒内能看到主画面、左上角 B-roll 和字幕。样例使用测试画面和合成音轨来验证剪辑与合成。想试另外两类，把最后一条命令的参数换成 `product` 或 `mv`，成片分别是 `out/demo-product.mp4`、`out/demo-mv.mp4`。

试着修改 `examples/index.tsx` 里的字幕，或修改 `examples/mv-plan.json` 里的音乐事件，再跑一次。三个短样均以 960×540、30 fps 输出；完整案例的选段、画幅和成片交付件见各自简报。完整流程前可以检查依赖。短样已在 macOS 验证，Windows 与 Linux 的端到端流程待独立验证。

```sh
python3 skills/ai-video-workflow/scripts/env_check.py
```

## 用自己的素材

1. 选 [一个案例](cases/README.md)，准备属于你的原始媒体和对应的文字材料。在项目里用独立目录保存输入和输出。
2. 用 Codex 等编程 Agent 打开仓库，把该案例中「可直接复制的提示词」发给它。请它读取剪辑工作流，先交短样或带声粗样，再完成全片。
3. 把出片时用的素材、时间表和回听结果一起存下来。字幕和镜头的变化应可在工程中修改、重新渲染。

| 案例 | 输入 | 读者可以复刻的结构 |
| --- | --- | --- |
| [01 真人口播](cases/01-真人口播.md) | 一段原声、稿件、若干 B-roll | 真人和角窗开场，跟随讲解插入实例，多画面布局、字幕和剪点表 |
| [02 产品动画](cases/02-苹果手机进化.md) | 官方来源、产品参照、原创或获准使用的音乐 | 每段一个节点、一项成就、一幅解释其意义的画面 |
| [03 音乐 MV](cases/03-音乐MV.md) | 可使用的歌、校对歌词、角色与画风 | 同一角色、单行歌词、音乐事件驱动转场，动作和歌词共用时间轴 |

## 技能和工具

- **1 个技能入口，5 个制作阶段。** `ai-video-workflow` 将分镜、转写、粗剪、合成和镜头动效串起来。[SKILL.md](skills/ai-video-workflow/SKILL.md)
- **现有工具。** faster-whisper 提取口播和候选唱词，FFmpeg 负责粗剪、封装与解码检查，Remotion 根据时间轴绘制。MV 可用 librosa 提取候选拍点，`prepare_mv_timeline.py` 把原曲秒数映射到成片帧号。[音乐 MV 复现指南](docs/歌词剧情MV复现.md)
- **依案例增加工具。** 实测 iPhone 片用 SceneKit 做三维场景，完整蜡笔 MV 用 Pillow/NumPy 做绘制。Audio Separator、SOFA 和 Beat This! 是音频增强候选，基础复刻入口只需要上面列出的依赖。
- 技能 ZIP 解压后可将 `ai-video-workflow` 目录添加到支持 Skill 的 Agent 配置。也可以直接让 Agent 读取本仓库的 [SKILL.md](skills/ai-video-workflow/SKILL.md) 和案例文件。ZIP 内的 `runtime/` 提供与仓库相同的短样命令。

公开短样在本机生成。正式实测原片、商品图片、商业歌曲及完整歌词由使用者自行准备。公开短样证明当前项目的合成和时间轴路径可运行，实拍内容校正、画面事实核对、歌词与听感复核仍是各案的验收环节。
