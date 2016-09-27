# -*- encoding: utf-8 -*-

import sqlite3
import config

NOW = 0
DATE = 1
TIME = 2

RAW_NOW = 4
RAW_DATE = 31
RAW_TIME = 32

HOUR = 0
MINUTE = 1
SECOND = 2

HIGH = 0
LOW = 1
CLOSED = 2
DT = 3
MIN = 4
MARK = 5
MARK_END = "END"
MARK_ING = "ING"

T0935 = 575
T1130 = 690
T1200 = 720
T1305 = 785
T1500 = 900
T1530 = 930

REPEAT = 8  # 8-9最合理,不超过60s,不会计算入下一条K线,又可以最大化低概率事件.


class KLine(object):
    def __init__(self, code):
        self.high = 0.0  # mark the high and low
        self.low = 1000000.00  # init is high enough
        self.closed = 0.0
        self.datetime = "2016-08-15 8:00:02"  # judge if the same minute
        self.minute = 0  # judge if the same K line
        self.code = code

        db_name = code + ".sqlite"
        print db_name
        self._conn = sqlite3.connect(db_name)

    def __del__(self):
        self._conn.close()

    def get_kline(self, data):
        print data

    def get_now(self):
        return self.closed

    def store(self, k):
        print k

    def fetch(self, count):
        print count

    def get_peek(self, count):
        print count

    def _set_max_min(self, curr):
        mark = True  # 标记数据有变化,False表示数据没变化
        if curr > self.high:
            self.high = curr
        if curr < self.low:
            self.low = curr

        if self.closed == curr:
            mark = False

        self.closed = curr

        return mark


class KLine1Min(KLine):
    def __init__(self, code):
        self._mark_0931 = False  # 标记是否是第一个数据
        self._mark_1301 = False
        self._mark = False
        self._count = 0
        KLine.__init__(self, code)

    def get_kline(self, data):
        r = [float(data[RAW_NOW]), data[RAW_DATE], data[RAW_TIME]]
        # r = [data[NOW], data[DATE], data[TIME]]
        print "raw_data: ", r
        config.LOGGER.info("raw_data: %s %s %s", str(r[0]), str(r[1]), str(r[2]))
        k1 = []
        dt = r[DATE] + " " + r[TIME]
        # if dt == self.datetime:  # desert the same record, 这里不能丢弃,丢弃会影响5分钟K线的处理
        #     return k1

        t = r[TIME].split(':')
        minute = int(t[HOUR])*60 + int(t[MINUTE])  # convert hour to seconds
        if self.minute != minute:  # next minute time record is coming
            self._mark = False
            self._count = 0
            if self.minute == 0:  # check if the first record
                self.high = self.low = self.closed = r[NOW]
            else:
                k1 = [self.high, self.low, self.closed, self.datetime, self.minute, MARK_ING]
                self.high = self.low = r[NOW]  # next k line, reset the high and low
            self.minute = minute  # update the minute
            self.datetime = dt  # update the datetime
            self.closed = r[NOW]
        else:  # calc the high and low
            if self._mark is False:
                res = self._set_max_min(r[NOW])
                if res is False:
                    self._count += 1
                    if self._count == REPEAT:
                        k1 = [self.high, self.low, self.closed, self.datetime, self.minute, MARK_END]
                        self._count = 0
                        self._mark = True

                self.datetime = dt  # update the datetime

        return k1

    def store(self, k):
        if len(k):
            print "k1: ", k
            config.LOGGER.info("k1: %s %s %s %s", str(k[0]), str(k[1]), str(k[2]), str(k[3]))
            try:
                self._conn.execute("INSERT INTO min1 (high, low, closed, fetch_time) VALUES (?, ?, ?, ?)",
                                   (k[HIGH], k[LOW], k[CLOSED], k[DT]))
                self._conn.commit()
            except Exception, e:
                print "sql insert e is ", e
            return True
        else:
            return False

    def fetch(self, count):
        cursor = self._conn.execute("SELECT high, low, closed, fetch_time from min1 ORDER BY fetch_time DESC LIMIT %d"
                                    % count)
        data = cursor.fetchall()  # get all record in db
        data.reverse()  # order by time
        cursor.close()  # release the cursor resource
        return data

    def get_peek(self, count):
        cursor = self._conn.execute("SELECT MAX(high), MIN(low) from min1 ORDER BY fetch_time DESC LIMIT %d"
                                    % count)
        peek = cursor.fetchall()
        return peek[0]


class KLine5Min(KLine):
    def __init__(self, code):
        self._mark_0935 = False  # 标记是否是第一个数据
        self._mark_04 = False
        self._mark_59 = False
        self._mark_1305 = False
        KLine.__init__(self, code)

    def get_kline(self, k):
        """通过 1分钟K线得到5分钟K线

        如果1分钟K线是不连续的，该算法可能出现问题，合并会乱掉,
        9:35前的数据合并到一根线
        11：25～12：00的数据合并到一条K线
        12：00～13：05的数据合并到一条K线
        14：55～15：30的数据合并到一条K线
        11:30，15：00后如果返回的数据相同代表该K线组合完成，后面的数据丢弃
        :param k: 1分钟K线数据
        :return: 列表形式的单根5分钟K线或者[]
        """
        if len(k) < 1:
            return []

        minute = k[MIN]
        k5 = []
        if minute < T0935:
            self._set_max_min(k[NOW])
            self.datetime = k[DT]
            self._mark_0935 = True
            self.minute = minute
        elif minute < T1130:
            if self._mark_0935:  # (1), 此时_mark5_04, _mark5_59必然是False
                self._mark_0935 = False
                k5 = [self.high, self.low, self.closed, self.datetime, self.minute, MARK_ING]

            if (minute % 10) / 5 == 0:
                self._mark_04 = True
                if self._mark_59:  # (2) 此处跟（1）不可能同时发生
                    self._mark_59 = False
                    k5 = [self.high, self.low, self.closed, self.datetime, self.minute, MARK_ING]
            else:
                self._mark_59 = True
                if self._mark_04:  # (3) 此处跟（1）不可能同时发生
                    self._mark_04 = False
                    k5 = [self.high, self.low, self.closed, self.datetime, self.minute, MARK_ING]

            self._set_max_min(k[NOW])
            self.minute = minute
            self.datetime = k[DT]
        elif minute < T1200:  # 时间统一标注为 "xxxx-xx-xx 11:29:59"
            if self._mark_59:  # 25-29的数据还没有完成,如果完成了就把数据丢掉
                res = self._set_max_min(k[NOW])
                if res is False or k[MARK] == MARK_END:  # 不存在数据更新就认为结束了
                    self._mark_59 = False
                    dt = k[DT].split(' ')
                    st = dt[0] + " " + "11:29:59"
                    k5 = [self.high, self.low, self.closed, st, self.minute, MARK_END]
        elif minute < T1305:
            self._set_max_min(k[NOW])
            self.minute = minute
            self.datetime = k[DT]
            self._mark_1305 = True
        elif minute < T1500:
            if self._mark_1305:
                self._mark_1305 = False
                k5 = [self.high, self.low, self.closed, self.datetime, self.minute, MARK_ING]

            if (minute % 10) / 5 == 0:
                self._mark_04 = True
                if self._mark_59:
                    self._mark_59 = False
                    k5 = [self.high, self.low, self.closed, self.datetime, self.minute, MARK_ING]
            else:
                self._mark_59 = True
                if self._mark_04:
                    self._mark_04 = False
                    k5 = [self.high, self.low, self.closed, self.datetime, self.minute, MARK_ING]

            self._set_max_min(k[NOW])
            self.minute = minute
            self.datetime = k[DT]
        elif minute < T1530:  # 时间统一标注为 "xxxx-xx-xx 14:59:59"
            if self._mark_59:  # 25-29的数据还没有完成,如果完成了就把数据丢掉
                res = self._set_max_min(k[NOW])
                if res is False or k[MARK] == MARK_END:  # 不存在数据更新活着1分钟K线带有结束标志就认为结束了
                    self._mark_59 = False
                    dt = k[DT].split(' ')
                    st = dt[0] + " " + "14:59:59"
                    k5 = [self.high, self.low, self.closed, st, self.minute, MARK_END]
        else:
            return []

        if len(k5) > 0:
            self.high = 0.0
            self.low = 1000000.00
            self.closed = 0.0

        return k5

    def store(self, k):
        if len(k):
            print "k5: ", k
            config.LOGGER.info("k5: %s %s %s %s", str(k[0]), str(k[1]), str(k[2]), str(k[3]))
            try:
                self._conn.execute("INSERT INTO min5 (high, low, closed, fetch_time) VALUES (?, ?, ?, ?)",
                                   (k[HIGH], k[LOW], k[CLOSED], k[DT]))
                self._conn.commit()
            except Exception, e:
                print "sql insert e is ", e
            return True
        else:
            return False

    def fetch(self, count):
        cursor = self._conn.execute("SELECT high, low, closed, fetch_time from min5 ORDER BY fetch_time DESC LIMIT %d"
                                    % count)
        data = cursor.fetchall()  # get all record in db
        data.reverse()  # order by time
        cursor.close()  # release the cursor resource
        return data

    def get_peek(self, count):
        cursor = self._conn.execute("SELECT MAX(high), MIN(low) from min5 ORDER BY fetch_time DESC LIMIT %d"
                                    % count)
        peek = cursor.fetchall()
        return peek[0]


class KLineDay(KLine):
    def __init__(self, code):
        KLine.__init__(self, code)

    def get_kline(self, data):
        pass


class KLineMonth(KLine):
    pass


# if __name__ == "__main__":
#     kline1 = KLine1Min("sh000001")
#     kline5 = KLine5Min("sh000001")
#     k = [[2980.4295, "2016-09-26", "15:01:03"],
#          [2980.4295, "2016-09-26", "15:01:03"],
#          [2980.4295, "2016-09-26", "15:01:03"],
#          [2980.4295, "2016-09-26", "15:01:03"],
#          [2980.4295, "2016-09-26", "15:01:03"],
#          [2980.4295, "2016-09-26", "15:01:03"],
#          [2980.4295, "2016-09-26", "15:01:03"],
#          [2980.4295, "2016-09-26", "15:01:03"],
#          [2980.4295, "2016-09-26", "15:01:03"],
#          [2980.4295, "2016-09-26", "15:01:03"],
#          [2980.4295, "2016-09-26", "15:01:03"],
#          [2980.4295, "2016-09-26", "15:01:03"],
#          [2980.4295, "2016-09-26", " 15:00:47"],
#          [2980.6811, "2016-09-26", " 14:59:57"],
#          [2980.7904, "2016-09-26", " 14:58:57"],
#          [2980.7625, "2016-09-26", " 14:57:57"],
#          [2981.1489, "2016-09-26", " 14:56:57"],
#          [2981.6039, "2016-09-26", " 14:55:57"],
#          [2982.0711, "2016-09-26", " 14:54:52"],
#          [2983.1922, "2016-09-26", " 14:53:57"],
#          [2983.971, "2016-09-26", " 14:52:57"],
#          [2985.3906, "2016-09-26", " 14:51:57"],
#          [2986.9492, "2016-09-26", " 14:50:57"],
#          [2987.1787, "2016-09-26", " 14:49:57"],
#          [2988.2995, "2016-09-26", " 14:48:56"]]
#     k.reverse()
#
#     for i in range(0, 25):
#         k1 = kline1.get_kline(k[i])
#         print "k1:", k1
#         k5 = kline5.get_kline(k1)
#         print "k5: ", k5

# if __name__ == "__main__":
#     kline = KLine1Min("sh000001")
#     rec = kline.fetch(250)
#     for item in rec:
#         print item
#
#     pk = kline.get_peek(250)
#     print pk

# if __name__ == "__main__":
#     rec0 = [10.06, '2016-08-15', '14:54:02']
#     rec1 = [10.020, '2016-08-15', '14:55:02']
#     rec2 = [10.00, '2016-08-15', '14:55:03']
#     rec3 = [10.02, '2016-08-15', '14:56:02']
#     rec4 = [10.50, '2016-08-15', '14:57:03']
#     rec5 = [10.40, '2016-08-15', '14:58:02']
#     rec6 = [10.10, '2016-08-15', '14:59:03']
#     rec7 = [10.01, '2016-08-15', '14:59:04']
#     rec8 = [10.58, '2016-08-15', '15:01:06']
#     rec9 = [10.58, '2016-08-15', '15:02:04']
#     rec10 = [10.58, '2016-08-15', '15:03:04']
#     kline1 = KLine1Min("sh000001")
#     kline5 = KLine5Min("sh000001")
#     k1 = kline1.get_kline(rec0)
#     k5 = kline5.get_kline(k1)
#     print k5
#     kline1.store(k1)
#     kline5.store(k5)
#     k1 = kline1.get_kline(rec1)
#     k5 = kline5.get_kline(k1)
#     print k5
#     kline1.store(k1)
#     kline5.store(k5)
#     k1 = kline1.get_kline(rec2)
#     k5 = kline5.get_kline(k1)
#     print k5
#     kline1.store(k1)
#     kline5.store(k5)
#     k1 = kline1.get_kline(rec3)
#     k5 = kline5.get_kline(k1)
#     print k5
#     kline1.store(k1)
#     kline5.store(k5)
#     k1 = kline1.get_kline(rec4)
#     k5 = kline5.get_kline(k1)
#     print k5
#     kline1.store(k1)
#     kline5.store(k5)
#     k1 = kline1.get_kline(rec5)
#     k5 = kline5.get_kline(k1)
#     print k5
#     kline1.store(k1)
#     kline5.store(k5)
#     k1 = kline1.get_kline(rec6)
#     k5 = kline5.get_kline(k1)
#     print k5
#     kline1.store(k1)
#     kline5.store(k5)
#     k1 = kline1.get_kline(rec7)
#     k5 = kline5.get_kline(k1)
#     print k5
#     kline1.store(k1)
#     kline5.store(k5)
#     k1 = kline1.get_kline(rec8)
#     k5 = kline5.get_kline(k1)
#     print k5
#     kline1.store(k1)
#     kline5.store(k5)
#     k1 = kline1.get_kline(rec9)
#     k5 = kline5.get_kline(k1)
#     print k5
#     kline1.store(k1)
#     kline5.store(k5)
#     k1 = kline1.get_kline(rec10)
#     k5 = kline5.get_kline(k1)
#     print k5
#     kline1.store(k1)
#     kline5.store(k5)
