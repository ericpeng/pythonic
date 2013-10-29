#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django.conf import settings
from django.conf.urls import patterns, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('apps.extra.views',
    (r'^$','index'),
    (r'^about/$','about'),
    (r'^zen/$','zen'),
    (r'^feedback/$','feedback'),
    (r'^feedback/success/$','feedback_success'),
    (r'^help/$','help_use'),
    #(r'^search/$','search'),
)

urlpatterns += patterns('',
    (r'^accounts/',include('apps.accounts.urls')),
    (r'^people/',include('apps.people.urls')),
    (r'^pypi/',include('apps.pypi.urls')),
)

# urlpatterns = patterns('',
#     url(r'^$', 'apps.main.views.homepage'),
#     url(r'^help/', include('apps.help.urls')),
#     url(r'^credit/', include(extra_patterns)),
# )

urlpatterns += patterns('apps',
    # Examples:
    # url(r'^$', 'pythonic.views.home', name='home'),
    # url(r'^pythonic/', include('pythonic.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    
    (r'^node/(\S+)/create/$','topic.views.create_topic'),
    (r'^node/(\S+)/edit/$','topic.views.node_edit'),
    (r'^node/(\S+)/choose/$','topic.views.node_choose_description'),
    (r'^node/(\S+)/$','topic.views.node'),
    
    #(r'^node/explore/$','topic.views.all'),
    (r'^apply/$','topic.views.apply_node'),
    (r'^apply/new/$','topic.views.apply_new'),
    (r'^topic/(\d+)/create/$','topic.views.create_reply'),
    (r'^topic/(\d+)/$','topic.views.topic_detail'),
    (r'^topic/$','topic.views.topic'),

    (r'^ajax_focus/$','people.views.ajax_focus'),
    (r'^cancel_focus/(\d+)/$','topic.views.cancel_focus'),
    (r'^ajax_user_match/$','topic.views.ajax_user_match'),
    (r'^notice/$','topic.views.notice'),
    (r'^notice/readed/$','topic.views.notice_readed'),
    (r'^message/$','topic.views.message'),
    (r'^ajax_message/$','topic.views.ajax_message'),
    (r'^message/new/$','topic.views.message_new'),
    (r'^message/create/$','topic.views.message_create'),
    (r'^message/history/(\d+)/$','topic.views.message_history'),
    (r'^message/reply/$','topic.views.message_reply'),
    #(r'^messages/new/$','topic.views.new_message'),
)

urlpatterns += patterns('',
    (r'^admin/', include(admin.site.urls)),       #admin中的static文件夹下的静态文件在开发环境下自动serve，生产环境下由/static请求处理
)

#以下是处理静态文件请求，由于效率和安全因素，仅限于开发环境，不能用于生产环境！！！
#在生产环境中，服务器将static、media、admin/static等请求直接转发出去，由该服务器或其它前端服务器来处理静态请求，以下所有代码将由于无法接收到请求而失效
#在生产环境中，请运行 python manage.py collectstatic 命令将admin/static、STATICFILES_DIRS和各个app下的静态文件集中放入MEDIA_ROOT（事先为空）


# if settings.DEBUG:
#     urlpatterns += patterns('',url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),)
#static函数是对上述代码的完全封装，更灵活的使用MEDIA_URL，理论上static函数也可以用于static文件的serve，但为了效率，用了另外一种views函数来serve static文件   
urlpatterns += static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT )    


# if settings.DEBUG:
#     urlpatterns += patterns('django.contrib.staticfiles.views',url(r'^static/(?P<path>.*)$', 'serve'),)
#这个helper function是对上述代码的完全封装，更灵活的使用STATIC_URL
#django.contrib.staticfiles。views.serve自动地从STATICFILES_DIRS、STATIC_ROOT以及各个app的static子目录里面搜索静态文件
urlpatterns += staticfiles_urlpatterns()







# if settings.STATIC_MEDIA_SERVER:
#     urlpatterns += patterns('',
#         (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
#             {'document_root': 'media'}),
# )