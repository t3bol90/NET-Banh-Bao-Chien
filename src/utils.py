import glob
import json
from enum import Enum
import re

patterns = {
    '[àáảãạăắằẵặẳâầấậẫẩ]': 'a',
    '[đ]': 'd',
    '[èéẻẽẹêềếểễệ]': 'e',
    '[ìíỉĩị]': 'i',
    '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
    '[ùúủũụưừứửữự]': 'u',
    '[ỳýỷỹỵ]': 'y'
}

areas = ["MienNam", "MienBac", "MienTrung"]


def convert(text):
    """
    Convert from 'Tieng Viet co dau' thanh 'Tieng Viet khong dau'
    text: input string to be converted
    Return: string converted
    """
    output = text
    for regex, replace in patterns.items():
        output = re.sub(regex, replace, output)
        # deal with upper case
        output = re.sub(regex.upper(), replace.upper(), output)
    return output.replace(' ', '')


class bucket_list:
    def __init__(self):
        self.miennam = {}
        self.mienbac = {}
        self.mientrung = {}

    @staticmethod
    def province_contain_check(province: str) -> bool:
        tmp, l_province = query_handler(STATE.HELP, province)
        for area in areas:
            if province in l_province[area]:
                return True
        return False


bucket = bucket_list()


class STATE(Enum):
    ERROR = 0
    HELP = 1
    INDEPENDENCE = 2
    AUTORESULT = 3


def read_data():
    global bucket
    mien = [{}, {}, {}]
    for (file, i) in zip(glob.glob("./Data/*.json"), range(3)):
        with open(file) as f:
            data = json.load(f)
            mien[i] = dict(data[0]["xs_data"])

    bucket.miennam = mien[0]
    bucket.mienbac = mien[1]
    bucket.mientrung = mien[2]


def query_handler(state, province="", pot='') -> (STATE, dict):
    global bucket
    if state == STATE.ERROR:
        return state, {'ERROR': 'Wrong Syntax! Try h or --help for more information'}
    if state == STATE.HELP:
        extract_packet = {}
        for area in areas:
            extract_packet[area] = []
        for prov in bucket.mientrung.items():
            extract_packet["MienTrung"].append(convert(prov[0]))
        for prov in bucket.mienbac.items():
            extract_packet["MienBac"].append(convert(prov[0]))
        for prov in bucket.miennam.items():
            extract_packet["MienNam"].append(convert(prov[0]))
        return state, extract_packet
    if not bucket.province_contain_check(province):
        return STATE.ERROR,{
            'ERROR': 'Unknown province or this province does not have jackpot on today!\nTry h or --h for more '
                     'information'}
    if state == STATE.INDEPENDENCE:
        extract_packet = {}
        position = None
        for area in [bucket.miennam.items(), bucket.mientrung.items(), bucket.mienbac.items()]:
            for prov in area:
                if province == convert(prov[0]):
                    extract_packet = prov
                    break
        return state, extract_packet
    if state == STATE.AUTORESULT:
        res = {}
        extract_packet = {}
        for area in [bucket.miennam.items(), bucket.mientrung.items(), bucket.mienbac.items()]:
            for prov in area:
                if province == convert(prov[0]):
                    extract_packet = prov
                    break
        extract_packet = extract_packet[1]

        for type, raw_pots in extract_packet.items():
            if pot in raw_pots.split(", "):
                res["BINGO"] = type
                return state, res
        res["NO JACKPOT"] = "TRUNG GIO"
        return state, res

