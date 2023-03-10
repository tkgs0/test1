from .db import DB, lazy_init_database
from .impl import get_at_segment, send_message
from .utils import create_match_func_factory, join, ArrowUtil, fixed_two_decimal_digits
from .config import Config
from .cd import CD_Check
from .rebirth import RebirthSystem
from .badge import BadgeSystem
from .constants import OpFrom, TimeConst, FarmConst
from .farm import FarmSystem
from .friends import FriendsSystem
from typing import Optional

KEYWORDS = {
    "chinchin": ["็ๅญ"],
    "pk": ["pk"],
    "lock_me": ["๐ๆ"],
    "lock": ["๐", "suo", "ๅฆ", "้"],
    "glue": ["ๆ่ถ"],
    "see_chinchin": ["็ไป็ๅญ", "็็็ๅญ"],
    "sign_up": ["ๆณจๅ็ๅญ"],
    "ranking": ["็ๅญๆๅ", "็ๅญๆ่ก"],
    "rebirth": ["็ๅญ่ฝฌ็"],
    "badge": ["็ๅญๆๅฐฑ"],
    # farm
    "farm": ["็ๅญไปๅข"],
    "farm_start": ["็ๅญไฟฎ็ผ", "็ๅญ็ปๅ", "็ๅญไฟฎไป"],
    # friends
    "friends": ["็ๅ", '็ๅญๅฅฝๅ', '็ๅญๆๅ'],
    "friends_add": ["ๅณๆณจ็ๅญ", "ๆทปๅ ็ๅ", "ๆทปๅ ๆๅ"],
    "friends_delete": ["ๅๅณ็ๅญ", "ๅ ้ค็ๅ", "ๅ ้คๆๅ"],
    # help
    "help": ["็ๅญๅธฎๅฉ"],
}

VERSION = '2.6.0'
HELPPER = f"็ไบไธช็ v{VERSION}\nๅฏ็จ็ๆไปค/ๅ่ฝๆ๏ผ\n" + "ใ".join(
    [
        KEYWORDS.get("sign_up")[0],
        KEYWORDS.get("chinchin")[0],
        f"@ๆไบบ {KEYWORDS.get('see_chinchin')[0]}",
        f"@ๆไบบ {KEYWORDS.get('pk')[0]}",
        KEYWORDS.get("lock_me")[0],
        f"@ๆไบบ {KEYWORDS.get('lock')[0]}",
        KEYWORDS.get("glue")[0],
        KEYWORDS.get("ranking")[0],
        KEYWORDS.get("rebirth")[0],
        KEYWORDS.get("badge")[0],
        KEYWORDS.get("farm")[0],
        KEYWORDS.get("farm_start")[0],
        KEYWORDS.get("friends")[0],
        f"@ๆไบบ {KEYWORDS.get('friends_add')[0]}",
        f"@ๆไบบ {KEYWORDS.get('friends_delete')[0]}",
    ]
)


def message_processor(
    message: str,
    qq: int,
    group: int,
    at_qq: Optional[int] = None,
    nickname: Optional[str] = None,
    fuzzy_match: bool = False,
    impl_at_segment=None,
    impl_send_message=None,
):
    """
    main entry
    TODO: ็ ด่งฃ็ๅญ๏ผ่ขซ็ ด่งฃ็ ็ๅญ ้ฟๅบฆๆไฝ x 100 ๅ
    TODO๏ผ็ฏ็็ๅญๆๆๅ๏ผ็ๅญ้ฟๅบฆๆไฝๅ ๅ
    TODO: ไธๅ็พคไธๅ็้็ฝฎๅๆฐ
    TODO: ่ฝฌ็็บงๅซไธๅไธ่ฝ่พ้
    TODO: ็ๅญๆๅฐๆ่ก
    TODO๏ผ็ๅญๆๅฐฑ้ขๅค็ๆ็คบ่ฏญ
    TODO: ็ฉๅ็ณป็ป
    TODO: ๆฝๅ utils ๆไปถ็ๅฏผๅฅ
    TODO: ็ๅญๅฑไบซๆ่กๆฆ

    TODO๏ผๆๅๅ ๆ
    """
    # lazy init database
    lazy_init_database()

    # message process
    message = message.strip()
    match_func = create_match_func_factory(fuzzy=fuzzy_match)

    # hack at impl
    if impl_at_segment:
        global get_at_segment
        get_at_segment = impl_at_segment

    # ๆถๆฏไธไธๆ๏ผ็จไบ่ฟฝๅ ๆถๆฏ
    msg_ctx = {"before": [get_at_segment(qq)], "after": []}

    def create_send_message_hook(origin_send_message):
        # hack send message impl
        def send_message_hook(qq, group, message):
            before = join(msg_ctx["before"], "\n")
            content = None
            after = join(msg_ctx["after"], "\n")
            # is string
            if isinstance(message, str):
                content = message
            # is list
            elif isinstance(message, list):
                content = join(message, "\n")
            text = join([before, content, after], "\n")
            origin_send_message(qq, group, text)

        return send_message_hook

    global send_message
    if not impl_send_message:
        impl_send_message = send_message
    send_message = create_send_message_hook(impl_send_message)

    # >>> ่ฎฐๅฝใๅๅงๅๆฐๆฎ้ถๆฎต
    # ่ฎฐๅฝๆฐๆฎ - info
    DB.sub_db_info.record_user_info(
        qq,
        {
            "latest_speech_group": group,
            "latest_speech_nickname": nickname,
        },
    )
    # ๅๅงๅๆฐๆฎ - badge
    DB.sub_db_badge.init_user_data(qq, at_qq)
    # ๅๅงๅๆฐๆฎ - farm
    DB.sub_db_farm.init_user_data(qq, at_qq)
    # ๅๅงๅๆฐๆฎ - friends
    DB.sub_db_friends.init_user_data(qq, at_qq)

    # flow context
    ctx = {
        "qq": qq,
        "at_qq": at_qq,
        "group": group,
        "msg_ctx": msg_ctx,
    }

    # ็ๅญๅธฎๅฉ (search)
    if match_func(KEYWORDS.get("help"), message):
        return Chinchin_help.entry_help(ctx)

    # ๆณจๅ็ๅญ
    if match_func(KEYWORDS.get("sign_up"), message):
        return Chinchin_me.sign_up(ctx)

    # ไธ้ข็้ป่พๅฟ้กปๆ็ๅญ
    if not DB.is_registered(qq):
        not_has_chinchin_msg = None
        if at_qq:
            not_has_chinchin_msg = "ๅฏนๆนๅ ไธบไฝ ๆฒกๆ็ๅญๆ็ปไบไฝ ๏ผๅฟซๅปๆณจๅไธๅช็ๅญๅง๏ผไธ็ถไผ่ขซไบบ็งไธ่ตท๏ผ"
        else:
            not_has_chinchin_msg = "ไฝ ่ฟๆฒกๆ็ๅญ๏ผ"
        message_arr = [
            not_has_chinchin_msg,
        ]
        send_message(qq, group, join(message_arr, "\n"))
        return

    # >>> ๆฃๆฅ้ถๆฎต
    # ๆฃๆฅๆๅฐฑ
    badge_msg = BadgeSystem.check_whether_get_new_badge(qq)
    if badge_msg:
        msg_ctx["before"].append(badge_msg)

    # ๆฃๆฅๆๅ
    friends_daily_info = FriendsSystem.check_friends_daily(qq)
    if friends_daily_info:
        msg_ctx["before"].append(friends_daily_info["message"])
        friends_profit = friends_daily_info["profit"]
        if friends_profit > 0:
            DB.length_increase(
                qq,
                Chinchin_intercepor.length_operate(
                    qq, friends_profit, source=OpFrom.FRIENDS_COLLECT, at_qq=at_qq
                ),
            )
        else:
            DB.length_decrease(qq, -friends_profit)

    # ๆฃๆฅไฟฎ็ผ็ถๆ
    is_current_planting = Chinchin_farm.check_planting_status(ctx)

    def eager_return():
        # TODO ๏ผๆฅ็ๆฌกๆฐๅคชๅค่ทๅพ โๆฅๆฅๅฝ็โ ๆๅฐฑ
        message_arr = ["ไฝ ็็ๅญ่ฟๅจ้ญๅณไฟฎ็ผไธญ๏ผๆ ๆณ่ฟ่กๅถไปๆไฝ๏ผๆ็ฅ้ไฝ ๅพๆฅ๏ผไฝไฝ ๅๅซๆฅ"]
        return send_message(qq, group, join(message_arr, "\n"))

    # >>> ๅน้้ถๆฎต
    # ็ๅญไปๅข (search)
    if match_func(KEYWORDS.get("farm"), message):
        return Chinchin_farm.entry_farm_info(ctx)
    # ็ๅญไฟฎ็ผ
    if match_func(KEYWORDS.get("farm_start"), message):
        return Chinchin_farm.entry_farm(ctx)

    # ็ๅญๆๅ (search)
    if match_func(KEYWORDS.get("ranking"), message):
        return Chinchin_info.entry_ranking(ctx)

    # ็ๅญๆๅฐฑ (search)
    if match_func(KEYWORDS.get("badge"), message):
        return Chinchin_badge.entry_badge(ctx)

    # ็ๅญ่ฝฌ็ (opera)
    if match_func(KEYWORDS.get("rebirth"), message):
        # TODO๏ผๅฐ opera ๅ search ๅฝไปคๅๅผ
        if is_current_planting:
            return eager_return()
        else:
            return Chinchin_upgrade.entry_rebirth(ctx)

    # ็ๅ (search)
    if match_func(KEYWORDS.get("friends"), message):
        return Chinchin_friends.entry_friends(ctx)
    
    # ๆฅ่ฏข็ๅญไฟกๆฏ (search)
    # FIXME: ๆณจๆๅ ไธบๆฏๆจก็ณๅน้๏ผๆไปฅ โ็ๅญโ ็ๅฝไปค่ฆๆพๅฐๆๆ "็ๅญxxx" ๅฝไปค็ๆๅ
    if match_func(KEYWORDS.get("chinchin"), message):
        return Chinchin_info.entry_chinchin(ctx)

    # ็ๅญไฟฎ็ผ๏ผๅจไฟฎ็ผ็ถๆไธ่ฝ่ฟ่กๅถไปๆไฝ
    if is_current_planting:
        return eager_return()

    # ๅฏนๅซไบบ็ (opera)
    if at_qq:
        if not DB.is_registered(at_qq):
            message_arr = ["ๅฏนๆน่ฟๆฒกๆ็ๅญ๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return

        # pkๅซไบบ
        if match_func(KEYWORDS.get("pk"), message):
            return Chinchin_with_target.entry_pk_with_target(ctx)

        # ๐ๅซไบบ
        if match_func(KEYWORDS.get("lock"), message):
            return Chinchin_with_target.entry_lock_with_target(ctx)

        # ๆ่ถๅซไบบ
        if match_func(KEYWORDS.get("glue"), message):
            return Chinchin_with_target.entry_glue_with_target(ctx)

        # ็ๅซไบบ็็ๅญ
        if match_func(KEYWORDS.get("see_chinchin"), message):
            return Chinchin_info.entry_see_chinchin(ctx)

        # ็ๅไบคๅ
        if match_func(KEYWORDS.get("friends_add"), message):
            return Chinchin_friends.entry_friends_add(ctx)

        # ็ๅๅๅฐฝ
        if match_func(KEYWORDS.get("friends_delete"), message):
            return Chinchin_friends.entry_friends_delete(ctx)

    else:
        # ๐่ชๅทฑ
        if match_func(KEYWORDS.get("lock_me"), message):
            return Chinchin_me.entry_lock_me(ctx)

        # ่ชๅทฑๆ่ถ
        if match_func(KEYWORDS.get("glue"), message):
            return Chinchin_me.entry_glue(ctx)


class Chinchin_intercepor:
    @staticmethod
    def length_operate(qq: int, origin_change: float, source: str = OpFrom.OTHER, at_qq: int = None):
        # ่ฝฌ็ๅ ๆ
        rebirth_weight = RebirthSystem.get_weight_by_qq(qq)
        result = origin_change * rebirth_weight
        # ๆๅฐฑๅ ๆ
        result = BadgeSystem.handle_weighting_by_qq(qq, result, source)
        # ๆๅๅ ๆ
        result = FriendsSystem.handle_weighting(qq, at_qq=at_qq, length=result, source=source)
        # fixed
        result = fixed_two_decimal_digits(result, to_number=True)
        return result

    @staticmethod
    def length_weight(qq: int, origin_length: float, source: str = OpFrom.OTHER, at_qq: int = None):
        result = origin_length
        # ๆๅๅ ๆ
        result = FriendsSystem.handle_weighting(qq, at_qq=at_qq, length=result, source=source)
        # fixed
        result = fixed_two_decimal_digits(result, to_number=True)
        return result

class Chinchin_view:
    @staticmethod
    def length_label(
        length: float,
        level: int = None,
        need_level_label: bool = True,
        data_only: bool = False,
        unit: str = "cm",
    ):
        if level is None:
            length_value = fixed_two_decimal_digits(length)
            if data_only:
                return {
                    "length": length_value,
                }
            return f"{length_value}{unit}"
        else:
            level_view = RebirthSystem.view.get_rebirth_view_by_level(
                level=level, length=length
            )
            pure_length = level_view["pure_length"]
            if data_only:
                return {
                    "length": fixed_two_decimal_digits(pure_length),
                    "current_level_info": level_view["current_level_info"],
                }
            level_label = ""
            if need_level_label:
                label = level_view["current_level_info"]["name"]
                level_label = f" ({label})"
            return f"{fixed_two_decimal_digits(pure_length)}{unit}{level_label}"


class Chinchin_info:
    @staticmethod
    def entry_ranking(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        msg_ctx = ctx["msg_ctx"]
        # remove before `at` msg
        if len(msg_ctx["before"]) > 0:
            del msg_ctx["before"][0]
        top_users = DB.get_top_users()
        message_arr = [
            "ใ็ๅญๅฎๅฎๆ้ฟๅคง็ๅญใ",
        ]
        for user in top_users:
            idx = top_users.index(user) + 1
            prefix = ""
            if idx == 1:
                prefix = "๐ฅ"
            elif idx == 2:
                prefix = "๐ฅ"
            elif idx == 3:
                prefix = "๐ฅ"
            nickname = user.get("latest_speech_nickname")
            if not nickname:
                nickname = "ๆ ๅ่ฑ้"
            badge = BadgeSystem.get_first_badge_by_badge_string_arr(
                user.get("badge_ids")
            )
            if badge:
                nickname = f"ใ{badge}ใ{nickname}"
            length_label = Chinchin_view.length_label(
                length=user.get("length"),
                level=user.get("level"),
                need_level_label=True,
            )
            message_arr.append(f"{idx}. {prefix}{nickname} ้ฟๅบฆ๏ผ{length_label}")
        send_message(qq, group, join(message_arr, "\n"))

    @staticmethod
    def entry_chinchin(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        user_chinchin_info = ChinchinInternal.internal_get_chinchin_info(qq)
        send_message(qq, group, join(user_chinchin_info, "\n"))

    @staticmethod
    def entry_see_chinchin(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        at_qq = ctx["at_qq"]
        target_chinchin_info = ChinchinInternal.internal_get_chinchin_info(
            at_qq)
        msg_text = join(target_chinchin_info, "\n")
        msg_text = msg_text.replace("ใ็ๅญไฟกๆฏใ", "ใๅฏนๆน็ๅญไฟกๆฏใ")
        send_message(qq, group, msg_text)


class ChinchinInternal:
    @staticmethod
    def internal_get_chinchin_info(qq: int):
        user_data = DB.load_data(qq)
        message_arr = [
            "ใ็ๅญไฟกๆฏใ",
        ]
        # badge
        badge_label = BadgeSystem.get_badge_label_by_qq(qq)
        if badge_label is not None:
            message_arr.append(f"ๆๅฐฑ: {badge_label}")
        length_label = Chinchin_view.length_label(
            length=user_data.get("length"),
            level=user_data.get("level"),
            need_level_label=True,
            unit="ๅ็ฑณ",
        )
        # length
        message_arr.append(f"้ฟๅบฆ: {length_label}")
        # friends
        friends_info = FriendsSystem.get_friends_data(qq)
        share_need_cost = friends_info['friends_need_cost']
        if share_need_cost > 0:
            share_text = None
            share_count = friends_info['friends_share_count']
            if share_count > 0:
                share_text = f"{share_count}ไบบๅฑไบซ"
            message_arr.append(
                join([
                    f"ๅฅฝๅ่ดน: {share_need_cost}cm",
                    share_text
                ], '๏ผ')
            )
        # locked
        if user_data.get("locked_time") != TimeConst.DEFAULT_NONE_TIME:
            message_arr.append(
                "ๆ่ฟ่ขซ๐ๆถ้ด: {}".format(
                    ArrowUtil.date_improve(user_data.get("locked_time"))
                )
            )
        # pk
        if user_data.get("pk_time") != TimeConst.DEFAULT_NONE_TIME:
            message_arr.append(
                "ๆ่ฟpkๆถ้ด: {}".format(
                    ArrowUtil.date_improve(user_data.get("pk_time")))
            )
        # pked
        if user_data.get("pked_time") != TimeConst.DEFAULT_NONE_TIME:
            message_arr.append(
                "ๆ่ฟ่ขซpkๆถ้ด: {}".format(ArrowUtil.date_improve(
                    user_data.get("pked_time")))
            )
        # glueing
        if user_data.get("glueing_time") != TimeConst.DEFAULT_NONE_TIME:
            message_arr.append(
                "ๆ่ฟๆ่ถๆถ้ด: {}".format(
                    ArrowUtil.date_improve(user_data.get("glueing_time"))
                )
            )
        # glued
        if user_data.get("glued_time") != TimeConst.DEFAULT_NONE_TIME:
            message_arr.append(
                "ๆ่ฟ่ขซๆ่ถๆถ้ด: {}".format(
                    ArrowUtil.date_improve(user_data.get("glued_time"))
                )
            )
        # register
        message_arr.append(
            "ๆณจๅๆถ้ด: {}".format(ArrowUtil.date_improve(
                user_data.get("register_time")))
        )
        return message_arr


class Chinchin_me:
    @staticmethod
    def entry_lock_me(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        # check limited
        is_today_limited = DB.is_lock_daily_limited(qq)
        if is_today_limited:
            message_arr = ["ไฝ ็็ๅญไปๅคฉๅคช็ดฏไบ๏ผๆนๅคฉๅๆฅๅง๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return
        # check cd
        is_in_cd = CD_Check.is_lock_in_cd(qq)
        if is_in_cd:
            message_arr = ["ๆญไธไผๅง๏ผๅด้ฝ้บปไบ๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return
        lock_me_min = Config.get_config("lock_me_chinchin_min")
        user_data = DB.load_data(qq)
        DB.record_time(qq, "locked_time")
        DB.count_lock_daily(qq)
        if user_data.get("length") < lock_me_min:
            is_need_punish = Config.is_hit("lock_me_negative_prob")
            if is_need_punish:
                punish_value = Config.get_lock_me_punish_value()
                # not need weighting
                DB.length_decrease(qq, punish_value)
                message_arr = [
                    "ไฝ ็็ๅญ่ฟไธๅค้ฟ๏ผไฝ ๐ไธ็๏ผ็ๅญ่ชๅฐๅฟๅๅฐไบไผคๅฎณ๏ผ็ผฉ็ญไบ{}ๅ็ฑณ".format(punish_value)]
                send_message(qq, group, join(message_arr, "\n"))
            else:
                message_arr = ["ไฝ ็็ๅญๅคชๅฐไบ๏ผ่ฟ๐ไธๅฐ"]
                send_message(qq, group, join(message_arr, "\n"))
        else:
            # record record_lock_me_count to qq
            DB.sub_db_badge.record_lock_me_count(qq)
            # FIXME: ๅ ไธบ๐่ชๅทฑๅๆฅ้ซ๏ผ่ฟๆ ทไผๅฏผ่ดๅผบ่ไธ็ด๐่ชๅทฑ๏ผ่ถๅผบ๏ผๆไปฅ้่ฆไธ็งๅฐๆฆ็ๅถ่ฃๆบๅถใ
            is_lock_failed = Config.is_hit(
                "lock_me_negative_prob_with_strong_person")
            if is_lock_failed:
                punish_value = Config.get_lock_punish_with_strong_person_value()
                # not need weighting
                DB.length_decrease(qq, punish_value)
                # record record_lock_punish_count to qq
                DB.sub_db_badge.record_lock_punish_count(qq)
                # record record_lock_punish_length_total to qq
                DB.sub_db_badge.record_lock_punish_length_total(
                    qq, punish_value)
                message_arr = ["ไฝ ็็ๅญๅคช้ฟไบ๏ผๆฒก๐ไฝ็็ธไบ๏ผ็ผฉ็ญไบ{}ๅ็ฑณ".format(punish_value)]
                send_message(qq, group, join(message_arr, "\n"))
            else:
                plus_value = Chinchin_intercepor.length_operate(
                    qq, Config.get_lock_plus_value(), source=OpFrom.LOCK_ME
                )
                # weighting from qq
                DB.length_increase(qq, plus_value)
                # record record_lock_plus_count to qq
                DB.sub_db_badge.record_lock_plus_count(qq)
                # record record_lock_plus_length_total to qq
                DB.sub_db_badge.record_lock_plus_length_total(qq, plus_value)
                # TODO: ๐่ชๅทฑๆๆๆๅ ๆ
                message_arr = ["่ชๅทฑๆ่ชๅทฑๆ่ๆไบ๏ผ็ๅญๆถจไบ{}ๅ็ฑณ".format(plus_value)]
                send_message(qq, group, join(message_arr, "\n"))

    @staticmethod
    def entry_glue(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        # check limited
        is_today_limited = DB.is_glue_daily_limited(qq)
        if is_today_limited:
            message_arr = ["็ๅญๅฟซ่ขซไฝ ๅฒ็ธไบ๏ผๆนๅคฉๅๆฅๅฒๅง๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return
        # check cd
        is_in_cd = CD_Check.is_glue_in_cd(qq)
        if is_in_cd:
            message_arr = ["ไฝ ๅๆไบไธ่ถ๏ผๆญไธไผๅง๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return
        DB.record_time(qq, "glueing_time")
        DB.count_glue_daily(qq)
        # record record_glue_me_count to qq
        DB.sub_db_badge.record_glue_me_count(qq)
        is_glue_failed = Config.is_hit("glue_self_negative_prob")
        if is_glue_failed:
            punish_value = Config.get_glue_self_punish_value()
            # not need weighting
            DB.length_decrease(qq, punish_value)
            # record record_glue_punish_count to qq
            DB.sub_db_badge.record_glue_punish_count(qq)
            # record record_glue_punish_length_total to qq
            DB.sub_db_badge.record_glue_punish_length_total(qq, punish_value)
            message_arr = ["ๆ่ถ็ปๆ๏ผ็ๅญๅฟซ่ขซๅฒ็็ธไบ๏ผๅๅฐ{}ๅ็ฑณ".format(punish_value)]
            send_message(qq, group, join(message_arr, "\n"))
        else:
            plus_value = Chinchin_intercepor.length_operate(
                qq, Config.get_glue_plus_value(), source=OpFrom.GLUE_ME
            )
            # weighting from qq
            DB.length_increase(qq, plus_value)
            # record record_glue_plus_count to qq
            DB.sub_db_badge.record_glue_plus_count(qq)
            # record record_glue_plus_length_total to qq
            DB.sub_db_badge.record_glue_plus_length_total(qq, plus_value)
            message_arr = ["็ๅญๅฏนไฝ ็ไปๅบๅพๆปกๆๅ๏ผๅขๅ {}ๅ็ฑณ".format(plus_value)]
            send_message(qq, group, join(message_arr, "\n"))

    @staticmethod
    def sign_up(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        if DB.is_registered(qq):
            message_arr = ["ไฝ ๅทฒ็ปๆ็ๅญไบ๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return
        # ๆณจๅ
        new_length = Config.new_chinchin_length()
        new_user = {
            "qq": qq,
            "length": new_length,
            "register_time": ArrowUtil.get_now_time(),
            "daily_lock_count": 0,
            "daily_pk_count": 0,
            "daily_glue_count": 0,
            "latest_daily_lock": TimeConst.DEFAULT_NONE_TIME,
            "latest_daily_pk": TimeConst.DEFAULT_NONE_TIME,
            "latest_daily_glue": TimeConst.DEFAULT_NONE_TIME,
            "pk_time": TimeConst.DEFAULT_NONE_TIME,
            "pked_time": TimeConst.DEFAULT_NONE_TIME,
            "glueing_time": TimeConst.DEFAULT_NONE_TIME,
            "glued_time": TimeConst.DEFAULT_NONE_TIME,
            "locked_time": TimeConst.DEFAULT_NONE_TIME,
        }
        DB.create_data(new_user)
        message_arr = [
            "ไฝ ๆฏ็ฌฌ{}ไฝๆฅๆ็ๅญ็ไบบ๏ผๅฝๅ้ฟๅบฆ๏ผ{}ๅ็ฑณ๏ผ่ฏทๅฅฝๅฅฝๅๅพๅฎ๏ผ".format(
                DB.get_data_counts(),
                fixed_two_decimal_digits(new_length),
            )
        ]
        send_message(qq, group, join(message_arr, "\n"))


class Chinchin_with_target:
    @staticmethod
    def entry_pk_with_target(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        at_qq = ctx["at_qq"]
        # ไธ่ฝ pk ่ชๅทฑ
        if qq == at_qq:
            message_arr = ["ไฝ ไธ่ฝๅ่ชๅทฑ็็ๅญ่ฟ่ก่พ้๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return
        # check limited
        is_today_limited = DB.is_pk_daily_limited(qq)
        if is_today_limited:
            message_arr = ["ๆๆๅคชๅคๆฌก็ๅญ่ฆ่่ฑไบ๏ผๆนๅคฉๅๆฅๅง๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return
        # check cd
        is_in_cd = CD_Check.is_pk_in_cd(qq)
        if is_in_cd:
            message_arr = ["็ๅญๅ็ปๆๆๆ๏ผๆญไธไผๅง๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return
        # pk ไฟๆคๆบๅถ๏ผ็ฆๆญขๅทๅ
        is_target_protected = DB.is_pk_protected(at_qq)
        if is_target_protected:
            message_arr = ["ๅฏนๆนๅฟซๆฒกๆ็ๅญไบ๏ผ่ก่กๅฅฝๅง๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return
        target_data = DB.load_data(at_qq)
        user_data = DB.load_data(qq)
        target_length = target_data.get("length")
        user_length = Chinchin_intercepor.length_weight(
            origin_length=user_data.get("length"),
            qq=qq, at_qq=at_qq, source=OpFrom.PK_FROM_LENGTH, 
        )
        is_user_win = Config.is_pk_win(user_length, target_length)
        DB.record_time(qq, "pk_time")
        DB.record_time(at_qq, "pked_time")
        DB.count_pk_daily(qq)
        if is_user_win:
            is_giant_kill = user_length < target_length
            if is_giant_kill:
                pk_message = "pkๆๅไบ๏ผๅฏน้ขๆฌไปฅไธบ่ชๅทฑ็ๅญๆฏๆๆฃ็๏ผไฝๆฒกๆณๅฐ่ขซไฝ ๆฟไธ๏ผไฝ ็ๆๆฏๆๆฃ็"
            else:
                pk_message = "pkๆๅไบ๏ผๅฏน้ข็ๅญไธๅผไธๆ๏ผไฝ ็ๆฏๆๆฃ็"
            user_plus_value = Chinchin_intercepor.length_operate(
                qq, Config.get_pk_plus_value(), source=OpFrom.PK_WIN, at_qq=at_qq
            )
            target_punish_value = Chinchin_intercepor.length_operate(
                qq, Config.get_pk_punish_value(), source=OpFrom.PK_LOSE, at_qq=at_qq
            )
            # weighting from qq
            DB.length_increase(qq, user_plus_value)
            # weighting from qq
            DB.length_decrease(at_qq, target_punish_value)
            # record pk_win_count to qq
            DB.sub_db_badge.record_pk_win_count(qq)
            # record record_pk_plus_length_total to qq
            DB.sub_db_badge.record_pk_plus_length_total(qq, user_plus_value)
            message_arr = [
                f"{pk_message}๏ผ็ๅญ่ทๅพ่ชไฟกๅขๅ ไบ{user_plus_value}ๅ็ฑณ๏ผๅฏน้ข็ๅญๅๅฐไบ{target_punish_value}ๅ็ฑณ"
            ]
            send_message(qq, group, join(message_arr, "\n"))
        else:
            user_punish_value = Config.get_pk_punish_value()
            target_plus_value = Config.get_pk_plus_value()
            # not need weighting
            DB.length_decrease(qq, user_punish_value)
            DB.length_increase(at_qq, target_plus_value)
            # record pk_lose_count to qq
            DB.sub_db_badge.record_pk_lose_count(qq)
            # record record_pk_punish_length_total to qq
            DB.sub_db_badge.record_pk_punish_length_total(
                qq, user_punish_value)
            message_arr = [
                "pkๅคฑ่ดฅไบ๏ผๅจๅฏน้ข็ๅญ็้ดๅฝฑ็ฌผ็ฝฉไธ๏ผไฝ ็็ๅญๅๅฐไบ{}ๅ็ฑณ๏ผๅฏน้ข็ๅญๅขๅ ไบ{}ๅ็ฑณ".format(
                    user_punish_value, target_plus_value
                )
            ]
            send_message(qq, group, join(message_arr, "\n"))

    @staticmethod
    def entry_lock_with_target(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        at_qq = ctx["at_qq"]
        # ๐ ่ชๅทฑๆฏๅ็ฌ็้ป่พ
        if qq == at_qq:
            Chinchin_me.entry_lock_me(ctx)
            return
        # TODO๏ผ๐ๅซไบบๅฏ่ฝๅคฑ่ดฅ
        # check limited
        is_today_limited = DB.is_lock_daily_limited(qq)
        if is_today_limited:
            message_arr = ["ๅซ๐ไบ๏ผ่ฆๅฃ่ๆบ็กไบ๏ผๆนๅคฉๅ๐ๅง๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return
        # check cd
        is_in_cd = CD_Check.is_lock_in_cd(qq)
        if is_in_cd:
            message_arr = ["ๆญไธไผๅง๏ผๅด้ฝ้บปไบ๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return
        target_plus_value = Chinchin_intercepor.length_operate(
            qq, Config.get_lock_plus_value(), source=OpFrom.LOCK_WITH_TARGET,
            at_qq=at_qq
        )
        # weighting from qq
        DB.length_increase(at_qq, target_plus_value)
        DB.record_time(at_qq, "locked_time")
        DB.count_lock_daily(qq)
        # record record_lock_target_count to qq
        DB.sub_db_badge.record_lock_target_count(qq)
        # record record_lock_plus_count to qq
        DB.sub_db_badge.record_lock_plus_count(qq)
        # record record_lock_plus_length_total to qq
        DB.sub_db_badge.record_lock_plus_length_total(qq, target_plus_value)
        message_arr = ["๐็ๅพๅๅๅพ่ๆ๏ผๅฏนๆน็ๅญๅขๅ ไบ{}ๅ็ฑณ".format(target_plus_value)]
        send_message(qq, group, join(message_arr, "\n"))

    @staticmethod
    def entry_glue_with_target(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        at_qq = ctx["at_qq"]
        # ๆ่ถ่ชๅทฑ่ทณ่ฝฌ
        if qq == at_qq:
            Chinchin_me.entry_glue(ctx)
            return
        # check limited
        is_today_limited = DB.is_glue_daily_limited(qq)
        if is_today_limited:
            message_arr = ["ไฝ ไปๅคฉๅธฎๅคชๅคไบบๆ่ถไบ๏ผๆนๅคฉๅๆฅๅง๏ผ "]
            send_message(qq, group, join(message_arr, "\n"))
            return
        # check cd
        is_in_cd = CD_Check.is_glue_in_cd(qq)
        if is_in_cd:
            message_arr = ["ไฝ ๅๆไบไธ่ถ๏ผๆญไธไผๅง๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return
        DB.record_time(at_qq, "glued_time")
        DB.count_glue_daily(qq)
        # record record_glue_target_count to qq
        DB.sub_db_badge.record_glue_target_count(qq)
        is_glue_failed = Config.is_hit("glue_negative_prob")
        if is_glue_failed:
            target_punish_value = Chinchin_intercepor.length_operate(
                qq, Config.get_glue_punish_value(), source=OpFrom.GLUE_WITH_TARGET_FAIL, at_qq=at_qq
            )
            # weighting from qq
            DB.length_decrease(at_qq, target_punish_value)
            # record record_glue_punish_count to qq
            DB.sub_db_badge.record_glue_punish_count(qq)
            # record record_glue_punish_length_total to qq
            DB.sub_db_badge.record_glue_punish_length_total(
                qq, target_punish_value)
            message_arr = ["ๅฏนๆน็ๅญๅฟซ่ขซๅคงๅฎถๅฒๅไบ๏ผๅๅฐ{}ๅ็ฑณ".format(target_punish_value)]
            send_message(qq, group, join(message_arr, "\n"))
        else:
            target_plus_value = Chinchin_intercepor.length_operate(
                qq, Config.get_glue_plus_value(), source=OpFrom.GLUE_WITH_TARGET_SUCCESS, at_qq=at_qq
            )
            # weighting from qq
            DB.length_increase(at_qq, target_plus_value)
            # record record_glue_plus_count to qq
            DB.sub_db_badge.record_glue_plus_count(qq)
            # record record_glue_plus_length_total to at_qq
            DB.sub_db_badge.record_glue_plus_length_total(
                qq, target_plus_value)
            message_arr = [
                "ไฝ ็ๆ่ถ่ฎฉๅฏนๆน็ๅญๆๅฐๅพ่ๆ๏ผๅฏนๆน็ๅญๅขๅ {}ๅ็ฑณ".format(target_plus_value)]
            send_message(qq, group, join(message_arr, "\n"))


class Chinchin_upgrade:
    @staticmethod
    def entry_rebirth(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        # TODO: ๆปก่ฝฌไบบๅฃซๆ็คบ๏ผไธ่ฝๅ่ฝฌไบ
        info = RebirthSystem.get_rebirth_info(qq)
        if info["can_rebirth"] is False:
            message_arr = ["ไฝ ๅ็ๅญๅ็ฎ็ธๅฏน๏ผ็ๅญๆไบๆๅคด๏ผ่ฏดไธๆฌกไธๅฎ๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return
        # rebirth
        is_rebirth_fail = info["failed_info"]["is_failed"]
        if is_rebirth_fail:
            # punish
            punish_length = info["failed_info"]["failed_punish_length"]
            DB.length_decrease(qq, punish_length)
            message_arr = [
                "็ปๆฐ็็ไนไธญ๏ผ่ดธ็ถๆธกๅซ่ไน็ไธ็๏ผ็ๅญๅคฑๅป่ๆ็็ธไบ๏ผๅๅฐ{}ๅ็ฑณ".format(punish_length)]
            send_message(qq, group, join(message_arr, "\n"))
            return
        # success
        is_first_rebirth = info["current_level_info"] is None
        rebirth_data = {
            "qq": qq,
            "level": info["next_level_info"]["level"],
            "latest_rebirth_time": ArrowUtil.get_now_time(),
        }
        if is_first_rebirth:
            DB.sub_db_rebirth.insert_rebirth_data(rebirth_data)
        else:
            DB.sub_db_rebirth.update_rebirth_data(rebirth_data)
        message_arr = [
            "ไฝ ไธบไบๅผบๅบฆๅทฒ็ป่ตฐไบๅคช่ฟ๏ผๅดๅฟ่ฎฐๅฝๅไธบไปไน่ๅบๅ๏ผ็ตๅ็ณ็ซ้ด้ฃๅไธบใ{}ใ๏ผ".format(
                info["next_level_info"]["name"]
            )
        ]
        send_message(qq, group, join(message_arr, "\n"))
        return


class Chinchin_badge:
    @staticmethod
    def entry_badge(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        badge_view = BadgeSystem.get_badge_view(qq)
        message_arr = []
        if badge_view is None:
            message_arr.append("็ฐๅจๆฏๅนปๆณๆถ้ด")
        else:
            message_arr.append(badge_view)
        send_message(qq, group, join(message_arr, "\n"))


class Chinchin_farm:
    @staticmethod
    def entry_farm_info(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        view = FarmSystem.get_farm_view(qq)
        message_arr = [view]
        send_message(qq, group, join(message_arr, "\n"))

    @staticmethod
    def entry_farm(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        # ๆฃๆฅๆฏๅฆๅฏ็ฉ
        is_current_can_play = FarmSystem.is_current_can_play()
        if not is_current_can_play:
            message_arr = ["็ๅญไปๅขๅคง้จ็ดง้ญ๏ผๆไบๆถๅๅๆฅๅง๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return
        # ๆฃๆฅๆฏๅฆๆญฃๅจไฟฎ็ผ
        is_current_planting = FarmSystem.is_current_planting(qq)
        if is_current_planting:
            message_arr = ["็จๅฎๅฟ่บ๏ผไฝ ็็ๅญๆญฃๅจ็งๅฏไฟฎ็ปไธญ๏ผ"]
            send_message(qq, group, join(message_arr, "\n"))
            return
        # ๅฏ็ฉ็้ป่พ, start plant
        plant_info = FarmSystem.start_plant(qq)
        need_time_minutes = plant_info["need_time_minutes"]
        message_arr = [f"็ฅๅชไผๅจๅฟ่ฆ็ๆถๅๅฑ็ฐไป็ๅญ็ๅฐๅฑฑไธ่ถ๏ผๅฎๆ้ฃๅ้ข่ฎก้่ฆ{need_time_minutes}ๅ้"]
        send_message(qq, group, join(message_arr, "\n"))

    @staticmethod
    def check_planting_status(ctx):
        qq = ctx["qq"]
        is_current_planting = FarmSystem.is_current_planting(qq)
        if not is_current_planting:
            data = DB.sub_db_farm.get_user_data(qq)
            is_plant_over = FarmConst.is_planting(data["farm_status"])
            if is_plant_over:
                # reset user
                FarmSystem.reset_user_data(qq)
                # reward length
                expect_plus_length = data["farm_expect_get_length"]
                reward_length = Chinchin_intercepor.length_operate(
                    qq, expect_plus_length, source=OpFrom.FARM_OVER
                )
                # update length
                DB.length_increase(qq, reward_length)
                # add msg
                ctx["msg_ctx"]["before"].append(
                    f"็ๅญไฟฎ็ผ็ปๆ๏ผไฝ ๆ่งๅๆๆชๆ็่ๆ๏ผๅขๅ ไบ{reward_length}ๅ็ฑณ"
                )
        return is_current_planting


class Chinchin_friends:
    @staticmethod
    def entry_friends(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        view = FriendsSystem.get_friends_list_view(qq)
        message_arr = [view]
        send_message(qq, group, join(message_arr, "\n"))

    @staticmethod
    def entry_friends_add(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        at_qq = ctx["at_qq"]
        config = FriendsSystem.read_config()
        max = config["max"]
        friends_data = FriendsSystem.get_friends_data(qq)
        # ๆๅๆปกไบ
        is_friends_limit = len(friends_data["friends_list"]) >= max
        message_arr = ["ไธ่ฆๅทไบ๏ผไฝ ็็ๅๅทฒ็ปๅคๅคไบ๏ผ"]
        if is_friends_limit:
            return send_message(qq, group, join(message_arr, "\n"))
        # ๅทฒ็ปๆฏๆๅไบ
        is_already_friends = at_qq in friends_data["friends_list"]
        message_arr = ["ไปๅทฒ็ปๆฏไฝ ็็ๅไบ๏ผๅๅผๅงไบๆฏๅงใ"]
        if is_already_friends:
            return "\n".join(message_arr)
        # ๅๅคๆทปๅ ๆๅ
        # ่ฎก็ฎ่ดน็จ
        target_friends_data = FriendsSystem.get_friends_data(at_qq)
        target_shared_count = target_friends_data["friends_share_count"]
        target_user_length = target_friends_data["length"]
        daily_need_cost = fixed_two_decimal_digits(
            config["cost"]["base"] * target_user_length
            + config["cost"]["share"] * target_shared_count,
            to_number=True,
        )
        current_length = friends_data["length"]
        is_can_pay_length = current_length >= daily_need_cost
        if not is_can_pay_length:
            message_arr = ["่ชๅทฑ็็ๅญ้ฝๅฟซๆฒกไบ๏ผ่ฟๆณ็ฝๅซใ"]
            return send_message(qq, group, join(message_arr, "\n"))
        # immediate pay
        DB.length_decrease(qq, daily_need_cost)
        nickname = target_friends_data.get("latest_speech_nickname")
        if not nickname:
            nickname = "ๆ ๅ่ฑ้"
        message_arr = [
            f"โ่ฟๆฏไปๅคฉ็ๆๅ่ดน...โ๏ผโ่ฆๆฐธ่ฟๅจไธ่ตทๅo(*๏ฟฃโฝ๏ฟฃ*)โ๏ผไฝ ไปๅบไบ{daily_need_cost}cm๏ผ้กบๅฉๅ{nickname}ๆไธบไบๅฅฝๆๅ๏ผ",
        ]
        # transfer length
        will_get_length = daily_need_cost * (1 - config["fee"]["friends"])
        DB.length_increase(at_qq, will_get_length)
        # add friend
        FriendsSystem.add_friends(qq, at_qq)
        return send_message(qq, group, join(message_arr, "\n"))

    @staticmethod
    def entry_friends_delete(ctx: dict):
        # TODO: ๅๅฐฝ้่ฆๆถ่ดน
        # TODO: ๅไธๆฏๆไบคๅไธๆ้ ๆ็้ฎ้ข๏ผๆฏๅฆไบคไบๆๅไฝๆฏๅฏนๆน้็พคไบ๏ผๆฒกๆณ at ไปๆญ็ปๅณ็ณปไบใ
        qq = ctx["qq"]
        group = ctx["group"]
        at_qq = ctx["at_qq"]
        # ๆฃๆฅๆฏๅฆๆฏๆๅ
        friends_data = FriendsSystem.get_friends_data(qq)
        is_already_friends = at_qq in friends_data["friends_list"]
        if not is_already_friends:
            message_arr = ["ไปไธๆฏไฝ ็็ๅ๏ผๅๅผๅงไบๆฏๅงใ"]
            return send_message(qq, group, join(message_arr, "\n"))
        # ๅ ้คๆๅ
        nickname = friends_data.get("latest_speech_nickname")
        if not nickname:
            nickname = "ๆ ๅ่ฑ้"
        message_arr = [
            f"ๆ่ฆๅ้ ไธไธชๆๆ็ๅญ้ฝๅไผค็ไธ็...๏ผไฝ ไปฌ้ฝๆฏๆ็ๆๅ๏ผไฝไนๆฏๆ็ๆไบบ๏ผๅ{nickname}ๆญ็ปไบๅณ็ณป"]
        FriendsSystem.delete_friends(qq, at_qq)
        return send_message(qq, group, join(message_arr, "\n"))

class Chinchin_help():

    @staticmethod
    def entry_help(ctx: dict):
        qq = ctx["qq"]
        group = ctx["group"]
        send_message(qq, group, HELPPER)
