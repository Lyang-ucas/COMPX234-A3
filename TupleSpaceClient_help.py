import socket
import sys
import os

def main():
    if len(sys.argv) != 4:
        print("Usage: python tuple_space_client.py <server-hostname> <server-port> <input-file>")
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])
    input_file_path = sys.argv[3]

    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' does not exist.")
        sys.exit(1)

    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # TASK 1: Create a TCP/IP socket and connect it to the server.
    # Hint: socket.socket(socket.AF_INET, socket.SOCK_STREAM) creates the socket.
    # Then call sock.connect((hostname, port)) to connect.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, port))

    try:
        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split(" ", 2)
            cmd = parts[0]
            message = ""

            # TASK 2: Build the protocol message string to send to the server.
            # Format:  "NNN X key"        for READ / GET
            #          "NNN P key value"   for PUT
            # where NNN is the total message length as a zero-padded 3-digit number,
            # X is "R" for READ and "G" for GET.
            # Hint: for READ/GET, size = 6 + len(key). For PUT, size = 7 + len(key) + len(value).
            # Reject lines with invalid format or key+" "+value > 970 chars.
            if cmd == "READ" :
                if len(parts) < 2:
                    print(f"Error: Invalid READ format for line: {line}")
                    continue
                msg_body = f"R {parts[1]}"
                message = f"{len(msg_body) + 3:03d} {msg_body}"
            elif cmd == "GET":
                if len(parts) < 2:
                    print(f"Error: Invalid GET format for line: {line}")
                    continue
                msg_body = f"G {parts[1]}"
                message = f"{len(msg_body) + 3:03d} {msg_body}"
            elif cmd == "PUT":
                if len(parts) < 3:
                    print(f"Error: Invalid PUT format for line: {line}")
                    continue
                key = parts[1]
                value = parts[2]
                if len(key) + len(value) + 1 > 970:
                    print(f"Error: Key and value length exceeds 970 characters for line: {line}")
                    continue
                msg_body = f"P {key} {value}"
                message = f"{len(msg_body) + 3:03d} {msg_body}"
            else:
                print(f"Error: Invalid command format for line: {line}")
                continue

            # TASK 3: Send the message to the server, then receive the response.
            # - Send:    sock.sendall(message.encode())
            # - Receive: first read 3 bytes to get the response size (like the server does).
            #            Then read the remaining (size - 3) bytes to get the response body.
            message = f"{len(msg_body):03d} {msg_body}"
            sock.sendall(message.encode())
            len_bytes = sock.recv(3)
            if len(len_bytes) < 3:
                print(f"Error: Incomplete response size received for line: {line}")
                break
            resp_size = int(len_bytes.decode())
            resp_bytes = b""
            while len(resp_bytes) < resp_size:
                chunk = sock.recv(resp_size - len(resp_bytes))
                if not chunk:
                    print(f"Error: Connection closed by server while receiving response for line: {line}") 
                    break
                resp_bytes += chunk                           # Keep reading until we get the full response body
            response = resp_bytes.decode().strip()
            print(f"{line}: {response}")

    except (socket.error, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # TASK 4: Close the socket when done (already called for you — explain why
        if sock:
            sock.close()
        # finally: is the right place to do this even if an error occurs above).
        # The finally block ensures that the socket is closed regardless of whether an error occurs or not.

if __name__ == "__main__":
    main()