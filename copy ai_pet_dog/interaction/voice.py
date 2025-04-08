import pygame
import os
import time
import random

# 注意：这是一个模拟的语音识别模块
# 在实际应用中，可以使用如speech_recognition库进行真实的语音识别
# 但为了简化实现，这里使用模拟的方式

class VoiceRecognition:
    def __init__(self, dog):
        self.dog = dog
        self.is_listening = False
        self.recognized_command = None
        self.recognition_time = 0
        self.recognition_duration = 2  # 模拟识别需要2秒
        
        # 可识别的命令列表
        self.available_commands = {
            "坐下": self.command_sit,
            "握手": self.command_handshake,
            "打滚": self.command_roll,
            "接飞盘": self.command_fetch,
            "捡球": self.command_ball,
            "等待": self.command_stay,
            "好狗狗": self.command_praise
        }
        
        # 语音识别状态消息
        self.status_message = ""
    
    def start_listening(self):
        """开始监听语音命令"""
        if not self.is_listening:
            self.is_listening = True
            self.recognition_time = time.time()
            self.status_message = "正在聆听..."
            return True
        return False
    
    def update(self):
        """更新语音识别状态"""
        if self.is_listening:
            # 模拟语音识别过程
            elapsed_time = time.time() - self.recognition_time
            
            if elapsed_time >= self.recognition_duration:
                self.is_listening = False
                
                # 模拟识别结果（随机选择一个命令或无法识别）
                if random.random() < 0.7:  # 70%的识别成功率
                    self.recognized_command = random.choice(list(self.available_commands.keys()))
                    self.status_message = f"识别到命令: {self.recognized_command}"
                    
                    # 执行命令
                    self.execute_command(self.recognized_command)
                else:
                    self.recognized_command = None
                    self.status_message = "无法识别命令，请再试一次"
    
    def execute_command(self, command):
        """执行识别到的命令"""
        if command in self.available_commands:
            # 检查狗狗是否有对应的技能
            skill_required = command not in ["好狗狗"]  # 表扬不需要技能
            
            if skill_required and (command not in self.dog.skills or self.dog.skills[command] < 1):
                self.status_message = f"{self.dog.name}还不会{command}这个技能"
                return False
            
            # 执行命令对应的方法
            result = self.available_commands[command]()
            return result
        
        return False
    
    def command_sit(self):
        """坐下命令"""
        skill_level = self.dog.skills.get("坐下", 0)
        success_rate = 0.5 + (skill_level * 0.1)  # 基础成功率50%，每级技能+10%
        
        if random.random() < success_rate:
            self.status_message = f"{self.dog.name}听到命令后乖乖坐下了"
            # 增加亲密度
            self.dog.affection = min(100, self.dog.affection + 2)
            return True
        else:
            self.status_message = f"{self.dog.name}没有理解你的命令"
            return False
    
    def command_handshake(self):
        """握手命令"""
        skill_level = self.dog.skills.get("握手", 0)
        success_rate = 0.5 + (skill_level * 0.1)
        
        if random.random() < success_rate:
            self.status_message = f"{self.dog.name}伸出爪子和你握手"
            self.dog.affection = min(100, self.dog.affection + 2)
            self.dog.happiness = min(100, self.dog.happiness + 3)
            return True
        else:
            self.status_message = f"{self.dog.name}歪着头看着你"
            return False
    
    def command_roll(self):
        """打滚命令"""
        skill_level = self.dog.skills.get("打滚", 0)
        success_rate = 0.4 + (skill_level * 0.12)  # 基础成功率40%，每级技能+12%
        
        if random.random() < success_rate:
            self.status_message = f"{self.dog.name}在地上开心地打了个滚"
            self.dog.affection = min(100, self.dog.affection + 3)
            self.dog.happiness = min(100, self.dog.happiness + 5)
            # 轻微降低清洁度
            self.dog.cleanliness = max(0, self.dog.cleanliness - 3)
            return True
        else:
            self.status_message = f"{self.dog.name}似乎不想打滚"
            return False
    
    def command_fetch(self):
        """接飞盘命令"""
        skill_level = self.dog.skills.get("接飞盘", 0)
        success_rate = 0.3 + (skill_level * 0.14)  # 基础成功率30%，每级技能+14%
        
        if random.random() < success_rate:
            self.status_message = f"{self.dog.name}准备好接飞盘了！"
            self.dog.happiness = min(100, self.dog.happiness + 4)
            return True
        else:
            self.status_message = f"{self.dog.name}看起来对飞盘不感兴趣"
            return False
    
    def command_ball(self):
        """捡球命令"""
        skill_level = self.dog.skills.get("捡球", 0)
        success_rate = 0.4 + (skill_level * 0.12)
        
        if random.random() < success_rate:
            self.status_message = f"{self.dog.name}跑去找球了"
            self.dog.happiness = min(100, self.dog.happiness + 4)
            # 消耗一点精力
            self.dog.energy = max(0, self.dog.energy - 2)
            return True
        else:
            self.status_message = f"{self.dog.name}没有理解你的命令"
            return False
    
    def command_stay(self):
        """等待命令"""
        skill_level = self.dog.skills.get("原地等待", 0)
        success_rate = 0.3 + (skill_level * 0.14)
        
        if random.random() < success_rate:
            self.status_message = f"{self.dog.name}乖乖地原地等待"
            self.dog.affection = min(100, self.dog.affection + 3)
            return True
        else:
            self.status_message = f"{self.dog.name}坐不住，到处走动"
            return False
    
    def command_praise(self):
        """表扬命令"""
        # 表扬总是成功的
        self.status_message = f"{self.dog.name}听到表扬非常开心！"
        self.dog.happiness = min(100, self.dog.happiness + 5)
        self.dog.affection = min(100, self.dog.affection + 3)
        return True
    
    def render(self, screen, x, y):
        """渲染语音识别状态"""
        font = pygame.font.SysFont("Arial", 20)
        
        # 绘制状态消息
        if self.status_message:
            text_surface = font.render(self.status_message, True, (50, 50, 50))
            screen.blit(text_surface, (x, y))
        
        # 如果正在监听，绘制动画指示器
        if self.is_listening:
            # 绘制麦克风图标或动画
            elapsed_time = time.time() - self.recognition_time
            animation_frame = int((elapsed_time % 1) * 4)  # 0-3的动画帧
            
            # 简单的动画效果
            radius = 10 + animation_frame * 2
            pygame.draw.circle(screen, (255, 0, 0), (x - 20, y + 10), radius, 2)
            
            # 绘制进度条
            progress = min(1.0, elapsed_time / self.recognition_duration)
            pygame.draw.rect(screen, (200, 200, 200), (x, y + 25, 100, 10))
            pygame.draw.rect(screen, (0, 200, 0), (x, y + 25, int(100 * progress), 10))