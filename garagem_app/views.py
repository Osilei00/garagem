from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Sum
from .models import Perfil, Aquisição
from .forms import RegistroForm, PerfilForm, AquisiçãoForm


def staff_required(view_func):
    """Exige que o usuário seja staff (admin) para acessar a view."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff:
            return HttpResponseForbidden('Acesso negado.')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── Autenticação ─────────────────────────────────────────────────────────────

def view_login(request):
    """Página de login."""
    if request.user.is_authenticated:
        return redirect('aquisicoes')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('aquisicoes')
        messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'garagem_app/login.html')


def view_logout(request):
    """Faz logout e redireciona para login."""
    logout(request)
    return redirect('login')


def view_register(request):
    """Página de registro de novos usuários."""
    if request.user.is_authenticated:
        return redirect('aquisicoes')

    form = RegistroForm()
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.first_name}!')
            return redirect('aquisicoes')

    return render(request, 'garagem_app/register.html', {'form': form})


# ─── Admin ─────────────────────────────────────────────────────────────────────

@staff_required
def view_aquisicoes(request):
    """Lista todas as aquisições."""
    cliente_id = request.GET.get('cliente')
    busca = request.GET.get('busca', '')
    
    clientes = User.objects.filter(is_staff=False).order_by('first_name', 'username')
    
    qs = Aquisição.objects.select_related('cliente')
    
    if cliente_id:
        qs = qs.filter(cliente_id=cliente_id)
    
    if busca:
        qs = qs.filter(miniaturista__icontains=busca)
    
    aquisicoes = qs.order_by('-data_aquisicao', '-criado_em')
    
    total_valor = aquisicoes.aggregate(total=Sum('preco'))['total'] or 0
    
    return render(request, 'garagem_app/aquisicoes_list.html', {
        'aquisicoes': aquisicoes,
        'clientes': clientes,
        'cliente_selecionado': cliente_id,
        'busca': busca,
        'total_valor': total_valor,
    })


@staff_required
def view_aquisicao_criar(request):
    """Cria uma nova aquisição."""
    form = AquisiçãoForm()
    if request.method == 'POST':
        form = AquisiçãoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aquisição registrada com sucesso!')
            return redirect('aquisicoes')

    return render(request, 'garagem_app/aquisicao_form.html', {
        'form': form,
        'titulo': 'Nova Aquisição'
    })


@staff_required
def view_aquisicao_editar(request, aquisicao_id):
    """Edita uma aquisição existente."""
    aquisicao = get_object_or_404(Aquisição, id=aquisicao_id)
    form = AquisiçãoForm(instance=aquisicao)
    if request.method == 'POST':
        form = AquisiçãoForm(request.POST, instance=aquisicao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aquisição atualizada!')
            return redirect('aquisicoes')

    return render(request, 'garagem_app/aquisicao_form.html', {
        'form': form,
        'aquisicao': aquisicao,
        'titulo': 'Editar Aquisição'
    })


@staff_required
def view_aquisicao_excluir(request, aquisicao_id):
    """Exclui uma aquisição."""
    aquisicao = get_object_or_404(Aquisição, id=aquisicao_id)
    miniaturista = aquisicao.miniaturista
    aquisicao.delete()
    messages.success(request, f'Aquisição "{miniaturista}" excluída!')
    return redirect('aquisicoes')


@staff_required
def view_clientes(request):
    """Lista todos os clientes (usuários não-staff)."""
    clientes = User.objects.filter(is_staff=False).order_by('first_name', 'username')
    return render(request, 'garagem_app/clientes_list.html', {'clientes': clientes})


@staff_required
def view_cliente_detalhe(request, cliente_id):
    """Mostra detalhes de um cliente específico."""
    cliente = get_object_or_404(User, id=cliente_id, is_staff=False)
    aquisicoes = Aquisição.objects.filter(cliente=cliente).order_by('-data_aquisicao')
    total = aquisicoes.aggregate(total=Sum('preco'))['total'] or 0
    return render(request, 'garagem_app/cliente_detalhe.html', {
        'cliente': cliente,
        'aquisicoes': aquisicoes,
        'total': total,
    })
