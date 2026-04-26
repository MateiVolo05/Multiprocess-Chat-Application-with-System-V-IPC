import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db="database.db"):
        self.db_path = db
        self.initDb()
    def initDb(self):
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS ACCOUNTS(id INTEGER PRIMARY KEY AUTOINCREMENT, nume VARCHAR(100) NOT NULL, email VARCHAR(100) NOT NULL UNIQUE, password VARCHAR(100) NOT NULL)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS MESSAGES(id INTEGER PRIMARY KEY AUTOINCREMENT, senderId INTEGER, receiverId INTEGER, message VARCHAR(100), timestamp VARCHAR(100))''')
            db.commit()
            cursor.close()
    def getAccount(self, email, password):
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            cursor.execute('''SELECT id FROM ACCOUNTS WHERE email = ? AND password = ?''', (email, password))
            accountId = cursor.fetchone()
            cursor.close()
            if accountId is None:
                return -1
            else:
                return accountId[0]
    def getAccountInfo(self, email):
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            cursor.execute('''SELECT id, nume FROM ACCOUNTS WHERE email = ?''', (email,))
            account = cursor.fetchone()
            cursor.close()
            if account is None:
                return -1, ''
            else:
                return account[0], account[1]
    def addAccount(self, nume, email, password):
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            if self.getAccount(email, password) == -1:
                cursor.execute('''INSERT INTO ACCOUNTS (nume, email, password) VALUES (?, ?, ?)''', (nume, email, password))
                cursor.close()
                db.commit()
                return self.getAccount(email=email, password=password)
            else:
                cursor.close()
                return -1

    def getReceivers(self, userId):
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            cursor.execute(''' SELECT id, nume FROM ACCOUNTS WHERE id IN (SELECT DISTINCT receiverId FROM MESSAGES WHERE senderId = ? UNION SELECT DISTINCT senderId FROM MESSAGES WHERE receiverId = ?)''', (userId, userId))
            receivers = cursor.fetchall()
            cursor.close()
            return receivers

    def sendMessage(self, senderId, receiverId, message):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            cursor.execute('''INSERT INTO MESSAGES (senderId, receiverId, message, timestamp) VALUES (?, ?, ?, ?)''', (senderId, receiverId, message, now))
            cursor.close()
            db.commit()

    def getAllMessages(self, senderId, receiverId):
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            cursor.execute('''SELECT senderId, message, timestamp FROM MESSAGES WHERE (senderId = ? and receiverId = ?) OR (senderId = ? and receiverId = ?) ORDER BY timestamp ASC''', (senderId, receiverId, receiverId, senderId))
            messages = cursor.fetchall()
            cursor.close()
            return messages