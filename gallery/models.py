from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.db.models import Avg
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models.functions import Lower

class Tag(models.Model):
   name = models.CharField(max_length=100)
   slug = models.SlugField(unique=True, blank=True)

   def save(self, *args, **kwargs):
      if not self.slug:
         self.slug = slugify(self.name)
      super().save(*args, **kwargs)
      
   def __str__(self):
      return self.name



class Model(models.Model):  # Модель человека (автора)
   name = models.CharField(max_length=100)
   bio = models.TextField(blank=True, null=True)
   avatar = models.ImageField(upload_to='avatars/')
   tags = models.ManyToManyField('Tag', blank=True, related_name='models')
   average_rating = models.FloatField(default=0)
   slug = models.SlugField(unique=True, blank=True)
   subscribers = models.ManyToManyField(
      User, 
      through='Subscription', 
      related_name='subscribed_models'
   )
   created_at = models.DateTimeField(auto_now_add=True)
   
   @property
   def popularity(self):
      return Rating.objects.filter(content_type=ContentType.objects.get_for_model(Model), object_id=self.id).count()

   def update_rating(self):
        content_type = ContentType.objects.get_for_model(self)
        ratings = Rating.objects.filter(content_type=content_type, object_id=self.id)
        self.average_rating = ratings.aggregate(Avg('score'))['score__avg'] or 0
        self.save()
        return self.average_rating
   

   def save(self, *args, **kwargs):
      if not self.slug:
         self.slug = slugify(self.name)
      super().save(*args, **kwargs)
      
   def is_subscribed(self, user):
      return self.subscribers.filter(id=user.id).exists()

   def get_absolute_url(self):
      return reverse('model_detail', kwargs={'slug': self.slug})


   def __str__(self):
      return self.name
   



class Subscription(models.Model):
   user = models.ForeignKey(
      User, 
      on_delete=models.CASCADE, 
      related_name='subscriptions'
   )
   model = models.ForeignKey(
      'Model', 
      on_delete=models.CASCADE, 
      related_name='model_subscriptions'
   )
   created_at = models.DateTimeField(auto_now_add=True)

   class Meta:
      unique_together = ('user', 'model')

   def __str__(self):
      return f"{self.user.username} -> {self.model.name}"



class Pack(models.Model):  # Пак, который связан с автором
   model = models.ForeignKey('Model', on_delete=models.CASCADE, related_name='packs')
   title = models.CharField(max_length=100)
   description = models.TextField(blank=True, null=True)
   tags = models.ManyToManyField(Tag, blank=True, related_name='packs')
   preview = models.ImageField(upload_to='previews', null=True)
   slug = models.SlugField(unique=True, blank=True)
   created_at = models.DateTimeField(auto_now_add=True)
   average_rating = models.FloatField(default=0)
   
   @property
   def popularity(self):
      return Rating.objects.filter(content_type=ContentType.objects.get_for_model(Pack), object_id=self.id).count()

   def update_rating(self):
      from django.contrib.contenttypes.models import ContentType
      content_type = ContentType.objects.get_for_model(self)
      ratings = Rating.objects.filter(content_type=content_type, object_id=self.id)
      self.average_rating = ratings.aggregate(Avg('score'))['score__avg'] or 0
      self.save()

   def save(self, *args, **kwargs):
      if not self.slug:
         self.slug = slugify(self.title)
      super().save(*args, **kwargs)

   def get_absolute_url(self):
      return reverse('pack_detail', kwargs={'slug': self.slug})
   
   
   class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(Lower('title').desc(), name='title_lower_idx'),
        ]

   def __str__(self):
      return self.title
   


   
   
class FavoritePack(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
   pack = models.ForeignKey('Pack', on_delete=models.CASCADE, related_name='favorited_by')
   added_at = models.DateTimeField(auto_now_add=True)

   class Meta:
      unique_together = ('user', 'pack')

   def __str__(self):
      return f"{self.user.username} добавил {self.pack.title} в избранное"



class Photo(models.Model):
   pack = models.ForeignKey(Pack, on_delete=models.CASCADE, related_name='photos', null=True)
   image = models.ImageField(upload_to='photos/', null=True)
   description = models.CharField(max_length=255, blank=True, null=True)
   uploaded_at = models.DateTimeField(auto_now_add=True)

   def __str__(self):
      return f"Фото {self.id} из пака {self.pack.title}"
   

class Video(models.Model):
   pack = models.ForeignKey(
      'Pack',
      on_delete=models.CASCADE,
      related_name='videos',
      null=True,
   )
   video = models.FileField(upload_to='videos/')
   description = models.CharField(max_length=255, blank=True, null=True)
   uploaded_at = models.DateTimeField(auto_now_add=True)
   def __str__(self):
      return f"Видео {self.id} из пака {self.pack.title}"

   

class Comment(models.Model):
   pack = models.ForeignKey(Pack, on_delete=models.CASCADE, related_name='comments')
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   text = models.TextField(verbose_name="Комментарий")
   created_at = models.DateTimeField(auto_now_add=True)

   def __str__(self):
      return f"Комментарий от {self.user.username} к {self.pack.title}"


class Rating(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
   content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
   object_id = models.PositiveIntegerField()
   content_object = GenericForeignKey('content_type', 'object_id')
   score = models.PositiveSmallIntegerField(verbose_name="Оценка", choices=[(i, str(i)) for i in range(1, 6)])
   created_at = models.DateTimeField(auto_now_add=True)

   
   def related_object(self):
      return str(self.content_object)
   related_object.short_description = 'Связанный объект'

   class Meta:
      unique_together = ('user', 'content_type', 'object_id')

   def __str__(self):
      return f"Оценка {self.score} от {self.user.username} к {self.content_object}"
   

class ContentSuggestion(models.Model):
   """Модель для предложений новых авторов и паков"""
   
   SUGGESTION_TYPE_CHOICES = [
      ('model', 'Новая модель'),
      ('pack', 'Новый пак'),
   ]

   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='suggestions')
   suggestion_type = models.CharField(max_length=10, choices=SUGGESTION_TYPE_CHOICES, null=True)

   model_name = models.CharField(max_length=100, blank=True, null=True)
   model_bio = models.TextField(blank=True, null=True)
   model_avatar = models.ImageField(upload_to='suggested_avatars/', blank=True, null=True)

   pack_title = models.CharField(max_length=100, blank=True, null=True)
   pack_description = models.TextField(blank=True, null=True)
   pack_photos = models.FileField(upload_to='suggested_packs/', blank=True, null=True)

   related_model = models.ForeignKey(Model, on_delete=models.CASCADE, blank=True, null=True, related_name="suggested_packs")

   submitted_at = models.DateTimeField(auto_now_add=True, null=True)
   is_reviewed = models.BooleanField(default=False)

   def __str__(self):
      return f"{self.get_suggestion_type_display()} от {self.user.username}"
   
   
# ПОТОМ ПОПРОБУЙ УБРАТЬ ВСЕ NULL=TRUE