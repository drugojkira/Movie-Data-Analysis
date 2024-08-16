import os
import zipfile
import pandas as pd
import matplotlib.pyplot as plt
import requests
import ast
from collections import Counter

url = "https://storage.yandexcloud.net/academy.ai/the_movies_dataset.zip"
response = requests.get(url)
zip_path = "the_movies_dataset.zip"

with open(zip_path, 'wb') as f:
    f.write(response.content)

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall("the_movies_dataset")

print(os.listdir("the_movies_dataset"))

movies_metadata = pd.read_csv('the_movies_dataset/movies_metadata.csv', low_memory=False)
credits = pd.read_csv('the_movies_dataset/credits.csv', low_memory=False)

movies_metadata['id'] = movies_metadata['id'].astype(str)
credits['id'] = credits['id'].astype(str)

movies_metadata['budget'] = pd.to_numeric(movies_metadata['budget'], errors='coerce')
movies_metadata['revenue'] = pd.to_numeric(movies_metadata['revenue'], errors='coerce')

movies_credits = pd.merge(movies_metadata, credits, left_on='id', right_on='id')

# Проверка гипотезы о выпуске фильмов по пятницам
movies_metadata['release_date'] = pd.to_datetime(movies_metadata['release_date'], errors='coerce')
movies_metadata['release_day'] = movies_metadata['release_date'].dt.dayofweek

release_day_counts = movies_metadata['release_day'].value_counts().sort_index()

days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
release_day_counts.index = days_of_week

plt.figure(figsize=(10, 6))
plt.bar(release_day_counts.index, release_day_counts.values, color='skyblue')
plt.title('Количество фильмов, выпущенных в каждый день недели')
plt.xlabel('День недели')
plt.ylabel('Количество фильмов')
plt.show()

# Проверка гипотез о кассовых и дорогих фильмах с участием известных актеров
movies_credits['cast'] = movies_credits['cast'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

actor_counter = Counter()

for cast in movies_credits['cast']:
    actor_counter.update([actor['name'] for actor in cast])

top_actors = [actor for actor, count in actor_counter.most_common(20)]

movies_credits['top_actors'] = movies_credits['cast'].apply(lambda x: [actor['name'] for actor in x if actor['name'] in top_actors])

top_revenue_movies = movies_credits[movies_credits['revenue'] > 0].sort_values('revenue', ascending=False).head(100)
top_revenue_actors = Counter([actor for actors in top_revenue_movies['top_actors'] for actor in actors])

top_budget_movies = movies_credits[movies_credits['budget'] > 0].sort_values('budget', ascending=False).head(100)
top_budget_actors = Counter([actor for actors in top_budget_movies['top_actors'] for actor in actors])

plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
plt.barh(*zip(*top_revenue_actors.most_common(10)), color='lightcoral')
plt.title('Топ-10 актёров в самых кассовых фильмах')
plt.xlabel('Количество фильмов')
plt.ylabel('Актёры')

plt.subplot(1, 2, 2)
plt.barh(*zip(*top_budget_actors.most_common(10)), color='lightgreen')
plt.title('Топ-10 актёров в самых дорогих фильмах')
plt.xlabel('Количество фильмов')
plt.ylabel('Актёры')

plt.tight_layout()
plt.show()

# Оценка знакомых актеров
known_actors = set(top_revenue_actors.keys()).union(set(top_budget_actors.keys()))
print("Сколько актеров из вашего результата вам знакомы?")
print(known_actors)
