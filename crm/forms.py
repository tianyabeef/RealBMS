from datetime import date
from decimal import Decimal
from django import forms
from crm.models import Analyses, ContractApplications


class IntentionForm(forms.ModelForm):
    def clean_price(self):
        if int(self.cleaned_data.get('price')) < 0:
            raise forms.ValidationError('预计成交价不能小于0')
        return self.cleaned_data['price']

    def clean_closing_date(self):
        if self.cleaned_data.get('closing_date') < date.today():
            raise forms.ValidationError('预计成交时间不能早于今日')
        return self.cleaned_data['closing_date']


class ContractApplicationsForm(forms.ModelForm):
    analyses_aa = forms.ModelMultipleChoiceField(
        label="高级分析",
        queryset=Analyses.objects.filter(union_id__contains="AA"),
        widget=forms.CheckboxSelectMultiple()
    )
    analyses_pa = forms.ModelMultipleChoiceField(
        label="个性化分析",
        queryset=Analyses.objects.filter(union_id__contains="PA"),
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        model = ContractApplications
        fields = '__all__'
    
    def _decimalization(self, field_name):
        original = self.cleaned_data.get(field_name)
        if original:
            original = Decimal(original).quantize(Decimal('0.00'))
        return original
    
    def clean_total_price(self):
        return self._decimalization("total_price")

    def clean_sequence_single_price(self):
        return self._decimalization("sequence_single_price")

    def clean_sequence_total_price(self):
        return self._decimalization("sequence_total_price")

    def clean_extract_total_price(self):
        return self._decimalization("extract_total_price")
    
    def clean_sample_return_price(self):
        return self._decimalization("sample_return_price")

    def clean_data_delivery_price(self):
        return self._decimalization("data_delivery_price")

    def clean_first_payment(self):
        return self._decimalization("first_payment")

    def clean_final_payment(self):
        return self._decimalization("final_payment")
