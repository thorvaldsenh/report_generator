import requests
import json
from basic_app import const
from .tools import create_basic_parameters


# Send GET Request to FA Solution to get the query result for expiring instruments


def get_top_bottom(startDate, endDate, portfolioId):
    query_name = "BoardTopBottom"
    url = const.get_query_url(query_name)

    payload = create_basic_parameters(startDate=startDate, endDate=endDate, portfolioId=portfolioId)
    response = requests.request("POST", url, data=payload, headers=const.headers)
    return {'data': json.loads(response.text)} if response else None


def get_cash(startDate, endDate, portfolioId):
    query_name = "BoardCash"
    url = const.get_query_url(query_name)

    payload = create_basic_parameters(startDate=startDate, endDate=endDate, portfolioId=portfolioId)
    response = requests.request("POST", url, data=payload, headers=const.headers)
    return {'data': json.loads(response.text)} if response else None


def get_commitment(portfolio, endDate):
    query_name = 'BoardCommitment'
    url = const.get_query_url(query_name)

    payload = create_basic_parameters(endDate=endDate, portfolioId=portfolio)
    response = requests.request("POST", url, data=payload, headers=const.headers)
    return {'data': json.loads(response.text)} if response else None
