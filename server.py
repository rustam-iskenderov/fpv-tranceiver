import subprocess
import socket
import time
import logging
import urllib.request
import concurrent.futures
import threading

from utils import *
from globals import *

eventStopVideoStream = threading.Event()

def listen_control_loop(socket_client: ConcurrentSocket):            

    while True:
        # waiting for a ping from a client, in order to create reversed connection back to the client
        try:
            pair_data_address = socket_client.recv()

            logging.info('Control loop received {} from {}'.format(pair_data_address[0], pair_data_address[1]))
            
            if socket_client.is_alive(pair_data_address[0]):
                socket_client.set_return_address(pair_data_address[1])
            else :
                socket_client.append_message(pair_data_address[0])

        except socket.error as exc:
            logging.error('Listen control stream {}, socket.error : {}'.format(socket_client.return_address, exc))


def listen_video_loop(socket_viewer: ConcurrentSocket):
            
    while True:
        # waiting for a ping from a client, in order to create reversed connection back to the client
        try:
            pair_data_address = socket_viewer.recv()

            logging.info('Video loop received {} from {}'.format(pair_data_address[0], pair_data_address[1]))
            
            if socket_viewer.is_alive(pair_data_address[0]):
                socket_viewer.set_return_address(pair_data_address[1])
 
        except socket.error as exc:
            logging.error('Listen video stream {}, socket.error : {}'.format(socket_viewer.return_address, exc))


def redirect_video_loop(socket_viewer: ConcurrentSocket):
            
    socket_camera_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_camera_video.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_camera_video.bind(('', port_camera_video))
        
    while True:

#        if eventStopVideoStream.is_set():
#            break

        try:
            pair_data_address = socket_camera_video.recvfrom(65535)

            socket_viewer.LOG = False
            socket_viewer.send(pair_data_address[0])
            logging.info('Sending video to {}'.format(socket_viewer.return_address))
            socket_viewer.LOG = True

        except socket.error as exc:
            logging.error('Redirect video stream socket.error : {}'.format(exc))



def redirect_control_loop(socket_from: ConcurrentSocket, socket_to: ConcurrentSocket):

    while True:
        try:
            message = socket_from.pop()            
            socket_to.send(message)

        except socket.error as exc:
            logging.error('Redirect control stream socket.error : {}'.format(exc))


logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO,
                    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ])

logging.info('Server is running')

external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
logging.info('Server public ip {}'.format(external_ip))


socket_camera_ctrl = ConcurrentSocket(port_camera_control)
socket_viewer_ctrl = ConcurrentSocket(port_viewer_control)


thread_listen_ctrl_viewer = threading.Thread(target = listen_control_loop, args = (socket_viewer_ctrl,))
thread_listen_ctrl_viewer.start()

thread_listen_ctrl_camera = threading.Thread(target = listen_control_loop, args = (socket_camera_ctrl,))
thread_listen_ctrl_camera.start()


# camera <- server <- viewer (commands)
thread_redirect_ctrl = threading.Thread(target = redirect_control_loop, args = (socket_viewer_ctrl, socket_camera_ctrl,))
thread_redirect_ctrl.start()

# camera -> server -> viewer (telemetry)
#threadControlChannel = thread.start_new_thread(threadRedirectControlStream, (clientCameraAddress, clientViewerAddress))

# creating video channel
socket_viewer_video = ConcurrentSocket(port_viewer_video)
thread_listen_video_viewer = threading.Thread(target = listen_video_loop, args = (socket_viewer_video,))
thread_listen_video_viewer.start()

thread_redirect_video = threading.Thread(target = redirect_video_loop, args = (socket_viewer_video,))
thread_redirect_video.start()


thread_listen_ctrl_viewer.join()
thread_listen_ctrl_camera.join()
thread_redirect_ctrl.join()

thread_listen_video_viewer.join()
thread_redirect_video.join()


# subprocess.call(["",""])

# cmd = "raspivid -n -t 0 -w 1280 -h 720 -hf -fps 25 -b 2000000 -o - | gst-launch-1.0 -e -vvvv fdsrc ! h264parse ! rtph264pay pt=96 config-interval=5 ! udpsink host=192.168.1.3 port=6243"
# cmd = "raspivid -n -t 0 -w 1280 -h 720 -hf -fps 25 -b 2000000 -o - | gst-launch-1.0 -e -vvvv fdsrc ! h264parse ! rtph264pay pt=96 config-interval=5 ! udpsink host={} port={}"
# cmd = cmd.format(address[0], address[1])
# print(cmd)


# ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# output = ps.communicate()[0]
# print(output)
