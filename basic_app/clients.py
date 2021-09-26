import requests
import json
from basic_app import const

from .models import ClientList


# Function for getting client data from FA. The clients to be included needs to have SIMPLE in external ID
def get_clients():
    # Name of Query in FA Solutions
    query_name = "BoardSimpleClients"

    # API Call to FA to get the result of the query
    responseFA1 = requests.request("POST", const.get_query_url(query_name), headers=const.headers)
    fa_clients = json.loads(responseFA1.text)
    client_codes = []
    for dic in fa_clients:
        port = dic.pop('portfolios', None)
        dic['start_date'] = dic['start_date'][:10]
        dic['parent'] = [dic['parent']]
        if any(c['code'] == dic['code'] for c in client_codes):
            for client in client_codes:
                if client['code'] == dic['code']:
                    old = client['all']
                    client['all'] = old + [port]
        else:
            dic['all'] = [port]
            client_codes.append(dic)

    new_clients = {i['code']: i for i in client_codes}

    if client_codes:
        ClientList.objects.all().delete()
        for client in client_codes:
            try:
                ClientList.objects.create(code=client['code'],
                                          parent=client['parent'],
                                          currency=client['currency'],
                                          start_date=client['start_date'],
                                          name=client['name'],
                                          portfolios=client['all'])
            except:
                print("Client already exist")
    return new_clients


# Run the function and assign the result to the variable clients. A dictionary with all client data.
# clients = get_clients()

#
# def get_client_list():
#     clients = get_clients()
#     CLIENTS = []
#     for client in clients:
#         CLIENTS.append((client, clients[client]['name']))
#     CLIENTS = tuple(CLIENTS)
#     return CLIENTS


def update_clients():
    global clients
    clients = get_clients()
