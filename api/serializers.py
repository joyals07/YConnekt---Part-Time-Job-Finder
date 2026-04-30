from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from EmployerApp.models import EmployerDB
from EmployeeApp.models import EmployeeDB

class CustomTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        role = None
        if EmployerDB.objects.filter(user=user).exists():
            role = "employer"
        elif EmployeeDB.objects.filter(user=user).exists():
            role = "employee"

        data.update({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": role
        })

        return data