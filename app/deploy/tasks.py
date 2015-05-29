#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' 
--------------------------------------------------------------------------------------
tasks.py
--------------------------------------------------------------------------------------
A set of tasks to manage your AWS Django deployment.

author : Ashok Fernandez (github.com/ashokfernandez/)
credit : Derived from files in https://github.com/gcollazo/Fabulous
date   : 11 / 3 / 2014

Tasks include:
    - configure_instance  : Configures a new EC2 instance (as definied in settings.py) and return's it's public dns
                            This takes around 8 minutes to complete.
 
    - update_packages : Updates the python packages on the server to match those found in requirements/common.txt and 
                        requirements/prod.txt
 
    - deploy : Pulls the latest commit from the master branch on the server, collects the static files, syncs the db and                   
               restarts the server
 
    - reload_gunicorn : Pushes the gunicorn startup script to the servers and restarts the gunicorn process, use this if you 
                        have made changes to templates/start_gunicorn.bash
 
    - reload_nginx : Pushes the nginx config files to the servers and restarts the nginx, use this if you 
                     have made changes to templates/nginx-app-proxy or templates/nginx.conf

    - reload_supervisor : Pushes the supervisor config files to the servers and restarts the supervisor, use this if you 
                          have made changes to templates/supervisord-init or templates/supervisord.conf

'''

# Spawns a new EC2 instance (as definied in djangofab_conf.py) and return's it's public dns
# This takes around 8 minutes to complete.
configure_instance = [

    # First command as regular user
    {"action": "sudo", "params": "rm -rf ~/*"},
    {"action": "run", "params": "whoami"},

    # # sudo apt-get update
    # {"action": "sudo", "params": "add-apt-repository ppa:webupd8team/java",
    #     "message": "Add java apt repository"},
    # {"action": "sudo", "params": "add-apt-repository ppa:gstreamer-developers/ppa",
    #     "message": "Add gstreamer apt repository"},
    # {"action": "sudo", "params": "apt-get update -qq",
    #     "message": "Updating apt-get"},

    # # List of APT packages to install
    # {"action": "apt",
    #     "params": ["libpq-dev", "nginx", "git",
    #                "python-setuptools", "python-dev", "build-essential", "python-pip",
    #                "libmysqlclient-dev", "subversion", "sox", "oracle-java7-installer", "mp3split",
    #                "gstreamer0.10-tools", "gstreamer-tools", "gstreamer0.10-plugins-base", "gstreamer0.10-plugins-good", "gstreamer0.10-plugins-bad"],
    #     "message":"Installing apt-get packages" },

    # # List of pypi packages to install
    # {"action": "pip", "params": ["virtualenv", "supervisor"],
    #     "message":"Installing pip packages"},

    # project directory
    {"action": "run",  "params": "mkdir -p %(PROJECT_DIR)s", "message": "Create project folder" },
    {"action": "sudo", "params": "chown -R %(EC2_SERVER_USERNAME)s: %(PROJECT_DIR)s"},

    # git setup
    {"action": "run", "params": "git config --global user.name '%(GIT_USERNAME)s'",
        "message": "Configuring git"},
    {"action": "run",
        "params": "git config --global user.email '%(ADMIN_EMAIL)s'"},
    {"action": "put", "params": {"file": "%(GIT_KEY_PATH)s",
                                 "destination": "/home/%(EC2_SERVER_USERNAME)s/.ssh/%(GIT_KEY_NAME)s"}},
    {"action": "run", "params":
     "chmod 600 /home/%(EC2_SERVER_USERNAME)s/.ssh/%(GIT_KEY_NAME)s"},
    {"action": "run", "params":
     u"""echo 'IdentityFile /home/%(EC2_SERVER_USERNAME)s/.ssh/%(GIT_KEY_NAME)s' >> /home/%(EC2_SERVER_USERNAME)s/.ssh/config"""},
    {"action": "run", "params":
     "ssh-keyscan github.com >> /home/%(EC2_SERVER_USERNAME)s/.ssh/known_hosts"},

    # Clone the git repo
    {"action": "run",
        "params": "git clone %(REPOSITORY)s %(PROJECT_DIR)s"},

    # virtualenv
    {"action": "run",
        "params": "mkdir -p %(ENV_DIR)s", "message": "Create project folder" },
    {"action": "run",
        "params": "virtualenv %(ENV_DIR)s", "message": "Configuring virtualenv" },

    {"action": "sudo", "params": "chown -R %(EC2_SERVER_USERNAME)s: %(ENV_DIR)s"},
    # {"action": "run", "params":
    #     "echo 'expo WORKON_HOME=%(PRO_DIR)s' >> /home/%(EC2_SERVER_USERNAME)s/.profile"},
    {"action": "run", "params":
        u"echo 'source %(ACTIVATE)s' >> /home/%(EC2_SERVER_USERNAME)s/.profile"},
    {"action": "run", "params": "source /home/%(EC2_SERVER_USERNAME)s/.profile"},

    {"action": "virtualenv", "params":
        "pip install -r %(PROJECT_PATH)s/requirements/common.txt --upgrade"},


    # {"action": "run", "params": """echo "alias webapps='cd %(APPS_DIR)s'" >> /home/%(SERVER_USERNAME)s/.profile""",
    #     "message": "Creating webapps alias"},


 

    # {"action": "put", "params": {"file": "%(FAB_CONFIG_PATH)s/templates/gunicorn.conf.py",
    #                              "destination": "%(PROJECT_PATH)s/gunicorn.conf.py"}},

    # # Create run and log dirs for the gunicorn socket and logs
    # {"action": "run", "params": "mkdir %(PROJECT_PATH)s/logs"},

    # # Add gunicorn startup script to project folder
    # {"action": "put_template", "params": {"template": "%(FAB_CONFIG_PATH)s/templates/start_gunicorn.bash",
    #                                       "destination": "%(PROJECT_PATH)s/start_gunicorn.bash"}},
    # {"action": "sudo",
    #  "params": "chmod +x %(PROJECT_PATH)s/start_gunicorn.bash"},

    # # Install the requirements from the pip requirements files
    # {"action": "virtualenv", "params":
    #  "pip install -r %(PROJECT_PATH)s/requirements/common.txt --upgrade"},
    # {"action": "virtualenv", "params":
    #  "pip install -r %(PROJECT_PATH)s/requirements/prod.txt --upgrade"},

    # # nginx
    # {"action": "put", "params": {"file": "%(FAB_CONFIG_PATH)s/templates/nginx.conf",
    #                              "destination": "/home/%(SERVER_USERNAME)s/nginx.conf"},
    #     "message": "Configuring nginx"},
    # {"action": "sudo",
    #  "params": "mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.old"},
    # {"action": "sudo", "params":
    #  "mv /home/%(SERVER_USERNAME)s/nginx.conf /etc/nginx/nginx.conf"},
    # {"action": "sudo", "params": "chown root:root /etc/nginx/nginx.conf"},
    # {"action": "put_template", "params": {"template": "%(FAB_CONFIG_PATH)s/templates/nginx-app-proxy",
    #                                       "destination": "/home/%(SERVER_USERNAME)s/%(PROJECT_NAME)s"}},
    # {"action": "sudo", "params": "rm -rf /etc/nginx/sites-enabled/default"},
    # {"action": "sudo", "params":
    #  "mv /home/%(SERVER_USERNAME)s/%(PROJECT_NAME)s /etc/nginx/sites-available/%(PROJECT_NAME)s"},
    # {"action": "sudo", "params":
    #  "ln -s /etc/nginx/sites-available/%(PROJECT_NAME)s /etc/nginx/sites-enabled/%(PROJECT_NAME)s"},
    # {"action": "sudo", "params":
    #  "chown root:root /etc/nginx/sites-available/%(PROJECT_NAME)s"},
    # {"action": "sudo", "params": "/etc/init.d/nginx restart",
    #  "message": "Restarting nginx"},

    # # Run collectstatic and syncdb
    # {"action": "virtualenv",
    #  "params": "python %(PROJECT_PATH)s/manage.py collectstatic -v 0 --noinput"},
    # {"action": "virtualenv",
    #  "params": "python %(PROJECT_PATH)s/manage.py syncdb"},


    # # Setup supervisor
    # {"action": "run", "params": "echo_supervisord_conf > /home/%(SERVER_USERNAME)s/supervisord.conf",
    #     "message": "Configuring supervisor"},
    # {"action": "put_template", "params": {"template": "%(FAB_CONFIG_PATH)s/templates/supervisord.conf",
    #                                       "destination": "/home/%(SERVER_USERNAME)s/my.supervisord.conf"}},
    # {"action": "run", "params":
    #  "cat /home/%(SERVER_USERNAME)s/my.supervisord.conf >> /home/%(SERVER_USERNAME)s/supervisord.conf"},
    # {"action": "run",
    #  "params": "rm /home/%(SERVER_USERNAME)s/my.supervisord.conf"},
    # {"action": "sudo", "params":
    #  "mv /home/%(SERVER_USERNAME)s/supervisord.conf /etc/supervisord.conf"},
    # {"action": "sudo", "params": "supervisord"},
    # {"action": "put", "params": {"file": "%(FAB_CONFIG_PATH)s/templates/supervisord-init",
    #                              "destination": "/home/%(SERVER_USERNAME)s/supervisord-init"}},
    # {"action": "sudo", "params":
    #  "mv /home/%(SERVER_USERNAME)s/supervisord-init /etc/init.d/supervisord"},
    # {"action": "sudo", "params": "chmod +x /etc/init.d/supervisord"},
    # {"action": "sudo", "params": "update-rc.d supervisord defaults"}
]

# Updates the python packages on the server to match those found in requirements/common.txt and
# requirements/prod.txt
update_packages = [
    # Updates the python packages
    {"action": "virtualenv", "params":
        "pip install -r %(PROJECT_PATH)s/requirements/common.txt --upgrade"},
]

# Pulls the latest commit from the master branch on the server, collects the static files, syncs
# the db and restarts the server
deploy = [

    # Pull the latest version from the bitbucket repo
    {"action": "run", "params": "cd %(PROJECT_PATH)s && git pull"},

    # Update the database
    {"action": "virtualenv",
     "params": "python %(PROJECT_PATH)s/manage.py collectstatic -v 0 --noinput"},
    {"action": "virtualenv",
     "params": "python %(PROJECT_PATH)s/manage.py syncdb"},

    # Restart gunicorn to update the site
    {"action": "sudo", "params": "supervisorctl restart %(PROJECT_NAME)s"}
]

# Pushes the gunicorn startup script to the servers and restarts the gunicorn process, use this
# if you have made changes to templates/start_gunicorn.bash
reload_gunicorn = [

    # Push the gunicorn startup script to server
    {"action": "put_template", "params": {"template": "%(FAB_CONFIG_PATH)s/templates/start_gunicorn.bash",
                                          "destination": "%(PROJECT_PATH)s/start_gunicorn.bash"}},
    {"action": "sudo",
     "params": "chmod +x %(PROJECT_PATH)s/start_gunicorn.bash"},

    # Restart gunicorn to update the site
    {"action": "sudo", "params": "supervisorctl restart %(PROJECT_NAME)s"}
]

# Pushes the nginx config files to the servers and restarts the nginx, use this if you
# have made changes to templates/nginx-app-proxy or templates/nginx.conf
reload_nginx = [

    # stop old nginx process
    {"action": "sudo", "params": "service nginx stop"},

    # Load the nginx config files
    {"action": "put", "params": {"file": "%(FAB_CONFIG_PATH)s/templates/nginx.conf",
                                 "destination": "/home/%(SERVER_USERNAME)s/nginx.conf"},
        "message": "Configuring nginx"},
    {"action": "sudo",
     "params": "mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.old"},
    {"action": "sudo", "params":
     "mv /home/%(SERVER_USERNAME)s/nginx.conf /etc/nginx/nginx.conf"},
    {"action": "sudo", "params": "chown root:root /etc/nginx/nginx.conf"},
    {"action": "put_template", "params": {"template": "%(FAB_CONFIG_PATH)s/templates/nginx-app-proxy",
                                          "destination": "/home/%(SERVER_USERNAME)s/%(PROJECT_NAME)s"}},
    {"action": "sudo", "params": "rm -rf /etc/nginx/sites-enabled/default"},
    {"action": "sudo", "params":
     "mv /home/%(SERVER_USERNAME)s/%(PROJECT_NAME)s /etc/nginx/sites-available/%(PROJECT_NAME)s"},
    # {"action":"sudo", "params":"ln -s /etc/nginx/sites-available/%(PROJECT_NAME)s /etc/nginx/sites-enabled/%(PROJECT_NAME)s"},
    {"action": "sudo", "params":
     "chown root:root /etc/nginx/sites-available/%(PROJECT_NAME)s"},
    {"action": "sudo", "params": "/etc/init.d/nginx restart",
     "message": "Restarting nginx"},
]

# Pushes the supervisor config files to the servers and restarts the supervisor, use this if you
# have made changes to templates/supervisord-init or templates/supervisord.conf
reload_supervisor = [

    # stop old supervisor process
    {"action": "sudo", "params": "supervisorctl stop all"},
    {"action": "sudo", "params": "killall supervisord"},

    # Setup supervisor
    {"action": "run", "params": "echo_supervisord_conf > /home/%(SERVER_USERNAME)s/supervisord.conf",
        "message": "Configuring supervisor"},
    {"action": "put_template", "params": {"template": "%(FAB_CONFIG_PATH)s/templates/supervisord.conf",
                                          "destination": "/home/%(SERVER_USERNAME)s/my.supervisord.conf"}},
    {"action": "run", "params":
     "cat /home/%(SERVER_USERNAME)s/my.supervisord.conf >> /home/%(SERVER_USERNAME)s/supervisord.conf"},
    {"action": "run",
     "params": "rm /home/%(SERVER_USERNAME)s/my.supervisord.conf"},
    {"action": "sudo", "params":
     "mv /home/%(SERVER_USERNAME)s/supervisord.conf /etc/supervisord.conf"},
    {"action": "sudo", "params": "supervisord"},
    {"action": "put", "params": {"file": "%(FAB_CONFIG_PATH)s/templates/supervisord-init",
                                 "destination": "/home/%(SERVER_USERNAME)s/supervisord-init"}},
    {"action": "sudo", "params":
     "mv /home/%(SERVER_USERNAME)s/supervisord-init /etc/init.d/supervisord"},
    {"action": "sudo", "params": "chmod +x /etc/init.d/supervisord"},
    {"action": "sudo", "params": "update-rc.d supervisord defaults"},

    # Restart supervisor
    {"action": "sudo", "params": "supervisorctl start all"}
]
