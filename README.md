# Scholapp Server
Our server initializes multiple flask apps as microservices from a JSON file configuration provided to our microservices manager.

Those apps include:

 1. Video streamer microservice
 2. Image saver microservice
 3. Chat microservice
 4. DB microservice
 5. Audio streamer microservice

Our JSON file configuration allows you to reuse the same flask app with various different ports and parameters available for the required app.

The currently existing apps are currently used with our client side, which sends REST requests to get and post data from and into the server.
