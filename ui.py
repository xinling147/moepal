import pygame
import os
import math

class UI:
    def __init__(self, screen, dog):
        self.screen = screen
        self.dog = dog
        self.width, self.height = screen.get_size()
        
        # 颜色定义
        self.colors = {
            "background": (240, 248, 255),  # 淡蓝色背景
            "text": (50, 50, 50),         # 深灰色文字
            "button": (70, 130, 180),     # 钢蓝色按钮
            "button_hover": (100, 149, 237),  # 矢车菊蓝色按钮悬停
            "button_text": (255, 255, 255),  # 白色按钮文字
            "status_bar_bg": (200, 200, 200),  # 状态栏背景
            "hunger_bar": (255, 165, 0),      # 橙色饥饿度
            "happiness_bar": (255, 215, 0),    # 金色快乐度
            "health_bar": (50, 205, 50),       # 绿色健康度
            "cleanliness_bar": (135, 206, 250),  # 淡蓝色清洁度
            "energy_bar": (147, 112, 219)       # 紫色精力值
        }
        
        # 加载字体
        pygame.font.init()
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.font_medium = pygame.font.SysFont("Arial", 20)
        self.font_large = pygame.font.SysFont("Arial", 24)
        
        # 加载图像资源
        self.load_images()
        
        # 创建按钮
        self.create_buttons()
        
        # 当前选中的菜单
        self.current_menu = "main"  # main, food, play, train
        
        # 消息显示
        self.message = ""
        self.message_time = 0
        
        # 动画状态
        self.animation_frame = 0
        self.animation_time = 0
        self.current_animation = "idle"  # idle, eat, play, sleep, bath
    
    def load_images(self):
        """加载图像资源，如果不存在则创建占位图像"""
        self.images = {}
        
        # 创建占位图像
        def create_placeholder(name, color, size):
            surf = pygame.Surface(size)
            surf.fill(color)
            # 绘制像素风格的轮廓
            pygame.draw.rect(surf, (255, 255, 255), (0, 0, size[0], size[1]), 2)
            pygame.draw.rect(surf, (0, 0, 0), (2, 2, size[0]-4, size[1]-4), 1)
            # 添加文字标识
            font = pygame.font.SysFont("Arial", 14)
            text = font.render(name, True, (0, 0, 0))
            text_rect = text.get_rect(center=(size[0]//2, size[1]//2))
            surf.blit(text, text_rect)
            return surf
        
        # 加载SVG图像的函数
        def load_svg_image(file_path, size):
            try:
                import io
                import cairosvg
                # 将SVG转换为PNG格式的内存流
                png_data = cairosvg.svg2png(url=file_path, output_width=size[0], output_height=size[1])
                # 从内存流创建Surface
                return pygame.image.load(io.BytesIO(png_data))
            except (ImportError, FileNotFoundError):
                print(f"无法加载SVG图像: {file_path}，使用占位图像代替")
                return create_placeholder(os.path.basename(file_path), (200, 200, 200), size)
        
        # 宠物图像 - 柯基犬像素风格
        dog_size = (150, 150)
        base_path = os.path.join(os.path.dirname(__file__), "assets/images/pixel_dogs")
        
        # 尝试加载柯基犬图像，如果失败则使用占位图像
        try:
            self.images["dog_idle"] = load_svg_image(os.path.join(base_path, "corgi_idle.svg"), dog_size)
            self.images["dog_eat"] = load_svg_image(os.path.join(base_path, "corgi_eat.svg"), dog_size)
            self.images["dog_play"] = load_svg_image(os.path.join(base_path, "corgi_play.svg"), dog_size)
            self.images["dog_sleep"] = load_svg_image(os.path.join(base_path, "corgi_sleep.svg"), dog_size)
            self.images["dog_bath"] = load_svg_image(os.path.join(base_path, "corgi_bath.svg"), dog_size)
        except Exception as e:
            print(f"加载柯基犬图像失败: {e}，使用占位图像代替")
            self.images["dog_idle"] = create_placeholder("Dog Idle", (200, 200, 200), dog_size)
            self.images["dog_eat"] = create_placeholder("Dog Eating", (220, 180, 150), dog_size)
            self.images["dog_play"] = create_placeholder("Dog Playing", (150, 220, 150), dog_size)
            self.images["dog_sleep"] = create_placeholder("Dog Sleeping", (150, 150, 220), dog_size)
            self.images["dog_bath"] = create_placeholder("Dog Bathing", (150, 200, 220), dog_size)
        
        # 背景图像
        self.images["background"] = create_placeholder("Background", self.colors["background"], (self.width, self.height))
        
        # 物品图像
        item_size = (40, 40)
        self.images["food_normal"] = create_placeholder("Dog Food", (210, 180, 140), item_size)
        self.images["food_premium"] = create_placeholder("Premium Food", (230, 190, 150), item_size)
        self.images["food_treat"] = create_placeholder("Treat", (240, 200, 160), item_size)
        self.images["food_chicken"] = create_placeholder("Chicken", (250, 220, 190), item_size)
        self.images["food_beef"] = create_placeholder("Beef", (200, 150, 130), item_size)
        
        self.images["toy_ball"] = create_placeholder("Ball", (255, 0, 0), item_size)
        self.images["toy_frisbee"] = create_placeholder("Frisbee", (0, 255, 0), item_size)
        self.images["toy_rope"] = create_placeholder("Rope", (0, 0, 255), item_size)
        self.images["toy_puzzle"] = create_placeholder("Puzzle", (255, 255, 0), item_size)
    
    def create_buttons(self):
        """创建界面按钮"""
        self.buttons = {
            "main": [
                {"rect": pygame.Rect(50, 400, 100, 40), "text": "喂食", "action": "food_menu"},
                {"rect": pygame.Rect(170, 400, 100, 40), "text": "玩耍", "action": "play_menu"},
                {"rect": pygame.Rect(290, 400, 100, 40), "text": "洗澡", "action": "bath"},
                {"rect": pygame.Rect(410, 400, 100, 40), "text": "睡觉", "action": "sleep"},
                {"rect": pygame.Rect(530, 400, 100, 40), "text": "训练", "action": "train_menu"},
                {"rect": pygame.Rect(650, 400, 100, 40), "text": "抚摸", "action": "pet"}
            ],
            "food": [
                {"rect": pygame.Rect(50, 460, 120, 40), "text": "普通狗粮", "action": "feed_normal"},
                {"rect": pygame.Rect(190, 460, 120, 40), "text": "高级狗粮", "action": "feed_premium"},
                {"rect": pygame.Rect(330, 460, 120, 40), "text": "狗狗零食", "action": "feed_treat"},
                {"rect": pygame.Rect(470, 460, 120, 40), "text": "鸡肉", "action": "feed_chicken"},
                {"rect": pygame.Rect(610, 460, 120, 40), "text": "牛肉", "action": "feed_beef"},
                {"rect": pygame.Rect(650, 520, 100, 40), "text": "返回", "action": "main_menu"}
            ],
            "play": [
                {"rect": pygame.Rect(50, 460, 120, 40), "text": "普通玩耍", "action": "play_normal"},
                {"rect": pygame.Rect(190, 460, 120, 40), "text": "接飞盘", "action": "play_frisbee"},
                {"rect": pygame.Rect(330, 460, 120, 40), "text": "追球", "action": "play_ball"},
                {"rect": pygame.Rect(470, 460, 120, 40), "text": "拔河", "action": "play_rope"},
                {"rect": pygame.Rect(610, 460, 120, 40), "text": "智力游戏", "action": "play_puzzle"},
                {"rect": pygame.Rect(650, 520, 100, 40), "text": "返回", "action": "main_menu"}
            ],
            "train": [
                {"rect": pygame.Rect(50, 460, 120, 40), "text": "坐下", "action": "train_sit"},
                {"rect": pygame.Rect(190, 460, 120, 40), "text": "握手", "action": "train_handshake"},
                {"rect": pygame.Rect(330, 460, 120, 40), "text": "打滚", "action": "train_roll"},
                {"rect": pygame.Rect(470, 460, 120, 40), "text": "接飞盘", "action": "train_frisbee"},
                {"rect": pygame.Rect(610, 460, 120, 40), "text": "捡球", "action": "train_fetch"},
                {"rect": pygame.Rect(50, 520, 120, 40), "text": "原地等待", "action": "train_stay"},
                {"rect": pygame.Rect(650, 520, 100, 40), "text": "返回", "action": "main_menu"}
            ]
        }
    
    def handle_event(self, event):
        """处理用户事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 检查按钮点击
            mouse_pos = pygame.mouse.get_pos()
            self.check_button_click(mouse_pos)
        
        elif event.type == pygame.MOUSEMOTION:
            # 鼠标移动时检查是否在宠物上，实现抚摸交互
            mouse_pos = pygame.mouse.get_pos()
            dog_rect = self.images["dog_idle"].get_rect(center=(self.width//2, 250))
            if dog_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                # 如果在宠物上按住鼠标，触发抚摸动作
                self.perform_action("pet")
    
    def check_button_click(self, pos):
        """检查按钮点击"""
        # 检查当前菜单的按钮
        for button in self.buttons.get(self.current_menu, []):
            if button["rect"].collidepoint(pos):
                self.perform_action(button["action"])
                break
    
    def perform_action(self, action):
        """执行按钮动作"""
        # 菜单切换
        if action == "main_menu":
            self.current_menu = "main"
            return
        elif action == "food_menu":
            self.current_menu = "food"
            return
        elif action == "play_menu":
            self.current_menu = "play"
            return
        elif action == "train_menu":
            self.current_menu = "train"
            return
        
        # 喂食动作
        if action.startswith("feed_"):
            food_map = {
                "feed_normal": "普通狗粮",
                "feed_premium": "高级狗粮",
                "feed_treat": "狗狗零食",
                "feed_chicken": "鸡肉",
                "feed_beef": "牛肉"
            }
            food_type = food_map.get(action)
            if food_type:
                self.message = self.dog.feed(food_type)
                self.message_time = pygame.time.get_ticks()
                self.current_animation = "eat"
                self.animation_frame = 0
                self.animation_time = pygame.time.get_ticks()
        
        # 玩耍动作
        elif action.startswith("play_"):
            game_map = {
                "play_normal": "普通玩耍",
                "play_frisbee": "接飞盘",
                "play_ball": "追球",
                "play_rope": "拔河",
                "play_puzzle": "智力游戏"
            }
            game_type = game_map.get(action)
            if game_type:
                self.message = self.dog.play(game_type)
                self.message_time = pygame.time.get_ticks()
                self.current_animation = "play"
                self.animation_frame = 0
                self.animation_time = pygame.time.get_ticks()
        
        # 训练动作
        elif action.startswith("train_"):
            skill_map = {
                "train_sit": "坐下",
                "train_handshake": "握手",
                "train_roll": "打滚",
                "train_frisbee": "接飞盘",
                "train_fetch": "捡球",
                "train_stay": "原地等待"
            }
            skill_name = skill_map.get(action)
            if skill_name:
                self.message = self.dog.train(skill_name)
                self.message_time = pygame.time.get_ticks()
        
        # 其他动作
        elif action == "bath":
            self.message = self.dog.bath()
            self.message_time = pygame.time.get_ticks()
            self.current_animation = "bath"
            self.animation_frame = 0
            self.animation_time = pygame.time.get_ticks()
        
        elif action == "sleep":
            self.message = self.dog.sleep()
            self.message_time = pygame.time.get_ticks()
            self.current_animation = "sleep"
            self.animation_frame = 0
            self.animation_time = pygame.time.get_ticks()
        
        elif action == "pet":
            self.message = self.dog.pet()
            self.message_time = pygame.time.get_ticks()
    
    def update_animation(self):
        """更新动画状态"""
        current_time = pygame.time.get_ticks()
        
        # 每200毫秒更新一帧
        if current_time - self.animation_time > 200:
            self.animation_frame += 1
            self.animation_time = current_time
            
            # 动画持续时间（帧数）
            animation_duration = {
                "eat": 5,
                "play": 8,
                "sleep": 10,
                "bath": 6
            }
            
            # 检查动画是否结束
            if self.current_animation in animation_duration and self.animation_frame >= animation_duration[self.current_animation]:
                self.current_animation = "idle"
                self.animation_frame = 0
        
        # 消息显示时间（3秒）
        if self.message and current_time - self.message_time > 3000:
            self.message = ""
    
    def render(self):
        """渲染界面"""
        # 绘制背景
        self.screen.blit(self.images["background"], (0, 0))
        
        # 更新动画
        self.update_animation()
        
        # 绘制宠物
        dog_image_key = f"dog_{self.current_animation}"
        if dog_image_key in self.images:
            dog_image = self.images[dog_image_key]
        else:
            dog_image = self.images["dog_idle"]
        
        # 添加简单的动画效果
        dog_y_offset = math.sin(pygame.time.get_ticks() * 0.005) * 5  # 轻微上下浮动
        self.screen.blit(dog_image, dog_image.get_rect(center=(self.width//2, 250 + dog_y_offset)))
        
        # 绘制状态栏
        self.render_status_bars()
        
        # 绘制宠物信息
        self.render_dog_info()
        
        # 绘制按钮
        self.render_buttons()
        
        # 绘制消息
        if self.message:
            message_surf = self.font_medium.render(self.message, True, self.colors["text"])
            message_rect = message_surf.get_rect(center=(self.width//2, 150))
            # 绘制消息背景
            pygame.draw.rect(self.screen, (255, 255, 255, 200), 
                            (message_rect.left - 10, message_rect.top - 5, 
                             message_rect.width + 20, message_rect.height + 10))
            pygame.draw.rect(self.screen, (100, 100, 100), 
                            (message_rect.left - 10, message_rect.top - 5, 
                             message_rect.width + 20, message_rect.height + 10), 2)
            self.screen.blit(message_surf, message_rect)
    
    def render_status_bars(self):
        """渲染状态栏"""
        # 状态栏位置和尺寸
        bar_width = 150
        bar_height = 15
        bar_spacing = 25
        start_x = 50
        start_y = 50
        
        # 状态属性和对应颜色
        status_bars = [
            {"name": "饥饿度", "value": self.dog.hunger, "color": self.colors["hunger_bar"]},
            {"name": "快乐度", "value": self.dog.happiness, "color": self.colors["happiness_bar"]},
            {"name": "健康度", "value": self.dog.health, "color": self.colors["health_bar"]},
            {"name": "清洁度", "value": self.dog.cleanliness, "color": self.colors["cleanliness_bar"]},
            {"name": "精力值", "value": self.dog.energy, "color": self.colors["energy_bar"]}
        ]
        
        for i, bar in enumerate(status_bars):
            # 绘制状态名称
            name_surf = self.font_small.render(bar["name"], True, self.colors["text"])
            self.screen.blit(name_surf, (start_x, start_y + i * bar_spacing))
            
            # 绘制状态栏背景
            bar_bg_rect = pygame.Rect(start_x + 60, start_y + i * bar_spacing, bar_width, bar_height)
            pygame.draw.rect(self.screen, self.colors["status_bar_bg"], bar_bg_rect)
            
            # 绘制状态栏
            bar_fill_width = (bar["value"] / 100) * bar_width
            bar_fill_rect = pygame.Rect(start_x + 60, start_y + i * bar_spacing, bar_fill_width, bar_height)
            pygame.draw.rect(self.screen, bar["color"], bar_fill_rect)
            
            # 绘制状态值
            value_surf = self.font_small.render(f"{int(bar['value'])}", True, self.colors["text"])
            self.screen.blit(value_surf, (start_x + 60 + bar_width + 10, start_y + i * bar_spacing))
    
    def render_dog_info(self):
        """渲染宠物信息"""
        # 宠物基本信息
        info_x = 550
        info_y = 50
        info_spacing = 25
        
        info_items = [
            {"name": "名称", "value": self.dog.name},
            {"name": "品种", "value": self.dog.breed},
            {"name": "性格", "value": self.dog.personality},
            {"name": "年龄", "value": f"{int(self.dog.age)}天"},
            {"name": "阶段", "value": self.dog.GROWTH_STAGES[self.dog.growth_stage]},
            {"name": "亲密度", "value": f"{int(self.dog.affection)}/100"}
        ]
        
        for i, item in enumerate(info_items):
            # 绘制信息名称
            name_surf = self.font_small.render(f"{item['name']}:", True, self.colors["text"])
            self.screen.blit(name_surf, (info_x, info_y + i * info_spacing))
            
            # 绘制信息值
            value_surf = self.font_small.render(item["value"], True, self.colors["text"])
            self.screen.blit(value_surf, (info_x + 70, info_y + i * info_spacing))
        
        # 绘制技能信息
        if self.dog.skills:
            skill_title = self.font_medium.render("已学技能:", True, self.colors["text"])
            self.screen.blit(skill_title, (info_x, info_y + len(info_items) * info_spacing + 10))
            
            for i, (skill_name, skill_level) in enumerate(self.dog.skills.items()):
                skill_text = f"{skill_name} Lv.{skill_level}"
                skill_surf = self.font_small.render(skill_text, True, self.colors["text"])
                self.screen.blit(skill_surf, (info_x + 20, info_y + (len(info_items) + 1) * info_spacing + i * 20))
    
    def render_buttons(self):
        """渲染按钮"""
        mouse_pos = pygame.mouse.get_pos()
        
        # 绘制当前菜单的按钮
        for button in self.buttons.get(self.current_menu, []):
            # 检查鼠标是否悬停在按钮上
            button_color = self.colors["button_hover"] if button["rect"].collidepoint(mouse_pos) else self.colors["button"]
            
            # 绘制按钮
            pygame.draw.rect(self.screen, button_color, button["rect"])
            pygame.draw.rect(self.screen, (50, 50, 50), button["rect"], 2)  # 边框
            
            # 绘制按钮文字
            text_surf = self.font_small.render(button["text"], True, self.colors["button_text"])
            text_rect = text_surf.get_rect(center=button["rect"].center)
            self.screen.blit(text_surf, text_rect)