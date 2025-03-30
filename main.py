import pygame
import sys
import os
from dog import Dog
from ui import UI
import json
import time

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
                return Dog("小狗")
        else:
            return Dog("小狗")
    
    def save_dog(self):
        """保存宠物数据"""
        save_path = os.path.join(os.path.dirname(__file__), "data/saves/dog.json")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, "w") as f:
            json.dump(self.dog.to_dict(), f, indent=4)
    
    def update(self):
        """更新游戏状态"""
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        
        # 每隔一段时间更新宠物状态
        if elapsed_time >= 60:  # 每分钟更新一次
            self.dog.update_status(elapsed_time)
            self.last_update_time = current_time
            self.save_dog()
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # 将事件传递给UI处理
            self.ui.handle_event(event)
    
    def run(self):
        """运行游戏主循环"""
        while self.running:
            # 处理事件
            self.handle_events()
            
            # 更新游戏状态
            self.update()
            
            # 渲染界面
            self.ui.render()
            
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