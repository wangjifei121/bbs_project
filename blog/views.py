import os

from django import views  # 写CBV视图函数时要用
from django.conf import settings
from django.contrib import auth  # 登录校验用户时要用
from django.contrib.auth.decorators import login_required
from django.db import transaction  # 点赞时，写入事务要用
from django.db.models import F  # F 查询，更新文章表的点赞记录时要用
from django.http import JsonResponse  # 给前端返回Json对象时用
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404  # 渲染页面用
from django.views.decorators.cache import never_cache  # 某些情况下，需要每次都刷新，不能使用浏览器缓存

from blog import models  # 创建用户，写进数据库的时候要用
from blog.forms import LoginForm  # 导入，之后生成页面的时候要用
from blog.forms2 import RegisterForm  # 注册时要用
from utils.mypage import MyPage  # 分页
from bs4 import BeautifulSoup  # 文章存库校验用

# 记录日志的
import logging

logger = logging.getLogger(__name__)  # 生成一个以当前文件名为名字的日志实例对象
collect_logger = logging.getLogger("collect")  # 生成一个名字是collect的日志实例对象


# 登录,用CBV写
class Login(views.View):

    def get(self, request):
        # 没有数据时只是一个空的样式
        form_obj = LoginForm()
        return render(request, 'login.html', {'form_obj': form_obj})

    def post(self, request):
        res = {'code': 0}
        # print(request.POST)
        user = request.POST.get('username')
        pwd = request.POST.get('password')
        v_code = request.POST.get('v_code')
        # 先判断验证码是否正确
        if v_code.upper() != request.session.get("v_code", ""):
            res["code"] = 1
            res["msg"] = "验证码错误"
        # 正确之后再走下一步，检验用户名密码是否正确
        else:
            user_obj = auth.authenticate(request, username=user, password=pwd)
            if user_obj:
                # 如果正确就登录
                auth.login(request, user_obj)
                logger.debug('{}登录了...'.format(user))
                logger.info('{}的登录了...'.format(user))
                collect_logger.warning("{}登录了...".format(user))
            else:
                res['code'] = 1
                res['msg'] = '用户名或密码错误'
        return JsonResponse(res)


# 给index加了个登录验证的装饰器
class Index(views.View):
    # @method_decorator(login_required)
    def get(self, request):
        print(request.user)
        print(type(request.user))
        # print(dir(request.user)) # 【查看此对象都有哪些方法属性】
        print(request.user.username, type(request.user.username))
        articles = models.Article.objects.all()
        # return render(request,'index.html',{'articles':articles})
        # 【分页】
        data_amout = articles.count()
        page_num = request.GET.get('page', 1)
        page_obj = MyPage(page_num, data_amout, per_page_data=2, url_prefix='index')
        # 按照分页的设置对总数居进行切片
        data = articles[page_obj.start:page_obj.end]
        page_html = page_obj.ret_html()
        return render(request, 'index.html', {'articles': data, 'page_html': page_html})


# 注销
def logout(request):
    auth.logout(request)
    return redirect('/index/')


# 因为前端流程改了，所以要加上这个告诉浏览器每次点击都访问服务器，不使用浏览器缓存
@never_cache
# 返回验证码图片的视图
def v_code(request):
    # 随机生成图片
    from PIL import Image, ImageDraw, ImageFont
    import random
    # 生成随机颜色的方法
    def random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    # 生成图片对象
    image_obj = Image.new(
        "RGB",  # 生成图片的模式
        (250, 35),  # 图片大小
        random_color()
    )
    # 生成一个准备写字的画笔
    draw_obj = ImageDraw.Draw(image_obj)  # 在哪里写
    font_obj = ImageFont.truetype('static/font/kumo.ttf', size=28)  # 加载本地的字体文件

    # 生成随机验证码
    tmp = []
    for i in range(5):
        n = str(random.randint(0, 9))
        l = chr(random.randint(65, 90))
        u = chr(random.randint(97, 122))
        r = random.choice([n, l, u])
        tmp.append(r)
        # 每一次取到要写的东西之后，往图片上写
        draw_obj.text(
            (i * 45 + 25, 0),  # 坐标
            r,  # 内容
            fill=random_color(),  # 颜色
            font=font_obj  # 字体
        )
    v_code = "".join(tmp)  # 得到最终的验证码
    # global V_CODE
    # V_CODE = v_code  # 保存在全局变量不行！！！
    # 将该次请求生成的验证码保存在该请求对应的session数据中
    request.session['v_code'] = v_code.upper()

    # 直接将生成的图片保存在内存中
    from io import BytesIO
    f = BytesIO()
    image_obj.save(f, "png")
    # 从内存读取图片数据
    data = f.getvalue()
    return HttpResponse(data, content_type="image/png")


# 用户名查重功能
def user(request):
    res = {'code': 0}
    username = request.POST.get('user')
    user_obj = models.UserInfo.objects.filter(username=username)
    if user_obj:
        res['code'] = 1
        res['msg'] = '该用户名已存在'
    return JsonResponse(res)


# 注册
class Register(views.View):

    def get(self, request):
        form_obj = RegisterForm()
        return render(request, 'register.html', {'form_obj': form_obj})

    def post(self, request):
        res = {'code': 0}
        v_code = request.POST.get('v_code')
        # 查看验证码是否正确
        if v_code.upper() == request.session.get('v_code'):
            print(request.POST)
            username = request.POST.get('username')
            # 查看用户名是否重复
            if not models.UserInfo.objects.filter(username=username):
                # 验证码正确，之后再接收传来的所有post数据进行实例化
                print()
                form_obj = RegisterForm(request.POST)
                print(form_obj, type(form_obj))
                if form_obj.is_valid():
                    # 删除多余的
                    form_obj.cleaned_data.pop('re_password')
                    # 提取文件需要用这种方式
                    avatar_file = request.FILES.get('avatar')
                    # 写进数据库
                    models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_file)
                    res['msg'] = '/login/'
                else:
                    # 用户填写的不符合要求
                    res['code'] = 1
                    res['msg'] = form_obj.errors  # 【拿到所有字段的错误提示信息】
            else:
                res['code'] = 3
                res['msg'] = '用户已存在'
        else:
            res['code'] = 2
            res['msg'] = '验证码错误'
        return JsonResponse(res)


def home(request, username, *args):
    print(args)
    print(username)
    user_obj = get_object_or_404(models.UserInfo, username=username)
    blog = user_obj.blog
    article_list = models.Article.objects.filter(user=user_obj)
    if args:
        if args[0] == "category":
            # 表示按照文章分类查询
            article_list = article_list.filter(category__title=args[1])
            print(article_list)
        elif args[0] == "tag":
            # 表示按照文章的标签查询
            article_list = article_list.filter(tags__title=args[1])
            print(article_list)
        else:
            # 表示按照文章的日期归档查询
            try:
                year, month = args[1].split("-")
                article_list = article_list.filter(create_time__year=year, create_time__month=month)
                print(article_list)
            except Exception as e:
                article_list = []

    return render(request, 'home1.html', {
        'username': username,
        'article_list': article_list,
        'blog': blog,
    })


#  【如何去重，见views/ article2.html/ home2.html/ base.html/ my_tag.py/ left_menu.html,】


# 文章详情
def article(request, username, id):
    '''
    :param request: 请求对象
    :param username: 用户名
    :param id: 主键
    :return:
    '''
    article_obj = models.Article.objects.filter(id=id).first()  # 找到点击的文章
    user_obj = get_object_or_404(models.UserInfo, username=username)
    blog = user_obj.blog
    comment_list = models.Comment.objects.filter(article_id=id)

    return render(request, 'article1.html', {
        'article': article_obj,
        'username': username,
        'blog': blog,
        'comments': comment_list,
    })


# 处理点赞的
def up_down(request):
    if request.method == 'POST':
        res = {'code': 0}  # 【初始状态，code为0，经过一段处理之后，如果还是0，表示点赞或反对成功】
        user_id = request.POST.get('userid')
        article_id = request.POST.get('articleid')
        isup = request.POST.get('isup')  # 得到的永远是一个字符串
        is_up = True if isup.upper() == 'TRUE' else False  # （三元运算）将前面传过来的字符串进行判断，转化为布尔值
        print(request.POST)
        # 【2】看看点赞的用户，的id是不是文章的作者的id，如果能查到就证明这篇文章就是这个人写的，限制不能给自己点赞
        article_obj = models.Article.objects.filter(id=article_id, user_id=user_id)
        print(article_obj)
        if article_obj:
            res['code'] = 1  # 【失败code为1】
            res['msg'] = '不能给自己的文章点赞！' if is_up else '不能反对自己的内容！'
            return JsonResponse(res)

        # 【3】看看该用户在此文章有没有点赞记录，如果有查出是'点赞过'还是'反对过'，动态地返回给前端。
        is_exist = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
        # 如果存在，表示已经有过记录。
        if is_exist:
            res['code'] = 1  # 【失败code为1】
            res['msg'] = '已经点过赞' if is_exist.is_up == True else '已经反对过'
        else:
            # 【4】可以点赞了,将用户的点赞写进数据库对应的表中
            # 事务操作，先更新点赞表，再更新文章表
            with transaction.atomic():
                # 先创建点赞记录
                models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
                # 在更新文章表，更新哪个字段。
                if is_up:
                    # 更新点赞数
                    models.Article.objects.filter(id=article_id).update(up_count=F('up_count') + 1)
                else:
                    # 更新反对数
                    models.Article.objects.filter(id=article_id).update(down_count=F('down_count') + 1)
            res['msg'] = '点赞成功' if is_up else '反对成功'

        return JsonResponse(res)


# 处理评论的
def comment(request):
    if request.method == 'POST':
        res = {'code': 0}
        user_id = request.POST.get('user_id')
        article_id = request.POST.get('article_id')
        comment_content = request.POST.get('content')
        parent_id = request.POST.get('parentid')  # 后添加的，用于区分是不是子评论
        print(user_id, article_id, comment_content)
        print(parent_id)
        with transaction.atomic():  # 事务操作
            # 1，创建新评论
            if parent_id:
                # 添加子评论
                comment_obj = models.Comment.objects.create(content=comment_content, user_id=user_id,
                                                            article_id=article_id,
                                                            parent_comment_id=parent_id)
            else:
                # 添加父评论
                comment_obj = models.Comment.objects.create(content=comment_content, user_id=user_id,
                                                            article_id=article_id)
            # 2，更新评论数
            models.Article.objects.filter(id=article_id).update(comment_count=F('comment_count') + 1)
            res['data'] = {
                'id': comment_obj.id,
                'create_time': comment_obj.create_time.strftime('%Y-%m-%d %H:%M'),
                'username': request.user.username
            }
        return JsonResponse(res)


@login_required
# 个人后台
def myself(request):
    # 获取当前用户的所有文章
    article_list = models.Article.objects.filter(user=request.user)
    username = request.user.username
    return render(request, 'backend.html', {'article_list': article_list, 'username': username})


@login_required
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        # 清洗用户发部的文章内容，去掉script标签
        soup = BeautifulSoup(content, 'html.parser')  # 以这个检验方法，以那个校验规则，校验这个内容，得出结果
        script_list = soup.select('script')
        for i in script_list:
            i.decompose()
        # 事务操作，写入数据库
        with transaction.atomic():
            article_obj = models.Article.objects.create(
                title=title,
                desc=soup.text[0:150],
                user=request.user,
                category_id=category_id
            )
            models.ArticleDetail.objects.create(
                content=soup.prettify(),
                article=article_obj
            )
        print(soup.text[0:150])
        return redirect('/myself/')
    # 查询该博客站点的文章分类
    blog = request.user.blog
    category_list = models.Category.objects.filter(blog=blog)
    return render(request, 'add_article.html', {'category_list': category_list})


# 富文本编辑器的图片上传
def upload(request):
    res = {'error': 0}  # 本富文本插件返回响应的时候接收的格式error
    print(request.FILES)
    file_obj = request.FILES.get('imgFile')  # 本插件的文件中的属性
    file_path = os.path.join(settings.MEDIA_ROOT, "article_imgs", file_obj.name)
    with open(file_path, 'wb')as f:
        for chunk in file_obj.chunks():
            f.write(chunk)
    url = '/media/article_imgs/' + file_obj.name
    res['url'] = url  # 前端需要路径
    return JsonResponse(res)

# 后端的操作，将前端的图片接收保存在本地文件夹，形成一个文件夹路径，返回给前端，前端访问路径，可显示图片
