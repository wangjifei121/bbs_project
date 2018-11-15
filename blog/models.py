# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

'''
为什么要建表：
    把所有属于一类的东西放在一张表里，然后用表和表关联的方式将许多表联系起来，方便查询，排放到网页上。

就相当于，所有人写的文章都放在文章表里，这一大堆都是文章，我写的文章标上我的记号，关联起来，
要不然别人问的时候，你写了多少文章，写了哪些文章，没法查，乱糟糟一大堆也没个记号，也没个证据，
设计关联就是查询的时候方便查询，并且将文章归属于某个人。
'''


class UserInfo(AbstractUser):  # 用户表，扩展了django内置的auth_user表
    '''
    【用户信息表：用户名‘叫啥’，‘用户密码’是什么，‘手机号’是多少，用的是‘哪个博客站点’】
    '''
    phone = models.CharField(max_length=11, null=True, unique=True, verbose_name='手机号')  # 手机号
    avatar = models.FileField(upload_to='avatars/', default='avatars/default.png', verbose_name='头像')  # 头像

    blog = models.OneToOneField(to='Blog', null=True)  # 一个用户对应一个博客站点

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name


class Blog(models.Model):
    '''
    【博客站点信息：这个博客站点的‘标题’是什么，‘主题’是什么，（已经被userinfo关联）】
    '''
    title = models.CharField(max_length=64, verbose_name='标题')  # 个人博客标题
    theme = models.CharField(max_length=64, verbose_name='主题')  # 博客主题

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '博客'
        verbose_name_plural = verbose_name


class Category(models.Model):
    '''
    【个人博客文章分类：‘哪一个’站点有‘哪些’分类，分类‘标题’叫什么】
    '''
    title = models.CharField(max_length=32, verbose_name='标题')  # 分类标题
    blog = models.ForeignKey(to='Blog', verbose_name='博客')  # 外键关联博客，一个博客站点可以有多个分类【外键设置在多对一的夺得一方，方便查询】

    def __str__(self):
        return '{}-{}'.format(self.blog.title, self.title)

    class Meta:
        verbose_name = '文章分类'
        verbose_name_plural = verbose_name


class Tag(models.Model):
    '''
    【标签：‘哪个’博客站点，有‘哪些’标签】
    '''
    title = models.CharField(max_length=32, verbose_name='标签名')  # 标签名
    blog = models.ForeignKey(to='Blog', verbose_name='所属博客')  # 所属博客

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name
        unique_together = (('title', 'blog'),)


class Article(models.Model):
    '''
    【文章：‘谁’写的，文章‘标题’是什么，文章‘描述’是什么，‘什么时候’创建的，属于‘什么分类’，有‘哪些标签’】
    '''
    title = models.CharField(max_length=50)  # 文章标题
    desc = models.CharField(max_length=255, verbose_name='文章描述')  # 文章描述
    create_time = models.DateTimeField(auto_now_add=True)  # 创建时间
    category = models.ForeignKey(to='Category', null=True, verbose_name='文章分类')  # 文章分类
    user = models.ForeignKey(to='UserInfo', verbose_name='作者')  # 作者（一个作者可以写多个文章，一篇文章只能是一个作者，文章---》作者，多对一）
    tags = models.ManyToManyField(  # 文章的标签，一个标签可以给多个文章贴，一篇文章也可贴多个标签
        to='Tag',  # 对哪个表设置多对多的字段
        through='Article2Tag',  # 用哪个表（自己建的表）
        through_fields=('article', 'tag'),  # 有前后顺序
        #  【以上是多对多字段的属性，使用自定义第三张表作为多对多的第三张表】
    )

    # 评论数
    comment_count = models.IntegerField(default=0)
    # 点赞数
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    # 查的次数远大于写的次数，查的时候方便，压力小，写的时候用事务，也可以这样设计



    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name


class ArticleDetail(models.Model):
    '''
    【文章详情表：文章‘标题’是什么，‘内容’是什么】
    '''
    content = models.TextField(verbose_name='文章内容')  # 文章内容
    article = models.OneToOneField(to='Article', verbose_name='文章标题')

    class Meta:
        verbose_name = '文章详情'
        verbose_name_plural = verbose_name


class Article2Tag(models.Model):
    '''
    【文章和标签的多对多关系表：自定义的文章和标签多对多的第三张表】
    '''
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')

    def __str__(self):
        return '{}-{}'.format(self.article, self.tag)

    class Meta:
        unique_together = (('article', 'tag'),)  # 文章和标签在这个表中必须联合唯一，比如1-1，1-2，1-3，2-1，2-1，之后不能再有1-1，重复无效
        verbose_name = '文章-标签'
        verbose_name_plural = verbose_name


class ArticleUpDown(models.Model):
    '''
    【点赞表：‘谁’对‘哪篇文章’发表态度，是‘点赞’还是‘踩灭’】
    '''
    user = models.ForeignKey(to='UserInfo', null=True)  # 哪个用户
    article = models.ForeignKey(to='Article', null=True)  # 对哪个文章点赞
    is_up = models.BooleanField(default=True)  # 点赞还是踩灭

    def __str__(self):
        return '{}-{}'.format(self.user_id, self.article_id)

    class Meta:
        unique_together = (('article', 'user'),)  # 同一个人只能给一篇文章点赞，用户和文章在点在的表里，联合唯一。
        verbose_name = '点赞'
        verbose_name_plural = verbose_name


class Comment(models.Model):
    '''
    【评论表：‘谁’对‘什么内容’，写了‘什么评论’，‘父评论’是什么】
    '''
    article = models.ForeignKey(to='Article', null=True, blank=True)  # 设置外键的时候，会自动在表中加上 _id 字段，所以外键写字段的时候不用写id
    user = models.ForeignKey(to='UserInfo')
    content = models.CharField(max_length=255)  # 评论内容
    create_time = models.DateTimeField(auto_now_add=True)

    parent_comment = models.ForeignKey('self', null=True, blank=True)  # 自己关联自己，父评论可以为空，证明是跟评论。

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name


'''
ORM对应的类里面包含一个Meta类，而Meta类封装了一些数据库的信息，主要字段如下：

db_table:ORM在数据库中的表名默认是app_类名，可通过db_table重写表名。

index_together:联合索引。

unique_together:联合唯一索引。

ordering:指定默认按什么字段排序。
'''
