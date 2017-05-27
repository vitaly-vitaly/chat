import socket, select, time
import sys
from sys import argv
from thread import *


# list of all chanels
chanell_list = [('all', '')]

# this structure has fields:
# string name    - name of user in chat
# socket socket  - socket appropirated current connection of this user
# string chanell - current chanell of user
conn_list = [ ]

# this structure has fields:
# string login    - login of user
# string password - password of user
# string name     - name of user in chat
user_list = [ ]

#get world from client
def get_word(conn):
    reply = ''
    while 1:
        ch = conn.recv(1)
        if ch == '\r':
            break
        if ch == '\n':
            continue
        reply += ch
    return reply


def log(level, msg):
    start_time = time.gmtime()
    cur_time = "{hour}:{minute}:{second}".format(
            hour=start_time.tm_hour,
            minute=start_time.tm_min,
            second=start_time.tm_sec,
        )
    print "{time}\t{level}\t{msg}".format(
        time=cur_time,
        level=level,
        msg=msg,
    )


# send message to chat (used for both common and system message)
def send_to_chat(reply, name):
    cur_chanell = ''
    for (val1, val2, val3) in conn_list:
        if val1 == name:
            cur_chanell = val3
            break

    for (val1, val2) in chanell_list:
        if val1 == cur_chanell:
            chanell_list.remove((val1, val2))
            chanell_list.append((val1, val2 + reply))
            break
    
    for (val1, val2, val3) in conn_list:
        if val1 == name:
            continue

        if val3 != cur_chanell:
            continue
        
        val2.send('\r' + '[' + cur_chanell + '] ' + reply)
        val2.send('[' + cur_chanell + '] ' + 'You: ')

# join to chat with default chanell (all)
def join_to_chat(conn):
    conn.send('Welcome to chat. Please choose, would you like to sign in(S) or register(R).\n\r')
    move = '' #will be used for keeping register type

    while True:
        move = get_word(conn)
        if move != 'R' and move != 'S':
            conn.send('Please, enter S(sign in) or R(register)\n\r')
            continue
        break

    if move == 'S':
        conn.send('Please, enter your login and password.\n\r')

        while True:
            conn.send('Login: ')
            login = get_word(conn)
            conn.send('Password: ')
            password = get_word(conn)

            is_joined = False
            for (val1, val2, val3) in user_list:
                if val1 == login and val2 == password:
                    for (v1, v2, v3) in conn_list:
                        if val3 == v1:
                            is_joined = True
                            break
                    if is_joined == True:
                        break
                    
                    conn.send('Welcome, ' + val3 + '\n\r')
                    conn_list.append((val3, conn, 'all'))
                    return val3

            if is_joined == True:
                conn.send('This user is already joined to chat\n\r')
            else:
                conn.send('Login or password is wrong. Please try again\n\r')

    if move == 'R':
        conn.send('Please, enter your personal data:\n\r')

        conn.send('Login: ')
        while True:
            login = get_word(conn)
            is_login_used = False
            for (val1, val2, val3) in user_list:
                if login == val1:
                    is_login_used = True
                    break
            if is_login_used == True:
                conn.send('Sorry, but this login is already registered. Please enter other login: ')
                continue
            break        

        conn.send('Password: ')
        password = get_word(conn)        

        conn.send('Please, enter you name: ')
        while True:
            name = get_word(conn)
            if len(name) < 2:
                conn.send('Please, enter name with length 2 or more characters:')
                continue

            is_name_used = False
            for (val1, val2, val3) in user_list:
                if name == val3:
                    is_name_used = True
                    break
            if is_name_used == True:
                conn.send('Sorry, but this name is already used. Please enter other name: ')
                continue

            break
        
        conn.send('Register is done well!\n\r')
        conn.send('======================\n\r\n\r')

        user_list.append((login, password, name))
        conn_list.append((name, conn, 'all'))

        return name

# if we get command, try to execute it
# return value mean, are we need exit from command reading cycle or not
def exec_command(reply, name, conn):
    if   reply == '!help':
        conn.send('Available commands list:\n\r')
        conn.send('!reglist       - show registered users list\n\r')
        conn.send('!online        - show online list\n\r')
        conn.send('!channels      - show list of all available chanell\n\r')
        conn.send('!join          - join another channel\n\r')
        conn.send('!history       - show chat history\n\r')
        conn.send('!exit          - exit chat\n\r')
        return False
    elif reply == '!exit':
        log("DEBUG", "User disconnected")
        for (val1, val2, val3) in conn_list:
            if val1 == name:
                send_to_chat(name + ' exit from chat\n\r', name)
                conn_list.remove((val1, val2, val3))
                return True
    elif reply == '!reglist':
        conn.send('List of all users, registered in program:\n\r')
        for (val1, val2, val3) in user_list:
            conn.send(val3 + '\n\r')
        return False
    elif reply == '!online':
        conn.send('List of all users, which are being in chat now:\n\r')
        for (val1, val2, val3) in conn_list:
            conn.send(val1 + '\n\r')
        return False
    elif reply == '!channels':
        conn.send('List of all available chanell:\n\r')
        for (val1, val2) in chanell_list:
            conn.send(val1 + '\n\r')
        return False
    elif reply == '!join':
        conn.send('Enter name of chanell, which you want to use: ')
        chname = get_word(conn)
        is_need_create = True
        for (val1, val2) in chanell_list:
            if val1 == chname:
                is_need_create = False
                break
        if is_need_create == True:
            chanell_list.append((chname, ''))

        for (val1, val2, val3) in conn_list:
            if name == val1:
                conn_list.remove((val1, val2, val3))
                conn_list.append((val1, val2, chname))
                return False
    elif reply == '!history':
        conn.send('Chat history\n\r')
        conn.send('============\n\r')
        chanell = ''
        for (val1, val2, val3) in conn_list:
            if val1 == name:
                chanell = val3
                break
        for (val1, val2) in chanell_list:
            if val1 == chanell:
                conn.send(val2)
                conn.send('============\n\r')
                return False
    else:
        conn.send('Command was not found. Please try again.\n\r')
        return False

# function of each user
def start_user_thread(conn):
    name = join_to_chat(conn)
    log("DEBUG", "Connected new user")
    send_to_chat(name + ' joined to chat\n\r', name)
    
    while True:
        cur_chanell = ''
        for (val1, val2, val3) in conn_list:
            if val1 == name:
                cur_chanell = val3
                break
        
        conn.send('[' + cur_chanell + '] ' + 'You: ')
        reply = get_word(conn)

        is_need_exit = False
        if reply[0] == '!':
            is_need_exit = exec_command(reply, name, conn)
        else:
            reply = name + ': ' + reply + '\n\r'
            send_to_chat(reply, name)

        if is_need_exit == True:
            break

    conn.close()

def main():
    if len(argv) != 2:
        print "Usage: python server.py port"
        return

    host = '0.0.0.0'
    host = '10.55.160.252'
    port = int(argv[1])

    if port <= 1024 or port >= 65536:
        print "incorrect port"
        return

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    s.listen(10)

    log("DEBUG", "Start server on %s:%d" % (host, port))  
    while True:
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])

        start_new_thread(start_user_thread ,(conn,)) 
    s.close()


if __name__ == '__main__':
    main()
