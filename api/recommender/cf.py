import numpy as np
import pandas as pd
from rest_framework.response import Response
from rest_framework.decorators import api_view
from sklearn.neighbors import NearestNeighbors
from api.models import UserInteractionJobs
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity


@api_view(['GET'])
def getByCF(request):
    user_id = request.query_params['user_id']

    print("user_id", user_id)

    data = getInteraction()

    norm_matrix = normalized_utility_matrix(data)

    cf_score = cf(norm_matrix)

    knn = getKNN(cf_score, user_id, k=5)

    return Response(knn)


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


def cf(norm_matrix: pd.DataFrame):
    print(norm_matrix)
    sparse_df = csr_matrix(norm_matrix.values)

    norm_matrix_index = norm_matrix.index

    similarity_matrix = cosine_similarity_matrix(
        sparse_df)

    similarity_matrix_df = pd.DataFrame(
        similarity_matrix, index=norm_matrix_index, columns=norm_matrix_index)

    return similarity_matrix_df


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


def getKNN(similarity_matrix: pd.DataFrame, user_id, k=5):
    print("similarity_matrix\n", similarity_matrix)

    # Tìm các hàng trong ma trận tương đồng có giá trị lớn nhất
    row_idx = similarity_matrix.loc[int(user_id)]

    print("row_idx", row_idx)

    similar_rows = row_idx.nlargest(k+1)[1:]

    similar_dict = similar_rows.to_dict()

    return similar_dict

    # norm_matrix_1 = np.array([[2.4, 0, 0, 0, 0, -0.143333, 0.000000],
    #                           [2, 0, 0, -2, 0, 0, 0],
    #                           [0.00, 2.25, -0.75, 0, 0, -0.75, -0.75],
    #                           [-1.17, -1.17, -0.17, 0.83,
    #                            0.83, 0.000000, 0.83],
    #                           [-0.75, -2.75, 1.25, 0, 0, 0.000000, 2.25],
    #                           ])

    # # Tạo DataFrame từ ma trận norm_matrix_1 với thông tin user_id và job_id
    # user_ids = [1, 2, 3, 4, 5]
    # job_ids = [11, 12, 13, 14, 15, 16, 17]

    # df_norm = pd.DataFrame(norm_matrix_1, index=user_ids, columns=job_ids)

    # # Chuyển đổi ma trận thành DataFrame pivot_table với user_id là index và job_id là column
    # df_pivot = df_norm.reset_index().melt(id_vars=["index"], var_name="job_id")
    # df_pivot.columns = ["user_id", "job_id", "rating"]
    # df_pivot = df_pivot.pivot_table(
    #     index="user_id", columns="job_id", values="rating")

    # cf_score = cf(df_pivot, user_id)
