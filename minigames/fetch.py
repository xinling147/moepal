import pygame
import random
import math

class FetchGame:
    def __init__(self, screen, dog):
        self.screen = screen
        self.dog = dog
        self.width, self.height = screen.get_size()
        
        # 游戏状态
        self.active = False
        self.score = 0
        self.time_left = 30  # 30秒游戏时间
        self.start_time = 0
        
        # 飞盘属性
        self.frisbee_pos = [0, 0]
        self.frisbee_velocity = [0, 0]
        self.frisbee_thrown = False
        self.frisbee_caught = False
        
        # 狗狗位置和移动
        self.dog_game_pos = [self.width // 2, self.height - 100]
        self.dog_target = [0, 0]
        self.dog_speed = 5
        
        # 颜色
        self.colors = {
            "background": (135, 206, 235),  # 天蓝色
            "text": (50, 50, 50),
            "frisbee": (255, 0, 0),
            "dog": (150, 120, 90),
            "button": (70, 130, 180),
            "button_hover": (100, 149, 237),
            "button_text": (255, 255, 255)
        }
        
        # 字体
        self.font = pygame.font.SysFont("Arial", 24)
        self.font_large = pygame.font.SysFont("Arial", 36)
        
        # 加载资源
        self.load_resources()
    
    def load_resources(self):
        """加载游戏资源"""
        # 创建简单的像素风格飞盘
        self.frisbee_img = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.frisbee_img, (255, 0, 0), (15, 15), 15)
        pygame.draw.circle(self.frisbee_img, (220, 0, 0), (15, 15), 10)
        pygame.draw.circle(self.frisbee_img, (200, 0, 0), (15, 15), 5)
        
        # 创建简单的像素风格狗狗
        self.dog_img = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.ellipse(self.dog_img, self.colors["dog"], (0, 10, 50, 30))  # 身体
        pygame.draw.circle(self.dog_img, self.colors["dog"], (40, 15), 15)  # 头
        pygame.draw.ellipse(self.dog_img, (100, 80, 60), (45, 5, 10, 10))  # 耳朵
        pygame.draw.ellipse(self.dog_img, (0, 0, 0), (45, 15, 5, 5))  # 眼睛
    
    def start_game(self):
        """开始游戏"""
        self.active = True
        self.score = 0
        self.time_left = 30
        self.start_time = pygame.time.get_ticks()
        self.frisbee_thrown = False
        self.frisbee_caught = False
        self.dog_game_pos = [self.width // 2, self.height - 100]
    
    def throw_frisbee(self, start_pos, end_pos):
        """投掷飞盘"""
        if not self.frisbee_thrown and self.active:
            self.frisbee_pos = list(start_pos)
            
            # 计算飞盘速度（基于投掷方向和力度）
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            distance = max(1, math.sqrt(dx*dx + dy*dy))
            
            # 标准化并设置速度
            self.frisbee_velocity = [
                dx / distance * 10,  # 水平速度
                dy / distance * 10   # 垂直速度
            ]
            
            self.frisbee_thrown = True
            self.frisbee_caught = False
            
            # 设置狗狗的目标位置（预测飞盘落点）
            flight_time = abs(self.height - start_pos[1]) / abs(self.frisbee_velocity[1]) if self.frisbee_velocity[1] != 0 else 1
            target_x = start_pos[0] + self.frisbee_velocity[0] * flight_time
            target_x = max(50, min(self.width - 50, target_x))  # 确保在屏幕范围内
            self.dog_target = [target_x, self.height - 100]
    
    def update(self):
        """更新游戏状态"""
        if not self.active:
            return
        
        # 更新时间
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.start_time) / 1000  # 转换为秒
        self.time_left = max(0, 30 - elapsed)
        
        # 游戏时间结束
        if self.time_left <= 0:
            self.end_game()
            return
        
        # 更新飞盘位置
        if self.frisbee_thrown and not self.frisbee_caught:
            self.frisbee_pos[0] += self.frisbee_velocity[0]
            self.frisbee_pos[1] += self.frisbee_velocity[1]
            
            # 添加重力效果
            self.frisbee_velocity[1] += 0.2
            
            # 检查是否接住飞盘
            dog_rect = pygame.Rect(self.dog_game_pos[0] - 25, self.dog_game_pos[1] - 25, 50, 50)
            frisbee_rect = pygame.Rect(self.frisbee_pos[0] - 15, self.frisbee_pos[1] - 15, 30, 30)
            
            if dog_rect.colliderect(frisbee_rect):
                self.frisbee_caught = True
                self.score += 1
                # 狗狗技能等级影响得分
                if "接飞盘" in self.dog.skills:
                    self.score += self.dog.skills["接飞盘"] // 2
            
            # 检查飞盘是否落地或出界
            if (self.frisbee_pos[1] > self.height or 
                self.frisbee_pos[0] < 0 or 
                self.frisbee_pos[0] > self.width):
                self.frisbee_thrown = False
        
        # 更新狗狗位置（向目标移动）
        if self.frisbee_thrown and not self.frisbee_caught:
            dx = self.dog_target[0] - self.dog_game_pos[0]
            distance = abs(dx)
            
            if distance > self.dog_speed:
                self.dog_game_pos[0] += self.dog_speed if dx > 0 else -self.dog_speed
        else:
            # 没有飞盘时随机移动
            if random.random() < 0.01:  # 1%的几率改变目标
                self.dog_target[0] = random.randint(50, self.width - 50)
            
            dx = self.dog_target[0] - self.dog_game_pos[0]
            distance = abs(dx)
            
            if distance > self.dog_speed:
                self.dog_game_pos[0] += self.dog_speed / 2 if dx > 0 else -self.dog_speed / 2
    
    def render(self):
        """渲染游戏画面"""
        # 绘制背景
        self.screen.fill(self.colors["background"])
        
        if not self.active:
            # 绘制开始游戏按钮
            button_rect = pygame.Rect(self.width//2 - 100, self.height//2 - 25, 200, 50)
            mouse_pos = pygame.mouse.get_pos()
            button_color = self.colors["button_hover"] if button_rect.collidepoint(mouse_pos) else self.colors["button"]
            
            pygame.draw.rect(self.screen, button_color, button_rect)
            pygame.draw.rect(self.screen, (50, 50, 50), button_rect, 2)  # 边框
            
            text = self.font_large.render("开始游戏", True, self.colors["button_text"])
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            
            # 绘制游戏说明
            instructions = [
                "接飞盘游戏",
                "点击并拖动鼠标来投掷飞盘",
                "让你的狗狗接住尽可能多的飞盘",
                "游戏时间: 30秒"
            ]
            
            for i, line in enumerate(instructions):
                text = self.font.render(line, True, self.colors["text"])
                self.screen.blit(text, (self.width//2 - text.get_width()//2, self.height//2 - 150 + i*40))
            
            return
        
        # 绘制狗狗
        self.screen.blit(self.dog_img, (self.dog_game_pos[0] - 25, self.dog_game_pos[1] - 25))
        
        # 绘制飞盘
        if self.frisbee_thrown and not self.frisbee_caught:
            self.screen.blit(self.frisbee_img, (self.frisbee_pos[0] - 15, self.frisbee_pos[1] - 15))
        
        # 绘制分数和时间
        score_text = self.font.render(f"得分: {self.score}", True, self.colors["text"])
        self.screen.blit(score_text, (20, 20))
        
        time_text = self.font.render(f"时间: {int(self.time_left)}秒", True, self.colors["text"])
        self.screen.blit(time_text, (self.width - 150, 20))
        
        # 如果没有投掷飞盘，显示提示
        if not self.frisbee_thrown:
            hint_text = self.font.render("点击并拖动鼠标来投掷飞盘", True, self.colors["text"])
            self.screen.blit(hint_text, (self.width//2 - hint_text.get_width()//2, 60))
    
    def handle_event(self, event):
        """处理游戏事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.active:
                # 检查是否点击了开始按钮
                button_rect = pygame.Rect(self.width//2 - 100, self.height//2 - 25, 200, 50)
                if button_rect.collidepoint(event.pos):
                    self.start_game()
            else:
                # 开始投掷飞盘
                self.start_pos = event.pos
        
        elif event.type == pygame.MOUSEBUTTONUP and self.active:
            # 完成投掷飞盘
            if hasattr(self, 'start_pos') and not self.frisbee_thrown:
                self.throw_frisbee(self.start_pos, event.pos)
    
    def end_game(self):
        """结束游戏"""
        self.active = False
        
        # 根据得分增加狗狗的技能经验
        if "接飞盘" in self.dog.skills:
            current_level = self.dog.skills["接飞盘"]
            if current_level < 5:  # 最高5级
                # 根据得分增加经验，每5分增加1级
                new_level = min(5, current_level + self.score // 5)
                if new_level > current_level:
                    self.dog.skills["接飞盘"] = new_level
        else:
            # 首次玩游戏，初始化技能
            if self.score >= 3:  # 至少需要3分才能获得技能
                self.dog.skills["接飞盘"] = 1
        
        # 增加狗狗的快乐度和亲密度
        happiness_gain = min(30, self.score * 2)
        self.dog.happiness = min(100, self.dog.happiness + happiness_gain)
        
        affection_gain = min(15, self.score)
        self.dog.affection = min(100, self.dog.affection + affection_gain)
        
        # 消耗精力
        energy_cost = min(40, 20 + self.score * 2)
        self.dog.energy = max(0, self.dog.energy - energy_cost)