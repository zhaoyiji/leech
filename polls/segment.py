# -*- encoding: utf-8 -*-

VAL = 1

D1 = 0
G1 = 1
D2 = 2
G2 = 3
START = 4
INIT = 1
MAJOR = 1
MINOR = 2

POS = 5


class Segment(object):

    @classmethod
    def get_segment(cls, pen):
        index = Segment.get_seg_point(pen)
        segment = []
        while index != -1:
            segment.append(index)
            pen = pen[index:]
            index = Segment.get_seg_point(pen)

        for i in range(1, len(segment)):  # 把相对位置换算成绝对位置
            segment[i] += segment[i-1]

        return segment

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
        minor = Segment.get_seg_minor(pen)
        major = Segment.get_seg_major(pen)
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
    def get_seg_minor(cls, pen):
        init = Segment.get_seg_init_minor(pen)
        if init and init[INIT]:
            direct = init[0]
            start = init[INIT][START]
            index = start - 1
            d2 = init[INIT][D2]
            g2 = init[INIT][G2]
            if direct == "down":
                for i in range(start+2, len(pen), 2):
                    d = pen[i][VAL]
                    g = pen[i-1][VAL]
                    if d < d2:
                        if g < g2:  # 低-低,形成了顶分型,符合要求
                            if g2 > pen[0][VAL]:  # 顶不高于上一个顶，忽略，高于上一个顶才有效
                                return ["down", d2, g2, d, g, index]
                        else:  # 低-高,包含关系,后包前
                            g2 = g
                            index = i - 1
                    else:
                        if g < g2:  # 高-低,包含关系,前包后
                            d2 = d
                        else:  # 高-高,忽略g2d2这一笔,继续向下
                            d2 = d
                            g2 = g
                            index = i - 1
            else:
                for i in range(start+2, len(pen), 2):
                    d = pen[i-1][VAL]
                    g = pen[i][VAL]
                    if d > d2:
                        if g > g2:  # 低-低,形成了底分型,符合要求
                            if d2 < pen[0][VAL]:  # 底不低于上一个底，忽略，低于上一个底才有效
                                return ["up", d2, g2, d, g, index]
                        else:  # 高-低,包含关系,前包后
                            g2 = g
                    else:
                        if g > g2:  # 低-高,包含关系,后包前
                            d2 = d
                            index = i - 1
                        else:  # 低-低,忽略d2g2这一笔,继续向下
                            d2 = d
                            index = i - 1
                            g2 = g
        else:
            return []

    @classmethod
    def get_seg_major(cls, pen):
        init = Segment.get_seg_init_major(pen)
        if init and init[INIT]:
            direct = init[0]
            start = init[INIT][START]
            index = start - 1
            d2 = init[INIT][D2]
            g2 = init[INIT][G2]
            if direct == "down":
                for i in range(start+2, len(pen), 2):
                    d = pen[i-1][VAL]
                    g = pen[i][VAL]
                    if d > d2:
                        if g > g2:  # 高-高,形成了底分型,符合要求
                            return ["down", d2, g2, d, g, index]
                        else:  # 高-低,包含关系,前包后
                            g2 = g
                    else:
                        if g > g2:  # 低-高,包含关系,后包前
                            d2 = d
                            index = i - 1
                        else:  # 高-高,忽略g2d2这一笔,继续向下
                            d2 = d
                            index = i - 1
                            g2 = g
            else:
                for i in range(start+2, len(pen), 2):
                    d = pen[i][VAL]
                    g = pen[i-1][VAL]
                    if d < d2:
                        if g < g2:  # 低-低,形成了顶分型,符合要求
                            return ["up", d2, g2, d, g, index]
                        else:  # 低-高,包含关系,后包前
                            g2 = g
                            index = i - 1
                    else:
                        if g < g2:  # 高-低,包含关系,前包后
                            d2 = d
                        else:  # 高-高,忽略d2g2这一笔,继续向下
                            d2 = d
                            g2 = g
                            index = i - 1
        else:
            return []

    @classmethod
    def get_seg_init_minor(cls, pen):
        """ 线段端点计算初始化,得到标准特征序列的初始化分型的前2根，同时计算主方向，次方向。

        :param pen:
            pen[i][0] = index
            pen[i][1] = val
        :return: ["direct", [d1, g1, d2, g2, pos]]
                ["direct", init]
        """
        if len(pen) < 6:
            return []

        init = []
        direct = "up"
        if pen[0][VAL] > pen[1][VAL]:
            direct = "down"

        if direct == "up":
            d1 = pen[0][VAL]
            g1 = pen[1][VAL]
            for i in range(3, len(pen), 2):  # 次方向，计算趋势向下特征向量，特征向量方向为低到高,最终目标是得到底分型
                d = pen[i-1][VAL]
                g = pen[i][VAL]
                if d > d1:  # 分四种情况分析(1 VS 2，低点在前，高点在后)
                    if g > g1:  # 高-高 趋势还在向上,前面一条可以忽略了
                        d1 = d
                        g1 = g
                    else:  # 高-低,包含关系，前包后
                        g1 = g
                else:
                    if g >= g1:  # 低-高，包含关系,后包前
                        d1 = d
                    else:  # 低-低
                        init = [d1, g1, d, g, i]  # 得到符合要求的特征向量
                        break
        else:  # direct is "down"
            d1 = pen[1][VAL]
            g1 = pen[0][VAL]
            for i in range(3, len(pen), 2):  # 次方向，计算趋势向上特征向量，特征向量方向为高到低,最终目标是得到顶分型
                d = pen[i][VAL]
                g = pen[i-1][VAL]
                if d > d1:  # 分四种情况分析(1 VS 2，低点在前，高点在后)
                    if g > g1:  # 高-高
                        init = [d1, g1, d, g, i]  # 得到符合要求的特征向量
                        break
                    else:  # 高-低,包含关系，前包后
                        d1 = d
                else:
                    if g >= g1:  # 低-高，包含关系,后包前
                        g1 = g
                    else:  # 低-低 趋势还在向下,前面一条可以忽略了
                        d1 = d
                        g1 = g

        return [direct, init]

    @classmethod
    def get_seg_init_major(cls, pen):
        """ 线段端点计算初始化,得到标准特征序列的初始化分型的前2根，同时计算主方向，次方向。

        :param pen:
            pen[i][0] = index
            pen[i][1] = val
        :return: ["direct", [d1, g1, d2, g2, pos]]
                ["direct", init]
        """
        if len(pen) < 7:
            return []

        init = []
        direct = "up"
        if pen[0][VAL] > pen[1][VAL]:
            direct = "down"

        if direct == "up":
            d1 = pen[2][VAL]
            g1 = pen[1][VAL]
            for i in range(4, len(pen), 2):  # 主方向，计算向上特征向量，特征向量方向为高到低，最终目标是得到顶分型
                g = pen[i-1][VAL]
                d = pen[i][VAL]
                if d > d1:  # 分四种情况分析(1 VS 2，低点在前，高点在后)
                    if g > g1:  # 高-高
                        init = [d1, g1, d, g, i]  # 得到符合要求的特征向量
                        break
                    else:  # 高-低,包含关系，前包后
                        d1 = d
                else:
                    if g >= g1:  # 低-高，包含关系,后包前
                        g1 = g
                    else:  # 低-低 趋势还在向下,前面一条可以忽略了
                        d1 = d
                        g1 = g
        else:  # direct is "down"
            g1 = pen[2][VAL]
            d1 = pen[1][VAL]
            for i in range(4, len(pen), 2):  # 主方向，计算向下特征向量，特征向量方向为低到高，最终目标是得到底分型
                d = pen[i-1][VAL]
                g = pen[i][VAL]
                if d > d1:  # 分四种情况分析(1 VS 2，低点在前，高点在后)
                    if g > g1:  # 高-高, 趋势还在向上，没意义忽略
                        d1 = d
                        g1 = g
                    else:  # 高-低,包含关系，前包后
                        g1 = g
                else:
                    if g >= g1:  # 低-高，包含关系,后包前
                        d1 = d
                    else:  # 低-低 趋势还在向下,前面一条可以忽略了
                        init = [d1, g1, d, g, i]  # 得到符合要求的特征向量
                        break

        return [direct, init]

if __name__ == "__main__":
    # 第一笔向上测试用例
    pen1 = [[0, 1], [1, 3], [2, 2], [3, 5], [4, 3], [5, 4], [6, 2]]
    # pen2 = [[0, 2], [1, 1], [2, 5], [3, 4], [4, 8], [5, 6], [6, 7], [7, 3]]
    # pen3 = [[0, 8], [1, 1], [2, 3], [3, 2], [4, 7], [5, 5], [6, 6], [7, 4]]
    # pen4 = [[0, 8], [1, 1], [2, 7], [3, 4], [4, 2], [5, 3], [6, 5], [7, 6],
    #         [8, 11], [9, 9], [10, 10], [11, 8]]
    # pen5 = [[0, 8], [1, 1], [2, 2], [3, 4], [4, 7], [5, 3], [6, 5], [7, 6],
    #         [8, 11], [9, 9], [10, 10], [11, 8]]

    # 第一笔向下测试用例
    # pen1 = [[0, 9], [1, 7], [2, 8], [3, 5], [4, 7], [5, 6], [6, 8]]
    # pen1 = [[0, 5], [1, 7], [2, 4], [3, 6], [4, 2], [5, 5], [6, 3], [7, 6]]
    # pen1 = [[0, 1], [1, 7], [2, 4], [3, 6], [4, 2], [5, 5], [6, 3], [7, 8], [8, 4], [9, 6], [10, 3]]
    pen1 = [[0, 2], [1, 7], [2, 4], [3, 6], [4, 2], [5, 5], [6, 3], [7, 6], [8, 2], [9, 5],
            [10, 1], [11, 4], [12, 2], [13, 5]]

    # seg = Segment.get_segment(pen1)
    # print seg
    # seg = Segment.get_segment(pen2)
    # print seg
    # seg = Segment.get_segment(pen3)
    # print seg
    # seg = Segment.get_segment(pen4)
    # print seg
    seg = Segment.get_segment(pen1)
    print seg
