# PyVideoTrans CLI

精简版视频翻译配音工具，去除了原版复杂的 GUI 和多余的渠道支持，专注于核心功能。

## 功能特性

- ✅ **语音识别**: 支持 Whisper (faster-whisper / openai-whisper)
- ✅ **文本翻译**: 支持本地 LLM 模型（待实现具体集成）
- ✅ **语音合成**: 支持 Qwen TTS (API 版本和本地版本)
- ❌ **不支持**: 其他 TTS 渠道、 diarization、声音克隆等

## 安装

### 基础安装

```bash
pip install -e .
```

### 带 CUDA 支持

```bash
pip install -e ".[cuda]"
```

### 手动安装依赖

```bash
pip install faster-whisper dashscope requests pydub
```

## 使用方法

### 完整流程（转录 + 翻译 + 配音）

```bash
pyvideotrans-cli -i input.mp4 -o ./output --target-lang en --qwen-api-key YOUR_API_KEY
```

### 仅语音识别

```bash
pyvideotrans-cli -i input.mp4 --mode transcribe --whisper-model base
```

### 仅翻译

```bash
pyvideotrans-cli -i input.mp4 --mode translate --source-lang zh --target-lang en
```

### 仅 TTS

```bash
pyvideotrans-cli -i input.mp4 --mode tts --tts-type qwen_api --voice-role Cherry
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-i, --input` | 输入视频文件 | 必填 |
| `-o, --output` | 输出目录 | `./output` |
| `-c, --cache` | 缓存目录 | `./cache` |
| `--source-lang` | 源语言代码 | `auto` |
| `--target-lang` | 目标语言代码 | `en` |
| `--whisper-model` | Whisper 模型 | `base` |
| `--cuda` | 启用 CUDA 加速 | `False` |
| `--tts-type` | TTS 类型 | `qwen_api` |
| `--voice-role` | Qwen TTS 角色 | `Cherry` |
| `--qwen-api-key` | Qwen API 密钥 | `` |
| `--mode` | 处理模式 | `all` |

## 支持的 Whisper 模型

- `tiny` - 最小最快，精度最低
- `base` - 平衡选择（推荐）
- `small` - 更高精度
- `medium` - 高精度
- `large` - 最高精度，最慢

## Qwen TTS 角色

常用角色：
- `Cherry` - 女声
- `Alex` - 男声
- `Emma` - 女声
- `Jack` - 男声

更多角色请参考 Qwen TTS 文档。

## 项目结构

```
pyvideotrans_cli/
├── videotrans/
│   ├── cli.py          # 主 CLI 入口
│   ├── tts/            # TTS 模块（预留）
│   ├── recognition/    # 语音识别模块（预留）
│   ├── translator/     # 翻译模块（预留）
│   └── util/           # 工具函数（预留）
├── pyproject.toml      # 项目配置
└── README.md           # 说明文档
```

## 与原版对比

| 功能 | 原版 pyvideotrans | 精简版 CLI |
|------|-------------------|------------|
| GUI 界面 | ✅ | ❌ |
| Whisper 识别 | ✅ | ✅ |
| 本地 LLM 翻译 | ✅ | ✅ (待完善) |
| Qwen TTS API | ✅ | ✅ |
| Qwen TTS Local | ✅ | ⏳ (待实现) |
| 其他 TTS 渠道 | ✅ (30+种) | ❌ |
| 声音克隆 | ✅ | ❌ |
| 说话人分离 | ✅ | ❌ |
| 音频对齐 | ✅ | ❌ |
| 批量处理 | ✅ | ❌ |

## TODO

- [ ] 实现本地 Qwen TTS 推理
- [ ] 集成实际本地 LLM 翻译（Ollama/vLLM）
- [ ] 实现音频片段合并逻辑
- [ ] 添加视频硬编码字幕功能
- [ ] 添加背景音处理
- [ ] 优化错误处理和重试机制

## License

MIT License

## 致谢

本项目基于 [pyvideotrans](https://github.com/jianchang512/pyvideotrans) 精简改造。
