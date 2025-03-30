import pygame
import random
import time
import math

class EmotionSystem:
    def __init__(self, dog):
        self.dog = dog
        
        # 情感状态
        self.current_emotion = "normal"  # 当前情感：normal, happy, sad, angry, tired, hungry, excited
        self.emotion_intensity = 0.5     # 情感强度（0-1）
        self.emotion_change_time = 0     # 上次情感变化时间
        
        # 情感记忆
        self.last_interaction_time = time.time()
        self.interaction_history = []    # 记录最近的互动
        self.interaction_count = 0       # 互动次数
        
        # 情感表达
        self.expression_frames = {}      # 表情动画帧
        self.current_frame = 0
        self.animation_time = 0
        
        # 加载表情资源（这里使用占位符）
        self.load_expressions()
        
        # 情感音效（占位）
        self.sounds = {}
    
    def load_expressions(self):
        """加载表情资源（使用简单的占位图像）"""
        # 在实际应用中，这里应该加载真实的表情图像
        # 这里创建简单的占位符
        expressions = ["normal", "happy", "sad", "angry", "tired", "hungry", "excited"]
        
        for expr in expressions:
            # 为每种表情创建3帧动画
            self.expression_frames[expr] = []
            for i in range(3):
                # 创建一个简单的表情图像
                frame = pygame.Surface((50, 50), pygame.SRCALPHA)
                
                # 根据表情类型绘制不同的图像
                if expr == "normal":
                    color = (150, 150, 150)
                    # 普通表情 - 中性眼睛和嘴巴
                    pygame.draw.circle(frame, color, (25, 25), 20)  # 脸
                    pygame.draw.circle(frame, (0, 0, 0), (15, 20), 3)  # 左眼
                    pygame.draw.circle(frame, (0, 0, 0), (35, 20), 3)  # 右眼
                    pygame.draw.arc(frame, (0, 0, 0), (15, 25, 20, 10), 0, math.pi, 2)  # 嘴
                
                elif expr == "happy":
                    color = (255, 200, 100)
                    # 开心表情 - 弯曲的眼睛和微笑
                    pygame.draw.circle(frame, color, (25, 25), 20)  # 脸
                    # 眼睛随动画帧变化
                    eye_height = 18 + i
                    pygame.draw.arc(frame, (0, 0, 0), (10, eye_height, 10, 5), math.pi, 2*math.pi, 2)  # 左眼
                    pygame.draw.arc(frame, (0, 0, 0), (30, eye_height, 10, 5), math.pi, 2*math.pi, 2)  # 右眼
                    pygame.draw.arc(frame, (0, 0, 0), (10, 25, 30, 15), 0, math.pi, 2)  # 微笑
                
                elif expr == "sad":
                    color = (100, 150, 200)
                    # 悲伤表情 - 下垂的眼睛和嘴巴
                    pygame.draw.circle(frame, color, (25, 25), 20)  # 脸
                    pygame.draw.circle(frame, (0, 0, 0), (15, 20), 3)  # 左眼
                    pygame.draw.circle(frame, (0, 0, 0), (35, 20), 3)  # 右眼
                    pygame.draw.arc(frame, (0, 0, 0), (15, 30, 20, 10), math.pi, 2*math.pi, 2)  # 嘴
                
                elif expr == "angry":
                    color = (255, 100, 100)
                    # 生气表情 - 皱眉和抿嘴
                    pygame.draw.circle(frame, color, (25, 25), 20)  # 脸
                    # 眉毛
                    pygame.draw.line(frame, (0, 0, 0), (10, 15), (20, 18), 2)  # 左眉
                    pygame.draw.line(frame, (0, 0, 0), (40, 15), (30, 18), 2)  # 右眉
                    pygame.draw.circle(frame, (0, 0, 0), (15, 22), 3)  # 左眼
                    pygame.draw.circle(frame, (0, 0, 0), (35, 22), 3)  # 右眼
                    pygame.draw.line(frame, (0, 0, 0), (15, 35), (35, 35), 2)  # 嘴
                
                elif expr == "tired":
                    color = (180, 180, 200)
                    # 疲倦表情 - 半闭的眼睛
                    pygame.draw.circle(frame, color, (25, 25), 20)  # 脸
                    # 眼睛随动画帧变化
                    eye_height = 3 - i
                    pygame.draw.ellipse(frame, (0, 0, 0), (10, 20, 10, eye_height))  # 左眼
                    pygame.draw.ellipse(frame, (0, 0, 0), (30, 20, 10, eye_height))  # 右眼
                    pygame.draw.arc(frame, (0, 0, 0), (15, 30, 20, 5), 0, math.pi, 2)  # 嘴
                
                elif expr == "hungry":
                    color = (220, 220, 150)
                    # 饥饿表情 - 张开的嘴
                    pygame.draw.circle(frame, color, (25, 25), 20)  # 脸
                    pygame.draw.circle(frame, (0, 0, 0), (15, 20), 3)  # 左眼
                    pygame.draw.circle(frame, (0, 0, 0), (35, 20), 3)  # 右眼
                    # 嘴随动画帧变化
                    mouth_height = 10 + i*2
                    pygame.draw.ellipse(frame, (0, 0, 0), (15, 30, 20, mouth_height))  # 张开的嘴
                
                elif expr == "excited":
                    color = (255, 150, 150)
                    # 兴奋表情 - 大眼睛和大笑
                    pygame.draw.circle(frame, color, (25, 25), 20)  # 脸
                    # 眼睛随动画帧变化
                    eye_size = 4 + i
                    pygame.draw.circle(frame, (0, 0, 0), (15, 18), eye_size)  # 左眼
                    pygame.draw.circle(frame, (0, 0, 0), (35, 18), eye_size)  # 右眼
                    pygame.draw.arc(frame, (0, 0, 0), (10, 25, 30, 15), 0, math.pi, 3)  # 大笑
                
                self.expression_frames[expr].append(frame)
    
    def update(self):
        """更新情感状态"""
        current_time = time.time()
        
        # 检查是否需要更新情感状态（每10秒检查一次）
        if current_time - self.emotion_change_time > 10:
            self.update_emotion()
            self.emotion_change_time = current_time
        
        # 检查长时间无互动
        if current_time - self.last_interaction_time > 3600:  # 1小时无互动
            hours_without_interaction = (current_time - self.last_interaction_time) / 3600
            if hours_without_interaction > 24:  # 超过24小时
                self.current_emotion = "sad"
                self.emotion_intensity = min(1.0, hours_without_interaction / 48)  # 最多2天达到最大强度
            else:
                # 根据无互动时间逐渐变得无聊或想念
                if random.random() < 0.7:  # 70%几率变得想念
                    self.current_emotion = "sad"
                else:  # 30%几率变得生气
                    self.current_emotion = "angry"
                self.emotion_intensity = min(1.0, hours_without_interaction / 24)
        
        # 更新动画帧
        if current_time - self.animation_time > 0.2:  # 每200毫秒更新一帧
            self.current_frame = (self.current_frame + 1) % 3
            self.animation_time = current_time
    
    def update_emotion(self):
        """根据宠物状态更新情感"""
        # 基于宠物状态确定情感
        if self.dog.hunger < 30:
            self.current_emotion = "hungry"
            self.emotion_intensity = (30 - self.dog.hunger) / 30
        elif self.dog.energy < 20:
            self.current_emotion = "tired"
            self.emotion_intensity = (20 - self.dog.energy) / 20
        elif self.dog.happiness < 30:
            if random.random() < 0.7:  # 70%几率变得悲伤
                self.current_emotion = "sad"
            else:  # 30%几率变得生气
                self.current_emotion = "angry"
            self.emotion_intensity = (30 - self.dog.happiness) / 30
        elif self.dog.happiness > 80:
            if random.random() < 0.6:  # 60%几率变得开心
                self.current_emotion = "happy"
            else:  # 40%几率变得兴奋
                self.current_emotion = "excited"
            self.emotion_intensity = (self.dog.happiness - 80) / 20
        else:
            self.current_emotion = "normal"
            self.emotion_intensity = 0.5
        
        # 性格影响情感表达
        if self.dog.personality == "活泼":
            # 活泼的狗更容易表现出兴奋和开心
            if self.current_emotion == "normal" and random.random() < 0.3:
                self.current_emotion = "happy"
        elif self.dog.personality == "温顺":
            # 温顺的狗很少表现出生气
            if self.current_emotion == "angry":
                self.current_emotion = "sad"
        elif self.dog.personality == "机警":
            # 机警的狗更容易表现出紧张或兴奋
            if self.current_emotion == "normal" and random.random() < 0.3:
                self.current_emotion = "excited"
        elif self.dog.personality == "顽皮":
            # 顽皮的狗更容易表现出兴奋
            if self.current_emotion == "happy" and random.random() < 0.5:
                self.current_emotion = "excited"
        elif self.dog.personality == "独立":
            # 独立的狗情感表达更加平静
            if self.current_emotion in ["excited", "happy"] and random.random() < 0.3:
                self.current_emotion = "normal"
    
    def record_interaction(self, interaction_type):
        """记录互动"""
        self.last_interaction_time = time.time()
        self.interaction_count += 1
        
        # 记录最近的10次互动
        self.interaction_history.append(interaction_type)
        if len(self.interaction_history) > 10:
            self.interaction_history.pop(0)
        
        # 根据互动类型更新情感
        if interaction_type == "feed":
            if self.dog.hunger < 30:  # 如果很饿，喂食会让狗很开心
                self.current_emotion = "happy"
                self.emotion_intensity = 0.8
            else:  # 如果不是很饿，效果一般
                self.current_emotion = "normal"
                self.emotion_intensity = 0.5
        
        elif interaction_type == "play":
            if self.dog.energy > 50:  # 如果精力充沛，玩耍会让狗兴奋
                self.current_emotion = "excited"
                self.emotion_intensity = 0.9
            else:  # 如果精力不足，效果一般
                self.current_emotion = "happy"
                self.emotion_intensity = 0.6
        
        elif interaction_type == "pet":
            # 抚摸通常会让狗开心
            self.current_emotion = "happy"
            self.emotion_intensity = 0.7
        
        elif interaction_type == "bath":
            # 根据性格决定对洗澡的反应
            if self.dog.personality in ["活泼", "顽皮"]:
                self.current_emotion = "angry"
                self.emotion_intensity = 0.6
            else:
                self.current_emotion = "normal"
                self.emotion_intensity = 0.5
        
        elif interaction_type == "sleep":
            # 睡觉前通常是疲倦的
            self.current_emotion = "tired"
            self.emotion_intensity = 0.7
        
        # 更新情感变化时间
        self.emotion_change_time = time.time()
    
    def get_current_expression(self):
        """获取当前表情图像"""
        if self.current_emotion in self.expression_frames:
            return self.expression_frames[self.current_emotion][self.current_frame]
        else:
            return self.expression_frames["normal"][0]
    
    def get_emotion_description(self):
        """获取情感描述"""
        descriptions = {
            "normal": "平静",
            "happy": "开心",
            "sad": "难过",
            "angry": "生气",
            "tired": "疲倦",
            "hungry": "饥饿",
            "excited": "兴奋"
        }
        
        intensity_desc = ""
        if self.emotion_intensity > 0.8:
            intensity_desc = "非常"
        elif self.emotion_intensity > 0.5:
            intensity_desc = "比较"
        elif self.emotion_intensity > 0.3:
            intensity_desc = "有点"
        
        emotion_name = descriptions.get(self.current_emotion, "平静")
        return f"{intensity_desc}{emotion_name}"
    
    def get_emotion_message(self):
        """获取基于情感的消息"""
        messages = {
            "normal": [
                f"{self.dog.name}看起来很放松。",
                f"{self.dog.name}平静地看着你。",
                f"{self.dog.name}摇了摇尾巴。"
            ],
            "happy": [
                f"{self.dog.name}看起来很开心！",
                f"{self.dog.name}兴奋地摇着尾巴。",
                f"{self.dog.name}快乐地转了个圈。"
            ],
            "sad": [
                f"{self.dog.name}看起来有点难过。",
                f"{self.dog.name}发出轻轻的呜咽声。",
                f"{self.dog.name}耷拉着耳朵。"
            ],
            "angry": [
                f"{self.dog.name}看起来有点不高兴。",
                f"{self.dog.name}发出低沉的咆哮声。",
                f"{self.dog.name}不耐烦地走来走去。"
            ],
            "tired": [
                f"{self.dog.name}看起来很疲倦。",
                f"{self.dog.name}打了个哈欠。",
                f"{self.dog.name}想找个地方睡觉。"
            ],
            "hungry": [
                f"{self.dog.name}的肚子咕咕叫，看起来很饿。",
                f"{self.dog.name}盯着食物碗。",
                f"{self.dog.name}用鼻子拱你的手，似乎在要吃的。"
            ],
            "excited": [
                f"{self.dog.name}兴奋地跳来跳去！",
                f"{self.dog.name}发出开心的叫声。",
                f"{self.dog.name}迫不及待地想玩耍。"
            ]
        }
        
        if self.current_emotion in messages:
            return random.choice(messages[self.current_emotion])
        else:
            return random.choice(messages["normal"])
    
    def render(self, screen, x, y):
        """渲染情感表达"""
        # 获取当前表情
        expression = self.get_current_expression()
        
        # 根据情感强度调整大小
        size_factor = 1.0 + (self.emotion_intensity * 0.3)  # 强度越高，表情越大
        scaled_size = int(50 * size_factor)
        scaled_expression = pygame.transform.scale(expression, (scaled_size, scaled_size))
        
        # 居中绘制
        pos_x = x - scaled_size // 2
        pos_y = y - scaled_size // 2
        screen.blit(scaled_expression, (pos_x, pos_y))
        
        # 绘制情感描述（可选）
        font = pygame.font.SysFont("Arial", 16)
        emotion_text = font.render(self.get_emotion_description(), True, (50, 50, 50))
        screen.blit(emotion_text, (x - emotion_text.get_width() // 2, y + scaled_size // 2 + 5))