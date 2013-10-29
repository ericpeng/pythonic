#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from apps.topic import widgets
from django.contrib.admin import widgets as admin_widgets
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

class MarkDownField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {'widget': widgets.MarkDownInput}
        defaults.update(kwargs)
        
        if defaults['widget'] == admin_widgets.AdminTextareaWidget:
            defaults['widget'] = widgets.AdminMarkDownInput
        
        return super(MarkDownField, self).formfield(**defaults)

#节点：节点名称，节点英文slug，节点描述，创建时间，最后更新时间，话题数目
class ParentNode(models.Model):
    name = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name
       
#节点：节点名称，节点英文slug，节点描述，创建时间，最后更新时间，话题数目
class Node(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    #pic = models.ImageField(upload_to='pic/',default='pic/default.jpg')
    #description = models.TextField(default='')
    #description = models.ForeignKey(Description,null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(blank=True, null=True)
    num_topics = models.IntegerField(default=0)
    category = models.ForeignKey(ParentNode)
    #users = models.ManyToManyField(User)

    def __unicode__(self):
        return self.name
    
#节点描述：内容，作者，节点，时间
class Description(models.Model):
    content = MarkDownField()
    author = models.ForeignKey(User)
    node = models.ForeignKey(Node)
    time = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
     
    def __unicode__(self):
        return self.content
    
#话题：标题，内容，所属节点，作者，查看次数，回复次数，创建时间，最后更新时间
class Topic(models.Model):
    title = models.CharField(max_length=100)
    #content = models.TextField()  
    content = MarkDownField()
    #content_html = wmd_models.MarkDownField(editable = False, blank = True)
    node = models.ForeignKey(Node)
    author = models.ForeignKey(User,related_name='+')
    num_views = models.IntegerField(default=0)
    num_replies = models.PositiveSmallIntegerField(default=0)
    last_reply = models.ForeignKey(User,related_name='+',null=True)
    created_on = models.DateTimeField(auto_now_add=True)      #第一次创建时加入当前时间
    updated_on = models.DateTimeField(blank=True, null=True)   #最后一次回复
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return "/topic/%i/" % self.id
#     def save(self, force_insert = False, force_update = False):
#         self.content_html = markdown(self.content)
#         print self.content_html
#         super(Topic,self).save(force_insert, force_update)

#回复：内容，所属话题，作者，创建时间
class Reply(models.Model):
    #content = models.TextField()
    content = MarkDownField()
    #content_html = wmd_models.MarkDownField(editable = False, blank = True)
    author = models.ForeignKey(User)
    topic = models.ForeignKey(Topic)
    has_parent = models.BooleanField(default=False)
    parent = models.ForeignKey('self',null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.content
    
    def save(self,*args,**kwargs):
        #self.content_html = markdown(self.content)
        print self.content
        super(Reply,self).save(*args,**kwargs)
    
class Notice(models.Model):
    sender = models.ForeignKey(User,related_name='+') #not to create a backwards relation
    recipient = models.ForeignKey(User,related_name='+')
    is_topic = models.BooleanField()
    topic = models.ForeignKey(Topic,null=True)
    reply = models.ForeignKey(Reply,null=True)
    content = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now_add=True)
    is_readed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.content
    
class Message(models.Model):
    is_sender = models.BooleanField()
    talk_to = models.ForeignKey(User,related_name='+')
    belong_to = models.ForeignKey(User,related_name='+')
    content = models.CharField(max_length=200,blank=False)
    time = models.DateTimeField()
    is_deleted = models.BooleanField(default=False)
    is_readed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.content
    
def create_notice(sender, **kwargs):
    reply = kwargs['instance']   
    if reply.has_parent:
        print reply.author,reply.parent.author,reply.topic,reply.parent
        if reply.author != reply.parent.author:     #可以回复自己的回复，但是不新建提醒
            Notice.objects.create(sender=reply.author,recipient=reply.parent.author,is_topic=False,topic=reply.topic,reply=reply.parent,content=reply.content)
    else:
        print reply.author,reply.topic.author,reply.topic
        if reply.author != reply.topic.author:      #可以回复自己的话题，但是不新建提醒
            Notice.objects.create(sender=reply.author,recipient=reply.topic.author,is_topic=True,topic=reply.topic,content=reply.content)
    print '新的提醒：',reply.content
    


post_save.connect(create_notice, sender=Reply)
