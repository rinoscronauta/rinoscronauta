import requests
import os
import datetime
import re

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = 'rinoscronauta'

# configurações da API
headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
query = """
query($username: String!) {
  user(login: $username) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

# funções
def fetch_contributions():
    # Busca os dados de contribuição diária via GitHub GraphQL API.
    url = "https://api.github.com/graphql"
    response = requests.post(url, json={"query": query, "variables": {"username": USERNAME}}, headers=headers)

    # Verifica se a resposta foi bem-sucedida
    if response.status_code != 200:
        print(f"Erro na solicitação: {response.status_code}")
        print("Resposta:", response.json())  # Exibe a resposta da API para ajudar no debug
        return []

    data = response.json()

    # Verifica se a chave 'data' está presente
    if 'data' not in data:
        print("Erro: 'data' não encontrado na resposta da API.")
        print("Resposta:", data)  # Exibe a resposta da API para ajudar no debug
        return []

    days = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    contributions = []
    
    for week in days:
        for day in week['contributionDays']:
            date = datetime.datetime.strptime(day['date'], "%Y-%m-%d").date()
            count = day['contributionCount']
            contributions.append((date, count))
    return contributions


def calculate_tolerant_streak(contributions, tolerance=1):
    """Calcula o streak de contribuições permitindo uma tolerância de dias sem contribuição."""
    streak = 0
    max_streaks = []
    skipped_days = 0
    total_contribuicoes = sum(count for _, count in contributions)
    data_inicio_contribuicoes = contributions[0][0]  # Primeira data na lista

    # Variáveis para rastrear as datas do streak atual e do streak máximo
    inicio_streak_atual = None
    fim_streak_atual = None
    inicio_streak_maximo = None
    fim_streak_maximo = None
    max_streak_length = 0
    current_streak_start = None

    for i, (current_date, current_count) in enumerate(contributions):
        if current_count > 0:
            # Início do streak
            if streak == 0:
                current_streak_start = current_date
            streak += 1
            skipped_days = 0
        elif skipped_days < tolerance:
            skipped_days += 1
        else:
            # Finaliza o streak atual e verifica se é o máximo
            max_streaks.append((streak, current_streak_start, contributions[i - 1][0]))  # Guarda o streak e as datas
            if streak > max_streak_length:
                max_streak_length = streak
                inicio_streak_maximo = current_streak_start
                fim_streak_maximo = contributions[i - 1][0]
            streak = 0
            skipped_days = 0

    # Adiciona o último streak (pode ser o máximo) à lista
    max_streaks.append((streak, current_streak_start, contributions[-1][0]))

    # Verifica se o último streak foi o máximo
    if streak > max_streak_length:
        inicio_streak_maximo = current_streak_start
        fim_streak_maximo = contributions[-1][0]

    # Define os valores para o streak atual
    if streak > 0:
        inicio_streak_atual = current_streak_start
        fim_streak_atual = contributions[-1][0]

    # Retorna as variáveis desejadas
    return {
        "streak_atual": streak,
        "total_contribuicoes": total_contribuicoes,
        "data_inicio_contribuicoes": data_inicio_contribuicoes,
        "data_inicio_streak_atual": inicio_streak_atual,
        "data_fim_streak_atual": fim_streak_atual,
        "data_inicio_streak_maximo": inicio_streak_maximo,
        "data_fim_streak_maximo": fim_streak_maximo,
        "streak_maximo": max(item[0] for item in max_streaks)
    }

# Executa a função
contributions = fetch_contributions()
streak = calculate_tolerant_streak(contributions, tolerance=2)
print(streak)

# Carregar README.md e substituir os placeholders
with open("README.md", "r") as file:
    readme_content = file.read()

# Substituir valores
readme_content = readme_content.replace("{{ streak['total_contribuicoes'] }}", str(total_contribuicoes))
readme_content = readme_content.replace("{{ streak['streak_atual'] }}", str(streak_atual))
readme_content = readme_content.replace("{{ streak['streak_maximo'] }}", str(streak_maximo))
readme_content = readme_content.replace("{{ streak['data_inicio_contribuicoes'] }}", data_inicio_contribuicoes)
readme_content = readme_content.replace("{{ streak['data_inicio_streak_atual'] }}", data_inicio_streak_atual)
readme_content = readme_content.replace("{{ streak['data_fim_streak_atual'] }}", data_fim_streak_atual)
readme_content = readme_content.replace("{{ streak['data_inicio_streak_maximo'] }}", data_inicio_streak_maximo)
readme_content = readme_content.replace("{{ streak['data_fim_streak_maximo'] }}", data_fim_streak_maximo)

# Salvar o README.md atualizado
with open("README.md", "w") as file:
    file.write(readme_content)
