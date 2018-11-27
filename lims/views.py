from django.shortcuts import render

from lims.models import *
from hashlib import md5

def getData(request):
    index = request.GET.get("index")
    msg = "未查找到数据"
    if ExtExecute.objects.filter(query_code=index):
        sub_number = ExtExecute.objects.filter(query_code=index).first().extSubmit.subProject.sub_number
        dataset = ExtExecute.objects.filter(query_code=index).first().sampleinfoext_set.all()
        type = 1
    elif LibExecute.objects.filter(query_code=index):
        sub_number = LibExecute.objects.filter(query_code=index).first().libSubmit.subProject.sub_number
        dataset = LibExecute.objects.filter(query_code=index).first().sampleinfolib_set.all()
        type = 2
    elif SeqExecute.objects.filter(query_code=index):
        sub_number = SeqExecute.objects.filter(query_code=index).first().seqSubmit.subProject.sub_number
        dataset = SeqExecute.objects.filter(query_code=index).first().sampleinfoseq_set.all()
        type = 3
    else:
        return render(request,"Showdata.html",{"error":msg})
    return render(request,"Showdata.html",{"data":dataset,"type":type,"sub_number":sub_number})