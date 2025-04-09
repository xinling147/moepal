import pygame
import sys
import os
import random
from dog import Dog
from ui import UI
import json
import time
from minigames import FetchGame, MazeGame, RaceGame
from interaction import VoiceRecognition, TouchInteraction, EmotionSystem

class Game:
    def __init__(self):
        # 初始化Pygame
        pygame.init()
        pygame.display.set_caption("AI宠物狗狗")
        
        # 设置屏幕尺寸
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        
        # 创建目录结构
        self.create_directories()
        
        # 加载或创建宠物
        self.dog = self.load_dog()
        
        # 初始化UI
        self.ui = UI(self.screen, self.dog)
        
        # 游戏时钟
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # 上次状态更新时间
        self.last_update_time = time.time()
        
        # 时间系统
        self.game_time = 8.0  # 游戏内时间（小时），从早上8点开始
        self.day_length = 24  # 一天的长度（小时）
        self.time_speed = 12.0  # 时间流速倍率（5分钟现实时间 = 1天游戏时间）
        self.day_cycle = 0  # 当前天数
        
        # 迷你游戏系统
        self.mini_games = {
            "fetch": FetchGame(self.screen, self.dog, self.ui),
            "maze": MazeGame(self.screen, self.dog, self.ui),
            "race": RaceGame(self.screen, self.dog, self.ui)
        }
        self.current_game = None
        
        # 交互系统
        self.voice_recognition = VoiceRecognition(self.dog)
        self.touch_interaction = TouchInteraction(self.dog)
        self.emotion_system = EmotionSystem(self.dog)
        
        # 是否激活语音识别
        self.voice_active = False
        
        # 环境系统
        self.environment = {
            "weather": "sunny",  # 天气状态: sunny, rainy, cloudy, snowy
            "season": "spring",  # 季节: spring, summer, autumn, winter
            "toys": []  # 场景中放置的玩具列表
        }
        
        # 天气变化计时器
        self.weather_change_time = time.time() + random.uniform(300, 600)  # 5-10分钟后随机变化天气
        
        # 季节持续时间（游戏内天数）
        self.season_duration = 30  # 30天一个季节
        
        # 游戏运行标志
        self.running = True
    
    def create_directories(self):
        """创建必要的目录结构"""
        directories = [
            "assets/images/pixel_dogs",
            "assets/images/animations",
            "assets/images/backgrounds",
            "assets/images/items",
            "assets/sounds",
            "minigames",
            "interaction",
            "data/saves"
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(os.path.dirname(__file__), directory), exist_ok=True)
    
    def load_dog(self):
        """加载宠物数据或创建新宠物"""
        save_path = os.path.join(os.path.dirname(__file__), "data/saves/dog.json")
        
        if os.path.exists(save_path):
            try:
                with open(save_path, "r") as f:
                    dog_data = json.load(f)
                return Dog.from_dict(dog_data)
            except Exception as e:
                print(f"加载宠物数据失败: {e}")
                return Dog("小狗", "未知品种", "友好")  # 提供所有必需的参数
        else:
            return Dog("小狗", "未知品种", "友好")  # 提供所有必需的参数
    
    def save_dog(self):
        """保存宠物数据"""
        save_path = os.path.join(os.path.dirname(__file__), "data/saves/dog.json")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, "w") as f:
            json.dump(self.dog.to_dict(), f, indent=4)
    
    def add_toy_to_environment(self, toy_type, position):
        """向环境中添加玩具"""
        self.environment["toys"].append({
            "type": toy_type,
            "position": position,
            "placed_time": self.game_time,
            "id": len(self.environment["toys"])
        })
        self.ui.display_message(f"在场景中放置了{toy_type}")
    
    def remove_toy_from_environment(self, toy_id):
        """从环境中移除玩具"""
        for i, toy in enumerate(self.environment["toys"]):
            if toy["id"] == toy_id:
                removed_toy = self.environment["toys"].pop(i)
                self.ui.display_message(f"移除了{removed_toy['type']}")
                return True
        return False
    
    def change_weather(self, weather_type=None):
        """改变天气"""
        weather_types = ["sunny", "rainy", "cloudy", "snowy"]
        
        # 如果没有指定天气类型，则随机选择一个不同于当前的天气
        if weather_type is None:
            current_weather = self.environment["weather"]
            available_weathers = [w for w in weather_types if w != current_weather]
            weather_type = random.choice(available_weathers)
        
        # 确保天气类型有效
        if weather_type in weather_types:
            self.environment["weather"] = weather_type
            
            # 天气效果
            weather_effects = {
                "sunny": {"happiness": 5, "energy": 5},
                "rainy": {"happiness": -5, "cleanliness": -10},
                "cloudy": {"happiness": -2, "energy": -2},
                "snowy": {"energy": -5, "happiness": 3, "cleanliness": -3}
            }
            
            # 应用天气效果
            if weather_type in weather_effects:
                effects = weather_effects[weather_type]
                effect_desc = []
                
                for attribute, value in effects.items():
                    current = getattr(self.dog, attribute)
                    setattr(self.dog, attribute, max(0, min(100, current + value)))
                    if value > 0:
                        effect_desc.append(f"{attribute}+{value}")
                    else:
                        effect_desc.append(f"{attribute}{value}")
                
                # 显示天气变化消息
                weather_name = {
                    "sunny": "晴天",
                    "rainy": "雨天",
                    "cloudy": "阴天",
                    "snowy": "雪天"
                }.get(weather_type, weather_type)
                
                self.ui.display_message(f"天气变为{weather_name}！{', '.join(effect_desc)}")
                
                # 设置下一次天气变化时间
                self.weather_change_time = time.time() + random.uniform(300, 600)
                
                # 更新UI中的环境信息
                self.ui.update_environment(self.environment)
    
    def update_season(self):
        """更新季节"""
        # 每30天更换一次季节
        day_in_season = self.day_cycle % self.season_duration
        season_number = (self.day_cycle // self.season_duration) % 4
        
        seasons = ["spring", "summer", "autumn", "winter"]
        new_season = seasons[season_number]
        
        if new_season != self.environment["season"]:
            self.environment["season"] = new_season
            
            # 季节名称
            season_name = {
                "spring": "春季",
                "summer": "夏季",
                "autumn": "秋季",
                "winter": "冬季"
            }.get(new_season, new_season)
            
            self.ui.display_message(f"季节变为{season_name}了！")
            
            # 更新UI中的环境信息
            self.ui.update_environment(self.environment)
    
    def start_mini_game(self, game_name):
        """启动迷你游戏"""
        if game_name in self.mini_games:
            self.current_game = game_name
            self.mini_games[game_name].start_game()
            return True
        return False
    
    def end_mini_game(self):
        """结束迷你游戏"""
        self.current_game = None
    
    def toggle_voice_recognition(self):
        """切换语音识别状态"""
        self.voice_active = not self.voice_active
        if self.voice_active:
            self.voice_recognition.start_listening()
            self.ui.display_message("开始语音识别，请讲话...")
        else:
            self.ui.display_message("停止语音识别")
        return self.voice_active
    
    def update(self):
        """更新游戏状态"""
        current_time = time.time()
        real_elapsed_time = current_time - self.last_update_time
        
        # 如果正在进行迷你游戏，暂停时间流逝
        if not self.current_game:
            # 计算游戏内时间流逝
            game_elapsed_time = real_elapsed_time * self.time_speed
            self.game_time += game_elapsed_time / 3600  # 转换为游戏内小时
            
            # 计算天数
            new_day = False
            if self.game_time >= self.day_length:
                new_days = int(self.game_time / self.day_length)
                self.day_cycle += new_days
                self.game_time %= self.day_length
                new_day = True
            
            # 如果是新的一天，更新季节
            if new_day:
                self.update_season()
            
            # 随机天气变化
            if current_time >= self.weather_change_time:
                self.change_weather()
            
            # 判断是否为白天
            is_day = 6 <= self.game_time < 19  # 6点到19点为白天
            
            # 更新宠物状态（使用实际时间流逝）
            if real_elapsed_time >= 10:  # 每10秒现实时间更新一次
                self.dog.update_status(real_elapsed_time, is_day=is_day)
                self.last_update_time = current_time
                self.save_dog()
                
                # 检查是否有成长阶段变化
                if self.dog.update_growth_stage():
                    growth_stage = self.dog.GROWTH_STAGES[self.dog.growth_stage]
                    self.ui.display_message(f"{self.dog.name}已经成长为{growth_stage}了！")
            
            # 将时间信息传递给UI
            time_info = {
                "hour": int(self.game_time),
                "minute": int((self.game_time % 1) * 60),
                "day": self.day_cycle,
                "is_day": is_day
            }
            self.ui.update_time(time_info)
            
            # 更新情感系统
            emotion_update = self.emotion_system.update()
            if emotion_update:
                self.ui.display_message(emotion_update)
            
            # 更新语音识别
            if self.voice_active:
                self.voice_recognition.update()
                if self.voice_recognition.status_message and self.voice_recognition.status_message != "正在聆听...":
                    self.ui.display_message(self.voice_recognition.status_message)
            
            # 处理环境中的玩具互动
            self.update_toys_interaction()
        else:
            # 更新当前迷你游戏
            game_active = self.mini_games[self.current_game].update()
            if not game_active:
                # 游戏结束，处理奖励
                game_result = self.mini_games[self.current_game].get_result()
                if game_result and "score" in game_result:
                    # 根据分数给予奖励
                    happiness_gain = min(20, game_result["score"] / 5)
                    self.dog.happiness = min(100, self.dog.happiness + happiness_gain)
                    
                    # 提升相关技能
                    if self.current_game == "fetch" and "接飞盘" in self.dog.skills:
                        skill_exp = min(5, game_result["score"] / 10)
                        self.dog.skills["接飞盘"] = min(5, self.dog.skills["接飞盘"] + skill_exp * 0.1)
                    
                    # 显示游戏结果
                    self.ui.display_message(f"游戏结束！得分: {game_result['score']}，快乐度+{int(happiness_gain)}")
                
                self.end_mini_game()
                # 重置时间更新
                self.last_update_time = time.time()
    
    def update_toys_interaction(self):
        """更新玩具互动"""
        # 移除放置时间超过3小时的玩具
        current_time = self.game_time + self.day_cycle * self.day_length
        self.environment["toys"] = [
            toy for toy in self.environment["toys"] 
            if current_time - (toy["placed_time"] + toy.get("day", 0) * self.day_length) < 3
        ]
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # 如果正在进行迷你游戏，将事件传递给迷你游戏
            if self.current_game:
                self.mini_games[self.current_game].handle_event(event)
            else:
                # 先检查是否点击了UI按钮
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    # 检查是否点击了按钮
                    button_clicked = False
                    for button in self.ui.buttons.get(self.ui.current_menu, []):
                        if button["rect"].collidepoint(mouse_pos):
                            button_clicked = True
                            break
                    
                    # 只有在没有点击按钮时，才传递给触摸交互系统
                    if not button_clicked:
                        touch_result = self.touch_interaction.handle_event(event)
                        if touch_result:
                            self.ui.display_message(touch_result)
                else:
                    # 处理其他类型的事件（鼠标移动、释放等）
                    touch_result = self.touch_interaction.handle_event(event)
                    if touch_result:
                        self.ui.display_message(touch_result)
                
                # 将事件传递给UI处理
                action = self.ui.handle_event(event)
                
                # 处理UI返回的动作
                if action:
                    if action.startswith("play_minigame_"):
                        game_name = action.replace("play_minigame_", "")
                        self.start_mini_game(game_name)
                    elif action == "toggle_voice":
                        self.toggle_voice_recognition()
                    elif action.startswith("place_toy_"):
                        toy_type = action.replace("place_toy_", "")
                        # 放置玩具在随机位置
                        position = (random.randint(100, self.width - 100), 
                                    random.randint(300, self.height - 100))
                        self.add_toy_to_environment(toy_type, position)
                    elif action.startswith("change_weather_"):
                        weather_type = action.replace("change_weather_", "")
                        self.change_weather(weather_type)
    
    def run(self):
        """运行游戏主循环"""
        while self.running:
            # 处理事件
            self.handle_events()
            
            # 更新游戏状态
            self.update()
            
            # 渲染界面
            if self.current_game:
                self.mini_games[self.current_game].render()
            else:
                # 更新UI中的环境信息
                self.ui.update_environment(self.environment)
                self.ui.render()
                
                # 如果语音识别开启，显示语音识别状态
                if self.voice_active:
                    self.voice_recognition.render(self.screen, 20, self.height - 60)
            
            # 更新显示
            pygame.display.flip()
            
            # 控制帧率
            self.clock.tick(self.fps)
        
        # 退出前保存数据
        self.save_dog()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()