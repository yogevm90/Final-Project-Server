from flask_microservices.test_microservice.test_app import TestApp


def test_test_microservice():
    TestApp("mock").run(host="127.0.0.1", port=5000)
