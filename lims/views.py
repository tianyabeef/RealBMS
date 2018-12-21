import datetime

from django.shortcuts import render
from lims.models import *
import os
import zipfile

def getpicture(word):
    if word.split(".")[1] not in ["doc","docx"]:
        return None
    word_zip = word.split(".")[0] + ".zip"
    path = ""
    for i in word.split("/")[0:-1]:
        path += i
        path += "/"
    path += "tem/"
    if not os.path.exists(path):
        os.rename(word,word_zip)
        f = zipfile.ZipFile(word_zip,"r")
        for file in f.filelist:
            f.extract(file,path)
        f.close()
        os.rename(word_zip,word)
        pic = os.listdir(os.path.join(path,"word/media"))
        result = []
        result_ = []
        for i in pic:
            result.append(os.path.join(path,"word/media/") + i)
        for j in result:
            url = "/media/" + j.split("/media/")[1] + "/media/" + j.split("/media/")[2]
            result_.append(url)
        return result_
    else:
        pic = os.listdir(os.path.join(path, "word/media"))
        result = []
        result_ = []
        for i in pic:
            result.append(os.path.join(path, "word/media/") + i)
        for j in result:
            url = "/media/" + j.split("/media/")[1]  + "/media/" +j.split("/media/")[2]
            result_.append(url)
        return result_


def getData(request):
    index = request.GET.get("index")
    msg = "未查找到数据"
    if ExtExecute.objects.filter(query_code=index):
        ext = ExtExecute.objects.filter(query_code=index).first()
        result = getpicture(ext.upload_file.path)
        if result:
            for i in result:
                i = request.META.get("HTTP_HOST") + i
        subject = ext.extSubmit.subProject
        dataset = ext.sampleinfoext_set.all()
        type = 1
    elif LibExecute.objects.filter(query_code=index):
        result = getpicture(LibExecute.objects.filter(query_code=index).first().upload_file.path)
        if result:
            for i in result:
                i = request.META.get("HTTP_HOST") + i
        subject = LibExecute.objects.filter(query_code=index).first().libSubmit.subProject
        dataset = LibExecute.objects.filter(query_code=index).first().sampleinfolib_set.all()
        type = 2
    elif SeqExecute.objects.filter(query_code=index):
        subject = SeqExecute.objects.filter(query_code=index).first().seqSubmit.subProject
        dataset = SeqExecute.objects.filter(query_code=index).first().sampleinfoseq_set.all()
        type = 3
        return render(request, "Showdata.html", {"data": dataset, "type": type, "subject": subject})
    else:
        return render(request,"Showdata.html",{"error":msg})
    return render(request,"Showdata.html",{"data":dataset,"type":type,"subject":subject,"pic":result})