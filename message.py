from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QIcon

stc_icon = "resources/stc_logo.ico"


class message:
    def __init__(self):
        super().__init__()
        pass

    def Show_message_box(self, title, message):
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowIcon(QIcon(stc_icon))
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        temp = message_box.exec()
        if temp == QMessageBox.StandardButton.Ok:
            del message_box

    def Logout_message_box(self, title, message):
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowIcon(QIcon(stc_icon))
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        temp = message_box.exec()
        #        del message_box
        if temp == QMessageBox.StandardButton.Yes:
            return True
        else:
            return False
