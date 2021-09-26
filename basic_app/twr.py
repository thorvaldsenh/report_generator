# Library Imports
import pandas
import requests
import json
from datetime import datetime,timedelta
# from pandas.io.json import json_normalize
from basic_app import const

# Start the timer
df_columns = ['endDate', 'twr', 'bm']
reporting_fields = ['endDate', 'analysis(GIVEN).twr', 'analysis(GIVEN).twrBm']
timePeriodCodes = ["DAYS-0"]
frequency="DAYS-0"

def create_api_fields():
    reporting_dict = dict(zip(df_columns,reporting_fields))
    api_fields = []

    for key, value in reporting_dict.items():
        api_value = key+"="+value
        api_fields.append(api_value)

    return api_fields

# Creating the total DataFrame
reporting_df = pandas.DataFrame(columns=df_columns)

# Function for creating the json data to be sent to the FA API
def create_parameters_json_twr(fields, portfolio, startDate, endDate):
    data = {}
    data['startDate'] = startDate.strftime("%Y-%m-%d")
    data['endDate'] = endDate.strftime("%Y-%m-%d")
    data['pfIds'] = portfolio
    params1 = {}
    params1['key'] = const.fa_api_key
    params1['endDate'] = endDate.strftime("%Y-%m-%d")
    params1['locale'] = "en_US"
    params1['includeChildren'] = "true"
    params1['includeData'] = "true"
    params1['includeData'] = "false"
    params1['dataFields'] = ["date","indexedValue"]
    analysisFields = fields
    params1['analysisFields'] = analysisFields
    params1['dataTimePeriodCode'] = "GIVEN"
    params1['calculateIrr'] = "false"
    params1['calculateContribution'] = "false"
    timePeriodCodes = ["GIVEN"]
    params1['timePeriodCodes'] = timePeriodCodes
    params1['frequency'] = frequency
    params1['grouppedByProperties'] = ["PORTFOLIO"]
    data['paramsSet'] = [params1]
    return json.dumps(data)


# Function for getting analytics data from FA API and creating a dataframe from it
def get_analytics_twr(payload):
    response = requests.request("POST", const.get_analytics_url(), data=payload, headers=const.headers)
    print(response)
    if not response:
        return const.bad_resp
    try:
        json_resp = json.loads(response.text)
    except:
        return {"data": "Bad response from FA Solutions. Please try again"}
    print(response.text)
    json_resp = json.dumps(json_resp['analytics']['grouppedAnalyticsTimeSeries']['PORT_DATA']['timeSeriesSelected'])
    df = pandas.read_json(json_resp)
    df = pandas.json_normalize(df['fields'])
    df['twr'] = 100+df['twr']*100
    df['bm'] = 100+df['bm']*100
    # df.drop(['grouppedAnalytics'], axis=1, inplace=True)
    df = df[df_columns]
    return df

# def create_dataframe():
#     df_json_data = create_parameters_json(api_fields, pfIds)
#     try:
#         df = get_analytics(df_json_data)
#     except:
#         return {"data": "Bad response from FA Solutions. Please try again"}
#     dicret = df.to_dict('records')
#     return dicret

def return_twr(portfolio, startDate, endDate):
    print(portfolio)
    print(startDate)
    print(endDate)
    api_fields = create_api_fields()
    df_json_data = create_parameters_json_twr(api_fields, portfolio, startDate, endDate)
    print(df_json_data)
    df = get_analytics_twr(df_json_data)
    try:
        dicret = df.to_dict('records')
    except:
        return {"data": "Bad response from FA Solutions. Please try again"},{"data": "Bad response from FA Solutions. Please try again"}

    twr_dict = {'access_records': dicret}

    labels = df['endDate'].tolist()
    twrs = df['twr'].tolist()
    bms = df['bm'].tolist()

    data = {
            "labels": labels,
            "twrs": twrs,
            "bms": bms,
        }
    data2 = df.values.tolist()
    data2.insert(0,['Date','TWR','BM'])
    return data, data2
