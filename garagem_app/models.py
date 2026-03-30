from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    """
    Perfil estendido para cada usuário.
    Criado automaticamente quando um novo usuário é registrado.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuário'
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefone'
    )
    foto_perfil = models.ImageField(
        upload_to='perfis/',
        blank=True,
        null=True,
        verbose_name='Foto de Perfil'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Sobre'
    )

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'Perfil de {self.user.get_full_name() or self.user.username}'


class Aquisição(models.Model):
    """
    Registro de aquisição de uma miniatura por um cliente.
    """
    cliente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='aquisicoes',
        verbose_name='Cliente'
    )
    miniaturista = models.CharField(
        max_length=200,
        verbose_name='Nome da Miniatura'
    )
    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Preço (R$)'
    )
    data_aquisicao = models.DateField(
        verbose_name='Data da Aquisição'
    )
    observação = models.TextField(
        blank=True,
        verbose_name='Observação'
    )
    foto = models.ImageField(
        upload_to='aquisicoes/',
        blank=True,
        null=True,
        verbose_name='Foto da Miniatura'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    class Meta:
        verbose_name = 'Aquisição'
        verbose_name_plural = 'Aquisições'
        ordering = ['-data_aquisicao']

    def __str__(self):
        return f'{self.cliente.get_full_name() or self.cliente.username} - {self.miniaturista}'


@receiver(post_save, sender=User)
def criar_perfil(sender, instance, created, **kwargs):
    """Cria um Perfil automaticamente quando um novo User é criado."""
    if created:
        Perfil.objects.create(user=instance)


@receiver(post_save, sender=User)
def salvar_perfil(sender, instance, **kwargs):
    """Salva o Perfil automaticamente quando o User é salvo."""
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
