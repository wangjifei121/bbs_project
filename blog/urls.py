from django.conf.urls import url
from blog import views

urlpatterns = [
    # 添加文章【前端用富文本的插件，后端用beautifulsoup4模块】
    url(r'^add_article/$',views.add_article),
    url(r'^upload/$',views.upload),
    # index点击名字，跳转到个人主页
    url(r'^(\w+)/$',views.home),
    # 个人主页点击分类，跳转到分类的个人主页
    url(r'^(\w+)/(category|tag|archive)/(.*)/$', views.home),
    # 点击标题显示文章内容【第五天】
    url(r'^(\w+)/p/(\d+)',views.article),  # 意思是谁的id为几的哪一篇文章

]