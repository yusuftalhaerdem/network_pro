# this is just a copy of peer.py, which is created for test purposes

import os, sys, socket, select, threading, _thread, time, datetime

UDPHelloMessage = False
join = False
admin = False
userIsBusy = False


def ask_user_for_active_user_selection(active_user_list):
    print("active users:  ")
    if len(active_user_list) == 0:
        print("Your friend list is empty. You can search users and add them as a friend!  ")
        return -1
    for number in range(len(active_user_list)):
        print("[" + str(number) + "]" + active_user_list[number])

    while True:
        try:
            user_no = int(input("please enter the [no] of user you want to chat with "))
            if user_no == -1:
                return -1
            elif user_no < len(active_user_list):
                return user_no
        except:
            print("you entered something wrong, please enter a valid user number. \n you can enter -1 to quit")


class p2pChatCentralClient(threading.Thread):  # CENTRAL_CLIENT THREAD
    conversationList = []

    def __init__(self):
        threading.Thread.__init__(self)
        self.password = None
        self.userName = None
        self.peer_name = None
        self.thread_2 = None
        self.user_listening = None
        self.thread = None
        self.peer2_addr = None
        self.addr = None
        self.port_no = None
        self.ip_address = None
        self.peer2_socket = None
        self.HOST = 'localhost'
        self.PORT_TCP = 4004  # central tcp_port
        self.UDP_PORT = 4050
        self.UDP_IP = "192.168.56.1"
        self.UDP_ADDR = (self.UDP_IP, self.UDP_PORT)
        self.central_client_socket = None
        self.startTime = 0
        self.endTime = 0
        self.runProgram = 1

    def get_message(self):
        return self.central_client_socket.recv(1024).decode("utf-8")

    def send_message(self, message):
        self.central_client_socket.send(message.encode("utf-8"))

    def send_message_peer(self, message):
        self.peer2_socket.send(message.encode("utf-8"))

    def run(self):
        self.central_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Socket successfully created \n")
        self.central_client_socket.settimeout(2)
        self.central_client_socket.connect((self.HOST, self.PORT_TCP))
        print("Socket successfully connected \n")
        print("*****************P2P CHAT APPLICATION*****************\n")

        while self.runProgram == 1:

            while True:
                choice = str(input("Click 1 to register if you do not have an account, or 2 to log in if you do.\n"
                                   ">>>"))
                match choice:
                    case "1":
                        self.registerToTheSystem()
                        break
                    case "2":
                        self.joinToTheApp()
                        # send logout req
                        self.startTime = time.time()
                        self.kill()
                        break
                    case _:
                        print("Please enter a valid number! \n ")


    def registerToTheSystem(self):  # REGISTER OP

        # sends register message
        while True:
            centralClient.central_client_socket.send(bytes("register", "utf-8"))
            print("---------------To register, enter your username and password.-------------- \n")
            print("*Your username should be unique! \n")

            while True:
                self.userName = str(input(">>>username: "))
                self.password = str(input(">>>password: "))
                # validations for username and password
                if (self.userName == "") or (self.password == ""):
                    print("You cannot leave the username or the password blank!\n")
                elif len(self.userName) < 5:
                    print("Your username should have at least 5 character!\n")
                elif len(self.password) < 8 or not has_numbers(self.password):
                    print("Your password should have at least 8 character and at least 1 digit!\n")
                else:
                    break

            data = str(self.userName + "," + self.password)

            # send the username and password to the central server
            centralClient.central_client_socket.send(bytes(data, "utf-8"))

            # receive the registration status from the central server
            registrationStatus = centralClient.central_client_socket.recv(1024).decode("utf-8")

            match registrationStatus:
                case "userExists":
                    print("This username is registered in the system! Please choose another username. \n")
                    continue
                case "success":
                    print("You have successfully signed up. You can login to the system at any time with this "
                          "username and password. \n")
                    break
                case _:
                    print("Incorrect data for 'register' \n")

    def joinToTheApp(self):  # JOIN OPERATION
        # sends join message to the central server

        while True:
            centralClient.central_client_socket.send(bytes("join", "utf-8"))
            print("---------------To join, enter your username and password.--------------\n")

            # validations for username and password
            while True:
                self.userName = str(input(">>>username: "))
                self.password = str(input(">>>password: "))
                if self.userName == "" or self.password == "":
                    print("You cannot leave the username or the password blank! \n")
                else:
                    break
            chat.ipAddress()
            data = str(self.userName + "," + self.password + "," + chat.HOST + "," + str(chat.PORT))

            # sends the username and password to the central server
            centralClient.central_client_socket.send(bytes(data, "utf-8"))

            # gets the login status from the central server
            loginStatus = centralClient.central_client_socket.recv(1024).decode("utf-8")

            match loginStatus:
                case "incorrectInfo":
                    print("User name or password is incorrect! Try again.\n")
                    continue
                case "success":
                    self.create_udp_thread()
                    self.create_port_listen()
                    # msg_to_send = self.ip_address + "," + str(self.port_no)
                    # self.send_message(msg_to_send)
                    msg_rcvd = self.get_message()
                    if msg_rcvd == "successful ip and port replacements":
                        print("server is active and server is informed")

                    print("You have successfully joined!\n")
                    print("********************Welcome to P2P chatting Application**********************\n")
                    print("In this application, you can "
                          "search for a person by username and start chatting right away!\n\n"
                          "*****************************************************************************\n")
                    global join
                    join = True
                    self.userStatus = False
                    global UDPHelloMessage
                    UDPHelloMessage = True
                    while True:
                        print("Please, select what you want to do!\n"
                              "Press:\n"
                              "     1 to search user by username\n"
                              "     2 to chatting\n"
                              "     3 to exit\n")

                        choice = str(input())
                        match choice:
                            case "1":  # search
                                searchedUsersIPandPort, username = self.searchUser()  #
                                if searchedUsersIPandPort == "back":
                                    continue
                                while True:
                                    addUser = str(input("If you want to add this user to your"
                                                        " chat list press 1, otherwise press 2 to continue."))
                                    match addUser:
                                        case "1":
                                            self.conversationList.append(username)  # todo: dunno2
                                            self.userStatus = True
                                            print(f"User {addUser} is successfully added in your chat list.\n"
                                                  "You can only chat with the people in your chat list,\n")
                                            break
                                        case "2":
                                            break
                                        case _:
                                            print("Invalid input!")
                                continue

                            case "2":  # chat

                                #  basics
                                socket_client = centralClient.central_client_socket
                                FORMAT = "utf-8"
                                MESSAGE_SIZE = 1024


                                # sends a request to get active user list.

                                data = "get active user list"
                                self.send_message(data)

                                active_user_str = socket_client.recv(MESSAGE_SIZE).decode(FORMAT)
                                active_user_list = active_user_str.split(",")

                                activeUserInTheChatLst = list()
                                for i in active_user_list:
                                    for j in self.conversationList:
                                        if i == j:
                                            activeUserInTheChatLst.append(i)

                                user_no = ask_user_for_active_user_selection(activeUserInTheChatLst)
                                if user_no == -1:
                                    continue
                                selected_user_name = activeUserInTheChatLst[user_no]

                                message = "get user info"
                                socket_client.send(message.encode(FORMAT))

                                socket_client.send(selected_user_name.encode(FORMAT))

                                user_info = socket_client.recv(MESSAGE_SIZE).decode(FORMAT)

                                peer_ip, peer_port = user_info.split(",")
                                self.peer2_addr = (peer_ip, int(peer_port))

                                # now we will try to connect with other user.

                                self.peer2_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                self.peer2_socket.connect(self.peer2_addr)

                                self.send_message_peer(self.userName)
                                # socket.timeout(999)
                                # answer_message = self.peer2_socket.recv(1024).decode("utf-8")

                                # socket.timeout(None)

                                self.start_listening_user()
                                self.thread.join()
                                return

                            case "3":
                                exit()
                                return
                            case _:
                                print("Invalid input! \n")
                    break

    def searchUser(self):  # SEARCH OPERATION
        # sends search message to the central server
        while True:
            centralClient.central_client_socket.send(bytes("search", "utf-8"))
            searchedUsersIPandPort = []

            while True:
                self.nameOfTheUser = str(input(">>Enter the username you want to search: \n"))
                if self.nameOfTheUser != "":
                    break
                else:
                    print("You should enter an username to be able to search one!")

            # sends the username to the central server
            centralClient.central_client_socket.send(bytes(self.nameOfTheUser, "utf-8"))
            # receives the search status, ip and port from the central server
            searchStatus = centralClient.central_client_socket.recv(1024).decode("utf-8")
            match searchStatus:
                case "userCouldNotFound":
                    print("We do not have an user with the username you entered in our system!\n")
                    return "back", ""
                case "offlineUser":
                    print("The user with the username you entered is not online at the moment. "
                          "You can try again later.\n")
                    return "back", ""
                case "success":
                    centralClient.central_client_socket.send("temp".encode("utf-8"))

                    ip, port = centralClient.central_client_socket.recv(1024).decode("utf-8").split(',')
                    searchedUsersIPandPort = [ip, port]
                    print("\nIP address of the user is: " + ip + "\t Port number of the user is: " + port)
                    return searchedUsersIPandPort, self.nameOfTheUser
                case _:
                    print("Sorry, something went wrong! Try again")

    def emptyChatList(self):
        self.conversationList = []

    def kill(self):
        self.runProgram = 0

    def find_available_port_no(self):
        ip = socket.gethostbyname(socket.gethostname())  # getting ip-address of host
        serv = None
        # i didnt wanna use first 9000 port just in case of some system programs wants to use them
        for port in range(56535):  # check for all available ports

            try:
                serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a new socket
                serv.bind((ip, port + 9000))  # bind socket with address
                return port + 9000
            except:
                print('failed to open port no :', (port + 9000))  # print open port number

            serv.close()  # close connection
        pass

    def start_listening_socket(self, port_no):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # peer_ip = socket.gethostbyname(socket.gethostname)
        server.bind((self.ip_address, port_no))
        server.listen(3)
        thread = threading.Thread(target=self.handle_server, args=(server, ""))
        self.thread = thread
        thread.start()

    def handle_server(self, server, nothing):
        conn, addr = server.accept()
        # peer_name = conn.recv(1024).decode("utf-8")
        self.peer_name = conn.recv(1024).decode("utf-8")
        msg = ""
        while msg != "-1":
            msg = conn.recv(1024).decode("utf-8")
            print("[" + self.peer_name + "]" + msg)

        return


    def create_port_listen(self):
        FORMAT = "utf-8"
        # but first, we will try to create a port and listener
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.port_no = self.find_available_port_no()
        is_available = True

        try:
            self.start_listening_socket(self.port_no)
        except:
            is_available = False
            print("error creating a socket for listening")

        if is_available:
            self.send_message((self.ip_address + "," + str(self.port_no)))
            self.addr = (self.ip_address, self.port_no)
        else:
            self.send_message("failure")

        pass

    def start_listening_user(self):

        print("user accepted chat request")
        print("you can write -1 to end chat.")
        input_msg = ""
        while input_msg != "-1":
            input_msg = input()
            self.send_message_peer(input_msg)
        pass

    def start_udp_client(self):
        udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            time.sleep(6)
            udp_client.sendto(self.userName.encode("utf-8"), self.UDP_ADDR)
            # print("msgs are sent")

    def create_udp_thread(self):
        thread = threading.Thread(target=self.start_udp_client)
        thread.start()
        pass


class Chat(threading.Thread):  # CHAT SERVER THREAD
    sockets = []

    def __init__(self):
        threading.Thread.__init__(self)
        self.HOST = self.ipAddress()
        self.PORT = 0  # otomatik 1024-65535 arasinda uygun bir porta atama yapar.
        self.server_socket = None
        self.conn = None
        self.serverTextStart = True
        self.running = 1
        self.sock = None

    def ipAddress(self):
        # finds the users ip address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect(("8.8.8.8", 80))
        self.HOST = self.sock.getsockname()[0]
        self.PORT = self.sock.getsockname()[1]
        self.sock.close()
        return self.HOST


# checks if the input string has number
def has_numbers(str):
    return any(char.isdigit() for char in str)


if __name__ == "__main__":
    chat = Chat()
    centralClient = p2pChatCentralClient()

    # chat_client = Chat_Client("", 0, "LobyParticipant")
    # text_input = Text_Input()

    chat.start()  # baglanma isteklerini dinler            ** ** ** ** **
    centralClient.start()  # merkezi server ile iletisimi saglar
