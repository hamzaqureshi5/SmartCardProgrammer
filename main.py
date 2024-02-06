# Only needed for access to command line arguments
import time
import os
import sys
from connection import PcscSimLink
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTextEdit
from forms.main_ui import Ui_MainWindow

debug = False
from connection import PcscSimLink


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("SCRIPT LOADER")
        self.showFullScreen()
        self.setWindowIcon(QIcon("resources\\stc_logo.ico"))
        self.ui.reader_refresh.setIcon(QIcon("resources\\refresh.ico"))
        self.ui.reader_connection.setIcon(QIcon("resources\\connect.ico"))
        self.ui.textEdit.setLineWrapMode(
            QTextEdit.LineWrapMode.NoWrap
        )  # Commenting this line removes the delay

        self.showMaximized()
        #        self.con=CardConnection()
        self.scc = PcscSimLink(self.ui.textEdit)
        self.devices = self.scc.refresh_hid_list()

        #        scc.connect_to_reader()
        self.ui.reader_connection.clicked.connect(self.connect_to_reader)
        self.ui.reader_refresh.clicked.connect(self.refresh_hid_list)
        #        self.ui.reader_refresh.clicked.connect(self.scc.editbox_test)

        self._pre_os_sys_path = ""
        self._operat_sys_path = ""
        self._pre_perso_path = ""
        self._perso_path = ""

        self.ui.pre_os_browse_button.clicked.connect(self.browse_PRE_OS_File)
        self.ui.op_sys_browse_button.clicked.connect(self.browse_OS_File)
        self.ui.pre_perso_browse_button.clicked.connect(self.browse_PRE_PERSO_File)
        self.ui.perso_browse_button.clicked.connect(self.browse_PERSO_File)

        #        self.ui.reader_refresh.clicked.connect(self.refresh_hid_list)

        self.ui.load_button.clicked.connect(self.loadFile)
        self.refresh_hid_list()

    #        print(self.scc.break_cmd_res_sw("A0B000000A [985955555555111111F0]SW9000"))
    # test case
    #        self.scc.custom_connect(2)
    #        path="scripts/commands.txt"
    #        self.scc.run_script(path)

    def connect_to_reader(self):
        selected_index = self.ui.reader_comboBox.currentIndex()
        if selected_index >= 0:
            rtn = self.scc.custom_connect(reader_number=selected_index)
            if rtn is True:
                self.connect_reader_index = selected_index
                self.ui.textEdit.append(
                    f"Connected to HID reader: {self.reader_list[selected_index]}"
                )
                print(f"Connected to HID reader: {self.reader_list[selected_index]}")
            else:
                print("Error connecting to HID reader:{}".format(rtn))
                self.ui.textEdit.append(
                    "Error connecting to HID reader: {}".format(rtn)
                )

    def disconnect_to_reader(self):
        bool_rtn, e, reader_2_disconnect = self.scc.disconnect()
        if bool_rtn is True:
            self.ui.textEdit.append(
                f"Disconnected to HID reader: {self.reader_list[reader_2_disconnect]}"
            )
            print(f"Connected to HID reader: {self.reader_list[reader_2_disconnect]}")
        else:
            print("Error disconnecting to HID reader:{}".format(e))
            self.ui.textEdit.append("Error disconnecting to HID reader: {}".format(e))

    def refresh_hid_list(self):
        #        self.scc.calculate_something(50,self.ui.textEdit)
        #        self.scc.run_script("")
        self.ui.reader_comboBox.clear()
        self.reader_list = self.scc.refresh_hid_list()
        for device in self.reader_list:
            self.ui.reader_comboBox.addItem(str(device))

    def is_path_selected(self, path):
        return os.path.exists(path)  # and (len(path)>0)

    def browseFile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*txt)"
        )
        if file_path:
            return file_path

    def loadFile(self):
        self.ui.textEdit.clear()
        if (
            self.is_path_selected(self._pre_os_sys_path)
            and self.ui.pre_os_check_box.isChecked()
        ):
            path = self._pre_os_sys_path
            self.scc.run_script(path=path)
            self.ui.textEdit.append(
                "#=========================Pre OS Loaded ============================#"
            )

        if (
            self.is_path_selected(self._operat_sys_path)
            and self.ui.os_sys_check_box.isChecked()
        ):
            path = self._operat_sys_path
            self.scc.run_script(path=path)
            self.ui.textEdit.append(
                "#======================== OS Loaded =================================#"
            )

        if (
            self.is_path_selected(self._pre_perso_path)
            and self.ui.pre_perso_check_box.isChecked()
        ):
            path = self._pre_perso_path
            self.scc.run_script(path=path)
            self.ui.textEdit.append(
                "#=========================Pre Perso Loaded ===========================#"
            )

        if (
            self.is_path_selected(self._perso_path)
            and self.ui.perso_check_box.isChecked()
        ):
            path = self._perso_path
            self.scc.run_script(path=path)
            self.ui.textEdit.append(
                "#=========================Post Peros Loaded ============================#"
            )

    def browse_PRE_OS_File(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "SELECT PRE OS FILE", "", "All Files (*txt)"
        )
        if file_path:
            self.ui.pre_os_path.setText(file_path)
            self._pre_os_sys_path = file_path
            temp = f'<a href="{file_path}">{file_path}</a>'
            self.ui.textEdit.append("{} is selected as Pre OS\n".format(temp))

    def browse_OS_File(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "SELECT OS File", "", "All Files (*txt)"
        )
        if file_path:
            self.ui.op_sys_path.setText(file_path)
            self._operat_sys_path = file_path
            temp = f'<a href="{file_path}">{file_path}</a>'
            self.ui.textEdit.append("{} is selected as OS\n".format(temp))

    def browse_PRE_PERSO_File(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "SELECT PRE PERSO FILE", "", "All Files (*txt)"
        )
        if file_path:
            self.ui.pre_perso_path.setText(file_path)
            self._pre_perso_path = file_path
            temp = f'<a href="{file_path}">{file_path}</a>'
            self.ui.textEdit.append("{} is selected as Pre Perso File\n".format(temp))

    def browse_PERSO_File(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "SELECT PRESO FILE", "", "All Files (*txt)"
        )
        if file_path:
            self.ui.perso_path.setText(file_path)
            self._perso_path = file_path
            temp = f'<a href="{file_path}">{file_path}</a>'
            self.ui.textEdit.append("{} is selected as PERSO File\n".format(temp))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
