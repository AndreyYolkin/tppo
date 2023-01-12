import argparse
import json
import socket
import threading
import _thread
from src.logger import Logger

class RelayClient:
    def __init__(self, host, port, log_level):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(2)
        self.stop_event = threading.Event()
        self.logger = Logger(__name__, log_level)
        self.logger.add_file_handler('logs/client.log')

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
                print(f"\033[96m{message['type']}: {message['payload']}\033[0m")
            except TimeoutError:
                pass
            except socket.error:
                pass

    def get_state(self, index=None):
        message = {"type": "get_state"}
        if index is not None:
            message["index"] = index
        self.sock.sendto(json.dumps(message).encode(), (self.host, self.port))

    def get_indexed_state(self):
        index = input("Enter index: ")
        self.get_state(index)

    def set_state(self):
        string_state = input("Enter new state in format on,off,on,off,on,on : ")
        new_state = [x.strip() for x in string_state.split(',')]
        self.sock.sendto(json.dumps({"type": "set_state", "state": new_state}).encode(), (self.host, self.port))

    def set_indexed_state(self):
        index = input("Enter index: ")
        state = input("Enter new state: ")
        self.sock.sendto(json.dumps({"type": "set_state", "index": index, "state": state}).encode(), (self.host, self.port))

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
            print("\033[95mWhat would you like to do?\033[0m")
            print("1. Subscribe")
            print("2. Unsubscribe")
            print("3. Get state")
            print("4. Get state (Indexed)")
            print("5. Set state")
            print("6. Set state (Indexed)")
            print("7. Exit")
            choice = input()
            if choice == "1":
                self.subscribe()
            elif choice == "2":
                self.unsubscribe()
            elif choice == "3":
                self.get_state()
            elif choice == "4":
                self.get_indexed_state()
            elif choice == "5":
                self.set_state()
            elif choice == "6":
                self.set_indexed_state()
            elif choice == "7":
                self.stop()
                _thread.interrupt_main()
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    client = None
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", default="0.0.0.0", help="IP address of the host")
    parser.add_argument("-p", "--port", default=3000, type=int, help="Port number for the server")
    parser.add_argument("-l", "--log-level", default="INFO", help="Log level (DEBUG, INFO, WARNING, ERROR)")
    args = parser.parse_args()
    try:
        client = RelayClient(args.host, args.port, args.log_level)
        print(f"Host: {args.host}")
        print(f"Port: {args.port}")
        print(f"Log level: {args.log_level}\n")
        client.logger.debug(f"Host: {args.host}, Port: {args.port}, Log level: {args.log_level}")
        client.start()

    except KeyboardInterrupt:
        client.logger.info('Client stopped.')
        print("Client stopped..")
