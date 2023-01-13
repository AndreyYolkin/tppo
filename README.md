Relay Server
============

The relay server is a python program that allows you to control and monitor the state of a relay, which contains multiple switches. It allows you to get and set the state of all or a specific switch, subscribe to changes and notify subscribers when a switch or relay state changes.

Installation
------------

To install the Relay Server project, you will need to have Python 3.x installed on your system.

1.  Clone the repository:
```bash
git clone https://github.com/AndreyYolkin/tppo.git
```

2.  Install the dependencies:
```bash
pip install -r requirements.txt
```

Server
------

The server can be started by running the `tppo_server_1232.py` file. It takes the following arguments:

*   `host`: The host IP address to bind the server to. Defaults to `127.0.0.1`.
*   `port`: The port number to bind the server to. Defaults to `8002`.
*   `filename`: The filename of the storage file. Defaults to `device.bson`.
*   `log_level`: The log level for the server. Defaults to `INFO`.

To start the server, you can run the following command:

```bash
python tppo_server_1232.py --host=127.0.0.1 --port=8002 --filename=device.bson --log_level=INFO
```

Client
------

The client allows you to interact with the relay server by sending commands to it and receiving notifications from it. It can be started by running the `tppo_client_1232.py` file. It takes the following arguments:

*   `host`: The host IP address of the server. Defaults to `127.0.0.1`.
*   `port`: The port number of the server. Defaults to `8002`.
*   `log_level`: The log level for the client. Defaults to `INFO`.

To start the client, you can run the following command:
```bash
python tppo_client_1232.py --host=127.0.0.1 --port=8002 --log_level=INFO
```

API
---

The relay server also provides a REST API that can be used to get and set the state of a relay. The API has the following endpoints:

*   `GET /api/relay`: Retrieves the current state of all switches in the relay.
    
    *   Inputs: None
    *   Outputs: JSON object with a single key, "state", which contains an array of strings representing the state of each switch (either "on" or "off").
*   `GET /api/relay/<int:index>`: Retrieves the current state of a specific switch in the relay, specified by its index.
    
    *   Inputs:
        *   `index`: the index of the switch (integer)
    *   Outputs: JSON object with a single key, "state", which contains a string representing the state of the switch (either "on" or "off").
*   `POST /api/relay`: Updates the state of all switches in the relay.
    
    *   Inputs:
        *   A JSON object with a single key, "state", which contains an array of strings representing the desired state of each switch (either "on" or "off").
    *   Outputs: JSON object with the same format as the `GET /api/relay` endpoint.
*   `POST /api/relay/<int:index>`: Updates the state of a specific switch in the relay, specified by its index.
    
    *   Inputs:
        *   `index`: the index of the switch (integer)
        *   A JSON object with a single key, "state", which contains a string representing the desired state of the switch (either "on" or "off").
    *   Outputs: JSON object with the same format as the `GET /api/relay/<int:index>` endpoint.

Also, Flask has UI page, where you can see and change the state of relay, available at `/` of Flask instance.

To start the flask, you can run the following command:
```bash
python tppo_rest_1232.py --port=5000
```