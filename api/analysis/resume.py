from django.http import HttpResponse
import pandas as pd
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.models import Resumes, Jobs, Companies
import matplotlib.pyplot as plt
from rest_framework.response import Response


def getDataResume():
    resumes = Resumes.objects.all()

    data = []

    for resume in resumes:
        resumeSkills = resume.resumeskills_set.all().values(
            'm_skill__id', 'm_skill__name'),

        skills = convertSkillToText(resumeSkills[0])

        d = {
            "id": resume.id,
            "name": resume.name,
            # "title": resume.title,
            # "email": resume.email,
            # "birthday": resume.birthday,
            # "phone_number": resume.phone_number,

            "location_name": resume.m_location.name,
            "education_level_name": resume.m_education_level.name,
            "experience_name": resume.m_experience.name,
            "working_form_name": resume.m_working_form.name,
            "job_name": resume.m_job.name,

            "skills": skills,
        }

        data.append(d)

    return data


@api_view(['GET'])
def getAllResume(request):
    data = getDataResume()

    df = pd.DataFrame(data)
    df.to_excel('resumes.xlsx', index=False)

    return Response(data)


def getResumeChart(request):
    data = getDataResume()

    df = pd.DataFrame(data)

    rating_count_df = pd.DataFrame(df.groupby(
        ['experience_name']).size(), columns=['count'])

    print(rating_count_df)

    ax = rating_count_df.reset_index().rename(columns={'index': 'experience name count'}).plot('experience_name', 'count', 'bar',
                                                                                               figsize=(
                                                                                                   12, 8),
                                                                                               fontsize=10)

    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x()
                                          * 1.005, p.get_height() * 1.005))

    plt.title('Biểu đồ cột thống kê số lượng ứng viên theo kinh nghiệm')
    plt.xlabel('Kinh nghiệm', fontsize=12)
    plt.ylabel('Số lượng', fontsize=12)

    response = HttpResponse(content_type='image/png')
    plt.savefig(response, format='png')
    plt.close()

    return response


def convertSkillToText(skills):

    text = ""

    for skill in skills:
        if text != "":
            text += ", "

        text += skill['m_skill__name']

    return text


@api_view(['GET'])
def pieChart(request):
    labels = ['Label 1', 'Label 2', 'Label 3', 'Label 4']
    sizes = [15, 30, 45, 10]

    plt.pie(sizes, labels=labels)
    plt.axis('equal')

    plt.title('Biểu đồ cột thống kê số lượng ứng viên theo kinh nghiệm')
    plt.xlabel('Kinh nghiệm', fontsize=12)
    plt.ylabel('Số lượng', fontsize=12)

    response = HttpResponse(content_type='image/png')
    plt.savefig(response, format='png')
    plt.close()

    return response
