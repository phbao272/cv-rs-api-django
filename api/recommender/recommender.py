
import math
import random

import numpy as np
import pandas as pd
from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import HopeJobs, Jobs, Resumes, UserInteractionJobs

from .cbf import cbf
from .cf import cf


@api_view(['GET'])
def getRecommend(request):
    user_id = request.query_params['user_id']

    case = checkCase(user_id)

    # print("CASEEEEE", case)

    # print("case 2")
    # result_2 = case2(user_id)
    # for job in result_2:
    #     print(job["title"],
    #           " - similarity:", job["similarity"])

    # print("case 3")

    # result_3 = case3(user_id)
    # for job in result_3:
    #     print(job["title"],
    #           " - mean rating:", job["mean_rating"])

    # print("case 4")

    # result_4 = case4(user_id)
    # for job in result_4:
    #     print(job["title"],
    #           " - page rank score:", job["page_rank_score"])

    match case:
        case "case-1":  # case-1: user chưa đủ tương tác và chưa có CV ==> Hot Job
            # print("case-1")
            result = recommendHotJob()

            for job in result:
                print(job["title"],
                      " - Interaction Score:", job["interaction_score"])
        case "case-2":  # case-2: user chưa đủ tương tác và có CV ==> 20% random + 80% CBF
            # print("case-2")
            result = case2(user_id)

            for job in result:
                print(job["title"],
                      " - Similarity:", job["similarity"])
        case "case-3":  # case-3: user đủ tương tác và chưa có CV ===> 20% random + 80% CF
            # print("case-3")

            result = case3(user_id)
            for job in result:
                print(job["title"],
                      " - Mean Rating:", job["mean_rating"])

        case "case-4":  # case-4: user đủ tương tác và có CV ===> 20% random + 80% PageRank
            # print("case-4")

            result = case4(user_id)

            for job in result:
                print(job["title"],
                      " - Page Rank Score:", job["page_rank_score"])
        case _:
            print("default")

    return Response(result)


@api_view(['GET'])
def getHopeJob(request):

    ndcg_res = []

    user_id_random = random.sample(range(1, 146), 145)
    # print("user_id_random:", user_id_random)

    # for type in ["cbf"]:
    for k in range(1, 9):
        print("k: ", k)

        for type in ["cbf", "cf", "hybrid"]:
            print("type:", type)
            res = []

            for user_id in user_id_random:
                # for user_id in range(1, 146):

                # print("user_id:", user_id)
                result = getJobIds(user_id, type)

                hope_jobs = HopeJobs.objects.get(
                    user=user_id).hope_jobs.split(',')

                hope_jobs = [int(job_id) for job_id in hope_jobs]

                job_ids = [job['id'] for job in result][:k]

                res.append({
                    "user_id": user_id,
                    "job_ids": ",".join([str(elem) for elem in job_ids]),
                    "ndcg": ndcg(hope_jobs, job_ids, k)
                })

            average_ndcg = sum([r['ndcg'] for r in res]) / len(res)

            ndcg_res.append({
                "type": type,
                "average_ndcg": average_ndcg,
                "res": res
            })

            print("average_ndcg:", k, " ,", average_ndcg)

    return Response(ndcg_res)


def getJobIds(user_id, type):
    cbf_recommend = []
    cf_recommend = []

    if (type == "cf"):
        cbf_recommend = []
        cf_recommend = cf(user_id)
    elif (type == "cbf"):
        cbf_recommend = cbf(user_id)
        cf_recommend = []
    elif (type == "hybrid"):
        cbf_recommend = cbf(user_id)
        cf_recommend = cf(user_id)

    page_rank_recommend = calcPageRank(cbf_recommend, cf_recommend)

    page_rank_recommend_sort = sorted(
        page_rank_recommend.items(), key=lambda x: x[1], reverse=True)

    page_rank_recommend_ids = [job_id for job_id,
                               rank in page_rank_recommend_sort][:16]

    job_ids = Jobs.objects.values_list('id', flat=True)

    random_recommend_ids = randomRecommends(job_ids, page_rank_recommend_ids)

    # recommend_ids = page_rank_recommend_ids + random_recommend_ids
    recommend_ids = page_rank_recommend_ids

    job_recommends = Jobs.objects.filter(id__in=recommend_ids)

    res = []

    for job in job_recommends:
        d = {
            "id": job.id,
            "title": job.title,
        }

        d["page_rank_score"] = - \
            999 if job.id in random_recommend_ids else page_rank_recommend[job.id]
        res.append(d)

    res_sorted = sorted(
        res, key=lambda k: k['page_rank_score'], reverse=True)

    return res_sorted


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

    cbf_recommend_ids = list(cbf_recommend.keys()) if len(
        cbf_recommend) != 0 else []

    cf_recommend_ids = list(cf_recommend.keys()) if len(
        cf_recommend) != 0 else []

    recommend_ids = set(cbf_recommend_ids + cf_recommend_ids)

    # print("cbf_recommend", cbf_recommend)
    # print("cf_recommend", cf_recommend)

    # print("cbf_recommend_ids", cbf_recommend_ids)
    # print("cf_recommend_ids", cf_recommend_ids)
    # print("recommend_ids", recommend_ids)

    d = 0.85

    PR_CBF = 1 - d
    PR_CF = 1 - d

    sum_weight_cbf = 0.000000000000001
    sum_weight_cf = 0.000000000000001

    PR = {}

    if (len(cbf_recommend) != 0):
        sum_weight_cbf = sum(cbf_recommend.values()) if sum(
            cbf_recommend.values()) != 0 else 0.000000000000001

    if (len(cf_recommend) != 0):
        sum_weight_cf = sum(cf_recommend.values()) if sum(
            cf_recommend.values()) != 0 else 0.000000000000001

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


def recommendHotJob():
    # Lấy danh sách các job_id trong truy vấn interactions
    interactions = UserInteractionJobs.objects.all().values(
        'job_id').annotate(total_rating=Sum('rating')).order_by('-total_rating')[:20]
    job_sort_ids = [interaction['job_id'] for interaction in interactions]

    # Lọc các đối tượng UserInteractionJobs bằng job_id__in
    filtered_interactions = UserInteractionJobs.objects.filter(
        job_id__in=job_sort_ids).values('job_id').annotate(
        total_rating=Sum('rating')).order_by('-total_rating')

    # Lấy danh sách các job_id đã lọc được
    sorted_job_ids = [interaction['job_id']
                      for interaction in filtered_interactions]

    # Lấy danh sách các đối tượng Jobs đã lọc được
    job_recommends = Jobs.objects.filter(id__in=sorted_job_ids)

    # Tạo danh sách các đối tượng Jobs với interaction_score
    res = []
    for job in job_recommends:
        interaction_score = filtered_interactions.get(job_id=job.id)[
            'total_rating']

        d = objJob(job)
        d["interaction_score"] = interaction_score

        res.append(d)

    res_sorted = sorted(
        res, key=lambda k: k['interaction_score'], reverse=True)

    return res_sorted


def case2(user_id):
    job_ids = Jobs.objects.values_list('id', flat=True)
    cbf_recommend = cbf(user_id)[:16]

    recommend_ids = [job["id"] for job in cbf_recommend]

    random_recommend_ids = randomRecommends(job_ids, recommend_ids)

    total_recommend_ids = recommend_ids + random_recommend_ids

    job_recommends = Jobs.objects.filter(id__in=total_recommend_ids)

    res = []

    for job in job_recommends:
        similarity = None
        for job_cbf in cbf_recommend:
            if job.id == job_cbf["id"]:
                similarity = job_cbf["similarity"]
                break

        d = objJob(job)

        d["similarity"] = similarity if similarity != None else -999

        res.append(d)

    res_sorted = sorted(
        res, key=lambda k: k['similarity'], reverse=True)

    return res_sorted


def case3(user_id):
    job_ids = Jobs.objects.values_list('id', flat=True)
    cf_recommend = cf(user_id)

    recommend_ids = list(cf_recommend.keys())[:16]

    random_recommend_ids = randomRecommends(job_ids, recommend_ids)

    total_recommend_ids = recommend_ids + random_recommend_ids

    job_recommends = Jobs.objects.filter(id__in=total_recommend_ids)

    res = []

    for job in job_recommends:
        d = objJob(job)

        d["mean_rating"] = - \
            999 if job.id in random_recommend_ids else cf_recommend[job.id]

        res.append(d)

    res_sorted = sorted(
        res, key=lambda k: k['mean_rating'], reverse=True)

    return res_sorted


def case4(user_id):
    cbf_recommend = cbf(user_id)
    cf_recommend = cf(user_id)

    page_rank_recommend = calcPageRank(cbf_recommend, cf_recommend)

    page_rank_recommend_sort = sorted(
        page_rank_recommend.items(), key=lambda x: x[1], reverse=True)

    page_rank_recommend_ids = [job_id for job_id,
                               rank in page_rank_recommend_sort][:16]

    job_ids = Jobs.objects.values_list('id', flat=True)

    random_recommend_ids = randomRecommends(job_ids, page_rank_recommend_ids)

    recommend_ids = page_rank_recommend_ids + random_recommend_ids

    job_recommends = Jobs.objects.filter(id__in=recommend_ids)

    res = []

    for job in job_recommends:
        d = objJob(job)

        d["page_rank_score"] = - \
            999 if job.id in random_recommend_ids else page_rank_recommend[job.id]
        res.append(d)

    res_sorted = sorted(
        res, key=lambda k: k['page_rank_score'], reverse=True)

    return res_sorted


def objJob(job: Jobs):
    return {
        "id": job.id,
        "title": job.title,
        "description": job.description,

        "company": {
            "id": job.company.id,
            "name": job.company.name,
            "photo": job.company.photo
        },

        "m_location_id": job.m_location.id,
        "location": {
            "id": job.m_location.id,
            "name": job.m_location.name
        },

        "m_education_level_id": job.m_education_level.id,
        "m_education_level_name": job.m_education_level.name,

        "m_experience_id": job.m_experience.id,
        "m_experience_name": job.m_experience.name,

        "m_working_form_id": job.m_working_form.id,

        "m_salary_id": job.m_salary.id,
        "salary": {
            "id": job.m_salary.id,
            "name": job.m_salary.name
        },

        "job_skills": job.jobskills_set.all().values('m_skill__id', 'm_skill__name'),

    }


def ndcg(recommend_ids, job_ids, k):
    if len(recommend_ids) == 0:
        return 0

    if len(job_ids) == 0:
        return 0

    if len(recommend_ids) > k:
        recommend_ids = recommend_ids[:k]

    dcg = 0.00000000001
    for i in range(len(recommend_ids)):
        if recommend_ids[i] in job_ids:
            dcg += 1 / math.log2(i + 2)

    idcg = 0.00000000001
    for i in range(len(job_ids)):
        idcg += 1 / math.log2(i + 2)

    return dcg / idcg
