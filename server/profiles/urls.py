
# profiles/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    RegistrationView,
    LogoutView,
    UserViewSet,
    FieldViewSet,
    FieldAssignmentViewSet,
    FieldAttachmentViewSet,
    LoginView
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'fields', FieldViewSet)
router.register(r'field-assignments', FieldAssignmentViewSet)
router.register(r'field-attachments', FieldAttachmentViewSet)

urlpatterns = [
    # Auth endpoints
    path('logins/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegistrationView.as_view(), name='auth_register'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('login/', LoginView.as_view(), name="login"),

    # Router URLs
    path('', include(router.urls)),
]
