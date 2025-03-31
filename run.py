from app import app, socketio

if __name__ == "__main__":
    print("启动AI宠物狗应用...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 