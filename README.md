# Spotlight API

## Docker

- To install Docker `brew cask install docker`

- To install docker compose `pip install docker-compose`

- To build the container, run the command `docker build -t spotlight-api:latest .`

- To run the container after it is built, use the command `docker run -d -p 5000:5000 spotlight-api:latest`

Use `docker ps` to see which containers are currently running. You should see the 
API container running on port 5000 if everything works correctly.

You may also use docker compose to run the service with the command `docker-compose up`.

Check if it worked:

- Install Postman
- Create a POST request. URL: `localhost:5000/login`
- It should fail since the login credentials are not setup yet but it should recognize the request.

## Database Setup
We are using Alembic migrations for the database, which requires an up-to-date migrations folder to be 
generated and applied to your local database. To do this:

If you don't have a `migrations` folder in your root directory, verify that
both the `spotlight_api` and `spotlight_db` containers are both running.

Once this is complete, perform the following:
1. Run `docker exec spotlight_api flask db init`. This creates the `migrations` directory.
2. Run `docker exec spotlight_api flask db migrate`. This uses the `models` module to create
the necessary migrations.
3. Run `docker exec spotlight_api flask db upgrade`. This pushes the migrations to the database.

To verify that the setup worked correctly, use a database viewer or verify using cURL or an API request
tool like Postman.

Create user using a POST request. URL: `localhost:5000/user` with body: 
```
{
    "password":"<enter password>",
    "first_name":"<name>",
    "last_name":"<last name>",
    "email":"<@gmail.com>"
}
```
Login using newly created credentials. URL: `localhost:5000/login` with body: 
```
{
    "password":"<enter password>", 
    "email":"<@gmail.com>"
}
``` 
This should return a token which will be used in authentication.

## Testing
We are using `nosetests` for test discovery and `coverage` for determining test 
coverage. To run the test suite, either run `nosetests` or `coverage run -m nose` 
to generate a test coverage report.

Use `coverage report -m` to generate a command line report for test coverage
and `coverage html` to generate an HTML report.
