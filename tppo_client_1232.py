from src.client import RelayClient
import argparse

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