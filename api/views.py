from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def calcTFIDF(request):

    dataset = [
        "AAAA BBB",
        "CCC"
    ]

    tfIdfTransformer = TfidfTransformer(use_idf=True)
    countVectorizer = CountVectorizer()
    wordCount = countVectorizer.fit_transform(dataset)
    newTfIdf = tfIdfTransformer.fit_transform(wordCount)
    df = pd.DataFrame(newTfIdf[0].T.todense(
    ), index=countVectorizer.get_feature_names_out(), columns=["TF-IDF"])
    df = df.sort_values('TF-IDF', ascending=False)

    return Response({'idfs': newTfIdf})
