import azure.functions as func
import logging


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    return func.HttpResponse("Hello, world!")
