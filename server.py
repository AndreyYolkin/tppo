import json
import socket
import threading

class RelayServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.subscribers = set()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.lock = threading.Lock()

    def subscribe(self, subscriber):
        self.subscribers.add(subscriber)
        self.send_notification("subscribed", subscriber)
        
    def unsubscribe(self, subscriber):
        self.subscribers.remove(subscriber)
        self.send_notification("unsubscribed", subscriber)

    def send_notification(self, notification_type, subscriber):
        message = {
            "type": notification_type,
            "subscriber": subscriber
        }
        message_json = json.dumps(message)
        for subscriber in self.subscribers:
            self.sock.sendto(message_json.encode(), subscriber)

    def start(self):
        notification_loop = threading.Thread(target=self._notification_loop)
        notification_loop.daemon = True
        notification_loop.start()
        notification_loop.join()


    def _notification_loop(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            message_json = data.decode()
            message = json.loads(message_json)
            if message["type"] == "subscribe":
                self.subscribe(addr)
                with self.lock:
                    print(f"{addr} has subscribed")
            elif message["type"] == "unsubscribe":
                self.unsubscribe(addr)
                with self.lock:
                    print(f"{addr} has unsubscribed")

if __name__ == "__main__":
    try:
        server = RelayServer("0.0.0.0", 8000)
        server.start()
    except KeyboardInterrupt:
        print("Server stopped.")
