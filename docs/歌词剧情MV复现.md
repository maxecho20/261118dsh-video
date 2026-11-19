# 用本项目做歌词剧情 MV

这份指南把音乐、角色、剧本、分镜和成片串起来。运行目录按案例隔离，歌曲和歌词由使用者提供。短样建议选 20–35 秒的连续乐句。

## 从参考作品学到的做法

《富士山下》开场能看到雪夜站台、像素人物、章节标识和空间层次。角色一出现，观众就知道人物身处何处。用可识别的角色、地点和动作推动本片；人物、场景和画面另行设计。网页后续播放出现登录提示，记录范围是已见的开场画面。[成片参考](https://www.douyin.com/video/7698246233147624758)

制作教程 01:18 讲歌词时间和节奏，02:19 讲风格样图，02:55 把角色动作单独存成代码，03:18 将歌词和镜头写在一起，04:37 用草图先校正方向。这套项目据此采用一个角色组件、一张统一时间表、一轮带声动态分镜再进正式动画。[作者制作教程](https://www.douyin.com/video/7698697526622440714)

## 音频到时间轴

1. 从原曲估算拍点与音头。需要重拍时以试听或专用 downbeat 模型核对，编曲段落随歌曲记录。用可信歌词逐行对照实际录音，按演唱的起止标记。Whisper 可辅助定位候选。混音识别不准时，可用 Audio Separator 分离人声，再用 SOFA 将已知歌词对齐到歌声。Beat This 可补小节首拍候选。接入前用同一片段比对实听时间标记。[Audio Separator](https://github.com/nomadkaraoke/python-audio-separator) · [SOFA 歌声对齐](https://github.com/qiuqiao/SOFA) · [Beat This!](https://github.com/CPJKU/beat_this)
2. 让执行模型读歌词行及音乐事件，写人物、地点、每场动作和衔接。角色各镜共用一个像素组件和固定色板。标记歌词开始/结束、动作起势和音乐撞点。记录音乐测量与人工复核来源。
3. 将标记存成一个计划，时间均写原曲秒数。运行转换生成片内帧号，字幕与镜头共用同一个片内零点。Remotion 按输出帧渲染角色、背景和字幕；音轨从同一个原曲起点切入。

```sh
python3 -m pip install librosa==0.11.0
python3 skills/ai-video-workflow/scripts/beat-map.py path/to/song.mp3 path/to/beats.json
python3 scripts/prepare_mv_timeline.py path/to/mv-plan.json path/to/mv-timeline.json
```

以下是一个可复制的时钟示例，时间与文字为示意。正式工程将片内帧字段用于 Sequence、字幕和关键帧。区间的 `end_frame` 是排除端。精确同步的剪辑点建议在实际画面里复核是否落在目标两帧内。

```json
{
  "fps": 30,
  "clip_start_s": 30.2,
  "clip_end_s": 36.2,
  "events": [
    {"id": "L01", "type": "lyric", "start_s": 30.4, "end_s": 32.0, "text": "填写已校歌词"},
    {"id": "S01", "type": "scene", "start_s": 30.2, "end_s": 36.2, "action": "角色走到门口，停步，翻牌"},
    {"id": "B01", "type": "cue", "start_s": 35.2, "action": "翻牌落点"}
  ]
}
```

## 带声分镜和正式出片

先用静止布局与少量关键帧渲染动态分镜，接上原音。逐行查唱词和字幕，正常播放检查谁做了什么、为什么转场。确认后再细化表演，最终输出可复渲工程、MP4、角色源素材、脚本和实际落点记录。时间表转换和拍点提取已有脚本，自动歌声对齐与剧情动画仍按案例接入和验证。
