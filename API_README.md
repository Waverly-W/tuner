## 📡 API 接口

### 1. 健康检查

```http
GET /health
```

响应:
```json
{
  "status": "healthy",
  "model": "IndexTTS2",
  "timestamp": "2025-11-16T12:00:00"
}
```

### 2. 文本转语音合成

```http
POST /api/tts
Content-Type: multipart/form-data
```

#### 基本参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `text` | string | ✅ | 要合成的文本 |
| `speaker_audio` | file | ✅ | 音色参考音频 (wav格式) |

#### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `output_filename` | string | 自动生成 | 输出文件名（不含扩展名） |
| `emotion_mode` | int | 0 | 情感控制模式 (0-3) |
| `emotion_audio` | file | - | 情感参考音频 |
| `emotion_weight` | float | 1.0 | 情感权重 (0.0-2.0) |
| `emotion_vector` | string | - | 8维情感向量，格式: `0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8` |
| `emotion_text` | string | - | 情感描述文本 |
| `use_random` | bool | false | 是否使用随机采样 |
| `max_mel_tokens` | int | 600 | 最大mel tokens (100-2000) |
| `temperature` | float | 1.0 | 采样温度 (0.1-2.0) |
| `top_p` | float | 0.85 | nucleus sampling (0.0-1.0) |
| `top_k` | int | 0 | top-k sampling (0为禁用) |
| `length_penalty` | float | 1.0 | 长度惩罚 (0.5-2.0) |
| `repetition_penalty` | float | 1.1 | 重复惩罚 (1.0-2.0) |
| `num_beams` | int | 1 | beam search数量 (1-5) |

#### 情感控制模式

- **模式 0**: 从音色参考音频获取情感（默认）
- **模式 1**: 使用情感参考音频
- **模式 2**: 使用 8 维情感向量
- **模式 3**: 使用情感描述文本

#### 8 维情感向量

```
[高兴, 愤怒, 悲伤, 害怕, 厌恶, 忧郁, 惊讶, 平静]
```

每个值的范围: 0.0 - 1.0

#### 响应格式

直接返回 WAV 格式的音频文件。

- **Content-Type**: `audio/wav`

### 3. 列出输出文件

```http
GET /api/outputs
```

响应:
```json
{
  "files": [
    {
      "filename": "test.wav",
      "size": 102400,
      "created": "2025-11-16T12:00:00",
      "url": "/static/test.wav"
    }
  ],
  "count": 1
}
```

## 💻 使用示例

### 1. curl 命令

#### 基本语音合成

```bash
curl -X POST "http://localhost:8000/api/tts" \
  -F "text=你好，这是测试" \
  -F "speaker_audio=@examples/voice_01.wav" \
  -F "output_filename=my_test" \
  -o output.wav
```

#### 带情感控制的语音合成

```bash
curl -X POST "http://localhost:8000/api/tts" \
  -F "text=这个声音很悲伤" \
  -F "speaker_audio=@examples/voice_01.wav" \
  -F "emotion_mode=1" \
  -F "emotion_audio=@examples/emo_sad.wav" \
  -F "emotion_weight=0.8" \
  -o sad_voice.wav
```

#### 使用情感向量

```bash
curl -X POST "http://localhost:8000/api/tts" \
  -F "text=这是一个快乐的声音" \
  -F "speaker_audio=@examples/voice_01.wav" \
  -F "emotion_mode=2" \
  -F "emotion_vector=0.8,0.1,0.1,0.1,0.1,0.1,0.7,0.2" \
  -o happy_voice.wav
```

### 2. Python 客户端

```python
import requests

# 基本使用
response = requests.post(
    "http://localhost:8000/api/tts",
    files={
        "speaker_audio": open("voice.wav", "rb")
    },
    data={
        "text": "你好，这是测试！",
        "output_filename": "my_test"
    }
)

if response.status_code == 200:
    # 保存音频文件
    with open("output.wav", "wb") as f:
        f.write(response.content)
    print("音频已保存到 output.wav")
else:
    print(f"错误: {response.text}")
```

### 3. JavaScript/Fetch

```javascript
async function synthesize(text, audioFile) {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('speaker_audio', audioFile);

    const response = await fetch('http://localhost:8000/api/tts', {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        return url;
    } else {
        console.error('Synthesis failed');
    }
}

// 使用
const audioBlob = new Blob([...], { type: 'audio/wav' });
synthesize("你好！", audioBlob).then(audioUrl => {
    console.log('音频URL:', audioUrl);
    // 可以直接播放
    // new Audio(audioUrl).play();
});
```