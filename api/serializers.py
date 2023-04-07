from rest_framework import serializers
from api.models import UserSimilarities


class UserSimilaritiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSimilarities
        fields = '__all__'
