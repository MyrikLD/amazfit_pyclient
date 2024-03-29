from enum import Enum, IntFlag


class HeaderFlags(IntFlag):
    first_chunk = 0x01
    last_chunk = 0x02
    needs_ack = 0x04
    encrypted = 0x08

    def __getattribute__(self, item):
        if item.startswith("_"):
            return super().__getattribute__(item)

        if item in self._member_map_:
            return super().__getattribute__(item) in self

        return super().__getattribute__(item)


class ChunkedEndpoint(int, Enum):
    SERVICES_0 = 0x0000

    HTTP = 0x0001
    WIFI = 0x0003
    UNKNOWN_5 = 0x0005
    CALENDAR = 0x0007
    SHORTCUT_CARDS = 0x0009
    CONFIG = 0x000A
    UNKNOWN_0B = 0x000B  # 11
    UNKNOWN_0C = 0x000C  # 12
    ICONS = 0x000D
    WEATHER = 0x000E
    ALARMS = 0x000F
    UNKNOWN_11 = 0x0011  # 17
    UNKNOWN_12 = 0x0012  # 18 TodoModule
    CANNED_MESSAGES = 0x0013
    CONNECT = 0x0015  # 21 ConnectModule
    STEPS = 0x0016
    USER_INFO = 0x0017
    VIBRATION_PATTERNS = 0x0018
    WORKOUT = 0x0019
    FIND_DEVICE = 0x001A
    MUSIC = 0x001B
    HEARTRATE = 0x001D
    NOTIFICATIONS = 0x001E
    DISPLAY = 0x0023
    DISPLAY_ITEMS = 0x0026
    BATTERY = 0x0029
    REMINDERS = 0x0038
    LOGS = 0x003A
    SILENT_MODE = 0x003B
    AUTH = 0x0082
    COMPAT = 0x0090
    DEVICE_FEATURE = 0x0028  # 40 DeviceFeatureModule
    SLEEP_DATA = 0x0032  # 50 SleepDataModule
    BLOODPRESSURE_34 = 0x0034
    UNKNOWN_42 = 0x0042  # 66

    JS = 0x00A0  # 160 JSModule


# m68204id


class ChunkedEndpointSleep(int, Enum):
    QueryVersion = 0x01
    VersionResult = 0x02
    QueryConfig = 0x03
    ConfigResult = 0x04
    QueryData = 0x05
    DataResult = 0x06
    WriteData = 0x07
    WriteDataResult = 0x08
    WritePlan = 0x09
    WritePlanResult = 0x0A
    PlanChange = 0x0B
