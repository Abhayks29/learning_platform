from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import PracticeProblem, TestCase, CodeSubmission


class PracticeProblemForm(forms.ModelForm):
    class Meta:
        model = PracticeProblem
        fields = ('title', 'course', 'description', 'difficulty', 'tags', 'starter_code', 'solution_code')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'starter_code': forms.Textarea(attrs={'rows': 8, 'class': 'font-mono'}),
            'solution_code': forms.Textarea(attrs={'rows': 8, 'class': 'font-mono'}),
            'tags': forms.TextInput(attrs={'placeholder': 'array, string, dynamic-programming'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            Row(Column('difficulty'), Column('course')),
            'tags',
            'description',
            'starter_code',
            'solution_code',
            Submit('submit', 'Save Problem', css_class='bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded'),
        )


class TestCaseForm(forms.ModelForm):
    class Meta:
        model = TestCase
        fields = ('input_data', 'expected_output', 'is_hidden')
        widgets = {
            'input_data': forms.Textarea(attrs={'rows': 2, 'class': 'font-mono'}),
            'expected_output': forms.Textarea(attrs={'rows': 2, 'class': 'font-mono'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


TestCaseFormSet = inlineformset_factory(
    PracticeProblem, TestCase,
    form=TestCaseForm,
    fields=('input_data', 'expected_output', 'is_hidden'),
    extra=3,
    can_delete=True,
)


class CodeSubmissionForm(forms.ModelForm):
    class Meta:
        model = CodeSubmission
        fields = ('code', 'language')
        widgets = {
            'code': forms.Textarea(attrs={'rows': 20, 'class': 'font-mono hidden'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['language'].widget = forms.Select(choices=[
            ('python', 'Python'),
            ('javascript', 'JavaScript'),
            ('java', 'Java'),
            ('cpp', 'C++'),
        ])
