# 小说转音频听书工具 - 产品需求文档（PRD）

## 一、产品概述

### 1.1 产品定位
小说转音频听书工具是一款基于 LLM 智能文本清洗和 IndexTTS2 高质量语音合成的文本书籍转有声书解决方案。支持多格式文本书籍（epub、mobi、pdf、txt、md）自动转换为专业级有声书，解决阅读场景限制问题，提升知识获取效率。

### 1.2 核心价值主张
- **智能清洗**：LLM 识别并去除引用、旁注、页脚等非正文内容
- **情感表达**：基于上下文的 8 维情感向量控制，生成富有感情的有声书
- **多音色支持**：旁白与对话角色音色自动分配，保持一致性
- **一站式服务**：从文本书籍到标准有声书格式的完整解决方案

### 1.3 目标用户
| 用户类型 | 典型场景 | 核心需求 |
|----------|----------|----------|
| 重度阅读爱好者 | 通勤、运动、睡前 | 解放双眼，碎片时间利用 |
| 学习者 | 多感官学习 | 提升记忆效果，理解力增强 |
| 视觉障碍用户 | 无障碍阅读 | 替代视觉获取信息 |
| 内容创作者 | 有声书制作 | 快速批量生成专业有声书 |

## 二、功能需求

### 2.1 文件解析与预处理模块

#### 2.1.1 支持格式
| 格式 | 优先级 | 技术方案 | 处理能力 |
|------|--------|----------|----------|
| TXT | P0 | 直接读取 | 100% |
| MD | P0 | 直接读取 | 100% |
| EPUB | P0 | 解析 OEBPS 目录 | 保留章节结构 |
| PDF | P1 | pdfplumber + OCR | 扫描版支持 |
| MOBI | P2 | Calibre 转换 | 需预处理 |
| DOCX | P2 | python-docx | 基础支持 |

#### 2.1.2 文件验证与预处理
**输入验证**：
- 文件大小限制：≤ 100MB
- 文件类型白名单：.txt, .md, .epub, .pdf, .mobi, .docx
- 字符编码检测：UTF-8, GBK, GB2312

**预处理流程**：
1. 编码转换 → UTF-8
2. DRM 保护检测 → 提示用户处理
3. 目录结构提取（EPUB/MOBI）
4. 章节列表生成

### 2.2 文本结构化分析模块

#### 2.2.1 章节分割

**识别规则引擎**：
```python
# 章节标题正则模式
CHAPTER_PATTERNS = [
    r'^第[一二三四五六七八九十百千万\d]+章\s+',  # 第X章
    r'^第[一二三四五六七八九十百千万\d]+回\s+',  # 第X回
    r'Chapter\s+\d+\s*[:.]?\s*',          # Chapter X
    r'^\d+\.\s+',                         # 1. 标题
    r'^\*{3,}.*?\*{3,}',                 # *** 标题 ***
    r'^\[第\d+章\]',                      # [第X章]
]

# 特殊章节识别
SPECIAL_CHAPTERS = {
    'prologue': r'^(序章|楔子|前言|引子|序幕)\s*',
    'epilogue': r'^(尾声|后记|附录|跋)\s*',
    'extra': r'^(番外|外传|特别篇)\s*'
}
```

**章节分割算法**：
1. 逐行扫描文本
2. 匹配章节正则模式
3. 边界判断（避免误匹配）
4. 生成章节结构树

#### 2.2.2 句子分割

**智能分割策略**：
```python
# 中文句号识别
chinese_splits = ['。', '！', '？', '…', '……']

# 英文句号识别（排除缩写）
exclude_abbreviations = [
    'Mr.', 'Mrs.', 'Dr.', 'Prof.', 'St.',
    'etc.', 'e.g.', 'i.e.', 'vs.', 'No.'
]

# 引号内句号处理
def split_with_quote_aware(sentence):
    # 避免 "他说。" 这类句号被分割
    pass
```

**分割输出格式**：
```json
{
  "chapter_id": "ch001",
  "chapter_title": "第1章 初入江湖",
  "sentences": [
    {
      "id": "s001",
      "text": "正文内容...",
      "start_pos": 100,
      "end_pos": 200,
      "metadata": {
        "has_quote": false,
        "is_dialogue": false
      }
    }
  ]
}
```

### 2.3 LLM 智能文本清洗模块

#### 2.3.1 内容识别与分类

**待识别内容类型**：

| 类型 | 示例 | 处理策略 |
|------|------|----------|
| **引用内容** | ""...引号内容..."" | 保留但标注（用引用音调） |
| **旁注注释** | 【注释：xxx】<br>（译者注：xxx） | 移除或转为轻音调 |
| **页眉页脚** | "第 12 页"<br>"作者：xxx" | 完全移除 |
| **脚注编号** | [1]、[2]、(1) | 移除编号，保留内容可选 |
| **编辑备注** | "（此处有删减）"<br>"[作者删节]" | 移除 |
| **特殊符号** | ★◆※→← | 移除或语音描述 |
| **空白内容** | 连续空行 | 压缩 |

**LLM 提示词模板**：

```python
SYSTEM_PROMPT = """
你是一个专业的文本清洗助手，负责从文本书籍中识别并标注非正文内容。

任务：对每句话进行分析，识别内容类型，并提供处理建议。

输出格式（JSON）：
{
  "original_text": "原始文本",
  "is_noise": true/false,
  "content_type": "dialogue/narration/description/quote/footnote/noise",
  "speaker": "角色名/无",
  "noise_type": "页脚/旁注/脚注/其他噪音/null",
  "process_suggestion": "保留/移除/语音描述",
  "cleaned_text": "清洗后的文本",
  "confidence": 0.95
}
"""

USER_PROMPT = f"""
分析以下文本：
"{sentence}"

上下文（前3句）：
{context}

请返回 JSON 格式结果。
"""
```

#### 2.3.2 情感识别与标注

**8 维情感空间**：
```
[高兴, 愤怒, 悲伤, 害怕, 厌恶, 忧郁, 惊讶, 平静]
```

**LLM 情感分析提示**：

```python
EMOTION_PROMPT = """
分析文本的情感色彩，输出 8 维情感向量（0.0-1.0 浮点数）。

任务：基于文本内容和上下文，判断情感倾向。

输出 JSON：
{
  "emotion_vector": [0.1, 0.2, 0.1, 0.1, 0.1, 0.2, 0.3, 0.9],
  "primary_emotion": "平静",
  "emotion_intensity": 0.7,  # 0.0-1.0
  "reasoning": "情感分析理由"
}

规则：
- 向量和 = 1.0（归一化）
- 主要情感为最高值
- 强度表示情感强烈程度
"""
```

**上下文关联分析**：
- 分析前后 5 句话的情感连续性
- 识别对话场景的情感转折
- 章节级别的情感氛围（高潮、平静、悬疑等）

**输出格式**：
```json
{
  "sentence_id": "s001",
  "text": "清洗后的文本",
  "analysis": {
    "type": "dialogue",
    "speaker": "张三",
    "emotion": {
      "vector": [0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.2],
      "primary": "平静",
      "intensity": 0.6
    },
    "context_emotion": {
      "continuity": 0.8,  # 与上文情感连续性 0-1
      "transition": 0.2    # 本句情感变化程度 0-1
    }
  }
}
```

### 2.4 语音合成引擎模块（IndexTTS2）

#### 2.4.1 TTS API 集成

**API 基础信息**：
- 端点：`POST http://localhost:8000/api/tts`
- Content-Type：`multipart/form-data`

**核心参数配置**：

```python
# 基础参数
base_params = {
    "text": "要合成的文本",
    "speaker_audio": "音色参考音频文件",
    "output_filename": "输出文件名",
}

# 情感控制参数（模式2：8维情感向量）
emotion_params = {
    "emotion_mode": 2,
    "emotion_vector": "0.1,0.2,0.1,0.1,0.1,0.1,0.2,0.1",
    "emotion_weight": 0.8,
}
```

**批量处理策略**：

```python
class TTSBatchProcessor:
    def __init__(self, max_concurrent=3):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.retry_config = {
            "max_retries": 3,
            "base_delay": 2,  # 指数退避
            "backoff_factor": 2
        }

    async def synthesize(self, sentence_data):
        async with self.semaphore:
            for attempt in range(self.retry_config["max_retries"]):
                try:
                    return await self._call_tts_api(sentence_data)
                except Exception as e:
                    if attempt == self.retry_config["max_retries"] - 1:
                        raise e
                    delay = self.retry_config["base_delay"] * (2 ** attempt)
                    await asyncio.sleep(delay)
```

#### 2.4.2 多音色支持

**预设音色配置**：

| 音色ID | 名称 | 适用场景 | 特征 |
|--------|------|----------|------|
| V01 | 旁白男声 | 叙述 | 沉稳、客观、清晰 |
| V02 | 旁白女声 | 叙述 | 温和、清晰 |
| V03 | 青年男声 | 对话 | 活力、年轻 |
| V04 | 成熟男声 | 对话 | 低沉、磁性 |
| V05 | 少女音 | 对话 | 清脆、甜美 |
| V06 | 知性女声 | 对话 | 优雅、知性 |

**音色分配算法**：

```python
def assign_voice(sentence_data, char_database):
    """基于角色数据库分配音色"""
    if sentence_data["type"] == "narration":
        return "V01"  # 统一使用旁白男声

    if sentence_data["type"] == "dialogue":
        speaker = sentence_data.get("speaker", "未知")
        if speaker in char_database:
            return char_database[speaker]["voice_id"]
        else:
            # 新角色：分配相近音色
            return assign_similar_voice(speaker, char_database)
```

#### 2.4.3 音频质量优化

**参数调优**：
```python
# 高质量配置
high_quality_config = {
    "temperature": 0.8,         # 降低随机性
    "top_p": 0.85,              # nucleus sampling
    "length_penalty": 1.2,      # 适度增加长度
    "repetition_penalty": 1.1,  # 减少重复
    "num_beams": 3,             # beam search
}
```

### 2.5 有声书组装与输出模块

#### 2.5.1 音频拼接

**拼接流程**：

```python
class AudioAssembler:
    def __init__(self):
        self.silence_duration_ms = 300  # 句子间静音
        self.chapter_silence_ms = 1000   # 章节间静音

    def assemble_chapter(self, chapter_data):
        """组装章节音频"""
        audio_clips = []

        for sentence in chapter_data["sentences"]:
            # 添加句子音频
            audio_clips.append(sentence["audio_path"])

            # 添加句子间静音（除非是句号结尾的短停顿）
            if not is_short_pause(sentence):
                silence = Audio.silence(duration=self.silence_duration_ms)
                audio_clips.append(silence)

        # 拼接音频
        chapter_audio = concatenate(audio_clips)

        # 生成元数据
        metadata = self.generate_metadata(chapter_data, chapter_audio)

        return chapter_audio, metadata
```

#### 2.5.2 有声书格式输出

**目录结构**：

```
audiobook/
├── book_title/
│   ├── 00_metadata.json          # 图书元数据
│   ├── 01_cover.jpg              # 封面图
│   ├── 02_book.ncx               # 目录索引（可选）
│   ├── chapters/                 # 章节音频
│   │   ├── ch001_第1章.wav
│   │   ├── ch002_第2章.wav
│   │   └── ...
│   ├── playlist.m3u8             # 播放列表
│   └── index.opf                 # OPF 有声书索引
```

**元数据规范**：

```json
{
  "title": "书籍标题",
  "author": "作者姓名",
  "narrator": "朗读者",
  "language": "zh-CN",
  "genre": "小说",
  "duration": 7200,
  "total_chapters": 50,
  "publish_date": "2025-11-17",
  "description": "书籍简介",
  "cover_url": "01_cover.jpg",
  "chapters": [
    {
      "id": "ch001",
      "title": "第1章 初入江湖",
      "file": "chapters/ch001_第1章.wav",
      "duration": 145.2,
      "start_time": 0
    }
  ]
}
```

**输出格式支持**：

| 格式 | 优点 | 适用场景 |
|------|------|----------|
| **M4B** | 支持章节书签、多音色 | 专业有声书 |
| **ZIP** | 兼容性好 | 压缩传输 |
| **HLS(m3u8)** | 流媒体播放 | 在线收听 |
| **MP3** | 通用支持 | 设备兼容 |

## 三、非功能需求

### 3.1 性能指标

| 指标类型 | 目标值 | 说明 |
|----------|--------|------|
| 文本处理速度 | 1万字/分钟 | 解析+清洗 |
| TTS 转换速度 | 实时因子 0.8 | 5分钟文本需4分钟处理 |
| 并发任务数 | 3-5个 | 同时处理多本书 |
| 内存占用 | < 4GB | 处理500页书籍 |
| GPU 显存 | < 8GB | FP16 模式 |

### 3.2 质量指标

| 指标 | 目标 | 测量方法 |
|------|------|----------|
| 文本清洗准确率 | >95% | 人工抽样评估 |
| 语音合成质量 | MOS >4.0 | 主观评分 |
| 音频拼接平滑度 | 无缝衔接 | 过渡时间 <10ms |
| 章节分割准确率 | >98% | 标题匹配率 |

### 3.3 用户体验需求

**交互体验**：
- 实时进度展示（文件上传 → 解析 → 清洗 → 合成 → 组装）
- 可暂停/继续任务
- 断点续传（支持大文件处理中断恢复）
- 预览功能（清洗前后对比、样例播放）

**响应时间**：
- 文件上传：< 5秒（100MB以内）
- 解析开始：< 2秒
- 清洗进度：实时刷新
- TTS 处理：每分钟文本 < 1秒响应

### 3.4 可扩展性

**水平扩展**：
- 支持多 TTS 服务实例（负载均衡）
- 分布式任务队列（Redis/RabbitMQ）
- 文本清洗 LLM 可配置（GPT-4/Claude/本地模型）

**垂直扩展**：
- TTS 参数可定制（温度、采样等）
- 音色库可扩展
- 输出格式可扩展

## 四、技术架构要求

### 4.1 技术栈

**后端（Python）**：
- Web 框架：FastAPI
- 文本处理：spaCy、NLTK、pdfplumber
- 文件解析：EbookLib、python-docx、Calibre
- LLM 集成：OpenAI API / Anthropic Claude API
- 音频处理：PyDub、FFmpeg
- 任务队列：Celery + Redis
- 数据库：SQLite（开发）/ PostgreSQL（生产）
- 缓存：Redis

**前端（React + shadcn）**：
- 框架：React 18 + TypeScript
- 状态管理：Zustand
- UI 组件：shadcn/ui + Tailwind CSS
- 拖拽上传：react-dropzone
- 进度展示：react-circular-progressbar
- 音频播放：react-audio-player

### 4.2 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                        前端层                             │
│  React + shadcn (文件上传、进度展示、音频播放)              │
└────────────────────┬──────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼──────────────────────────────────────┐
│                     API 网关层                            │
│                (认证、限流、路由)                         │
└───────────────┬────────────────┬──────────────────────────┘
                │                │
    ┌───────────▼──────────┐ ┌──▼──────────────┐
    │    文件处理服务       │ │   任务处理服务   │
    │  File Processor      │ │ Task Processor  │
    └───────────┬──────────┘ └─┬────────────────┘
                │              │
    ┌───────────▼──────────┐ ┌──▼──────────────┐
    │   TTS 服务集群       │ │  LLM 服务集群   │
    │  (IndexTTS2)         │ │ (GPT-4/Claude)  │
    └──────────────────────┘ └─────────────────┘
```

### 4.3 数据流设计

```
文件上传 → 格式识别 → 文本提取 → 章节分割 → 句子分割
    ↓
LLM 清洗 → 情感分析 → 音色分配 → TTS 合成 → 音频拼接
    ↓
元数据生成 → 格式转换 → 打包输出 → 下载链接
```

## 五、开发计划

### Phase 1：MVP 核心功能（4周）

**Week 1-2：基础功能**
- [ ] 文件解析（txt、md）
- [ ] 章节分割（正则）
- [ ] 句子分割
- [ ] 基础清洗（正则，非 LLM）
- [ ] TTS 集成（单音色）

**Week 3-4：音频处理**
- [ ] 音频拼接
- [ ] 静音间隔优化
- [ ] 有声书格式输出（M4B/ZIP）
- [ ] 元数据生成

**交付物**：可处理 txt/md 文件的基础听书工具

### Phase 2：智能化升级（4周）

**Week 5-6：LLM 集成**
- [ ] LLM 接入（GPT-4 API）
- [ ] 文本清洗智能识别
- [ ] 情感向量分析
- [ ] 上下文关联优化

**Week 7-8：多音色系统**
- [ ] 角色识别与音色库
- [ ] 多音色 TTS 合成
- [ ] 音频平滑过渡
- [ ] EPUB 支持

**交付物**：支持智能清洗的多音色有声书生成器

### Phase 3：完善与优化（2周）

**Week 9：功能完善**
- [ ] PDF OCR 扫描版支持
- [ ] Web 界面开发
- [ ] 实时进度展示
- [ ] 断点续传

**Week 10：优化部署**
- [ ] 性能优化（并发、缓存）
- [ ] 错误处理完善
- [ ] Docker 容器化
- [ ] 压力测试

**交付物**：完整产品 v1.0

### 里程碑计划

| 时间 | 里程碑 | 关键交付物 |
|------|--------|------------|
| 第2周 | 文本处理完成 | 章节/句子分割准确率 >90% |
| 第4周 | 音频输出完成 | 可播放的有声书文件 |
| 第6周 | LLM 集成完成 | 文本清洗准确率 >95% |
| 第8周 | 多音色完成 | 角色音色一致性 >90% |
| 第10周 | 产品发布 | v1.0 正式版本 |

## 六、风险评估与应对

### 6.1 技术风险

| 风险项 | 影响程度 | 概率 | 应对策略 |
|--------|----------|------|----------|
| LLM API 成本过高 | 高 | 中 | 1. 使用本地开源模型（如 Qwen-7B）<br>2. 缓存机制（相似文本复用）<br>3. 批量处理降低单次调用成本 |
| TTS API 调用超时 | 中 | 中 | 1. 异步重试（指数退避）<br>2. 失败隔离（单句失败不影响整章）<br>3. 降级方案（无情感模式） |
| OCR 准确率低 | 中 | 高 | 1. 多引擎对比（Tesseract vs PaddleOCR）<br>2. 人工校验入口<br>3. 置信度低于阈值时提示 |
| 大文件内存溢出 | 高 | 中 | 1. 流式处理（分段读取）<br>2. 分块处理（每章独立）<br>3. 内存监控与告警 |
| GPU 显存不足 | 中 | 低 | 1. FP16 模式（降低50%显存）<br>2. 动态批处理<br>3. 多GPU 支持（未来） |

### 6.2 产品风险

| 风险项 | 影响程度 | 概率 | 应对策略 |
|--------|----------|------|----------|
| 版权合规问题 | 高 | 中 | 1. 强制用户确认版权<br>2. 仅处理本地文件（不上传）<br>3. 服务条款明确免责声明 |
| 用户体验差 | 中 | 中 | 1. 预览功能（处理前查看清洗效果）<br>2. 手工调整入口<br>3. 快速迭代收集反馈 |
| 处理时间过长 | 中 | 中 | 1. 实时进度展示<br>2. 预估时间提示<br>3. 后台异步处理（无需等待） |
| 音频质量不满意 | 中 | 高 | 1. 多音色选择<br>2. 手动参数调优入口<br>3. 示例音频参考 |

### 6.3 成本风险

| 成本项 | 月度预算 | 优化方案 |
|--------|----------|----------|
| LLM API | $200-500 | 本地模型、缓存 |
| TTS API | $100-300 | 批量折扣 |
| 服务器 | $200-500 | 自动扩缩容 |
| 存储 | $50-100 | 清理策略 |

## 七、商业模式

### 7.1 收费模式

**免费版**（吸引用户）：
- 每月 3 本书
- 基础单音色
- 标准质量
- 有水印

**会员版**（$9.9/月，核心用户）：
- 无限书籍
- 多音色（6种）
- 高质量（无水印）
- 优先处理
- 云端存储

**专业版**（$29.9/月，批量用户）：
- 会员版所有功能
- 批量处理（最多50本/次）
- 定制音色上传
- API 访问权限
- 专业格式输出（M4B）

### 7.2 增值服务

| 服务类型 | 价格 | 说明 |
|----------|------|------|
| 真人配音服务 | 100-500元/小时 | 专业播音员录制 |
| 有声书商城 | 销售分成 30% | 已处理书籍 |
| 企业定制 | 按需报价 | 批量处理、内容审核 |

### 7.3 市场定位

**直接竞品**：
- 懒人听书：综合平台，无文本转音频
- 微信读书：内置 TTS，但质量一般
- 网易见外：视频字幕转音频，非专门做书籍

**差异化优势**：
- LLM 智能清洗（去除非正文）
- 情感化 TTS（8维向量）
- 多角色音色（对话场景）
- 标准有声书格式输出

## 八、成功指标

### 8.1 业务指标

| 指标 | 目标（3个月） | 目标（6个月） |
|------|---------------|---------------|
| 注册用户数 | 1,000 | 10,000 |
| 付费转化率 | 5% | 8% |
| 月活跃用户 | 500 | 5,000 |
| 复购率 | 60% | 70% |

### 8.2 产品指标

| 指标 | 目标值 |
|------|--------|
| 处理成功率 | >95% |
| 用户满意度 | >4.5/5.0 |
| 平均处理时间 | <5分钟/万字 |
| 错误率 | <1% |

## 九、总结

本产品通过 LLM 智能清洗和 IndexTTS2 高质量语音合成，解决传统 TTS 工具在书籍处理上的不足。重点在于：

1. **技术差异化**：情感化 TTS + 多音色
2. **质量保证**：智能识别正文 + 高保真输出
3. **用户价值**：一站式解决（文本书→有声书）

建议采用 MVP 快速验证市场需求（Phase 1），再逐步迭代优化（Phase 2-3）。

---

**文档版本**：v1.0
**创建日期**：2025-11-17
**最后更新**：2025-11-17
