from src.server import RelayServer
import argparse

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