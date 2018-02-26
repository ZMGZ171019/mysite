from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.db.models import Count
from .forms import EmailPostForm, CommentForm, SearchForm
from taggit.models import Tag
from haystack.query import SearchQuerySet

def post_list(request, tag_slug=None):
	'''post_list视图将request对象作为参数。所有的的视图都需要这个参数.另有一个可选的tag_slug参数，默认是一个None值。这个参数会带进URL中.'''
	object_list = Post.published.all()#这个视图中，通过使用之前创建的published管理器,获取到了所有状态为已发布的帖子
	tag = None

	if tag_slug:
		tag = get_object_or_404(Tag, slug=tag_slug)#取回所有发布状态的帖子，假如给予标签slug，我们通过get_object_or_404()用给定的slug来获取标签对象.
		object_list = object_list.filter(tags__in=[tag])
	
	paginator = Paginator(object_list, 3)#每页3帖子
	page = request.GET.get('page')
	try:
		posts = paginator.page(page)
	except PageNotAnInteger:
		#如果页面不是整数，则传递第一个页面
		posts = paginator.page(1)
	except EmptyPage:
		#如果页面超出了范围，交付结果的最后一页
		posts = Paginator.page(paginator.num_pages)
	return render(request,#使用Django提供的快捷方法render()通过给予的模板（template）来渲染帖子列。这个函数将request对象作为参数,模板路径以及变量来渲染的给予的模板
				  'blog/post/list.html',
				  {'page': page,#返回一个渲染文本（一般是HTML代码）HttpResponse对象。render()方法考虑到了请求内容，这样任何模板内容处理器设置的变量都可以带入给予的模板中。
				   'posts': posts,
				  'tag': tag})


class PostListView(ListView):
	queryset = Post.published.all()
	context_object_name = 'posts'
	paginate_by = 3
	template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
	'''这个视图使用year，month，day以及post作为参数通过给予slug和日期来获取到一篇已经发布的帖子,注意，当我们创建Post模型时，我们给slgu字段添加了unique_for_date参数。
	这样可以确保在给予的日期中只有一个帖子会带有一个slug，因此，能通过日期和slug取回单独的帖子'''
	post = get_object_or_404(Post, slug=post,#通过使用get_object_or_404()快捷方法来检索期望的Post。这个函数能取回匹配给予的参数的对象，或者当没有匹配的对象时返回一个404异常。
							 status='published',#状态为已发表
							 publish__year=year,
							 publish__month=month,
							 publish__day=day)
	comments = post.comments.filter(active=True)
	new_comment = None

	if request.method == 'POST':
		comment_form = CommentForm(data=requset.POST)
		if comment_form.is_valid():
			new_comment = comment_form.save(commit=False)
			new_comment.post = post
			new_comment.save()
	else:
		comment_form = CommentForm()
	
	post_tags_ids = post.tags.values_list('id', flat=True)
	'''取回了一个包含当前帖子所有标签的ID的Python列表。values_list() 查询集返回包含给定的字段值的元祖。
	我们传给元祖flat=True来获取一个简单的列表类似[1,2,3,...]。'''
	similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)#获取所有包含这些标签的帖子排除了当前的帖子
	similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
	'''使用Count聚合函数来生成一个计算字段same_tags，该字段包含与查询到的所有 标签共享的标签数量。
	通过共享的标签数量来排序（降序）结果并且通过publish字段来挑选拥有相同共享标签数量的帖子中的最近的一篇帖子。
	我们对返回的结果进行切片只保留最前面的4篇帖子。'''
	return render(request,#使用render()快捷方法来使用一个模板去渲染取回的帖子
				  'blog/post/detail.html',
				  {'post': post,
				  'comments': comments,
				  'new_comment': new_comment,
				  'comment_form': comment_form,
				  'similar_posts': similar_posts})


def post_share(request, post_id):
	post = get_object_or_404(Post, id=post_id, status='published')
	sent = False
	cd = None
	if request.method == 'POST':
		form = EmailPostForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			post_url = request.build_absolute_url(
				post.get_absolute_url())
			'''通过使用post.get_absolute_url()方法来获取到帖子的绝对路径,
				将这个绝对路径作为request.build_absolute_uri()的输入值来构建一个完整的包含了HTTP schema和主机名的url,
				通过使用验证过的表单数据来构建email的主题和消息内容并最终给表单to字段中包含的所有email地址发送email'''
			subject = '{}({})recommends you reading "{}"'.format(cd['name'],cd['email'], post.title)
			message = 'read "{} at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
			send_mail(subject, message, 'admin@myblog.com',[cd['to']])
			sent = True
		else:
			form = EmailPostForm()
		return render(request, 'blog/post/share.html',
					  {'post': post,
					   'form': form,
					   'sent': sent,
					   'cd': cd})


def post_search(request):
	form = SearchForm()
	if 'query' in request.GET:
		form = SearchForm(request.GET)
		if form.is_valid():
			cd = form.cleaned_data
			results = SearchQuerySet().models(Post).filter(content=cd['query']).load_all()
			total_results = results.count()

		return render(request, 'blog/post/search.html',
					  {'form': form,
					   'cd': cd,
					   'results': results,
					   'total_results': total_results})
	return render(request,'blog/post/search.html',{'form':form})


