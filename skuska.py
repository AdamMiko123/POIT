from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect    
import serial

ser = serial.Serial("/dev/ttyS2")
ser.baudrate = 9600

async_mode = None
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 
    
def background_thread(args):
    count = 0
    while True:
        read_ser = ser.readline()
        read_ser = read_ser.decode()
        if args:
            vyber = dict(args).get('Vyber')
            btnV = dict(args).get('btn_value')
        else:
            vyber = 1
            btnV = 'null'
        print (args) 
        socketio.sleep(1)
        count += 1
        read_ser_data = read_ser.split(" ")
        print(read_ser_data)
        if btnV == "start":
            socketio.emit('my_response',{'distance': float(read_ser_data[0]), 'humidity': float(read_ser_data[1]),
                                         'temperature': float(read_ser_data[2]), 'photo': float(read_ser_data[3]), 'count': count},
                          namespace='/test')  

@app.route('/', methods=['GET', 'POST'])
def skuska():
    return render_template('skuska.html', async_mode=socketio.async_mode)
  
@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['Vyber'] = message['value']  
    #emit('my_response', {'Distance': session['Distance'], 'Humidity': session['Humidity'], 'Temperature': session['Temperature'], 'Photo': session['Photo']})
 
@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    emit('my_response', {'data': 'Disconnected!'})
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('click_event', namespace='/test')
def db_message(message):   
    session['btn_value'] = message['value']    

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)