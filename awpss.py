#!/usr/bin/env python3

import os
import json
from subprocess import call
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

class Awpss():
    ''' Main class file. '''

    conf_dir  = os.path.join(os.path.expanduser('~'), '.awpss')
    conf_file = os.path.join(conf_dir, 'config')
    hist_file = os.path.join(conf_dir, 'history')
    log_file  = os.path.join(conf_dir, 'awpss_cronjob.log')
    
    resources = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
    cron_file = os.path.join(resources, 'awpss_cronjob.py')
    
    api_list      = ['Pixiv API', 'Gelbooru API', 'Danbooru API', 'Shimmie2 Danbooru API']
    api_list_safe = [a.lower().replace(" ", "_") for a in api_list]
    
    conf = {
        'api'        :'gelbooru_api',
        'url'        :'http://gelbooru.com/',
        'tags'       :'ore_no_imouto_ga_konna_ni_kawaii_wake_ga_nai',
        'timeout'    :'60',
        'rating'     :'true',
        'size'       :'true',
        'enabled'    :'true',
        'api_limit'  :'10',
        'cache_size' :'500', # Number of images
        'offset'     :'0',
        'user'       :'',
        'pass'       :''
    }

    def write_conf(self):
        ''' Saves options to state file in home directory. '''

        if not os.path.exists(self.conf_dir):
            os.makedirs(self.conf_dir)

        with open(self.conf_file, 'w') as handle:
            json.dump(self.conf, handle, indent=3)

    def read_conf(self):
        ''' Retrieves the fields from the option file. '''

        if os.path.exists(self.conf_file):
            with open(self.conf_file, 'r') as handle:
                self.conf = json.loads(handle.read())

    def get_fields(self):
        ''' Gets the fields. '''

        self.conf['api']     = self.api_list_safe[self.apis_combo.get_active()]
        self.conf['url']     =                    self.url_entry.get_text()
        self.conf['tags']    =                    self.tags_entry.get_text()
        self.conf['timeout'] =                str(self.timeout_spin_button.get_value_as_int())
        self.conf['user']    =                    self.user_entry.get_text()
        self.conf['pass']    =                    self.pass_entry.get_text()
        self.conf['rating']  =                str(self.rating_check.get_active()).lower()
        self.conf['enabled'] =                str(self.enabled_check.get_active()).lower()

        screen    = Gtk.Window().get_screen()
        mg        = screen.get_monitor_geometry(screen.get_monitor_at_window(screen.get_active_window()))
        self.conf['size'] = 'x'.join([str(mg.width), str(mg.height)]) if self.size_check.get_active() else 'false'

    def setup_cron(self, widget, dummy):
        ''' Save the options. '''
        
        self.get_fields()
        self.write_conf()
        
        if os.path.exists(self.hist_file):
            os.remove(self.hist_file)
        
        command  = ['/usr/bin/env', 'python3', self.cron_file, '2>&1', '>', self.log_file]
        cron_job = '0 * * * * %s' % ' '.join(command)
        add_cron = "( crontab -l | grep -v awpss ; echo \"%s\" ) | crontab - " % cron_job
        rm_cron  = 'crontab -l | grep -v awpss | crontab - '
        
        if self.conf['enabled'] == 'true':
            call(add_cron, shell=True)
            call(command)
        else:
            call(rm_cron, shell=True)



    ''' GUI on_change methods '''
    #def on_apis_combo_changed(self, combo):
    #    text = combo.get_active_text()



    def __init__(self):
        ''' Main Gtk window definitions. '''

        # Create a new window.
        window = Gtk.Window()
        window.set_title('Anime Wallpaper Slideshow')
        window.connect('delete_event', lambda w, e: Gtk.main_quit())
        window.set_border_width(5)
        window.set_default_size(1280/2, 720/2)

        # Get saved values or load defaults
        self.read_conf()

        # Vertical box with options
        vbox = Gtk.VBox()
        vbox.set_homogeneous(False)
        vbox.set_spacing(3)
        window.add(vbox)

        # Retrieve and set the artwork
        artwork = Gtk.VBox()
        fileimage = os.path.join(self.resources, 'Anime_film_icon.svg')
        # Window icon
        window.set_icon_from_file(fileimage)
        # Main image
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(fileimage, -1, 256, True)
        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)
        artwork.pack_start(image, True, True, 0)
        vbox.pack_start(artwork, True, True, 1)

        # Frame that contains table and hbox, aka everything below main image
        frame = Gtk.Frame()
        vbox.pack_start(frame, True, True, 1)
        frame.set_border_width(5)
        frame.set_shadow_type(Gtk.ShadowType.NONE)

        # Table with all main options
        table = Gtk.Table(9, 4)
        table.set_border_width(3)
        table.set_row_spacings(4)
        table.set_col_spacings(6)

        # Set API
        label = Gtk.Label('API: ')
        label.set_alignment(0, 0.5)
        table.attach_defaults(label, 0, 1, 0, 1)
        frame.add(table)

        self.apis_combo = Gtk.ComboBoxText()
        self.apis_combo.set_entry_text_column(0)
        # self.apis_combo.connect("changed", self.on_apis_combo_changed)
        for api in self.api_list:
            self.apis_combo.append_text(api)
        self.apis_combo.set_active(self.api_list_safe.index(self.conf['api']))
        self.apis_combo.set_tooltip_text('Set which API your preferred imageboard uses.')
        table.attach_defaults(self.apis_combo, 1, 4, 0, 1)

        # Set URL
        label = Gtk.Label('URL of imageboard: ')
        label.set_alignment(0, 0.5)
        table.attach_defaults(label, 0, 1, 1, 2)

        self.url_entry = Gtk.Entry()
        self.url_entry.set_text(self.conf['url'])
        self.url_entry.set_tooltip_text('The url of your preferred imageboard with trailing slash.')
        table.attach_defaults(self.url_entry, 1, 4, 1, 2)

        # Set Tags
        label = Gtk.Label('Tags to filter wallpapers: ')
        label.set_alignment(0, 0.5)
        table.attach_defaults(label, 0, 1, 2, 3)

        self.tags_entry = Gtk.Entry()
        self.tags_entry.set_text(self.conf['tags'])
        self.tags_entry.set_tooltip_text('Tags to filter wallpapers, e.g. favorite artist.')
        table.attach_defaults(self.tags_entry, 1, 4, 2, 3)

        # Timeout
        label = Gtk.Label('Timeout (minutes): ')
        label.set_alignment(0, 0.5)
        table.attach_defaults(label, 0, 1, 3, 4)

        adjustment = Gtk.Adjustment(int(self.conf['timeout']), 1, 1440, 5, 15)
        self.timeout_spin_button = Gtk.SpinButton()
        self.timeout_spin_button.set_adjustment(adjustment)
        self.timeout_spin_button.set_numeric(True)
        self.timeout_spin_button.set_tooltip_text('Time between wallpaper switch in minutes.')
        table.attach_defaults(self.timeout_spin_button, 1, 4, 3, 4)

        # Set User
        label = Gtk.Label('Username: ')
        label.set_alignment(0, 0.5)
        table.attach_defaults(label, 0, 1, 4, 5)

        self.user_entry = Gtk.Entry()
        self.user_entry.set_text(self.conf['user'])
        self.user_entry.set_tooltip_text('Your username on the website above. Likely only needed for Danbooru and Pixiv.')
        table.attach_defaults(self.user_entry, 1, 4, 4, 5)

        # Set Pass
        label = Gtk.Label('API Key: ')
        label.set_alignment(0, 0.5)
        table.attach_defaults(label, 0, 1, 5, 6)

        self.pass_entry = Gtk.Entry()
        self.pass_entry.set_text(self.conf['pass'])
        self.pass_entry.set_tooltip_text('API key or password needed to talk to website. Likely only needed for Danbooru and Pixiv.')
        table.attach_defaults(self.pass_entry, 1, 4, 5, 6)

        # Limit to rating safe
        label = Gtk.Label('Limit to safe rated images? ')
        label.set_alignment(0, 0.5)
        table.attach_defaults(label, 0, 1, 6, 7)

        self.rating_check = Gtk.CheckButton()
        self.rating_check.set_tooltip_text('Should we set rating:safe?')
        self.rating_check.set_active(self.conf['rating'] == 'true')
        table.attach(self.rating_check, 1, 4, 6, 7, Gtk.AttachOptions(2), Gtk.AttachOptions(1), 0, 0)

        # Limit to screen size
        label = Gtk.Label('Limit to your current screen size? ')
        label.set_alignment(0, 0.5)
        table.attach_defaults(label, 0, 1, 7, 8)

        self.size_check = Gtk.CheckButton()
        self.size_check.set_tooltip_text('Should we try and only use wallpaper of the same size as your desktop?')
        self.size_check.set_active(self.conf['size'] != 'false')
        table.attach(self.size_check, 1, 4, 7, 8, Gtk.AttachOptions(2), Gtk.AttachOptions(1), 0, 0)

        # Enabled checkbox
        label = Gtk.Label('Enabled? ')
        label.set_alignment(0, 0.5)
        table.attach_defaults(label, 0, 1, 8, 9)

        self.enabled_check = Gtk.CheckButton()
        self.enabled_check.set_tooltip_text('Enable or disable the slideshow.')
        self.enabled_check.set_active(self.conf['enabled'] == 'true')
        table.attach(self.enabled_check, 1, 4, 8, 9, Gtk.AttachOptions(2), Gtk.AttachOptions(1), 0, 0)

        # Horizontal box with close and apply buttons
        frame = Gtk.Frame()
        hbox = Gtk.HBox()
        hbox.set_homogeneous(True)
        frame.add(hbox)
        frame.set_border_width(5)
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        vbox.pack_start(frame, False, True, 0)

        # Close button
        button = Gtk.Button(stock=Gtk.STOCK_CLOSE)
        button.connect('clicked', lambda w: Gtk.main_quit())
        hbox.pack_start(button, False, True, 0)
        button.set_can_default(True)
        button.grab_default()

        # Apply button
        button = Gtk.Button(stock=Gtk.STOCK_APPLY)
        button.connect('clicked', self.setup_cron, None)
        hbox.pack_start(button, False, True, 0)

        # Done
        window.show_all()

def main():
    Gtk.main()
    return 0

if __name__ == '__main__':
    Awpss()
    main()
