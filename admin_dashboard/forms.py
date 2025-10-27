from django import forms
from .models import JenisHama

class JenisHamaForm(forms.ModelForm):
    class Meta:
        model = JenisHama
        fields = ['nama', 'nama_latin', 'deskripsi', 'gejala', 'cara_pencegahan', 'cara_penanganan', 'gambar']
        widgets = {
            'deskripsi': forms.Textarea(attrs={'rows': 3}),
            'gejala': forms.Textarea(attrs={'rows': 3}),
            'cara_pencegahan': forms.Textarea(attrs={'rows': 3}),
            'cara_penanganan': forms.Textarea(attrs={'rows': 3}),
        }
