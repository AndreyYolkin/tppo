import argparse
import json
import socket
import threading
from src.state import RelayState
from src.storage import Storage
from src.logger import Logger

class RelayServer:
    def __init__(self, host, port, filename, log_level):
        self.host = host
        self.port = port
        self.subscribers = set()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.lock = threading.Lock()
        self.init_state(filename)
        self.logger = Logger(__name__, log_level)
        self.logger.add_file_handler('logs/server.log')

    # Wrapper for response
    def respond_to(self, type, payload, address):
        message = {
            "type": type,
            "payload": payload
        }
        message = json.dumps(message).encode()
        self.sock.sendto(message, address)

    def send_notification(self, notification_type, payload):
        for subscriber in self.subscribers:
            self.respond_to(notification_type, payload, subscriber)

    # Getter/Setter of state
    def init_state(self, filename):
        self.relay_state = RelayState(6)
        self.storage = Storage(filename, self.relay_state.get_state())
        try:
            self.relay_state.set_state(self.storage.get())
        except ValueError:
            pass

    def get_state(self, index=None):
        return self.relay_state.get_state(index)

    def set_state(self, state):
        try:
            self.relay_state.set_state(state)
            self.send_notification('state_changed', self.get_state())
        except ValueError:
            self.send_notification('state_changed', self.get_state())
    
    def save_state(self, state, index=None):
        self.relay_state.set_state(state, index)
        self.storage.set(self.get_state())

    # Subscribers

    def subscribe(self, subscriber):
        self.subscribers.add(subscriber)
        
    def unsubscribe(self, subscriber):
        try:
            self.subscribers.remove(subscriber)
        except KeyError:
            self.logger.warning(f"we can't unusbscribe if client is not subscribed {subscriber}")
            self.respond_to("error", "we can't unusbscribe if client is not subscribed", subscriber)

    def start(self):
        notification_loop = threading.Thread(target=self._api_loop)
        notification_loop.daemon = True
        storage_loop = threading.Thread(target=self.storage._check_file_change, args=(self.set_state,))
        storage_loop.daemon = True
        storage_loop.start()
        notification_loop.start()
        self.logger.debug(notification_loop)
        self.logger.debug(storage_loop)
        self.logger.info('Server started')
        storage_loop.join()
        notification_loop.join()

    def _api_loop(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            data = json.loads(data.decode())
            self.logger.info(f"{addr}, {data['type']}")
            self.logger.debug(f"{addr}, {data}")
            if data["type"] == "get_state":
                state = self.get_state(data.get("index", None))
                self.respond_to("success", state, addr)
            elif data["type"] == "set_state":
                try:
                    self.save_state(data.get("state"), data.get("index", None))
                    state = self.get_state()
                    self.respond_to("success", state, addr)
                except ValueError as err:
                    self.logger.error(str(err))
                    self.respond_to("error", str(err), addr)
            elif data["type"] == "subscribe":
                self.subscribe(addr)
                with self.lock:
                    self.logger.info(f"{addr} has subscribed")
            elif data["type"] == "unsubscribe":
                self.unsubscribe(addr)
                with self.lock:
                    self.logger.info(f"{addr} has unsubscribed")
            else:
                self.respond_to("error", "Invalid request type", addr)
                self.logger.warning(f"Invalid request type {addr}")

if __name__ == "__main__":
    server = None
    parser = argparse.ArgumentParser(description="Relay server",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-H", "--host", default="0.0.0.0", help="IP address of the host")
    parser.add_argument("-p", "--port", default=3000, type=int, help="Port number for the server")
    parser.add_argument("-f", "--filename", default="device.bson", help="Filename for data storage (BSON)")
    parser.add_argument("-l", "--log-level", default="INFO", help="Log level (DEBUG, INFO, WARNING, ERROR)")
    args = parser.parse_args()
    try:
        server = RelayServer(args.host, args.port, args.filename, args.log_level)
        print(f"Host: {args.host}")
        print(f"Port: {args.port}")
        print(f"Filename: {args.filename}")
        print(f"Log level: {args.log_level}\n")
        server.logger.debug(f"Host: {args.host}, Port: {args.port}, Filename: {args.filename}, Log level: {args.log_level}")
        server.start()
    except KeyboardInterrupt:
        server.logger.info("Server stopped.")
        print("Shutting down...")
