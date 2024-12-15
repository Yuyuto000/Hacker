from flask_socketio import SocketIO, join_room, leave_room, emit

socketio = SocketIO()

# ユーザーが接続したとき
@socketio.on('connect')
def handle_connect():
    print("ユーザーが接続しました。")

# メッセージの送信
@socketio.on('message')
def handle_message(data):
    room = data.get('room', '')
    message = data.get('message', '')
    if room:
        emit('message', {'message': message}, room=room)
    else:
        emit('message', {'message': message}, broadcast=True)

# ルームへの参加
@socketio.on('join')
def handle_join(data):
    room = data.get('room', '')
    if room:
        join_room(room)
        emit('status', {'message': f"{room} に参加しました。"}, room=room)

# ルームから退出
@socketio.on('leave')
def handle_leave(data):
    room = data.get('room', '')
    if room:
        leave_room(room)
        emit('status', {'message': f"{room} から退出しました。"}, room=room)

def init_chat(app):
    socketio.init_app(app)
    print("チャット機能が初期化されました。")
