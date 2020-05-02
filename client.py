import json
import socket
from enum import Enum

areas = ["MienNam", "MienBac", "MienTrung"]


class STATE(Enum):
    ERROR = 0
    HELP = 1
    INDEPENDENCE = 2
    AUTORESULT = 3


s = socket.socket()
port = 5000
host = "127.0.0.1"
s.connect((host, port))

exit_status = ["quit", "exit", "q", "x"]


def parse_packet(data):
    data = data.decode("utf8")
    status = STATE(int(data[0]))
    response = json.loads(data[1:])
    if status == STATE.ERROR:
        print("ERROR: ", response['ERROR'])
    elif status == STATE.HELP:
        print("Usage of Banh-Bao-Chien server ~")
        print("1. Send h or --help to get this message and list of province have result on today~")
        print("2. Send <Province> in order to get result of that province,\n"
              "   eg: '>GiaLai' to get lotery result from GiaLai")
        print("3. Send <Province> <Lottery number> in order to get autoresult\n"
              "   ~ if your Lotery number win the lottery, BBC will tell u which prize u have won\n"
              "   ~ in another case, BBC will send u a consolatory message\n"
              "   eg: '>GiaLai 19832' to check if 19832 can win the lottery or not.")
        print("List of provinces have lottery result on today")
        for area in areas:
            print("~~", area, "~~")
            for element in response[area]:
                print(element)
    elif status == STATE.INDEPENDENCE:
        print("Ket qua xo so cua tinh: ", response[0])
        for prize_type, number in response[1].items():
            print(prize_type, end=": ")
            print(*(number.split(", ")), sep=", ")
    elif status == STATE.AUTORESULT:
        for sentile, prize in response.items():

            if sentile == "NO JACKPOT":
                print("Ban da khong trung giai nao ca")
            else:
                print("Ban da trung giai: ", prize)


# Get hello from server ~
data = s.recv(1024)
print(data.decode("utf8"))

while True:
    user_in_query = input("> ")
    while user_in_query == '\n':
        user_in_query = input("> ")
    if user_in_query in exit_status:
        user_in_query = "quit"
        s.sendall(user_in_query.encode())
        s.close()
        print("Chao tam biet ~ chuc mot ngay tot lanh!")
        break
    elif user_in_query == '--help':
        user_in_query = 'h'
    s.sendall(user_in_query.encode())
    data = s.recv(1024)
    parse_packet(data)
s.close()
