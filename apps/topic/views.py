#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from apps.accounts.function import QuerySetEncoder
from apps.accounts.models import UserProfile
from apps.topic.forms import TopicForm, ReplyForm, MessageForm, ApplyForm, \
    MessageReply, NodeEditForm
from apps.topic.models import Topic, Node, Reply, Message, Notice, Description
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse, \
    HttpResponseServerError, Http404
from django.shortcuts import render
from django.template import context
from django.utils import simplejson
import datetime
import re
import time

def topic(request):
    context = {}
    context['topics'] = Topic.objects.all().order_by('-updated_on')[:10]
    context['nodes'] = Node.objects.all()[:10]
    if request.user.is_authenticated():
        node_list = request.user.node_set.all().order_by('?')[:8]
        context['node_list'] = node_list
    else:
        recommend_list = Node.objects.all().order_by('?')[:8]
        context['recommend_list'] = recommend_list
    print context
    return render(request,'topic.html',context)

def node(request, node_slug):
    context = {}
    try:
        node = Node.objects.get(slug=node_slug)
    except Node.DoesNotExist:
        raise Http404
    context['node'] = node
    description = Description.objects.filter(node=node,active=True)
    if description:
        description = description[0]
    else:
        description = None
    context['description'] = description
    context['topics'] = Topic.objects.filter(node=node).order_by('-updated_on')
    context['form'] = TopicForm()
    return render(request,'node.html',context)

def node_edit(request,node_slug):
    context = {}
    try:
        node = Node.objects.get(slug=node_slug)
    except Node.DoesNotExist:
        raise Http404
    if request.method == 'GET':
        description = Description.objects.filter(node=node).order_by('-time')
        context['node'] = node
        context['description'] = description
        context['form'] = NodeEditForm()
        return render(request,'node_edit.html',context)
    
    form = NodeEditForm(request.POST)
    if form.is_valid():
        content = form.cleaned_data['content']
        Description.objects.filter(node=node).update(active=False)
        Description.objects.create(content=content,author=request.user,node=node,active=True)
    return HttpResponseRedirect('/node/'+node_slug+"/")

def node_choose_description(request,node_slug):
    if request.method == 'GET':
        return HttpResponseRedirect('/node/'+node_slug+"/")
    try:
        node = Node.objects.get(slug=node_slug)
    except Node.DoesNotExist:
        raise Http404
    description_id = request.POST['description_id']    
    try:
        description = Description.objects.get(id=description_id)
    except Description.DoesNotExist:
        raise Http404
    if description.node == node:
        Description.objects.filter(node=node).update(active=False)
        description.active = True
        description.save()
    else:
        raise Http404
    return HttpResponseRedirect('/node/'+node_slug+"/")

def explore(request):
    context = {}
    
    return render(request,'explore.html',context)

def apply_node(request):
    if request.method == 'GET':
        return render(request,'apply.html')

def apply_new(request):
    context = {}
    if request.method == 'GET':
        form = ApplyForm()
        context['form'] = form
        print form
        return render(request,'apply_new.html',context)
    form = ApplyForm(request.POST)
    if form.is_valid():
        node = form.save(commit=False)
        node.author = request.user
        node.num_views = 0
        node.num_replies = 0
        node.updated_on = datetime.datetime.now()
        node.save()
    return render(request,'apply_success.html',context)

def create_topic(request, node_slug):
    if request.method == 'POST':
        try:
            node = Node.objects.get(slug=node_slug)
        except Node.DoesNotExist:
            raise Http404
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.node = node
            print request.user
            topic.author = request.user
            topic.num_views = 0
            topic.num_replies = 0
            topic.updated_on = datetime.datetime.now()
            topic.save()
            node.num_topics += 1
            node.save()
            
    return HttpResponseRedirect('/node/'+node_slug+"/")

def create_reply(request, topic_id):
    if request.method == 'POST':
        parent_id = request.POST['parent_id']
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.topic = Topic.objects.get(id=topic_id)
            reply.topic.num_replies += 1
            reply.topic.updated_on = datetime.datetime.now()
            reply.topic.last_reply = request.user
            reply.topic.save()
            if parent_id != '':
                reply.has_parent = True
                reply.parent = Reply.objects.get(pk=parent_id)
            reply.created_on = datetime.datetime.now()
            reply.save()
    return HttpResponseRedirect('/topic/'+topic_id+"/")

def topic_detail(request, topic_id):
    context = {}
    topic = Topic.objects.get(id=topic_id)
    context['topic'] = topic
    context['reply_list'] = Reply.objects.filter(topic=topic_id)
    context['form'] = ReplyForm()
    #print context
    return render(request,'topic_detail.html',context)

def cancel_focus(request, node_id):
    if request.method =='GET':
        node = Node.objects.get(pk=node_id)
        node.users.remove(request.user)
    return HttpResponseRedirect('/node/'+node_id+"/")

@login_required
def notice(request):
    context = {}
    if request.method == 'GET':
        notice_list = Notice.objects.filter(recipient=request.user).order_by('-time')
        num_notice = notice_list.filter(is_readed=False).count()
        talk_list = Message.objects.filter(belong_to=request.user).values('talk_to').distinct()
        num_message = 0
        if talk_list: 
            for item in talk_list:
                num = Message.objects.filter(is_sender=False,belong_to=request.user,talk_to=item['talk_to'],is_readed=False,is_deleted=False).count()
                num_message += num
        context['num_notice'] = num_notice
        context['num_message'] = num_message
        context['notice_list'] = notice_list
        return render(request,'notice.html',context)

@login_required
def notice_readed(request):
    if request.method == 'GET':
        Notice.objects.filter(recipient=request.user,is_readed=False).update(is_readed=True)
        return HttpResponseRedirect('/notice/')
    
@login_required
def message(request):
    if request.method =='GET':
        context = {}
        num_notice = Notice.objects.filter(recipient=request.user,is_readed=False).count()
        talk_list = Message.objects.filter(belong_to=request.user).values('talk_to').distinct()
        msg_list = []
        num_message = 0
        if talk_list: 
            for item in talk_list:
                message = Message.objects.filter(belong_to=request.user,talk_to=item['talk_to'],is_deleted=False).order_by('-time')[0]
                num = Message.objects.filter(is_sender=False,belong_to=request.user,talk_to=item['talk_to'],is_readed=False,is_deleted=False).count()
                num_message += num
                item = {}
                item['message'] = message
                item['number'] = num
                msg_list.append(item)
        context['num_notice'] = num_notice
        context['num_message'] = num_message
        context['msg_list'] = sorted(msg_list, key=lambda x:x['message'].time, reverse=True)
        return render(request,'message.html',context)
    
@login_required
def message_new(request):
    if request.method =='GET':
        context = {}
        num_notice = Notice.objects.filter(recipient=request.user,is_readed=False).count()
        talk_list = Message.objects.filter(belong_to=request.user).values('talk_to').distinct()
        num_message = 0
        if talk_list: 
            for item in talk_list:
                num = Message.objects.filter(is_sender=False,belong_to=request.user,talk_to=item['talk_to'],is_readed=False,is_deleted=False).count()
                num_message += num
        context['num_notice'] = num_notice
        context['num_message'] = num_message
        form = MessageForm()
        context['form'] = form
        return render(request,'message_new.html',context)

@login_required
def message_create(request):
    if request.method =='POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            talk_to_name = form.cleaned_data['recipient']
            content = form.cleaned_data['content']
            print 'content',len(content)
            try:
                talk_to_profile = UserProfile.objects.get(name=talk_to_name)
            except UserProfile.DoesNotExist:
                messages.error(request,'该用户不存在')
                pass
            else:
                talk_to = talk_to_profile.user
                sender = request.user
                if sender.id == talk_to.id:
                    messages.error(request,'不能发私信给自己')
                    return HttpResponseRedirect('/message/new/')
                else:
                    time = datetime.datetime.now()
                    Message.objects.create(is_sender=True,talk_to=talk_to,belong_to=request.user,content=content,time=time,is_readed=True)
                    Message.objects.create(is_sender=False,talk_to=request.user,belong_to=talk_to,content=content,time=time)
        else:
            return render(request,'message_new.html',locals())
    return HttpResponseRedirect('/message/')

@login_required
def message_history(request,talk_to):
    context = {}
    print request.method
    if request.method =='GET':
        Message.objects.filter(is_sender=False,talk_to=talk_to,belong_to=request.user,is_readed=False,is_deleted=False).update(is_readed=True) 
        msg_list = Message.objects.filter(belong_to=request.user,talk_to=talk_to,is_deleted=False).order_by('-time')[:5]
        #msg_list = msg_list_s.reverse()
        print msg_list
        context['form'] = MessageReply()
        context['msg_list'] = msg_list
        try:
            talk_to = User.objects.get(pk=talk_to)
        except:
            talk_to = None
        context['talk_to'] = talk_to
        return render(request,'history.html',context)

@login_required
def ajax_message(request):
    success = False
    to_return = {'msg':u'No GET data sent.'}
    if request.method =='GET':
        num = request.GET['num_message']
        end = int(num) + 10
        talk_to = request.GET['to_message']
        #talk_to = User.objects.get(id=talk_to_id)
        msg_list = Message.objects.filter(belong_to=request.user,talk_to=talk_to,is_deleted=False).order_by('-time')[num:end]
        msgs = []
        for item in msg_list:
            msg = {}
            msg['id'] = item.id
            msg['is_sender'] = item.is_sender
            msg['belong_to'] = item.belong_to.id
            msg['belong_to_avatar'] = item.belong_to.get_profile().avatar
            msg['talk_to'] = item.talk_to.id
            msg['talk_to_avatar'] = item.talk_to.get_profile().avatar
            msg['content'] = item.content
            msg['time'] = 'aaa'
            msgs.append(msg)
        to_return['msgs'] = msgs
        to_return['end'] = end
        success = True
    print msg_list
    #serialized = serializers.serialize("json",msg_list,ensure_ascii=False) #, fields=('foo','bar')
    serialized = simplejson.dumps(to_return)
    if success == True:
        print serialized
        return HttpResponse(serialized, mimetype="application/json")
    else:
        return HttpResponseServerError(serialized, mimetype="application/json")

#         Message.objects.filter(is_sender=False,talk_to=talk_to,belong_to=request.user,is_readed=False,is_deleted=False).update(is_readed=True) 
#         msg_list = Message.objects.filter(belong_to=request.user,talk_to=talk_to,is_deleted=False).order_by('-time')[:5]
#         context['form'] = MessageReply()
#         context['msg_list'] = msg_list
#         try:
#             talk_to = User.objects.get(pk=talk_to)
#         except:
#             talk_to = None
#         context['talk_to'] = talk_to
#        return render(request,'history.html',context)
  
@login_required
def message_reply(request):
    if request.method =='POST':
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/')
        form = MessageReply(request.POST)
        talk_to = request.POST['talk_to']
        if form.is_valid():
            
            content = form.cleaned_data['content']
            try:
                talk_to = User.objects.get(pk=talk_to)
            except User.DoesNotExist:
                messages.error(request,'该用户不存在或已注销')
                pass
            else:
                time = datetime.datetime.now()
                Message.objects.create(is_sender=True,talk_to=talk_to,belong_to=request.user,content=content,time=time,is_readed=True)
                Message.objects.create(is_sender=False,talk_to=request.user,belong_to=talk_to,content=content,time=time)
            return HttpResponseRedirect('/message/history/'+str(talk_to.id)+'/')
        else:
            Message.objects.filter(is_sender=False,talk_to=talk_to,belong_to=request.user,is_readed=False,is_deleted=False).update(is_readed=True) 
            msg_list = Message.objects.filter(belong_to=request.user,talk_to=talk_to,is_deleted=False).order_by('time')[:20]
            try:
                talk_to = User.objects.get(pk=talk_to)
            except:
                talk_to = None
            return render(request,'history.html',locals())
    return HttpResponseRedirect('/')

def ajax_user_match(request):
    success = False
    to_return = {'msg':u'No POST data sent.' }
    if request.method == "GET":
        get = request.GET.copy()
        if get.has_key('q'):
            q = get['q'].strip()
            qs = re.split(r'\s+',q)
            print qs
            match_list = []
            profiles = UserProfile.objects
            for item in qs:
                profiles = profiles.filter(name__icontains=item)
            profiles = profiles[0:10]
            print profiles
            if profiles:
                for item in profiles:
                    user = {}
                    user['avatar'] = item.avatar
                    user['name'] = item.name
                    user['signature'] = item.signature
                    match_list.append(user)        
            to_return["match"] = match_list
            print to_return
            success = True
        else:
            to_return['msg'] = u"Require keywords"
    serialized = simplejson.dumps(to_return)
    if success == True:
        return HttpResponse(serialized, mimetype="application/json")
    else:
        return HttpResponseServerError(serialized, mimetype="application/json")