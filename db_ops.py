import pypyodbc

# https://kerteriz.net/python-ile-mssql-veritabani-baglantisi-islemleri/

db = pypyodbc.connect(
    'Driver={SQL Server};'
    'Server=NBS086;'
    'Database=p2p;'
    #'Trusted_Connection=Yes'
    'UID=p2pAdmin;'
    'PWD=543543;'
)

cursor = db.cursor()


# temp solution
def active_user(username):
    query = "update users set is_online = ?  where username = ?"
    cursor.execute(query, (True, username))
    cursor.commit()


def get_active_users():
    query = "select u.username from users u where u.is_online = 'True' "
    cursor.execute(query)
    usernames = cursor.fetchall()
    username_list = []
    for username in usernames:
        username_list += username

    return username_list


def list_to_str(list):
    data = ""
    for element in list:
        data += "," + element

    return data[1:]


def db_add_user(username, password, is_online=False, ip_address="", port=""):
    query = 'INSERT INTO users VALUES(?,?,?,?,?)'
    data = [username, password, is_online, ip_address, port]

    try:
        cursor.execute(query, data)
        db.commit()
        return True
    except:
        return False


def db_logout(username):
    query = 'update users set is_online = ?  where username = ?'
    try:
        cursor.execute(query, (False, username))
        db.commit()
        return True
    except:
        print("an error occurred at updating online status")
        return False


def db_login(username, ip_address, port):
    query = 'update users set is_online = ?, ip_address=?, port=? from users where username = ?'
    try:
        cursor.execute(query, (True, ip_address, port, username))
        db.commit()
        return True
    except:
        print("an error occurred at updating online status")
        return False


# you give the username and get password else returns -1
def db_get_password(username):
    try:
        cursor.execute("select u.username, u.password from users as u")
        result = cursor.fetchall()
        for element in result:
            if element[0] == username:
                return element[1]

        return "user does not exist"
    except:
        return "fail"


def db_is_user_online(username):
    try:
        cursor.execute("select u.username, u.is_online, u.ip_address, u.port from users as u")
        result = cursor.fetchall()
        for element in result:
            if element[0] == username:
                return element[1:]

        return "user does not exist"
    except:
        return "fail"


# print(db_is_user_online("username"))

'''
db_is_user_online("username")
print(db_get_password("sena1"))
print(db_update_online_status("sena1", True))
print(db_add_user("username1", "password", True, "hi", "hi2"))
'''

if __name__ == '__main__':
    print (get_active_users())
