from django.contrib import admin
from .models import Post, Comment

class PostAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug', 'author', 'publish', 'status')#页面中展示的字段都是你在list-dispaly属性中指定
	list_filter = ('status', 'created', 'publish', 'author')#右侧边栏根据list_filter属性中指定的字段来过滤返回结果
	search_fields = ('title', 'body')#通过使用search_fields属性定义了一个搜索字段列(搜索框)
	prepopulated_fields = {'slug':('title',)}#通过使用prepopulated_fields属性告诉Django通过输入的标题(title)来填充slug字段
	raw_id_fields = ('author',)#author字段展示显示为了一个搜索控件，这样当你的用户量达到成千上万级别的时候比再使用下拉框进行选择更加的人性化
	date_hierarchy = 'publish'#可以通过时间层快速导航的栏，该栏通过定义date_hierarchy属性实现
	ordering = ['status', 'publish']#帖子默认通过Status和Publish列进行排序 因为通过使用ordering属性指定了默认排序
admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'post', 'created', 'active')
	list_filter = ('active', 'created', 'updated')
	search_fields = ('name', 'email', 'body')
admin.site.register(Comment, CommentAdmin)
