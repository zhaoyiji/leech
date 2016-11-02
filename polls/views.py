from django.shortcuts import render
from django.http import HttpResponse

import json

import k_line
import data_analyze

COUNT = 500

# Create your views here.
def index(request):
    kline = k_line.KLine1Min("sh000001")
    k = kline.fetch(COUNT)
    # print k
    history = data_analyze.HistoryData('sh000001')
    part = history.analyze(COUNT)
    exclude = history.format_exclude_view()
    print "exclude: ", exclude
    turnoff = history.format_turnoff_view()
    print "turnoff: ", turnoff
    pen = history.format_pen_view()
    print "pen: ", pen
    seg = history.format_segment_view()
    print "seg: ", seg
    print "part ", part
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
    lines = {"exclude": json.dumps(exclude),
             "part": json.dumps(part),
             "pen": json.dumps(pen),
             "seg": json.dumps(seg),
             "base": base,
             "min": float(peek[1])}

    return render(request, 'polls/hello.html', lines)


def detail(request, question_id):
    question = []
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)
