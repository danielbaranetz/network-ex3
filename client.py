import os
import socket
import time

MSG_SIN = b"SIN"
MSG_SIN_ACK = b"SIN/ACK"
MSG_ACK = b"ACK"
MSG_NEGOTIATION_REQUEST = b"MAX_SIZE_REQ"


def start_client():
    config = get_client_config()
    if not config:
        return
    server_ip = config.get("server_ip", "127.0.0.1")
    server_port = config["server_port"]
    file_path = config["message_file"]
    window_size = config["window_size"]
    timeout = config["timeout"]

    is_dynamic = config.get("dynamic_message_size", False)

    print(f"--- Client Starting ---")
    print(f"Target: {server_ip}:{server_port}")
    print(f"File to send: {file_path}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_ip, server_port))
        print("Connected to server.")

        if not perform_client_handshake(sock):
            sock.close()
            return

        print("Requesting max message size...")
        sock.sendall(MSG_NEGOTIATION_REQUEST)

        response = sock.recv(1024).strip()
        current_max_msg_size = int(response)
        print(f"Server approved max size: {current_max_msg_size} bytes")

        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found!")
            return

        with open(file_path, "rb") as f:
            file_data = f.read()
        print(f"Loaded {len(file_data)} bytes.")

        send_file_reliable(sock, file_data, window_size, timeout, current_max_msg_size, is_dynamic)

        print("Done.")
        sock.close()

    except ConnectionRefusedError:
        print("Error: Could not connect to server. Is it running?")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_client_config():
    while True:
        answer = input("Would you like to load the configuration from a file? (y/n): ")
        if answer == "y":
            config_file = input("Please enter the path to the configuration file (default: client_config.txt): ")
            if not config_file: config_file = "client_config.txt"

            if not os.path.exists(config_file):
                print("Configuration file not found.\n")
                continue

            config = {}
            try:
                with open(config_file, "r") as f:
                    for line in f:
                        if ":" in line:
                            key, value = line.strip().split(":", 1)
                            key = key.strip()
                            value = value.strip().strip('"')

                            if key in ["server_port", "window_size", "timeout", "maximum_msg_size"]:
                                config[key] = int(value)
                            elif key == "dynamic_message_size":
                                config[key] = value.lower() == "true"
                            else:
                                config[key] = value

                if "message" in config:
                    config["message_file"] = config["message"]

                return config
            except Exception as e:
                print(f"Error parsing file: {e}")

        elif answer == "n":
            try:
                server_ip = input("Enter Server IP: ")
                server_port = int(input("Enter Server Port: "))
                max_msg_size = int(input("Enter Request Max Message Size: "))
                window_size = int(input("Enter Window Size: "))
                timeout = int(input("Enter Timeout (seconds): "))

                dynamic_input = input("Dynamic Message Size? (True/False): ")
                is_dynamic = dynamic_input.lower() == "true"

                message_file = input("Enter path to file to send: ")

                return {
                    "server_ip": server_ip,
                    "server_port": server_port,
                    "maximum_msg_size": max_msg_size,
                    "window_size": window_size,
                    "timeout": timeout,
                    "dynamic_message_size": is_dynamic,
                    "message_file": message_file
                }
            except ValueError:
                print("Error: Port, sizes and timeout must be numbers.\n")
                continue
        else:
            print("Please enter 'y' or 'n'.")


def perform_client_handshake(sock: socket.socket):
    try:
        sock.send(MSG_SIN)
        data = sock.recv(1024)
        if data.strip() != MSG_SIN_ACK:
            print(f"Handshake failed. Expected SIN/ACK, got {data}")
            return False
        print(f"Handshake received SIN/ACK. Sending ACK ...")
        sock.send(MSG_ACK)
        print(f"Handshake completed")
        return True
    except Exception as e:
        print(f"Handshake error: {e}")
        return False


import time
import socket


def send_file_reliable(sock, file_data, window_size, timeout, max_msg_size, is_dynamic):
    packets = []
    total_len = len(file_data)
    current_pos = 0

    while current_pos < total_len:
        chunk = file_data[current_pos: current_pos + max_msg_size]
        packets.append(chunk)
        current_pos += max_msg_size

    total_packets = len(packets)
    print(f"File split into {total_packets} packets.")

    base = 0
    next_seq = 0
    sock.settimeout(timeout)

    while base < total_packets:

        while next_seq < base + window_size and next_seq < total_packets:
            packet_data = packets[next_seq]

            if len(packet_data) > max_msg_size:
                packet_data = packet_data[:max_msg_size]

            msg_header = f"{next_seq}:".encode()
            msg_to_send = msg_header + packet_data

            try:
                sock.send(msg_to_send)
                print(f"Sent packet {next_seq}")
                time.sleep(0.05)  # avoid TCP sticky packets
                next_seq += 1
            except Exception as e:
                print(f"Error sending: {e}")
                break

        try:
            ack_data = sock.recv(1024)
            ack_str = ack_data.decode().strip()

            if "|" in ack_str:
                parts = ack_str.split("|")

                if parts[0].isdigit():
                    ack_num = int(parts[0])

                if is_dynamic and len(parts) > 1:
                    size_candidate = ''.join(filter(str.isdigit, parts[1]))

                    if size_candidate:
                        new_size = int(size_candidate)
                        if new_size != max_msg_size:
                            print(f"\nServer requested Dynamic Size Update: {max_msg_size} -> {new_size} bytes\n")
                            max_msg_size = new_size
            else:
                ack_num = int(ack_str)

            print(f"Received ACK {ack_num}")

            if ack_num >= base:
                base = ack_num + 1

        except socket.timeout:
            print(f"No ACK received for {timeout} seconds. Resending window from {base}...")
            next_seq = base  # Go-Back-N

        except ValueError:
            print(f"Warning: Received raw data '{ack_str}' which caused parsing error, ignoring.")

        except Exception as e:
            print(f"Error {e}")
            break

    print(f"\nAll {total_packets} packets acknowledged successfully.")


if __name__ == "__main__":
    start_client()