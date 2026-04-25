from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import (
#     UserViewSet, FieldViewSet, CropSeasonViewSet,
#     FieldUpdateViewSet
# )

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

]
