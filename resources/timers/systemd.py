#!/usr/bin/env python3

import os
from subprocess import call
from ..set_wallpaper import is_running

class SystemD:
    
    minutes   = ''
    task_file = ''
    log_file  = ''
    
    def reload_systemd(self):
        call(['systemctl', '--user', 'daemon-reload'])
    
    def write_files(self):
        home         = os.path.expanduser('~')
        systemd_dir  = os.path.join(home, '.local', 'share', 'systemd', 'user')
        service_file = os.path.join(systemd_dir, 'awpss.service')
        timer_file   = os.path.join(systemd_dir, 'awpss.timer')
        
        if not os.path.exists(systemd_dir):
            os.makedirs(systemd_dir)
        
        service = '''
[Unit]
Description=Anime Wallpaper Slideshow Task

[Service]
Type=oneshot
ExecStart={}

'''.format(self.task_file)
        
        f = open(service_file,'w')
        f.write(service)
        f.close()
        
        timer = '''
[Unit]
Description=Anime Wallpaper Slideshow Timer

[Timer]
OnBootSec=1min
OnUnitActiveSec={}min

[Install]
WantedBy=timers.target

'''.format(self.minutes)
        
        f = open(timer_file,'w')
        f.write(timer)
        f.close()
        
        self.reload_systemd()
    
    def set_minutes(self, minutes='60'):
        self.minutes = minutes
    
    def enable(self, enable=True):
        
        self.write_files()
        
        if enable:
            call(['systemctl', '--user', 'enable', 'awpss.service'])
            call(['systemctl', '--user', 'enable', 'awpss.timer'])
            call(['systemctl', '--user', 'start',  'awpss.timer'])
        else:
            call(['systemctl', '--user', 'disable', 'awpss.service'])
            call(['systemctl', '--user', 'disable', 'awpss.timer'])
            call(['systemctl', '--user', 'stop',    'awpss.timer'])
        
    def set(self, task_file='', log_file='', minutes='60', enabled=False):
        self.task_file = task_file
        self.log_file  = log_file
        self.set_minutes(minutes)
        self.enable(enabled)

    def __init__(self, task_file=None, log_file=None, minutes='60', enabled=False):
        if task_file is not None:
            self.set(task_file, log_file, minutes, enabled)


