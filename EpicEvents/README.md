# EpicEvents
A website using Django admnistration website as the frontend and a RESTful API using Django Rest Framework as the backend.
This website is meant to allow the management of users with different roles, clients, their contracts and events related to them.

## Setup and execution:
This website can be installed and deployed locally following these steps:

### Setup
1. Clone the repository using`$git clone https://github.com/Corentin-Br/Projet-12.git` or downloading [the zip file](https://github.com/Corentin-Br/Projet-12/archive/refs/heads/master.zip).
2. Create the virtual environment with `$ py -m venv env` on windows or `$ python3 -m venv env` on macos or linux.
3. Activate the virtual environment with `$ env\Scripts\activate` on windows or `$ source env/bin/activate` on macos or linux.
4. Install the dependencies with `$ pip install -r requirements.txt`.
5. Make sure PostgreSQL is installed. If it's not, you can download it [here](https://www.postgresql.org/download/)
5. If you don't have a Postgres database named EpicEvents created, you'll need to create it. You can follow the instructions [here](https://www.postgresql.org/docs/current/sql-createdatabase.html)
6. Get in the folder EpicEvents with `$ cd EpicEvents`, and create a file named `.env` which will need to have two entries: `django_key` which will be the secret key used by the application, and `db_password` which will be the password to the Postgres database you're using.
7. Run the command `$ python manage.py migrate` to create the required tables in the database.

### Execution
1. If that's not already the case, activate the virtual environment as you did during the setup.
2. Get in the folder EpicEvents with `$ cd EpicEvents`
3. Deploy the website locally with `$ python manage.py run server`


### Use
1. After deploying the website, use the command `$ python manage.py createsuperuser` to create an admin user with corresponding logs.
2. You can access the login page [here](localhost:8000/admin/login), where you can then start populating and modifying the database.