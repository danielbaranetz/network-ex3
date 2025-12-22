import os


def get_client_config():
    while True:
        answer = input("Would you like to load the configuration from a file? (y/n): ")

        if answer == "y": # load from config file
            config_file = input("Please enter the path to the configuration file: ")
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

                            if key == "server_port" or key == "window_size" or key == "timeout" or key == "maximum_msg_size":
                                config[key] = int(value)
                            elif key == "dynamic_message_size":
                                config[key] = value.lower() == "true"
                            else:
                                config[key] = value
                return config
            except Exception as e:
                print(f"Error parsing file: {e}")

        elif answer == "n": # load from input
            try:
                server_ip = input("Enter Server IP: ")
                server_port = int(input("Enter Server Port: "))
                max_msg_size = int(input("Enter Request Max Message Size: "))
                window_size = int(input("Enter Window Size: "))
                timeout = int(input("Enter Timeout (seconds): "))

                dynamic_input = input("Dynamic Message Size? (True/False): ")
                is_dynamic = dynamic_input.lower() == "true"

                message_file = input("Enter path to file to send: ")
                if not os.path.exists(message_file):
                    print(f"Error: The file '{message_file}' does not exist.")
                    continue

                return {
                    "server_ip": server_ip,
                    "server_port": server_port,
                    "maximum_msg_size": max_msg_size,
                    "window_size": window_size,
                    "timeout": timeout,
                    "dynamic_message_size": is_dynamic,
                    "message": message_file
                }
            except ValueError:
                print("Error: Port, sizes and timeout must be numbers.\n")
                continue
        else:
            print("Please enter 'y' or 'n'.")


if __name__ == "__main__":
    conf = get_client_config()
    print(conf)