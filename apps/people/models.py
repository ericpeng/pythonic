#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django.contrib.auth.models import User
from django.db import models

#我关注的用户
class Follow(models.Model):
    user = models.ForeignKey(User,related_name='+')
    follow = models.ForeignKey(User,related_name='+')
    time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '' + self.user.get_profile().name + ' follow ' + self.follow.get_profile().name
    
#用户关注了我
# class Fans(models.Model):
#     user = models.ForeignKey(User,related_name='+')
#     fans = models.ForeignKey(User,related_name='+')
#     time = models.DateTimeField(auto_now_add=True)
# 
#     def __unicode__(self):
#         return self.user + ' be fans of ' + self.follow