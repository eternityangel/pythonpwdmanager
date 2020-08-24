import sqlite3
import os
import sys
import signal
import secrets
import cryptography
from cryptography.fernet import Fernet
from time import sleep


def createConn(val):
    conn = sqlite3.connect(DB_FILE)
    if val == 1:
        if conn:
            cur = conn.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS data(id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT, service TEXT NOT NULL, username TEXT UNIQUE NOT NULL DEFAULT "null", password TEXT NOT NULL, email TEXT NOT NULL, name TEXT)')
            conn.commit()
            pass
        else:
            print('Connection failed')
            sys.exit(1)
        options(conn, cur)
    if val == 2:

        return conn

def handleFiles():
    DB_DIR_EXISTS = os.path.exists(DB_DIRECTORY)
    DB_FILE_EXISTS = os.path.exists(DB_FILE)
    DB_KEYFILE_EXISTS = os.path.exists(DB_KEYFILE)
    if DB_DIR_EXISTS == True:
        if DB_FILE_EXISTS == True:
            if DB_KEYFILE_EXISTS == True:
                createConn(1)
            else:
                key = Fernet.generate_key()
                file = open(DB_KEYFILE, 'wb')
                file.write(key)
                file.close()
                pass
        else:
            file = open(DB_FILE, "w")
            file.close()
            pass
    else:
        os.mkdir(DB_DIRECTORY)
        pass
    handleFiles()
try:
    if sys.version_info[0] < 3:
        sys.exit('Please use python version 3 or newer to run this script.')

    DB_DIRECTORY = os.path.expandvars('$HOME/.passwordmanager')
    DB_FILE = os.path.expandvars('$HOME/.passwordmanager/db.db')
    DB_KEYFILE = os.path.expandvars('$HOME/.passwordmanager/key.key')


    def exit(conn):
        if conn:
            conn.close()
        print(txtcolor.FAIL + '     exit\n' + txtcolor.ENDC)
        sys.exit(1)

    class txtcolor:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    def yes_or_no(question):
        while "the answer is invalid":
            reply = str(input(question+' (y/n): ')).lower().strip()
            if reply[0] == 'Y' or reply[0] == 'y':
                return True
            if reply[0] == 'n' or reply[0] == 'n':
                return False

    def clearScreen():
        print('\033[2J')

    def decodepwd(data):
        key = getKey()
        f = Fernet(key)
        encryptedpwds = data
        securepwd = f.decrypt(encryptedpwds)
        decodedsecurepwd = securepwd.decode('utf-8')
        return decodedsecurepwd
    try:
        def showpass(answer, conn, cur):
            if answer == "search":
                serv = str(input('search by service: '))
                if serv:
                    service = serv
                else:
                    return
                findQuery = "SELECT * FROM data WHERE service LIKE '%{}%'".format(service)
                # Pythonin Sqlite3 on vähän höveli, ja tarvitsee tuon prosentin
                # lisättynä parametriin. Jep. pöljää.
                cur.execute(findQuery)
                results = cur.fetchall()
                if len(results) != 0:
                    print(txtcolor.OKGREEN + "Known records with '"+service+"' in service name:\n" + txtcolor.ENDC)
                    for row in results:
                        decodedsecurepwd = decodepwd(row[3])
                        print(txtcolor.OKGREEN + txtcolor.BOLD + "Id: ", row[0])
                        print("Service: ", row[1])
                        print("Username: ", row[5])
                        print("Password: ", decodedsecurepwd)
                        print("Email: ", row[4])
                        print("Name: ", row[2]+"\n"+txtcolor.ENDC)
                else:
                    print(txtcolor.WARNING+'    No records found!'+txtcolor.ENDC)
            elif answer == "all":
                cur.execute("SELECT * FROM data")
                rows = cur.fetchall()
                print(txtcolor.OKGREEN + "Known records:\n" + txtcolor.ENDC)
                if len(rows) != 0:
                    for row in rows:
                        decodedsecurepwd = decodepwd(row[3])
                        print(txtcolor.OKGREEN + txtcolor.BOLD + "Id: ", row[0])
                        print("Service: ", row[1])
                        print("Username: ", row[5])
                        print("Password: ", decodedsecurepwd)
                        print("Email: ", row[4])
                        print("Name: ", row[2]+"\n"+txtcolor.ENDC)

                else:
                    print('    No records found!')

    except cryptography.fernet.InvalidSignature:
        sometext = txtcolor.FAIL + 'Bad Authentication Token. Exiting...' + txtcolor.ENDC
        sys.exit(sometext)
    except cryptography.fernet.InvalidToken:

        sometext = txtcolor.FAIL + 'Bad Authentication Token. Exiting...' + txtcolor.ENDC
        sys.exit(sometext)

    def handlePasswords(answer, conn, cur):
        int(answer)
        if answer == 3:
            ask = txtcolor.BOLD+txtcolor.OKBLUE+'Service (required): '+txtcolor.ENDC
            service = str(input(ask))
            ask = txtcolor.BOLD+txtcolor.OKBLUE+'Username (required): '+txtcolor.ENDC
            name = str(input(ask))
            ask = txtcolor.BOLD+txtcolor.OKBLUE+'Email (required): '+txtcolor.ENDC
            email = str(input(ask))
            ask = txtcolor.BOLD+txtcolor.OKBLUE+'Name (not required): '+txtcolor.ENDC
            username = str(input(ask))
            ask = txtcolor.BOLD+txtcolor.OKBLUE+'Password strength (required): '+txtcolor.ENDC

            print(txtcolor.BOLD+txtcolor.OKGREEN+"How strong your password needs to be?")
            print('1. Not so (8 letters/numbers) ')
            print('2. Medium (12 letters/numbers)')
            print('3. Strong (16 letters/numbers), default')
            print('4. Stronger (20 letters/numbers)')
            print('5. Strongest (32 letters/numbers)')

            try:
                passwordinput = int(input(ask))
            except ValueError:
                print("That's not a number, try again!")
                options(conn, cur)
            if passwordinput > 0:
                if passwordinput == 1:
                    password = secrets.token_hex(4)
                elif passwordinput == 2:
                    password = secrets.token_hex(6)
                elif passwordinput == 3:
                    password = secrets.token_hex(8)
                elif passwordinput == 4:
                    password = secrets.token_hex(10)
                elif passwordinput == 5:
                    password = secrets.token_hex(16)
                else:
                    password = secrets.token_hex(8)
            
            key = getKey()
            message = password
            notEncrypted = message.encode()
            f = Fernet(key)
            encrypted = f.encrypt(notEncrypted)
            sql = "INSERT INTO data(service, username, password, email, name) VALUES (?, ?, ?, ?, ?)"
            values = [service, username, encrypted, email, name]
            cur.execute(sql, values)
            conn.commit()
            print(cur.lastrowid,"rows affected")
            print(txtcolor.ENDC)
            options(conn, cur)

        elif answer == 8:
            deletebyid = str(input('delete record by id: '))
            deleteQuery = "DELETE FROM data WHERE id='{}';".format(deletebyid)
            cur.execute(deleteQuery)
            conn.commit()
            print("\n",cur.rowcount, "rows affected")

        elif answer == 9:
            value = yes_or_no('Proceed? This action cannot be undone.')
            if value == True:
                cur.execute('DROP TABLE data;')
                cur.execute('CREATE TABLE IF NOT EXISTS data(id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT, service TEXT NOT NULL, username TEXT UNIQUE NOT NULL DEFAULT "null", password TEXT NOT NULL, email TEXT NOT NULL, name TEXT)')
                conn.commit()

            else:
                print("\n",cur.rowcount, "rows affected")
                options(conn, cur)
    def getKey():
        file = open(DB_KEYFILE, 'rb')
        key = file.read()
        file.close()
        return(key)

    def options(conn, cur):
        os.system('clear')
        sleep(1)
        print(txtcolor.WARNING+txtcolor.BOLD+'\n[+] Sleeping second after continuing...'+txtcolor.ENDC)
        sleep(1)
        while True:
            print(txtcolor.BOLD + txtcolor.OKBLUE)
            print('Options: \n')
            print('    1. Search passwords')
            print('    2. Show all passwords')
            print('    3. Create passwords')
            print(txtcolor.ENDC + txtcolor.BOLD + txtcolor.FAIL)
            print('    8. Delete record')
            print('    9. Delete all records')
            print('    0. Exit' + txtcolor.ENDC)
            print('')
            try:
                optionask = txtcolor.OKGREEN+'  (option) > '+txtcolor.OKBLUE+txtcolor.BOLD
                answer = int(input(optionask))
                print(txtcolor.ENDC)
            except ValueError:
                print("\nUgh, that's not a number! Try again.")
                continue
            if answer == 1:
                showpass("search", conn, cur)
            elif answer == 2:
                showpass("all", conn, cur)
            elif answer == 3:
                handlePasswords(answer, conn, cur)
            elif answer == 8:
                handlePasswords(answer, conn, cur)
            elif answer == 9:
                handlePasswords(answer, conn, cur)
            elif answer == 0:
                conn.close()
                exit(conn)

            else:
                print("Ugh, that's not a choice! Try again.")


            

    if __name__ == "__main__":
        handleFiles()
except KeyboardInterrupt:
    exit(createConn(2))
except EOFError:
    exit(createConn(2))