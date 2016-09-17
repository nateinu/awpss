#!/usr/bin/env python3

from subprocess import call
from ..set_wallpaper import is_running

class Cron:
    
    minutes   = ''
    task_file = ''
    log_file  = ''
    
    def set_minutes(self, minutes='60'):
        
        minutes = int(minutes)
        
        if   minutes < 1:
            # default
            self.minutes = '0 * * * *'
        elif minutes < 2:
            # every minute
            self.minutes = '* * * * *'
        elif minutes < 6:
            # every five minutes
            self.minutes = '*/5 * * * *'
        elif minutes < 11:
            # every ten minutes
            self.minutes = '*/10 * * * *'
        elif minutes < 31:
            # every 30 minutes
            self.minutes = '0,30 * * * *'
        elif minutes < 61:
            # every hour
            self.minutes = '0 * * * *'
        elif minutes < 121:
            # every 2 hours
            self.minutes = '0 */2 * * *'
        elif minutes < 1441:
            # once a day
            self.minutes = '0 0 * * *'
        elif minutes < 10081:
            # once a week
            self.minutes = '0 0 * * 3'
        elif minutes < 43801:
            # once a month
            self.minutes = '0 0 1 * *'
        elif minutes < 525601:
            # once a year
            self.minutes = '0 0 1 1 *'
        else:
            # default
            self.minutes = '0 * * * *'
    
    def enable(self, enable=True):
        command  = ['/usr/bin/env', 'python3', self.task_file]
        cron_job = '{} {} 2>&1 >> {}'.format(self.minutes, ' '.join(command), self.log_file)
        add_cron = '( crontab -l | grep -v awpss ; echo "{}" ) | crontab - '.format(cron_job)
        rm_cron  = 'crontab -l | grep -v awpss | crontab - '
        
        if enable:
            call(add_cron, shell=True)
            call(command)
        else:
            call(rm_cron, shell=True)
        
        if not is_running('cron'):
            print('Cron does not seem to be running.\nYou might need to run:\n"sudo systemctl enable crond ; sudo systemctl start crond"\nOR\n"sudo /etc/init.d/cron start"\n')

    def set(self, task_file='', log_file='', minutes='60', enabled=False):
        self.task_file = task_file
        self.log_file  = log_file
        self.set_minutes(minutes)
        self.enable(enabled)

    def __init__(self, task_file=None, log_file=None, minutes='60', enabled=False):
        if task_file is not None:
            self.set(task_file, log_file, minutes, enabled)


