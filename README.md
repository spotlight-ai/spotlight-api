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

### Setup database

- View all docker containers: `docker ps`
- Init: `docker exec spotlight_api flask db init`
- Migrate: `docker exec spotlight_api flask db migrate`
- Upgrade: `docker exec spotlight_api flask db upgrade`

Check if it worked:

- Open Postman
- Create user using a POST request. URL: `localhost:5000/user` with body: `{"password":"<enter password>","first_name":"<name>","last_name":"<last name>","email":"<@gmail.com>"}`
- Login using newly created credentials. URL: `localhost:5000/login` with body: `{"password":"<enter password>", "email":"<@gmail.com>"}`. This should return a token which will be used in authentication.
