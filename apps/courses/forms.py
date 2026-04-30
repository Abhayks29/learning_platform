from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Course, Lesson, Category


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('title', 'category', 'description', 'thumbnail', 'status')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            Row(Column('category'), Column('status')),
            'description',
            'thumbnail',
            Submit('submit', 'Save Course', css_class='bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded'),
        )


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ('title', 'description', 'video', 'video_url', 'duration_minutes', 'order', 'is_free_preview')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'description',
            'video',
            'video_url',
            Row(Column('duration_minutes'), Column('order')),
            'is_free_preview',
            Submit('submit', 'Save Lesson', css_class='bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded'),
        )

    def clean(self):
        cleaned_data = super().clean()
        video = cleaned_data.get('video')
        video_url = cleaned_data.get('video_url')
        if not video and not video_url:
            raise forms.ValidationError('Provide either a video file or a video URL.')
        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'slug')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'slug',
            Submit('submit', 'Save Category', css_class='bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded'),
        )
