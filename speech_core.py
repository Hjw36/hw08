import whisper
import edge_tts
import os

# 加载轻量语音识别模型
model = whisper.load_model("small")

def audio_to_text(audio_path):
    """麦克风录音文件转文字"""
    result = model.transcribe(audio_path, language="zh")
    return result["text"]

async def text_to_audio(text, save_path):
    """文字生成语音音频"""
    voice = "zh-CN-YunyangNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save_sync(save_path)
    return save_path