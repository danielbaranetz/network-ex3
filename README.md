# 📡 Assignment 3: Reliable Data Transfer over TCP

**Submitted by:**
* Student 1: 208291377
* Student 2: 213338320

---

## 📖 Overview
This project implements a custom **Reliable Data Transfer (RDT)** protocol on top of a standard TCP connection. The goal is to simulate mechanisms like sliding windows, segmentation, and connection management at the application layer.

The implementation includes a multi-threaded server and a reliable client that handles packet loss (simulated via timeouts) and dynamic flow control.

---

## 📂 Files Structure

| File Name | Description |
|-----------|-------------|
| `server.py` | Multi-threaded server. Handles Handshake, Buffering, and Dynamic Sizing. |
| `client.py` | Client application. Implements Segmentation, Sliding Window, and Retransmission. |
| `server_config.txt` | Configuration for the server (Port, Max Message Size, Dynamic Mode). |
| `client_config.txt` | Configuration for the client (IP, Port, Window Size, Timeout). |
| `my_test_file.txt` | The sample text file used for transmission testing. |
| `record.pcapng` | Wireshark capture file demonstrating the full protocol flow. |
| `Report.pdf` | Final submission report with screenshots and detailed explanations. |

---

## 🚀 How to Run

### Prerequisites
* Python 3.x (Tested on Python 3.13)
* Standard libraries only (`socket`, `threading`, `time`, `os`, `random`).

### 1️⃣ Run the Server
The server will load settings from `server_config.txt` (or use defaults if the file is missing).
```bash
  python server.py
```

### 2️⃣ Run the Client
Open a separate terminal. The client will guide you through the setup.
```bash
  python client.py
```
You will be asked: Would you like to load the configuration from a file? (y/n)

Press 'y' to load parameters from client_config.txt.

The client will automatically connect, negotiate parameters, and start sending my_test_file.txt.