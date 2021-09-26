import requests
from datetime import datetime
import json
from basic_app import const
from .tools import create_basic_parameters


# Function to get the strategic allocation for the client and the benchmark component returns
def get_strategic(portfolioId, startDate, endDate):
    query_name = "BoardStrategicAllocation"
    url = const.get_query_url(query_name)

    bom_date = datetime(endDate.year, endDate.month, 1)

    payload_ytd = create_basic_parameters(startDate=startDate, endDate=endDate, portfolioId=portfolioId)
    payload_mtd = create_basic_parameters(startDate=bom_date, endDate=endDate, portfolioId=portfolioId)

    # Send API call to FA To fetch the query called "BoardStrategicAllocation"
    responseFA1 = requests.request("POST", url, data=payload_ytd, headers=const.headers)

    # Send API call to FA To fetch the query called "BoardStrategicAllocation" for MTD data
    responseFA2 = requests.request("POST", url, data=payload_mtd, headers=const.headers)

    # Convert FA responses to proper JSON format
    response_ytd = json.loads(responseFA1.text)
    response_mtd = json.loads(responseFA2.text)
    print(response_ytd)
    for ac in response_ytd:
        ac['bm_return_ytd'] = ac.pop('bm_return', None)
        for j in response_mtd:
            if j['code'] == ac['code']:
                ac['bm_return_mtd'] = j.pop('bm_return', None)
    # Create lists to be used to create the final dictionary to be returned
    # code = []
    # asset_class = []
    # allocation = []
    # strategic = []
    # bm_return_ytd = []
    # bm_return_mtd = []
    # # Loop through the first response to populate the relevant list data
    # for i in response_ytd:
    #     code.append(i['code'])
    #     asset_class.append(i['asset_class'])
    #     allocation.append(i['allocation'])
    #     strategic.append(i['strategic'])
    #     bm_return_ytd.append(i['bm_return_ytd'])
    #     bm_return_mtd.append(i['bm_return_mtd'])
    # # Loop through the second response to populate the MTD benchmark returns
    # # for i in response_mtd:
    # #     bm_return_mtd.append(i['bm_return'])
    # # Convert the lists to a dictionary which will be returned by the function
    # data = {
    #     "code": code,
    #     "asset_class": asset_class,
    #     "allocation": allocation,
    #     "strategic": strategic,
    #     "bm_return_mtd": bm_return_mtd,
    #     "bm_return_ytd": bm_return_ytd,
    # }
    # CREATE FOOTNOTE WITH BM INFO
    footnote = []
    for i in response_ytd:
        if i['strategic'] != 0:
            if not i['bm_name']:
                footnote.append(f"{i['strategic']:.0f}% -undefined-")
            elif i['bm_name'][-3:] == 'NOK':
                footnote.append(f"{i['strategic']:.0f}% {i['bm_name'][:-3].rstrip()}")
            else:
                footnote.append(f"{i['strategic']:.0f}% {i['bm_name']}")
    bm_note = ", ".join(footnote)
    if len(bm_note) == 0:
        bm_note = "No benchmark specified"
    return response_ytd, bm_note
