#!/usr/bin/env python3

from getpass import getpass
import crypt
import sys
import os
import random

def checking_root():
    if ( os.getuid() != 0 ):
        print ("[!]The Script should be run as root")
        sys.exit()
    else:
        pass

#Nos devuelve el hash encriptado <str>
def generate_password(clear_password):
    password = crypt.crypt(clear_password)
    return password
#Crea el directorio home y cambia los permisos
def user_prerequisites(username):
    home_dir = "mkdir /home/%s"%username
    h_dir="/home/%s"%username
    change_permissions = "chown %s:%s %s && chmod 700 %s"%(username,username,home_dir.split()[1],h_dir)
    try:
        os.system(home_dir)
        os.system(change_permissions)
    except:
        print ("[!] Something went wrong with the user %s")%username
def check_for_users(username):
    passwd = open("/etc/passwd", 'r')
    passwd_data = passwd.readlines()

    for user in passwd_data:
        if username ==  user.split(":")[0]:
            print ("[!] User already on the system")
            sys.exit()


#Agrega el usuario a passwd ( uid debe de ser el comienzo del rango de uid)
def add_passwd(username,uid=None):
    check_for_users(username)
    passwd = open("/etc/passwd", 'r')
    passwd_data = passwd.readlines()

    if ( uid == None ):
        print ("[!] The UID Will generate automatically")
        uid = random.randrange(1000,6000)
    else:
        for user in passwd_data:
            try:
                if ( uid in user.split(":")[2] ):
                    uid = uid +1
            except:
                pass

    home_directory = "/home/%s"%(username)
    terminal = "/bin/zsh"
    user_line = "%s:x:%s:%s:%s:%s:%s"%(username,uid,uid,username,home_directory,terminal)
    passwd = open("/etc/passwd", 'a')
    passwd.write(str(user_line)+"\n")
    passwd.close()
    #Creamos el grupo para el usuario invidual
    group_line = "%s:x:%s:"%(username,uid)
    group = open("/etc/group",'a')
    group.write(group_line+"\n")
    group.close()

def add_shadow(username,password):
    encr_password = generate_password(password)
    user_line = "%s:%s:17495:0:99999:7:::"%(username,encr_password)
    try:
        shadow = open("/etc/shadow", 'a')
        shadow.write(user_line+"\n")
    except:
        print("[!] Failure with /etc/shadow")

def add_user(username,password, uid=None):
    add_passwd(username,uid)
    if (password == " "  ):
        password = getpass()
    else:
        password = password

    add_shadow(username,password)
    user_prerequisites(username)

if __name__ == "__main__":
    checking_root()
    if ( len(sys.argv) != 3 ):
        print ("[!]Usage: UManagement.py id-user user1:uid --> ADD with custom UID")
        print ("[!]Usage: UManagemet.py users user1:user2 --> ADD A list with random UID")
        print ("[!]Usage: UManagement.py list wordlist_usernames --> ADD a list of users")
        print ("[!] INFO: List should be user:password format")
    else:
        if ( sys.argv[1] == "id-user" ):
            u_data = sys.argv[2].split(":")
            username = u_data[0]
            uid = u_data[1]
            add_user(username," ",uid)

        if ( sys.argv[1] == "users" ):
            for user in sys.argv[2].split(":"):
                add_user(user, " ")

        if ( sys.argv[1] == "list"):
            file_open = open(sys.argv[2], 'r')
            file_data = file_open.readlines()
            for user in file_data:
                userpass = user.strip().split(":")
                username = userpass[0]
                password = userpass[1]
                print ( username +" "+password )
                add_user(username,password)
