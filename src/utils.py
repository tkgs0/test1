import arrow
import random
import secrets


def arrow_now():
    return arrow.now(tz='Asia/Shanghai')


def arrow_get(time: str):
    return arrow.get(time, tzinfo='Asia/Shanghai')


def get_arrow_gap_timestamp(time_1: str, time_2: str):
    return arrow_get(time_1).int_timestamp - arrow_get(time_2).int_timestamp


def get_arrow_gap_minutes(time_1: str, time_2: str):
    return get_arrow_gap_timestamp(time_1, time_2) / 60


def join(arr: list, sep: str = ''):
    # filter all empty value
    arr = list(filter(lambda x: x, arr))
    return sep.join(arr)


def get_now_time():
    return arrow_now().format('YYYY-MM-DD HH:mm:ss')


def date_improve(time: str):
    ins = arrow_get(time)
    is_today = (ins.format('YYYY-MM-DD') == arrow_now().format('YYYY-MM-DD'))
    if is_today:
        return ins.format('HH:mm')
    is_this_year = (ins.format('YYYY') == arrow_now().format('YYYY'))
    if is_this_year:
        return ins.format('MM-DD HH:mm')
    return ins.format('YYYY-MM-DD HH:mm')


def fixed_two_decimal_digits(num: int, to_number: bool = False):
    result = '{:.2f}'.format(num)
    if to_number:
        return float(result)
    return result


def is_date_outed(time: str):
    return arrow_get(time).format('YYYY-MM-DD') != arrow_now().format('YYYY-MM-DD')


def create_match_func_factory(fuzzy: bool = False):
    def is_keyword_matched(keywords: list, text: str):
        for keyword in keywords:
            if fuzzy:
                if text.startswith(keyword):
                    return True
            else:
                if text == keyword:
                    return True
        return False
    return is_keyword_matched


def get_object_values(obj: dict):
    vs = obj.values()
    ret = []
    for v in vs:
        if isinstance(v, list):
            ret.extend(v)
        else:
            ret.append(v)
    return ret


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass


class Random():

    nums = []
    max_nums = 500

    @staticmethod
    def get_secure_random_number():
        cryptogen = random.SystemRandom()
        return cryptogen.random()

    @staticmethod
    def generate_secure_random_number():
        return secrets.randbits(256) / ((1 << 256) - 1)

    @classmethod
    def get_single_random(cls):
        # num_1 = cls.generate_secure_random_number()
        num_2 = cls.generate_secure_random_number()
        return num_2

    @classmethod
    def fill(cls):
        while len(cls.nums) < cls.max_nums:
            cls.nums.append(cls.get_single_random())

    @classmethod
    def random(cls):
        if len(cls.nums) == 0:
            cls.fill()
        return cls.nums.pop()
