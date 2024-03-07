# -*- coding: utf-8 -*-
"""Final IIC.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YGUOeO1AEAcatoXSAfzc-za5no8J_Z8x

#IMPORTAÇÃO DE DEPENDÊNCIAS
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors
import numpy as np
from sklearn.metrics import accuracy_score
import sklearn.metrics.pairwise as pw
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
!pip install fuzzywuzzy
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

"""##Filmes"""

url = 'https://drive.google.com/file/d/11soEDwLvKtI6dR3-3OkUWyXnHqU-_0bP/view?usp=sharing'
url='https://drive.google.com/uc?id=' + url.split('/')[-2]
df_filme = pd.read_csv(url,sep=',')

"""##Notas"""

url = 'https://drive.google.com/file/d/1nrzhbmeK5OTEoqiCQ5lsayk8_q3FLnQc/view?usp=sharing'
url='https://drive.google.com/uc?id=' + url.split('/')[-2]
df_nota = pd.read_csv(url,sep=',')

"""##Dados"""

url = 'https://drive.google.com/file/d/1TayoFh9h-1Ghtk0Tm_LQWjqPyLlyJGzQ/view?usp=sharing'
url='https://drive.google.com/uc?id=' + url.split('/')[-2]
df_dados = pd.read_csv(url,sep=',')

"""##Tags"""

url = 'https://drive.google.com/file/d/1utKL4qufR0OmACaAeNubINH5n-Vkb4U2/view?usp=sharing'
url='https://drive.google.com/uc?id=' + url.split('/')[-2]
df_tag = pd.read_csv(url,sep=',')

#filmes = pd.read_csv("/content/drive/MyDrive/IIC/IIC Final/Dados.csv", sep="\t")
#nota = pd.read_csv("/content/drive/MyDrive/IIC/IIC Final/star.csv", sep="\t")

df_filme.head()

df_nota.head()

df_dados.head()

df_tag.head()

print("Colunas em df_nota:", df_nota.columns)

df_filme.shape

df_nota.shape

"""#LIMPEZA DE DADOS"""

duplicados = df_filme[df_filme.duplicated(keep='first')]
print(duplicados)

df_filme_set = set(df_filme['movieId'])
df_nota_set = set(df_nota['movieId'])

df_nota.drop_duplicates(subset ='movieId', keep='first', inplace=True)

"""#COMBINANDO DATAFRAMES"""

df_juntar = df_filme.merge(df_nota, on='movieId')
df_juntar.head()

filmes = pd.pivot_table(df_juntar, index='title', columns='userId', values='rating').fillna(0)
filmes.head()

"""#REMOÇÃO DE VALORES NULOS"""

rec = pw.cosine_similarity(filmes)
rec

rec_df = pd.DataFrame(rec, columns=filmes.index, index=filmes.index)
rec_df.head()

"""#Resultado obtido utilizando o Colaborative Filtering"""

cossine_df = pd.DataFrame(rec_df['Finding Nemo'].sort_values(ascending=False))
cossine_df.columns = ['Recomendações']
cossine_df.head(20)

df_dados.head()

df_tag.head()

"""#transformando movieId em inteiro"""

df_filme['movieId'] = df_filme['movieId'].apply(lambda x: str(x))

df_dados.shape

df_tag.shape

df2 = df_filme.merge(df_dados, left_on='title', right_on='Name', how='left')
df2 = df2.merge(df_tag, left_on='movieId', right_on='movieId', how='left')
df2['Infos'] = df2['genres'] + str(df2['Directors_Cast']) + str(df2['Discription']) + df2['tag']
df2.head()

vetor = TfidfVectorizer()
Tfidf = vetor.fit_transform(df2['Infos'].apply(lambda x: np.str_(x)))

similaridade = cosine_similarity(Tfidf)
similaridade

similaridade_df = pd.DataFrame(similaridade, columns=df2['title'], index=df2['title'])
similaridade_df.head ()

"""#Resultado obtido utilizando o Content-Based-Filtering"""

resultado_df = pd.DataFrame(similaridade_df['Finding Nemo'].sort_values(ascending=False))
resultado_df.columns = ['Recomendações']
resultado_df.head(30)

"""#KNN"""

df_dados.head()

df_tag.head()

filme_df2 = df_filme.merge(df_dados, left_on='title', right_on='Name', how='left')
filme_df2 = filme_df2.merge(df_tag, left_on='movieId', right_on='movieId', how='left')
filme_df2['Infos'] = filme_df2['genres'] + str(filme_df2['Directors_Cast']) + str(filme_df2['Discription']) + filme_df2['tag']
filme_df2.head()

filme_df2['Infos'].fillna('', inplace=True)

vectorizer = CountVectorizer()
info_matrix = vectorizer.fit_transform(filme_df2['Infos'])

knnsim = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=30)
knnsim.fit(info_matrix)

def get_recommendations(title, knn_model, vectorizer, dataframe, matrix):
    # Encontrar o índice do filme no DataFrame
    idx = dataframe.index[dataframe['Finding Nemo'] == title].tolist()[0]

    # Obter os vizinhos mais próximos
    distances, indices = knn_model.kneighbors(matrix[idx])

    # Exibir os filmes recomendados
    print(f"Recomendações para '{title}':")
    for i, index in enumerate(indices.flatten()):
        if i == 0:
            continue  # O próprio filme está na lista de recomendações, ignorando-o
        print(f"{i}: {dataframe['Finding Nemo'][index]}, Distância: {distances.flatten()[i]:.4f}")

from tabulate import tabulate

def recommender(movie_title, knn_model, vectorizer, dataframe, matrix, num_recommendations=30):

    idx = dataframe.index[dataframe['title'] == movie_title].tolist()[0]


    distances, indices = knn_model.kneighbors(matrix[idx])


    recommended_movies = []
    for i, index in enumerate(indices.flatten()):
        if i == 0:
            continue
        recommended_movies.append((dataframe['title'][index], distances.flatten()[i]))


    recommended_movies = sorted(recommended_movies, key=lambda x: x[1])

    # Criar uma lista de listas para a tabela
    table_data = [[i+1, title, f"{distance:.4f}"] for i, (title, distance) in enumerate(recommended_movies[:num_recommendations])]

    # Cabeçalho da tabela
    headers = ["Rank", "Movie Title", "Distance"]

    # Retorna a tabela formatada
    return tabulate(table_data, headers=headers, tablefmt="grid")


movie_title = 'Finding Nemo'
table_result = recommender(movie_title, knnsim, vectorizer, filme_df2, info_matrix)


print(table_result)