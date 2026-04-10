"""
TTS 配音模块 - 使用 Qwen TTS (API / Local)
"""
import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QwenTTS:
    """Qwen TTS 配音器 (API 版本)"""
    subtitles: List[Dict]
    target_language: str = "en"
    api_key: Optional[str] = None
    model: str = "qwen3-tts-flash"
    voice: str = "Cherry"
    output_dir: str = "./output"
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("Qwen TTS API key is required")
        self.output_path = Path(self.output_dir)
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def synthesize(self) -> List[Dict]:
        """
        执行 TTS，返回带音频文件路径的字幕列表
        Returns:
            List[Dict]: [{"start_time": 0.0, "end_time": 1.5, "text": "...", "filename": "path/to/audio.wav"}]
        """
        try:
            import dashscope
            import requests
            
            logger.info(f"Using Qwen TTS model: {self.model}")
            
            for i, sub in enumerate(self.subtitles):
                if not sub.get("text", "").strip():
                    continue
                
                output_file = self.output_path / f"audio_{i:04d}.wav"
                
                # 调用 Qwen TTS API
                response = dashscope.audio.qwen_tts.SpeechSynthesizer.call(
                    model=self.model,
                    api_key=self.api_key,
                    text=sub["text"],
                    voice=self.voice
                )
                
                if response is None:
                    raise RuntimeError("API call returned None response")
                
                if not hasattr(response, 'output') or response.output is None:
                    raise RuntimeError(f"TTS API error: {response.message if hasattr(response, 'message') else str(response)}")
                
                # 下载音频文件
                audio_url = response.output.audio.get("url")
                if not audio_url:
                    raise RuntimeError("No audio URL in response")
                
                res = requests.get(audio_url)
                res.raise_for_status()
                
                # 保存为 WAV
                with open(output_file, 'wb') as f:
                    f.write(res.content)
                
                sub["filename"] = str(output_file)
                logger.info(f"Generated audio for segment {i+1}/{len(self.subtitles)}")
            
            return self.subtitles
            
        except ImportError as e:
            logger.error(f"dashscope not installed: {e}")
            raise RuntimeError("Please install dashscope: pip install dashscope")
    
    def merge_audio(self, output_path: str) -> str:
        """合并所有音频片段为一个文件"""
        from pydub import AudioSegment
        
        merged = AudioSegment.empty()
        
        for sub in self.subtitles:
            if "filename" in sub and Path(sub["filename"]).exists():
                audio = AudioSegment.from_wav(sub["filename"])
                # 根据时间戳添加静音间隔
                silence_duration = int(sub["start_time"] * 1000) - len(merged)
                if silence_duration > 0:
                    merged += AudioSegment.silent(duration=silence_duration)
                merged += audio
        
        output_file = Path(output_path)
        merged.export(str(output_file), format="wav")
        logger.info(f"Merged audio saved to: {output_file}")
        return str(output_file)


@dataclass
class QwenTTSLocal:
    """Qwen TTS Local 版本 (需要额外安装 qwen-tts)"""
    subtitles: List[Dict]
    target_language: str = "en"
    model_name: str = "1.7B"
    output_dir: str = "./output"
    is_cuda: bool = False
    
    def __post_init__(self):
        self.output_path = Path(self.output_dir)
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def synthesize(self) -> List[Dict]:
        """
        使用本地 Qwen TTS 模型进行合成
        TODO: 实现本地 Qwen TTS 推理
        """
        logger.warning("Local Qwen TTS is not yet fully implemented.")
        logger.warning("Please use QwenTTS (API version) or implement local inference.")
        
        # 这里可以集成 qwen-tts 本地推理
        # 参考：https://github.com/QwenLM/Qwen3-TTS
        
        raise NotImplementedError("Local Qwen TTS requires implementation")
