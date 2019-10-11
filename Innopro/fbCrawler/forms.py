import io, csv
from django import forms

from .models import BankStatement

class BankStatementForm(forms.Form):
    
    data_file = forms.FileField()

    def process_data(self):
        f = io.TextIOWrapper(self.cleaned_data['data_file'].file)
        reader = csv.DictReader(f)

        for transaction in reader:
            print(transaction)