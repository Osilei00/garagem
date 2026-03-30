from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/',    views.view_login,    name='login'),
    path('logout/',   views.view_logout,   name='logout'),
    path('registro/', views.view_register, name='register'),

    # Cliente
    path('kanban/',                              views.view_kanban,       name='kanban'),
    path('comprovante/<int:aquisicao_id>/',      views.view_comprovante,  name='comprovante'),

    # Admin – Visão geral
    path('painel/',              views.view_admin_dashboard, name='admin_dashboard'),
    path('painel/kanban/',       views.view_admin_kanban,    name='admin_kanban'),
    path('painel/clientes/',     views.view_clientes,        name='clientes'),

    # Admin – Aquisições
    path('painel/aquisicao/nova/',                        views.view_aquisicao_criar,   name='aquisicao_criar'),
    path('painel/aquisicao/<int:aquisicao_id>/avancar/',  views.view_aquisicao_avancar, name='aquisicao_avancar'),
    path('painel/aquisicao/<int:aquisicao_id>/voltar/',   views.view_aquisicao_voltar,  name='aquisicao_voltar'),

    # Admin – Miniaturas
    path('painel/miniaturas/',                          views.view_miniaturas,      name='miniaturas'),
    path('painel/miniaturas/nova/',                     views.view_miniatura_criar,  name='miniatura_criar'),
    path('painel/miniaturas/<int:miniatura_id>/editar/', views.view_miniatura_editar, name='miniatura_editar'),
]
