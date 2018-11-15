from django import template
from blog import models
from django.db.models import Count
from django.shortcuts import  get_object_or_404


register = template.Library()

@register.inclusion_tag(filename='left_menu.html')
def left_menu(username):
    user_obj = get_object_or_404(models.UserInfo, username=username)
    # 【查找当前用户关联的blog对象】
    blog = user_obj.blog
    # 【查找当前blog对应的文章分类有哪些】
    category_list = models.Category.objects.filter(blog=blog).order_by('id')
    # 【找到当前blog对应的文章标签有哪些】
    tag_list = models.Tag.objects.filter(blog=blog)
    # 【查找当前用户写的所有文章】
    article_list = models.Article.objects.filter(user=user_obj)
    # 【日期归档，额外执行sql语句】
    archive_list = models.Article.objects.filter(user=user_obj).extra(
        select={"y_m": "DATE_FORMAT(create_time,'%%Y-%%m')"}  # 查出满足日期格式的queryset对象，
    ).values('y_m').annotate(c=Count('id')).values('y_m', 'c')  # 拿日期字段，按日期进行分组，计数，后面要用，所以前面起别名。
    # 【执行整句sql语句】
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute(
        """select c.shuliang,blog_category.title from (select count(1) as shuliang, category_id from blog_article where user_id = {} group by category_id order by id)as c inner join blog_category on c.category_id=blog_category.id;""".format(
            user_obj.id))
    cou = cursor.fetchall()

    return {
        'username': username,
        'blog': blog,
        'category_list': category_list,
        'tag_list': tag_list,
        'archive_list': archive_list,
        'count': cou,
    }