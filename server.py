import random
import socket
import threading
import os

MSG_SIN = b"SIN"
MSG_SIN_ACK = b"SIN/ACK"
MSG_ACK = b"ACK"
MSG_NEGOTIATION_REQUEST = b"MAX_SIZE_REQ"



def load_config(filename="server_config.txt"):  # Pre-defined file to override
    config = {
        "maximum_msg_size": 100,
        "dynamic_message_size": False,
        "port": 12345
    }
    if os.path.exists(filename):  # Override the file
        try:
            with open(filename, "r") as f:
                for line in f:
                    if ":" in line:
                        key, value = line.strip().split(":", 1)
                        if key.strip() == "maximum_msg_size":
                            config["maximum_msg_size"] = int(value.strip())
                        elif key.strip() == "port":
                            config["port"] = int(value.strip())
                        elif key.strip() == "dynamic_message_size":
                            config["dynamic_message_size"] = value.strip().lower() == "true"
        except Exception as e:
            print(f"Error reading config: {e}")
    return config



def perform_handshake(conn: socket.socket) -> bool:
    print("Waiting for SIN...")
    try:
        data = conn.recv(1024)
    except TimeoutError:
        print("Handshake failed: Timeout waiting for SIN.")
        return False

    if data.strip() != MSG_SIN:
        print(f"Handshake failed: Expected SIN, got {data.strip()}")
        return False

    print("Received SIN. Sending SIN/ACK...")
    conn.sendall(MSG_SIN_ACK)

    print("Waiting for final ACK...")
    data = conn.recv(1024)

    if data.strip() != MSG_ACK:
        print(f"Handshake failed: Expected final ACK, got {data.strip()}")
        return False

    print("Handshake complete !.")
    return True


def handle_client(conn: socket.socket, addr, max_msg_size, dynamic_size):
    with conn:
        print(f"[new connection] {addr} started.")

        if not perform_handshake(conn):
            print(f"[connection closed] {addr}")
            return

        print("Starting negotiation...")
        req = conn.recv(1024).strip()
        if req != MSG_NEGOTIATION_REQUEST:
            print(f"Negotiation failed: Expected size request, got {req}")
            return

        response_data = str(max_msg_size).encode('utf-8')
        conn.sendall(response_data)
        print(f"Sent max message size: {max_msg_size}")

        expected_seq = 0
        buffer = {}
        received_data = {}

        recv_buf_size = int(max_msg_size) + 100

        while True:
            try:
                data = conn.recv(recv_buf_size)
                if not data:
                    print("Client disconnected")
                    break

                try: # Parsing
                    header_end_index = data.find(b':')
                    if header_end_index == -1:
                        continue
                    seq_str = data[:header_end_index]
                    msg_str = data[header_end_index + 1:]
                    seq_num = int(seq_str)
                except ValueError:
                    print("Error: Invalid sequence number")
                    continue

                print(f"Received Packet {seq_num}. (Looking for {expected_seq})")

                if seq_num == expected_seq:
                    received_data[seq_num] = msg_str
                    expected_seq += 1

                    while expected_seq in buffer:
                        print(f"Found {expected_seq} in buffer, processing it too.")
                        received_data[expected_seq] = buffer.pop(expected_seq)
                        expected_seq += 1

                elif seq_num > expected_seq:
                    print(f"Packet {seq_num} arrived early. Buffering.")
                    buffer[seq_num] = msg_str


                last_ok = expected_seq - 1
                ack_msg = f"{last_ok}"
                if dynamic_size: # Using random from 50 to max_msg_size
                    new_size = random.randint(50, max_msg_size)
                    ack_msg += f"|{new_size}"
                    recv_buf_size = new_size + 100

                conn.sendall(ack_msg.encode())

            except Exception as e:
                print(f"Error in loop: {e}")
                break

        print("Full message received:")
        full_content = b"".join([received_data[i] for i in sorted(received_data.keys())])
        try:
            print(full_content.decode(errors='ignore'))
        except:
            print("[Binary data received]")


# Run server
def start_server():
    config = load_config()
    HOST = '0.0.0.0'
    PORT = config["port"]
    MAX_SIZE = config["maximum_msg_size"]
    DYNAMIC = config["dynamic_message_size"]

    print(f"Server starting on port {PORT}...")
    print(f"Config: Max Size={MAX_SIZE}, Dynamic={DYNAMIC}")

    # Open Socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client,
                                      args=(conn, addr, MAX_SIZE, DYNAMIC))
            thread.start()


if __name__ == "__main__":
    start_server()