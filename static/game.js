let socket = io();
let petId = null;
let petStatus = {};
let environmentState = {
    weather: "sunny",
    season: "spring",
    toys: [],
    is_day: true,
    hour: 8,
    minute: 0,
    day: 0
};

// 声音识别
let recognition = null;
let isVoiceRecognitionActive = false;

let canvas = document.getElementById('pet-canvas');
let ctx = canvas.getContext('2d');

// 设置Canvas的实际尺寸
function resizeCanvas() {
    const container = canvas.parentElement;
    canvas.width = container.clientWidth;
    canvas.height = 400;
}

// 监听窗口大小变化
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// 创建宠物
async function createPet() {
    const petName = document.getElementById('petName').value || '小狗';
    const petBreed = document.getElementById('petBreed').value || '柯基';
    const petPersonality = document.getElementById('petPersonality').value || '活泼';

    try {
        const response = await fetch('/api/create_pet', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: petName,
                breed: petBreed,
                personality: petPersonality
            })
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            petId = data.pet_id;
            petStatus = data.pet_info;
            environmentState = data.environment;
            document.getElementById('creation-form').style.display = 'none';
            document.getElementById('pet-container').style.display = 'block';
            updateStatusBars();
            updateEnvironmentDisplay();
            setupVoiceRecognition();
            startGameLoop();
        }
    } catch (error) {
        console.error('创建宠物失败:', error);
    }
}

// 更新状态栏
function updateStatusBars() {
    document.getElementById('hunger-bar').style.width = `${petStatus.hunger}%`;
    document.getElementById('happiness-bar').style.width = `${petStatus.happiness}%`;
    document.getElementById('health-bar').style.width = `${petStatus.health}%`;
    document.getElementById('cleanliness-bar').style.width = `${petStatus.cleanliness}%`;
    document.getElementById('energy-bar').style.width = `${petStatus.energy}%`;
    
    // 更新年龄和等级信息
    document.getElementById('pet-age').textContent = `年龄: ${petStatus.age}天`;
    document.getElementById('pet-level').textContent = `等级: ${petStatus.level}`;
    
    // 更新技能列表
    const skillsList = document.getElementById('skills-list');
    skillsList.innerHTML = '';
    
    for (const [skill, level] of Object.entries(petStatus.skills)) {
        const skillItem = document.createElement('li');
        skillItem.textContent = `${skill} Lv.${level}`;
        skillsList.appendChild(skillItem);
    }
    
    // 根据状态更新宠物外观
    updatePetAppearance();
}

// 更新宠物外观
function updatePetAppearance() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 绘制宠物
    drawPet(ctx);
}

// 绘制宠物
function drawPet(ctx) {
    const centerX = 200;
    const centerY = 200;
    
    // 绘制身体 (根据品种调整)
    ctx.fillStyle = petStatus.appearance.body_color || '#A0522D';
    
    // 柯基特有的扁平身体
    if (petStatus.breed === '柯基') {
        ctx.beginPath();
        ctx.ellipse(centerX, centerY + 20, 60, 40, 0, 0, Math.PI * 2);
        ctx.fill();
        
        // 短腿
        for (let i = -1; i <= 1; i+=2) {
            for (let j = -1; j <= 1; j+=2) {
                ctx.beginPath();
                ctx.ellipse(centerX + i * 40, centerY + 40 + j * 10, 10, 15, 0, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    } else {
        // 其他犬种
        ctx.beginPath();
        ctx.ellipse(centerX, centerY, 50, 60, 0, 0, Math.PI * 2);
        ctx.fill();
        
        // 腿
        for (let i = -1; i <= 1; i+=2) {
            for (let j = -1; j <= 1; j+=2) {
                ctx.beginPath();
                ctx.ellipse(centerX + i * 30, centerY + 50 + j * 5, 10, 30, 0, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }
    
    // 头
    ctx.fillStyle = petStatus.appearance.body_color || '#A0522D';
    ctx.beginPath();
    ctx.arc(centerX, centerY - 50, 40, 0, Math.PI * 2);
    ctx.fill();
    
    // 耳朵 (根据品种调整)
    ctx.fillStyle = petStatus.appearance.ear_color || '#8B4513';
    if (petStatus.breed === '柯基') {
        // 三角形耳朵
        for (let i = -1; i <= 1; i+=2) {
            ctx.beginPath();
            ctx.moveTo(centerX + i * 20, centerY - 70);
            ctx.lineTo(centerX + i * 45, centerY - 95);
            ctx.lineTo(centerX + i * 40, centerY - 60);
            ctx.fill();
        }
    } else {
        // 圆形耳朵
        for (let i = -1; i <= 1; i+=2) {
            ctx.beginPath();
            ctx.ellipse(centerX + i * 30, centerY - 80, 20, 30, 0, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    
    // 眼睛
    ctx.fillStyle = '#000000';
    for (let i = -1; i <= 1; i+=2) {
        ctx.beginPath();
        ctx.arc(centerX + i * 15, centerY - 55, 5, 0, Math.PI * 2);
        ctx.fill();
    }
    
    // 鼻子
    ctx.fillStyle = '#000000';
    ctx.beginPath();
    ctx.ellipse(centerX, centerY - 40, 10, 5, 0, 0, Math.PI * 2);
    ctx.fill();
    
    // 嘴巴
    ctx.strokeStyle = '#000000';
    ctx.beginPath();
    ctx.moveTo(centerX, centerY - 35);
    ctx.lineTo(centerX, centerY - 30);
    ctx.stroke();
    
    ctx.beginPath();
    ctx.moveTo(centerX, centerY - 30);
    ctx.bezierCurveTo(centerX - 10, centerY - 25, centerX + 10, centerY - 25, centerX, centerY - 30);
    ctx.stroke();
    
    // 尾巴
    ctx.fillStyle = petStatus.appearance.body_color || '#A0522D';
    ctx.beginPath();
    
    if (petStatus.breed === '柯基') {
        // 柯基短尾巴
        ctx.ellipse(centerX + 65, centerY, 10, 15, Math.PI / 4, 0, Math.PI * 2);
    } else {
        // 普通尾巴
        ctx.ellipse(centerX + 65, centerY - 20, 10, 40, Math.PI / 4, 0, Math.PI * 2);
    }
    ctx.fill();
    
    // 表情 (根据心情状态)
    if (petStatus.happiness > 80) {
        // 高兴表情 - 微笑的眼睛
        ctx.strokeStyle = '#000000';
        for (let i = -1; i <= 1; i+=2) {
            ctx.beginPath();
            ctx.arc(centerX + i * 15, centerY - 55, 10, Math.PI / 10, Math.PI - Math.PI / 10, true);
            ctx.stroke();
        }
    } else if (petStatus.happiness < 30) {
        // 低落的表情 - 伤心的眼睛
        ctx.strokeStyle = '#0000FF';
        for (let i = -1; i <= 1; i+=2) {
            ctx.beginPath();
            ctx.moveTo(centerX + i * 10, centerY - 45);
            ctx.lineTo(centerX + i * 20, centerY - 45);
            ctx.stroke();
        }
        
        // 泪滴
        ctx.fillStyle = '#0000FF';
        ctx.beginPath();
        ctx.arc(centerX - 20, centerY - 40, 3, 0, Math.PI * 2);
        ctx.fill();
    }
}

// 与宠物互动
function interact(action, params = {}) {
    if (!petId) return;
    
    socket.emit('interact', {
        pet_id: petId,
        action: action,
        params: params
    });
}

// 与环境互动
function environmentAction(envAction, params = {}) {
    socket.emit('interact', {
        pet_id: petId || 'global',
        action: 'environment_action',
        params: {
            env_action: envAction,
            ...params
        }
    });
}

// 定期更新宠物状态
function updateStatus() {
    if (!petId) return;
    
    fetch(`/api/get_pet_status/${petId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                petStatus = data.pet_info;
                environmentState = data.environment;
                updateStatusBars();
                updateEnvironmentDisplay();
            }
        })
        .catch(error => console.error('Error:', error));
}

// 更新环境显示
function updateEnvironmentDisplay() {
    // 更新时钟
    const clockElement = document.getElementById('clock');
    const timeString = `${String(environmentState.hour).padStart(2, '0')}:${String(environmentState.minute).padStart(2, '0')}`;
    clockElement.textContent = timeString;
    
    // 更新天气和季节显示
    const weatherElement = document.getElementById('weather');
    const seasonElement = document.getElementById('season');
    
    const weatherMap = {
        'sunny': '晴天 ☀️',
        'rainy': '雨天 🌧️',
        'cloudy': '多云 ☁️',
        'snowy': '雪天 ❄️'
    };
    
    const seasonMap = {
        'spring': '春季 🌱',
        'summer': '夏季 ☀️',
        'autumn': '秋季 🍂',
        'winter': '冬季 ❄️'
    };
    
    weatherElement.textContent = weatherMap[environmentState.weather] || environmentState.weather;
    seasonElement.textContent = seasonMap[environmentState.season] || environmentState.season;
    
    // 更新白天/黑夜背景
    const container = document.getElementById('pet-container');
    if (environmentState.is_day) {
        container.classList.remove('night');
        container.classList.add('day');
    } else {
        container.classList.remove('day');
        container.classList.add('night');
    }
    
    // 更新季节背景色
    container.classList.remove('spring', 'summer', 'autumn', 'winter');
    container.classList.add(environmentState.season);
    
    // 更新天气效果
    const weatherEffects = document.getElementById('weather-effects');
    weatherEffects.innerHTML = '';
    
    if (environmentState.weather === 'rainy') {
        for (let i = 0; i < 20; i++) {
            const raindrop = document.createElement('div');
            raindrop.className = 'raindrop';
            raindrop.style.left = `${Math.random() * 100}%`;
            raindrop.style.animationDuration = `${0.5 + Math.random() * 0.5}s`;
            raindrop.style.animationDelay = `${Math.random() * 0.5}s`;
            weatherEffects.appendChild(raindrop);
        }
    } else if (environmentState.weather === 'snowy') {
        for (let i = 0; i < 30; i++) {
            const snowflake = document.createElement('div');
            snowflake.className = 'snowflake';
            snowflake.style.left = `${Math.random() * 100}%`;
            snowflake.style.animationDuration = `${3 + Math.random() * 5}s`;
            snowflake.style.animationDelay = `${Math.random() * 2}s`;
            weatherEffects.appendChild(snowflake);
        }
    } else if (environmentState.weather === 'cloudy') {
        for (let i = 0; i < 5; i++) {
            const cloud = document.createElement('div');
            cloud.className = 'cloud';
            cloud.style.top = `${10 + Math.random() * 20}%`;
            cloud.style.left = `${Math.random() * 100}%`;
            cloud.style.animationDuration = `${60 + Math.random() * 60}s`;
            weatherEffects.appendChild(cloud);
        }
    }
    
    // 更新玩具显示
    renderToys();
}

// 渲染玩具
function renderToys() {
    const toysContainer = document.getElementById('toys-container');
    toysContainer.innerHTML = '';
    
    environmentState.toys.forEach((toy, index) => {
        const toyElement = document.createElement('div');
        toyElement.className = 'toy';
        toyElement.dataset.index = index;
        
        // 设置玩具图标
        let toyIcon = '🎾'; // 默认为球
        if (toy.type === 'ball') toyIcon = '🏀';
        else if (toy.type === 'frisbee') toyIcon = '🥏';
        else if (toy.type === 'bone') toyIcon = '🦴';
        else if (toy.type === 'rope') toyIcon = '➰';
        
        toyElement.textContent = toyIcon;
        toyElement.style.left = `${toy.position.x}px`;
        toyElement.style.top = `${toy.position.y}px`;
        
        // 添加交互事件
        toyElement.addEventListener('click', () => {
            const toyMenu = document.createElement('div');
            toyMenu.className = 'toy-menu';
            toyMenu.style.left = `${toy.position.x + 20}px`;
            toyMenu.style.top = `${toy.position.y}px`;
            
            const playButton = document.createElement('button');
            playButton.textContent = '玩耍';
            playButton.addEventListener('click', () => {
                interact('play', { game_type: toy.type });
                toyMenu.remove();
            });
            
            const removeButton = document.createElement('button');
            removeButton.textContent = '移除';
            removeButton.addEventListener('click', () => {
                environmentAction('remove_toy', { toy_index: index });
                toyMenu.remove();
            });
            
            toyMenu.appendChild(playButton);
            toyMenu.appendChild(removeButton);
            document.body.appendChild(toyMenu);
            
            // 点击其他地方关闭菜单
            document.addEventListener('click', function closeMenu(e) {
                if (!toyMenu.contains(e.target) && e.target !== toyElement) {
                    toyMenu.remove();
                    document.removeEventListener('click', closeMenu);
                }
            });
        });
        
        toysContainer.appendChild(toyElement);
    });
}

// 打开环境菜单
function openEnvironmentMenu() {
    const envMenu = document.getElementById('environment-menu');
    envMenu.style.display = 'block';
}

// 关闭环境菜单
function closeEnvironmentMenu() {
    const envMenu = document.getElementById('environment-menu');
    envMenu.style.display = 'none';
}

// 改变天气
function changeWeather(weather) {
    environmentAction(`change_weather_${weather}`);
    closeEnvironmentMenu();
}

// 放置玩具
function placeToy(toyType) {
    // 随机位置或者让用户点击选择位置
    const x = 100 + Math.random() * 600;
    const y = 150 + Math.random() * 200;
    
    environmentAction(`place_toy_${toyType}`, {
        position: { x, y }
    });
    
    closeEnvironmentMenu();
}

// 迷你游戏 - 接飞盘
function startFetchGame() {
    const gameArea = document.getElementById('game-area');
    gameArea.innerHTML = '';
    gameArea.style.display = 'block';
    
    const title = document.createElement('h2');
    title.textContent = '接飞盘游戏';
    
    const scoreDisplay = document.createElement('div');
    scoreDisplay.id = 'game-score';
    scoreDisplay.textContent = '得分: 0';
    
    const gameCanvas = document.createElement('canvas');
    gameCanvas.id = 'fetch-canvas';
    gameCanvas.width = 800;
    gameCanvas.height = 400;
    
    const closeButton = document.createElement('button');
    closeButton.textContent = '退出游戏';
    closeButton.addEventListener('click', () => {
        gameArea.style.display = 'none';
        
        // 发送游戏结果
        const score = parseInt(scoreDisplay.textContent.split(': ')[1]);
        interact('minigame', { 
            game_type: 'fetch',
            result: { score }
        });
    });
    
    gameArea.appendChild(title);
    gameArea.appendChild(scoreDisplay);
    gameArea.appendChild(gameCanvas);
    gameArea.appendChild(closeButton);
    
    // 游戏状态
    let score = 0;
    let frisbeeX = 50;
    let frisbeeY = 200;
    let frisbeeSpeedX = 0;
    let frisbeeSpeedY = 0;
    let dogX = 700;
    let dogY = 300;
    let isThrown = false;
    
    const ctx = gameCanvas.getContext('2d');
    
    // 绘制场景
    function drawGame() {
        // 清空画布
        ctx.clearRect(0, 0, gameCanvas.width, gameCanvas.height);
        
        // 绘制背景
        ctx.fillStyle = '#87CEEB';
        ctx.fillRect(0, 0, gameCanvas.width, 150);
        ctx.fillStyle = '#7CFC00';
        ctx.fillRect(0, 150, gameCanvas.width, gameCanvas.height - 150);
        
        // 绘制飞盘
        ctx.fillStyle = '#FF4500';
        ctx.beginPath();
        ctx.arc(frisbeeX, frisbeeY, 20, 0, Math.PI * 2);
        ctx.fill();
        
        // 绘制宠物
        ctx.fillStyle = petStatus.appearance.body_color || '#A0522D';
        ctx.beginPath();
        ctx.ellipse(dogX, dogY, 40, 25, 0, 0, Math.PI * 2);
        ctx.fill();
        
        // 头
        ctx.beginPath();
        ctx.arc(dogX - 50, dogY - 10, 25, 0, Math.PI * 2);
        ctx.fill();
        
        // 眼睛
        ctx.fillStyle = '#000000';
        ctx.beginPath();
        ctx.arc(dogX - 60, dogY - 15, 3, 0, Math.PI * 2);
        ctx.fill();
        
        // 更新游戏状态
        if (isThrown) {
            frisbeeX += frisbeeSpeedX;
            frisbeeY += frisbeeSpeedY;
            frisbeeSpeedY += 0.2; // 重力
            
            // 移动宠物跟随飞盘
            const targetX = frisbeeX + 50;
            dogX = dogX + (targetX - dogX) * 0.05;
            
            // 检测接住飞盘
            const distance = Math.sqrt(Math.pow(frisbeeX - (dogX - 50), 2) + Math.pow(frisbeeY - dogY, 2));
            if (distance < 40) {
                score++;
                scoreDisplay.textContent = `得分: ${score}`;
                resetFrisbee();
            }
            
            // 飞盘落地
            if (frisbeeY > 380) {
                resetFrisbee();
            }
            
            // 飞盘出界
            if (frisbeeX < 0 || frisbeeX > gameCanvas.width) {
                resetFrisbee();
            }
        }
        
        requestAnimationFrame(drawGame);
    }
    
    // 重置飞盘位置
    function resetFrisbee() {
        frisbeeX = 50;
        frisbeeY = 200;
        frisbeeSpeedX = 0;
        frisbeeSpeedY = 0;
        isThrown = false;
    }
    
    // 添加事件监听器
    gameCanvas.addEventListener('mousedown', (e) => {
        if (!isThrown) {
            const rect = gameCanvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            
            frisbeeX = mouseX;
            frisbeeY = mouseY;
        }
    });
    
    gameCanvas.addEventListener('mousemove', (e) => {
        if (!isThrown && e.buttons === 1) {
            const rect = gameCanvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            
            frisbeeX = mouseX;
            frisbeeY = mouseY;
        }
    });
    
    gameCanvas.addEventListener('mouseup', (e) => {
        if (!isThrown) {
            const rect = gameCanvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            
            frisbeeSpeedX = (mouseX - frisbeeX) * 0.1;
            frisbeeSpeedY = (mouseY - frisbeeY) * 0.1;
            isThrown = true;
        }
    });
    
    drawGame();
}

// 设置语音识别
function setupVoiceRecognition() {
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'zh-CN';
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            const messageLog = document.getElementById('message-log');
            
            // 添加语音输入到消息日志
            const messageElement = document.createElement('div');
            messageElement.className = 'message voice-message';
            messageElement.textContent = `你说: ${transcript}`;
            messageLog.appendChild(messageElement);
            messageLog.scrollTop = messageLog.scrollHeight;
            
            // 发送语音命令到服务器
            interact('voice_command', { command: transcript });
        };
        
        recognition.onerror = function(event) {
            console.error('语音识别错误:', event.error);
            toggleVoiceRecognition(); // 出错时停止识别
        };
        
        recognition.onend = function() {
            if (isVoiceRecognitionActive) {
                recognition.start(); // 如果仍然处于激活状态，重新开始识别
            }
        };
    } else {
        alert('你的浏览器不支持语音识别功能，请使用Chrome浏览器。');
    }
}

// 切换语音识别
function toggleVoiceRecognition() {
    if (!recognition) {
        alert('你的浏览器不支持语音识别功能，请使用Chrome浏览器。');
        return;
    }
    
    const voiceButton = document.getElementById('voice-button');
    
    if (isVoiceRecognitionActive) {
        recognition.stop();
        isVoiceRecognitionActive = false;
        voiceButton.textContent = '开启语音识别';
        voiceButton.classList.remove('active');
    } else {
        recognition.start();
        isVoiceRecognitionActive = true;
        voiceButton.textContent = '关闭语音识别';
        voiceButton.classList.add('active');
    }
}

// 开始游戏循环
function startGameLoop() {
    setInterval(updateStatus, 10000); // 每10秒更新一次状态
}

// 添加服务器更新和交互响应的监听器
socket.on('pet_update', function(data) {
    if (data.pet_id === petId) {
        petStatus = data.pet_info;
        environmentState = data.environment;
        updateStatusBars();
        updateEnvironmentDisplay();
    }
});

socket.on('interaction_response', function(data) {
    const messageLog = document.getElementById('message-log');
    const messageElement = document.createElement('div');
    messageElement.className = 'message response-message';
    messageElement.textContent = data.message;
    messageLog.appendChild(messageElement);
    messageLog.scrollTop = messageLog.scrollHeight;
});

socket.on('environment_update', function(data) {
    environmentState = data;
    updateEnvironmentDisplay();
});

socket.on('time_update', function(data) {
    environmentState.hour = data.time.hour;
    environmentState.minute = data.time.minute;
    environmentState.day = data.time.day;
    environmentState.is_day = data.time.is_day;
    updateEnvironmentDisplay();
});

// 事件监听器
document.addEventListener('DOMContentLoaded', function() {
    // 绑定按钮事件
    document.getElementById('create-pet-button').addEventListener('click', createPet);
    
    // 添加互动按钮的事件监听器
    document.querySelectorAll('.action-button').forEach(button => {
        button.addEventListener('click', function() {
            const action = this.dataset.action;
            
            switch(action) {
                case 'feed':
                    interact('feed');
                    break;
                case 'play':
                    interact('play');
                    break;
                case 'clean':
                    interact('clean');
                    break;
                case 'sleep':
                    interact('sleep');
                    break;
                case 'train':
                    const skillInput = prompt('请输入要训练的技能:', '坐下');
                    if (skillInput) {
                        interact('train', { skill: skillInput });
                    }
                    break;
                case 'pet':
                    interact('pet');
                    break;
                case 'environment':
                    openEnvironmentMenu();
                    break;
                case 'toggle_voice':
                    toggleVoiceRecognition();
                    break;
                case 'minigame_fetch':
                    startFetchGame();
                    break;
            }
        });
    });
    
    // 环境菜单事件
    document.querySelectorAll('.weather-button').forEach(button => {
        button.addEventListener('click', function() {
            changeWeather(this.dataset.weather);
        });
    });
    
    document.querySelectorAll('.toy-button').forEach(button => {
        button.addEventListener('click', function() {
            placeToy(this.dataset.toy);
        });
    });
    
    document.getElementById('close-env-menu').addEventListener('click', closeEnvironmentMenu);
});