#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from apps.people.models import Follow
from apps.topic.models import Topic, Reply, Message
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import Http404, HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.utils import simplejson

def home(request, user_id):
    context = {}
    if request.method == 'POST':
        return render(request,'index.html',locals())
    people = User.objects.get(id=user_id)
    topic_list = Topic.objects.filter(author=people).order_by('-created_on')
    reply_list = Reply.objects.filter(author=people).order_by('-created_on')
    if request.user.is_authenticated(): 
        num_private_message = Message.objects.filter(belong_to=request.user,talk_to=people,is_deleted=False).count()
        context['num_private_message'] = num_private_message
    context['people'] = people
    context['topic_list'] = topic_list
    context['reply_list'] = reply_list
    return render(request,'people.html',context)

@login_required
def ajax_focus(request):
    success = False
    to_return = {}
    if request.method =='GET':
        get = request.GET.copy()
        if get.has_key('people_id'):
            people_id = get['people_id']
            try:
                user = User.objects.get(pk=people_id)
            except User.DoesNotExist:
                raise Http404
            follow = Follow.objects.create(user=request.user,follow=user)
            print follow
            to_return['result'] = True
            success=True
        else:
            to_return={'msg':u'Require keywords'}
    serialized = simplejson.dumps(to_return)
    if success:
        return HttpResponse(serialized, mimetype="application/json")
    else:
        return HttpResponseServerError(serialized, mimetype="application/json")