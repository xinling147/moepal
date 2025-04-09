import pygame
import random
import time
import os
import json

class RaceGame:
    def __init__(self, screen, dog, ui):
        self.screen = screen
        self.dog = dog
        self.ui = ui
        self.width, self.height = screen.get_size()
        
        # 游戏状态
        self.active = False
        self.score = 0
        self.base_score = 100  # 基础分数
        self.distance = 0  # 跑步距离
        self.time_left = 60  # 游戏时间
        self.start_time = 0
        self.last_time_penalty = 0  # 上次扣分时间
        self.perfect_jumps = 0  # 完美跳跃次数
        self.obstacle_touches = 0  # 障碍物触碰次数
        
        # 多人对战模式
        self.multiplayer = False
        self.players = []  # 存储多个玩家的状态
        
        # 季节性特别关卡
        self.current_season = "spring"  # spring, summer, fall, winter
        self.seasonal_effects = {
            "spring": {"background": (200, 230, 255), "obstacle_bonus": 1.2},
            "summer": {"background": (255, 220, 180), "obstacle_bonus": 1.5},
            "fall": {"background": (230, 190, 170), "obstacle_bonus": 1.3},
            "winter": {"background": (240, 240, 255), "obstacle_bonus": 1.1}
        }
        
        # 难度设置
        self.difficulty = 1  # 1=初级, 2=中级, 3=高级
        self.difficulty_names = {1: "初级", 2: "中级", 3: "高级"}
        
        # 玩家设置
        self.player_y = self.height - 100
        self.player_x = 100
        self.player_speed = 0
        self.player_jump = False
        self.player_jump_height = 0
        self.gravity = 1
        self.player_state = "normal"  # normal, perfect, hit
        self.state_timer = 0
        
        # 障碍物
        self.obstacles = []
        self.obstacle_types = {
            "hurdle": {"width": 20, "height": 40, "y_offset": 0, "color": (100, 100, 100)},
            "pit": {"width": 60, "height": 20, "y_offset": 30, "color": (50, 50, 50)},
            "platform": {"width": 80, "height": 15, "y_offset": -30, "color": (150, 100, 50)},
            "bridge": {"width": 40, "height": 10, "y_offset": 0, "color": (120, 80, 40)}
        }
        self.available_obstacles = ["hurdle"]  # 初始只有矮栏
        self.obstacle_speed = 5
        self.obstacle_timer = 0
        
        # 成就系统
        self.achievements = {
            "speed_demon": {"name": "速度恶魔", "desc": "在一局游戏中得分超过150分", "unlocked": False},
            "perfect_jumper": {"name": "完美跳跃者", "desc": "在一局游戏中完成10次完美跳跃", "unlocked": False},
            "marathon": {"name": "马拉松选手", "desc": "累计游戏时间超过5分钟", "unlocked": False},
            "season_master": {"name": "季节大师", "desc": "在所有季节性关卡中获得100分以上", "unlocked": False},
            "multiplayer_champion": {"name": "多人竞技冠军", "desc": "在多人对战模式中获得第一名", "unlocked": False},
            "obstacle_expert": {"name": "障碍专家", "desc": "连续通过10个障碍物且不触碰", "unlocked": False}
        }
        
        # 游戏记录
        self.high_score = 0
        self.total_play_time = 0
        self.load_game_data()  # 加载游戏数据
        
        # 暂停菜单
        self.paused = False
        self.menu_options = ["继续游戏", "重新开始", "返回主菜单", "游戏设置", "查看规则"]
        self.selected_option = 0
        
        # 颜色
        self.colors = {
            "background": (200, 230, 255),
            "player": (150, 120, 90),
            "player_perfect": (220, 180, 100),  # 完美跳跃时的颜色
            "player_hit": (255, 100, 100),  # 碰撞时的颜色
            "obstacle": (100, 100, 100),
            "ground": (100, 180, 100),
            "text": (50, 50, 50),
            "button": (70, 130, 180),
            "button_hover": (100, 149, 237),
            "button_text": (255, 255, 255),
            "menu_bg": (0, 0, 0, 180),  # 半透明黑色
            "menu_selected": (255, 255, 0),
            "achievement": (255, 215, 0)
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
        
        # 创建完美跳跃时的狗狗图像
        self.dog_perfect_img = pygame.Surface((50, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(self.dog_perfect_img, self.colors["player_perfect"], (0, 0, 40, 20))
        pygame.draw.circle(self.dog_perfect_img, self.colors["player_perfect"], (40, 10), 10)
        pygame.draw.ellipse(self.dog_perfect_img, (220, 180, 100), (45, 5, 5, 5))
        pygame.draw.ellipse(self.dog_perfect_img, (0, 0, 0), (45, 10, 2, 2))
        
        # 创建碰撞时的狗狗图像
        self.dog_hit_img = pygame.Surface((50, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(self.dog_hit_img, self.colors["player_hit"], (0, 0, 40, 20))
        pygame.draw.circle(self.dog_hit_img, self.colors["player_hit"], (40, 10), 10)
        pygame.draw.ellipse(self.dog_hit_img, (255, 150, 150), (45, 5, 5, 5))
        pygame.draw.ellipse(self.dog_hit_img, (0, 0, 0), (45, 10, 2, 2))
        
        # 加载声音效果
        try:
            # pygame.mixer.init()
            # self.sounds = {
            #     "jump": pygame.mixer.Sound(os.path.join("assets", "sounds", "sfx", "jump.wav")),
            #     "perfect": pygame.mixer.Sound(os.path.join("assets", "sounds", "sfx", "perfect.wav")),
            #     "hit": pygame.mixer.Sound(os.path.join("assets", "sounds", "sfx", "hit.wav")),
            #     "achievement": pygame.mixer.Sound(os.path.join("assets", "sounds", "sfx", "achievement.wav"))
            # }
            self.sounds = {}
        except:
            # 如果声音加载失败，创建空的字典
            self.sounds = {}
            print("警告：无法加载声音文件")
    
    def load_game_data(self):
        """加载游戏数据"""
        try:
            data_path = os.path.join("data", "saves", "race_game.json")
            if os.path.exists(data_path):
                with open(data_path, "r") as f:
                    data = json.load(f)
                    self.high_score = data.get("high_score", 0)
                    self.total_play_time = data.get("total_play_time", 0)
                    self.achievements = data.get("achievements", self.achievements)
        except Exception as e:
            print(f"加载游戏数据失败: {e}")
    
    def save_game_data(self):
        """保存游戏数据"""
        try:
            data_path = os.path.join("data", "saves", "race_game.json")
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            
            data = {
                "high_score": self.high_score,
                "total_play_time": self.total_play_time,
                "achievements": self.achievements
            }
            
            with open(data_path, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"保存游戏数据失败: {e}")
    
    def start_game(self):
        """开始游戏"""
        self.active = True
        self.paused = False
        self.score = self.base_score
        self.distance = 0
        self.time_left = 60
        self.start_time = time.time()
        self.last_time_penalty = 0
        self.perfect_jumps = 0
        self.obstacle_touches = 0
        self.obstacles = []
        self.player_jump = False
        self.player_jump_height = 0
        self.player_y = self.height - 100
        self.player_state = "normal"
        self.state_timer = 0
        
        # 设置季节特效
        season_effect = self.seasonal_effects[self.current_season]
        self.colors["background"] = season_effect["background"]
        self.obstacle_bonus = season_effect["obstacle_bonus"]
        
        # 多人对战模式初始化
        if self.multiplayer:
            self.players = [{
                "x": self.player_x + i * 100,
                "y": self.height - 100,
                "jump": False,
                "jump_height": 0,
                "state": "normal",
                "score": self.base_score,
                "perfect_jumps": 0,
                "obstacle_touches": 0
            } for i in range(2)]  # 支持2人对战
        
        # 根据难度设置游戏参数
        if self.difficulty == 1:  # 初级
            self.obstacle_speed = 5
            self.available_obstacles = ["hurdle", "pit"]
            self.obstacle_timer_range = (80, 150)  # 障碍物生成间隔范围
            self.time_penalty_interval = 15  # 时间惩罚间隔(秒)
        elif self.difficulty == 2:  # 中级
            self.obstacle_speed = 7
            self.available_obstacles = ["hurdle", "pit", "platform"]
            self.obstacle_timer_range = (60, 120)
            self.time_penalty_interval = 10
        else:  # 高级
            self.obstacle_speed = 9
            self.available_obstacles = ["hurdle", "pit", "platform", "bridge"]
            self.obstacle_timer_range = (40, 90)
            self.time_penalty_interval = 5
            
        # 根据季节调整难度
        season_bonus = self.seasonal_effects[self.current_season]["obstacle_bonus"]
        self.obstacle_speed = int(self.obstacle_speed * season_bonus)
    
    def update(self):
        """更新游戏状态"""
        if not self.active or self.paused:
            return True
        
        # 更新时间
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        self.time_left = max(0, 60 - elapsed_time)
        
        # 根据难度设置的时间惩罚间隔扣分
        if int(elapsed_time) // self.time_penalty_interval > self.last_time_penalty:
            self.last_time_penalty = int(elapsed_time) // self.time_penalty_interval
            self.score = max(0, self.score - 1)
        
        # 游戏时间结束
        if self.time_left <= 0:
            self.end_game()
            return False
        
        # 更新玩家状态计时器
        if self.player_state != "normal":
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.player_state = "normal"
        
        # 更新玩家跳跃
        if self.player_jump:
            self.player_jump_height -= self.gravity
            self.player_y -= self.player_jump_height
            
            # 检查是否着地
            if self.player_y >= self.height - 100:
                self.player_y = self.height - 100
                self.player_jump = False
        
        # 增加距离
        self.distance += self.obstacle_speed / 10
        
        # 生成障碍物
        self.obstacle_timer -= 1
        if self.obstacle_timer <= 0:
            # 随机障碍物间隔
            self.obstacle_timer = random.randint(60, 120)
            
            # 随机选择障碍物类型
            obstacle_type = random.choice(self.available_obstacles)
            obstacle_info = self.obstacle_types[obstacle_type]
            
            # 创建新障碍物
            new_obstacle = {
                "x": self.width,
                "y": self.height - 80 + obstacle_info["y_offset"],
                "width": obstacle_info["width"],
                "height": obstacle_info["height"],
                "type": obstacle_type,
                "color": obstacle_info["color"],
                "passed": False  # 标记是否已经通过
            }
            self.obstacles.append(new_obstacle)
        
        # 更新障碍物位置
        for obstacle in self.obstacles[:]:
            obstacle["x"] -= self.obstacle_speed
            
            # 检查是否完美通过障碍物
            if not obstacle["passed"] and obstacle["x"] < self.player_x - 50:
                obstacle["passed"] = True
                self.score += 5  # 完美跨越加5分
                self.perfect_jumps += 1
                self.player_state = "perfect"
                self.state_timer = 15  # 显示完美状态15帧
                
                # 播放完美跳跃音效
                if "perfect" in self.sounds:
                    self.sounds["perfect"].play()
            
            # 移除已经通过的障碍物
            if obstacle["x"] < -100:
                self.obstacles.remove(obstacle)
                continue
            
            # 检测碰撞
            if self.check_collision(obstacle):
                # 碰撞扣分
                self.score = max(0, self.score - 3)  # 触碰障碍扣3分
                self.obstacle_touches += 1
                self.player_state = "hit"
                self.state_timer = 15  # 显示受伤状态15帧
                
                # 播放碰撞音效
                if "hit" in self.sounds:
                    self.sounds["hit"].play()
        
        # 检查成就并显示解锁提示
        unlocked_achievements = self.check_achievements()
        if unlocked_achievements:
            for ach in unlocked_achievements:
                # 显示成就解锁动画
                self.ui.display_message(f"成就解锁: {ach['name']} - {ach['desc']}", duration=3000)
                # 播放成就解锁音效
                if "achievement" in self.sounds:
                    self.sounds["achievement"].play()
        
        return True
        
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
            # 绘制难度选择和开始游戏按钮
            self.render_start_menu()
            return
            
        # 绘制季节信息
        season_text = self.font.render(f"季节: {self.current_season}", True, self.colors["text"])
        self.screen.blit(season_text, (20, 80))
        
        # 多人对战模式下绘制所有玩家
        if self.multiplayer:
            for i, player in enumerate(self.players):
                # 绘制玩家
                player_color = (150, 120 + i * 30, 90)
                player_surface = pygame.Surface((50, 30), pygame.SRCALPHA)
                pygame.draw.ellipse(player_surface, player_color, (0, 0, 40, 20))
                pygame.draw.circle(player_surface, player_color, (40, 10), 10)
                self.screen.blit(player_surface, (player["x"], player["y"] - 20))
                
                # 绘制玩家分数
                score_text = self.font.render(f"玩家{i+1}: {player['score']}", True, self.colors["text"])
                self.screen.blit(score_text, (self.width - 200, 20 + i * 30))
        
        # 绘制地面
        pygame.draw.rect(self.screen, self.colors["ground"], (0, self.height - 50, self.width, 50))
        
        # 绘制玩家
        if self.player_state == "perfect":
            self.screen.blit(self.dog_perfect_img, (self.player_x, self.player_y - 20))
        elif self.player_state == "hit":
            self.screen.blit(self.dog_hit_img, (self.player_x, self.player_y - 20))
        else:
            self.screen.blit(self.dog_img, (self.player_x, self.player_y - 20))
        
        # 绘制障碍物
        for obstacle in self.obstacles:
            pygame.draw.rect(
                self.screen, 
                obstacle.get("color", self.colors["obstacle"]),
                (obstacle["x"], obstacle["y"], obstacle["width"], obstacle["height"])
            )
        
        # 绘制游戏信息
        self.render_game_info()
        
        # 如果游戏暂停，绘制暂停菜单
        if self.paused:
            self.render_pause_menu()
    
    def render_start_menu(self):
        """渲染开始菜单"""
        # 绘制游戏标题
        title = self.font_large.render("障碍赛跑游戏", True, self.colors["text"])
        self.screen.blit(title, (self.width//2 - title.get_width()//2, self.height//4))
        
        # 绘制难度选择
        difficulty_text = self.font.render(f"难度: {self.difficulty_names[self.difficulty]}", True, self.colors["text"])
        self.screen.blit(difficulty_text, (self.width//2 - difficulty_text.get_width()//2, self.height//2 - 80))
        
        # 难度调整按钮
        left_rect = pygame.Rect(self.width//2 - 120, self.height//2 - 80, 30, 30)
        right_rect = pygame.Rect(self.width//2 + 90, self.height//2 - 80, 30, 30)
        
        pygame.draw.rect(self.screen, self.colors["button"], left_rect)
        pygame.draw.rect(self.screen, self.colors["button"], right_rect)
        
        left_text = self.font.render("<", True, self.colors["button_text"])
        right_text = self.font.render(">", True, self.colors["button_text"])
        
        self.screen.blit(left_text, (left_rect.centerx - left_text.get_width()//2, left_rect.centery - left_text.get_height()//2))
        self.screen.blit(right_text, (right_rect.centerx - right_text.get_width()//2, right_rect.centery - right_text.get_height()//2))
        
        # 绘制开始游戏按钮
        button_rect = pygame.Rect(self.width//2 - 100, self.height//2, 200, 50)
        mouse_pos = pygame.mouse.get_pos()
        button_color = self.colors["button_hover"] if button_rect.collidepoint(mouse_pos) else self.colors["button"]
        
        pygame.draw.rect(self.screen, button_color, button_rect)
        pygame.draw.rect(self.screen, (50, 50, 50), button_rect, 2)  # 边框
        
        text = self.font_large.render("开始游戏", True, self.colors["button_text"])
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)
        
        # 绘制游戏说明
        instructions = [
            "按空格键跳跃，避开障碍物",
            "游戏时间: 60秒",
            f"最高分: {self.high_score}"
        ]
        
        for i, line in enumerate(instructions):
            text = self.font.render(line, True, self.colors["text"])
            self.screen.blit(text, (self.width//2 - text.get_width()//2, self.height//2 + 80 + i*30))
        
        # 绘制成就信息
        unlocked_count = sum(1 for ach in self.achievements.values() if ach["unlocked"])
        ach_text = self.font.render(f"已解锁成就: {unlocked_count}/{len(self.achievements)}", True, self.colors["achievement"])
        self.screen.blit(ach_text, (self.width//2 - ach_text.get_width()//2, self.height//2 + 180))
    
    def render_game_info(self):
        """渲染游戏信息"""
        # 绘制分数和时间
        score_text = self.font.render(f"得分: {self.score}", True, self.colors["text"])
        self.screen.blit(score_text, (20, 20))
        
        time_text = self.font.render(f"时间: {int(self.time_left)}秒", True, self.colors["text"])
        self.screen.blit(time_text, (self.width - 150, 20))
        
        # 绘制难度
        diff_text = self.font.render(f"难度: {self.difficulty_names[self.difficulty]}", True, self.colors["text"])
        self.screen.blit(diff_text, (20, 50))
        
        # 绘制完美跳跃和触碰次数
        perfect_text = self.font.render(f"完美跳跃: {self.perfect_jumps}", True, self.colors["player_perfect"])
        self.screen.blit(perfect_text, (self.width - 150, 50))
    
    def handle_event(self, event):
        """处理游戏事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.active:
                # 检查是否点击了开始按钮
                button_rect = pygame.Rect(self.width//2 - 100, self.height//2 - 25, 200, 50)
                if button_rect.collidepoint(event.pos):
                    self.start_game()
                # 检查是否点击了多人模式按钮
                multi_button_rect = pygame.Rect(self.width//2 - 100, self.height//2 + 60, 200, 50)
                if multi_button_rect.collidepoint(event.pos):
                    self.multiplayer = not self.multiplayer
                # 检查是否点击了季节切换按钮
                season_button_rect = pygame.Rect(self.width//2 - 100, self.height//2 + 120, 200, 50)
                if season_button_rect.collidepoint(event.pos):
                    seasons = list(self.seasonal_effects.keys())
                    current_index = seasons.index(self.current_season)
                    self.current_season = seasons[(current_index + 1) % len(seasons)]
        
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


    def check_achievements(self):
        """检查并更新成就"""
        # 检查速度恶魔成就
        if self.score > 150 and not self.achievements["speed_demon"]["unlocked"]:
            self.achievements["speed_demon"]["unlocked"] = True
            self.ui.display_message(f"解锁成就：{self.achievements['speed_demon']['name']}")
        
        # 检查完美跳跃者成就
        if self.perfect_jumps >= 10 and not self.achievements["perfect_jumper"]["unlocked"]:
            self.achievements["perfect_jumper"]["unlocked"] = True
            self.ui.display_message(f"解锁成就：{self.achievements['perfect_jumper']['name']}")
        
        # 检查马拉松选手成就
        total_time = self.total_play_time + (time.time() - self.start_time)
        if total_time >= 300 and not self.achievements["marathon"]["unlocked"]:
            self.achievements["marathon"]["unlocked"] = True
            self.ui.display_message(f"解锁成就：{self.achievements['marathon']['name']}")
        
        # 检查障碍专家成就
        if len([o for o in self.obstacles if o["passed"]]) >= 10 and self.obstacle_touches == 0:
            if not self.achievements["obstacle_expert"]["unlocked"]:
                self.achievements["obstacle_expert"]["unlocked"] = True
                self.ui.display_message(f"解锁成就：{self.achievements['obstacle_expert']['name']}")