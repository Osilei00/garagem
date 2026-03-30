from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Perfil, Miniatura, Aquisicao


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        label='Nome',
        widget=forms.TextInput(attrs={'placeholder': 'Seu nome'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        label='Sobrenome',
        widget=forms.TextInput(attrs={'placeholder': 'Seu sobrenome'})
    )
    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget=forms.EmailInput(attrs={'placeholder': 'seu@email.com'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Nome de usuário'
        self.fields['password1'].widget.attrs['placeholder'] = 'Senha'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirmar senha'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['telefone', 'foto_perfil', 'bio']
        widgets = {
            'telefone': forms.TextInput(attrs={'placeholder': '(11) 99999-9999'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Conte um pouco sobre você...'}),
        }


class MiniaturaForm(forms.ModelForm):
    modelo = forms.ChoiceField(
        choices=[],
        required=True,
        label='Modelo',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Miniatura
        fields = ['modelo', 'preco', 'foto']
        widgets = {
            'preco': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        modelos = Miniatura.objects.values_list('modelo', flat=True).distinct().order_by('modelo')
        self.fields['modelo'].choices = [('', '— Selecione o modelo —')] + [(m, m) for m in modelos if m]


class AquisicaoForm(forms.ModelForm):
    miniatura = forms.ChoiceField(
        choices=[],
        required=True,
        label='Miniatura',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Aquisicao
        fields = ['cliente', 'miniatura', 'observacao']
        widgets = {
            'observacao': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Observações sobre a aquisição...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = User.objects.filter(is_staff=False).order_by('first_name', 'username')
        miniaturas = Miniatura.objects.filter(disponivel=True).order_by('modelo')
        self.fields['miniatura'].choices = [('', '— Selecione a miniatura —')] + [(m.id, f"{m.modelo}") for m in miniaturas]

    def clean_miniatura(self):
        miniatura_id = self.cleaned_data['miniatura']
        return get_object_or_404(Miniatura, id=miniatura_id)


class ComprovanteForm(forms.ModelForm):
    class Meta:
        model = Aquisicao
        fields = ['comprovante_pagamento', 'observacao']
        widgets = {
            'observacao': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Informações sobre o pagamento (banco, horário, etc.)...'
            }),
        }
        labels = {
            'comprovante_pagamento': 'Comprovante de Pagamento (imagem)',
            'observacao': 'Observação (opcional)',
        }
