from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (BaseAPIRootView, IngredientViewSet, RecipeViewSet,
                       TagViewSet, UserViewSet)

app_name = 'api'


class RuDefaultRouter(DefaultRouter):
    """Показывает описание главной страницы API на русском языке.
    """
    APIRootView = BaseAPIRootView


v1_router = RuDefaultRouter()
v1_router.register('tags', TagViewSet, 'tags')
v1_router.register('ingredients', IngredientViewSet, 'ingredients')
v1_router.register('recipes', RecipeViewSet, 'recipes')
v1_router.register('users', UserViewSet, 'users')

urlpatterns = (
    path('v1/', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
)
