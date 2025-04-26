from django.urls import path
from .views import ModelListView, ModelDetailView, SearchView, AutocompleteSearchView, RateObjectView, TagListView, FilterByTagView, AdvancedFilterView, PackDetailView, EditCommentView, DeleteCommentView, UserProfileView, FavoritesListView, AddToFavoritesView, RemoveFromFavoritesView, SignUpView, UserLoginView, SubmitSuggestionView, SubscribeView, UnsubscribeView, NotificationsView, AdminSuggestionsView, AdminSuggestionActionView
from django.contrib.auth import views as auth_views

urlpatterns = [
   # Главная и поиск
   path('', ModelListView.as_view(), name='index'),
   path('search/', SearchView.as_view(), name='search'),
   path('autocomplete/', AutocompleteSearchView.as_view(), name='autocomplete_search'),
   path('advanced-filter/', AdvancedFilterView.as_view(), name='advanced_filter'),

   # Аутентификация и профиль
   path('login/', UserLoginView.as_view(), name='login'),
   path('logout/', auth_views.LogoutView.as_view(), name='logout'),
   path('signup/', SignUpView.as_view(), name='signup'),
   path('profile/<str:username>/', UserProfileView.as_view(), name='user_profile'),

   # Паки и избранное
   path('packs/<slug:slug>/', PackDetailView.as_view(), name='pack_detail'),
   path('favorites/', FavoritesListView.as_view(), name='favorites_list'),
   path('favorites/add/<slug:slug>/', AddToFavoritesView.as_view(), name='add_to_favorites'),
   path('favorites/remove/<slug:slug>/', RemoveFromFavoritesView.as_view(), name='remove_from_favorites'),

   # Подписки и уведомления
   path('subscribe/<slug:model_slug>/', SubscribeView.as_view(), name='subscribe'),
   path('unsubscribe/<slug:model_slug>/', UnsubscribeView.as_view(), name='unsubscribe'),
   path('notifications/', NotificationsView.as_view(), name='notifications'),

   # Комментарии
   path('comment/edit/<int:pk>/', EditCommentView.as_view(), name='edit_comment'),
   path('comment/delete/<int:pk>/', DeleteCommentView.as_view(), name='delete_comment'),

   # Оценки и рейтинги
   path('rate/<str:app_label>/<str:model_name>/<slug:slug>/', RateObjectView.as_view(), name='rate_object'),

   # Предложения для сайта
   path('suggestion/', SubmitSuggestionView.as_view(), name='submit_suggestion'),

   # Админка и модерация
   path('moderation/suggestions/', AdminSuggestionsView.as_view(), name='admin_suggestions'),
   path('moderation/suggestions/action/', AdminSuggestionActionView.as_view(), name='admin_suggestion_action'),
   
   # Темы и авторы
   path('tags/', TagListView.as_view(), name='tag_list'),
   path('tags/<slug:tag_slug>/', FilterByTagView.as_view(), name='filter_by_tag'),
   path('<slug:slug>/', ModelDetailView.as_view(), name='model_detail'),
]

