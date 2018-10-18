from django.shortcuts import render
from django.views.generic.list import ListView
from pm.models import SubProject
import operator
from functools import partial, reduce, update_wrapper
from django.db.models import Q
from teacher.models import SampleInfoForm



class ProjectListView(ListView):
    model = SubProject
    def get_context_data(self, **kwargs):
        context = super(ProjectListView,self).get_context_data(**kwargs)
        context["opts"] = SubProject._meta
        context['has_permission'] = True
        context['has_filters'] = True
        context['site_url'] = '/'
        query =  self.request.GET.get('q')
        if query:
            query = query.strip()
            context['queryq'] = query
        return context

    def get_queryset(self):
        result = super(ProjectListView, self).get_queryset()
        print(self.request)
        query = self.request.GET.get('q')
        if query:
            query = query.strip()
            #模糊检索合同号，和检索项目id
            result = SubProject.objects.filter(reduce(operator.or_, [Q(contract__contract_number__icontains=query),Q(id__icontains=query)]))
            return result
        querystatus = self.request.GET.get('status')
        if querystatus:
            querystatus = querystatus.strip()
            #模糊检索合同号，和检索项目id
            result = SubProject.objects.filter(status=querystatus)
            return result
        return result


class SampleInfoFormListView(ListView):
    model = SampleInfoForm
    def get_context_data(self, **kwargs):
        context = super(SampleInfoFormListView,self).get_context_data(**kwargs)
        context["opts"] = SampleInfoForm._meta
        context['has_permission'] = True
        context['has_filters'] = True
        context['site_url'] = '/'
        query = self.request.GET.get('q')
        if query:
            query = query.strip()
            context['queryq'] = query
        return context

    def get_queryset(self):
        result = super(SampleInfoFormListView, self).get_queryset()
        print(self.request)
        query = self.request.GET.get('q')
        if query:
            query = query.strip()
            #模糊检索合同号，和检索项目id
            result = SampleInfoForm.objects.filter(reduce(operator.or_, [Q(contract__contract_number__icontains=query),Q(id__icontains=query)]))
            return result
        querystatus = self.request.GET.get('status')
        if querystatus:
            querystatus = querystatus.strip()
            #模糊检索合同号，和检索项目id
            result = SampleInfoForm.objects.filter(status=querystatus)
            return result
        return result