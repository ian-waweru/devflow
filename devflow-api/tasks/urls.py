from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'', TaskViewSet, basename='task')

urlpatterns = router.urls