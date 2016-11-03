# -*- encoding: utf-8 -*-

CLOSED = 2

MA5_T = 5
MA10_T = 10


def get_ma_x(data, period):
    if len(data) < period:
        return []

    ma = []
    cal = 0.0
    for i in range(0, len(data)):
        cal += data[i][CLOSED]
        if i >= period:
            cal -= data[i-period][CLOSED]
            ma.append(cal / period)
        elif i == period - 1:
            ma.append(cal / period)
        else:
            ma.append(0.0)

    return ma


def get_ma_baseline(data):
    p = [MA5_T, MA10_T]
    ma = [[MA5_T], [MA10_T]]
    for i in range(0, len(p)):
        ma[i] = get_ma_x(data, p[i])

    print ma
    return ma

if __name__ == "__main__":
    print "avg test"
    exclude = []
    get_ma_baseline(exclude)
