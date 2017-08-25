# Installation

In order to use sci.AI EXE you need:
- MongoDB
- Ubuntu 14.04 or newer
- Apache2 with WSGI module
- Supervisor

1 Clone repository

```
git clone git@github.com:sciAI/exe.git
```

2 Go to folder with repository content (jupyter-testing by default)

```
cd exe
```

3 Create two virtual environments (for Python 2 and Python 3):

```
virtualenv -p python py2env
virtualenv -p python3 py3env
```

4 Activate py2env:

```
source py2env/bin/activate
```

5 Install requirements

```
pip install -r requirements.txt
```

6 Create new configuration file:

```
cd /opt/exe
cp config_example.py config.py
nano config.py
```

You should at least change the following lines:

```
MONGODB_SETTINGS = [
    {
        'alias': 'main',
        'db': 'jupyter',
        'host': 'localhost',
        'port': 12345
    }
]
```

7 Configure Apache2:

```
cd /etc/apache2/sites-available
nano exe.conf
```

And paste content:

```
Listen 80
<VirtualHost *:80>
        #ServerName exe.sci.ai
        #ServerAdmin hello@sci.ai
        WSGIScriptAlias / /opt/exe/app.wsgi

         <Directory /opt/exe/>
                Require all granted
                Order allow,deny
                Allow from all
        </Directory>

        Alias /static /opt/exe/validator/static
        <Directory /opt/exe/validator/static/>
                Order allow,deny
                Allow from all
        </Directory>

        ErrorLog ${APACHE_LOG_DIR}/exe/error.log
        LogLevel warn
        CustomLog ${APACHE_LOG_DIR}/exe/access.log combined
</VirtualHost>
```

8 Configure Supervisor

```
cd /etc/supervisor/conf.d/
nano exe.conf
```

And insert the following content:

```
[program:exe]
command=/opt/exe/py2env/bin/python /opt/exe/worker/worker.py high normal low
process_name=%(program_name)s

numprocs=1
stopsignal=TERM
autostart=true
autorestart=true

; Log files
stderr_logfile=/var/log/apache2/exe/workers.err.log
stdout_logfile=/var/log/apache2/exe/workers.out.log
```

9 Configure kernels for IPython.

a) Python 2

```
source py2env/bin/activate
pip install ipykernel
python -m ipykernel install --prefix=./py2env --name 'python2'
```

b) Python 3

```
source py3env/bin/activate
pip install ipykernel
python -m ipykernel install --prefix=./py2env --name 'python3'
```

10 Change rights for directories 

```
chown www-data:www-data -R exe/static/uploads
chown www-data:www-data -R py2env
chown www-data:www-data -R py3env
```

11 Restart Apache2 and Supervisor:

```
service apache2 restart
service supervisor restart
```

And open in browser:

```
http://YOUR_IP
```

If everything is okay you will see form to upload new file.