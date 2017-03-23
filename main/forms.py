from dal_select2.widgets import ModelSelect2
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UsernameField
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import _password_validators_help_text_html as password_help
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.core.validators import MinLengthValidator
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

from .models import GRADES, Profile, LanProfile, PAYTYPES, TournamentTeam, get_next_lan, Tournament, NamedProfile


class UserRegForm(forms.ModelForm):
    """Registration form part 1"""

    class Meta:
        model = User
        fields = ('first_name', 'email', 'username')

    first_name = forms.CharField(label='Fulde navn', max_length=100)
    email = forms.EmailField(label='Email')
    username = UsernameField(max_length=100, label='Brugernavn')
    password = forms.CharField(label='Kodeord', widget=forms.TextInput(attrs={'type': 'password'}),
                               help_text=password_help())

    def clean_password(self):
        password_validation.validate_password(self.cleaned_data.get('password'), self.instance)
        return self.cleaned_data.get('password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LabelSelect(forms.Select):
    """Like a Select but starts on a disabled value (so it has like a placeholder)"""

    def __init__(self, *args, label=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label

    def render_options(self, *args, **kwargs):
        output = ''
        if self.label:
            output += format_html('<option value="" selected="" disabled="">{}</option>', self.label)
        return output + super().render_options(*args, **kwargs)


class ProfileRegForm(forms.ModelForm):
    """Registration form part 2"""

    class Meta:
        model = Profile
        fields = ('grade',)

    grade = forms.ChoiceField(sorted(GRADES, reverse=True), label='Klasse', widget=LabelSelect(label='Klasse'))
    captcha = ReCaptchaField(widget=ReCaptchaWidget(size='100%'), label='Bot sikring')


class TilmeldForm(forms.ModelForm):
    """Tilmeldings form"""

    class Meta:
        model = LanProfile
        fields = ('seat', 'paytype')

    def __init__(self, *args, **kwargs):
        ok_seats = [('', '')]
        lan = kwargs.pop('lan')
        for row in kwargs.pop('seats'):
            for seat in row:
                if seat[0] is not None and seat[1] is None:
                    ok_seats.append((seat[0], seat[0]))

        profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)
        self.fields['seat'] = forms.ChoiceField(choices=ok_seats, widget=forms.HiddenInput, required=False,
                                                error_messages={'invalid_choice': 'Der opstod en fejl, prøv igen.'})
        if lan.paytypes and profile:
            try:
                LanProfile.objects.get(profile=profile, lan=lan)
                del self.fields['paytype']
            except LanProfile.DoesNotExist:
                self.fields['paytype'] = forms.ChoiceField(label='Vælg ønsket betalingsmetode',
                                                           widget=forms.RadioSelect,
                                                           choices=((k, v) for k, v in dict(PAYTYPES).items() if
                                                                    k in lan.paytypes), )
        else:
            del self.fields['paytype']

    def save(self, commit=True, profile=None, lan=None):
        # Is the user already tilmeldt?
        try:
            lanprofile = LanProfile.objects.get(profile=profile, lan=lan)
            # If so, move them (that is, their seat)
            lanprofile.seat = self.cleaned_data['seat']
            lanprofile.save(update_fields=['seat'])
            return False
        except LanProfile.DoesNotExist:
            lanprofile = super().save(commit=False)
            lanprofile.profile = profile
            lanprofile.lan = lan
            lanprofile.save()
            return True


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'email')

    first_name = forms.CharField(label='Fulde navn', max_length=100)
    email = forms.EmailField(label='Email')


# Not proud of this, but it works :/
class PhotoInput(forms.ClearableFileInput):
    clear_checkbox_label = 'Fjern'
    template_with_initial = (
        '<img src="%(initial_url)s" alt="%(initial_text)s (%(initial)s)"/>'
        '<br><div class="file"><label for="id_photo" class="choose" title="Upload nyt profilbillede">'
        'Upload nyt profilbillede</label>%(clear_template)s<br>%(input)s</div>'
    )

    template_with_clear = ('<div class="check">%(clear)s <label for="%(clear_checkbox_id)s">'
                           '%(clear_checkbox_label)s</label></div>')

    template = ('<br><div class="file big"><label for="id_photo" class="choose" title="Upload profilbillede">'
                'Upload profilbillede</label>%(input)s</div>')

    def render(self, name, value, attrs=None):
        if self.is_initial(value):
            return super().render(name, value, attrs)
        else:
            substitutions = {'input': super().render(name, value, attrs)}
            return mark_safe(self.template % substitutions)


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('grade', 'bio', 'photo')

    bio = forms.CharField(
        max_length=1024,
        widget=forms.Textarea,
        required=False
    )

    photo = forms.ImageField(widget=PhotoInput, required=False, label="Profilbillede")
    photo.widget.attrs = {'accept': 'image/*'}

    grade = forms.ChoiceField(sorted(GRADES, reverse=True), label='Klasse', widget=LabelSelect(label='Klasse'))


class TournamentSelect2(ModelSelect2):
    autocomplete_function = 'tournamentSelect2'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Media.js += ('main/script/tournamentSelect2.js',)

    def filter_choices_to_render(self, selected_choices):
        """Filter out un-selected choices if choices is a QuerySet."""
        # Filter out named profiles
        pre_filter_choices = []
        for choice in pre_filter_choices:
            try:
                int(choice)
                pre_filter_choices.append(choice)
            except ValueError:
                pass
        self.choices.queryset = self.choices.queryset.filter(
            pk__in=[c for c in pre_filter_choices if c]
        )


class TournamentModelChoiceField(forms.ModelChoiceField):
    """ModelChoiceField with less validation"""

    def to_python(self, value):
        try:
            return super().to_python(value)
        except ValidationError as e:
            if isinstance(value, str):
                # What could possibly go wrong :/
                return value
            else:
                raise e


class TournamentTeamForm(forms.ModelForm):
    class Meta:
        model = TournamentTeam
        fields = ('name', 'profiles', 'namedprofiles', 'tournament')
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "Et hold med dette navn existerer allerede!",
            }
        }

    class Media:
        js = ('autocomplete_light/vendor/select2/dist/js/i18n/da.js',)

    def __init__(self, *args, **kwargs):
        self.tournament = kwargs.pop('tournament')
        self.profile = kwargs.pop('profile')
        super().__init__(*args, **kwargs)

        lan = get_next_lan()

        del self.fields['profiles']
        del self.fields['namedprofiles']

        self.fields['tournament'] = forms.ModelChoiceField(queryset=Tournament.objects.all(),
                                                           widget=forms.HiddenInput())
        self.initial['tournament'] = self.tournament

        self.fields['profile_0'] = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'readonly': True, }),
                                                   label='Medlem 1 (dig selv)')

        for i in range(1, self.tournament.team_size):
            forward = ['profile_{}'.format(j) for j in range(1, self.tournament.team_size) if j != i]
            self.fields['profile_{}'.format(i)] = TournamentModelChoiceField(
                queryset=Profile.objects.filter(lanprofile__lan=lan),
                widget=TournamentSelect2(
                    url='autocomplete-profile',
                    forward=forward,
                    attrs={'data-html': 'true', 'data-placeholder': 'Søg efter brugere som er tilmeldt LAN'},
                ),
                label='Medlem {}'.format(i + 1),
            )

        self.initial['profile_0'] = self.profile.user.first_name

        self.fields['name'].validators.append(MinLengthValidator(3))

    def clean(self):
        self.cleaned_data['profiles'] = []
        self.cleaned_data['namedprofiles'] = []
        for key, val in list(self.cleaned_data.items()):
            if key.startswith('profile_'):
                if key != 'profile_0':
                    if isinstance(val, str):
                        np = NamedProfile.objects.create(name=val)
                        self.cleaned_data['namedprofiles'].append(np)
                    else:
                        self.cleaned_data['profiles'].append(val)
                        try:
                            LanProfile.objects.get(profile=val, lan=get_next_lan())
                        except LanProfile.DoesNotExist:
                            raise ValidationError(
                                '%(profile)s er ikke tilmeldt LAN og kan derfor ikke være med på dit hold.',
                                params={'profile': val.user.first_name},
                                code='missingtilmelding'
                            )
                else:
                    self.cleaned_data['profiles'].append(self.profile)
                del self.cleaned_data[key]
        self.cleaned_data['tournament'] = self.tournament
        super().clean()
