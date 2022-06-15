from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect    
import serial #import potrebnych kniznic

async_mode = None
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

#nastavenie seriovej komunikacie
ser=serial.Serial("/dev/ttyS2")
ser.baudrate = 9600
  
def background_thread(args):
    count = 0
    while True:
        #citanie zo seriovej komunikacie
        read_ser = ser.readline()
        read_ser = read_ser.decode()
        
        #dictionary args
        btnVchoose = dict(args).get('btn_choose')
        btnVstart = dict(args).get('btn_start')
        print (args)
        
        #wait 1 sec.
        socketio.sleep(1)
        #counter
        count += 1
        
        # uprava dotiahnutych dat a vypis
        read_ser_data = read_ser.split(" ")
        read_ser_data[3] = read_ser_data[3].replace("\r\n","")
        print(read_ser_data)
        
        #zapis tychto dat do suboru file.txt
        with open("file.txt","a") as file:
            file.write("Distance: "+read_ser_data[0]+" Humidity: "+read_ser_data[1]+" Temperature: "+read_ser_data[2]+" Photo: "+read_ser_data[3]+"\n")
            
        #vypis upravenych dat do skuska.html
        if btnVstart == "Start":
            if btnVchoose == "Distance":
                socketio.emit('my_response',{'velicina': "Distance", 'data_choose': float(read_ser_data[0]), 'count': count, 'unit': " cm"}, namespace='/test')
            if btnVchoose == "Humidity":
                socketio.emit('my_response',{'velicina': "Humidity", 'data_choose': float(read_ser_data[1]), 'count': count, 'unit': " %"}, namespace='/test')
            if btnVchoose == "Temperature":
                socketio.emit('my_response',{'velicina': "Temperature", 'data_choose': float(read_ser_data[2]), 'count': count, 'unit': " °C"}, namespace='/test')
            if btnVchoose == "Photo":
                socketio.emit('my_response',{'velicina': "Photo", 'data_choose': float(read_ser_data[3]), 'count': count, 'unit': ""}, namespace='/test')
                
#metoda pre prepojenie so skuska.html
@app.route('/', methods=['GET', 'POST'])
def skuska():
    return render_template('skuska.html', async_mode=socketio.async_mode)

#metoda pre pouzitie start a stop tlacidiel
@socketio.on('start_event', namespace='/test')
def start_event(message):   
    session['btn_start'] = message['value']
    
#metoda pre pouzitie vyberovych tlacidiel
@socketio.on('choose_event', namespace='/test')
def choose_event(message):   
    session['btn_choose'] = message['value']
    
#metoda pre ukoncenie spojenia
@socketio.on('closed', namespace='/test')
def closed():
    emit('my_response', {'data': 'Closed'})
    disconnect()
    ser.cancel_read()

@socketio.on('connect', namespace='/test')
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
    emit('my_response', {'data': 'Connected', 'count': 0})   

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)