import socket
import json

HOST = "127.0.0.1"
PORT = 5001


def start_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((HOST, PORT))
    server.listen(5)

    print("================================")
    print(" PoultrySense Socket Server")
    print("================================")
    print(f"Server running on {HOST}:{PORT}")
    print("Waiting for farm data...\n")

    while True:

        connection, address = server.accept()

        try:
            data = connection.recv(4096).decode("utf-8")

            if data:

                farm_data = json.loads(data)

                print("----- NEW FARM DATA -----")
                print(farm_data)
                print("-------------------------\n")

                response = {
                    "status": "success",
                    "message": "Farm data received successfully"
                }

                connection.send(
                    json.dumps(response).encode("utf-8")
                )

        except Exception as error:

            print("Error:", error)

        finally:

            connection.close()


if __name__ == "__main__":
    start_server()