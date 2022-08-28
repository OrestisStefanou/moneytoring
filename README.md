# How to run the app
uvicorn app.main:app --reload

# How to run tests
pytest app/tests/


# Code structure
- models: All the pydantic models that we use to model the data we use in the app.In database subfolder we have the models that are backed with a table in our db and in http subfolder the models that we use to structure the response we get from our http providers
- http: The http clients that we use in the app to make external http calls to our providers
- errors: The custom erros(exceptions) that we use accross the app
- entities: The models that we expose to the clients of the app
- repos: An abstraction on top of the models , any actions that we do to fetch or create any model is happening through the repos classes
- routers: Where we declare the endpoints of the app
- services: Functions that use the repos to perform any crud actions on our models
- controllers: Use the services to perform the neccessary actions an endpoint needs to return a response

# Next steps
1. Transition to another database(Postgres, CockroachDB)
2. Add analytics endpoints?
    1. Get transactions filtered by category
    2. Get transactions filtered by custom category
    3. Endpoints to get amount that spent and amount that was credited per account and total