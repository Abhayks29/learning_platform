from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Quiz, Question, Choice


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ('title', 'description', 'time_limit_minutes', 'passing_score')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'description',
            Row(Column('time_limit_minutes'), Column('passing_score')),
            Submit('submit', 'Save Quiz', css_class='bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded'),
        )


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text', 'explanation', 'order')
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2}),
            'explanation': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ('text', 'is_correct')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


ChoiceFormSet = inlineformset_factory(
    Question, Choice,
    form=ChoiceForm,
    fields=('text', 'is_correct'),
    extra=4,
    max_num=6,
    can_delete=True,
)


class QuizAttemptAnswerForm(forms.Form):
    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for question in questions:
            self.fields[f'question_{question.id}'] = forms.ModelChoiceField(
                queryset=question.choices.all(),
                widget=forms.RadioSelect,
                label=question.text,
                empty_label=None,
                required=True,
            )
