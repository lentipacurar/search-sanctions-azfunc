import azure.functions as func
from custom_pkg import send_email
from custom_pkg import get_legacy_session
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="search_sanctions", auth_level=func.AuthLevel.ANONYMOUS)
def search_sanctions(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        url = f"https://scsanctions.un.org/en?keywords={name}&per-page=2500&sections=s&sections=s&sort=id&includes={name}&excludes=&committee=&nationality=&reference_from=&reference_to="

        # Make HTTP GET request using custom SSL context
        response = get_legacy_session().get(url)

        # Check if request was successful
        if response.status_code == 200:
            # Send email with response as attachment
            logging.info('This HTTP triggered function executed successfully.')
            return send_email(response.text, name)
        else:
            logging.info('Error occurred while fetching data.')
            return func.HttpResponse('Error occurred while fetching data', status_code=500)
    else:
        return func.HttpResponse(
             'This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.',
             status_code=200
        )
