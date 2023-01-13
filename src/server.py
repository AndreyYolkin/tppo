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

    def send_notification(self, notification_type, payload, index=None):
        for subscriber in self.subscribers:
            if index:
                if subscriber[1] == index:
                    self.respond_to(notification_type, payload, subscriber[0])
            else:
                if subscriber[1] is None:
                    self.respond_to(notification_type, payload, subscriber[0])

    # Getter/Setter of state
    def init_state(self, filename):
        self.relay_state = RelayState(6)
        self.previous_state = self.relay_state.get_state()
        self.storage = Storage(filename, self.relay_state.get_state())
        try:
            self.relay_state.set_state(self.storage.get())
            self.previous_state = self.relay_state.get_state()
        except ValueError:
            pass

    def get_state(self, index=None):
        return self.relay_state.get_state(index)

    def set_state(self, state):
        changed_indices = self._compare_and_notify(state)
        try:
            self.relay_state.set_state(state)
        except ValueError:
            pass

        if len(changed_indices) > 0:
            for idx in changed_indices:
                self.send_notification('state_changed', self.get_state(idx), idx)
            self.send_notification('state_changed', self.get_state(), None)
    
    def save_state(self, state, index=None):
        p = self.relay_state.imagine_state(state, index)
        self.storage.set(p)
        return p

    # Subscribers

    def subscribe(self, subscriber, index=None):
        self.subscribers.add((subscriber, int (index) if index else None))
        
    def unsubscribe(self, subscriber, index=None):
        try:
            new_subscribers = set(self.subscribers)
            for sub in self.subscribers:
                if sub[0] == subscriber and sub[1] == (int (index) if index else None):
                    new_subscribers.remove(sub)
            self.subscribers = new_subscribers
        
        except KeyError:
            self.logger.warning(f"we can't unusbscribe if client is not subscribed {subscriber}")
            self.respond_to("error", "we can't unusbscribe if client is not subscribed", subscriber)

    def _compare_and_notify(self, state):
        if self.previous_state is None:
            self.previous_state = self.relay_state.get_state()
            return range(len(state))
        else:
            changed_indices = []
            for i in range(len(state)):
                if state[i] != self.previous_state[i]:
                    changed_indices.append(i)
                    self.previous_state[i] = state[i]
            return changed_indices

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
                    state = self.save_state(data.get("state"), data.get("index", None))
                    self.respond_to("success", state, addr)
                except ValueError as err:
                    self.logger.error(str(err))
                    self.respond_to("error", str(err), addr)
            elif data["type"] == "subscribe":
                self.subscribe(addr, data.get('index', None))
                self.respond_to("success", "subscribed", addr)
                with self.lock:
                    self.logger.info(f"{addr} has subscribed")
            elif data["type"] == "unsubscribe":
                self.unsubscribe(addr, data.get('index', None))
                self.respond_to("success", "unsubscribed", addr)
                with self.lock:
                    self.logger.info(f"{addr} has unsubscribed")
            else:
                self.respond_to("error", "Invalid request type", addr)
                self.logger.warning(f"Invalid request type {addr}")
