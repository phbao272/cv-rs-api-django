from django.http import HttpResponse
import pandas as pd
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.models import Jobs, Companies
import matplotlib.pyplot as plt
from rest_framework.response import Response


@api_view(['GET'])
def getAllCompany(request):
    data = getDataCompany()

    df = pd.DataFrame(data)
    df.to_excel('companies.xlsx', index=False)

    return Response(data)


def getDataCompany():
    companies = Companies.objects.all()

    data = []

    for company in companies:
        job = Jobs.objects.filter(company=company.id).values()

        print(job)

        d = {
            "id": company.id,
            "name": company.name,
            "description": company.description,
            "count_job": len(job),
            "jobs": list(job),
        }

        data.append(d)

    return data


def getCompanyChart(request):
    data = getDataCompany()

    df = pd.DataFrame(data)

    ax = df.plot(kind='bar', x='name', y='count_job')

    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x()
                    * 1.005, p.get_height() * 1.005))

    plt.tight_layout()
    plt.title('Biểu đồ cột thống kê số lượng việc làm của công ty')
    plt.xlabel('Tên công ty', fontsize=12)
    plt.ylabel('Số lượng', fontsize=12)

    response = HttpResponse(content_type='image/png')
    plt.savefig(response, format='png')
    plt.close()

    return response


def getDataJob():
    jobs = Jobs.objects.all()

    data = []

    for job in jobs:
        jobSkills = job.jobskills_set.all().values(
            'm_skill__id', 'm_skill__name'),

        skills = convertSkillToText(jobSkills[0])

        d = {
            "id": job.id,
            "name": job.name,
            # "title": job.title,
            # "email": job.email,
            # "birthday": job.birthday,
            # "phone_number": job.phone_number,

            "location_name": job.m_location.name,
            "education_level_name": job.m_education_level.name,
            "experience_name": job.m_experience.name,
            "working_form_name": job.m_working_form.name,

            "skills": skills,
        }

        data.append(d)

    return data


def convertSkillToText(skills):

    text = ""

    for skill in skills:
        if text != "":
            text += ", "

        text += skill['m_skill__name']

    return text
