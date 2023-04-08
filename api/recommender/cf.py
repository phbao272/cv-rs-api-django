import ast

import numpy as np
import pandas as pd
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

from api.models import CFUserJobs, UserInteractionJobs, UserSimilarities


@api_view(['GET'])
def getUserSimilarityById(request):
    try:
        user_id = request.query_params['user_id']

        user_similarity = UserSimilarities.objects.filter(
            user=user_id).first()

        d = {
            'user_id': user_similarity.user.id,
            'user_similarity': user_similarity.user_similarity
        }

        data_dict = ast.literal_eval(user_similarity.user_similarity)

        return Response(d)
    except Exception as e:
        return Response(e)


@api_view(['GET'])
def getByCF(request):

    user_id = request.query_params['user_id']

    res = cf(user_id)

    return Response(res)


def cf(user_id: int):
    user_jobs = CFUserJobs.objects.filter(user=user_id).first()

    job_recommends = ast.literal_eval(user_jobs.job_recommends)

    return job_recommends


def createDataSimilarity():
    with transaction.atomic():
        data = getInteraction()

        norm_matrix = normalized_utility_matrix(data)

        sim_matrix = calcSimilarityMatrix(norm_matrix)

        user_ids = norm_matrix.index

        result = {}

        for i in user_ids:
            knn = getKNN(sim_matrix, i, k=10)

            result[i] = getJobRecommender(knn, norm_matrix, 20)

            updateOrCreateUserSimilarities(i, str(knn))
            updateOrCreateCFUserJobs(i, str(result[i]))


def getJobRecommender(knn: dict, norm_matrix: pd.DataFrame, n: int = 5):
    similar_user_list = list(knn.keys())
    sum_weighted = np.sum(list(knn.values()))

    job_list = norm_matrix.columns

    # print("job_list", job_list)

    # print("similar_user_list", similar_user_list)

    weighted = {}

    for key, value in knn.items():
        weighted[key] = value/sum_weighted

    # print("weighted", weighted)

    weighted_list = list(weighted.values())

    # print("weighted_list", weighted_list)

    # rating_similarities_user = norm_matrix.values[similar_user_list]
    rating_similarities_user = norm_matrix.loc[similar_user_list]

    # print("rating_similarities_user", rating_similarities_user,
    #       rating_similarities_user.shape)

    weighted_list = np.array(weighted_list)[
        :, np.newaxis] + np.zeros(len(job_list))

    # print("weighted_list\n", weighted_list, weighted_list.shape)

    new_rating_matrix = weighted_list*rating_similarities_user
    mean_rating_list = new_rating_matrix.sum(axis=0)

    print("mean_rating_list\n", mean_rating_list, mean_rating_list.shape)

    n = min(len(mean_rating_list), n)
    job_recommender = np.argsort(mean_rating_list)[::-1][:n]
    # job_recommender = mean_rating_list.argsort()[-n:][::-1]
    # job_recommender = mean_rating_list.argsort()[::-1][-n:]

    # print("job_recommender\n", job_recommender)

    job_recommender_ids = norm_matrix.columns[job_recommender.tolist()]

    print(
        "res", job_recommender_ids)
    job_recommender_dict = {}
    for job_id, similarity_score in zip(job_recommender_ids, mean_rating_list[job_recommender_ids.values.tolist()]):
        job_recommender_dict[job_id] = similarity_score

    return job_recommender_dict


def updateOrCreateUserSimilarities(user_id, user_similarity):
    obj, created = UserSimilarities.objects.update_or_create(
        user_id=user_id,
        defaults={
            'user_similarity': user_similarity
        }
    )

    # print("obj", obj, "created", created)


def updateOrCreateCFUserJobs(user_id, job_recommends):
    obj, created = CFUserJobs.objects.update_or_create(
        user_id=user_id,
        defaults={
            'job_recommends': job_recommends
        }
    )


def calcSimilarityMatrix(norm_matrix: pd.DataFrame):
    # print(norm_matrix)
    sparse_df = csr_matrix(norm_matrix.values)

    norm_matrix_index = norm_matrix.index

    similarity_matrix = cosine_similarity_matrix(
        sparse_df)

    print(similarity_matrix.shape)

    similarity_matrix_df = pd.DataFrame(
        similarity_matrix, index=norm_matrix_index, columns=norm_matrix_index)

    return similarity_matrix_df


def getKNN(similarity_matrix: pd.DataFrame, user_id, k=5):
    # print("similarity_matrix\n", similarity_matrix)

    # Tìm các hàng trong ma trận tương đồng có giá trị lớn nhất
    row_idx = similarity_matrix.loc[int(user_id)]

    # print("row_idx", row_idx)

    similar_rows = row_idx.nlargest(k+1)[1:]

    similar_dict = similar_rows.to_dict()

    return similar_dict


def cosine_similarity_matrix(matrix):

    # Create matrix with zeros row x row
    similarity_matrix = np.zeros((matrix.shape[0], matrix.shape[0]))

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[0]):
            if i != j:
                # Calculate cosine similarity between row i and row j
                # matrix[i].reshape(1, -1) được sử dụng để biến đổi ma trận 1 chiều matrix[i]
                # thành ma trận 2 chiều với 1 hàng và số cột bằng với số lượng phần tử của matrix[i].
                similarity_matrix[i][j] = cosine_similarity(matrix[i].reshape(
                    1, -1), matrix[j].reshape(1, -1))
            else:
                similarity_matrix[i][j] = 1
    return similarity_matrix


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

    # print("norm_matrix\n", norm_matrix)

    return norm_matrix


def utility_matrix(data):
    df = pd.DataFrame(data)
    df = df.pivot_table(index='user_id', columns='job_id', values='rating')
    df = df.fillna(0)

    return df


def getInteraction():
    interaction = UserInteractionJobs.objects.all()

    return list(interaction.values())
