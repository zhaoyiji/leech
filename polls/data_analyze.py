# -*- encoding: utf-8 -*-

import k_line
import segment

HIGH = 0
LOW = 1
CLOSED = 2
DT = 3

INCLUDE = 4

TURNOFF = 5

PART = 6

DIRECT = 4

INCLUDE_STR = "include"
UP = "up"
DOWN = "down"
NORMAL = "normal"
IGN = "ignore"
TOP = "top"
BOT = "bottom"
MID = "middle"

MA5 = 5
MA10 = 10
MA20 = 20
MA60 = 60
MA250 = 250

POS = 5


class HistoryData(object):
    """Data Analyze

    Analyze History data
    Read from history file and turn to record list, than put the records to real analyze.
    """
    def __init__(self, code):
        self._code = code
        self._line = []
        # self._include = []
        self._exclude = []
        self._turnoff = []
        self._index = []
        self._part = []
        self._pen = []
        self._segment = []
        self._ma = [[MA5], [MA10], [MA20], [MA60], [MA250]]

    def analyze(self, count):
        """Get ALl Records from history record file min5.dat.

        Get All Records and truncated to 720 records If more than 720 items.
        at the same time, simplified it.

        :param count: count fetch len
        """
        kline = k_line.KLine1Min(self._code)
        self._line = kline.fetch(count)  # 获取数据库记录
        print self._line
        print "### _turnoff #############################################"
        self._turnoff = self._mark_turnoff()  # 标记高低点
        print self._turnoff
        print "### _index #############################################"
        self._index = self._get_part_index  # 计算分型并且得到分型的坐标
        print self._index
        print "### _index #############################################"
        self._exclude = self._get_exclude()
        print self._exclude
        print "### _part #############################################"
        self._part = self._get_part()  # 标记分型
        print self._part
        print "### _pen #############################################"
        self._get_pen()
        print self._pen
        print "### _segment #############################################"
        self._get_segment()
        print self._segment
        print "### view #############################################"
        self.format_segment_view()
        line = self.format_view()
        print "### end #############################################"

        return line

    def _get_ma(self):
        p = [MA5, MA10, MA20, MA60, MA250]
        for i in range(0, 5):
            self._ma[i] = self._get_ma_x(p[i])

        return self._ma

    def _get_ma_x(self, period):
        if len(self._line) < period:
            return []

        ma = []
        cal = 0.0
        for i in range(0, len(self._line)):
            cal += self._line[i][CLOSED]
            if i >= period:
                cal -= self._line[i-period][CLOSED]
                ma.append(cal/period)
            elif i == period - 1:
                ma.append(cal/period)
            else:
                ma.append(0.0)

        return ma

    def _get_segment(self):
        index = HistoryData.get_seg_point(self._pen)
        pen = self._pen
        while index != -1:
            self._segment.append(index)
            pen = pen[index:]
            index = HistoryData.get_seg_point(pen)

        for i in range(1, len(self._segment)):
            self._segment[i] += self._segment[i-1]

        return self._segment

    @classmethod
    def get_seg_point(cls, pen):
        """通过笔得到线段

        算法逻辑:
        [1]:假定第一个分型为线段起点
        [2]:第一笔的方向为主方向,第二笔的方向为次方向,同时计算2组标准特征向量(做包含处理), pen[0][1] > pen[1][1]为下,否则为上
        [3]:计算出主方向的特征序列分型,第一笔向下,则计算底分型,反之计算顶分型 特征序列为 p1p2-p3p4-p5p6...
        [4]:计算出次方向的特征序列分型,第二笔向上,则计算顶分型,反之计算底分型 特征序列为 p0p1-p2p3-p4p5...
        [5]:[3]计算得到的分型比[4]得到的分型先出现,则立刻得到了此次线段端点,计算结束
        [6]:[4]计算得到的分型比[3]得到的分型先出现,如果第一笔向下,分型顶比线段起点高,则立刻得到了线段端点,该端点时上一个端点的延续
            ,比线段起点低,则忽略该分型,继续向下计算。

        其他说明:这里可能出现 线段端点 高-高,低-低的情况,高高则忽略上一个高,低低则忽略上一个低

        :param pen:
            pen[i][0] = index
            pen[i][1] = val
        :return:
            point[0] = index
        """
        minor = segment.Segment.get_seg_minor(pen)
        major = segment.Segment.get_seg_minor(pen)
        if minor:
            if major:
                if major[POS] < minor[POS]:
                    return major[POS]
                else:
                    return minor[POS]
            else:
                return minor[POS]
        else:
            if major:
                return major[POS]
            else:
                return -1

    @classmethod
    def get_direction(cls, pen):
        """获取方向 up\down\[]

            [d1,g1,d2,g2,direct,pos]
        :param pen:
        """
        if len(pen) < 6:
            return []

        direction = DOWN
        if pen[1][1] > pen[0][1]:
            direction = UP
        x1 = pen[1][1]
        y1 = pen[2][1]

        for i in range(4, len(pen)):
            if i % 2 != 0:
                continue

            x = pen[i-1][1]
            y = pen[i][1]
            if x > x1:
                if y > y1:
                    return [y1, x1, y, x, UP, i-1]  # 按照低高低高返回,xy为一组特征序列
                else:
                    if direction == UP:
                        x1 = x
                    else:
                        y1 = y
            else:
                if y >= y1:
                    if direction == UP:
                        y1 = y
                    else:
                        x1 = x
                else:
                    return [x1, y1, x, y, DOWN, i-1]  # 按照低高低高返回,xy为一组特征序列

        return []

    def _get_pen(self):
        for i in range(0, len(self._index)):
            index = self._index[i]
            pen = [index]
            if self._turnoff[index][TURNOFF] == TOP:
                pen.append(self._turnoff[index][HIGH])
            else:
                pen.append(self._turnoff[index][LOW])

            self._pen.append(pen)

        return self._pen

    def _get_part(self):
        for i in self._index:
            val = []
            if self._turnoff[i][TURNOFF] == TOP:
                val.append(self._turnoff[i][HIGH])
                val.append(self._turnoff[i][DT])
            else:
                val.append(self._turnoff[i][LOW])
                val.append(self._turnoff[i][DT])

            self._part.append(val)

        return self._part

    def _get_part_index(self):
        index = []
        peek = self._get_peek_index()
        last_peek = peek[0]
        for i in peek:
            last = self._turnoff[last_peek]
            curr = self._turnoff[i]
            if last[TURNOFF] == TOP:  # 前一个分析的是顶
                if curr[TURNOFF] == TOP:  # 一顶之后又是一顶,这里有可能更新当前的顶位置
                    if curr[HIGH] > last[HIGH]:  # 这个顶比上一个顶要高，要按这个来算,否则的话该顶被忽略
                        last_peek = i
                else:  # curr[3] = "bottom 一顶之后来了一底
                    if (i - last_peek) > 3:  # 符合一顶一底要求，分型间至少有一根K线
                        index.append(last_peek)
                        last_peek = i
            else:  # 前一个分析的是底
                if curr[TURNOFF] == BOT:  # 一底之后又是一底,这里有可能更新当前的底位置
                    if curr[LOW] < last[LOW]:  # 这个底比上一个底要低，要按这个来算,否则的话该底被忽略
                        last_peek = i
                else:  # curr[3] = "bottom 一底之后来了一顶
                    if (i - last_peek) > 3:  # 符合一底一顶要求，分型间至少有一根K线
                        index.append(last_peek)
                        last_peek = i

        return index

    def _get_peek_index(self):
        i = 0
        index = []
        for item in self._turnoff:
            if item[TURNOFF] != MID:
                index.append(i)
            i += 1

        return index

    def _get_exclude(self):
        for item in self._turnoff:
            if item[INCLUDE] != INCLUDE_STR:
                self._exclude.append(item)

        return self._exclude

    def _mark_turnoff(self):
        """标记转折点并且解决K线包含关系.

        经过该函数处理后的K线列表是不存在包含关系，并且各个转折点有标记的K线列表，此处转折点没做分型处理
        """
        turnoff = []  # 记录转折点信息
        direction = UP  # 趋势，默认为向上，即为底
        line = list(self._line[0])  # 元组转化为列表
        line.append(NORMAL)
        line.append(MID)
        for item in self._line:  # 4种情况分析
            if item[HIGH] > line[HIGH]:  # a)当前K线的高点比前一K线的高点高
                if item[LOW] >= line[LOW]:  # （1）当前K线的低点比前一K线的低点要高
                    line[INCLUDE] = NORMAL
                    k = line[:]
                    turnoff.append(k)  # 前一K线属于有效K线，记录下来
                    line = list(item)  # 更新前一K线为当前K线
                    line.append(NORMAL)
                    line.append(MID)
                    if direction == DOWN:  # 如果原趋势向下，则上一条K线为一个底，相应的趋势得改为向上
                        # line[4] = "bottom"  # 标记该K线为一个底
                        k[TURNOFF] = BOT
                        direction = UP
                else:  # （2）当前K线的低点比前一K线的低点要低，这种情况属于包含关系，后包前
                    line[INCLUDE] = INCLUDE_STR
                    k = line[:]
                    turnoff.append(k)  # 前一K线属于无效K线，记录下来并标记为include
                    if direction == UP:
                        line[HIGH] = item[HIGH]  # 向上替换高位数据
                    else:
                        line[LOW] = item[LOW]  # 向下替换低位数据
            else:  # b)当前K线的高点比前一K线的高点要低
                if item[LOW] >= line[LOW]:  # （3）当前K线的低点比前一K线的低点要高，这种情况属于包含关系，前包后
                    k = list(item)
                    k.append(INCLUDE_STR)
                    k.append(MID)
                    turnoff.append(k)  # 前一K线属于无效K线，记录下来并标记为include,\
                    # 这里前后2根K线的位置已经互换，但不影响结果
                    if direction == UP:
                        line[LOW] = item[LOW]  # 向上替换低位数据
                    else:
                        line[HIGH] = item[HIGH]  # 向下替换高位数据
                else:  # （4）当前K线的低点比前一K线的低点要低
                    line[INCLUDE] = NORMAL
                    k = line[:]
                    turnoff.append(k)  # 前一K线属于有效K线，记录下来
                    line = list(item)  # 更新前一K线为当前K线
                    line.append(NORMAL)
                    line.append(MID)
                    if direction == UP:  # 如果原趋势向上，则上一条K线为一个顶，相应的趋势得改为向下
                        # line[4] = TOP  # 标记该K线为一个顶
                        k[TURNOFF] = TOP
                        direction = DOWN

        return turnoff

    def format_exclude_view(self):
        return self._exclude

    def format_turnoff_view(self):
        return self._turnoff

    def format_part_view(self):
        line = self._turnoff[:]  # _turnoff 是列表，_line是元组，选择使用_turnoff
        for item in line:
            item.append(IGN)

        for item in self._index:
            line[item][PART] = line[item][TURNOFF]

        return line

    def format_pen_view(self):
        return self._pen

    def format_segment_view(self):
        point = []
        for item in self._segment:
            point.append(self._pen[item])

        return point

    def format_view(self):
        return self.format_part_view()

if __name__ == "__main__":
    history = HistoryData('sh000001')
    history.analyze(250)
