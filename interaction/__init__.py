# 交互功能包初始化文件
from .voice import VoiceRecognition
from .touch import TouchInteraction
from .emotion import EmotionSystem

# 导出交互类
__all__ = ['VoiceRecognition', 'TouchInteraction', 'EmotionSystem']