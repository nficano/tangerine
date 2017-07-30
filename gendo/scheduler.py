#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from crontab import CronTab


class Task(object):
    def __init__(self, schedule, fn, **options):
        self.schedule = schedule
        self.fn = fn
        self.options = options
        self.next_run = self.get_next_run(schedule)

    def get_next_run(self, schedule):
        now = datetime.datetime.now()
        entry = CronTab(schedule)
        delta = datetime.timedelta(0, entry.next())
        return now + delta

    def run(self):
        self.fn(**self.options)

    def __repr__(self):
        return str(self.next_run)
