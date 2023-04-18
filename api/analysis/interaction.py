from django.http import HttpResponse
import pandas as pd
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.models import Resumes, UserInteractionJobs, Users
import matplotlib.pyplot as plt
from rest_framework.response import Response


def getDataInteraction():
    interactions = UserInteractionJobs.objects.all()

    data = []

    for interaction in interactions:

        d = {
            "id": interaction.id,
            "rating": interaction.rating,
            "user_id": interaction.user.id,
            "job_id": interaction.job.id,
        }

        data.append(d)

    return data


@api_view(['GET'])
def getInteractionChart(request):
    data = getDataInteraction()

    # print(data)

    df = pd.DataFrame(data)

    job_counts = df.groupby('job_id')['id'].count()

    ax = job_counts.plot(kind="line", figsize=(
        12, 8), title='Rating Frequency of All Jobs', fontsize=12)
    ax.set_xlabel('Job ID')
    ax.set_ylabel('Count')
    plt.show()

    response = HttpResponse(content_type='image/png')
    plt.savefig(response, format='png')
    plt.close()

    return response


@api_view(['GET'])
def getUserInteractionChart(request):
    users = Users.objects.filter(role=1)

    dataUser = []

    for user in users:

        d = {
            "id": user.id,
            "name": user.name,
        }

        dataUser.append(d)

    interactions = getDataInteraction()

    count = {}

    for user in dataUser:
        count[user["id"]] = 0

    for interaction in interactions:
        print("interaction", interaction["user_id"])

        count[interaction["user_id"]] += 1

    return Response(count.values())


@api_view(['GET'])
def checkInfo(request):
    users = Users.objects.filter(role=1)

    has_resume = 0
    no_resume = 0

    has_interactions = 0
    no_interactions = 0

    case_1 = []
    case_2 = []
    case_3 = []
    case_4 = []

    for user in users:
        resume = Resumes.objects.filter(user=user.id)
        interactions = UserInteractionJobs.objects.filter(user=user.id)

        count_resume = resume.count()
        count_interactions = interactions.count()

        if count_interactions >= 5:
            if count_resume == 0:
                case_3.append(user.id)
            else:
                case_4.append(user.id)
        else:
            if count_resume == 0:
                case_1.append(user.id)

            else:
                case_2.append(user.id)

    return Response({"has_resume": has_resume, "no_resume": no_resume, "has_interactions": has_interactions, "no_interactions": no_interactions,
                     "case_1": case_1, "case_2": case_2, "case_3": case_3, "case_4": case_4})


def checkCase(user_id):
    resume = Resumes.objects.filter(user=user_id)
    interactions = UserInteractionJobs.objects.filter(user=user_id)

    count_resume = resume.count()
    count_interactions = interactions.count()

    if count_interactions >= 5:
        if count_resume == 0:
            return "case-3"
        else:
            return "case-4"
    else:
        if count_resume == 0:
            return "case-1"
        else:
            return "case-2"
