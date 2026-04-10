"""
文本翻译模块 - 使用本地 LLM API 进行翻译
"""
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Translator:
    """本地 LLM 翻译器"""
    subtitles: List[Dict]
    target_language: str
    api_url: str = "http://localhost:1234/v1"
    api_key: str = "not-needed"
    model_name: str = "local-model"
    max_token: int = 4096
    temperature: float = 0.2
    
    def translate(self) -> List[Dict]:
        """
        执行翻译，返回翻译后的字幕列表
        Returns:
            List[Dict]: [{"start_time": 0.0, "end_time": 1.5, "text": "翻译后的文本"}]
        """
        try:
            from openai import OpenAI
            import httpx
            
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_url,
                http_client=httpx.Client()
            )
            
            # 批量翻译 (每批最多 10 条)
            batch_size = 10
            translated_subtitles = []
            
            for i in range(0, len(self.subtitles), batch_size):
                batch = self.subtitles[i:i + batch_size]
                batch_texts = [sub["text"] for sub in batch]
                
                prompt = self._build_prompt(batch_texts)
                
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a professional subtitle translation engine."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_token,
                    temperature=self.temperature
                )
                
                translated_text = response.choices[0].message.content.strip()
                
                # 解析翻译结果
                translated_lines = self._parse_translation(translated_text, len(batch_texts))
                
                for j, sub in enumerate(batch):
                    translated_subtitles.append({
                        "start_time": sub["start_time"],
                        "end_time": sub["end_time"],
                        "text": translated_lines[j] if j < len(translated_lines) else sub["text"]
                    })
                
                logger.info(f"Translated batch {i//batch_size + 1}")
            
            return translated_subtitles
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise
    
    def _build_prompt(self, texts: List[str]) -> str:
        """构建翻译提示词"""
        input_text = "\n".join(texts)
        return f"""Translate the following text to {self.target_language}. 
Only output the translation, one line per input line. Do not include any explanations.

<input>
{input_text}
</input>

Translation:"""
    
    def _parse_translation(self, text: str, expected_lines: int) -> List[str]:
        """解析翻译结果"""
        # 尝试提取 <TRANSLATE_TEXT> 标签内容
        match = re.search(r'<TRANSLATE_TEXT>(.*?)</TRANSLATE_TEXT>', text, re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(1)
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 如果行数不匹配，尝试其他解析方式
        if len(lines) != expected_lines:
            # 可能返回的是单行，用标点分割
            if len(lines) == 1 and expected_lines > 1:
                import re
                lines = re.split(r'[.!?。！？;；]', lines[0])
                lines = [l.strip() for l in lines if l.strip()]
        
        return lines[:expected_lines]
    
    def save_to_srt(self, subtitles: List[Dict], output_path: str) -> str:
        """保存字幕为 SRT 格式"""
        def format_time(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
        srt_content = ""
        for i, sub in enumerate(subtitles, 1):
            srt_content += f"{i}\n"
            srt_content += f"{format_time(sub['start_time'])} --> {format_time(sub['end_time'])}\n"
            srt_content += f"{sub['text']}\n\n"
        
        output_file = Path(output_path)
        output_file.write_text(srt_content, encoding="utf-8")
        logger.info(f"Translated SRT saved to: {output_file}")
        return str(output_file)
