import json
import requests


def get_unhcr_token():
    loginData = {'grant_type': 'password', 'username': 'mbazin@unicef.org', 'password': '?45x6UJa'}
    response = requests.post("https://www.unhcrmenadagdata.org/RaisWebApiv2/Token", loginData)
    parsed_json_response = json.loads(response.text)

    auth = 'Bearer ' + parsed_json_response['access_token']
    return {'Authorization': auth}


def get_unhcr_principal_applicant(case_number):

    headers = get_unhcr_token()

    getDataResponse = requests.get(
        "https://www.unhcrmenadagdata.org//RaisWebApiv2/api/GetPAByCase/{id}".format(id=case_number),
        headers=headers
    ).json()
    return getDataResponse


def get_unhcr_individuals(case_number):

    headers = get_unhcr_token()

    getDataResponse = requests.get(
        "https://www.unhcrmenadagdata.org//RaisWebApiv2/api/GetIndividualsByCase/{id}".format(id=case_number),
        headers=headers
    ).json()
    return getDataResponse
