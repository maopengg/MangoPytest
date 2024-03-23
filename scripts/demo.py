
from datetime import datetime

def timestamp_to_datetime(timestamp_ms):
    # 如果时间戳是毫秒级的，需要转换为秒
    timestamp_s = timestamp_ms / 1000.0
    # 将时间戳转换为datetime对象
    dt_object = datetime.fromtimestamp(timestamp_s)
    # 使用strftime格式化日期和时间
    return dt_object.strftime('%Y-%m-%d %H:%M:%S')

# 示例：将毫秒级时间戳转换为年月日时分秒格式
timestamp_ms = 1711178777886
datetime_str = timestamp_to_datetime(timestamp_ms)
print(datetime_str)  # 输出格式如: "2023-07-17 17:39:37"