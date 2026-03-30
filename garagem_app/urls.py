from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('login/',    views.view_login,    name='login'),
    path('logout/',   views.view_logout,   name='logout'),
    path('registro/', views.view_register,  name='register'),
    
    # Aquisições
    path('aquisicoes/',                            views.view_aquisicoes,         name='aquisicoes'),
    path('aquisicoes/nova/',                       views.view_aquisicao_criar,    name='aquisicao_criar'),
    path('aquisicoes/<int:aquisicao_id>/editar/',   views.view_aquisicao_editar,   name='aquisicao_editar'),
    path('aquisicoes/<int:aquisicao_id>/excluir/', views.view_aquisicao_excluir, name='aquisicao_excluir'),
    
    # Clientes
    path('clientes/',                        views.view_clientes,         name='clientes'),
    path('cliente/<int:cliente_id>/',       views.view_cliente_detalhe,  name='cliente_detalhe'),
]
