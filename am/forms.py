from am.models import AnaExecute, WeeklyReport
from django import forms


class AnaExecuteModelForm(forms.ModelForm):
    class Meta:
        model = AnaExecute
        fields = "__all__"
    
    def clean_is_submit(self):
        is_submit = self.cleaned_data['is_submit']
        baidu_link = self.cleaned_data['baidu_link']
        end_date = self.cleaned_data['end_date']
        if is_submit and not (baidu_link and end_date):
            raise forms.ValidationError(
                '【结果百度链接】和【截止日期】都填写才可提交', code='invalid value'
            )
        return is_submit


class WeeklyReportModelForm(forms.ModelForm):
    class Meta:
        model = WeeklyReport
        fields = "__all__"
    
    def clean_is_submit(self):
        is_submit = self.cleaned_data['is_submit']
        start_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data['end_date']
        if is_submit and not (start_date and end_date):
            raise forms.ValidationError(
                '【开始日期】和【截止日期】都填写才可提交', code='invalid value'
            )
        return is_submit
