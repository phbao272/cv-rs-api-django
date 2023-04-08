
import random
import numpy as np
import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .cbf import cbf
from .cf import cf


from api.models import Jobs


@api_view(['GET'])
def getRecommend(request):
    user_id = request.query_params['user_id']

    cbf_recommend = cbf(user_id)
    cf_recommend = cf(user_id)

    page_rank_recommend = calcPageRank(cbf_recommend, cf_recommend)

    page_rank_recommend_sort = sorted(
        page_rank_recommend.items(), key=lambda x: x[1], reverse=True)

    page_rank_recommend_ids = [job_id for job_id,
                               rank in page_rank_recommend_sort][:16]

    job_ids = Jobs.objects.values_list('id', flat=True)

    random_recommend_ids = randomRecommends(job_ids, page_rank_recommend_ids)

    # print("random_recommend_ids", random_recommend_ids)

    recommend_ids = page_rank_recommend_ids + random_recommend_ids

    # print("recommend_ids", recommend_ids)

    job_recommends = Jobs.objects.filter(id__in=recommend_ids)

    res = []

    for job in job_recommends:
        res.append({
            "id": job.id,
            "title": job.title,
            "description": job.description,


            "company": {"id": job.company.id,
                        "name": job.company.name,
                        "photo": job.company.photo},

            "m_location_id": job.m_location.id,
            "location": {"id": job.m_location.id,
                         "name": job.m_location.name},

            "m_education_level_id": job.m_education_level.id,
            "m_education_level_name": job.m_education_level.name,

            "m_experience_id": job.m_experience.id,
            "m_experience_name": job.m_experience.name,

            "m_working_form_id": job.m_working_form.id,

            "m_salary_id": job.m_salary.id,
            "salary": {"id": job.m_salary.id,
                       "name": job.m_salary.name},

            "job_skills": job.jobskills_set.all().values('m_skill__id', 'm_skill__name'),

            "page_rank_score": page_rank_recommend[job.id] if job.id in page_rank_recommend else -9999
        })

    res_sorted = sorted(
        res, key=lambda k: k['page_rank_score'], reverse=True)

    return Response(res_sorted)


def randomRecommends(ids, recommend_ids, n=4):
    ids = list(ids)
    recommend_ids = list(recommend_ids)

    random_recommend_ids = []

    while len(random_recommend_ids) < n:
        random_id = random.choice(ids)

        if random_id not in recommend_ids:
            random_recommend_ids.append(random_id)

    return random_recommend_ids


def calcPageRank(cbf_recommend_list: list, cf_recommend):
    cbf_recommend = {}

    for job in cbf_recommend_list:
        cbf_recommend[job['id']] = job['similarity']

    cbf_recommend_ids = list(cbf_recommend.keys())
    cf_recommend_ids = list(cf_recommend.keys())

    recommend_ids = set(cbf_recommend_ids + cf_recommend_ids)

    # print("cbf_recommend", cbf_recommend)
    # print("cf_recommend", cf_recommend)

    # print("cbf_recommend_ids", cbf_recommend_ids)
    # print("cf_recommend_ids", cf_recommend_ids)
    # print("recommend_ids", recommend_ids)

    d = 0.85

    PR_CBF = 1 - d
    PR_CF = 1 - d

    sum_weight_cbf = 0
    sum_weight_cf = 0

    PR = {}

    sum_weight_cbf = sum(cbf_recommend.values())
    sum_weight_cf = sum(cf_recommend.values())

    # print("sum_weight_cbf", sum_weight_cbf)
    # print("sum_weight_cf", sum_weight_cf)

    case_1 = []
    case_2 = []
    case_3 = []

    for job_id in recommend_ids:
        if job_id in cbf_recommend_ids and job_id in cf_recommend_ids:
            case_1.append(job_id)
            PR[job_id] = (1 - d) + d * (PR_CBF*cbf_recommend[job_id] /
                                        sum_weight_cbf + PR_CF*cf_recommend[job_id]/sum_weight_cf)
        elif job_id in cbf_recommend_ids:
            case_2.append(job_id)

            PR[job_id] = (1 - d) + d * (PR_CBF*cbf_recommend[job_id] /
                                        sum_weight_cbf)
        elif job_id in cf_recommend_ids:
            case_3.append(job_id)

            PR[job_id] = (1 - d) + d * \
                (PR_CF*cf_recommend[job_id]/sum_weight_cf)

    # print("case_1", case_1)
    # print("case_2", case_2)
    # print("case_3", case_3)

    return PR
