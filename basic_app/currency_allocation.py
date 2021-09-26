# Library Imports
import pandas
import requests
import json
from datetime import datetime,timedelta
# from pandas.io.json import json_normalize
from basic_app import const

# Column names for the final output. theme is filled in by python from reporting_dimensions
df_columns = ['name', 'share']

# Function for creating the json data to be sent to the FA API
def create_parameters_json(pfIds, startdate,enddate,property):
    # Reporting fields to ask from FA API Analytics+. Number of fields must match df_columns -1 (theme not included)
    reporting_fields = ['name', 'analysis(GIVEN).shareOfTotal' ]

    # The dictionary start at the second field in df_columns ([1:]) as this value does not come from Analytics+
    reporting_dict = dict(zip(df_columns,reporting_fields))

    api_fields = []

    for key, value in reporting_dict.items():
        api_value = key+"="+value
        api_fields.append(api_value)


    # Creating the total DataFrame
    reporting_df = pandas.DataFrame(columns=df_columns)
    data = {}
    data['startDate'] = startdate.strftime("%Y-%m-%d")
    data['endDate'] = enddate.strftime("%Y-%m-%d")
    data['pfIds'] = pfIds
    params1 = {}
    params1['key'] = const.fa_api_key
    params1['endDate'] = enddate.strftime("%Y-%m-%d")
    params1['locale'] = "en_US"
    params1['includeChildren'] = "true"
    params1['includeData'] = "true"
    params1['includeData'] = "false"
    params1['dataFields'] = ["date","indexedValue"]
    analysisFields = api_fields
    params1['analysisFields'] = analysisFields
    params1['dataTimePeriodCode'] = "GIVEN"
    params1['calculateIrr'] = "false"
    params1['calculateContribution'] = "false"
    timePeriodCodes = ["GIVEN"]
    params1['timePeriodCodes'] = timePeriodCodes
    params1['grouppedByProperties'] = property
    data['paramsSet'] = [params1]
    return json.dumps(data)

def get_analytics(payload):
    response = requests.request("POST", const.get_analytics_url(), data=payload, headers=const.headers)
    try:
        json_data = json.loads(response.text)
    except:
        return const.bad_resp
    print(response)
    json_data = json.dumps(json_data['analytics']['grouppedAnalytics']['PORT_DATA']['grouppedAnalytics'])
    df = pandas.read_json(json_data)
    df = pandas.json_normalize(df['fields'])
    df.drop(['grouppedAnalytics'], axis=1, inplace=True)
    df['theme'] = ""
    df = df[df_columns]
    df['share'].clip(lower=0,inplace=True)
    return df

def return_currency_allocation(pfIds, startdate,enddate):
    params = create_parameters_json(pfIds,startdate,enddate,["CURRENCY"])
    try:
        df = get_analytics(params)
    except:
        return const.bad_resp
    try:
        data = df.values.tolist()
    except:
        return const.bad_resp
    
    data.insert(0,['Currency','Allocation'])
    return data
