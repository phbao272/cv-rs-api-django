from django.http import HttpResponse
import pandas as pd
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.models import UserInteractionJobs
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
