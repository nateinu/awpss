#!/usr/bin/env python3

import os
import re
import sys
import traceback
import configparser # python2 = ConfigParser ?
import subprocess
from subprocess import call

# From: Martin Hansen
# https://stackoverflow.com/users/2118300/martin-hansen
# https://stackoverflow.com/questions/1977694/change-desktop-background
# https://stackoverflow.com/questions/2035657/what-is-my-current-desktop-environment/21213358#21213358

def get_desktop_environment():
    
    if sys.platform in ["win32", "cygwin"]:
        return "windows"
    
    elif sys.platform == "darwin":
        return "mac"
    
    else:
        
        # Most likely either a POSIX system or something not much common
        
        desktop_session = os.environ.get("DESKTOP_SESSION")
        
        if desktop_session is not None:
            
            desktop_session = desktop_session.lower()
            
            if desktop_session in ["gnome","unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox", 
                                   "blackbox", "openbox", "icewm", "jwm", "afterstep","trinity", "kde",
                                   "pantheon"]:
                return desktop_session
            
            ## Special cases ##
            # Canonical sets $DESKTOP_SESSION to Lubuntu rather than LXDE if using LXDE.
            # There is no guarantee that they will not do the same with the other desktop environments.
            
            elif "xfce" in desktop_session or desktop_session.startswith("xubuntu"):
                return "xfce4"
            
            elif desktop_session.startswith("ubuntu"):
                return "unity"       
            
            elif desktop_session.startswith("lubuntu"):
                return "lxde" 
            
            elif desktop_session.startswith("kubuntu"): 
                return "kde" 
            
            elif desktop_session.startswith("razor"):
                return "razor-qt"
            
            elif desktop_session.startswith("wmaker"):
                return "windowmaker"
            
        if os.environ.get('KDE_FULL_SESSION') == 'true':
            return "kde"
        
        elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            if not "deprecated" in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                return "gnome2"
        
        elif is_running("gnome-session"):
            return "gnome"
        
        elif is_running("xfce-mcs-manage"):
            return "xfce4"
        
        elif is_running("xfce4start"):
            return "xfce4"
        
        elif is_running("openbox"):
            return "openbox"
        
        elif is_running("ksmserver"):
            return "kde"
    
    return "unknown"

def is_running(process):
    try:
        #Linux/Unix
        s = subprocess.Popen(["ps", "axw"],      stdout=subprocess.PIPE).communicate()[0].splitlines()
    except:
        #Windows
        s = subprocess.Popen(["tasklist", "/v"], stdout=subprocess.PIPE).communicate()[0].splitlines()
    
    for x in s:
        x = x.decode('utf-8')
        if re.search(process, x):
            return True
    
    return False

def get_config_dir(app_name):
    if "XDG_CONFIG_HOME" in os.environ:
        confighome = os.environ['XDG_CONFIG_HOME']
        
    elif "APPDATA" in os.environ:
        # On Windows
        confighome = os.environ['APPDATA']
        
    else:
        try:
            from xdg import BaseDirectory   
            confighome =  BaseDirectory.xdg_config_home
        except ImportError: # Most likely a Linux/Unix system anyway
            confighome =  os.path.join(get_home_dir(),".config")
            
    configdir = os.path.join(confighome,app_name)
    return configdir

def get_home_dir():
    if sys.platform == "cygwin":
        home_dir = os.getenv('HOME')
        
    else:
        home_dir = os.getenv('USERPROFILE') or os.getenv('HOME')
        
    if home_dir is not None:
        return os.path.normpath(home_dir)
    
    else:
        return os.path.expanduser('~')
        # raise KeyError("Neither USERPROFILE or HOME environment variables set.")



def set_wallpaper(file_loc, desktop_env = None):
    
    if desktop_env is None:
        desktop_env = get_desktop_environment()
    
    try:
        
        if   desktop_env == "gnome":
            
            if(os.environ.get('DBUS_SESSION_BUS_ADDRESS') is None):
                #print('DBUS_SESSION_BUS_ADDRESS is None')
                args = ['pgrep','gnome-session']
                lines = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').splitlines()
                pid = lines[-1]
                
                args = ['grep','-z','DBUS_SESSION_BUS_ADDRESS','/proc/%s/environ' % pid]
                lines = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0].partition(b'\0')[0].decode('utf-8').splitlines()
                address = lines[0].split("=",1)[1]
                
                os.environ['DBUS_SESSION_BUS_ADDRESS'] = address

            uri  = file_loc
            args = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri]
            call(args)

        elif desktop_env == "unity":

            uri  = "file://%s" % file_loc
            args = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri]
            call(args)

        elif desktop_env == "cinnamon":

            uri  = "file://%s" % file_loc
            args = ["gsettings", "set", "org.cinnamon.desktop.background", "picture-uri", uri]
            call(args)

        elif desktop_env == "mate":

            try:
                # MATE >= 1.6
                args = ["gsettings", "set", "org.mate.background", "picture-filename", "'%s'" % file_loc]
                call(args)
            except:
                # MATE < 1.6
                args = ["mateconftool-2","-t","string","--set","/desktop/mate/background/picture_filename",'"%s"' % file_loc]
                call(args)

        elif desktop_env == "gnome2": # Not tested

            args = ["gconftool-2","-t","string","--set","/desktop/gnome/background/picture_filename", '"%s"' %file_loc]
            call(args)

        elif desktop_env in ["kde3", "trinity"]:

            args = 'dcop kdesktop KBackgroundIface setWallpaper 0 "%s" 6' % file_loc
            call(args, shell=True)
            
        elif desktop_env == "kde":
            
            # KDE 4 - 5.6 have no real way to change wallpaper from shell or dbus/without gui
            # KDE 5.7+
            # (5.6 in Fedora 24 iso, but 5.7 after dnf update, this works after update)
            args = """qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript 'var allDesktops = desktops();print (allDesktops);for (i=0;i<allDesktops.length;i++) {d = allDesktops[i];d.wallpaperPlugin = "org.kde.image";d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");d.writeConfig("Image", "file://%s")}'""" % file_loc
            call(args, shell=True)
            
        elif desktop_env=="xfce4":

            args = ['xfconf-query','--channel','xfce4-desktop','--list']
            for window in subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0].splitlines():
                window = window.decode('utf-8')
                
                if re.search('last-image', window) or re.search('image-path', window):
                    call(["xfconf-query", "--channel", "xfce4-desktop", "--property", "%s" % window, "--set", file_loc])
                
                if re.search('image-style', window):
                    call(["xfconf-query", "--channel", "xfce4-desktop", "--property", "%s" % window, "--set", "3"])
                
                if re.search('image-show', window):
                    call(["xfconf-query", "--channel", "xfce4-desktop", "--property", "%s" % window, "--set", "true"])
                
            args = ["xfdesktop","--reload"]
            call(args)

        elif desktop_env=="razor-qt":
            
            desktop_conf = configparser.ConfigParser()
            # Development version
            desktop_conf_file = os.path.join(get_config_dir("razor"),"desktop.conf") 
            if os.path.isfile(desktop_conf_file):
                config_option = r"screens\1\desktops\1\wallpaper"
            else:
                desktop_conf_file = os.path.join(get_home_dir(),".razor/desktop.conf")
                config_option = r"desktops\1\wallpaper"
            desktop_conf.read(os.path.join(desktop_conf_file))
            try:
                if desktop_conf.has_option("razor",config_option): #only replacing a value
                    desktop_conf.set("razor",config_option,file_loc)
                    with codecs.open(desktop_conf_file, "w", encoding="utf-8", errors="replace") as f:
                        desktop_conf.write(f)
            except:
                pass

        elif desktop_env in ["fluxbox","jwm","openbox","afterstep"]:
            
            #http://fluxbox-wiki.org/index.php/Howto_set_the_background
            # used fbsetbg on jwm too since I am too lazy to edit the XML configuration 
            # now where fbsetbg does the job excellent anyway. 
            # and I have not figured out how else it can be set on Openbox and AfterSTep
            # but fbsetbg works excellent here too.
            
            try:
                args = ["fbsetbg", file_loc]
                call(args)
            except:
                sys.stderr.write("ERROR: Failed to set wallpaper with fbsetbg!\n")
                sys.stderr.write("Please make sure that You have fbsetbg installed.\n")

        elif desktop_env=="icewm":

            args = ["icewmbg", file_loc]
            call(args)

        elif desktop_env=="blackbox":

            args = ["bsetbg", "-full", file_loc]
            call(args)

        elif desktop_env=="lxde":

            args = "pcmanfm --set-wallpaper %s --wallpaper-mode=scaled" % file_loc
            call(args, shell=True)

        elif desktop_env=="pantheon":

            # elementary OS
            args = ['set-wallpaper', file_loc]
            call(args)

        elif desktop_env=="windowmaker":

            args = "wmsetbg -s -u %s" % file_loc
            call(args, shell=True)

        elif desktop_env=="enlightenment":
            
            args = "enlightenment_remote -desktop-bg-add 0 0 0 0 %s" % file_loc
            call(args, shell=True)
        
        elif desktop_env=="windows":
            
            import ctypes
            SPI_SETDESKWALLPAPER = 20
            ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, file_loc , 0)
        
        elif desktop_env=="mac":
            
            try:
                from appscript import app, mactypes
                app('Finder').desktop_picture.set(mactypes.File(file_loc))
            except ImportError:
                SCRIPT = """/usr/bin/osascript<<END
                tell application "Finder" to
                set desktop picture to POSIX file "%s"
                end tell
                END"""
                call(SCRIPT%file_loc, shell=True)
        
        else:
            
            sys.stderr.write("Warning: Failed to set wallpaper. Your desktop environment (%s) is not supported.\n" % desktop_env)
            sys.stderr.write("You can try manually to set Your wallpaper to %s\n" % file_loc)
            return False
        
        return True
    
    except:
        
        sys.stderr.write("ERROR: Failed to set wallpaper. There might be a bug.\n")
        sys.stderr.write("You can try manually to set Your wallpaper to %s\n" % file_loc)
        
        print("Unexpected error:", sys.exc_info()[0])
        traceback.print_exc(file=sys.stdout)
        return False


