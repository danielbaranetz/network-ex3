import socket
import threading

MSG_SIN = b"SIN"
MSG_SIN_ACK = b"SIN/ACK"
MSG_ACK = b"ACK"
MSG_NEGOTIATION_REQUEST = b"MAX_SIZE_REQ"


def perform_handshake(conn: socket.socket) -> bool:
    """מבצע את תהליך לחיצת היד הנדרש."""
    print("Waiting for SIN...")

    try:     # try to get SIN
        data = conn.recv(1024)
    except TimeoutError:
        print("Handshake failed: Timeout waiting for SIN.")
        return False

    if data.strip() != MSG_SIN:
        print(f"Handshake failed: Expected SIN, got {data.strip()}")
        return False

    print("Received SIN. Sending SIN/ACK...")

    conn.sendall(MSG_SIN_ACK)

    print("  > Waiting for final ACK...")
    data = conn.recv(1024)

    if data.strip() != MSG_ACK:
        print(f"Handshake failed: Expected final ACK, got {data.strip()}")
        return False

    print("Handshake complete !.")
    return True # 3 way handshake was successful


def handle_client(conn: socket.socket, addr, max_msg_size, dynamic_size):
    with conn:
        print(f"[new connection] {addr} started.")

        # שלב 1: לחיצת יד
        if not perform_handshake(conn):
            print(f"[connection closed] {addr}")
            return

        # שלב 2: תיאום גודל (Negotiation)
        # זה דורש גם שהוא יקבל בקשה ואז ישלח את המספר
        print("  > Starting negotiation...")

        req = conn.recv(1024).strip() # server request maximum 1024 bytes
        if req != MSG_NEGOTIATION_REQUEST:
            print(f"Negotiation failed: Expected size request, got {req}")
            return

        response_data = str(max_msg_size).encode('utf-8')
        conn.sendall(response_data) # server sends the maximum message
        print(f"Sent max message size: {max_msg_size}")

        expected_seq = 0
        buffer = {}

        # גודל הבאפר לקליטה צריך להיות גדול מהודעה מקסימלית + מקום לכותרת
        RECV_BUF_SIZE = int(max_msg_size) + 100
        while True:
            try:
                data = conn.recv(RECV_BUF_SIZE)
                if not data:
                    print("Client disconnected")
                    break
                try:
                    header_end_index = data.find(b':')
                    if header_end_index == -1:
                        print("Error: no sequence number was found")
                        continue
                    seq_str = data[:header_end_index]
                    msg_str = data[header_end_index+1:]
                    seq_num = int(seq_str)
                except ValueError:
                    print("Error: Invalid sequnece number")
                    continue
                print(f"Received Packet {seq_num}. (Looking for {expected_seq})")
                if seq_num == expected_seq:
                    expected_seq += 1
                while expected_seq in buffer:
                    print(f"Found {expected_seq} in buffer, processing it too.")
                    del buffer[expected_seq]
                    expected_seq += 1
                    if






            # כאן יכנס הקוד לקבלת סגמנטים, בדיקת Sequence Number ושליחת ACKs
            # ...
            # אם החיבור נסגר (הלקוח סיים לשלוח):
            # break
            pass