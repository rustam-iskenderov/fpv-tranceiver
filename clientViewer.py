import subprocess
import socket
import time
import logging
import urllib.request

from utils import *
from globals import *

def startWatchVideoStream(port):
    #cmd = "d:\\1.0\\x86_64\\bin\\gst-launch-1.0 -e -v udpsrc port={} ! application/x-rtp, payload=96! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! fpsdisplaysink sync=false text-overlay=false"
    cmd = "d:\\1.0\\x86_64\\bin\\gst-launch-1.0 -e -v udpsrc port={} ! decodebin ! videoconvert !  fpsdisplaysink sync=false text-overlay=false"
    cmd = cmd.format(port)
    logging.info(cmd)

    ps = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    #ps = subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)
    #output = ps.communicate()[0]
    #print(output)

    return ps

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO,
                    handlers=[
        logging.FileHandler("viewer.log"),
        logging.StreamHandler()
    ])

logging.info('Viewer is running')

socket_control = ConcurrentSocket()

thread_send_alive = threading.Thread(target = send_alive_loop, args = (socket_control, (server_ip, port_viewer_control),))
thread_send_alive.start()

subProcess = None

while True:    

    print('Enter command: {}, {}'.format(CMD_START, CMD_STOP))
    string = str(input()) 

    try:
        if string == CMD_START:
            socket_video = ConcurrentSocket()
            listen_port = socket_video.get_listen_port()
            socket_video.send_alive((server_ip, port_viewer_video))
            socket_video.close()

            if subProcess != None:
                subProcess.kill()

            subProcess = startWatchVideoStream(listen_port)

            time.sleep(1)

            socket_control.sendto(CMD_START.encode('utf-8'), (server_ip, port_viewer_control))
        
        if string == CMD_STOP:
            socket_control.sendto(CMD_STOP.encode('utf-8'), (server_ip, port_viewer_control))

            if subProcess != None:
                subProcess.kill()

    except socket.error as exc:
        logging.error('socket.error : {}'.format(exc))


