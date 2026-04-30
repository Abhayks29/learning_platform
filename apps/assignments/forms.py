from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Assignment, Submission


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ('title', 'description', 'due_date', 'max_score')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'description',
            Row(Column('due_date'), Column('max_score')),
            Submit('submit', 'Save Assignment', css_class='bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded'),
        )


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('text_response', 'file')
        widgets = {
            'text_response': forms.Textarea(attrs={'rows': 8, 'placeholder': 'Write your response here...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'text_response',
            'file',
            Submit('submit', 'Submit Assignment', css_class='bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded'),
        )

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text_response')
        file = cleaned_data.get('file')
        if not text and not file:
            raise forms.ValidationError('Please provide either a text response or upload a file.')
        return cleaned_data


class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('score', 'feedback')
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'score',
            'feedback',
            Submit('submit', 'Save Grade', css_class='bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded'),
        )
