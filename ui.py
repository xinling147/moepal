import pygame
import os
import math
import random
import sys

class UI:
    def __init__(self, screen, dog):
        self.screen = screen
        self.dog = dog
        self.width, self.height = screen.get_size()
        
        # 添加长按检测变量
        self.press_start_time = 0
        self.is_pressing = False
        self.press_duration_required = 2000  # 长按需要2000毫秒（2秒）
        
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
            "energy_bar": (147, 112, 219),      # 紫色精力值
            "day_bg": (135, 206, 250),          # 日间背景色
            "night_bg": (25, 25, 112),          # 夜间背景色
            # 季节色彩
            "spring_color": (144, 238, 144),   # 淡绿色
            "summer_color": (255, 236, 139),   # 淡黄色
            "autumn_color": (205, 133, 63),    # 棕色
            "winter_color": (230, 230, 250)    # 淡紫色
        }
        
        # 加载字体
        pygame.font.init()
        
        # 加载字体 - 尝试多种方法
        try:
            # 尝试方法1：使用特定的中文字体
            self.font_small = pygame.font.SysFont('simhei', 16)
            self.font_medium = pygame.font.SysFont('simhei', 20)
            self.font_large = pygame.font.SysFont('simhei', 24)
            # 测试字体是否能渲染中文
            test_surface = self.font_small.render('测试中文', True, (0, 0, 0))
            if test_surface.get_width() < 10:
                raise Exception("所选字体无法正确渲染中文")
        except Exception as e:
            print(f"使用SimHei字体失败: {e}")
            try:
                # 尝试方法2：使用微软雅黑
                self.font_small = pygame.font.SysFont('microsoftyahei', 16)
                self.font_medium = pygame.font.SysFont('microsoftyahei', 20)
                self.font_large = pygame.font.SysFont('microsoftyahei', 24)
            except Exception as e:
                print(f"使用微软雅黑字体失败: {e}")
                try:
                    # 尝试方法3：根据操作系统查找可用字体
                    if sys.platform.startswith('win'):
                        # Windows字体路径
                        font_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'simhei.ttf')
                    elif sys.platform.startswith('darwin'):
                        # macOS字体路径
                        font_path = '/System/Library/Fonts/PingFang.ttc'
                    else:
                        # Linux字体路径
                        font_path = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
                        
                    if os.path.exists(font_path):
                        self.font_small = pygame.font.Font(font_path, 16)
                        self.font_medium = pygame.font.Font(font_path, 20)
                        self.font_large = pygame.font.Font(font_path, 24)
                    else:
                        raise Exception(f"字体文件不存在: {font_path}")
                except Exception as e:
                    print(f"查找系统字体失败: {e}")
                    # 最后的方案：使用默认字体
                    print("使用默认字体")
                    self.font_small = pygame.font.Font(None, 16)
                    self.font_medium = pygame.font.Font(None, 20)
                    self.font_large = pygame.font.Font(None, 24)
        
        print(f"成功加载字体")
        
        # 加载图像资源
        self.load_images()
        
        # 创建按钮
        self.create_buttons()
        
        # 当前选中的菜单
        self.current_menu = "main"  # main, food, play, train
        
        # 消息显示
        self.message = ""
        self.message_time = 0
        self.message_duration = 3000  # 消息显示时间（毫秒）
        
        # 动画状态
        self.animation_frame = 0
        self.animation_time = 0
        self.current_animation = "idle"  # idle, eat, play, sleep, bath
        
        # 时间系统
        self.time_info = {
            "hour": 8,
            "minute": 0,
            "day": 0,
            "is_day": True
        }
        
        # 环境信息
        self.environment = {
            "weather": "sunny",
            "season": "spring",
            "toys": []
        }
    
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
            try:
                # 尝试使用当前字体
                font = self.font_small
                text = font.render(name, True, (0, 0, 0))
            except:
                # 如果当前字体无法渲染，使用默认字体
                font = pygame.font.Font(None, 14)
                text = font.render(name, True, (0, 0, 0))
            
            text_rect = text.get_rect(center=(size[0]//2, size[1]//2))
            surf.blit(text, text_rect)
            return surf
        
        # 创建物品图像并保存
        def create_and_save_item_image(name, color, size, file_path):
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 检查文件是否为空或不存在
            is_empty = not os.path.exists(file_path) or os.path.getsize(file_path) == 0
            
            if is_empty:
                # 创建物品图像
                surf = pygame.Surface(size)
                surf.fill((255, 255, 255))  # 白色背景
                
                # 根据物品类型绘制不同图案
                if "food" in name:
                    # 食物类物品
                    if "normal" in name:
                        # 普通狗粮
                        pygame.draw.circle(surf, (210, 180, 140), (size[0]//2, size[1]//2), size[0]//3)
                        for i in range(4):
                            offset_x = (i % 2) * 10 - 5
                            offset_y = (i // 2) * 10 - 5
                            pygame.draw.circle(surf, (190, 160, 120), (size[0]//2 + offset_x, size[1]//2 + offset_y), size[0]//6)
                    elif "premium" in name:
                        # 高级狗粮
                        pygame.draw.circle(surf, (230, 190, 150), (size[0]//2, size[1]//2), size[0]//3)
                        pygame.draw.polygon(surf, (255, 215, 0), [
                            (size[0]//2, size[1]//4),
                            (size[0]//2 + size[0]//8, size[1]//2),
                            (size[0]//2, size[1]//2 + size[1]//8),
                            (size[0]//2 - size[0]//8, size[1]//2)
                        ])
                    elif "treat" in name:
                        # 零食
                        pygame.draw.rect(surf, (240, 200, 160), (size[0]//4, size[1]//4, size[0]//2, size[1]//2))
                        pygame.draw.line(surf, (200, 160, 120), (size[0]//4, size[1]//2), (size[0]//4 + size[0]//2, size[1]//2), 2)
                    elif "chicken" in name:
                        # 鸡肉
                        pygame.draw.polygon(surf, (250, 220, 190), [
                            (size[0]//4, size[1]//4),
                            (size[0]//4 * 3, size[1]//4),
                            (size[0]//4 * 3, size[1]//4 * 3),
                            (size[0]//4, size[1]//4 * 3)
                        ])
                        pygame.draw.line(surf, (220, 190, 160), (size[0]//4, size[1]//4), (size[0]//4 * 3, size[1]//4 * 3), 2)
                        pygame.draw.line(surf, (220, 190, 160), (size[0]//4 * 3, size[1]//4), (size[0]//4, size[1]//4 * 3), 2)
                    elif "beef" in name:
                        # 牛肉
                        pygame.draw.polygon(surf, (200, 150, 130), [
                            (size[0]//4, size[1]//3),
                            (size[0]//4 * 3, size[1]//3),
                            (size[0]//4 * 3, size[1]//3 * 2),
                            (size[0]//4, size[1]//3 * 2)
                        ])
                        # 纹理
                        for i in range(3):
                            y = size[1]//3 + i * size[1]//9
                            pygame.draw.line(surf, (180, 130, 110), (size[0]//4, y), (size[0]//4 * 3, y), 1)
                elif "toy" in name:
                    # 玩具类物品
                    if "ball" in name:
                        # 球
                        pygame.draw.circle(surf, (255, 0, 0), (size[0]//2, size[1]//2), size[0]//3)
                        pygame.draw.circle(surf, (220, 0, 0), (size[0]//2 - size[0]//8, size[1]//2 - size[1]//8), size[0]//8)
                    elif "frisbee" in name:
                        # 飞盘
                        pygame.draw.circle(surf, (0, 255, 0), (size[0]//2, size[1]//2), size[0]//3)
                        pygame.draw.circle(surf, (255, 255, 255), (size[0]//2, size[1]//2), size[0]//5)
                    elif "rope" in name:
                        # 绳子
                        pygame.draw.rect(surf, (0, 0, 255), (size[0]//4, size[1]//3, size[0]//2, size[1]//3))
                        for i in range(4):
                            y = size[1]//3 + i * size[1]//12
                            color = (200, 200, 200) if i % 2 == 0 else (150, 150, 150)
                            pygame.draw.line(surf, color, (size[0]//4, y), (size[0]//4 * 3, y), 2)
                    elif "puzzle" in name:
                        # 智力玩具
                        pygame.draw.rect(surf, (255, 255, 0), (size[0]//4, size[1]//4, size[0]//2, size[1]//2))
                        pygame.draw.line(surf, (0, 0, 0), (size[0]//2, size[1]//4), (size[0]//2, size[1]//4 * 3), 2)
                        pygame.draw.line(surf, (0, 0, 0), (size[0]//4, size[1]//2), (size[0]//4 * 3, size[1]//2), 2)
                
                # 绘制边框
                pygame.draw.rect(surf, (0, 0, 0), (0, 0, size[0], size[1]), 2)
                
                # 保存图像
                try:
                    pygame.image.save(surf, file_path)
                    print(f"已创建并保存物品图像: {file_path}")
                except Exception as e:
                    print(f"保存物品图像失败: {file_path}, 错误: {e}")
                
                return surf
            else:
                # 如果文件存在且不为空，使用安全加载
                return safe_load_image(file_path, size, name)
        
        # 安全加载图像
        def safe_load_image(file_path, size, fallback_name=None):
            try:
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    img = pygame.image.load(file_path)
                    if size:
                        return pygame.transform.scale(img, size)
                    return img
                else:
                    print(f"图像文件为空或不存在: {file_path}")
                    return create_placeholder(fallback_name or os.path.basename(file_path), (200, 200, 200), size)
            except Exception as e:
                print(f"加载图像失败: {file_path}, 错误: {e}")
                return create_placeholder(fallback_name or os.path.basename(file_path), (200, 200, 200), size)
        
        # 宠物图像 - 柯基犬像素风格
        dog_size = (150, 150)
        base_path = os.path.join(os.path.dirname(__file__), "assets/images/pixel_dogs")
        
        # 根据README.md中的目录结构加载图像
        # 尝试从不同状态子文件夹中加载图像
        state_folders = ["normal", "happy", "sad", "sleeping", "sick"]
        
        # 为每个状态加载对应的图像
        for state in state_folders:
            # 加载每个状态的idle图像
            idle_path = os.path.join(base_path, state, f"{state}_idle_01.png")
            if os.path.exists(idle_path) and os.path.getsize(idle_path) > 0:
                self.images[f"dog_{state}_idle"] = safe_load_image(idle_path, dog_size, f"Dog {state.capitalize()} Idle")
                print(f"成功加载狗狗{state}待机图像: {idle_path}")
            else:
                # 如果找不到特定状态的idle图像，创建占位图像
                self.images[f"dog_{state}_idle"] = create_placeholder(f"Dog {state.capitalize()} Idle", (200, 200, 200), dog_size)
                print(f"未找到{state}待机图像，使用占位图像代替")
        
        # 确保至少有一个默认的idle图像
        if "dog_normal_idle" in self.images:
            self.images["dog_idle"] = self.images["dog_normal_idle"]
        else:
            self.images["dog_idle"] = create_placeholder("Dog Idle", (200, 200, 200), dog_size)
        
        # 尝试加载其他动作图像
        action_mappings = {
            "eat": "eat",
            "play": "play",
            "sleep": "sleep",
            "bath": "bath"
        }
        
        # 为每个状态和动作组合加载图像
        for state in state_folders:
            for action_key, action in action_mappings.items():
                action_path = os.path.join(base_path, state, f"{state}_{action}_01.png")
                if os.path.exists(action_path) and os.path.getsize(action_path) > 0:
                    self.images[f"dog_{state}_{action}"] = safe_load_image(action_path, dog_size, f"Dog {state.capitalize()} {action.capitalize()}")
                    print(f"成功加载狗狗{state} {action}图像: {action_path}")
                else:
                    # 如果找不到特定状态和动作的图像，使用该状态的idle图像
                    self.images[f"dog_{state}_{action}"] = self.images[f"dog_{state}_idle"]
                    print(f"未找到{state} {action}图像，使用{state} idle图像代替")
        
        # 为简单的动作键创建引用
        for action_key, action in action_mappings.items():
            self.images[f"dog_{action}"] = self.images[f"dog_normal_{action}"] if f"dog_normal_{action}" in self.images else self.images["dog_idle"]
        
        # 加载背景图像
        # 先检查子文件夹中的背景图片
        bg_loaded = False
        bg_folders = ["home", "garden", "park", "shop"]
        bg_files = ["home_day.jpg", "garden_day.jpg", "park_day.jpg", "living_room.jpg", "01.jpg"]
        
        # 先尝试从子文件夹加载
        for folder in bg_folders:
            folder_path = os.path.join(os.path.dirname(__file__), "assets/images/backgrounds", folder)
            if os.path.exists(folder_path):
                for file in os.listdir(folder_path):
                    if file.endswith(".jpg") or file.endswith(".png"):
                        bg_path = os.path.join(folder_path, file)
                        print(f"尝试加载背景图片: {bg_path}")
                        
                        try:
                            bg_img = pygame.image.load(bg_path)
                            # 保存原始背景图片
                            self.images["background_original"] = bg_img
                            self.images["background"] = pygame.transform.scale(bg_img, (self.width, self.height))
                            print(f"成功加载背景图片: {file} (从 {folder} 文件夹)")
                            bg_loaded = True
                            break
                        except Exception as e:
                            print(f"加载背景图片失败: {file}, 错误: {e}")
                            continue
            
            if bg_loaded:
                break
        
        # 如果从子文件夹加载失败，尝试从主文件夹加载
        if not bg_loaded:
            for bg_file in bg_files:
                bg_path = os.path.join(os.path.dirname(__file__), "assets/images/backgrounds", bg_file)
                print(f"尝试加载背景图片: {bg_path}")
                
                if os.path.exists(bg_path) and os.path.getsize(bg_path) > 0:
                    try:
                        bg_img = pygame.image.load(bg_path)
                        # 保存原始背景图片
                        self.images["background_original"] = bg_img
                        self.images["background"] = pygame.transform.scale(bg_img, (self.width, self.height))
                        print(f"成功加载背景图片: {bg_file}")
                        bg_loaded = True
                        break
                    except Exception as e:
                        print(f"加载背景图片失败: {bg_file}, 错误: {e}")
        
        if not bg_loaded:
            print("无法加载任何背景图片，使用纯色背景")
            self.images["background"] = pygame.Surface((self.width, self.height))
            self.images["background"].fill(self.colors["background"])
        
        # 物品图像
        item_size = (40, 40)
        items_path = os.path.join(os.path.dirname(__file__), "assets/images/items")
        
        # 确保物品目录存在
        os.makedirs(items_path, exist_ok=True)
        
        # 食物类物品
        self.images["food_normal"] = create_and_save_item_image("food_normal", (210, 180, 140), item_size, os.path.join(items_path, "food_normal.png"))
        self.images["food_premium"] = create_and_save_item_image("food_premium", (230, 190, 150), item_size, os.path.join(items_path, "food_premium.png"))
        self.images["food_treat"] = create_and_save_item_image("food_treat", (240, 200, 160), item_size, os.path.join(items_path, "food_treat.png"))
        self.images["food_chicken"] = create_and_save_item_image("food_chicken", (250, 220, 190), item_size, os.path.join(items_path, "food_chicken.png"))
        self.images["food_beef"] = create_and_save_item_image("food_beef", (200, 150, 130), item_size, os.path.join(items_path, "food_beef.png"))
        
        # 玩具类物品
        self.images["toy_ball"] = create_and_save_item_image("toy_ball", (255, 0, 0), item_size, os.path.join(items_path, "toy_ball.png"))
        self.images["toy_frisbee"] = create_and_save_item_image("toy_frisbee", (0, 255, 0), item_size, os.path.join(items_path, "toy_frisbee.png"))
        self.images["toy_rope"] = create_and_save_item_image("toy_rope", (0, 0, 255), item_size, os.path.join(items_path, "toy_rope.png"))
        self.images["toy_puzzle"] = create_and_save_item_image("toy_puzzle", (255, 255, 0), item_size, os.path.join(items_path, "toy_puzzle.png"))
    
    def create_buttons(self):
        """创建界面按钮"""
        self.buttons = {
            "main": [
                {"rect": pygame.Rect(50, 435, 100, 40), "text": "喂食", "action": "food_menu"},
                {"rect": pygame.Rect(170, 435, 100, 40), "text": "玩耍", "action": "play_menu"},
                {"rect": pygame.Rect(290, 435, 100, 40), "text": "洗澡", "action": "bath"},
                {"rect": pygame.Rect(410, 435, 100, 40), "text": "睡觉", "action": "sleep"},
                {"rect": pygame.Rect(530, 435, 100, 40), "text": "训练", "action": "train_menu"},
                {"rect": pygame.Rect(650, 435, 100, 40), "text": "抚摸", "action": "pet"},
                {"rect": pygame.Rect(650, 495, 100, 40), "text": "迷你游戏", "action": "minigame_menu"},
                {"rect": pygame.Rect(50, 495, 100, 40), "text": "语音识别", "action": "toggle_voice"},
                {"rect": pygame.Rect(170, 495, 100, 40), "text": "环境", "action": "environment_menu"}
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
            ],
            "minigame": [
                {"rect": pygame.Rect(50, 460, 150, 40), "text": "接飞盘游戏", "action": "play_minigame_fetch"},
                {"rect": pygame.Rect(220, 460, 150, 40), "text": "迷宫探险", "action": "play_minigame_maze"},
                {"rect": pygame.Rect(390, 460, 150, 40), "text": "障碍跑比赛", "action": "play_minigame_race"},
                {"rect": pygame.Rect(650, 520, 100, 40), "text": "返回", "action": "main_menu"}
            ],
            "environment": [
                {"rect": pygame.Rect(50, 460, 120, 40), "text": "放置球", "action": "place_toy_ball"},
                {"rect": pygame.Rect(190, 460, 120, 40), "text": "放置飞盘", "action": "place_toy_frisbee"},
                {"rect": pygame.Rect(330, 460, 120, 40), "text": "放置绳子", "action": "place_toy_rope"},
                {"rect": pygame.Rect(470, 460, 120, 40), "text": "放置智力玩具", "action": "place_toy_puzzle"},
                {"rect": pygame.Rect(50, 520, 120, 40), "text": "晴天", "action": "change_weather_sunny"},
                {"rect": pygame.Rect(190, 520, 120, 40), "text": "雨天", "action": "change_weather_rainy"},
                {"rect": pygame.Rect(330, 520, 120, 40), "text": "阴天", "action": "change_weather_cloudy"},
                {"rect": pygame.Rect(470, 520, 120, 40), "text": "雪天", "action": "change_weather_snowy"},
                {"rect": pygame.Rect(650, 520, 100, 40), "text": "返回", "action": "main_menu"}
            ]
        }
    
    def handle_event(self, event):
        """处理用户事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键单击
            # 检查按钮点击
            mouse_pos = pygame.mouse.get_pos()
            action = self.check_button_click(mouse_pos)
            
            # 开始长按检测
            dog_rect = self.images["dog_idle"].get_rect(center=(self.width//2, 250))
            if dog_rect.collidepoint(mouse_pos):
                self.press_start_time = pygame.time.get_ticks()
                self.is_pressing = True
            
            if action:
                return action
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # 左键释放
            self.is_pressing = False
            self.press_start_time = 0
        
        elif event.type == pygame.MOUSEMOTION:
            # 检查是否正在长按狗狗
            if self.is_pressing:
                mouse_pos = pygame.mouse.get_pos()
                dog_rect = self.images["dog_idle"].get_rect(center=(self.width//2, 250))
                if not dog_rect.collidepoint(mouse_pos):  # 如果鼠标移出狗狗区域
                    self.is_pressing = False
                    self.press_start_time = 0
                else:  # 如果仍在狗狗区域内
                    current_time = pygame.time.get_ticks()
                    if current_time - self.press_start_time >= self.press_duration_required:
                        self.is_pressing = False  # 重置长按状态
                        self.press_start_time = 0
                        return self.perform_action("pet")  # 触发抚摸动作
        
        return None
    
    def check_button_click(self, pos):
        """检查按钮点击"""
        # 检查当前菜单的按钮
        for button in self.buttons.get(self.current_menu, []):
            if button["rect"].collidepoint(pos):
                return self.perform_action(button["action"])
        return None
    
    def perform_action(self, action):
        """执行按钮动作"""
        # 菜单切换
        if action == "main_menu":
            self.current_menu = "main"
            return None
        elif action == "food_menu":
            self.current_menu = "food"
            return None
        elif action == "play_menu":
            self.current_menu = "play"
            return None
        elif action == "train_menu":
            self.current_menu = "train"
            return None
        elif action == "minigame_menu":
            self.current_menu = "minigame"
            return None
        elif action == "environment_menu":
            self.current_menu = "environment"
            return None
        
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
                self.display_message(self.dog.feed(food_type))
                self.current_animation = "eat"
                self.animation_frame = 0
                self.animation_time = pygame.time.get_ticks()
                return None
        
        # 玩耍动作
        elif action.startswith("play_"):
            if action.startswith("play_minigame_"):
                # 返回迷你游戏启动指令
                return action
            
            game_map = {
                "play_normal": "普通玩耍",
                "play_frisbee": "接飞盘",
                "play_ball": "追球",
                "play_rope": "拔河",
                "play_puzzle": "智力游戏"
            }
            game_type = game_map.get(action)
            if game_type:
                self.display_message(self.dog.play(game_type))
                self.current_animation = "play"
                self.animation_frame = 0
                self.animation_time = pygame.time.get_ticks()
                return None
        
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
                self.display_message(self.dog.train(skill_name))
                return None
        
        # 其他动作
        elif action == "bath":
            self.display_message(self.dog.bath())
            self.current_animation = "bath"
            self.animation_frame = 0
            self.animation_time = pygame.time.get_ticks()
            return None
        
        elif action == "sleep":
            self.display_message(self.dog.sleep(hours=8, is_day=self.time_info["is_day"]))
            self.current_animation = "sleep"
            self.animation_frame = 0
            self.animation_time = pygame.time.get_ticks()
            return None
        
        elif action == "pet":
            self.display_message(self.dog.pet())
            return None
        
        # 将动作返回给游戏主循环
        return action
    
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
    
    def update_time(self, time_info):
        """更新时间信息"""
        self.time_info = time_info
        
        # 只有当没有加载背景图片时才使用纯色背景
        if not isinstance(self.images.get("background_original"), pygame.Surface):
            # 根据时间更新背景颜色
            if time_info["is_day"]:
                # 白天背景
                self.colors["background"] = self.colors["day_bg"]
            else:
                # 夜晚背景
                self.colors["background"] = self.colors["night_bg"]
            
            # 重新创建背景图像
            self.images["background"] = pygame.Surface((self.width, self.height))
            self.images["background"].fill(self.colors["background"])
    
    def display_message(self, text, duration=3000):
        """显示消息"""
        if text:  # 只有当有新消息时才更新
            self.message = text
            self.message_time = pygame.time.get_ticks()
            self.message_duration = duration  # 设置消息持续时间为3秒
    
    def update_environment(self, environment):
        """更新环境信息"""
        self.environment = environment
        
        # 如果没有背景图片，则使用纯色背景
        if "background_original" not in self.images or not isinstance(self.images["background_original"], pygame.Surface):
            # 根据季节调整背景色调
            if self.time_info["is_day"]:
                base_color = self.colors["day_bg"]
            else:
                base_color = self.colors["night_bg"]
            
            # 混合季节颜色
            season_color = self.colors.get(f"{self.environment['season']}_color", (255, 255, 255))
            
            # 根据季节和日夜调整背景颜色
            if self.time_info["is_day"]:
                # 白天：季节色彩更明显
                r = int(base_color[0] * 0.7 + season_color[0] * 0.3)
                g = int(base_color[1] * 0.7 + season_color[1] * 0.3)
                b = int(base_color[2] * 0.7 + season_color[2] * 0.3)
            else:
                # 夜晚：季节色彩较弱
                r = int(base_color[0] * 0.9 + season_color[0] * 0.1)
                g = int(base_color[1] * 0.9 + season_color[1] * 0.1)
                b = int(base_color[2] * 0.9 + season_color[2] * 0.1)
                
            # 确保RGB值在0-255范围内
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # 更新背景颜色
            self.colors["background"] = (r, g, b)
            
            # 重新创建背景图像
            if "background" not in self.images:
                self.images["background"] = pygame.Surface((self.width, self.height))
            self.images["background"].fill(self.colors["background"])
        else:
            # 使用已加载的背景图片
            # 复制原始背景以进行处理
            bg_img = self.images["background_original"].copy()
            bg_img = pygame.transform.scale(bg_img, (self.width, self.height))
            
            # 添加季节色彩滤镜
            season_color = self.colors.get(f"{self.environment['season']}_color", (255, 255, 255))
            season_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            if self.time_info["is_day"]:
                # 白天：季节色彩轻微叠加
                season_overlay.fill((season_color[0], season_color[1], season_color[2], 40))  # 透明度低
            else:
                # 晚上：使背景变暗并添加轻微季节色彩
                dark_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                dark_overlay.fill((0, 0, 30, 150))  # 蓝色调的暗色覆盖层
                bg_img.blit(dark_overlay, (0, 0))
                season_overlay.fill((season_color[0], season_color[1], season_color[2], 20))  # 更低的透明度
            
            bg_img.blit(season_overlay, (0, 0))
            self.images["background"] = bg_img
    
    def render(self):
        """渲染界面"""
        # 绘制背景
        self.screen.blit(self.images["background"], (0, 0))
        
        # 绘制环境元素（天气和季节）
        self.render_environment()
        
        # 绘制时间信息
        self.render_time_info()
        
        # 绘制宠物
        self.render_dog()
        
        # 绘制场景中的玩具
        self.render_toys()
        
        # 绘制状态栏
        self.render_status_bars()
        
        # 绘制宠物信息
        self.render_dog_info()
        
        # 绘制按钮
        self.render_buttons()
        
        # 绘制消息
        current_time = pygame.time.get_ticks()
        if self.message and current_time - self.message_time < self.message_duration:
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
        elif current_time - self.message_time >= self.message_duration:
            self.message = ""
    
    def render_environment(self):
        """渲染环境元素"""
        # 绘制天气和季节信息
        weather_names = {
            "sunny": "晴天",
            "rainy": "雨天",
            "cloudy": "阴天",
            "snowy": "雪天"
        }
        
        season_names = {
            "spring": "春季",
            "summer": "夏季",
            "autumn": "秋季",
            "winter": "冬季"
        }
        
        weather_text = f"天气：{weather_names.get(self.environment['weather'], self.environment['weather'])}"
        season_text = f"季节：{season_names.get(self.environment['season'], self.environment['season'])}"
        
        # 绘制天气信息
        weather_surf = self.font_small.render(weather_text, True, (255, 255, 255) if not self.time_info["is_day"] else (50, 50, 50))
        self.screen.blit(weather_surf, (20, 20))
        
        # 绘制季节信息
        season_surf = self.font_small.render(season_text, True, (255, 255, 255) if not self.time_info["is_day"] else (50, 50, 50))
        self.screen.blit(season_surf, (20, 40))
        
        # 根据天气添加实时效果
        if self.environment["weather"] == "rainy":
            # 绘制雨滴
            for _ in range(100):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                pygame.draw.line(self.screen, (200, 200, 255), 
                                (x, y), (x - 5, y + 15), 1)
        elif self.environment["weather"] == "cloudy":
            # 绘制云朵
            for _ in range(5):
                x = random.randint(50, self.width - 100)
                y = random.randint(50, 150)
                cloud_color = (220, 220, 220)
                # 创建一个带透明度的表面
                cloud_surface = pygame.Surface((100, 60), pygame.SRCALPHA)
                pygame.draw.circle(cloud_surface, cloud_color, (30, 30), 30)
                pygame.draw.circle(cloud_surface, cloud_color, (50, 20), 25)
                pygame.draw.circle(cloud_surface, cloud_color, (70, 30), 35)
                # 调整整个表面的透明度
                cloud_surface.set_alpha(180)
                self.screen.blit(cloud_surface, (x, y))
        elif self.environment["weather"] == "snowy":
            # 绘制雪花
            for _ in range(50):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 2)
    
    def render_toys(self):
        """渲染场景中的玩具"""
        for toy in self.environment["toys"]:
            toy_type = toy["type"]
            position = toy["position"]
            
            # 根据玩具类型选择图像
            if toy_type == "ball" and "toy_ball" in self.images:
                toy_image = self.images["toy_ball"]
            elif toy_type == "frisbee" and "toy_frisbee" in self.images:
                toy_image = self.images["toy_frisbee"]
            elif toy_type == "rope" and "toy_rope" in self.images:
                toy_image = self.images["toy_rope"]
            elif toy_type == "puzzle" and "toy_puzzle" in self.images:
                toy_image = self.images["toy_puzzle"]
            else:
                # 如果没有对应图像，创建一个占位图形
                toy_image = pygame.Surface((30, 30))
                toy_image.fill((255, 0, 0))
            
            # 绘制玩具
            toy_rect = toy_image.get_rect(center=position)
            self.screen.blit(toy_image, toy_rect)
    
    def render_time_info(self):
        """渲染时间信息"""
        time_text = f"第 {self.time_info['day'] + 1} 天  {self.time_info['hour']:02d}:{self.time_info['minute']:02d}"
        time_surf = self.font_medium.render(time_text, True, (255, 255, 255) if not self.time_info["is_day"] else (50, 50, 50))
        self.screen.blit(time_surf, (self.width - 200, 20))
        
        # 绘制日夜图标
        if self.time_info["is_day"]:
            # 绘制太阳
            pygame.draw.circle(self.screen, (255, 255, 0), (self.width - 220, 25), 10)
            # 绘制光芒
            for i in range(8):
                angle = i * math.pi / 4
                start_x = self.width - 220 + math.cos(angle) * 10
                start_y = 25 + math.sin(angle) * 10
                end_x = self.width - 220 + math.cos(angle) * 15
                end_y = 25 + math.sin(angle) * 15
                pygame.draw.line(self.screen, (255, 255, 0), (start_x, start_y), (end_x, end_y), 2)
        else:
            # 绘制月亮
            pygame.draw.circle(self.screen, (200, 200, 200), (self.width - 220, 25), 10)
            # 绘制月牙
            pygame.draw.circle(self.screen, self.colors["night_bg"], (self.width - 225, 22), 8)
    
    def determine_dog_state(self):
        """根据狗狗的属性确定当前状态"""
        # 如果狗狗在睡觉，返回sleeping状态
        if self.dog.is_sleeping:
            return "sleeping"
        
        # 如果健康值低，返回sick状态
        if self.dog.health < 30:
            return "sick"
        
        # 如果快乐度低，返回sad状态
        if self.dog.happiness < 30:
            return "sad"
        
        # 如果快乐度高，返回happy状态
        if self.dog.happiness > 80:
            return "happy"
        
        # 默认返回normal状态
        return "normal"
    
    def render_dog(self):
        """渲染宠物"""
        # 更新动画
        self.update_animation()
        
        # 确定狗狗当前状态
        dog_state = self.determine_dog_state()
        
        # 绘制宠物
        dog_image_key = f"dog_{self.current_animation}"
        
        # 如果是睡觉状态，优先使用睡觉图片
        if self.dog.is_sleeping:
            state_image_key = f"dog_sleeping_{self.current_animation}"
            if state_image_key in self.images:
                dog_image = self.images[state_image_key]
            elif "dog_sleeping_idle" in self.images:
                dog_image = self.images["dog_sleeping_idle"]
            else:
                dog_image = self.images[dog_image_key] if dog_image_key in self.images else self.images["dog_idle"]
        # 否则根据状态选择对应图片
        else:
            state_image_key = f"dog_{dog_state}_{self.current_animation}"
            if state_image_key in self.images:
                dog_image = self.images[state_image_key]
            elif f"dog_{dog_state}_idle" in self.images:
                dog_image = self.images[f"dog_{dog_state}_idle"]
            elif dog_image_key in self.images:
                dog_image = self.images[dog_image_key]
            else:
                dog_image = self.images["dog_idle"]
        
        # 添加简单的动画效果
        dog_y_offset = math.sin(pygame.time.get_ticks() * 0.005) * 5  # 轻微上下浮动
        self.screen.blit(dog_image, dog_image.get_rect(center=(self.width//2, 250 + dog_y_offset)))
    
    def render_status_bars(self):
        """渲染状态栏"""
        # 状态栏位置和尺寸
        bar_width = 150
        bar_height = 15
        bar_spacing = 30  # 增加垂直间距，从25增加到30
        start_x = 30  # 向左移动，从50减小到30
        start_y = 60  # 向下移动，从50增加到60
        
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
            
            # 绘制状态值，略微向左移动数值位置
            value_surf = self.font_small.render(f"{int(bar['value'])}", True, self.colors["text"])
            self.screen.blit(value_surf, (start_x + 60 + bar_width + 5, start_y + i * bar_spacing))
    
    def render_dog_info(self):
        """渲染宠物信息"""
        # 宠物基本信息
        info_x = 620  # 更往右移动，确保不重叠
        info_y = 60   # 保持与状态栏一致的垂直位置
        info_spacing = 25  # 减小垂直间距，使信息更紧凑
        
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
            
            # 绘制信息值，固定距离确保对齐
            value_surf = self.font_small.render(item["value"], True, self.colors["text"])
            self.screen.blit(value_surf, (info_x + 75, info_y + i * info_spacing))
        
        # 绘制技能信息
        if self.dog.skills:
            # 技能标题位置
            skill_y = info_y + len(info_items) * info_spacing + 10
            skill_title = self.font_medium.render("已学技能:", True, self.colors["text"])
            self.screen.blit(skill_title, (info_x, skill_y))
            
            # 绘制各技能信息，合理安排位置，更紧凑但不重叠
            skill_spacing = 22  # 技能间距略小，更紧凑
            for i, (skill_name, skill_level) in enumerate(self.dog.skills.items()):
                skill_text = f"{skill_name} Lv.{skill_level}"
                skill_surf = self.font_small.render(skill_text, True, self.colors["text"])
                self.screen.blit(skill_surf, (info_x + 15, skill_y + 25 + i * skill_spacing))
    
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