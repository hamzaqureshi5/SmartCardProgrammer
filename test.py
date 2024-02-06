from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.System import readers, listReaders, readergroups

# from connection import CardConnection
# cardservice.connection.disconnect()


def str_2_hex_converter(apdu_command):
    apdu_list = [
        f"0x{apdu_command[i:i+2].upper()}" for i in range(0, len(apdu_command), 2)
    ]
    output = "[" + ", ".join(apdu_list) + "]"
    return output


def apdu_size_check(apdu_str: str):
    len_var = int(apdu_command[8:10], 16)
    data = apdu_command[10:]

    if len_var == (len(data) // 2):
        print("Size Valid")
        return True
    else:
        print("Size Invalid")
        return False


apdu_command = [0xA0, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x00]
apdu_command = [0xA0, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x00]


def str_2_apdu(apdu_str: str):
    apdu_bytes = bytes.fromhex(apdu_str)
    apdu_list = list(apdu_bytes)
    return apdu_list


# print(cardservice.connection)
# response, sw1, sw2 = cardservice.connection.transmit(str_2_apdu(command))
# print("Response:", response)
# print("Status words:", hex(sw1), hex(sw2))

from connection import PcscSimLink


class SendCommands(PcscSimLink):
    def __init__(self, reader_handler: PcscSimLink, **kwargs):
        super().__init__(**kwargs)
        self.m_reader = reader_handler

    def test_run(self):
        apdu_command = "A0A40000023F00"
        print(self.get_atr())

    #        response, sw1, sw2 = self.send_apdu(apdu_command)
    #        print(response,sw1,sw2)

    def run_script(self, m_reader):
        try:
            with open(self.path, "r") as f:
                apdu_commands = f.readlines()

            # Create a log file for commands and responses
            with open("QC_logs.txt", "a+") as log_file:
                _ok = True
                for command in apdu_commands:
                    if _ok is True:
                        command = command.replace("\n", "")
                        command = command.replace(" ", "")  # to remove spaces
                        if command.startswith("#") or command.startswith("//"):
                            pass
                        else:
                            if self.is_valid_apdu(command):
                                (
                                    command,
                                    resp_2_verify,
                                    error_flag,
                                ) = self.break_cmd_res_sw(command)
                                apdu_list = str_2_apdu(command)
                                response, sw1, sw2 = m_reader.transmit(apdu_list)
                                response_hex = " ".join(
                                    ["{:02X}".format(byte) for byte in response]
                                )
                                sw1_hex = format(sw1, "02X")
                                sw2_hex = format(sw2, "02X")
                                log_file.write(f"CMD: {command.strip()}\n")
                                log_file.write(f"RES: {response_hex} ")
                                #                                log_file.write(f"SW {sw1_hex} {sw2_hex}\n")
                                log_file.write(
                                    "Response: {} Expected: {}".format(
                                        sw1_hex + sw2_hex, resp_2_verify
                                    )
                                )
                                log_file.write("\n")
                                _ok = self.error_check(
                                    sw1_hex,
                                    sw2_hex,
                                    resp_2_verify,
                                    error_flag,
                                    log_file,
                                )
                                log_file.write("\n")
                                # self.textEdit.append(command+"\nRES: "+sw1_hex+sw2_hex)
                                self.textEdit.append(command)

                                self.textEdit.append(
                                    "Response: {} Expected: {}".format(
                                        sw1_hex + sw2_hex, resp_2_verify
                                    )
                                )

                            elif command.lower() == "reset" or command.lower() == "rst":
                                self.reset_card()
                                response = self.get_ATR()
                                log_file.write(f"CMD: {command.strip()}\n")
                                log_file.write(f"ATR: {response}\n")
                                log_file.write("\n")
                                print("CARD RESET Successfull")

                            else:
                                pass
        #                                log_file.write(f"CMD: {command.strip()} Invalid\n")

        except KeyboardInterrupt:
            pass


#     def error_check(self,sw1,sw2,resp_2_verify,error_flag,log)->bool:
#         if error_flag is True:
#             resp=sw1+sw2
#             if resp == resp_2_verify:
#                 return True
#             else:
#                 print("ERROR ! Response: {} Expected: {}".format(resp,resp_2_verify))
#                 log.write("ERROR ! Response: {} Expected: {}".format(resp,resp_2_verify))
#                 return False

#         else:
#             return True


#     #apdu_command="A02000020830303031FFFFFFFF"
#     def is_valid_apdu(self,apdu_command):
#         if len(apdu_command) % 2 != 0 or not all(c in "0123456789ABCDEFSW" for c in apdu_command)  and (len(apdu_command)!=0):#and apdu_size_check(apdu_command)#:
#             return False
#         if len(apdu_command) < 10:
#             return False
#         return True

#     def header(self,log_file):
#         log_file.write("#======================================================#\n")
#         log_file.write("#=========================START========================#\n")
#         log_file.write("#======================================================#\n")

#     def reset_card(self):
#         self.cardservice.connection.disconnect()
#         self.cardservice.connection.connect()

#     def break_cmd_res(self,apdu:str):
#         print("CMD RESP BREAK")
#         if apdu.find("SW")!=-1:
#             error_flag=True
#             break_point=apdu.find("SW")
#             cmd=apdu[:break_point]
#             res=apdu[break_point+2:]
#             print(cmd," ",res)
#             return cmd,res,error_flag
#         else:
#             error_flag=False
#             break_point=len(apdu)
#             cmd=apdu[:break_point+1]
#             res=""
#             print(cmd," ",res)
#             return cmd,res,error_flag


# scc=PcscSimLink(2)
# scc.connect()
# print(scc.get_atr())
# apdu_command = "A0A40000023F00"
# (res, sw) = scc.send_apdu(apdu_command)
# print(res,sw)

apdu_command = [0xA0, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x00]

# reader_handler = PcscSimLink(2)

# Create an object of SendCommands and pass the reader_handler as a parameter
# send_commands_obj = SendCommands(reader_handler=reader_handler)
scc = PcscSimLink(2)
scc.connect()
sl = SendCommands(scc)
sl.test_run()

# (res, sw) = scc.send_apdu(apdu_command)
# print(res,sw)
