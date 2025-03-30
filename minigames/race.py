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