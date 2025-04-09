from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from dog import Dog
import json
import os
import time
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai_pet_dog_secret'
socketio = SocketIO(app)

# 存储所有在线宠物
pets = {}
# 数据保存路径
SAVE_DIR = os.path.join(os.path.dirname(__file__), "data/saves/web")
os.makedirs(SAVE_DIR, exist_ok=True)

# 环境状态
environment_state = {
    "weather": "sunny",  # sunny, rainy, cloudy, snowy
    "season": "spring",  # spring, summer, autumn, winter
    "toys": [],
    "is_day": True,
    "hour": 8,
    "minute": 0,
    "day": 0
}

def save_pet_data(pet_id, dog):
    """保存宠物数据到文件"""
    save_path = os.path.join(SAVE_DIR, f"{pet_id}.json")
    with open(save_path, "w") as f:
        json.dump(dog.to_dict(), f, indent=4)

def load_pet_data(pet_id):
    """从文件加载宠物数据"""
    save_path = os.path.join(SAVE_DIR, f"{pet_id}.json")
    if os.path.exists(save_path):
        with open(save_path, "r") as f:
            dog_data = json.load(f)
        return Dog.from_dict(dog_data)
    return None

def save_environment_data():
    """保存环境数据到文件"""
    save_path = os.path.join(SAVE_DIR, "environment.json")
    with open(save_path, "w") as f:
        json.dump(environment_state, f, indent=4)

def load_environment_data():
    """从文件加载环境数据"""
    global environment_state
    save_path = os.path.join(SAVE_DIR, "environment.json")
    if os.path.exists(save_path):
        with open(save_path, "r") as f:
            environment_state = json.load(f)

# 尝试加载环境数据
try:
    load_environment_data()
except:
    print("无法加载环境数据，使用默认值")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/create_pet', methods=['POST'])
def create_pet():
    data = request.json
    name = data.get('name', '小狗')
    breed = data.get('breed', '柯基')
    personality = data.get('personality', '活泼')
    
    # 尝试加载已有宠物数据
    pet_id = name  # 简单起见，使用名字作为ID
    existing_dog = load_pet_data(pet_id)
    
    if existing_dog:
        dog = existing_dog
    else:
        dog = Dog(name, breed, personality)
    
    pets[pet_id] = dog
    save_pet_data(pet_id, dog)
    
    return jsonify({
        'status': 'success',
        'pet_id': pet_id,
        'pet_info': dog.get_status(),
        'environment': environment_state
    })

@app.route('/api/get_pet_status/<pet_id>')
def get_pet_status(pet_id):
    if pet_id not in pets:
        return jsonify({'status': 'error', 'message': '找不到宠物'})
    
    dog = pets[pet_id]
    return jsonify({
        'status': 'success',
        'pet_info': dog.get_status(),
        'environment': environment_state
    })

@app.route('/api/get_environment')
def get_environment():
    return jsonify({
        'status': 'success',
        'environment': environment_state
    })

@socketio.on('interact')
def handle_interaction(data):
    pet_id = data['pet_id']
    action = data['action']
    params = data.get('params', {})
    
    if pet_id not in pets and action != 'environment_action':
        emit('interaction_response', {'status': 'error', 'message': '找不到宠物'})
        return
    
    result = "操作完成"
    
    # 针对环境的操作
    if action == 'environment_action':
        env_action = params.get('env_action', '')
        if env_action.startswith('change_weather_'):
            weather = env_action.replace('change_weather_', '')
            environment_state['weather'] = weather
            result = f"天气变为{weather}"
        elif env_action.startswith('place_toy_'):
            toy_type = env_action.replace('place_toy_', '')
            position = params.get('position', {'x': random.randint(100, 700), 'y': random.randint(150, 350)})
            environment_state['toys'].append({
                'type': toy_type,
                'position': position
            })
            result = f"放置了{toy_type}玩具"
        elif env_action == 'remove_toy':
            toy_index = params.get('toy_index', -1)
            if toy_index >= 0 and toy_index < len(environment_state['toys']):
                removed_toy = environment_state['toys'].pop(toy_index)
                result = f"移除了{removed_toy['type']}玩具"
        
        save_environment_data()
        emit('environment_update', environment_state)
    # 针对宠物的操作
    else:
        dog = pets[pet_id]
        
        if action == 'feed':
            food_type = params.get('food_type', '普通狗粮')
            result = dog.feed(food_type)
        elif action == 'play':
            game_type = params.get('game_type', '普通玩耍')
            result = dog.play(game_type)
        elif action == 'clean':
            result = dog.bath()
        elif action == 'sleep':
            duration = params.get('duration', 8)
            result = dog.sleep(duration)
        elif action == 'train':
            skill = params.get('skill', '坐下')
            result = dog.train(skill)
        elif action == 'pet':
            result = dog.pet()
        elif action == 'voice_command':
            command = params.get('command', '')
            # 解析语音命令
            if command in ['坐下', '握手', '打滚', '接飞盘', '捡球', '原地等待']:
                # 如果是技能命令
                if command in dog.skills:
                    result = f"{dog.name}听到你的命令，表演了{command}！"
                    dog.happiness = min(100, dog.happiness + 5)
                else:
                    result = f"{dog.name}似乎不理解"{command}"命令，也许需要先训练这个技能？"
            elif '喂' in command or '吃' in command:
                result = dog.feed('普通狗粮')
            elif '玩' in command:
                result = dog.play('普通玩耍')
            elif '洗澡' in command or '清洁' in command:
                result = dog.bath()
            elif '睡' in command:
                result = dog.sleep(8)
            else:
                result = f"{dog.name}疑惑地看着你，似乎不理解你的命令。"
        elif action == 'minigame':
            game_type = params.get('game_type', 'fetch')
            game_result = params.get('result', {'score': 0})
            
            if game_type == 'fetch':
                score = game_result.get('score', 0)
                dog.happiness = min(100, dog.happiness + min(30, score * 2))
                dog.energy = max(0, dog.energy - min(40, 20 + score * 2))
                
                # 更新接飞盘技能
                if "接飞盘" in dog.skills:
                    current_level = dog.skills["接飞盘"]
                    if current_level < 5:  # 最高5级
                        new_level = min(5, current_level + score // 5)
                        if new_level > current_level:
                            dog.skills["接飞盘"] = new_level
                            result = f"{dog.name}的"接飞盘"技能提升到了Lv.{new_level}！"
                elif score >= 3:
                    dog.skills["接飞盘"] = 1
                    result = f"{dog.name}学会了"接飞盘"技能！"
            
            elif game_type == 'maze':
                score = game_result.get('score', 0)
                dog.happiness = min(100, dog.happiness + min(20, score))
                dog.energy = max(0, dog.energy - min(30, 15 + score))
                
                # 更新智力游戏技能
                if "智力游戏" in dog.skills:
                    current_level = dog.skills["智力游戏"]
                    if current_level < 5:
                        new_level = min(5, current_level + score // 10)
                        if new_level > current_level:
                            dog.skills["智力游戏"] = new_level
                            result = f"{dog.name}的"智力游戏"技能提升到了Lv.{new_level}！"
                elif score >= 5:
                    dog.skills["智力游戏"] = 1
                    result = f"{dog.name}学会了"智力游戏"技能！"
            
            elif game_type == 'race':
                score = game_result.get('score', 0)
                dog.happiness = min(100, dog.happiness + min(20, score // 5))
                dog.energy = max(0, dog.energy - min(30, 10 + score // 5))
                
                # 更新障碍跑技能
                if "障碍跑" in dog.skills:
                    current_level = dog.skills["障碍跑"]
                    if current_level < 5:
                        new_level = min(5, current_level + score // 20)
                        if new_level > current_level:
                            dog.skills["障碍跑"] = new_level
                            result = f"{dog.name}的"障碍跑"技能提升到了Lv.{new_level}！"
                elif score >= 10:
                    dog.skills["障碍跑"] = 1
                    result = f"{dog.name}学会了"障碍跑"技能！"
        
        # 保存宠物数据
        save_pet_data(pet_id, dog)
        
        emit('interaction_response', {
            'status': 'success',
            'message': result
        })
        
        emit('pet_update', {
            'pet_id': pet_id,
            'pet_info': dog.get_status(),
            'environment': environment_state
        })

# 定期更新宠物状态和环境的后台任务
def background_task():
    while True:
        current_time = time.time()
        
        # 更新时间
        environment_state["minute"] += 10
        if environment_state["minute"] >= 60:
            environment_state["hour"] += 1
            environment_state["minute"] = 0
            
            if environment_state["hour"] >= 24:
                environment_state["hour"] = 0
                environment_state["day"] += 1
                
                # 每4天更换一次季节
                if environment_state["day"] % 4 == 0:
                    seasons = ["spring", "summer", "autumn", "winter"]
                    current_index = seasons.index(environment_state["season"])
                    next_index = (current_index + 1) % 4
                    environment_state["season"] = seasons[next_index]
        
        # 白天/黑夜判断 (6:00-18:00为白天)
        environment_state["is_day"] = 6 <= environment_state["hour"] < 18
        
        # 随机更改天气 (每3小时有20%的概率)
        if environment_state["minute"] == 0 and environment_state["hour"] % 3 == 0 and random.random() < 0.2:
            weathers = ["sunny", "rainy", "cloudy", "snowy"]
            current_index = weathers.index(environment_state["weather"])
            # 排除当前天气
            possible_weathers = weathers[:current_index] + weathers[current_index+1:]
            # 在冬天增加下雪的概率
            if environment_state["season"] == "winter" and "snowy" in possible_weathers and random.random() < 0.5:
                environment_state["weather"] = "snowy"
            else:
                environment_state["weather"] = random.choice(possible_weathers)
        
        # 保存环境状态
        save_environment_data()
        
        # 更新所有宠物状态
        for pet_id, dog in pets.items():
            dog.update_status(60)  # 每分钟更新
            save_pet_data(pet_id, dog)
        
        # 广播更新
        socketio.emit('time_update', {
            'time': {
                'hour': environment_state["hour"],
                'minute': environment_state["minute"],
                'day': environment_state["day"],
                'is_day': environment_state["is_day"]
            }
        })
        
        socketio.emit('environment_update', environment_state)
        
        socketio.sleep(60)  # 每分钟更新一次

@socketio.on('connect')
def handle_connect():
    socketio.start_background_task(background_task)

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)