# Library Imports
import pandas as pd
import requests
import json
from basic_app import strategy
from basic_app import const

# Input
# start = datetime.now()

# Column names for the final output. theme is filled in by python from reporting_dimensions
df_columns = ['theme', 'name', 'endDate', 'mv', 'code', 'share', 'twrBmMTD',
              'twrMTD', 'twrLocYTD', 'twrBmYTD', 'twrYTD', 'PnlMTD', 'PnlYTD', 'bookvalue',
              'commitmentTotal', 'committedCapital']  # when FA bug fixed ,'remainingCommitment'


# Function for creating the json data to be sent to the FA API
def create_parameters_json(pfIds, startdate, enddate, grouped_by, code):
    # Reporting fields to ask from FA API Analytics+. Number of fields must match df_columns -1 (theme not included)
    reporting_fields = ['name', 'endDate', 'analysis(GIVEN).marketValue', 'code',
                        'analysis(GIVEN).shareOfTotal', 'analysis(MTD).twrBm', 'analysis(MTD).twr',
                        'analysis(GIVEN).twrSec', 'analysis(GIVEN).twrBm', 'analysis(GIVEN).twr',
                        'analysis(MTD).totalNetProfitsOrig', 'analysis(GIVEN).totalNetProfitsOrig',
                        'analysis(GIVEN).purchaseTradeAmount', 'analysis(GIVEN).commitmentTotal',
                        'analysis(GIVEN).committedCapital']  # when FA bug fixed ,'analysis(GIVEN).remainingCommitment'

    # Check if the reporting month is in this month or last month, to determine correct FA format
    # if enddate.year != startdate.year:
    #     mtd_tag = "CALMONTH-1"
    # elif enddate.month == startdate.month:
    #     mtd_tag = "CALMONTH-0"
    # else:
    #     mtd_tag = "CALMONTH-"+str(int(startdate.month)-int(enddate.month))

    # Replace MTD with the correct month format
    mtd_tag = "CALMONTH-0"
    reporting_fields = [x.replace("MTD", mtd_tag) for x in reporting_fields]

    # The dictionary start at the second field in df_columns ([1:]) as this value does not come from Analytics+
    reporting_dict = dict(zip(df_columns[1:], reporting_fields))

    api_fields = [key + "=" + value for key, value in reporting_dict.items()]

    # Creating the total DataFrame
    # reporting_df = pd.DataFrame(columns=df_columns)
    data = {
        'startDate': startdate.strftime("%Y-%m-%d"),
        'endDate': enddate.strftime("%Y-%m-%d"),
        'pfIds': pfIds}
    params1 = {
        'key': const.fa_api_key,
        'endDate': enddate.strftime("%Y-%m-%d"),
        'locale': "en_US",
        'includeChildren': "true",
        'includeData': "false",
        'dataFields': ["date", "indexedValue"],
    }

    analysisFields = api_fields
    params1['analysisFields'] = analysisFields
    params1['dataTimePeriodCode'] = "GIVEN"
    params1['calculateIrr'] = "false"
    params1['calculateContribution'] = "false"
    timePeriodCodes = ["GIVEN", mtd_tag]
    params1['timePeriodCodes'] = timePeriodCodes
    params1['grouppedByProperties'] = grouped_by
    if code:
        params1['groupCode'] = code
    data['paramsSet'] = [params1]
    return json.dumps(data)


def get_analytics(payload):
    response = requests.request("POST", const.get_analytics_url(), data=payload, headers=const.headers)
    if not response:
        return const.bad_resp
    json_data = json.loads(response.text)
    json_data = json_data['analytics']['grouppedAnalytics']['PORT_DATA']['grouppedAnalytics']
    if not json_data:
        return const.bad_resp
    json_data = [x['fields'] for x in json_data]
    return json_data


def return_analytics(portfolio, startDate, endDate):
    params = create_parameters_json(portfolio, startDate, endDate, ["SECTOR"], "SimpleAssetAllocation")
    json_data = get_analytics(params)
    df = pd.DataFrame(json_data)
    # Get Strategic Allocations
    strategy_dictionary, bm_note = strategy.get_strategic(portfolio, startDate, endDate)

    if strategy_dictionary:
        strategy_df = pd.DataFrame(strategy_dictionary)
        try:
            df = df.join(strategy_df.set_index('code'), on='code', how='outer')
            df['name'].fillna(df['asset_class'], inplace=True)
            df['strategic'] = df['strategic'] / 100
            df['delta'] = (df['strategic'] - df['share']) * df['mv'].sum()
        except:
            return const.bad_resp, const.bad_resp, const.bad_resp

    df.fillna(0, inplace=True)
    df.sort_values('code', inplace=True)
    overview_dict = df.to_dict('records')
    params = create_parameters_json(portfolio, startDate, endDate, ["PORTFOLIO"], None)
    total_dict = get_analytics(params)
    return overview_dict, bm_note, total_dict
