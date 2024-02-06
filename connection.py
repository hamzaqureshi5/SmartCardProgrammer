from pySim.commands import SimCardCommands
from pySim.transport import init_reader, argparse_add_reader_args
from pySim.exceptions import SwMatchError

# from smartcard.util import toHexString,toBytes,toASCIIString,toASCIIBytes,HexListToBinString,BinStringToHexList
import string
from smartcard.CardConnection import CardConnection
from smartcard.CardRequest import CardRequest
from smartcard.Exceptions import (
    NoCardException,
    CardRequestTimeoutException,
    CardConnectionException,
    CardConnectionException,
)

from smartcard.System import readers
from pySim.exceptions import NoCardError, ProtocolError, ReaderError
from pySim.transport import LinkBase
from pySim.utils import h2i, i2h
from functools import wraps
from message import message
import time

LOGS_PATH = "logs.txt"


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        # first item in the args, ie `args[0]` is `self`
        rtn_str = (
            f"Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds"
        )
        print(rtn_str)
        return result, rtn_str

    return timeit_wrapper


def str_2_hex_converter(apdu_command):
    apdu_list = [
        f"0x{apdu_command[i:i+2].upper()}" for i in range(0, len(apdu_command), 2)
    ]
    output = "[" + ", ".join(apdu_list) + "]"
    return output


def str_2_apdu(apdu_str: str):
    apdu_bytes = bytes.fromhex(apdu_str)
    apdu_list = list(apdu_bytes)
    return apdu_list


class PcscSimLink(LinkBase):
    """pySim: PCSC reader transport link."""

    def __init__(self, textEdit=None, **kwargs):
        super().__init__(**kwargs)
        self.textEdit = textEdit
        self.r = readers()
        self.refresh_hid_list()

    def __del__(self):
        try:
            # FIXME: this causes multiple warnings in Python 3.5.3
            self._con.disconnect()
        except:
            pass
        return

    # def editbox_test(self):
    #     self.textEdit.append("AAAAAAA")

    def refresh_hid_list(self):
        try:
            self.r = readers()
            if len(self.r) == 0:
                raise ReaderError("No reader found")
        except CardConnectionException:
            raise ProtocolError()
        except NoCardException:
            raise NoCardError()
        return self.r

    def custom_connect(self, reader_number: int = 0):
        try:
            #            self.disconnect()
            #            r = readers()
            if reader_number >= len(self.r):
                raise ReaderError("No reader found for number %d" % reader_number)
            self._reader = self.r[reader_number]
            self._con = self._reader.createConnection()
            self._con.connect(CardConnection.T0_protocol)
            return True
        except CardConnectionException as e:
            return e
            raise ProtocolError()
        except NoCardException as e:
            return e
            raise NoCardError()

    def wait_for_card(self, timeout: int = None, newcardonly: bool = False):
        cr = CardRequest(
            readers=[self._reader], timeout=timeout, newcardonly=newcardonly
        )
        try:
            cr.waitforcard()
        except CardRequestTimeoutException:
            raise NoCardError()
        self.connect()

    def connect(self):
        try:
            # To avoid leakage of resources, make sure the reader
            # is disconnected
            self.disconnect()

            # Explicitly select T=0 communication protocol
            self._con.connect(CardConnection.T0_protocol)
        except CardConnectionException:
            raise ProtocolError()
        except NoCardException:
            raise NoCardError()

    def get_atr(self):
        return self._con.getATR()

    def disconnect(self):
        self._con.disconnect()

    def reset_card(self):
        self.disconnect()
        self.connect()
        return 1

    def _send_apdu_raw(self, pdu):
        apdu = h2i(pdu)

        data, sw1, sw2 = self._con.transmit(apdu)

        sw = [sw1, sw2]

        # Return value
        return i2h(data), i2h(sw)

    # @staticmethod
    # def calculate_something(num, text_edit):
    #     start_time = time.perf_counter()
    #     total = sum((x for x in range(0, num**2)))
    #     end_time = time.perf_counter()
    #     execution_time = end_time - start_time
    #     text_edit.append(f'Function calculate_something({num}) Took {execution_time:.4f} seconds')
    #     return total

    #    @staticmethod
    def run_script(self, path):
        debug = True

        try:
            start_time = time.perf_counter()
            with open(path, "r") as f:
                apdu_commands = f.readlines()

            with open(LOGS_PATH, "a+") as log_file:
                _ok = True
                for command in apdu_commands:
                    if _ok is True:
                        command = command.replace("\n", "")
                        command = command.replace(" ", "")  # to remove spaces
                        if command == "":
                            pass
                        else:
                            if (
                                command.startswith("#")
                                or command.startswith("//")
                                or command.startswith("/")
                            ):
                                pass
                            else:
                                if self.is_valid_apdu(command):
                                    (
                                        command,
                                        resp_2_verify,
                                        error_flag,
                                    ) = self.break_cmd_res_sw(command)

                                    (response, sw) = self.send_apdu(command)
                                    response = response.upper()
                                    sw = sw.upper()

                                    cmd = f"CMD: {command.strip()}"
                                    res = f"RES: [{response}]"
                                    #                                    sw_disp=f"SW: {sw}"
                                    res_verify = "SW: {} Expected: {}".format(
                                        sw, resp_2_verify
                                    )
                                    log_file.write(cmd + "\n")
                                    log_file.write(res + "\n")
                                    log_file.write(res_verify + "\n")
                                    log_file.write("\n")

                                    if debug:
                                        print(cmd)
                                        print(res)
                                        print(res_verify)

                                    self.textEdit.append(cmd)
                                    self.textEdit.append(res)
                                    self.textEdit.append(res_verify)
                                    self.textEdit.append("")

                                    _ok = self.error_check(
                                        sw, resp_2_verify, error_flag, log_file
                                    )
                                    log_file.write("\n")

                                elif (
                                    command.lower() == "reset"
                                    or command.lower() == "rst"
                                ):
                                    if self.reset_card():
                                        response = self.get_atr()
                                        cmd = f"CMD: {command.strip()}"
                                        res = (
                                            f"ATR: {self.dec_list_2_hex_str(response)}"
                                        )

                                        log_file.write(cmd + "\n")
                                        log_file.write(res + "\n")
                                        log_file.write("\n")

                                        if debug:
                                            print(cmd)
                                            print("CARD RESET")
                                            print(res)

                                        self.textEdit.append(cmd)
                                        self.textEdit.append(res)
                                        self.textEdit.append("")  # for spare line

                                else:
                                    cmd = f"CMD: {command.strip()} [INVALID]"

                                    log_file.write(cmd + "\n")
                                    log_file.write("\n")

                                    if debug:
                                        print(cmd)
                                        print("")

                                    self.textEdit.append(cmd)
                                    self.textEdit.append("")  # for spare line

                end_time = time.perf_counter()
                execution_time = end_time - start_time
                self.textEdit.append(
                    f"Script({path}) Took {execution_time:.4f} seconds\n"
                )
        #                log_file.write(f'Script({path}) Took {execution_time:.4f} seconds\n')

        except Exception as e:
            self.textEdit.append(str(e))
            pass

    def error_check(self, sw: str, resp_2_verify: str, error_flag: bool, log) -> bool:
        if error_flag is True:
            if sw.upper() == resp_2_verify.upper():
                return True
            else:
                error = "ERROR ! Response: {} Expected: {}".format(sw, resp_2_verify)
                message.Show_message_box(
                    "Error", "Error", "Error loading Script {}!".format(error)
                )
                print(error)
                log.write(error)
                self.textEdit.append(error)
                return False

        else:
            return True

    # apdu_command="A02000020830303031FFFFFFFF"
    def is_valid_apdu(self, apdu_command):
        if len(apdu_command) % 2 != 0 or not all(
            c in "0123456789ABCDEFSW" for c in apdu_command
        ):  # and (len(apdu_command)!=0):#and apdu_size_check(apdu_command)#:
            return False
        if len(apdu_command) < 10:
            return False
        return True

    def header(self, log_file):
        log_file.write("#======================================================#\n")
        log_file.write("#=========================START========================#\n")
        log_file.write("#======================================================#\n")

    # def reset_card(self):
    #     self._con.disconnect()
    #     self._con.connect()

    def break_cmd_res_sw(self, apdu: str):
        if apdu.find("[") == -1 and apdu.find("]") == -1:
            print(apdu.find("["))
            print(apdu.find("]"))

            pass

        if apdu.find("SW") != -1:
            error_flag = True
            break_point = apdu.find("SW")
            cmd = apdu[:break_point]
            res = apdu[break_point + 2 :]
            return cmd, res, error_flag
        else:
            error_flag = False
            break_point = len(apdu)
            cmd = apdu[: break_point + 1]
            res = ""
            return cmd, res, error_flag

    def dec_list_2_hex_str(self, dec_list):
        string = " ".join(list(map(lambda x: format(x, "02X").upper(), dec_list)))
        return string


# scc=PcscSimLink()
# # #scc.connect()
# # print(scc.refresh_hid_list())
# scc.custom_connect(2)
# path="scripts/commands.txt"
# PcscSimLink.run_script(scc,path)
# PcscSimLink.run_script(scc,path)
# ATR= [59, 159, 150, 128, 31, 135, 128, 49, 224, 115, 254, 33, 25, 103, 85, 84, 48, 48, 53, 2, 88, 252]
# print(dec_list_2_hex_str(ATR))

#     @staticmethod
#     def run_script(self,path):
#         debug=True

#         try:
#             start_time = time.perf_counter()
#             with open(path, "r") as f:
#                 apdu_commands = f.readlines()

#             with open(log_path, "a+") as log_file:

#                 _ok=True
#                 for command in apdu_commands:
#                     if _ok is True:

#                         command=command.replace("\n","")
#                         command=command.replace(" ","") #to remove spaces
#                         if command.startswith("#") or command.startswith("//") or command.startswith("/"):
#                             pass
#                         else:
#                             if self.is_valid_apdu(command):
#                                 command,resp_2_verify,error_flag=self.break_cmd_res(command)

#                                 (response, sw) = self.send_apdu(command)
#                                 response=response.upper()
#                                 sw=sw.upper()

#                                 cmd=f"CMD: {command.strip()}"
#                                 res=f"RES: [{response}]"
# #                                sw_disp=f"SW: {sw}"
#                                 res_verify="SW: {} Expected: {}".format(sw,resp_2_verify)
#                                 log_file.write(cmd+"\n")
#                                 log_file.write(res+"\n")
#                                 log_file.write(res_verify+"\n")
#                                 log_file.write("\n")

#                                 if debug:
#                                     print(cmd)
#                                     print(res)
#                                     print(res_verify)


#                                 self.textEdit.append(cmd)
#                                 self.textEdit.append(res)
#                                 self.textEdit.append(res_verify)
#                                 self.textEdit.append("")

#                                 _ok=self.error_check(sw,resp_2_verify,error_flag,log_file)
#                                 log_file.write("\n")


#                             elif command.lower() == "reset" or command.lower() == "rst":
#                                 if self.reset_card():
#                                     response=self.get_atr()
#                                     cmd=f"CMD: {command.strip()}"
#                                     res=f"ATR: {self.dec_list_2_hex_str(response)}"

#                                     log_file.write(cmd+"\n")
#                                     log_file.write(res+"\n")
#                                     log_file.write("\n")

#                                     if debug:
#                                         print(cmd)
#                                         print("CARD RESET")
#                                         print(res)

#                                     self.textEdit.append(cmd)
#                                     self.textEdit.append(res)
#                                     self.textEdit.append("")  # for spare line

#                             elif command==" ":
#                                 cmd=f"CMD: {command.strip()}"

#                                 log_file.write(cmd+"\n")
#                                 log_file.write("\n")

#                                 if debug:
#                                     print(cmd)
#                                     print("Invalid")

#                                 self.textEdit.append(cmd)
#                                 self.textEdit.append("")  # for spare line


#                             else:
#                                 pass
#             end_time = time.perf_counter()
#             execution_time = end_time - start_time
#             self.textEdit.append(f'Script({path}) Took {execution_time:.4f} seconds\n')
# #            log_file.write(f'Script({path}) Took {execution_time:.4f} seconds\n')

#         except Exception as e:
#             self.textEdit.append(str(e))
#             pass
