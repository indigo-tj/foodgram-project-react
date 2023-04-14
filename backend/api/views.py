from __future__ import annotations

from datetime import datetime as dt
from urllib.parse import unquote

from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import F, Q, QuerySet, Sum
from django.http.response import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.mixins import AddDelViewMixin
from api.paginators import PageLimitPagination
from api.permissions import AdminOrReadOnly, AuthorStaffOrReadOnly
from api.serializers import (IngredientSerializer, RecipeSerializer,
                             ShortRecipeSerializer, TagSerializer,
                             UserSubscribeSerializer)
from core.enums import Tuples, UrlQueries
from core.services import incorrect_layout
from foodgram.settings import DATE_TIME_FORMAT
from recipes.models import Carts, Favorites, Ingredient, Recipe, Tag
from users.models import Subscriptions

User = get_user_model()


class BaseAPIRootView(APIRootView):
    """Базовые пути API приложения.
    """


class UserViewSet(DjoserUserViewSet, AddDelViewMixin):
    """Работает с пользователями.
    """
    pagination_class = PageLimitPagination
    add_serializer = UserSubscribeSerializer
    permission_classes = (DjangoModelPermissions,)

    @action(
        methods=Tuples.ACTION_METHODS,
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request: WSGIRequest, id: int | str) -> Response:
        """Создаёт/удалет связь между пользователями.
        """
        return self._add_del_obj(id, Subscriptions, Q(author__id=id))

    @action(methods=('get',), detail=False)
    def subscriptions(self, request: WSGIRequest) -> Response:
        """Список подписок пользоваетеля.
        """
        if self.request.user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)

        pages = self.paginate_queryset(
            User.objects.filter(subscribers__user=self.request.user)
        )
        serializer = UserSubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Работает с тэгами.
    Изменение и создание тэгов разрешено только админам.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Работает с игридиентами.
    Изменение и создание ингридиентов разрешено только админам.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)

    def get_queryset(self) -> list[Ingredient]:
        """Получает queryset в соответствии с параметрами запроса.
        Реализован поиск объектов по совпадению в начале названия,
        также добавляются результаты по совпадению в середине.
        """
        name: str = self.request.query_params.get(UrlQueries.SEARCH_ING_NAME)
        queryset = self.queryset

        if name:
            if name[0] == '%':
                name = unquote(name)
            else:
                name = name.translate(incorrect_layout)

            name = name.lower()
            start_queryset = list(queryset.filter(name__istartswith=name))
            ingridients_set = set(start_queryset)
            cont_queryset = queryset.filter(name__icontains=name)
            start_queryset.extend(
                [ing for ing in cont_queryset if ing not in ingridients_set]
            )
            queryset = start_queryset

        return queryset


class RecipeViewSet(ModelViewSet, AddDelViewMixin):
    """Работает с рецептами.
    Вывод, создание, редактирование, добавление/удаление
    в избранное и список покупок.
    """
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (AuthorStaffOrReadOnly,)
    pagination_class = PageLimitPagination
    add_serializer = ShortRecipeSerializer

    def get_queryset(self) -> QuerySet[Recipe]:
        """Получает queryset в соответствии с параметрами запроса.
        """
        queryset = self.queryset

        tags: list = self.request.query_params.getlist(UrlQueries.TAGS.value)
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags).distinct()

        author: str = self.request.query_params.get(UrlQueries.AUTHOR.value)
        if author:
            queryset = queryset.filter(author=author)

        if self.request.user.is_anonymous:
            return queryset

        is_in_cart: str = self.request.query_params.get(UrlQueries.SHOP_CART)
        if is_in_cart in Tuples.SYMBOL_TRUE_SEARCH.value:
            queryset = queryset.filter(in_carts__user=self.request.user)
        elif is_in_cart in Tuples.SYMBOL_FALSE_SEARCH.value:
            queryset = queryset.exclude(in_carts__user=self.request.user)

        is_favorit: str = self.request.query_params.get(UrlQueries.FAVORITE)
        if is_favorit in Tuples.SYMBOL_TRUE_SEARCH.value:
            queryset = queryset.filter(in_favorites__user=self.request.user)
        if is_favorit in Tuples.SYMBOL_FALSE_SEARCH.value:
            queryset = queryset.exclude(in_favorites__user=self.request.user)
        return queryset

    @action(
        methods=Tuples.ACTION_METHODS,
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request: WSGIRequest, pk: int | str) -> Response:
        """Добавляет/удалет рецепт в `избранное`.
        """
        return self._add_del_obj(pk, Favorites, Q(recipe__id=pk))

    @action(
        methods=Tuples.ACTION_METHODS,
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request: WSGIRequest, pk: int | str) -> Response:
        """Добавляет/удалет рецепт в `корзину`.
        """
        return self._add_del_obj(pk, Carts, Q(recipe__id=pk))

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request: WSGIRequest) -> Response:
        """Загружает файл *.txt со списком покупок.
        """
        user = self.request.user
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = [
            f'Список покупок для:\n\n{user.first_name}\n'
            f'{dt.now().strftime(DATE_TIME_FORMAT)}\n'
        ]

        ingredients = Ingredient.objects.filter(
            recipe__recipe__in_carts__user=user
        ).values(
            'name',
            measurement=F('measurement_unit')
        ).annotate(amount=Sum('recipe__amount'))

        for ing in ingredients:
            shopping_list.append(
                f'{ing["name"]}: {ing["amount"]} {ing["measurement"]}'
            )

        shopping_list.append('\nПосчитано в Foodgram')
        shopping_list = '\n'.join(shopping_list)
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
