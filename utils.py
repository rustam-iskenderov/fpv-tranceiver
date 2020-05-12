import threading
import socket
import time
import logging

class ConcurrentSocket():

    MSG_SIZE = 512

    MSG_ALIVE = 'alive'

    LOG = True

    def __init__(self, port = 0):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        self.return_address = None                
        self.msg_list = []
        self.lock_send = threading.Lock()
        self.lock_msg_list = threading.Lock()
        self.condition = threading.Condition()
        
    def get_listen_port(self):
        return self.socket.getsockname()[1]
    
    def sendto(self, data, address):
        if self.LOG:
            logging.info('Sending {} from {} to {}'.format(data, self.return_address, address))

        with self.lock_send:
            self.socket.sendto(data, address)

    def send(self, data):
        if self.return_address is not None:
            self.sendto(data, self.return_address)
            return True
        return False

    # address (ip, port)
    def send_alive(self, address):
        self.sendto(self.MSG_ALIVE.encode('utf-8'), address)      
        
    def is_alive(self, data):
        return data.decode('utf-8') == self.MSG_ALIVE

    def recv(self):
        logging.info('Waiting for data on port {}'.format(self.get_listen_port()))
        pair_data_address = self.socket.recvfrom(self.MSG_SIZE)
        return pair_data_address
        
    def set_return_address(self, new_address):
        logging.info('Updating return address from {} to {}'.format(self.return_address, new_address))
        with self.lock_send:
            self.return_address = new_address

    def append_message(self, msg):
        with self.lock_msg_list:
            self.msg_list.append(msg)

        with self.condition:            
            self.condition.notify_all()    

    def pop(self):
        with self.condition:
            while len(self.msg_list) == 0:
                self.condition.wait()

        with self.lock_msg_list:
            return self.msg_list.pop(0)

    def close(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()


def send_alive_loop(socket_client: ConcurrentSocket, address):
    while True:
        try:
            socket_client.send_alive(address)
        except socket.error as exc:
            logging.error('socket.error : {}'.format(exc))
        finally:
            time.sleep(10)
