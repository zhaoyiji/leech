from django.shortcuts import render
from django.http import HttpResponse

import json

import k_line
import data_analyze

COUNT = 2000


# Create your views here.
def index(request):
    kline = k_line.KLine1Min("sh000001")
    k = kline.fetch(COUNT)
    # print k
    history = data_analyze.HistoryData('sh000001')
    history.analyze(COUNT)
    exclude = history.format_exclude_view()
    print "exclude: ", exclude
    turnoff = history.format_turnoff_view()
    print "turnoff: ", turnoff
    part = history.format_part_view()
    print "part: ", part
    pen = history.format_pen_view()
    print "pen: ", pen
    seg = history.format_segment_view()
    print "seg: ", seg
    ma5 = history.format_ma5_view
    ma10 = history.format_ma10_view
    print "ma5: ", ma5
    print "ma10: ", ma10
    peek = kline.get_peek(COUNT)
    print "peek: ", peek
    base = 400/(float(peek[0]) - float(peek[1]))
    print "base: ", base
    # lines = {"kline": json.dumps(k),
    #          "turnoff": json.dumps(turnoff),
    #          "exclude": json.dumps(exclude),
    #          "part": json.dumps(part),
    #          "pen": json.dumps(pen),
    #          "seg": json.dumps(seg),
    #          "base": base,
    #          "min": float(peek[1])}
    data = {"exclude": json.dumps(exclude),
            "part": json.dumps(part),
            "pen": json.dumps(pen),
            "seg": json.dumps(seg),
            "ma5": json.dumps(ma5),
            "ma10": json.dumps(ma10),
            "base": base,
            "min": float(peek[1])}

    return render(request, 'polls/hello.html', data)


def detail(request, question_id):
    question = []
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)
