from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, FieldViewSet, CropSeasonViewSet,
    FieldUpdateViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'fields', FieldViewSet)
router.register(r'seasons', CropSeasonViewSet, basename='seasons')
router.register(r'updates', FieldUpdateViewSet, basename='updates')

urlpatterns = [
    path('', include(router.urls)),
]
