import pygame
import random
import time

class MazeGame:
    def __init__(self, screen, dog):
        self.screen = screen
        self.dog = dog
        self.width, self.height = screen.get_size()
        
        # 游戏状态
        self.active = False
        self.score = 0
        self.time_left = 60  # 60秒游戏时间
        self.start_time = 0
        
        # 迷宫设置
        self.cell_size = 40
        self.maze_width = 15
        self.maze_height = 10
        self.maze = []
        
        # 玩家和目标位置
        self.player_pos = [0, 0]
        self.target_pos = [0, 0]
        self.treats_pos = []  # 额外奖励的位置
        
        # 移动控制
        self.move_cooldown = 0
        
        # 颜色
        self.colors = {
            "background": (240, 240, 240),
            "wall": (100, 100, 100),
            "player": (255, 100, 100),
            "target": (100, 255, 100),
            "treat": (255, 200, 0),
            "text": (50, 50, 50),
            "button": (70, 130, 180),
            "button_hover": (100, 149, 237),
            "button_text": (255, 255, 255)
        }
        
        # 字体
        self.font = pygame.font.SysFont("Arial", 24)
        self.font_large = pygame.font.SysFont("Arial", 36)
    
    def generate_maze(self):
        """生成随机迷宫"""
        # 初始化迷宫（1表示墙，0表示通道）
        self.maze = [[1 for _ in range(self.maze_width)] for _ in range(self.maze_height)]
        
        # 使用深度优先搜索生成迷宫
        def carve_passages(x, y):
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                nx, ny = x + dx*2, y + dy*2
                if (0 <= nx < self.maze_width and 0 <= ny < self.maze_height and 
                    self.maze[ny][nx] == 1):
                    self.maze[y + dy][x + dx] = 0
                    self.maze[ny][nx] = 0
                    carve_passages(nx, ny)
        
        # 从随机位置开始生成
        start_x = random.randrange(0, self.maze_width, 2)
        start_y = random.randrange(0, self.maze_height, 2)
        if start_x == self.maze_width - 1:
            start_x -= 1
        if start_y == self.maze_height - 1:
            start_y -= 1
        
        self.maze[start_y][start_x] = 0
        carve_passages(start_x, start_y)
        
        # 确保入口和出口是通道
        self.maze[0][0] = 0
        self.maze[self.maze_height-1][self.maze_width-1] = 0
        
        # 设置玩家和目标位置
        self.player_pos = [0, 0]
        self.target_pos = [self.maze_width-1, self.maze_height-1]
        
        # 添加一些额外的奖励
        self.treats_pos = []
        for _ in range(5):  # 添加5个奖励
            while True:
                x = random.randint(0, self.maze_width-1)
                y = random.randint(0, self.maze_height-1)
                if self.maze[y][x] == 0 and [x, y] != self.player_pos and [x, y] != self.target_pos and [x, y] not in self.treats_pos:
                    self.treats_pos.append([x, y])
                    break
    
    def start_game(self):
        """开始游戏"""
        self.active = True
        self.score = 0
        self.time_left = 60
        self.start_time = time.time()
        self.generate_maze()
    
    def update(self):
        """更新游戏状态"""
        if not self.active:
            return
        
        # 更新时间
        current_time = time.time()
        self.time_left = max(0, 60 - (current_time - self.start_time))
        
        # 游戏时间结束
        if self.time_left <= 0:
            self.end_game()
            return
        
        # 更新移动冷却时间
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
        
        # 检查是否到达目标
        if self.player_pos == self.target_pos:
            self.score += 10
            self.generate_maze()  # 生成新迷宫
        
        # 检查是否获得奖励
        for treat_pos in self.treats_pos.copy():
            if self.player_pos == treat_pos:
                self.score += 2
                self.treats_pos.remove(treat_pos)
    
    def move_player(self, dx, dy):
        """移动玩家"""
        if self.move_cooldown > 0:
            return
        
        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy
        
        # 检查是否可以移动（在迷宫范围内且不是墙）
        if (0 <= new_x < self.maze_width and 0 <= new_y < self.maze_height and 
            self.maze[new_y][new_x] == 0):
            self.player_pos = [new_x, new_y]
            self.move_cooldown = 5  # 设置移动冷却时间
    
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
                "迷宫游戏",
                "使用方向键移动你的狗狗",
                "收集骨头并找到出口",
                "游戏时间: 60秒"
            ]
            
            for i, line in enumerate(instructions):
                text = self.font.render(line, True, self.colors["text"])
                self.screen.blit(text, (self.width//2 - text.get_width()//2, self.height//2 - 150 + i*40))
            
            return
        
        # 计算迷宫在屏幕上的位置（居中）
        maze_screen_width = self.maze_width * self.cell_size
        maze_screen_height = self.maze_height * self.cell_size
        maze_x = (self.width - maze_screen_width) // 2
        maze_y = (self.height - maze_screen_height) // 2
        
        # 绘制迷宫
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                cell_x = maze_x + x * self.cell_size
                cell_y = maze_y + y * self.cell_size
                
                if self.maze[y][x] == 1:  # 墙
                    pygame.draw.rect(self.screen, self.colors["wall"], 
                                   (cell_x, cell_y, self.cell_size, self.cell_size))
        
        # 绘制奖励
        for x, y in self.treats_pos:
            treat_x = maze_x + x * self.cell_size + self.cell_size // 2
            treat_y = maze_y + y * self.cell_size + self.cell_size // 2
            pygame.draw.circle(self.screen, self.colors["treat"], 
                              (treat_x, treat_y), self.cell_size // 3)
        
        # 绘制目标
        target_x = maze_x + self.target_pos[0] * self.cell_size + self.cell_size // 2
        target_y = maze_y + self.target_pos[1] * self.cell_size + self.cell_size // 2
        pygame.draw.rect(self.screen, self.colors["target"], 
                       (target_x - self.cell_size//3, target_y - self.cell_size//3, 
                        self.cell_size*2//3, self.cell_size*2//3))
        
        # 绘制玩家
        player_x = maze_x + self.player_pos[0] * self.cell_size + self.cell_size // 2
        player_y = maze_y + self.player_pos[1] * self.cell_size + self.cell_size // 2
        pygame.draw.circle(self.screen, self.colors["player"], 
                          (player_x, player_y), self.cell_size // 3)
        
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
            # 方向键控制
            if event.key == pygame.K_UP:
                self.move_player(0, -1)
            elif event.key == pygame.K_DOWN:
                self.move_player(0, 1)
            elif event.key == pygame.K_LEFT:
                self.move_player(-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.move_player(1, 0)
    
    def end_game(self):
        """结束游戏"""
        self.active = False
        
        # 根据得分增加狗狗的能力
        intelligence_gain = min(10, self.score // 5)
        if intelligence_gain > 0:
            # 增加智力游戏相关技能
            if "智力游戏" in self.dog.skills:
                current_level = self.dog.skills["智力游戏"]
                if current_level < 5:  # 最高5级
                    new_level = min(5, current_level + intelligence_gain // 3)
                    if new_level > current_level:
                        self.dog.skills["智力游戏"] = new_level
            else:
                # 首次玩游戏，初始化技能
                if self.score >= 10:  # 至少需要10分才能获得技能
                    self.dog.skills["智力游戏"] = 1
        
        # 增加狗狗的快乐度和亲密度
        happiness_gain = min(20, self.score)
        self.dog.happiness = min(100, self.dog.happiness + happiness_gain)
        
        affection_gain = min(10, self.score // 2)
        self.dog.affection = min(100, self.dog.affection + affection_gain)
        
        # 消耗精力
        energy_cost = min(30, 15 + self.score)
        self.dog.energy = max(0, self.dog.energy - energy_cost)