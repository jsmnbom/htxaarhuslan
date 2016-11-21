# HTXAarhusLAN next gen website
  
## How to set up development environment  

### Set up
(Ideally you should only have to do this once)

1. Install python 3.5
2. Install postgresSQL
3. Set up a database and databse user

    Use pgAdmin to create a new database and new user, then give the user full access to the database.
4. Clone this repository

    `git clone https://github.com/bomjacob/htxaarhuslan.git`
5. Open terminal/cmd and cd into cloned directory

    `cd htxaarhuslan`
6. Install required dependencies

    `pip install -r requirements.txt`
7. Copy the file `.env.base` and rename the copied file to `.env`

    `cp .env.base .env`
8. Fill out configuration in the newly created `.env` file

    You can get a recaptcha key from google. Or just give it a empty string, but then you can't create users via the form on site (do it via the admin site instead).
9. Run database migrations (also always do this if you've pulled new changes from the repository)

    `python mange.py migrate`

### Run server
(Do this everytime you want to run the local dev server)

1. Optionally run a local mail server by running (in another terminal/cmd)

    `python -m smtpd -n -c DebuggingServer localhost:1025`
2. You should now be able to run the development server

    `python manage.py runserver`
