from rest_framework.response import Response
from rest_framework.decorators import api_view
from sklearn.neighbors import NearestNeighbors
import numpy as np


@api_view(['GET'])
def hello_world(request):
    print(request)

    return Response({'message': 'Hello, world!'})
