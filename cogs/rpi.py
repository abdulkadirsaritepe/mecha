
# * https://www.raspberrypi.org/documentation/computers/using_linux.html
# * To run a command every time the Raspberry Pi starts up, write @reboot instead of the time and date. 
# * For example: @reboot python /home/pi/myscript.py
# * This will run your Python script every time the Raspberry Pi reboots. 
# * If you want your command to be run in the background while the Raspberry Pi continues starting up, add a space and & at the end of the line, like this:
# * @reboot python /home/pi/myscript.py &


import re
import time, sys, datetime, json, sqlite3

if sys.platform == "linux":
    import RPi.GPIO as GPIO
    import mfrc522
    logDir = "/home/pi/asbot/mekanik/cogs/Logs" #! 
else:
    GPIO = None
    mfrc522 = None
    logDir = "C:\Dev\Github\src\mekanik\cogs\Logs"

class RPi:
    def __init__(self) -> None:
        self.statusLedPin = 37
        self.doorLockPin = 11
        self.locked = False
        self.closed = True
        self.memberDatabase = None
        self.authorized = []
        self.approved = []
        self.reader = None
        if GPIO != None:
            self.initialize_rfid()
        self.initialize_database()
        self.get_data_from_database()
    
    def initialize_rfid(self):
        self.reader = mfrc522.SimpleMFRC522()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.statusLedPin, GPIO.OUT)
        GPIO.setup(self.doorLockPin, GPIO.OUT)
        GPIO.output(self.statusLedPin, False)
        GPIO.output(self.doorLockPin, False)

    def initialize_database(self):
        if sys.platform == "linux":
            dataDir = f'{logDir}/mechdata.db'
        else:
            dataDir = f'{logDir}\mechdata.db'
        self.memberDatabase = None
        self.connect_database(dataDir)
        if not self.memberDatabase:
            print("[INFO] Couldn't connect to the database!")
            answer = (str(input("[INPUT] Do you want to try again? (y/n) "))).lower()
            if answer == 'y':
                self.connect_database(dataDir)
                if self.memberDatabase:
                    print("[INFO] Couldn't connect to the database!")
                    answer = (str(input("[INPUT] Do you want to change the directory of database? (y/n) "))).lower(),
                    
                    if answer == 'y':
                        newDir = str(input("[INPUT] Enter the new directory: "))
                        dataDir = newDir
                        self.connect_database(dataDir)
                        if not self.memberDatabase:
                            print('[INFO] Successfully connected.')
                        else:
                            print('[ERROR] Check the database and try again!')
                            return
                    else:
                        return
                else:
                    print('[INFO] Successfully connected.')
            else:
                return
        else:
            print('[INFO] Successfully connected.')
        
        self.create_table()

    def connect_database(self, dataDir):
        n = 0
        while self.memberDatabase == None and n < 5:
            try:
                self.memberDatabase = sqlite3.connect(dataDir)
            except Exception as Err:
                print(f'Errorx3001: {Err}')
                n+=1

    def create_table(self):
        self.memberDatabase.execute('''CREATE TABLE IF NOT EXISTS MEMBERS
                            (
                            STATUS TEXT,
                            POSITION TEXT,
                            NAME TEXT,
                            SURNAME TEXT,
                            CARDID INT);''')

    def get_data_from_database(self):
        self.authorized = []
        self.approved = []
        members = self.list_members()
        for member in members:
            if str(member["status"]).lower() == "active":
                self.approved.append(member)
                if str(member["position"]).lower() == "board":
                    self.authorized.append(member)

    def add_member(self, status, position, name, surname, cardId):
        params = (status, position, name,surname,cardId)
        try:
            self.memberDatabase.execute('INSERT INTO MEMBERS VALUES (?,?,?,?,?)', params)
            self.memberDatabase.commit()
            self.get_data_from_database()
        except Exception as Err:
            print(f'Errorx3003: {Err}')

    def remove_member(self, name, surname=None):
        try:
            if surname == None:
                params = (name,)
                members = self.search_member_by_name(keyword=name)
                if len(members) == 1:
                    self.memberDatabase.execute('DELETE from MEMBERS where NAME = ?', params)
                elif len(members) > 1:
                    return 2
                else:
                    return 0
            else:
                params = (name, surname)
                self.memberDatabase.execute('DELETE from MEMBERS where NAME = ? and SURNAME = ?', params)
            self.memberDatabase.commit()
            self.get_data_from_database()
            return 1
        except Exception as Err:
            print(f'Errorx3002: {Err}')
    
    def clear_all(self, password=0):
        if password == "MetuMechAdmin":
            try:
                self.memberDatabase.execute('delete from MEMBERS')
                self.memberDatabase.commit()
            except Exception as Err:
                print(f'Errorx3002: {Err}')

    def list_members(self):
        members = []
        cursor = self.memberDatabase.execute("SELECT status, position, name, surname, cardid from MEMBERS")
        for member_data in cursor:
            member_info = {"status":member_data[0], "position":member_data[1], "name":member_data[2], "surname":member_data[3], "cardid":member_data[4]}
            members.append(member_info)
        return members

    def search_member_by_name(self, search_type=0, keyword=None):
        try:
            if search_type == 0:
                params = (f'{keyword}',)
            elif search_type == 1:
                params = (f'%{keyword}%',)
            elif search_type == 2:
                params = (f'{keyword}%',)
            elif search_type == 3:
                params = (f'%{keyword}',)
            else:
                return
            result = (self.memberDatabase.execute('SELECT status, position, name, surname, cardid FROM MEMBERS WHERE name LIKE ?', params)).fetchall()
            members = []
            for member_data in result:
                member_info = {"status":member_data[0], "position":member_data[1], "name":member_data[2], "surname":member_data[3], "cardid":member_data[4]}
                members.append(member_info)
            return members
        except Exception as Err:
            print(f'Errorx3002: {Err}')
    
    def search_member_by_cardid(self, cardid=None):
        if type(cardid) != int:
            return
        try:
            params = (f'{str(cardid)}',)
            result = (self.memberDatabase.execute('SELECT status, position, name, surname, cardid FROM MEMBERS WHERE cardid LIKE ?', params)).fetchall()
            members = []
            for member_data in result:
                member_info = {"status":member_data[0], "position":member_data[1], "name":member_data[2], "surname":member_data[3], "cardid":member_data[4]}
                members.append(member_info)
            return members
        except Exception as Err:
            print(f'Errorx3002: {Err}')

    def mech_door(self):
        if len(self.approved) == 0:
            self.get_data_from_database()
        if len(self.approved) == 0:
            return None, None
        try:
            cardid, cardtag = self.reader.read()
            for member in self.approved:
                if int(cardid) == int(member["cardid"]):
                    result = (f'{str(member["name"])} {str(member["surname"])}', int(cardid))
                    trespassing = True
                    break
                else:
                    trespassing = False
            if trespassing:
                return trespassing, result
            else:
                return trespassing, int(cardid)
        except Exception as Err:
            print(f'Errorx---: {Err}')
            return None, None

    def open_door(self):
        GPIO.output(self.statusLedPin, True)
        GPIO.output(self.doorLockPin, True)
        time.sleep(2)
        GPIO.output(self.statusLedPin, False)
        GPIO.output(self.doorLockPin, False)

    def quit_rpi(self):
        self.memberDatabase.close()
        GPIO.cleanup()

