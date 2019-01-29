from django import forms


class IntentionForm(forms.ModelForm):
    def clean_price(self):
        if int(self.cleaned_data.get('price')) < 0:
            raise forms.ValidationError('预计成交价不能小于0')
        return self.cleaned_data['price']

    def clean_closing_date(self):
        if self.cleaned_data.get('closing_date') < date.today():
            raise forms.ValidationError('预计成交时间不能早于今日')
        return self.cleaned_data['closing_date']
