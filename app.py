from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

ROOM = 'watch_party'
users = {}
host_sid = None

MOVIE_FOLDER = 'movies'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/movie/<filename>')
def stream_movie(filename):
    return send_from_directory(MOVIE_FOLDER, filename)

@socketio.on('join')
def handle_join(data):
    global host_sid
    username = data.get('username', 'Guest')
    sid = request.sid
    is_host = False

    if not host_sid:
        is_host = True
        host_sid = sid

    users[sid] = {'username': username, 'is_host': is_host}
    join_room(ROOM)
    emit('user_list', users, room=ROOM)

    if is_host:
        emit('host_assigned', {'sid': sid}, room=sid)

@socketio.on('chat')
def handle_chat(data):
    user = users.get(request.sid, {})
    message = {'username': user.get('username', 'Unknown'), 'message': data['message']}
    emit('chat', message, room=ROOM)

@socketio.on('play')
def handle_play(data):
    if users.get(request.sid, {}).get('is_host'):
        emit('play', data, room=ROOM)

@socketio.on('pause')
def handle_pause(data):
    if users.get(request.sid, {}).get('is_host'):
        emit('pause', data, room=ROOM)

@socketio.on('load_video')
def handle_load_video(data):
    if users.get(request.sid, {}).get('is_host'):
        filename = data.get('filename')
        video_url = f"/movie/{filename}"
        emit('load_video', {'url': video_url}, room=ROOM)

@socketio.on('remove_user')
def handle_remove_user(data):
    if users.get(request.sid, {}).get('is_host'):
        sid = data.get('sid')
        if sid in users:
            emit('kicked', {}, room=sid)
            leave_room(ROOM, sid=sid)
            users.pop(sid)
            emit('user_list', users, room=ROOM)

@socketio.on('disconnect')
def handle_disconnect():
    global host_sid
    sid = request.sid
    was_host = users.get(sid, {}).get('is_host')
    users.pop(sid, None)

    if was_host and users:
        new_host_sid = next(iter(users))
        users[new_host_sid]['is_host'] = True
        host_sid = new_host_sid
        emit('host_assigned', {'sid': new_host_sid}, room=new_host_sid)
    elif not users:
        host_sid = None

    emit('user_list', users, room=ROOM)

if __name__ == '__main__':
    os.makedirs(MOVIE_FOLDER, exist_ok=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
