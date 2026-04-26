import sys
import os
from datetime import datetime

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QStringListModel, Qt, QEvent
from DatabaseManager import DatabaseManager
from CommunicationsManager import CommunicationsManager

class Login(QtWidgets.QMainWindow):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(ROOT_DIR, 'login.ui')

    def __init__(self, db):
        super().__init__()
        uic.loadUi(self.ui_path, self)
        self.setWindowTitle('Login')
        self.db = db
        self.createFinal.hide()
        self.loginFinal.hide()
        self.name.hide()
        self.email.hide()
        self.password.hide()
        self.createBtn.clicked.connect(self.createAccount)
        self.loginBtn.clicked.connect(self.login)
        self.createFinal.clicked.connect(self.addAccount)
        self.loginFinal.clicked.connect(self.loginAccount)

    def createAccount(self):
        self.title.setText('Create Account')
        self.createBtn.hide()
        self.loginBtn.show()
        self.createFinal.show()
        self.name.show()
        self.email.show()
        self.password.show()
        self.loginFinal.hide()
        self.name.show()

    def login(self):
        self.title.setText('Login')
        self.loginBtn.hide()
        self.createBtn.show()
        self.loginFinal.show()
        self.createFinal.hide()
        self.name.hide()
        self.email.show()
        self.password.show()

    def addAccount(self):
        if self.name.toPlainText() == '' or self.email.toPlainText() == '' or self.password.toPlainText() == '':
            QtWidgets.QMessageBox.information(self, 'Error', 'Please enter all fields')
        else:
            id = self.db.addAccount(self.name.toPlainText(), self.email.toPlainText(), self.password.toPlainText())
            if id>0:
                self.showMain(id)
            else:
                QtWidgets.QMessageBox.critical(self, 'Error', 'User exists')

    def loginAccount(self):
        if self.email.toPlainText() == '' or self.password.toPlainText() == '':
            QtWidgets.QMessageBox.information(self, 'Error', 'Please enter all fields')
        else:
            id = self.db.getAccount(self.email.toPlainText(), self.password.toPlainText())
            if id>0:
                self.showMain(id)
            else:
                    QtWidgets.QMessageBox.critical(self, 'Error', 'Login Data is wrong')

    def showMain(self, id):
        self.main_window = MainWindow(id, self.db)
        self.main_window.show()
        self.close()

class MainWindow(QtWidgets.QMainWindow):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(ROOT_DIR, 'main.ui')

    def __init__(self, userId, db):
        super().__init__()
        uic.loadUi(self.ui_path, self)
        self.setWindowTitle('Chat Application')
        self.userId = userId
        self.db = db
        self.comm = CommunicationsManager(self.userId)
        self.comm.messageReceived.connect(self.receiveMessage)
        self.comm.start()
        self.model = QStringListModel()
        self.receiverList.setModel(self.model)
        self.receivers = self.db.getReceivers(self.userId)
        if self.receivers:
            namesOnly = [item[1] for item in self.receivers]
            self.model.setStringList(namesOnly)
        self.receiverId = None
        self.lastDateDisplayed = None
        self.add.clicked.connect(self.addReceiver)
        self.receiverList.clicked.connect(self.openReceiver)
        self.messageInput.hide()
        self.sendBtn.hide()
        self.sendBtn.clicked.connect(self.sendMessage)
        self.chatLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.chatLayout.setAlignment(Qt.AlignTop)
        self.messagedDisplay.verticalScrollBar().rangeChanged.connect(self.scrollToBottom)
        self.messageInput.installEventFilter(self)

    def addReceiver(self):
        text, ok = QtWidgets.QInputDialog.getText(self, 'Add Receiver', 'Enter Receiver Email')
        if text and ok:
            receiverId, name = self.db.getAccountInfo(text)
            if receiverId>0:
                if not any(receiverId == r[0] for r in self.receivers):
                    self.receivers.append((receiverId, name))
                    namesOnly = [item[1] for item in self.receivers]
                    self.model.setStringList(namesOnly)
            else:
                QtWidgets.QMessageBox.critical(self, 'Error', 'Receiver does not exist')

    def openReceiver(self, index):
        receiver = self.model.data(index, Qt.DisplayRole)
        self.receiverId = self.receivers[index.row()][0]
        self.nameLabel.setText(receiver)
        self.nameLabel.setStyleSheet('background-color: rgb(0, 0, 127);color: #fff;padding:10px;font-size:20px;')
        self.messageInput.show()
        self.sendBtn.show()
        self.clearScreen()
        self.lastDateDisplayed = None
        histroy = self.db.getAllMessages(self.userId, self.receiverId)
        if histroy:
            for msgSender, mesText, timestamp in histroy:
                self.checkDate(timestamp)
                if msgSender == self.userId:
                    self.displayMessage(mesText, timestamp, True)
                else:
                    self.displayMessage(mesText, timestamp,False)

    def sendMessage(self):
        message = self.messageInput.toPlainText()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if message and self.receiverId:
            self.db.sendMessage(self.userId, self.receiverId, message)
            payload = {"senderId": self.userId, "receiverId": self.receiverId, "message": message, "timestamp": now}
            self.comm.sendMessage(targetId=self.receiverId, payload=payload)
            self.messageInput.clear()
            self.checkDate(now)
            self.displayMessage(message, now, True)

    def receiveMessage(self, payload):
        senderId = payload.get('senderId')
        receiverId = payload.get('receiverId')
        message = payload.get('message')
        timestamp = payload.get('timestamp')
        if self.receiverId and self.receiverId == senderId:
            self.checkDate(timestamp)
            self.displayMessage(message, timestamp, False)

    def clearScreen(self):
        while self.chatLayout.count():
            item = self.chatLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.clearLayout(item.layout())

    def clearLayout(self, layout):
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def displayMessage(self, message, timestamp, isMe = True):
        date = timestamp.split(" ")[0]
        time = timestamp.split(" ")[1]
        fullText = f"{message.replace('\n', '<br>')}<br><small style='color: {'#e0e0e0' if isMe else '#888888'};'>{time}</small>"
        hLayout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(self)
        label.setTextFormat(Qt.RichText)
        label.setWordWrap(True)
        label.setMaximumWidth(int(self.messagedDisplay.width() * 0.7))
        if isMe:
            style = """
                            background-color: #0078fe; 
                            color: white; 
                            border-top-left-radius: 10px; 
                            border-bottom-left-radius: 10px; 
                            border-top-right-radius: 10px;
                            padding: 8px; 
                            margin: 2px;
                        """
            hLayout.addStretch()
            hLayout.addWidget(label)
        else:
            style = """
                            background-color: #e9e9eb; 
                            color: black; 
                            border-top-left-radius: 10px; 
                            border-bottom-right-radius: 10px; 
                            border-top-right-radius: 10px;
                            padding: 8px; 
                            margin: 2px;
                        """
            hLayout.addWidget(label)
            hLayout.addStretch()
        label.setStyleSheet(style)
        label.setText(fullText)
        self.chatLayout.addLayout(hLayout)

    def scrollToBottom(self):
        self.messagedDisplay.verticalScrollBar().setValue(self.messagedDisplay.verticalScrollBar().maximum())

    def displayDateSeparator(self, date):
        dt = datetime.strptime(date, '%Y-%m-%d')
        displayDate = dt.strftime('%d %B %Y')
        label = QtWidgets.QLabel(displayDate)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
                    color: #888888; 
                    font-size: 11px; 
                    font-weight: bold;
                    margin-top: 15px; 
                    margin-bottom: 5px;
                """)
        self.chatLayout.addWidget(label)

    def checkDate(self, timestamp):
        currentDate = timestamp.split(" ")[0]
        if currentDate != self.lastDateDisplayed:
            self.displayDateSeparator(currentDate)
            self.lastDateDisplayed = currentDate

    def eventFilter(self, obj, event):
        if obj is self.messageInput and event.type() == QtCore.QEvent.KeyPress:
            if event.key() in (Qt.Key_Return , Qt.Key_Enter):
                if not event.modifiers() & Qt.ShiftModifier:
                    self.sendMessage()
                    return True
        return super().eventFilter(obj, event)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    db = DatabaseManager()
    login = Login(db)
    login.show()
    sys.exit(app.exec_())
