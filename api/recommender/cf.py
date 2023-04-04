import numpy as np
import pandas as pd
from rest_framework.response import Response
from rest_framework.decorators import api_view
from sklearn.neighbors import NearestNeighbors
from api.models import UserInteractionJobs


@api_view(['GET'])
def getByCF(request):

    data = getInteraction()

    norm_matrix = normalized_utility_matrix(data)

    cf_score = cf(norm_matrix, 1)

    return Response(cf_score)


def cf(norm_matrix, user_id, k=1):
    model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
    model_knn.fit(norm_matrix)

    distances, indices = model_knn.kneighbors(
        norm_matrix.iloc[user_id-1, :].values.reshape(1, -1), n_neighbors=k+1)

    # print(distances)
    # print(indices)

    top_k_indices = indices.flatten()[1:]

    top_k_distances = distances.flatten()[1:]

    print(top_k_indices)
    print(top_k_distances)

    return "1"


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
    print(u_matrix)

    for i, user in enumerate(users):
        # print('xx',  u_matrix.loc[user])

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
