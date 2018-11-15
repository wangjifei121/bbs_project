"""bbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from blog import views
from django.views.static import serve
from django.conf import settings
from blog import urls as blog_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # 用了CBV 【第一天】
    url(r'^login/$',views.Login.as_view()),
    url(r'^logout/$',views.logout),
    url(r'^v-code/$',views.v_code),
    #   【第二天】
    url(r'^register/$',views.Register.as_view()),
    # 给用户上传文件，配置一个处理的路由
    url(r'^media/(?P<path>.*)',serve,{'document_root':settings.MEDIA_ROOT}),
    #   【第三天】
    url(r'^index/$',views.Index.as_view()),
    #   【第四天】
    # 二级路由
    url(r'^blog/',include(blog_urls)),
    #   【第五天】
    # 初始页面就是index
    url(r'^$',views.Index.as_view()),
    # 处理点赞的url
    url(r'^Up_Down/$',views.up_down),
    #   【第六天】改进注册的用户名去重
    url(r'^user/$',views.user),
    url(r'comment/$',views.comment),
    #  【第七天】
    url(r'^myself/$',views.myself),


]



# =============↓显示面板的↓==============
from django.conf import settings
from django.conf.urls import include, url

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns