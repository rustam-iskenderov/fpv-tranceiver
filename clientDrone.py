import subprocess
import socket
import time
import logging
import urllib.request

from utils import *
from globals import *

def start_video_stream():
    logging.info('Starting video stream')
    cmd = "raspivid -g 24 -n -w 1280 -h 720 -b 1000000 -fps 24 -t 0 -o udp://{}:{}"
    cmd = cmd.format(server_ip, port_drone_video)
    logging.info(cmd)    
    ps = subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)
    #output = ps.communicate()[0]
    #print(output)
    return ps

def listen_control_loop(socketClient: ConcurrentSocket):

    sub_process = None

    while True:
        try:
            pair_data_address = socketClient.recv()
            logging.info('Received {} from {}'.format(pair_data_address[0], pair_data_address[1]))
        except socket.error as exc:
            logging.error('socket.error : {}'.format(exc))

        command = pair_data_address[0].decode('utf-8')

        if command == CMD_START:
            logging.info('command {} received'.format(command))
            
            if sub_process is not None:
                sub_process.kill()
                
            sub_process = start_video_stream()

        elif command == CMD_STOP:
            logging.info('command {} received'.format(command))
            if sub_process is not None:
                sub_process.kill()


logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO,
                    handlers=[
        logging.FileHandler("drone.log"),
        logging.StreamHandler()
    ])

logging.info('Camera is running')

socket_client = ConcurrentSocket()

thread_send_alive = threading.Thread(target = send_alive_loop, args = (socket_client, (server_ip, port_drone_control),))
thread_send_alive.start()

thread_control = threading.Thread(target = listen_control_loop, args = (socket_client,))
thread_control.start()

thread_send_alive.join()
thread_control.join()
        


