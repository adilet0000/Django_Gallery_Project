# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse, reverse_lazy
from django.db.models import Q, Count, Avg
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.db.models.functions import Lower
from django.contrib.postgres.search import SearchVector, SearchQuery
from unicodedata import normalize

from django.template.loader import render_to_string
from django.http import HttpResponse

from django.core.paginator import Paginator
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, UpdateView, DeleteView, CreateView

from .models import Model, Pack, Tag, Comment, Rating, Subscription, FavoritePack, ContentSuggestion
from .forms import CommentForm, RatingForm, ContentSuggestionForm, CustomUserCreationForm




from django.core.paginator import Paginator

class ModelListView(ListView):
   model = Model
   template_name = 'gallery/index.html'
   context_object_name = 'model_list'
   paginate_by = 2

   def get_queryset(self):
      sort_by = self.request.GET.get('sort_by', 'subscribers')

      if sort_by == 'subscribers':
         queryset = Model.objects.annotate(subscriber_count=Count('subscribers')).order_by('-subscriber_count')
      elif sort_by == 'rating':
         queryset = Model.objects.annotate(subscriber_count=Count('subscribers')).order_by('-average_rating')
      else:
         queryset = Model.objects.annotate(subscriber_count=Count('subscribers')).order_by('-subscriber_count')

      for model in queryset:
         model.average_rating = model.update_rating()
      
      return queryset

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['sort_by'] = self.request.GET.get('sort_by', 'subscribers')
      
      if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
         from django.template.loader import render_to_string
         html = render_to_string('gallery/index.html', context, request=self.request)
         return HttpResponse(html)
      
      return context



class ModelDetailView(DetailView):
   model = Model
   template_name = 'gallery/model_detail.html'
   context_object_name = 'model'
   slug_field = 'slug'
   slug_url_kwarg = 'slug'

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      model = self.object
      packs = model.packs.prefetch_related('photos', 'videos').all()

      # Пагинация паков
      content_type = ContentType.objects.get_for_model(Model)
      ratings = Rating.objects.filter(content_type=content_type, object_id=model.id)
      average_rating = ratings.aggregate(Avg('score'))['score__avg'] or 0
      total_ratings = ratings.count()

      is_subscribed = self.request.user.is_authenticated and model.is_subscribed(self.request.user)

      packs_info = [
         {
            'pack': pack,
            'photos_count': pack.photos.count(),
            'videos_count': pack.videos.count(),
         }
         for pack in packs
      ]

      context.update({
         'packs_info': packs_info,
         'average_rating': average_rating,
         'total_ratings': total_ratings,
         'is_subscribed': is_subscribed,
      })
      return context

   def post(self, request, *args, **kwargs):
      """Обрабатываем POST-запрос для рейтинга"""
      model = self.get_object()
      content_type = ContentType.objects.get_for_model(Model)

      if request.user.is_authenticated and 'rating' in request.POST:
         rating_score = request.POST.get('rating')

         if rating_score and rating_score.isdigit() and 1 <= int(rating_score) <= 5:
            rating_score = int(rating_score)

            existing_rating = Rating.objects.filter(content_type=content_type, object_id=model.id, user=request.user).first()
            if existing_rating:
               existing_rating.score = rating_score
               existing_rating.save()
            else:
               Rating.objects.create(
                  content_type=content_type,
                  object_id=model.id,
                  user=request.user,
                  score=rating_score,
               )

            model.update_rating()

      return redirect('model_detail', slug=model.slug)



class SearchView(TemplateView):
   template_name = 'gallery/search_results.html'

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      query = self.request.GET.get('q', '').strip()

      if query:
         normalized_query = normalize('NFKD', query)

         models = Model.objects.filter(
            Q(name__icontains=normalized_query) | Q(bio__icontains=normalized_query)
         ).distinct()

         packs = Pack.objects.filter(
            Q(title__icontains=normalized_query) | Q(description__icontains=normalized_query)
         ).distinct()
      else:
         models = Model.objects.none()
         packs = Pack.objects.none()

      context.update({
         'query': query,
         'models': models,
         'packs': packs,
      })
      return context

    
class AutocompleteSearchView(View):
   def get(self, request, *args, **kwargs):
      query = normalize('NFKC', request.GET.get('q', '').strip().lower())
      results = []

      if query:
         model_results = Model.objects.filter(name__icontains=query)[:5]
         results.extend([
            {'type': 'model', 'name': model.name, 'url': model.get_absolute_url()}
            for model in model_results
         ])

         pack_results = Pack.objects.filter(title__icontains=query)[:5]
         results.extend([
            {'type': 'pack', 'name': pack.title, 'url': pack.get_absolute_url()}
            for pack in pack_results
         ])

      return JsonResponse({'results': results})



class RateObjectView(View):
    def post(self, request, app_label, model_name, slug, *args, **kwargs):
        score = request.POST.get('score')
        if not score or not score.isdigit() or int(score) not in range(1, 6):
            return JsonResponse({
                'success': False,
                'message': 'Некорректная оценка'
            }, status=400)

        content_type = get_object_or_404(ContentType, app_label=app_label, model=model_name)
        rated_object = get_object_or_404(content_type.model_class(), slug=slug)

        existing_rating = Rating.objects.filter(
            content_type=content_type,
            object_id=rated_object.id,
            user=request.user
        ).first()

        if existing_rating:
            existing_rating.score = int(score)
            existing_rating.save()
            message = f"Вы обновили свою оценку для {rated_object}."
        else:
            Rating.objects.create(
                content_type=content_type,
                object_id=rated_object.id,
                user=request.user,
                score=int(score)
            )
            message = f"Вы успешно оценили {rated_object}."

        average_rating = Rating.objects.filter(
            content_type=content_type,
            object_id=rated_object.id
        ).aggregate(Avg('score'))['score__avg']

        total_ratings = Rating.objects.filter(
            content_type=content_type,
            object_id=rated_object.id
        ).count()

        return JsonResponse({
            'success': True,
            'message': message,
            'average_rating': round(average_rating, 1) if average_rating else 0,
            'total_ratings': total_ratings
        })

class TagListView(ListView):
   model = Tag
   template_name = 'gallery/tag_list.html'
   context_object_name = 'tags'

class FilterByTagView(TemplateView):
   template_name = 'gallery/filter_results.html'

   def get(self, request, *args, **kwargs):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        context = self.get_context_data(**kwargs)
        return render(request, 'gallery/advanced_filter_results.html', context)
    return super().get(request, *args, **kwargs)

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
      context['tag'] = tag
      context['models'] = Model.objects.filter(tags=tag)
      context['packs'] = Pack.objects.filter(tags=tag)
      return context

class AdvancedFilterView(TemplateView):
   template_name = 'gallery/advanced_filter.html'

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      request = self.request

      tags = request.GET.getlist('tags')
      sort_by = request.GET.get('sort_by', 'created_at')

      models = Model.objects.all()
      packs = Pack.objects.all()
      if tags:
         models = models.filter(tags__slug__in=tags).distinct()
         packs = packs.filter(tags__slug__in=tags).distinct()

      # Сортировка
      if sort_by == 'popularity':
         model_content_type = ContentType.objects.get_for_model(Model)
         pack_content_type = ContentType.objects.get_for_model(Pack)

         models = sorted(models, key=lambda m: Rating.objects.filter(
            content_type=model_content_type, object_id=m.id).count(), reverse=True)
         packs = sorted(packs, key=lambda p: Rating.objects.filter(
            content_type=pack_content_type, object_id=p.id).count(), reverse=True)

      elif sort_by == 'average_rating':
         models = sorted(models, key=lambda m: Rating.objects.filter(
            content_type=ContentType.objects.get_for_model(Model), object_id=m.id
         ).aggregate(avg=Avg('score'))['avg'] or 0, reverse=True)

         packs = sorted(packs, key=lambda p: Rating.objects.filter(
            content_type=ContentType.objects.get_for_model(Pack), object_id=p.id
         ).aggregate(avg=Avg('score'))['avg'] or 0, reverse=True)
      else:
         models = models.order_by('-created_at')
         packs = packs.order_by('-created_at')

      all_tags = Tag.objects.all()

      context.update({
         'models': models,
         'packs': packs,
         'all_tags': all_tags,
         'selected_tags': tags,
         'sort_by': sort_by,
      })
      return context



class PackDetailView(DetailView):
   model = Pack
   template_name = 'gallery/pack_detail.html'
   context_object_name = 'pack'
   slug_field = 'slug'
   slug_url_kwarg = 'slug'
   


   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       pack = self.object
       
       page = self.request.GET.get('page', 1)
       comments = pack.comments.all().order_by('-created_at')
       paginator = Paginator(comments, 2)
       comments_page = paginator.get_page(page)
       
       if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest' and self.request.GET.get('load_comments'):
           data = {
               'comments': [{
                   'id': comment.id,
                   'username': comment.user.username,
                   'text': comment.text,
                   'created_at': comment.created_at.strftime('%d %b %Y, %H:%M'),
                   'is_author': comment.user == self.request.user,
                   'edit_url': reverse('edit_comment', args=[comment.pk]),
                   'delete_url': reverse('delete_comment', args=[comment.pk])
               } for comment in comments_page],
               'has_next': comments_page.has_next(),
               'has_previous': comments_page.has_previous(),
               'current_page': comments_page.number,
               'total_pages': paginator.num_pages
           }
           return JsonResponse(data)

       context['comments'] = comments_page
       context['photos'] = pack.photos.all()
       
       content_type = ContentType.objects.get_for_model(Pack)
       ratings = Rating.objects.filter(content_type=content_type, object_id=pack.id)
       context['average_rating'] = ratings.aggregate(Avg('score'))['score__avg'] or 0
       context['total_ratings'] = ratings.count()

       user = self.request.user
       context['is_favorite'] = user.is_authenticated and FavoritePack.objects.filter(user=user, pack=pack).exists()

       context['comment_form'] = CommentForm()
       return context

   def post(self, request, *args, **kwargs):
       self.object = self.get_object()
       
       if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
           comment_form = CommentForm(request.POST)
           if comment_form.is_valid():
               comment = comment_form.save(commit=False)
               comment.pack = self.object
               comment.user = request.user
               comment.save()
               
               return JsonResponse({
                   'success': True,
                   'comment': {
                       'id': comment.id,
                       'username': comment.user.username,
                       'text': comment.text,
                       'created_at': comment.created_at.strftime('%d %b %Y, %H:%M'),
                       'is_author': True,
                       'edit_url': reverse('edit_comment', args=[comment.pk]),
                       'delete_url': reverse('delete_comment', args=[comment.pk])
                   }
               })
           return JsonResponse({'success': False})
           
       return super().post(request, *args, **kwargs)
    

class EditCommentView(LoginRequiredMixin, UpdateView):
   model = Comment
   form_class = CommentForm
   template_name = 'gallery/edit_comment.html'
   context_object_name = 'comment'

   def dispatch(self, request, *args, **kwargs):
      """Запрещаем редактирование чужих комментариев"""
      comment = self.get_object()
      if comment.user != request.user:
         return HttpResponseForbidden("Вы не можете редактировать чужой комментарий.")
      return super().dispatch(request, *args, **kwargs)

   def get_success_url(self):
      """После успешного редактирования возвращаем строковый URL"""
      return reverse('pack_detail', kwargs={'slug': self.object.pack.slug})



class DeleteCommentView(LoginRequiredMixin, DeleteView):
   model = Comment
   template_name = 'gallery/delete_comment.html'
   context_object_name = 'comment'

   def dispatch(self, request, *args, **kwargs):
      """Запрещаем удаление чужих комментариев"""
      comment = self.get_object()
      if comment.user != request.user:
         return HttpResponseForbidden("Вы не можете удалить чужой комментарий.")
      return super().dispatch(request, *args, **kwargs)

   def get_success_url(self):
      """После удаления возвращаем на страницу пака"""
      return reverse('pack_detail', kwargs={'slug': self.object.pack.slug})



class UserProfileView(LoginRequiredMixin, DetailView):
   model = User
   template_name = 'gallery/user_profile.html'
   context_object_name = 'profile_user'
   slug_field = 'username'
   slug_url_kwarg = 'username'

   def get_context_data(self, **kwargs):
      """Добавляем комментарии и рейтинги пользователя в контекст"""
      context = super().get_context_data(**kwargs)
      user = self.object
      context['comments'] = Comment.objects.filter(user=user).order_by('-created_at')
      context['ratings'] = Rating.objects.filter(user=user).select_related('content_type').order_by('-id')
      return context



class FavoritesListView(LoginRequiredMixin, ListView):
   model = FavoritePack
   template_name = 'gallery/favorites_list.html'
   context_object_name = 'favorites'

   def get_queryset(self):
      """Фильтруем избранные паки по текущему пользователю"""
      return FavoritePack.objects.filter(user=self.request.user).select_related('pack')

 
class AddToFavoritesView(LoginRequiredMixin, View):
    def post(self, request, slug, *args, **kwargs):
        """Добавляет пак в избранное через AJAX"""
        pack = get_object_or_404(Pack, slug=slug)
        FavoritePack.objects.get_or_create(user=request.user, pack=pack)

        return JsonResponse({
            'success': True,
            'is_favorite': True,
            'new_action_url': reverse('remove_from_favorites', kwargs={'slug': slug})
        })


class RemoveFromFavoritesView(LoginRequiredMixin, View):
    def post(self, request, slug, *args, **kwargs):
        """Удаляет пак из избранного через AJAX"""
        pack = get_object_or_404(Pack, slug=slug)
        FavoritePack.objects.filter(user=request.user, pack=pack).delete()

        return JsonResponse({
            'success': True,
            'is_favorite': False,
            'new_action_url': reverse('add_to_favorites', kwargs={'slug': slug})
        })

class SignUpView(CreateView):
   model = User
   form_class = CustomUserCreationForm
   template_name = 'gallery/signup.html'
   success_url = reverse_lazy('login')

   def form_valid(self, form):
      """При успешной регистрации хешируем пароль, логиним пользователя и показываем сообщение"""
      user = form.save(commit=False)
      user.set_password(form.cleaned_data['password1'])
      user.save()

      login(self.request, user)
      messages.success(self.request, 'Регистрация прошла успешно!')
      return redirect(self.success_url)


class UserLoginView(LoginView):
   template_name = 'gallery/login.html'
   redirect_authenticated_user = True
   next_page = reverse_lazy('index')

   def form_valid(self, form):
      messages.success(self.request, "Вы успешно вошли в систему!")
      return super().form_valid(form)

   def form_invalid(self, form):
      messages.error(self.request, "Неверное имя пользователя или пароль.")
      return super().form_invalid(form)


class SubmitSuggestionView(LoginRequiredMixin, CreateView):
   model = ContentSuggestion
   form_class = ContentSuggestionForm
   template_name = 'gallery/submit_suggestion.html'
   success_url = reverse_lazy('index')

   def form_valid(self, form):
      form.instance.user = self.request.user
      return super().form_valid(form)


class SubscribeView(LoginRequiredMixin, View):
    def post(self, request, model_slug, *args, **kwargs):
        try:
            model = get_object_or_404(Model, slug=model_slug)
            subscription, created = Subscription.objects.get_or_create(
                user=request.user, 
                model=model
            )

            button_html = f"""
            <div class="subscription-buttons">
                <form action="{request.build_absolute_uri('/unsubscribe/' + model.slug + '/')}" method="post">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{request.COOKIES.get('csrftoken')}">
                    <button type="submit" class="btn btn-danger">Отписаться</button>
                </form>
            </div>
            """

            return JsonResponse({
                'status': 'success' if created else 'info',
                'message': f"Вы успешно подписались на {model.name}!" if created 
                          else f"Вы уже подписаны на {model.name}.",
                'subscribers_count': model.subscribers.count(),
                'button_html': button_html
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

class UnsubscribeView(LoginRequiredMixin, View):
    def post(self, request, model_slug, *args, **kwargs):
        try:
            model = get_object_or_404(Model, slug=model_slug)
            subscription = Subscription.objects.filter(
                user=request.user, 
                model=model
            ).first()

            if subscription:
                subscription.delete()
                message = f"Вы успешно отписались от {model.name}."
                status = 'success'
            else:
                message = f"Вы не были подписаны на {model.name}."
                status = 'warning'

            button_html = f"""
            <div class="subscription-buttons">
                <form action="{request.build_absolute_uri('/subscribe/' + model.slug + '/')}" method="post">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{request.COOKIES.get('csrftoken')}">
                    <button type="submit" class="btn btn-success">Подписаться</button>
                </form>
            </div>
            """

            return JsonResponse({
                'status': status,
                'message': message,
                'subscribers_count': model.subscribers.count(),
                'button_html': button_html
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            

class NotificationsView(LoginRequiredMixin, ListView):
   template_name = 'gallery/notifications.html'
   context_object_name = 'new_packs'

   def get_queryset(self):
      """Получаем паки от подписанных моделей"""
      user_subscriptions = Subscription.objects.filter(user=self.request.user).values_list('model_id', flat=True)
      return Pack.objects.filter(model_id__in=user_subscriptions).order_by('-created_at')



class AdminSuggestionsView(UserPassesTestMixin, ListView):
   """Отображение списка предложений (только для админов)"""
   model = ContentSuggestion
   template_name = 'gallery/admin_suggestions.html'
   context_object_name = 'suggestions'

   def test_func(self):
      """Проверяем, является ли пользователь администратором"""
      return self.request.user.is_staff

   def get_queryset(self):
      """Выбираем только непроверенные предложения"""
      return ContentSuggestion.objects.filter(is_reviewed=False)

@method_decorator(staff_member_required, name='dispatch')
class AdminSuggestionActionView(View):
   """Обрабатывает одобрение и отклонение предложений"""
   def post(self, request, *args, **kwargs):
      suggestion_id = request.POST.get('suggestion_id')
      action = request.POST.get('action')
      suggestion = get_object_or_404(ContentSuggestion, id=suggestion_id)

      if action == 'approve':
         if suggestion.suggestion_type == 'model':
            model_instance = Model.objects.create(
               name=suggestion.model_name,
               bio=suggestion.model_bio,
               avatar=suggestion.model_avatar
            )
            suggestion.related_model = model_instance

         elif suggestion.suggestion_type == 'pack':
            if not suggestion.related_model:
               messages.error(request, "Ошибка: Пак должен быть привязан к модели.")
               return redirect('admin_suggestions')

            Pack.objects.create(
               title=suggestion.pack_title,
               description=suggestion.pack_description,
               model=suggestion.related_model
            )

      suggestion.is_reviewed = True
      suggestion.save()
      return redirect('admin_suggestions')

