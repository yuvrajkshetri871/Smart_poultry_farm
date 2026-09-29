import socket
import json

HOST = "127.0.0.1"
PORT = 5001


def send_farm_data(farm_data):

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:

        client.connect((HOST, PORT))

        message = json.dumps(farm_data)

        client.send(message.encode("utf-8"))

        response = client.recv(4096).decode("utf-8")

        return json.loads(response)

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }

    finally:

        client.close()