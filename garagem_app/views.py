from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Count
from .models import Perfil, Miniatura, Aquisicao
from .forms import (
    RegistroForm, PerfilForm, MiniaturaForm,
    AquisicaoForm, ComprovanteForm
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def staff_required(view_func):
    """Decorator que exige is_staff=True."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff:
            return HttpResponseForbidden('Acesso negado.')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── Auth ─────────────────────────────────────────────────────────────────────

def view_login(request):
    if request.user.is_authenticated:
        return redirect('kanban' if not request.user.is_staff else 'admin_kanban')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('admin_kanban' if user.is_staff else 'kanban')
        messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'garagem_app/login.html')


def view_logout(request):
    logout(request)
    return redirect('login')


def view_register(request):
    if request.user.is_authenticated:
        return redirect('kanban')

    form = RegistroForm()
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.first_name}! Sua conta foi criada.')
            return redirect('kanban')

    return render(request, 'garagem_app/register.html', {'form': form})


# ─── Cliente ──────────────────────────────────────────────────────────────────

@login_required
def view_kanban(request):
    if request.user.is_staff:
        return redirect('admin_kanban')

    aquisicoes = Aquisicao.objects.filter(cliente=request.user).select_related('miniatura')
    colunas = {
        'RESERVA':    {'label': 'Reserva',    'icon': '🔖', 'cor': 'amber',  'items': []},
        'RESERVA_PG': {'label': 'Reserva PG', 'icon': '💳', 'cor': 'blue',   'items': []},
        'GARAGEM':    {'label': 'Garagem',    'icon': '🏠', 'cor': 'purple', 'items': []},
        'COLECAO':    {'label': 'Coleção',    'icon': '🏆', 'cor': 'green',  'items': []},
    }

    for aq in aquisicoes:
        if aq.status in colunas:
            colunas[aq.status]['items'].append(aq)

    return render(request, 'garagem_app/kanban.html', {'colunas': colunas})


@login_required
def view_comprovante(request, aquisicao_id):
    aquisicao = get_object_or_404(Aquisicao, id=aquisicao_id, cliente=request.user)

    if not aquisicao.pode_enviar_comprovante():
        messages.warning(request, 'Comprovante só pode ser enviado quando o status for Reserva.')
        return redirect('kanban')

    form = ComprovanteForm(instance=aquisicao)
    if request.method == 'POST':
        form = ComprovanteForm(request.POST, request.FILES, instance=aquisicao)
        if form.is_valid():
            aq = form.save(commit=False)
            aq.status = Aquisicao.STATUS_RESERVA_PG
            aq.save()
            messages.success(request, 'Comprovante enviado! Aguarde a validação do administrador.')
            return redirect('kanban')

    return render(request, 'garagem_app/comprovante_form.html', {
        'form': form,
        'aquisicao': aquisicao,
    })


# ─── Admin ────────────────────────────────────────────────────────────────────

@staff_required
def view_admin_dashboard(request):
    total_clientes = User.objects.filter(is_staff=False).count()
    total_miniaturas = Miniatura.objects.count()
    aquisicoes = Aquisicao.objects.all()

    stats_status = {
        'RESERVA':    aquisicoes.filter(status='RESERVA').count(),
        'RESERVA_PG': aquisicoes.filter(status='RESERVA_PG').count(),
        'GARAGEM':    aquisicoes.filter(status='GARAGEM').count(),
        'COLECAO':    aquisicoes.filter(status='COLECAO').count(),
    }
    ultimas_aquisicoes = aquisicoes.select_related('cliente', 'miniatura').order_by('-data_criacao')[:8]

    return render(request, 'garagem_app/admin_dashboard.html', {
        'total_clientes': total_clientes,
        'total_miniaturas': total_miniaturas,
        'stats_status': stats_status,
        'ultimas_aquisicoes': ultimas_aquisicoes,
    })


@staff_required
def view_admin_kanban(request):
    cliente_id = request.GET.get('cliente')
    clientes = User.objects.filter(is_staff=False).order_by('first_name', 'username')

    qs = Aquisicao.objects.select_related('cliente', 'miniatura').all()
    cliente_selecionado = None
    if cliente_id:
        qs = qs.filter(cliente_id=cliente_id)
        cliente_selecionado = get_object_or_404(User, id=cliente_id)

    colunas = {
        'RESERVA':    {'label': 'Reserva',    'icon': '🔖', 'cor': 'amber',  'items': []},
        'RESERVA_PG': {'label': 'Reserva PG', 'icon': '💳', 'cor': 'blue',   'items': []},
        'GARAGEM':    {'label': 'Garagem',    'icon': '🏠', 'cor': 'purple', 'items': []},
        'COLECAO':    {'label': 'Coleção',    'icon': '🏆', 'cor': 'green',  'items': []},
    }
    for aq in qs:
        if aq.status in colunas:
            colunas[aq.status]['items'].append(aq)

    return render(request, 'garagem_app/admin_kanban.html', {
        'colunas': colunas,
        'clientes': clientes,
        'cliente_selecionado': cliente_selecionado,
    })


@staff_required
def view_aquisicao_criar(request):
    form = AquisicaoForm()
    if request.method == 'POST':
        form = AquisicaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aquisição criada com sucesso!')
            return redirect('admin_kanban')

    return render(request, 'garagem_app/aquisicao_form.html', {'form': form, 'titulo': 'Nova Aquisição'})


@staff_required
def view_aquisicao_avancar(request, aquisicao_id):
    aquisicao = get_object_or_404(Aquisicao, id=aquisicao_id)
    proximo = aquisicao.proximo_status()
    if proximo:
        aquisicao.status = proximo
        aquisicao.save()
        messages.success(request, f'Status atualizado para: {aquisicao.get_status_display()}')
    else:
        messages.info(request, 'Essa aquisição já está na fase final.')
    return redirect(request.META.get('HTTP_REFERER', 'admin_kanban'))


@staff_required
def view_aquisicao_voltar(request, aquisicao_id):
    """Retrocede o status (para correções)."""
    aquisicao = get_object_or_404(Aquisicao, id=aquisicao_id)
    fluxo = [Aquisicao.STATUS_RESERVA, Aquisicao.STATUS_RESERVA_PG,
             Aquisicao.STATUS_GARAGEM, Aquisicao.STATUS_COLECAO]
    try:
        idx = fluxo.index(aquisicao.status)
        if idx > 0:
            aquisicao.status = fluxo[idx - 1]
            aquisicao.save()
            messages.success(request, f'Status revertido para: {aquisicao.get_status_display()}')
    except ValueError:
        pass
    return redirect(request.META.get('HTTP_REFERER', 'admin_kanban'))


@staff_required
def view_clientes(request):
    clientes = User.objects.filter(is_staff=False).annotate(
        total_aquisicoes=Count('aquisicoes')
    ).order_by('first_name', 'username')

    return render(request, 'garagem_app/clientes_list.html', {'clientes': clientes})


@staff_required
def view_miniaturas(request):
    busca = request.GET.get('busca', '')
    miniaturas = Miniatura.objects.annotate(total_aquisicoes=Count('aquisicoes'))
    if busca:
        miniaturas = miniaturas.filter(modelo__icontains=busca)
    miniaturas = miniaturas.order_by('-data_cadastro')
    return render(request, 'garagem_app/miniaturas_list.html', {'miniaturas': miniaturas, 'busca': busca})


@staff_required
def view_miniatura_criar(request):
    form = MiniaturaForm()
    if request.method == 'POST':
        form = MiniaturaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Miniatura cadastrada com sucesso!')
            return redirect('miniaturas')
    return render(request, 'garagem_app/miniatura_form.html', {'form': form, 'titulo': 'Nova Miniatura'})


@staff_required
def view_miniatura_editar(request, miniatura_id):
    miniatura = get_object_or_404(Miniatura, id=miniatura_id)
    form = MiniaturaForm(instance=miniatura)
    if request.method == 'POST':
        form = MiniaturaForm(request.POST, request.FILES, instance=miniatura)
        if form.is_valid():
            form.save()
            messages.success(request, 'Miniatura atualizada!')
            return redirect('miniaturas')
    return render(request, 'garagem_app/miniatura_form.html', {
        'form': form,
        'miniatura': miniatura,
        'titulo': 'Editar Miniatura',
    })
