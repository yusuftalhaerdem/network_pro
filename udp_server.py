import threading
import socket
import time

import db_ops

TCP_PORT = 4050
TCP_IP = socket.gethostbyname(socket.gethostname())
SIZE = 1024
FORMAT = "utf-8"
thread_list = []

udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server.bind((TCP_IP, TCP_PORT))

active_user_list = []
active_user_list_time = []


def check_connection_updates():
    while True:
        udp_server.settimeout(999)
        data, addr = udp_server.recvfrom(SIZE)
        udp_server.settimeout(2)
        data = data.decode(FORMAT)
        # print(f"{data} informed its online status")
        try:
            index = active_user_list.index(data)
            active_user_list_time[index] = time.time()

            # adds user
        except:
            # add_user_udp(data)
            pass


def add_user_udp(username):  # this part is needless
    active_user_list.append(username)
    active_user_list_time.append(time.time())
    db_ops.active_user(username)

def check_new_users():
    for active_user in db_ops.get_active_users():
        if active_user_list.index(active_user) >= 0:
            continue
        active_user_list.append(active_user)
        active_user_list_time.append(time.time())
        pass

def retrieve_online_status():
    for active_user in db_ops.get_active_users():
        active_user_list.append(active_user)
        active_user_list_time.append(time.time())
        pass


def check_online_status():
    for active_user in db_ops.get_active_users():
        loc = 0
        try:
            loc = active_user_list.index(active_user)
        except:
            active_user_list.append(active_user)
            active_user_list_time.append(time.time())
            loc = active_user_list.index(active_user)

        last_check = active_user_list_time[loc]
        if time.time() - last_check > 20:
            print(f"{active_user} is now offline")
            active_user_list.pop(loc)
            active_user_list_time.pop(loc)
            db_ops.db_logout(active_user)


def start_udp():
    retrieve_online_status()
    udp_thread = threading.Thread(target=check_connection_updates)
    print("udp started at 4050")
    udp_thread.start()
    while True:
        time.sleep(1)
        check_online_status()


if __name__ == '__main__':
    start_udp()
    print("hello")

'''
message = "hello world"
message = message.encode(FORMAT)
server.sendto(message, addr)
def check_peer(username, addr, thread_count):
    thread_id = len(thread_list)
    in_loop = True
    print(server.gettimeout())
    while in_loop:
        try:
            server.settimeout(20)
            msg, addr2 = server.recvfrom(SIZE)
            msg = msg.decode(FORMAT)
            print("msg received: " + msg)
            server.settimeout(0)
        except:
            thread_list.pop(thread_id - 1)
            print(f"user {username} is disconnected.")

    thread_list.pop(thread_id - 1)
    pass
'''
