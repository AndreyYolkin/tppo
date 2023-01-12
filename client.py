import json
import socket
import threading

class RelayClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def subscribe(self):
        self.sock.sendto(json.dumps({"type": "subscribe"}).encode(), (self.host, self.port))
        print("Subscribed.")

    def unsubscribe(self):
        self.sock.sendto(json.dumps({"type": "unsubscribe"}).encode(), (self.host, self.port))
        print("Unsubscribed.")

    def receive_notification(self):
        while True:
            data, _ = self.sock.recvfrom(1024)
            message = json.loads(data.decode())
            print(f"{message['subscriber']} has {message['type']}")

    def start(self):
        main_loop = threading.Thread(target=self._main_loop)
        notification_loop = threading.Thread(target=self.receive_notification)
        main_loop.daemon = True
        notification_loop.daemon = True
        main_loop.start()
        notification_loop.start()
        main_loop.join()
        notification_loop.join()

    def _main_loop(self):
        while True:
            print("What would you like to do?")
            print("1. Subscribe")
            print("2. Unsubscribe")
            print("3. Exit")
            choice = input()
            if choice == "1":
                self.subscribe()
            elif choice == "2":
                self.unsubscribe()
            elif choice == "3":
                break
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    try:
        client = RelayClient("localhost", 8000)
        client.start()
    except KeyboardInterrupt:
        print("Client stopped.")
