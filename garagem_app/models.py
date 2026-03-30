from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    foto_perfil = models.ImageField(upload_to='perfis/', blank=True, null=True, verbose_name='Foto de Perfil')
    bio = models.TextField(blank=True, verbose_name='Sobre')

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'Perfil de {self.user.get_full_name() or self.user.username}'


@receiver(post_save, sender=User)
def criar_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)


@receiver(post_save, sender=User)
def salvar_perfil(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()


class Miniatura(models.Model):
    ESCALA_CHOICES = [
        ('1:18', '1:18'),
        ('1:24', '1:24'),
        ('1:32', '1:32'),
        ('1:43', '1:43'),
        ('1:64', '1:64'),
        ('outro', 'Outro'),
    ]

    marca = models.CharField(max_length=100, verbose_name='Marca do Carro', blank=True, default='')
    modelo = models.CharField(max_length=100, verbose_name='Modelo')
    ano = models.IntegerField(verbose_name='Ano do Carro', blank=True, null=True)
    escala = models.CharField(max_length=10, choices=ESCALA_CHOICES, default='1:64', verbose_name='Escala')
    fabricante = models.CharField(max_length=100, verbose_name='Fabricante', blank=True, default='', help_text='Ex: Bburago, Hot Wheels, Minichamps')
    foto = models.ImageField(upload_to='miniaturas/', blank=True, null=True, verbose_name='Foto')
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço (R$)')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    disponivel = models.BooleanField(default=True, verbose_name='Disponível')
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Miniatura'
        verbose_name_plural = 'Miniaturas'
        ordering = ['-data_cadastro']

    def __str__(self):
        return f'{self.marca} {self.modelo} ({self.escala}) – {self.fabricante}'


class Aquisicao(models.Model):
    STATUS_RESERVA = 'RESERVA'
    STATUS_RESERVA_PG = 'RESERVA_PG'
    STATUS_GARAGEM = 'GARAGEM'
    STATUS_COLECAO = 'COLECAO'

    STATUS_CHOICES = [
        (STATUS_RESERVA, '🔖 Reserva'),
        (STATUS_RESERVA_PG, '💳 Reserva PG'),
        (STATUS_GARAGEM, '🏠 Garagem'),
        (STATUS_COLECAO, '🏆 Coleção'),
    ]

    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='aquisicoes', verbose_name='Cliente')
    miniatura = models.ForeignKey(Miniatura, on_delete=models.PROTECT, related_name='aquisicoes', verbose_name='Miniatura')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_RESERVA, verbose_name='Status')
    observacao = models.TextField(blank=True, verbose_name='Observação')
    comprovante_pagamento = models.ImageField(
        upload_to='comprovantes/',
        blank=True,
        null=True,
        verbose_name='Comprovante de Pagamento'
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')

    class Meta:
        verbose_name = 'Aquisição'
        verbose_name_plural = 'Aquisições'
        ordering = ['-data_criacao']

    def __str__(self):
        return f'{self.cliente.username} – {self.miniatura} [{self.get_status_display()}]'

    def get_status_color(self):
        cores = {
            self.STATUS_RESERVA: 'amber',
            self.STATUS_RESERVA_PG: 'blue',
            self.STATUS_GARAGEM: 'purple',
            self.STATUS_COLECAO: 'green',
        }
        return cores.get(self.status, 'gray')

    def pode_enviar_comprovante(self):
        return self.status == self.STATUS_RESERVA

    def proximo_status(self):
        fluxo = [self.STATUS_RESERVA, self.STATUS_RESERVA_PG, self.STATUS_GARAGEM, self.STATUS_COLECAO]
        try:
            idx = fluxo.index(self.status)
            return fluxo[idx + 1] if idx + 1 < len(fluxo) else None
        except ValueError:
            return None
