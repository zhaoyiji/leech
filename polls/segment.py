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


class Segment(object):

    @classmethod
    def get_seg_minor(cls, pen):
        init = Segment.get_seg_init_minor(pen)
        if init:
            direct = init[0]
            start = init[INIT][START]
            d2 = init[D2]
            g2 = init[G2]
            if direct == "down":
                for i in range(start+2, len(pen), 2):
                    d = pen[i][VAL]
                    g = pen[i-1][VAL]
                    if d < d2:
                        if g < g2:  # 低-低,形成了顶分型,符合要求
                            if g2 > pen[0][VAL]:  # 顶不高于上一个顶，忽略，高于上一个顶才有效
                                return ["down", d2, g2, d, g, i]
                        else:  # 低-高,包含关系,后包前
                            g2 = g
                    else:
                        if g < g2:  # 高-低,包含关系,前包后
                            d2 = d
                        else:  # 高-高,忽略g2d2这一笔,继续向下
                            d2 = d
                            g2 = g
            else:
                for i in range(start+2, len(pen), 2):
                    d = pen[i-1][VAL]
                    g = pen[i][VAL]
                    if d > d2:
                        if g > g2:  # 低-低,形成了底分型,符合要求
                            if d2 < pen[0][VAL]:  # 底不低于上一个底，忽略，低于上一个底才有效
                                return ["up", d2, g2, d, g, i]
                        else:  # 高-低,包含关系,前包后
                            g2 = g
                    else:
                        if g > g2:  # 低-高,包含关系,后包前
                            d2 = d
                        else:  # 低-低,忽略d2g2这一笔,继续向下
                            d2 = d
                            g2 = g
        else:
            return []

    @classmethod
    def get_seg_major(cls, pen):
        init = Segment.get_seg_init_major(pen)
        if init:
            direct = init[0]
            start = init[INIT][START]
            d2 = init[D2]
            g2 = init[G2]
            if direct == "down":
                for i in range(start+2, len(pen), 2):
                    d = pen[i-1][VAL]
                    g = pen[i][VAL]
                    if d > d2:
                        if g > g2:  # 高-高,形成了底分型,符合要求
                            return ["down", d2, g2, d, g, i]
                        else:  # 高-低,包含关系,前包后
                            g2 = g
                    else:
                        if g > g2:  # 低-高,包含关系,后包前
                            d2 = d
                        else:  # 高-高,忽略g2d2这一笔,继续向下
                            d2 = d
                            g2 = g
            else:
                for i in range(start+2, len(pen), 2):
                    d = pen[i][VAL]
                    g = pen[i-1][VAL]
                    if d < d2:
                        if g < g2:  # 低-低,形成了顶分型,符合要求
                            return ["up", d2, g2, d, g, i]
                        else:  # 低-高,包含关系,后包前
                            g2 = g
                    else:
                        if g < g2:  # 高-低,包含关系,前包后
                            d2 = d
                        else:  # 高-高,忽略d2g2这一笔,继续向下
                            d2 = d
                            g2 = g
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
