"""Forms for the main app"""
# pylint: disable=W0232, R0903
import os
import yaml

from django import forms
from django.conf import settings
from django.template.defaultfilters import slugify

from django_jcrop.forms import JCropImageWidget
from games import models


class NewsForm(forms.ModelForm):
    class Meta:
        model = models.News
        exclude = ('slug', )


class GameForm(forms.ModelForm):
    title_logo = forms.ImageField(
        widget=JCropImageWidget, required=False
    )

    class Meta:
        model = models.Game
        exclude = ('slug', )

    def rename_uploaded_file(self, file_field, cleaned_data, slug):
        if self.files.get(file_field):
            clean_field = cleaned_data.get(file_field)
            _, ext = os.path.splitext(clean_field.name)
            relpath = 'games/banners/%s%s' % (slug, ext)
            clean_field.name = relpath
            current_abspath = os.path.join(settings.MEDIA_ROOT, relpath)
            if os.path.exists(current_abspath):
                os.remove(current_abspath)
            return clean_field
        return None

    def clean(self):
        cleaned_data = super(GameForm, self).clean()
        slug = cleaned_data.get('slug', self.instance.slug)
        name = cleaned_data.get('name', self.instance.name)
        if not slug:
            slug = slugify(name)
        # Modify only if title_logo has been posted
        for file_field in ('title_logo', 'icon'):
            cleaned_data[file_field] = self.rename_uploaded_file(file_field,
                                                                 cleaned_data,
                                                                 slug)
        cleaned_data['slug'] = slug
        return cleaned_data


class ScreenshotForm(forms.ModelForm):

    class Meta:
        model = models.Screenshot
        exclude = ['game', 'uploaded_at', 'uploaded_by']

    def __init__(self, *args, **kwargs):
        self.game = models.Game.objects.get(pk=kwargs.pop('game_id'))
        super(ScreenshotForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance['game'] = self.game
        return super(ScreenshotForm, self).save(*args, **kwargs)


class InstallerForm(forms.ModelForm):
    """Form to create and modify installers"""

    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'code-editor',
                                     'spellcheck': 'false'})
    )

    class Meta:
        """Form configuration"""
        model = models.Installer
        exclude = ("user", "slug", "game")

    def clean_content(self):
        """Verify that the content field is valid yaml"""
        yaml_data = self.cleaned_data["content"]
        try:
            yaml_data = yaml.load(yaml_data)
        except yaml.scanner.ScannerError:
            raise forms.ValidationError("Invalid YAML data (scanner error)")
        except yaml.parser.ParserError:
            raise forms.ValidationError("Invalid YAML data (parse error)")
        return yaml.dump(yaml_data, default_flow_style=False)