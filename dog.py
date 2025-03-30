import time
import random
import json

class Dog:
    # 狗狗品种及其特性
    BREEDS = {
        "拉布拉多": {"hunger_rate": 1.2, "happiness_bonus": 1.5, "energy_recovery": 1.2},
        "柯基": {"hunger_rate": 0.8, "happiness_bonus": 1.8, "energy_recovery": 0.9},
        "哈士奇": {"hunger_rate": 1.5, "happiness_bonus": 1.2, "energy_recovery": 1.5},
        "金毛": {"hunger_rate": 1.3, "happiness_bonus": 1.4, "energy_recovery": 1.1},
        "边牧": {"hunger_rate": 1.1, "happiness_bonus": 1.3, "energy_recovery": 1.4}
    }
    
    # 性格类型及其影响
    PERSONALITIES = {
        "活泼": {"happiness_rate": 0.8, "energy_consumption": 1.2},
        "温顺": {"happiness_rate": 1.0, "energy_consumption": 0.8},
        "机警": {"happiness_rate": 1.2, "energy_consumption": 1.0},
        "顽皮": {"happiness_rate": 0.7, "energy_consumption": 1.3},
        "独立": {"happiness_rate": 1.3, "energy_consumption": 0.9}
    }
    
    # 成长阶段
    GROWTH_STAGES = ["幼犬", "青年犬", "成年犬", "老年犬"]
    
    def __init__(self, name, breed="柯基", personality="活泼"):
        # 基本信息
        self.name = name
        self.breed = breed if breed in self.BREEDS else "柯基"
        self.personality = personality if personality in self.PERSONALITIES else "活泼"
        
        # 状态属性（0-100）
        self.hunger = 50       # 饥饿度（越低越饿）
        self.happiness = 70    # 快乐度
        self.health = 100      # 健康度
        self.cleanliness = 80  # 清洁度
        self.energy = 100      # 精力值
        
        # 成长相关
        self.age = 0           # 年龄（天）
        self.growth_stage = 0  # 成长阶段索引
        
        # 技能和能力
        self.skills = {}       # 技能字典 {"技能名": 等级}
        self.affection = 50   # 亲密度
        
        # 时间记录
        self.creation_time = time.time()
        self.last_update_time = time.time()
        
        # 特性修正值
        self.breed_traits = self.BREEDS[self.breed]
        self.personality_traits = self.PERSONALITIES[self.personality]
    
    def update_status(self, elapsed_time_seconds):
        """根据经过的时间更新宠物状态"""
        # 将秒转换为小时
        hours = elapsed_time_seconds / 3600
        
        # 更新饥饿度（随时间降低）
        hunger_decrease = 5 * hours * self.breed_traits["hunger_rate"]
        self.hunger = max(0, self.hunger - hunger_decrease)
        
        # 更新快乐度（随时间降低）
        happiness_decrease = 3 * hours / self.personality_traits["happiness_rate"]
        self.happiness = max(0, self.happiness - happiness_decrease)
        
        # 更新清洁度（随时间降低）
        cleanliness_decrease = 2 * hours
        self.cleanliness = max(0, self.cleanliness - cleanliness_decrease)
        
        # 更新精力值（如果不是睡觉状态，则随时间降低）
        energy_decrease = 1 * hours
        self.energy = max(0, self.energy - energy_decrease)
        
        # 更新健康度（受饥饿度和清洁度影响）
        if self.hunger < 20 or self.cleanliness < 30:
            health_decrease = 2 * hours
            self.health = max(0, self.health - health_decrease)
        
        # 更新年龄
        self.age += hours / 24  # 转换为天数
        self.update_growth_stage()
        
        # 更新时间记录
        self.last_update_time = time.time()
    
    def update_growth_stage(self):
        """根据年龄更新成长阶段"""
        if self.age < 90:  # 3个月内为幼犬
            new_stage = 0
        elif self.age < 365:  # 1年内为青年犬
            new_stage = 1
        elif self.age < 2555:  # 7年内为成年犬
            new_stage = 2
        else:  # 7年以上为老年犬
            new_stage = 3
        
        # 如果成长阶段发生变化
        if new_stage != self.growth_stage:
            self.growth_stage = new_stage
            return True
        return False
    
    def feed(self, food_type="普通狗粮"):
        """喂食"""
        food_effects = {
            "普通狗粮": {"hunger": 20, "health": 5},
            "高级狗粮": {"hunger": 30, "health": 10},
            "狗狗零食": {"hunger": 10, "happiness": 15},
            "鸡肉": {"hunger": 25, "happiness": 10, "health": 5},
            "牛肉": {"hunger": 35, "happiness": 15, "health": 8}
        }
        
        if food_type in food_effects:
            effects = food_effects[food_type]
            
            # 应用食物效果
            for attribute, value in effects.items():
                current_value = getattr(self, attribute)
                setattr(self, attribute, min(100, current_value + value))
            
            # 返回效果描述
            return f"{self.name}吃了{food_type}，感到很满足！"
        else:
            return f"{self.name}对这个食物不感兴趣..."
    
    def play(self, game_type="普通玩耍"):
        """玩耍"""
        # 检查精力是否足够
        if self.energy < 20:
            return f"{self.name}太累了，不想玩..."
        
        game_effects = {
            "普通玩耍": {"happiness": 15, "energy": -10},
            "接飞盘": {"happiness": 25, "energy": -20},
            "追球": {"happiness": 20, "energy": -15},
            "拔河": {"happiness": 30, "energy": -25},
            "智力游戏": {"happiness": 20, "energy": -10}
        }
        
        if game_type in game_effects:
            effects = game_effects[game_type]
            
            # 应用游戏效果（考虑性格特性）
            happiness_gain = effects["happiness"] * self.personality_traits["happiness_rate"]
            energy_cost = abs(effects["energy"]) * self.personality_traits["energy_consumption"]
            
            self.happiness = min(100, self.happiness + happiness_gain)
            self.energy = max(0, self.energy - energy_cost)
            
            # 轻微降低清洁度
            self.cleanliness = max(0, self.cleanliness - 5)
            
            return f"{self.name}玩{game_type}玩得很开心！"
        else:
            return f"{self.name}不知道怎么玩这个游戏..."
    
    def bath(self):
        """洗澡"""
        # 清洁度提高
        cleanliness_before = self.cleanliness
        self.cleanliness = 100
        
        # 根据性格可能影响快乐度
        if self.personality == "活泼" or self.personality == "顽皮":
            self.happiness = max(0, self.happiness - 10)
            message = f"{self.name}不太喜欢洗澡，但现在干净多了！"
        else:
            self.happiness = min(100, self.happiness + 5)
            message = f"{self.name}享受洗澡的过程，现在干干净净的！"
        
        return message
    
    def sleep(self, duration_hours=8):
        """睡觉"""
        # 精力恢复
        energy_recovery = min(100 - self.energy, duration_hours * 10 * self.breed_traits["energy_recovery"])
        self.energy = min(100, self.energy + energy_recovery)
        
        # 健康略微恢复
        self.health = min(100, self.health + duration_hours * 2)
        
        # 睡觉时间内饥饿度略微下降
        hunger_decrease = duration_hours * 2 * self.breed_traits["hunger_rate"]
        self.hunger = max(0, self.hunger - hunger_decrease)
        
        return f"{self.name}睡了{duration_hours}小时，精力恢复了！"
    
    def train(self, skill_name):
        """训练技能"""
        # 检查精力是否足够
        if self.energy < 30:
            return f"{self.name}太累了，无法集中注意力训练..."
        
        # 可训练的技能列表
        available_skills = ["坐下", "握手", "打滚", "接飞盘", "捡球", "原地等待"]
        
        if skill_name not in available_skills:
            return f"无法训练{skill_name}这个技能"
        
        # 初始化技能或提升等级
        current_level = self.skills.get(skill_name, 0)
        
        # 技能等级上限为5
        if current_level >= 5:
            return f"{self.name}的{skill_name}技能已经达到最高等级！"
        
        # 训练成功率基于当前等级和亲密度
        success_chance = 0.5 + (self.affection / 200) - (current_level * 0.1)
        success = random.random() < success_chance
        
        # 消耗精力
        self.energy = max(0, self.energy - 20)
        
        if success:
            # 提升技能等级
            self.skills[skill_name] = current_level + 1
            # 提升亲密度
            self.affection = min(100, self.affection + 5)
            # 提升快乐度
            self.happiness = min(100, self.happiness + 10)
            
            return f"{self.name}成功学会了{skill_name}！当前等级：{self.skills[skill_name]}"
        else:
            # 轻微提升亲密度
            self.affection = min(100, self.affection + 2)
            
            return f"{self.name}正在努力学习{skill_name}，但还需要更多练习。"
    
    def pet(self):
        """抚摸宠物"""
        # 提升快乐度和亲密度
        happiness_gain = 5 * self.personality_traits["happiness_rate"]
        self.happiness = min(100, self.happiness + happiness_gain)
        self.affection = min(100, self.affection + 3)
        
        responses = [
            f"{self.name}舒服地眯起了眼睛。",
            f"{self.name}用头蹭了蹭你的手。",
            f"{self.name}发出满足的呼噜声。",
            f"{self.name}摇了摇尾巴，看起来很开心。"
        ]
        
        return random.choice(responses)
    
    def get_status_description(self):
        """获取宠物状态描述"""
        status = {
            "hunger": self.get_attribute_level(self.hunger),
            "happiness": self.get_attribute_level(self.happiness),
            "health": self.get_attribute_level(self.health),
            "cleanliness": self.get_attribute_level(self.cleanliness),
            "energy": self.get_attribute_level(self.energy),
            "growth_stage": self.GROWTH_STAGES[self.growth_stage],
            "age": f"{int(self.age)}天"
        }
        
        return status
    
    def get_attribute_level(self, value):
        """将数值转换为描述级别"""
        if value >= 80:
            return "优秀"
        elif value >= 60:
            return "良好"
        elif value >= 40:
            return "一般"
        elif value >= 20:
            return "较差"
        else:
            return "糟糕"
    
    def to_dict(self):
        """将宠物数据转换为字典，用于保存"""
        return {
            "name": self.name,
            "breed": self.breed,
            "personality": self.personality,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "health": self.health,
            "cleanliness": self.cleanliness,
            "energy": self.energy,
            "age": self.age,
            "growth_stage": self.growth_stage,
            "skills": self.skills,
            "affection": self.affection,
            "creation_time": self.creation_time,
            "last_update_time": self.last_update_time
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建宠物实例"""
        dog = cls(data["name"], data["breed"], data["personality"])
        dog.hunger = data["hunger"]
        dog.happiness = data["happiness"]
        dog.health = data["health"]
        dog.cleanliness = data["cleanliness"]
        dog.energy = data["energy"]
        dog.age = data["age"]
        dog.growth_stage = data["growth_stage"]
        dog.skills = data["skills"]
        dog.affection = data["affection"]
        dog.creation_time = data["creation_time"]
        dog.last_update_time = data["last_update_time"]
        return dog