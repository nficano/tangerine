#!/usr/bin/env/python
# -*- coding: utf-8 -*-
import time
import datetime


class Task(object):
    def __init__(self, schedule, fn, **options):
        self.schedule = schedule
        self.fn = fn
        self.options = options
        self.next_run = self.get_next_run(schedule)

    def get_next_run(self, schedule):
        now = datetime.datetime.now()
        delta = datetime.timedelta(minutes=int(schedule))
        return now + delta

    def run(self):
        self.fn(**self.options)

    def __repr__(self):
        return str(self.next_run)


class Scheduler(object):
    def __init__(self):
        self.tasks = []

    def add_cron(self, schedule, f, **options):
        self.tasks.append(Task(schedule, f, **options))

    def cron(self, schedule, **options):
        def decorator(f):
            self.add_cron(schedule, f, **options)
            return f
        return decorator

    def run_pending(self):
        print self.tasks
        while True:
            now = datetime.datetime.now()
            for idx, task in enumerate(self.tasks):
                if now > task.next_run:
                    t = self.tasks.pop(idx)
                    t.run()
                    self.add_cron(t.schedule, t.fn, **t.options)
            time.sleep(5)


scheduler = Scheduler()


@scheduler.cron("1")
def task1():
    print "task1"


@scheduler.cron("2")
def task2():
    print "task2"


scheduler.run_pending()
