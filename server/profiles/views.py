# profiles/views.py
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import transaction,models


from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView


from .models import Field, FieldAssignment, FieldAttachment, UserRole, UserStatus
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    FieldSerializer,
    FieldAssignmentSerializer,
    FieldListSerializer,
    FieldDetailSerializer,
    AssignedAgentSerializer,
    FieldAttachmentSerializer,
    BulkFieldAssignmentSerializer,
    TokenLoginSerializer,

)
from .permissions import (
    IsAdmin,
    IsAdminOrCoordinator,
    IsOwnerOrAdmin,
    IsFieldAssignmentCreatorOrAdmin,
)

User = get_user_model()


# ==================== AUTH VIEWS ====================

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT login view"""
    serializer_class = CustomTokenObtainPairSerializer

# --- Login view (returns tokens + user info) ---
class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # create tokens
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        user_data = UserSerializer(user).data
        return Response({
            "message": "Login successful.",
            "user": user_data,
            # "is_active": user.is_active,
            "access": access,
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)




class CustomTokenRefreshView(TokenRefreshView):
    """JWT token refresh view"""
    pass


class RegistrationView(generics.CreateAPIView):
    """User registration view"""
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for immediate login
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LogoutView(generics.GenericAPIView):
    """Logout view - blacklist refresh token"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


# ==================== USER VIEWS ====================

class UserViewSet(viewsets.ModelViewSet):
    """User CRUD operations"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action == 'list':
            return [IsAdminOrCoordinator()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = User.objects.all()

        # Filter by role
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Search by username or email
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(phone_number__icontains=search)
            )

        return queryset

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change password for current user"""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'detail': 'Password updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAdmin])
    def bulk_create(self, request):
        """Bulk create users from list"""
        serializer = UserRegistrationSerializer(data=request.data, many=True)
        if serializer.is_valid():
            users = serializer.save()
            return Response(UserSerializer(users, many=True).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Activate/Deactivate user"""
        user = self.get_object()
        if user.status == UserStatus.ACTIVE:
            user.status = UserStatus.INACTIVE
        else:
            user.status = UserStatus.ACTIVE
        user.save()
        return Response(UserSerializer(user).data)


# ==================== FIELD VIEWS ====================



class FieldViewSet(viewsets.ModelViewSet):
    """Field CRUD operations"""
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return FieldDetailSerializer
        if self.action == 'list':
            return FieldDetailSerializer
        if self.action in ['agents', 'assign_agents', 'remove_agents']:
            return AssignedAgentSerializer
        if self.action == 'attachments':
            return FieldAttachmentSerializer
        return FieldSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'assign_agents', 'remove_agents']:
            return [IsAdminOrCoordinator()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = Field.objects.prefetch_related(
            'attachments',
            'fieldassignment_set__agent'
        ).annotate(
            active_season_count=models.Count(
                'seasons',
                filter=models.Q(seasons__status='active')
            ),
            active_agent_count=models.Count(
                'fieldassignment'
            )
        ).order_by('name')

        # Filter by active seasons
        has_active_seasons = self.request.query_params.get('has_active_seasons', None)
        if has_active_seasons is not None:
            if has_active_seasons.lower() == 'true':
                queryset = queryset.filter(active_season_count__gt=0)
            else:
                queryset = queryset.filter(active_season_count=0)

        # Search by name
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """
        Get single field with all related data:
        - Active seasons
        - Attachments
        - Assigned agents
        """
        instance = self.get_object()

        # Use the detail serializer which includes everything
        serializer = FieldDetailSerializer(instance, context={'request': request})

        return Response({
            'data': serializer.data,
            'meta': {
                'total_seasons': instance.seasons.count(),
                'active_seasons': instance.seasons.filter(status='active').count(),
                'assigned_agents': instance.fieldassignment_set.count(),
                'attachments': instance.attachments.count(),
            }
        })

    @action(detail=True, methods=['get'])
    def agents(self, request, pk=None):
        """Get all agents assigned to a field"""
        field = self.get_object()
        assignments = FieldAssignment.objects.filter(field=field)
        serializer = FieldAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrCoordinator])
    def assign_agents(self, request, pk=None):
        """Assign multiple agents to a field"""
        field = self.get_object()
        agent_ids = request.data.get('agent_ids', [])

        assigned = []
        errors = []

        for agent_id in agent_ids:
            try:
                agent = User.objects.get(id=agent_id, role=UserRole.FIELD_AGENT)
                assignment, created = FieldAssignment.objects.get_or_create(
                    field=field,
                    agent=agent,
                    defaults={'assigned_by': request.user}
                )
                if created:
                    assigned.append(FieldAssignmentSerializer(assignment).data)
                else:
                    errors.append(f"Agent {agent.username} already assigned")
            except User.DoesNotExist:
                errors.append(f"Agent with ID {agent_id} not found or not a field agent")

        return Response({
            'assigned': assigned,
            'errors': errors
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrCoordinator])
    def remove_agents(self, request, pk=None):
        """Remove agents from a field"""
        field = self.get_object()
        agent_ids = request.data.get('agent_ids', [])

        removed = FieldAssignment.objects.filter(
            field=field,
            agent_id__in=agent_ids
        ).delete()

        return Response({
            'removed_count': removed[0],
            'message': f'Successfully removed {removed[0]} agents'
        })


# ==================== FIELD ASSIGNMENT VIEWS ====================

class FieldAssignmentViewSet(viewsets.ModelViewSet):
    """Field Assignment CRUD operations"""
    queryset = FieldAssignment.objects.all()
    serializer_class = FieldAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrCoordinator]

    def get_queryset(self):
        queryset = FieldAssignment.objects.all()

        # Filter by field
        field_id = self.request.query_params.get('field_id', None)
        if field_id:
            queryset = queryset.filter(field_id=field_id)

        # Filter by agent
        agent_id = self.request.query_params.get('agent_id', None)
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)

        # Filter by current user if field agent
        if self.request.user.role == UserRole.FIELD_AGENT:
            queryset = queryset.filter(agent=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create assignments"""
        serializer = BulkFieldAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            field = get_object_or_404(Field, id=serializer.validated_data['field_id'])
            agent_ids = serializer.validated_data['agent_ids']

            assignments = []
            for agent_id in agent_ids:
                agent = get_object_or_404(User, id=agent_id)
                assignment, created = FieldAssignment.objects.get_or_create(
                    field=field,
                    agent=agent,
                    defaults={'assigned_by': request.user}
                )
                if created:
                    assignments.append(assignment)

            return Response(
                FieldAssignmentSerializer(assignments, many=True).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== FIELD ATTACHMENT VIEWS ====================

class FieldAttachmentViewSet(viewsets.ModelViewSet):
    """Field Attachment CRUD operations"""
    queryset = FieldAttachment.objects.all()
    serializer_class = FieldAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrCoordinator()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = FieldAttachment.objects.all()

        # Filter by field
        field_id = self.request.query_params.get('field_id', None)
        if field_id:
            queryset = queryset.filter(field_id=field_id)

        # Filter by attachment type
        attachment_type = self.request.query_params.get('attachment_type', None)
        if attachment_type:
            queryset = queryset.filter(attachment_type=attachment_type)

        return queryset

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Bulk upload files for a field"""
        field_id = request.data.get('field_id')
        files = request.FILES.getlist('files')

        if not field_id:
            return Response({'error': 'field_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        field = get_object_or_404(Field, id=field_id)
        attachments = []

        for file in files:
            attachment = FieldAttachment.objects.create(
                field=field,
                file=file,
                filename=file.name,
                file_size=file.size,
                mime_type=file.content_type,
                attachment_type=request.data.get('attachment_type', 'other'),
                description=request.data.get('description', ''),
                uploaded_by=request.user
            )
            attachments.append(attachment)

        return Response(
            FieldAttachmentSerializer(attachments, many=True).data,
            status=status.HTTP_201_CREATED
        )
