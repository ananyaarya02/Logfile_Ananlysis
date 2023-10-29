from django import forms

class LogFileForm(forms.Form):
    log_file = forms.FileField(label='Select a Log File')
    analysis_choices = [
        ('top_10_hours', 'Top 10 Hours'),
        ('code_count', 'Code Count'),
        # Add more options as needed
    ]
    analysis_option = forms.MultipleChoiceField(choices=analysis_choices, widget=forms.CheckboxSelectMultiple)

