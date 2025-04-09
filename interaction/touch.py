import pygame
import math
import time
import random

class TouchInteraction:
    def __init__(self, dog):
        self.dog = dog
        
        # 触摸状态
        self.touch_points = []  # 存储触摸轨迹点
        self.last_touch_time = 0
        self.touch_cooldown = 0.5  # 触摸冷却时间（秒）
        
        # 手势识别
        self.gesture = None
        self.gesture_time = 0
        
        # 可识别的手势
        self.gestures = {
            "pat": "抚摸",      # 简单的点击或短距离移动
            "circle": "转圈",   # 画圈
            "swipe": "跳跃",    # 快速滑动
            "zigzag": "玩耍"    # 之字形
        }
        
        # 反馈消息
        self.message = ""
        self.message_time = 0
    
    def handle_event(self, event):
        """处理pygame事件并转换为触摸事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 鼠标按下
            self.handle_touch(event.pos, True, False)
            return self.message
        
        elif event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            # 鼠标移动（按住左键）
            self.handle_touch(event.pos, True, True)
            return self.message
        
        elif event.type == pygame.MOUSEBUTTONUP:
            # 鼠标释放
            self.handle_touch(event.pos, False, False)
            return self.message
        
        return None
    
    def handle_touch(self, pos, is_down, is_motion):
        """处理触摸事件"""
        current_time = time.time()
        
        # 如果是按下或移动，记录触摸点
        if is_down:
            if is_motion:
                # 如果是移动，添加到轨迹
                if self.touch_points:
                    self.touch_points.append(pos)
            else:
                # 如果是新的按下，开始新的轨迹
                if current_time - self.last_touch_time > self.touch_cooldown:
                    self.touch_points = [pos]
                    self.last_touch_time = current_time
        else:
            # 如果是释放，分析手势
            if len(self.touch_points) > 1:
                self.recognize_gesture()
            
            # 清空触摸点
            self.touch_points = []
    
    def recognize_gesture(self):
        """识别手势类型"""
        if len(self.touch_points) < 2:
            return
        
        # 计算总移动距离和方向变化
        total_distance = 0
        direction_changes = 0
        prev_direction = None
        
        # 检测是否形成闭环（圆形）
        is_circle = False
        if len(self.touch_points) > 10:  # 至少需要一定数量的点才能形成圆
            first_point = self.touch_points[0]
            last_point = self.touch_points[-1]
            distance_start_end = math.sqrt((last_point[0] - first_point[0])**2 + 
                                          (last_point[1] - first_point[1])**2)
            
            # 如果起点和终点接近，可能是圆
            if distance_start_end < 50:  # 阈值可调整
                # 计算到中心点的平均距离，判断是否为圆
                center_x = sum(p[0] for p in self.touch_points) / len(self.touch_points)
                center_y = sum(p[1] for p in self.touch_points) / len(self.touch_points)
                
                distances = [math.sqrt((p[0] - center_x)**2 + (p[1] - center_y)**2) 
                           for p in self.touch_points]
                avg_distance = sum(distances) / len(distances)
                variance = sum((d - avg_distance)**2 for d in distances) / len(distances)
                
                # 如果方差较小，说明点到中心的距离比较一致，更可能是圆
                if variance < 200:  # 阈值可调整
                    is_circle = True
        
        # 计算移动距离和方向变化
        for i in range(1, len(self.touch_points)):
            p1 = self.touch_points[i-1]
            p2 = self.touch_points[i]
            
            # 计算距离
            distance = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            total_distance += distance
            
            # 计算方向
            if distance > 5:  # 忽略微小移动
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                
                # 简化为8个方向
                if abs(dx) > abs(dy):
                    current_direction = "right" if dx > 0 else "left"
                else:
                    current_direction = "down" if dy > 0 else "up"
                
                # 检测方向变化
                if prev_direction and current_direction != prev_direction:
                    direction_changes += 1
                
                prev_direction = current_direction
        
        # 根据特征判断手势类型
        if is_circle:
            self.gesture = "circle"
        elif direction_changes >= 3 and total_distance > 100:
            self.gesture = "zigzag"
        elif total_distance > 150 and direction_changes <= 1:
            self.gesture = "swipe"
        else:
            self.gesture = "pat"
        
        # 执行手势对应的动作
        self.perform_gesture_action()
    
    def perform_gesture_action(self):
        """执行手势对应的动作"""
        if self.gesture == "pat":  # 抚摸
            # 不再触发dog.pet()方法
            #self.message = f"{self.dog.name}注意到了你的动作。"
            pass
        
        elif self.gesture == "circle":  # 转圈
            # 检查狗狗是否有"打滚"技能
            if "打滚" in self.dog.skills and self.dog.skills["打滚"] > 0:
                success_rate = 0.5 + (self.dog.skills["打滚"] * 0.1)
                if random.random() < success_rate:
                    self.message = f"{self.dog.name}看到你画圈的手势，开心地打了个滚！"
                    self.dog.happiness = min(100, self.dog.happiness + 5)
                    self.dog.energy = max(0, self.dog.energy - 3)
                    self.dog.cleanliness = max(0, self.dog.cleanliness - 2)
                else:
                    self.message = f"{self.dog.name}看到你的手势，但没有理解你的意思。"
            else:
                self.message = f"{self.dog.name}好奇地看着你画的圈。也许可以教它打滚技能？"
        
        elif self.gesture == "swipe":  # 跳跃
            # 检查狗狗是否有足够的精力
            if self.dog.energy < 10:
                self.message = f"{self.dog.name}太累了，不想动。"
            else:
                self.message = f"{self.dog.name}看到你的手势，开心地跳了起来！"
                self.dog.happiness = min(100, self.dog.happiness + 3)
                self.dog.energy = max(0, self.dog.energy - 5)
        
        elif self.gesture == "zigzag":  # 玩耍
            if self.dog.energy < 15:
                self.message = f"{self.dog.name}看起来太累了，不想玩。"
            else:
                self.message = f"{self.dog.name}被你的手势逗得很开心，在原地转来转去！"
                self.dog.happiness = min(100, self.dog.happiness + 7)
                self.dog.energy = max(0, self.dog.energy - 7)
        
        # 记录消息时间
        self.message_time = time.time()
        self.gesture_time = time.time()
    
    def update(self):
        """更新状态"""
        current_time = time.time()
        
        # 清除超时的消息
        if self.message and current_time - self.message_time > 3:
            self.message = ""
        
        # 清除超时的手势
        if self.gesture and current_time - self.gesture_time > 1:
            self.gesture = None
    
    def render(self, screen, x, y):
        """渲染触摸反馈"""
        # 绘制当前触摸轨迹
        if len(self.touch_points) > 1:
            pygame.draw.lines(screen, (100, 100, 255), False, self.touch_points, 2)
        
        # 绘制消息
        if self.message:
            font = pygame.font.SysFont("Arial", 20)
            text_surface = font.render(self.message, True, (50, 50, 50))
            screen.blit(text_surface, (x, y))
        
        # 如果有识别出的手势，显示手势名称
        if self.gesture:
            font_small = pygame.font.SysFont("Arial", 16)
            gesture_name = self.gestures.get(self.gesture, self.gesture)
            gesture_text = font_small.render(f"手势: {gesture_name}", True, (100, 100, 100))
            screen.blit(gesture_text, (x, y + 30))

    def handle_shake(self, shake_intensity):
        """处理设备摇晃"""
        # 注意：这个功能在实际应用中需要通过加速度传感器实现
        # 在Pygame中可以模拟这个功能
        
        # 根据摇晃强度产生不同的反应
        if shake_intensity > 5:  # 强烈摇晃
            self.message = f"{self.dog.name}被摇晃吓到了，看起来有点紧张！"
            self.dog.happiness = max(0, self.dog.happiness - 5)
        elif shake_intensity > 3:  # 中等摇晃
            self.message = f"{self.dog.name}感觉到了摇晃，好奇地看着你。"
        elif shake_intensity > 1:  # 轻微摇晃
            self.message = f"{self.dog.name}感觉到了轻微的摇晃，摇了摇尾巴。"
            self.dog.happiness = min(100, self.dog.happiness + 2)
        
        self.message_time = time.time()