import json

from .fa_data_points import data_points


def create_data_points(list_of_data):
    return [i + "=" + data_points[i] for i in list_of_data]


def calc_perc_return(sec_type, twr, profit, ongoingcharges, averagemv):
    if sec_type not in ["Cash", "CURRENCY"]:
        return twr
    adjusted_profit = profit + ongoingcharges
    if averagemv == 0:
        return 0
    elif averagemv < 0:
        return -adjusted_profit / averagemv
    else:
        return adjusted_profit / averagemv


def create_basic_parameters(startDate=None, endDate=None, portfolioId=None):
    params = {}
    if startDate:
        params['startDate'] = startDate.strftime("%Y-%m-%d")
    if endDate:
        params['endDate'] = endDate.strftime("%Y-%m-%d")
    if portfolioId:
        params['portfolioId'] = portfolioId
    return json.dumps(params)
