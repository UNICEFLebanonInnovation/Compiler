import json
import requests


def get_unhcr_principal_applicant(case_number):

    loginData = {'grant_type': 'password', 'username': 'mbazin@unicef.org', 'password': '?45x6UJa'}
    response = requests.post("https://www.unhcrmenadagdata.org/RaisWebApiv2/Token", loginData)
    parsed_json_response = json.loads(response.text)
    print(parsed_json_response['access_token'])

    auth = 'Bearer ' + parsed_json_response['access_token']
    headers = {'Authorization': auth}

    getDataResponse = requests.get(
        "https://www.unhcrmenadagdata.org//RaisWebApiv2/api/GetPAByCase/{id}".format(id=case_number),
        headers=headers
    ).json()
    print(getDataResponse)
