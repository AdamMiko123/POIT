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
        read_ser_data[3] = read_ser_data[3].replace("\r\n","")
        print(read_ser_data)
        if btnV == "Start":
            socketio.emit('my_response',{'distance': float(read_ser_data[0]), 'humidity': float(read_ser_data[1]),
                                         'temperature': float(read_ser_data[2]), 'photo': float(read_ser_data[3]), 'count': count},
                          namespace='/test')  

@app.route('/', methods=['GET', 'POST'])
def skuska():
    return render_template('skuska.html', async_mode=socketio.async_mode)

@socketio.on('click_event', namespace='/test')
def click_event(message):   
    session['btn_value'] = message['value'] 

@socketio.on('my_event', namespace='/test')
def my_event(message):   
    session['Vyber'] = message['value']  
    #emit('my_response', {'Distance': session['Distance'], 'Humidity': session['Humidity'], 'Temperature': session['Temperature'], 'Photo': session['Photo']})
 
@socketio.on('close', namespace='/test')
def close():
    emit('my_response', {'data': 'Closed'})
    disconnect()

@socketio.on('connect', namespace='/test')
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
    emit('my_response', {'data': 'Connected', 'count': 0})   

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)