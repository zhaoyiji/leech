# -*- encoding: utf-8 -*-

import k_line

HIGH = 0
LOW = 1
CLOSED = 2
DT = 3

INCLUDE = 4

TURNOFF = 5

PART = 6

DIRECT = 4

INDEX = 5

D = 0
G = 1
DD = 2
GG = 3

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


class HistoryData(object):
    """Data Analyze

    Analyze History data
    Read from history file and turn to record list, than put the records to real analyze.
    """
    def __init__(self, code):
        self._code = code
        self._line = []
        self._include = []
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
        self._index = self._get_part_index()  # 计算分型并且得到分型的坐标
        print self._index
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
        index = HistoryData.get_point(self._pen)
        pen = self._pen
        while index != -1:
            self._segment.append(index)
            pen = pen[index:]
            index = HistoryData.get_point(pen)

        for i in range(1, len(self._segment)):
            self._segment[i] += self._segment[i-1]

        return self._segment

    @classmethod
    def get_point(cls, pen):
        """通过笔得到线段

        :param pen:
            pen[i][0] = index
            pen[i][1] = val
        """
        direct = HistoryData.get_direction(pen)
        if len(direct) == 0:
            return -1

        index = direct[INDEX]
        if direct[DIRECT] == UP:
            mark = 0  # 标记是否需要处理小底分型的情况
            # d1 = direct[D]
            g1 = direct[G]
            d2 = direct[DD]
            g2 = direct[GG]
            gx = 0  # 暂存变量，需要判断小底分型
            for i in range(5, len(pen)):
                if i % 2 == 0:  # 偶数点为低点，在低点时同时把上一个高点分析了,共四种情况分析
                    g3 = pen[i-1][1]
                    d3 = pen[i][1]
                    if d3 < d2:  # 低点比前一个更低
                        if g3 < g2:  # 低-低 (低点在前，高点在后比较)，有可能符合了条件破坏前一线段条件，分两种情况处理
                            if d3 <= g1:  # 马上可以确定前一个线段成立
                                return index  # 只要低点被突破，就得到了线段结束位置
                            else:  # 这里需要两种判断，一种情况是下一个跌继续跌破g1,一种是形成底分型
                                d2 = d3
                                gx = g3  # 暂存起来，需要判断小底分型
                                mark = 1  # 标记为需要处理小底分型
                        else:  # 低-高，包含关系，处理包含关系
                            g2 = g3
                            index = i-1
                            mark = 0  # 只要高点重新突破，就要重头再来
                    else:  # 低点比前一个高
                        if g3 < g2:  # 高-低，包含关系，处理包含关系
                            d2 = d3
                            if mark == 1:
                                if g3 > gx:  # 内部不存在小包含，必然形成了底分型
                                    return index
                                else:  # 内部存在小包含,处理包含关系
                                    gx = g3
                        else:  # 高-高
                            g1 = g2  # 向前推进
                            g2 = g3
                            d2 = d3
                            index = i-1
                            mark = 0  # 只要高点重新突破，就要重头再来
        else:  # "down"
            mark = 0  # 标记是否需要处理小底分型的情况
            d1 = direct[D]
            # g1 = direct[G]
            d2 = direct[DD]
            g2 = direct[GG]
            dx = 0  # 暂存变量，需要判断小底分型
            for i in range(5, len(pen)):
                if i % 2 == 0:  # 偶数点为高点，在高点时同时把上一个低点分析了,共四种情况分析
                    d3 = pen[i-1][1]
                    g3 = pen[i][1]
                    if g3 > g2:  # 高点比前一个更高
                        if d3 > d2:  # 高-高 (高点在前，低点在后比较)，有可能符合了条件破坏前一线段条件，分两种情况处理
                            if g3 >= d1:  # 马上可以确定前一个线段成立
                                return index  # 只要第一条低点被突破，就得到了线段结束位置
                            else:  # 这里需要两种判断，一种情况是下一个跌继续上攻破d1,一种是形成顶分型
                                g2 = g3
                                dx = d3  # 暂存起来，需要判断小底分型
                                mark = 1  # 标记为需要处理小底分型
                        else:  # 高-低，包含关系，处理包含关系,后包前
                            d2 = d3
                            index = i - 1
                            mark = 0  # 只要低点重新突破，就要重头再来
                    else:  # 高点比前一个低
                        if d3 > d2:  # 低-高，包含关系，处理包含关系
                            g2 = g3
                            if mark == 1:
                                if d3 < dx:  # 内部不存在小包含，必然形成了顶分型
                                    return index
                                else:  # 内部存在小包含,处理包含关系
                                    dx = d3
                        else:  # 低-低
                            d1 = d2  # 向前推进
                            g2 = g3
                            d2 = d3
                            index = i - 1
                            mark = 0  # 只要低点重新突破，就要重头再来

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
