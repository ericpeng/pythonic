#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from apps.accounts.models import UserProfile
from django import forms
from django.utils.safestring import mark_safe

class RegisterForm(forms.Form):
    email = forms.EmailField(label=u'邮箱',required=True,max_length=30,help_text=mark_safe("Initial to affirm that you agree to the <a href='/contract.pdf'>contract</a>."),widget=forms.TextInput(attrs={'class':'span5','autocomplete':'off'}))
    password = forms.CharField(label=u'密码',required=True,max_length=20,min_length=6,widget=forms.PasswordInput(attrs={'class':'span5','autocomplete':'off'}))   
    name = forms.CharField(label='名号',required=True,max_length=20,min_length=3,widget=forms.TextInput(attrs={'class':'span3','autocomplete':'off'}))
    city = forms.CharField(label='常居地',required=True,widget=forms.TextInput(attrs={'class':'span3','autocomplete':'off'}))
    
class LoginForm(forms.Form):
    email = forms.EmailField(label=u'邮箱',required=True,max_length=30)
    password = forms.CharField(label=u'密码',required=True,max_length=20,min_length=6,widget=forms.PasswordInput())
    
class ProfileForm(forms.ModelForm):
    name = forms.CharField(label=u'名号',max_length=20,min_length=3,widget=forms.TextInput(attrs={'class':'span5','autocomplete':'off'}))  #完全重载
    slug = forms.CharField(label=u'个性域名',max_length=40,min_length=3,widget=forms.TextInput(attrs={'class':'span5','autocomplete':'off'}))
    website = forms.CharField(label=u'网站/博客',max_length=30,required=False,widget=forms.TextInput(attrs={'class':'span5','autocomplete':'off'}))
    weibo = forms.CharField(label=u'微博',max_length=50,required=False,widget=forms.TextInput(attrs={'class':'span5','autocomplete':'off'}))
    github = forms.CharField(label=u'GitHub',max_length=50,required=False,widget=forms.TextInput(attrs={'class':'span5','autocomplete':'off'}))
    avatar = forms.ImageField(label=u'头像')
    city = forms.CharField(label=u'城市',max_length=10,widget=forms.TextInput(attrs={'class':'span2','autocomplete':'off'}))
    signature = forms.CharField(label=u'签名',max_length=40,required=False)
    introduction = forms.CharField(label=u'个人简介',max_length=200,required=False,widget=forms.Textarea(attrs={'class':'span8','style':'height:100px;'}))
    
    class Meta:
        model = UserProfile
        fields = ('name','slug','website','weibo','github','avatar','city','signature','introduction')