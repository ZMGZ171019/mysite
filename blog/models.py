
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.core.urlresolvers import reverse


class PublishedManager(models.Manager):

	def get_queryset(self):#get_queryset()是返回执行过的查询集（QuerySet）的方法
		return super(PublishedManager,
					 self).get_queryset().filter(status='published')


class Post(models.Model):
	STATUS_CHOICES = (
		('draft', 'Draft'),
		('published', 'Published'),
	)
	title = models.CharField(max_length=250)
	slug = models.SlugField(max_length=250, unique_for_date='publish')
	author = models.ForeignKey(User, related_name='blog_posts')
	body = models.TextField()#这是帖子的主体。它是TextField，在SQL数据库中被转化成TEXT。
	publish = models.DateTimeField(default=timezone.now)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=10,
							  choices=STATUS_CHOICES,
							  default='draft')
	#这个字段表示当前帖子的展示状态。我们使用了一个choices参数，这样这个字段的值只能是给予的选择参数中的某一个值。
	#（注：传入元组，比如(1,2)，那么该字段只能选择1或者2，没有其他值可以选择）
	objects = models.Manager()
	published = PublishedManager()
	tags = TaggableManager()#这个tags管理器（manager）允许你给Post对象添加，获取以及移除标签。

	class Meta:
		ordering = ('-publish',)
		#Django查询数据库的时候默认返回的是根据publish字段进行降序排列过的结果。我们使用负号来指定进行降序排列

	def __str__(self):
		return self.title
		#str()方法是当前对象默认的可读表现

	def get_absolute_url(self):
		return reverse('blog:post_detail',
					   args=[self.publish.year,
							 self.publish.strftime('%m'),
							 self.publish.strftime('%d'),
							 self.slug])


class Comment(models.Model):
	post = models.ForeignKey(Post, related_name='comments')
	name = models.CharField(max_length=80)
	email = models.EmailField()
	body = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	active = models.BooleanField(default=True)

	class Meta:
		ordering = ('created',)

	def __str__(self):
		return 'Comment by{} on {}'.format(self.name, self.post)

