import numpy as np
import pandas as pd
from rest_framework.response import Response
from rest_framework.decorators import api_view
from sklearn.neighbors import NearestNeighbors
from api.models import UserInteractionJobs
from scipy.sparse import csr_matrix


@api_view(['GET'])
def getByCF(request):

    data = getInteraction()

    norm_matrix = normalized_utility_matrix(data)

    cf_score = cf(norm_matrix, 1)

    return Response(cf_score)


def cf(norm_matrix, user_id, k=2):
    sparse_df = csr_matrix(norm_matrix.values)
    print(sparse_df)

    knn_model = NearestNeighbors(metric='cosine', algorithm='brute')
    knn_model.fit(sparse_df)

    similar_users, distances = get_similar_users(
        knn_model, norm_matrix, user_id, n=k)

    print(similar_users)
    print(distances)

    return similar_users


def get_similar_users(knn_model, matrix_df, user_id, n=5):
    # input to this function is the user and number of top similar users you want.

    knn_input = np.asarray([matrix_df.values[user_id-1]])  # .reshape(1,-1)

    distances, indices = knn_model.kneighbors(knn_input, n_neighbors=n+1)

    print("Top", n, "users who are very much similar to the User-", user_id, "are: ")
    print(" ")
    for i in range(1, len(distances[0])):
        print(i, ". User:", indices[0][i]+1,
              "separated by distance of", distances[0][i])
    return indices.flatten()[1:] + 1, distances.flatten()[1:]


def utility_matrix(data):
    df = pd.DataFrame(data)
    df = df.pivot_table(index='user_id', columns='job_id', values='rating')
    df = df.fillna(0)

    return df


def normalized_utility_matrix(data):
    # get users from data
    users = list(set([d['user_id'] for d in data]))
    mu = np.zeros(len(users), dtype=float)

    u_matrix = utility_matrix(data)
    norm_matrix = u_matrix.copy()

    for i, user in enumerate(users):
        mu[i] = np.mean(u_matrix.loc[user][u_matrix.loc[user] > 0])

        # Trừ giá trị trung bình từ các giá trị khác trong hàng tương ứng nhưng bỏ qua các giá trị bằng 0

        norm_matrix.loc[user] = u_matrix.loc[user] - \
            mu[i] * (u_matrix.loc[user] > 0)

    # print("users\n", users)

    # print("u_matrix\n", u_matrix)

    print("norm_matrix\n", norm_matrix)

    return norm_matrix


def getInteraction():
    interaction = UserInteractionJobs.objects.all()

    return list(interaction.values())
