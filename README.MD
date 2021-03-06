# exe.sci.AI

[exe.sci.AI](http://exe.sci.ai/) is a validator of the research code executability. Submit link to the full text paper to find Jupyter notebook and execute it automatically. Application will report result whether notebook executes successfully or fails due to the error. 

![](https://github.com/sciAI/exe/blob/master/images/exe_sci_ai_report.png)

Implementation is inspired by https://github.com/sparcopen/open-research-doathon/issues/25 conversation and chatting with @Daniel-Mietchen. 

## Getting Started

### Prerequisites

In order to use sci.AI EXE you need:

1 Ubuntu 14.04 or newer

2 Mongo DB 3.0+

3 Apache2 with WSGI module

```
sudo apt-get update
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi
sudo service apache2 restart
```

4 Supervisor

```
sudo apt-get install supervisor
sudo service supervisor restart
```

5 virtualenv

```
sudo apt-get install python-pip
sudo pip install virtualenv
```

### Installing

1 Clone repository

```
git clone git@github.com:sciAI/exe.git
```

2 Go to folder with repository content (exe by default)

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

If everything is okay you will see form to upload new file:

<p align="center">
<img style="max-width:400px;" src="images/main-page.png">
</p>


## Contributing

To be added.

## License

This project is licensed under the AGPL-3.0 License - see the [LICENSE](LICENSE) file for details