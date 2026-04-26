import json

import sysv_ipc
from PyQt5.QtCore import QThread, pyqtSignal


class CommunicationsManager(QThread):
    messageReceived = pyqtSignal(dict)

    def __init__(self, userId, key=1234):
        super().__init__()
        self.userId = userId
        self.key = key
        self.running = True

        try:
            self.message_queue = sysv_ipc.MessageQueue(self.key, sysv_ipc.IPC_CREAT)
        except sysv_ipc.Error as e:
            print(f"Eroare initializare coada: {e}")
    def run(self):
        while self.running:
            try:
                messageBytes, messageType  = self.message_queue.receive(type=self.userId)
                message = messageBytes.decode('utf-8').rstrip('\x00')
                payload = json.loads(message)
                if payload.get("action") == "STOP":
                    break
                self.messageReceived.emit(payload)
            except Exception as e:
                if self.running:
                    print(f"Eroare in run: {e}")
    def sendMessage(self, targetId, payload):
        try:
            messageBytes = json.dumps(payload).encode('utf-8')
            self.message_queue.send(messageBytes, type = targetId)
        except Exception as e:
            print(f"Eroare la trimitere: {e}")

    def stop(self):
        self.running = False
        dummyPayload = {"action": "STOP"}
        self.sendMessage(targetId=self.userId, payload=dummyPayload)
        self.quit()
        self.wait()