from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenViewBase
from django.db.models import Avg

from . import serializers
from .permissions import (
    AdminOnly, SelfOnly, IsAdminOrReadOnly, ReviewCommentPermission)
from reviews.models import User, Review, Category, Genre, Title
from api.filters import TitleFilter


class ListCreateDeleteViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    pass


class UserViewSet(viewsets.ModelViewSet):
    """
    Отображает, создает, обновляет и удаляет
    инстансы, относящиеся к :model:'posts.Post'.
    Представление доступно только юзерам с ролью
    'admin' и суперюзеру. Настроен поиск по полю
    'username'. При обращении к detail-представлению
    используется слаг 'username'.
    """

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [AdminOnly, ]
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'


class MeUserAPIView(APIView):
    """
    На эндпоинте v1/users/me предусматриваем представление
    объекта :model:'reviews.User', который можно либо
    получить (просмотреть), либо частично обновить.
    Эндпоинт доступен только авторизованным (jwt-токен)
    юзерам-объектам запроса.
    """

    permission_classes = [SelfOnly, ]

    def get(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = serializers.MeUserSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = serializers.MeUserSerializer(
            user,
            data=request.data,
            partial=True)
        if serializer.is_valid():
            serializer.save(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class RegistrationView(APIView):
    """
    Api-view для регистрации :model:'reviews.User' объектов.
    Любой допущен к регистрации таких инстансов.
    Также отправляет confirmation_code для получения jwt-токена.
    Поля - 'username' и 'email'.
    """

    permission_classes = [AllowAny, ]

    def post(self, request):
        """"Обработка POST-запроса на эндпоинт v1/auth/signup."""
        serializer = serializers.RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # При создании нового юзера направляем конфирмационный код.
            username = serializer.data['username']
            user = get_object_or_404(User, username=username)
            user.send_confirmation_code()
            return Response(serializer.data, status=status.HTTP_200_OK)
        # При пост-запросе отправка кода на email
        # существующему юзеру проводится на initial_data,
        # поскольку данные не прошли валидацию.
        try:
            username = serializer.initial_data['username']
            email = serializer.initial_data['email']
            if User.objects.filter(username=username, email=email).exists():
                user = User.objects.get(username=username, email=email)
                user.send_confirmation_code()
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        # Перехватываем ошибки отсутствия 'username' и 'email',
        # поскольку метод .is_valid() не предусматривает выбрасывание
        # exception по причине необходимости направления электронного письма
        # даже в случае ошибки валидации.
        except KeyError or ValidationError:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class TokenObtainApiYamdbView(TokenViewBase):
    """
    Вью-класс для эндпоинта v1/auth/token.
    Предназначен для выдачи jwt-токена.
    По сравнению с базовым: переопределен сериализатор.
    Введена настройка доступа - "для всех" - отличная
    от настроек проекта в settings.py.
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.YAMDbTokenObtainSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Вью-сет для отзывов.
    """
    serializer_class = serializers.ReviewSerializer
    permission_classes = [ReviewCommentPermission]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        author = self.request.user
        serializer.save(title=title, author=author)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Вью-сет для комментариев.
    """

    serializer_class = serializers.CommentSerializer
    permission_classes = [ReviewCommentPermission]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id, title=title_id)
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id, title=title_id)
        author = self.request.user
        serializer.save(review=review, author=author)


class TitlesViewSet(viewsets.ModelViewSet):
    """
    Вью-сет для Titles.
    """

    queryset = Title.objects.all().annotate(
        Avg("reviews__score")).order_by("id")
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.TitleListSerializer
        return serializers.TitleCreateSerializer


class GenresViewSet(ListCreateDeleteViewSet):
    """
    Вью-сет для жанров.
    """

    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
    permission_classes = (IsAdminOrReadOnly, )
    lookup_field = 'slug'
    pagination_class = PageNumberPagination


class CategoriesViewSet(ListCreateDeleteViewSet):
    """
    Вью-сет для категорий.
    """

    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
    permission_classes = (IsAdminOrReadOnly, )
    lookup_field = 'slug'
    pagination_class = PageNumberPagination
