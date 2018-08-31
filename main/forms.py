from dal_select2.widgets import ModelSelect2
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UsernameField
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import _password_validators_help_text_html as password_help
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

from main.utils import send_mobilepay_request
from .models import (GRADES, Profile, LanProfile, PAYTYPES, TournamentTeam, Tournament, NamedProfile,
                     FoodOrder, Lan)

PHONE_REGEX = r'^(\(?\+?(?:00)?[- ]?45\)?)?[- ]?((?:\d[ -]?){8})$'


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

    grade = forms.ChoiceField(choices=sorted(GRADES, reverse=True), label='Klasse', widget=LabelSelect(label='Klasse'))
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
            if isinstance(row, str):
                continue
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


class PhotoInput(forms.ClearableFileInput):
    clear_checkbox_label = 'Fjern'
    initial_text = 'Aktuelt'
    input_text = 'Upload nyt profilbillede'
    template_name = 'profile_photo_input.html'


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('grade', 'bio', 'phone', 'photo')

    bio = forms.CharField(
        max_length=1024,
        widget=forms.Textarea,
        required=False
    )

    photo = forms.ImageField(widget=PhotoInput, required=False, label="Profilbillede")
    photo.widget.attrs = {'accept': 'image/*'}

    grade = forms.ChoiceField(choices=sorted(GRADES, reverse=True), label='Klasse', widget=LabelSelect(label='Klasse'))

    phone_regex = RegexValidator(PHONE_REGEX, message='Intast et gyldigt telefonnummer f.eks. 12345678')
    phone = forms.CharField(validators=[phone_regex],
                            widget=forms.TextInput(attrs={'type': 'tel',
                                                          'patern': PHONE_REGEX,
                                                          'placeholder': '(+45) 1234 5678'}),
                            label='MobilePay telefonnummer',
                            required=False)

    def __init__(self, *args, **kwargs):
        groups = kwargs.pop('groups')
        request = kwargs.pop('request')

        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance', None)
        if instance:
            self.fields['grade'].choices += ((instance.grade, instance.grade), ('none', 'Ukendt'))

        if groups and groups.filter(name=settings.RESTRICTED_USER_GROUP).exists():
            del self.fields['photo']
            if request:
                messages.warning(request, 'Du har ikke tilladelse til at ændre profilbillede. Hvis du mener '
                                          'dette er en fejl, kontakt et medlem af LanCrew.')

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        phone.replace(' ', '')
        phone.replace('-', '')
        return phone[-8:]


class TournamentSelect2(ModelSelect2):
    autocomplete_function = 'tournamentSelect2'

    class Media:
        extend = False
        js = ['autocomplete_light/jquery.init.js',
              'main/script/tournamentSelect2.js',
              'autocomplete_light/autocomplete.init.js',
              'autocomplete_light/vendor/select2/dist/js/select2.full.js',
              'autocomplete_light/select2.js', ]

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

    def render(self, name, value, attrs=None, renderer=None):
        return super().render(name, value, attrs=attrs)


class TournamentModelChoiceField(forms.ModelChoiceField):
    """ModelChoiceField with less validation"""

    def __init__(self, *args, allow_external=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.allow_external = allow_external

    def to_python(self, value):
        try:
            return super().to_python(value)
        except ValidationError as e:
            if isinstance(value, str) and self.allow_external:
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

        lan = Lan.get_next()

        del self.fields['profiles']
        del self.fields['namedprofiles']

        self.fields['tournament'] = forms.ModelChoiceField(queryset=Tournament.objects.all(),
                                                           widget=forms.HiddenInput())
        self.initial['tournament'] = self.tournament

        self.fields['profile_0'] = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'readonly': True, }),
                                                   label='Medlem 1 (dig selv)')

        for i in range(1, self.tournament.team_size):
            forward = ['profile_{}'.format(j) for j in range(1, self.tournament.team_size) if j != i]
            attrs = {'data-html': 'true', 'data-placeholder': 'Søg efter brugere som er tilmeldt LAN'}
            if self.tournament.allow_external:
                attrs['data-allow-external'] = 'true'
            print(forward)
            widget = TournamentSelect2(
                url='autocomplete-profile',
                forward=forward,
                attrs=attrs,
            )
            self.fields['profile_{}'.format(i)] = TournamentModelChoiceField(
                queryset=Profile.objects.filter(lanprofile__lan=lan),
                widget=widget,
                label='Medlem {}'.format(i + 1),
                allow_external=self.tournament.allow_external
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
                            LanProfile.objects.get(profile=val, lan=Lan.get_next())
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


class FoodOrderForm(forms.ModelForm):
    class Meta:
        model = FoodOrder
        fields = ('time', 'lanprofile', 'order', 'price')

    FIELDS = (('category', 'kategori'),
              ('product', 'produkt'),
              ('part1', 'del'),
              ('part2', 'del'),
              ('part3', 'del'),
              ('acc1', 'tilbehør'),
              ('acc2', 'tilbehør'),
              ('acc3', 'tilbehør'),
              ('acc4', 'tilbehør'))

    phone_regex = RegexValidator(PHONE_REGEX, message='Intast et gyldigt telefonnummer f.eks. 12345678')
    phone = forms.CharField(validators=[phone_regex],
                            widget=forms.TextInput(attrs={'type': 'tel',
                                                          'patern': PHONE_REGEX,
                                                          'placeholder': '(+45) 1234 5678'}),
                            label='MobilePay telefonnummer',
                            required=False)

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile', None)
        self.lp = kwargs.pop('lanprofile', None)

        super().__init__(*args, **kwargs)

        del self.fields['time']
        del self.fields['lanprofile']
        del self.fields['order']
        self.fields['price'].widget = forms.HiddenInput(attrs={'value': 0})
        if self.profile:
            self.fields['phone'].initial = self.profile.phone

        for i, field in enumerate(self.FIELDS):
            widget = forms.Select(attrs={'data-placeholder': 'Vælg ' + field[1]},
                                  choices=[(None, '')])
            self.fields[field[0]] = forms.CharField(widget=widget,
                                                    label='' if i != 0 else 'Ordre',
                                                    required=False)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        phone.replace(' ', '')
        phone.replace('-', '')
        return phone[-8:]

    def clean(self):
        super().clean()
        self.cleaned_data['time'] = timezone.now()
        self.cleaned_data['lanprofile'] = self.lp
        self.cleaned_data['order'] = ' - '.join([self.cleaned_data[x[0]]
                                                 for x in self.FIELDS if self.cleaned_data[x[0]]])
        for x in self.FIELDS:
            del self.cleaned_data[x[0]]

    def save(self, **kwargs):
        if self.cleaned_data['phone'] and self.cleaned_data['phone'] != self.profile.phone:
            self.profile.phone = self.cleaned_data['phone']
            self.profile.save()
        order = super().save(**kwargs)

        if self.cleaned_data['phone']:
            send_mobilepay_request(lan=self.lp.lan,
                                   profile=self.lp.profile,
                                   type='LAN mad',
                                   amount=order.price,
                                   id=order.id)

    def __str__(self):
        return mark_safe(self._html_output(
            normal_row='%(label)s%(field)s%(help_text)s',
            error_row='%s',
            row_ender='',
            help_text_html='<span class="helptext">%s</span>',
            errors_on_separate_row=True).replace('\n', ''))
