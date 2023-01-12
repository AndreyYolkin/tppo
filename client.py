import json
import socket
import threading
import _thread

class RelayClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(2)
        self.stop_event = threading.Event()

    def subscribe(self):
        self.sock.sendto(json.dumps({"type": "subscribe"}).encode(), (self.host, self.port))
        print("Subscribed.")

    def unsubscribe(self):
        self.sock.sendto(json.dumps({"type": "unsubscribe"}).encode(), (self.host, self.port))
        print("Unsubscribed.")

    def receive_notification(self):
        while not self.stop_event.is_set():
            try:
                data, _ = self.sock.recvfrom(1024)
                message = json.loads(data.decode())
                print(f"{message['type']}: {message['payload']}")
            except TimeoutError:
                pass

    def get_state(self, index=None):
        message = {"type": "get_state"}
        if index is not None:
            message["index"] = index
        self.sock.sendto(json.dumps(message).encode(), (self.host, self.port))

    def set_state(self):
        string_state = input("Enter new state in format on,off,on,off,on,on : ")
        new_state = [x.strip() for x in string_state.split(',')]
        self.sock.sendto(json.dumps({"type": "set_state", "state": new_state}).encode(), (self.host, self.port))

    def stop(self):
        self.stop_event.set()

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
        while not self.stop_event.is_set():
            print("What would you like to do?")
            print("1. Subscribe")
            print("2. Unsubscribe")
            print("3. Get state")
            print("4. Set state")
            print("5. Exit")
            choice = input()
            if choice == "1":
                self.subscribe()
            elif choice == "2":
                self.unsubscribe()
            elif choice == "3":
                self.get_state()
            elif choice == "4":
                self.set_state()
            elif choice == "5":
                self.stop()
                _thread.interrupt_main()
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    try:
        client = RelayClient("localhost", 8000)
        client.start()

    except KeyboardInterrupt:
        print("Client stopped.")
