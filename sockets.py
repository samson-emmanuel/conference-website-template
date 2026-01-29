from flask_socketio import SocketIO, emit

socketio = SocketIO()

def init_app(app):
    socketio.init_app(app, cors_allowed_origins="*", message_queue=app.config.get('SOCKETIO_MESSAGE_QUEUE'))


@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('update_data')
def handle_update_data(data):
    """
    Receives updated data from a client and broadcasts it to all clients.
    """
    emit('data_updated', data, broadcast=True)
