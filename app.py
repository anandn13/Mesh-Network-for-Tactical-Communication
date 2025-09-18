# Streamlit dashboard for Mesh Gateway
# Reads serial from gateway ESP32 and displays messages live.
import streamlit as st
import serial
import threading
import queue
import os

st.set_page_config(layout='wide', page_title='Mesh Gateway Dashboard')
st.title('Mesh Network Dashboard (Gateway)')

serial_port = st.text_input('Serial port (e.g. COM3 or /dev/ttyUSB0)', value=os.getenv('SERIAL_PORT', ''))
baud = st.number_input('Baud rate', value=115200, step=1)
connect = st.button('Connect')

msg_q = queue.Queue()

def serial_reader(port, baud, q):
    try:
        ser = serial.Serial(port, baud, timeout=1)
    except Exception as e:
        q.put(('__ERROR__', str(e)))
        return
    q.put(('__INFO__', f'Connected to {port} @ {baud}'))
    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                q.put(('__LINE__', line))
        except Exception as e:
            q.put(('__ERROR__', str(e)))
            break

reader_thread = None
if connect and serial_port:
    reader_thread = threading.Thread(target=serial_reader, args=(serial_port, baud, msg_q), daemon=True)
    reader_thread.start()

col1, col2 = st.columns([3,1])
with col1:
    st.subheader('Live log')
    log_box = st.empty()
with col2:
    st.subheader('Controls')
    st.write('Type `send <dst> <message>` in gateway Serial Monitor to send messages from gateway.')
    st.write('Gateway must be flashed with IS_GATEWAY = true.')

logs = []
while not msg_q.empty():
    typ, val = msg_q.get()
    if typ == '__LINE__':
        logs.append(val)
    elif typ == '__INFO__':
        logs.append('[INFO] ' + val)
    elif typ == '__ERROR__':
        logs.append('[ERROR] ' + val)

if logs:
    log_box.text_area('Gateway log', '\n'.join(logs[-500:]), height=600)
else:
    log_box.text_area('Gateway log', 'No data yet. Connect and open Serial Monitor on the gateway (115200).', height=600)