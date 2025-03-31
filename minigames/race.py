import pygame
import random
import time

class RaceGame:
    def __init__(self, screen, dog):
        self.screen = screen
        self.dog = dog
        self.width, self.height = screen.get_size()
        
        # 游戏状态
        self.active = False
        self.score = 0
        self.distance = 0  # 跑步距离
        self.time_left = 45  # 45秒游戏时间
        self.start_time = 0
        
        # 玩家设置
        self.player_y = self.height - 100
        self.player_x = 100
        self.player_speed = 0
        self.player_jump = False
        self.player_jump_height = 0
        self.gravity = 1
        
        # 障碍物
        self.obstacles = []
        self.obstacle_speed = 5
        self.obstacle_timer = 0
        
        # 颜色
        self.colors = {
            "background": (200, 230, 255),
            "player": (150, 120, 90),
            "obstacle": (100, 100, 100),
            "ground": (100, 180, 100),
            "text": (50, 50, 50),
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
        # 创建简单的像素风格狗狗
        self.dog_img = pygame.Surface((50, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(self.dog_img, self.colors["player"], (0, 0, 40, 20))  # 身体
        pygame.draw.circle(self.dog_img, self.colors["player"], (40, 10), 10)  # 头
        pygame.draw.ellipse(self.dog_img, (100, 80, 60), (45, 5, 5, 5))  # 耳朵
        pygame.draw.ellipse(self.dog_img, (0, 0, 0), (45, 10, 2, 2))  # 眼睛
        
        # 障碍物图像
        self.obstacle_img = pygame.Surface((20, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.obstacle_img, self.colors["obstacle"], (0, 0, 20, 40))
    
    def start_game(self):
        """开始游戏"""
        self.active = True
        self.score = 0
        self.distance = 0
        self.time_left = 45
        self.start_time = time.time()
        self.obstacles = []
        self.player_jump = False
        self.player_jump_height = 0
        self.player_y = self.height - 100
        self.obstacle_speed = 5
    
    def update(self):
        """更新游戏状态"""
        if not self.active:
            return True
        
        # 更新时间
        current_time = time.time()
        self.time_left = max(0, 45 - (current_time - self.start_time))
        
        # 游戏时间结束
        if self.time_left <= 0:
            self.end_game()
            return False
        
        # 更新玩家跳跃
        if self.player_jump:
            self.player_jump_height -= self.gravity
            self.player_y -= self.player_jump_height
            
            # 检查是否着地
            if self.player_y >= self.height - 100:
                self.player_y = self.height - 100
                self.player_jump = False
        
        # 增加距离和分数
        self.distance += self.obstacle_speed / 10
        self.score = int(self.distance)
        
        # 逐渐增加难度
        if self.score > 0 and self.score % 10 == 0:
            self.obstacle_speed = min(15, 5 + self.score / 10)
        
        # 生成障碍物
        self.obstacle_timer -= 1
        if self.obstacle_timer <= 0:
            # 随机障碍物间隔
            self.obstacle_timer = random.randint(60, 120)
            
            # 创建新障碍物
            new_obstacle = {
                "x": self.width,
                "y": self.height - 80,
                "width": 20,
                "height": 40
            }
            self.obstacles.append(new_obstacle)
        
        # 更新障碍物位置
        for obstacle in self.obstacles[:]:
            obstacle["x"] -= self.obstacle_speed
            
            # 移除已经通过的障碍物
            if obstacle["x"] < -50:
                self.obstacles.remove(obstacle)
            
            # 检测碰撞
            if self.check_collision(obstacle):
                self.end_game()
                return False
        
        return True
    
    def check_collision(self, obstacle):
        """检查是否与障碍物碰撞"""
        player_rect = pygame.Rect(self.player_x, self.player_y - 20, 50, 30)
        obstacle_rect = pygame.Rect(
            obstacle["x"], obstacle["y"], obstacle["width"], obstacle["height"]
        )
        
        return player_rect.colliderect(obstacle_rect)
    
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
                "障碍赛跑游戏",
                "按空格键跳跃，避开障碍物",
                "游戏时间: 45秒"
            ]
            
            for i, line in enumerate(instructions):
                text = self.font.render(line, True, self.colors["text"])
                self.screen.blit(text, (self.width//2 - text.get_width()//2, self.height//2 - 150 + i*40))
            
            return
        
        # 绘制地面
        pygame.draw.rect(self.screen, self.colors["ground"], (0, self.height - 50, self.width, 50))
        
        # 绘制玩家
        self.screen.blit(self.dog_img, (self.player_x, self.player_y - 20))
        
        # 绘制障碍物
        for obstacle in self.obstacles:
            pygame.draw.rect(
                self.screen, 
                self.colors["obstacle"],
                (obstacle["x"], obstacle["y"], obstacle["width"], obstacle["height"])
            )
        
        # 绘制分数和时间
        score_text = self.font.render(f"得分: {self.score}", True, self.colors["text"])
        self.screen.blit(score_text, (20, 20))
        
        time_text = self.font.render(f"时间: {int(self.time_left)}秒", True, self.colors["text"])
        self.screen.blit(time_text, (self.width - 150, 20))
    
    def handle_event(self, event):
        """处理游戏事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.active:
                # 检查是否点击了开始按钮
                button_rect = pygame.Rect(self.width//2 - 100, self.height//2 - 25, 200, 50)
                if button_rect.collidepoint(event.pos):
                    self.start_game()
        
        elif event.type == pygame.KEYDOWN and self.active:
            # 空格键跳跃
            if event.key == pygame.K_SPACE and not self.player_jump:
                self.player_jump = True
                self.player_jump_height = 12  # 跳跃初始速度
    
    def end_game(self):
        """结束游戏"""
        self.active = False
        
        # 根据得分增加狗狗的能力
        stamina_gain = min(10, self.score // 10)
        if stamina_gain > 0:
            # 增加耐力相关技能
            if "障碍跑" in self.dog.skills:
                current_level = self.dog.skills["障碍跑"]
                if current_level < 5:  # 最高5级
                    self.dog.skills["障碍跑"] = min(5, current_level + stamina_gain / 5)
            else:
                # 首次玩游戏，初始化技能
                if self.score >= 10:  # 至少需要10分才能获得技能
                    self.dog.skills["障碍跑"] = 1
        
        # 增加狗狗的快乐度和减少精力
        happiness_gain = min(20, self.score // 5)
        self.dog.happiness = min(100, self.dog.happiness + happiness_gain)
        
        # 消耗精力
        energy_cost = min(30, 10 + self.score // 5)
        self.dog.energy = max(0, self.dog.energy - energy_cost)
    
    def get_result(self):
        """获取游戏结果"""
        return {
            "score": self.score,
            "status": "completed" if self.time_left <= 0 else "aborted"
        }