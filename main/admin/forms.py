from django import forms

from main.models import Profile, LanProfile, GRADES


class AdminLanProfileForm(forms.ModelForm):
    class Meta:
        model = LanProfile
        fields = '__all__'


class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'

    grade = forms.ChoiceField(GRADES, required=True, label='Klasse')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance', None)
        if instance:
            self.fields['grade'].choices += ((instance.grade, instance.grade), ('none', 'Ukendt'))
