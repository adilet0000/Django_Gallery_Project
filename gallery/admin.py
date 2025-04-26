from django.contrib import admin
from .models import Model, Pack, Photo, Tag, Comment, Rating, ContentSuggestion, Subscription, Video

@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
   list_display = ('name',)
   search_fields = ('name', 'bio')
   filter_horizontal = ('tags',)


@admin.register(Pack)
class PackAdmin(admin.ModelAdmin):
   list_display = ('title', 'model', 'created_at')
   search_fields = ('title', 'description')
   filter_horizontal = ('tags',)

admin.site.register(Tag)
admin.site.register(Video)
admin.site.register(Subscription)

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
   list_display = ('id', 'pack', 'description')
   list_filter = ('pack',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
   list_display = ('pack', 'user', 'text')
   search_fields = ('pack', 'user')

class RatingAdmin(admin.ModelAdmin):
   list_display = ('user', 'related_object', 'score', 'created_at')
   list_filter = ('score', 'created_at')
   search_fields = ('user__username',)

admin.site.register(Rating, RatingAdmin)

@admin.register(ContentSuggestion)
class ContentSuggestionAdmin(admin.ModelAdmin):
   list_display = ('model_name', 'user', 'submitted_at', 'is_reviewed')
   list_filter = ('is_reviewed',)
   search_fields = ('model_name', 'user__username')

