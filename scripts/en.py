import json
import re

# Caminho do arquivo JSON de entrada
caminho_json = r"C:\Users\osile\OneDrive\Documentos\#Osilei\Programação\Meus Projetos\garagem\scripts\hotwheels_test_2025.json"

# Caminho do arquivo TXT de saída
caminho_saida = r"C:\Users\osile\OneDrive\Documentos\#Osilei\Programação\Meus Projetos\garagem\scripts\nomes_formatados.txt"

# Palavras proibidas que devem ser removidas
PALAVRAS_REMOVER = [
    "short",
    "card",
    "international",
    "blister",
    "long",
    "blistercard"
]

with open(caminho_json, "r", encoding="utf-8") as arquivo:
    dados = json.load(arquivo)

nomes_formatados = []

for item in dados:
    nome = item.get("name", "")
    partes = nome.split("_")

    # Filtrar partes que NÃO são códigos (códigos são tudo maiúsculo ou só números)
    partes_validas = [
        p for p in partes
        if not p.isupper() and not p.isdigit()
    ]

    # Juntar as partes válidas
    nome_limpo = " ".join(partes_validas)

    # Remover palavras proibidas (case-insensitive)
    nome_limpo = nome_limpo.lower()
    for palavra in PALAVRAS_REMOVER:
        nome_limpo = nome_limpo.replace(palavra, "")

    # Remover espaços duplos criados após limpeza
    nome_limpo = re.sub(r"\s+", " ", nome_limpo).strip()

    # Capitalizar corretamente (primeira letra de cada palavra)
    nome_limpo = nome_limpo.title()

    nomes_formatados.append(nome_limpo)

# Remover duplicados mantendo a ordem original
nomes_unicos = list(dict.fromkeys(nomes_formatados))

# Salvar no arquivo TXT
with open(caminho_saida, "w", encoding="utf-8") as saida:
    for nome in nomes_unicos:
        saida.write(nome + "\n")

print("Arquivo gerado com sucesso!")