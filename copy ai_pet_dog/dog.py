import random
import time
import json
import math

class Dog:
    # 定义成长阶段
    GROWTH_STAGES = {
        0: "幼犬",
        1: "青年期",
        2: "成年期",
        3: "老年期"
    }
    
    def __init__(self, name, breed, personality):
        self.name = name
        self.breed = breed
        self.personality = personality
        
        # 基础属性
        self.hunger = 100  # 饥饿度 (越高越好)
        self.happiness = 100  # 快乐度
        self.health = 100  # 健康值
        self.cleanliness = 100  # 清洁度
        self.energy = 100  # 能量值
        
        # 成长属性
        self.age = 0  # 以天为单位
        self.level = 1  # 等级
        self.experience = 0  # 经验值
        self.growth_stage = 0  # 成长阶段：0=幼犬, 1=青年期, 2=成年期, 3=老年期
        self.affection = 50  # 亲密度
        
        # 个性化属性根据性格设置
        if personality == "活泼":
            self.happiness_decay = 0.8
            self.energy_decay = 1.2
        elif personality == "温顺":
            self.happiness_decay = 1.0
            self.energy_decay = 0.8
        elif personality == "机警":
            self.happiness_decay = 1.1
            self.energy_decay = 1.0
        elif personality == "粘人":
            self.happiness_decay = 1.2
            self.energy_decay = 1.0
        elif personality == "独立":
            self.happiness_decay = 0.7
            self.energy_decay = 0.9
        else:
            self.happiness_decay = 1.0
            self.energy_decay = 1.0
        
        # 技能和训练
        self.skills = {}  # 格式: {技能名: 熟练度}
        
        # 状态
        self.is_sleeping = False
        self.sleep_until = 0
        
        # 外观
        self.appearance = self._generate_appearance()
        
        # 上次更新时间
        self.last_update_time = time.time()
    
    def _generate_appearance(self):
        """根据品种生成外观特征"""
        colors = {
            "柯基": ["#A0522D", "#F4A460", "#D2B48C"],
            "哈士奇": ["#2F4F4F", "#708090", "#C0C0C0"],
            "金毛": ["#DAA520", "#CD853F", "#B8860B"],
            "拉布拉多": ["#8B4513", "#A0522D", "#4A2304"],
            "柴犬": ["#D2691E", "#CD853F", "#A0522D"]
        }
        
        breed_color = colors.get(self.breed, ["#A0522D", "#8B4513", "#D2691E"])
        
        return {
            "body_color": random.choice(breed_color),
            "ear_color": random.choice(breed_color),
            "size": 1.0  # 将来可以随着年龄增长
        }
    
    def to_dict(self):
        """将狗的状态转换为字典，用于保存"""
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
            "level": self.level,
            "experience": self.experience,
            "happiness_decay": self.happiness_decay,
            "energy_decay": self.energy_decay,
            "skills": self.skills,
            "is_sleeping": self.is_sleeping,
            "sleep_until": self.sleep_until,
            "appearance": self.appearance,
            "last_update_time": self.last_update_time,
            "growth_stage": self.growth_stage,
            "affection": self.affection
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典恢复狗的状态"""
        dog = cls(data["name"], data["breed"], data["personality"])
        dog.hunger = data.get("hunger", 100)
        dog.happiness = data.get("happiness", 100)
        dog.health = data.get("health", 100)
        dog.cleanliness = data.get("cleanliness", 100)
        dog.energy = data.get("energy", 100)
        dog.age = data.get("age", 0)
        dog.level = data.get("level", 1)
        dog.experience = data.get("experience", 0)
        dog.happiness_decay = data.get("happiness_decay", 1.0)
        dog.energy_decay = data.get("energy_decay", 1.0)
        dog.skills = data.get("skills", {})
        dog.is_sleeping = data.get("is_sleeping", False)
        dog.sleep_until = data.get("sleep_until", 0)
        dog.appearance = data.get("appearance", dog._generate_appearance())
        dog.last_update_time = data.get("last_update_time", time.time())
        dog.growth_stage = data.get("growth_stage", 0)
        dog.affection = data.get("affection", 50)
        return dog
    def update_status(self, seconds_passed):
        """更新狗的状态"""
        # 如果在睡觉，检查是否应该醒来
        if self.is_sleeping:
            if time.time() >= self.sleep_until:
                self.is_sleeping = False
                self.energy = min(100, self.energy + 80)  # 睡觉后恢复能量
                return f"{self.name}醒来了，精力充沛！"
            else:
                # 睡觉时不会消耗属性
                return f"{self.name}正在睡觉..."
        
        # 计算真实流逝的时间（分钟）并转换为游戏天数
        minutes_passed = seconds_passed / 60
        days_passed = minutes_passed / 5  # 5分钟现实时间 = 1天游戏时间
        
        # 根据游戏天数更新属性（原来的衰减值乘以5以适应新的时间比例）
        self.hunger = max(0, self.hunger - 1.0 * days_passed)  # 0.2 * 5 = 1.0
        self.happiness = max(0, self.happiness - 1.5 * days_passed * self.happiness_decay)  # 0.3 * 5 = 1.5
        self.cleanliness = max(0, self.cleanliness - 0.75 * days_passed)  # 0.15 * 5 = 0.75
        self.energy = max(0, self.energy - 0.5 * days_passed * self.energy_decay)  # 0.1 * 5 = 0.5
        
        # 更新年龄
        self.age += days_passed
        
        # 饥饿会影响健康
        if self.hunger < 20:
            health_penalty = (20 - self.hunger) * 0.25 * days_passed  # 0.05 * 5 = 0.25
            self.health = max(0, self.health - health_penalty)
        
        # 清洁度低会影响健康
        if self.cleanliness < 30:
            health_penalty = (30 - self.cleanliness) * 0.15 * days_passed  # 0.03 * 5 = 0.15
            self.health = max(0, self.health - health_penalty)
        
        # 快乐度低会影响健康
        if self.happiness < 20:
            health_penalty = (20 - self.happiness) * 0.1 * days_passed  # 0.02 * 5 = 0.1
            self.health = max(0, self.health - health_penalty)
        
        # 健康恢复
        if self.health < 100 and self.hunger > 50 and self.happiness > 50:
            self.health = min(100, self.health + 0.5 * days_passed)  # 0.1 * 5 = 0.5
        
        # 检查经验增长和升级
        self.check_level_up()
        
        # 更新最后更新时间
        self.last_update_time = time.time()
        
        return None
    
    def add_experience(self, amount):
        """增加经验值"""
        self.experience += amount
        self.check_level_up()
    
    def check_level_up(self):
        """检查是否升级"""
        # 计算升级所需经验 (随等级增加)
        required_exp = self.level * 100
        
        if self.experience >= required_exp:
            self.level += 1
            self.experience -= required_exp
            
            # 升级奖励
            self.hunger = min(100, self.hunger + 20)
            self.happiness = min(100, self.happiness + 20)
            self.health = min(100, self.health + 20)
            self.cleanliness = min(100, self.cleanliness + 20)
            self.energy = min(100, self.energy + 20)
            
            return f"{self.name}升级了！现在是{self.level}级了！"
        
        return None
    
    def feed(self, food_type="普通狗粮"):
        """喂食"""
        if self.is_sleeping:
            return f"{self.name}正在睡觉，不能喂食。"
        
        # 能量太低无法进食
        if self.energy < 10:
            return f"{self.name}太累了，没力气吃东西。"
        
        food_values = {
            "普通狗粮": {"hunger": 20, "happiness": 5, "health": 5, "exp": 10},
            "高级狗粮": {"hunger": 30, "happiness": 10, "health": 15, "exp": 15},
            "狗狗零食": {"hunger": 10, "happiness": 15, "health": 0, "exp": 5},
            "鸡肉": {"hunger": 25, "happiness": 20, "health": 10, "exp": 20},
            "牛肉": {"hunger": 35, "happiness": 25, "health": 15, "exp": 25}
        }
        
        if food_type not in food_values:
            food_type = "普通狗粮"
        
        values = food_values[food_type]
        
        # 如果已经吃饱了
        if self.hunger >= 95:
            return f"{self.name}已经吃饱了，不想再吃了。"
        
        # 增加属性
        self.hunger = min(100, self.hunger + values["hunger"])
        self.happiness = min(100, self.happiness + values["happiness"])
        self.health = min(100, self.health + values["health"])
        self.energy = max(0, self.energy - 5)  # 吃饭消耗一点能量
        
        # 增加经验
        self.add_experience(values["exp"])
        
        return f"{self.name}吃了{food_type}，看起来很满足！"
    
    def play(self, game_type="普通玩耍"):
        """玩耍"""
        if self.is_sleeping:
            return f"{self.name}正在睡觉，不能玩耍。"
        
        # 能量检查
        if self.energy < 20:
            return f"{self.name}太累了，不想玩了。"
        
        # 饥饿检查
        if self.hunger < 20:
            return f"{self.name}太饿了，没心情玩。"
        
        game_values = {
            "普通玩耍": {"happiness": 20, "energy": 15, "hunger": 10, "exp": 15},
            "接飞盘": {"happiness": 25, "energy": 25, "hunger": 15, "exp": 25},
            "追球": {"happiness": 30, "energy": 30, "hunger": 20, "exp": 20},
            "拔河": {"happiness": 35, "energy": 35, "hunger": 20, "exp": 30},
            "智力游戏": {"happiness": 25, "energy": 15, "hunger": 10, "exp": 35}
        }
        
        if game_type not in game_values:
            game_type = "普通玩耍"
        
        values = game_values[game_type]
        
        # 更新属性
        self.happiness = min(100, self.happiness + values["happiness"])
        self.energy = max(0, self.energy - values["energy"])
        self.hunger = max(0, self.hunger - values["hunger"])
        self.cleanliness = max(0, self.cleanliness - 5)  # 玩耍会变脏
        
        # 增加经验
        self.add_experience(values["exp"])
        
        # 技能相关
        skill_message = ""
        if game_type in self.skills:
            # 已有技能练习可能会提升熟练度
            skill_level = self.skills[game_type]
            if skill_level < 5 and random.random() < 0.3:  # 30%几率提升
                self.skills[game_type] += 1
                skill_message = f"，{game_type}技能提升到了{self.skills[game_type]}级！"
        
        return f"{self.name}和你玩了{game_type}，非常开心{skill_message}"
    
    def bath(self):
        """洗澡"""
        if self.is_sleeping:
            return f"{self.name}正在睡觉，不能洗澡。"
        
        # 能量检查
        if self.energy < 10:
            return f"{self.name}太累了，没精力洗澡。"
        
        # 如果已经很干净
        if self.cleanliness >= 90:
            return f"{self.name}已经很干净了，不需要洗澡。"
        
        # 有些狗不喜欢洗澡
        happiness_change = -10 if random.random() < 0.3 else 10
        
        # 更新属性
        self.cleanliness = 100
        self.happiness = max(0, min(100, self.happiness + happiness_change))
        self.energy = max(0, self.energy - 10)
        
        # 增加经验
        self.add_experience(10)
        
        if happiness_change < 0:
            return f"{self.name}洗完澡了，虽然不太喜欢洗澡的过程，但现在很干净了！"
        else:
            return f"{self.name}洗完澡了，看起来很享受，现在非常干净！"
    
    def sleep(self, hours=8):
        """睡觉"""
        if self.is_sleeping:
            return f"{self.name}已经在睡觉了。"
        
        # 如果不累
        if self.energy > 80:
            return f"{self.name}现在精力充沛，不想睡觉。"
        
        # 设置睡眠状态
        self.is_sleeping = True
        self.sleep_until = time.time() + hours * 3600  # 小时转换为秒
        
        return f"{self.name}开始睡觉了，预计{hours}小时后醒来。"
    
    def train(self, skill):
        """训练技能"""
        if self.is_sleeping:
            return f"{self.name}正在睡觉，不能训练。"
        
        # 能量和饥饿检查
        if self.energy < 30:
            return f"{self.name}太累了，没精力训练。"
        
        if self.hunger < 30:
            return f"{self.name}太饿了，没心情训练。"
        
        if self.happiness < 30:
            return f"{self.name}心情不好，不想训练。"
        
        # 允许训练的技能列表
        allowed_skills = ["坐下", "握手", "打滚", "接飞盘", "捡球", "原地等待"]
        
        if skill not in allowed_skills:
            return f"不能教{self.name}这个技能，请选择基本技能。"
        
        # 检查是否已有此技能
        if skill in self.skills:
            current_level = self.skills[skill]
            if current_level >= 5:  # 技能等级上限
                return f"{self.name}的{skill}技能已经达到最高级了！"
            
            # 训练成功率根据当前等级调整
            success_rate = 0.8 - (current_level - 1) * 0.1  # 等级越高越难提升
            
            if random.random() < success_rate:
                self.skills[skill] += 1
                
                # 更新属性
                self.energy = max(0, self.energy - 20)
                self.hunger = max(0, self.hunger - 10)
                self.happiness = max(0, min(100, self.happiness + 10))
                
                # 增加经验
                self.add_experience(25)
                
                return f"{self.name}的{skill}技能提升到了{self.skills[skill]}级！"
            else:
                # 训练失败也会消耗
                self.energy = max(0, self.energy - 15)
                self.hunger = max(0, self.hunger - 5)
                
                return f"{self.name}尝试学习{skill}，但这次没有进步。"
        else:
            # 学习新技能
            success_rate = 0.7  # 新技能基础学习成功率
            
            # 根据狗的等级提高成功率
            success_rate += min(0.2, (self.level - 1) * 0.05)
            
            if random.random() < success_rate:
                self.skills[skill] = 1
                
                # 更新属性
                self.energy = max(0, self.energy - 25)
                self.hunger = max(0, self.hunger - 15)
                self.happiness = max(0, min(100, self.happiness + 15))
                
                # 增加经验
                self.add_experience(50)
                
                return f"{self.name}学会了新技能：{skill}！"
            else:
                # 学习失败
                self.energy = max(0, self.energy - 20)
                self.hunger = max(0, self.hunger - 10)
                
                return f"{self.name}还没有理解{skill}是什么，需要更多训练。"
    
    def pet(self):
        """抚摸"""
        if self.is_sleeping:
            return f"{self.name}正在睡觉，轻轻抚摸了一下，它看起来很安心。"
        
        # 增加快乐值
        happiness_increase = 10
        if self.personality == "粘人":
            happiness_increase = 15
        elif self.personality == "独立":
            happiness_increase = 5
        
        self.happiness = min(100, self.happiness + happiness_increase)
        
        # 增加经验
        self.add_experience(5)
        
        if self.personality == "粘人":
            return f"{self.name}非常享受你的抚摸，蹭来蹭去，尾巴摇个不停！"
        elif self.personality == "独立":
            return f"{self.name}接受了你的抚摸，但保持着一定的距离。"
        else:
            return f"{self.name}开心地享受着你的抚摸，尾巴轻轻摇摆。"
    
    def update_growth_stage(self):
        """根据年龄更新成长阶段，返回是否有变化"""
        old_stage = self.growth_stage
        
        # 根据年龄确定成长阶段
        if self.age < 30:  # 30天内为幼犬
            new_stage = 0
        elif self.age < 180:  # 6个月内为青年期
            new_stage = 1
        elif self.age < 1095:  # 3年内为成年期
            new_stage = 2
        else:  # 3年以上为老年期
            new_stage = 3
        
        # 如果成长阶段有变化
        if new_stage != old_stage:
            self.growth_stage = new_stage
            
            # 成长阶段变化带来的属性调整
            if new_stage == 1:  # 进入青年期
                self.energy = min(100, self.energy + 10)
                self.health = min(100, self.health + 5)
            elif new_stage == 2:  # 进入成年期
                self.energy = min(100, self.energy + 5)
                self.health = min(100, self.health + 10)
            elif new_stage == 3:  # 进入老年期
                self.energy = max(30, self.energy - 20)
                self.happiness = min(100, self.happiness + 10)
            
            return True
        
        return False
    
    def get_status(self):
        """获取当前状态"""
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
            "level": self.level,
            "experience": self.experience,
            "skills": self.skills,
            "is_sleeping": self.is_sleeping,
            "appearance": self.appearance,
            "growth_stage": self.growth_stage,
            "affection": self.affection
        }