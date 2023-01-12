import json
import socket
import threading
from state import RelayState
from storage import Storage

class RelayServer:
    def __init__(self, host, port, filename):
        self.host = host
        self.port = port
        self.subscribers = set()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.lock = threading.Lock()
        self.init_state(filename)

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
            self.respond_to("error", "we can't unusbscribe if client is not subscribed", subscriber)

    def start(self):
        notification_loop = threading.Thread(target=self._api_loop)
        notification_loop.daemon = True
        storage_loop = threading.Thread(target=self.storage._check_file_change, args=(self.set_state,))
        storage_loop.daemon = True
        storage_loop.start()
        notification_loop.start()
        notification_loop.join()

    def _api_loop(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            data = json.loads(data.decode())
            if data["type"] == "get_state":
                state = self.get_state()
                self.respond_to("success", state, addr)
            elif data["type"] == "set_state":
                try:
                    self.save_state(data["state"])
                    state = self.get_state()
                    self.respond_to("success", state, addr)
                except ValueError as err:
                    self.respond_to("error", str(err), addr)
            elif data["type"] == "subscribe":
                self.subscribe(addr)
                with self.lock:
                    print(f"{addr} has subscribed")
            elif data["type"] == "unsubscribe":
                self.unsubscribe(addr)
                with self.lock:
                    print(f"{addr} has unsubscribed")
            else:
                self.respond_to("error", "Invalid request type", addr)

if __name__ == "__main__":
    try:
        server = RelayServer("0.0.0.0", 8000, 'filename.bson')
        server.start()
    except KeyboardInterrupt:
        print("Server stopped.")
