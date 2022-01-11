import sys, socket, select, threading, _thread, time, sqlite3
from typing import Dict, Any

import db_ops
import udp_server


class centralServerInterface(threading.Thread):  # MAIN THREAD INTERFACE FOR ALL PEERS
    sockets = []

    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.running = 1

    def run(self):  # Thread starts
        while self.running == 1:
            # gets the user input from the peer
            request = self.conn.recv(1024).decode("utf-8")
            match request:
                case "get active user list":
                    self.return_active_users(self.conn, self.addr)
                case "get user info":
                    self.return_user_ınfo(self.conn, self.addr)
                case "register":
                    self.registerToTheSystem(self.conn, self.addr)
                case "join":
                    self.joinToTheSystem(self.conn, self.addr)
                case "search":
                    self.searchInTheSystem(self.conn, self.addr)
                case "clientPortUpdate":
                    userNameAndclientPortData = self.conn.recv(1024).decode("utf-8")
                    userName, clientPort = userNameAndclientPortData.split(",")
                    self.updateClientPort(userName, clientPort)
                case "userName":
                    userIpAddrAndPortData = self.conn.recv(1024).decode("utf-8")
                    userIpAddr, userPort, type = userIpAddrAndPortData.split(",")
                    userNameData = self.getUserName(userIpAddr, userPort, type)
                    userName = userNameData.replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace(
                        "'", "").replace(",", "")
                    if userName == "":
                        self.sendMessage(self.conn, "Failure7")
                        self.sendMessage(self.conn, str(userName))
                case _:
                    print("Wrong centralServer Request -> " + str(request) + "\n")
                    self.sendMessage(self.conn, "Wrong centralServer Request!")

    # sendMessage
    def sendMessage(self, socket, message):
        socket.send(bytes(message, "utf-8"))

    def registerToTheSystem(self, conn, addr):
        userNameAndPasswordData = conn.recv(1024).decode("utf-8")
        userName, password = userNameAndPasswordData.split(',')
        db_password = db_ops.db_get_password(userName)

        if db_password == "fail" or db_password == "user does not exist":
            db_ops.db_add_user(userName, password, True, "", "")
            self.sendMessage(conn, "success")
            pass
        else:
            self.sendMessage(conn, "userExists")
            pass


    def joinToTheSystem(self, conn, addr):
        # gets the username, password, ip address, and port information
        userNamePasswordIpAddrAndPortData = conn.recv(1024).decode("utf-8")
        userName, password, ipAddr, port = userNamePasswordIpAddrAndPortData.split(',')

        # gets the users in the database
        db_password = db_ops.db_get_password(userName)
        if db_password == "fail":
            self.sendMessage(conn, "incorrectInfo")
            pass
        elif db_password == "user does not exist":
            self.sendMessage(conn, "incorrectInfo")
            pass
        elif db_password == password:
            self.sendMessage(conn, "success")
            ip_and_port = conn.recv(1024).decode("utf-8")
            ip_and_port = ip_and_port.split(",")

            db_ops.db_login(userName, ip_and_port[0],
                            ip_and_port[1])  # todo: [problem] port no and ip address varies somehow
            self.sendMessage(conn, "successful ip and port replacements")
            # i dont want to find its reason so let me try like this
            print(ip_and_port[0], ip_and_port[1])
            pass
        else:
            self.sendMessage(conn, "incorrectInfo")

    def searchInTheSystem(self, conn, addr):
        # gets the username to search
        searchedUserName = conn.recv(1024).decode("utf-8")
        # gets the records in the database

        op_result = db_ops.db_is_user_online(searchedUserName)
        if op_result == "fail":
            self.sendMessage(conn, "userCouldNotFound")
        elif op_result == "user does not exist":
            self.sendMessage(conn, "userCouldNotFound")
        elif op_result[0] == False:
            self.sendMessage(conn, "offlineUser")
        else:
            self.sendMessage(conn, "success")
            self.sendMessage(conn, (op_result[1] + "," + op_result[2]))

    # kill the thread
    def kill(self):
        self.running = 0

    def return_active_users(self, conn, addr):
        active_user_list = db_ops.get_active_users()
        message = db_ops.list_to_str(active_user_list)

        self.sendMessage(conn, message)

        pass

    def return_user_ınfo(self, conn,
                         addr):  # todo: check if other user wants to communicate with this one. in somewhere
        # receives username from client
        username = conn.recv(1024).decode("utf-8")

        user_connection_info = db_ops.db_is_user_online(username)

        # returns ip address and port number alon
        self.sendMessage(conn, user_connection_info[1] + "," + user_connection_info[2])

        pass


class Tcp(threading.Thread):  # CREATE MAIN THREAD FOR "TCP" OPERATIONS
    sockets = []

    def __init__(self):
        threading.Thread.__init__(self)
        self.HOST = ''
        self.PORT = 4004
        self.server_socket = None
        self.running = 1

    def run(self):  # Run the thread
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen(10)
        # add server socket object to the list of readable connections
        self.sockets.append(self.server_socket)

        print("TCP server started on port " + str(self.PORT) + "\n")

        while 1:
            ready_to_read, ready_to_write, in_error = select.select(self.sockets, [], [], 0)

            for sock in ready_to_read:
                # a new connection request recieved
                if sock == self.server_socket:
                    self.conn, self.addr = self.server_socket.accept()
                    self.sockets.append(self.conn)
                    print("Client (%s, %s) connected" % self.addr)
                    thread = centralServerInterface(self.conn, self.addr)
                    thread.start()

    def kill(self):
        self.running = 0



if __name__ == "__main__":
    # activates threads
    tcpThread = Tcp()
    tcpThread.start()
    udp_server.start_udp()
    # udpThread.start()
