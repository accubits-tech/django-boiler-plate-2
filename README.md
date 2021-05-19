# Django: The powerful and flexible toolkit for building Web APIs.


![Django intro](django_boiler_plate/static/images/django-logo.png)

Author : Lija G

This is a boilerplate for Django Rest Framework designed and adopted by the Python developers at Accubits Technologies Inc. A basic user enrollment and verification application is implemented in this to provide a walk through the project structure.

This boilerplate enables the team to quickly setup a Django project environment with the adopted guidelines and helps new joiners to quickly get on board with us.

<br>


### Overview

---

*  ##### [Django: The web framework for perfectionists with deadlines](#Django-The web-framework-for-perfectionists-with deadlines)
*  ##### [Other dependencies in this template](#other-dependencies-in-this-template)
*  ##### [Structuring The Django Project](#structuring-the-django-project)
    * [Creating Project Folder](#creating-project-folder)
    * [Creating Application Folder](#creating-application-folder)
    * [Creating A Virtual Environment](#creating-a-virtual-environment)
    * [Creating Application Files](#creating-application-files)
    * [Installing Django And its Application Dependencies](#installing-flask-and-application-dependencies)
    * [Creating Application Utilities](#creating-application-utilities)
*  ##### [Configuring The Project Application](#configuring-the-project-application)
*  ##### [Structuring The Application Module Directory](#structuring-the-application-module-directory)
      * [Creating Application Modules](#creating-application-modules)
      * [Creating Module Models](#creating-module-models)
      * [Creating Module views](#creating-module-views)
      * [Creating Module Routes](#creating-module-routes)

*  ##### [Launch The application server](#launch-the-application-server)

<br>

### Contents

---

#### Django: The web framework for perfectionists with deadlines.

Django is a high-level Python Web framework that encourages rapid development and clean, pragmatic design

Django takes care of much of the hassle of Web development, so you can focus on writing your app without needing to reinvent the wheel. It’s free and open source

<br>


#### Other dependencies in this template

* Mysql - For storing user credentials and sessions
* Environ - For reading environment variables
* Django CORS - To enable cors policies for the API

<br>

#### Structuring The Django Project

Inside the project directory, we are going to have a virtual environment (i.e. venv) along with the application folders (i.e. api_v0) and some other files such as "env" for keeping the django configurations, and also "requirements.txt" files which stores the dependencies included in the project.

The structure - which is given as an example below - is highly extensible and it  was designed to help developers take applications from concept to completion as quickly as possible.

Example project structure:

```
~/project                      # Project root.
    |__ /project               # Django root, ie the project folder.
         |-- __init__.py
         |-- asgi.py           # Enables ASGI compatible web servers to serve your project (Django 3 only).
         |-- settings.py       # Contains the settings for your Django project.
         |-- urls.py           # Contains project-level URL configurations.
         |-- wsgi.py           # Enables WSGI compatible web servers to serve your project.
    |__ /api_v0                # The application folder, ie, the project modules.
         |__ /migrations       # Contains the migration commands to the database.
            |-- __init__.py
         |-- __init__.py
         |-- admin.py          # Register your app’s models with the Django admin application.
         |-- apps.py           # Configuration file common to all Django apps.
         |-- models.py         # The module containing the models for your app.
         |-- serializers.py    # Input and output data format definitions.
         |-- tests.py          # Test procedures.
         |-- urls.py           # Contains module-level URL configurations.
         |-- views.py          # The module containing the views for your app.
    |__ /utils  #  The utility package
         |-- __init__.py
         |-- pagination.py
         |-- validation_utils.py.py
    |__ /static
         |__ /css
         |__ /img
    |__ /venv       # Virtual Environment
    |-- manage.py   # Django project management utility
    |-- .env        # Environment variables

```

<br>

##### Creating Project Folder

* **django_boiler_plate** - *The project root*
  ```
    ~/django_boiler_plate  
        |__ /django_boiler_plate  
            |-- __init__.py
            |-- asgi.py  
            |-- settings.py  
            |-- urls.py  
            |-- wsgi.py  

  ```
  All  files will be created using the command.
  ```
        django-admin startproject <project-name>
  ```

<span></span>

##### Creating Application Folder

* **api_v0** - *The application module directory*
  ```
    |__ /api_v0  
         |__ /migrations  
            |-- __init__.py
         |-- __init__.py
         |-- admin.py  
         |-- apps.py  
         |-- models.py  
         |-- serializers.py  
         |-- tests.py  
         |-- urls.py  
         |-- views.py  
  ```
  The files required by the application module will be stored in **api_v0** folder. we can have **n** no.of application modules in our project.
  The Application module structure are generated by
  ```
    python manage.py startapp <app-name>
    ```

  NB: The urls.py will be need to add manually for storing module level url configurations.

<span></span>

<br>

##### Creating A Virtual Environment

Using a virtual environment brings with it a ton of benefits. Virtual environments allow you to manage separate package installations for different projects. They essentially allow you to create a “virtual” isolated Python installation and install packages into that virtual installation. When you switch projects, you can simply create a new virtual environment and not have to worry about breaking the packages installed in the other environments. It is always recommended to use a virtual environment while developing Python applications.

Run the following to create a new virtual environment with pip installed.

* **venv** - *Python virtual environment*

```
cd ~/project # project is the root folder of project
1. in Windows
python -m venv venv
venv\Scripts\activate
2. in ubuntu
python -m venv env
source venv/bin/activate
```

<br>

##### Creating Application Files

* **.env** - *This file is used to define sensitive credentials like passwords, DB credentials etc...*

<br>

##### Installing Django And Application Dependencies

* **requirements.txt** - *All the application's dependency packages will be defined within this file. Later these dependencies can be installed with pip.*

To install the required packages run the following commands.

```
pip install -r requirements
```

<br>



##### Creating Application Utilities

* **utils** - This folder contains all the functionalities that can be re-used by different modules of the
  application. Re-usable code blocks like string cleaning, date format switching etc.. are some examples of utilities.

  Example structure:
  ```
  |__ /utils
        |-- __init__.py
        |-- pagination.py
        |-- validation_utils.py
  ```

* **static** - *The static files directory*
  ```
  |__ /static
         |__ /css
         |__ /img
  ```
  Static files like custom stylesheets, JS, image etc... will be stored in this folder. Folder structure can be divided based on their file types

<span></span>

<br>

#### Configuring The Project Application

This section explains the basics of some project application configurations.

<br>


##### Step 1: Define Settings

As explained in the previous section, settings.py is used to define required application configurations.

**Step 1**: *Import necessary modules*

```
from environs import Env
```

<span></span>

**Step 2**: *Read the environment variables defined in the .env file*

```
env = Env()
env.read_env()
```

<span></span>

**Step 3**: *Define the necessary configs*

```
db = env.str("db")        # Reads 'api_key' defined in the .env file

db="mysql://root:Passw0rd@127.0.0.1:3306/user_app"
```

<br>

##### Step 2: Define Routes

Normally in projects involving APIs, most of the functionalities are invoked based on API calls. Each API will be designed to perform a specific action depending on the application and these actions/functionalities will be defined inside different modules. So, how does an API invoke a specific function? For that you can use routers to route these API calls to their respective function/task invokers.

Different routes can be created based on the use case and if required sub-routes can also be created.

Example routing:

Router definition (/django_boiler_plate/urls.py)

```
    path("v0/", include("api_v0.urls"))

```

here we are including all the urls from the app **api_v0** to our project with prefix **v0**

<br>

#### Structuring The Application Module Directory

The goal of the "**api_v0**" module, i.e, the application directory/module is  to encapsulate all related **models**, **views**, **urls** together.

<br>

##### Creating Application Modules

* **api_v0** - This folder is to modularize all related functions that can be logically grouped..

    Example structure:
    ```

    |__ /module1  
         |__ /migrations  
            |-- __init__.py
         |-- __init__.py
         |-- admin.py  
         |-- apps.py  
         |-- models.py  
         |-- serializers.py  
         |-- tests.py  
         |-- urls.py  
         |-- views.py  
    |__ /module2  
         |__ /migrations  
            |-- __init__.py
         |-- __init__.py
         |-- admin.py  
         |-- apps.py  
         |-- models.py  
         |-- serializers.py  
         |-- tests.py  
         |-- urls.py  
         |-- views.py  
  ```

<br>


##### Creating Module Models

*  This file defines the data structure/ table structure.

    model definition (/api_v0/models.py)

  Example structure:
  ```

class <model-name>(models.Model):
       <fields with data type>

  ```

after the creation of models need to run the below commands in order to reflect the changes in database.

```
python manage.py makemigrations
python manage.py migrate

```
<br>

##### Creating Module Views

*  This file contains all the services required by the application to handle various
   operations. Services can be anything that can be invoked when hitting an url.

    Views definition (/api_v0/views.py)

  Example structure:
  ```
  class <class_name>(viewsets.ModelViewSet):
      def list():
       # operations for listing data
      def create():
       # operations for creating data
      def update():
       # operations for updating data  
      def delete():
       # operations for deleting data
  ```

<br>

##### Creating Module Routes

*   This file contains routers to route all API calls to their related modules.

Example routing:

Router definition (/api_v0/urls.py)

  Example structure:
  ```
    router = DefaultRouter(trailing_slash=False)

    router.register(r"register", RegisterViewSet, basename="register")

    urlpatterns = [
    path(r'', include(router.urls)),
    ]
  ```

<br>


#### Launch The Application Server

Running the application server is pretty simple, all you need to do is specify the server ip and port details in the run.py file and then launch the server as shown below<sup>[[*see*](#host-port-config)]</sup>:

```
cd ~/project
source venv/bin/activate
python manage.py runserver
```


#### Documentation link

The api link is given below

https://www.getpostman.com/collections/9dbc16c372511f9e809c