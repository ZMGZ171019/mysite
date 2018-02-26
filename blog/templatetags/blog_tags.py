from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

from ..models import Post

@register.simple_tag
def total_posts():
	return Post.published.count()
'''模板标签（template tags）都需要包含一个叫做register的变量来表明自己是一个有效的标签（tag）库。
	这个变量是template.Library的一个实例，它是用来注册你自己的模板标签（template tags）和过滤器（filter）的。
	我们用一个Python函数定义了一个名为total_posts的标签，并用@register.simple-tag装饰器定义此函数为一个简单标签（tag）并注册它。
	Django将会使用这个函数名作为标签名。如果你想使用别的名字来注册这个标签（tag），你可以指定装饰器的name属性，比如@register.simple_tag(name='my_tag')。
	在添加了新的模板标签（template tags）模块后，你必须重启Django开发服务才能使用新的模板标签（template tags)和过滤器（filters)。
	在使用自定义的模板标签（template tags)之前，你必须使用{% load %}标签在模板中来加载它们才能有效。
	就像之前提到的，你需要使用包含了你的模板标签（template tags)和过滤器（filter)的Python模块的名字。'''

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
	latest_posts = Post.published.order_by('-publish')[:count]
	return {'latest_posts': latest_posts}
'''通过装饰器@register.inclusion_tag注册模板标签（template tag），指定模板必须被blog/post/latest_posts.html返回的值渲染。
	我们的模板标签将会接受一个可选的count参数（默认是5）允许我们指定我们想要显示的帖子数量。
	我们使用这个变量来限制Post.published.order_by('-publish')[:count]查询的结果。
	请注意，这个函数返回了一个字典变量而不是一个简单的值。
	包含标签（inclusion tags）必须返回一个字典值，作为上下文（context）来渲染特定的模板（template）。
	包含标签返回一个字典。这个我们刚创建的模板标签可以通过传入可选的评论数量值来使用显示，类似*{% show_latest_posts 3 %}。'''

@register.assignment_tag
def get_most_commented_posts(count=5):
	return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]
'''这个查询集（QuerySet）使用annotate()函数，为了进行聚合查询，使用了Count聚合函数。
	我们构建了一个查询集，聚合了每一个帖子的评论总数并保存在total_comments字段中，接着我们通过这个字段对查询集进行排序。
	我们还提供了一个可选的count变量，通过给定的值来限制返回的帖子数量。'''

@register.filter(name='markdown')
def markdown_format(text):
	return mark_safe(markdown.markdown(text))
'''我们使用和模板标签（template tags）一样的方法来注册我们自己的模板过滤器（template filter）。
	为了避免函数名和markdown模板名起冲突，我们将函数命名为markdown_format，然后将过滤器（filter）命名为markdown，
	在模板中的使用方法类似{{ variable|markdown }}。Django会转义过滤器生成的HTML代码.
	我们使用Django提供的mark_safe方法来标记结果，在模板（template）中作为安全的HTML被渲染。
	默认的，Django不会信赖任何HTML代码并且在输出之前会进行转义。唯一的例外就是被标记为安全转义的变量。
	这样的操作可以阻止Django从输出中执行潜在的危险的HTML，并且允许你创建一些例外情况只要你知道你正在运行的是安全的HTML。'''
