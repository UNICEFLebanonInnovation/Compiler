# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import models
from django.contrib import admin

from .models import (
    Outreach
)

admin.site.register(Outreach)
