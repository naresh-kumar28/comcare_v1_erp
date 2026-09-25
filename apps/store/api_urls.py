from rest_framework.routers import DefaultRouter
from apps.store.api_views import ProductViewSet

router = DefaultRouter()
router.register(r'', ProductViewSet, basename='product')

urlpatterns = router.urls
