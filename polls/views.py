from django.shortcuts import render
from django.http import HttpResponse

import json

import k_line
import data_analyze


# Create your views here.
def index(request):
    kline = k_line.KLine1Min("sh000001")
    k = kline.fetch(250)
    # print k
    history = data_analyze.HistoryData('sh000001')
    part = history.analyze(250)
    pen = history.format_pen_view()
    seg = history.format_segment_view()
    # print part
    print "len(part) = ", len(part)
    peek = kline.get_peek(250)
    print "peek: ", peek
    base = 400/(float(peek[0]) - float(peek[1]))
    base = 14
    print "base: ", base
    lines = {"kline": json.dumps(k),
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
