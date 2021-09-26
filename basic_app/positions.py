# Library Imports
import pandas
import requests
import json
from datetime import datetime
from basic_app import const
from .tools import get_data_points, calc_perc_return

# Column names for the final output. theme is filled in by python from reporting_dimensions
df_columns = ['ISIN', 'name', 'amount', 'purchaseprice', 'bookvalue', 'price', 'mv',
              'profitsytd', 'twr', 'twrsec', 'securitytype', 'ongoingcharges']

# Creating the total DataFrame
reporting_df = pandas.DataFrame(columns=df_columns)


# Function for creating the json data to be sent to the FA API
def create_parameters_json(pfIds, startdate, enddate):
    # Reporting fields to ask from FA API Analytics+. Number of fields must match df_columns -1 (theme not included)
    reporting_fields = ['security.isinCode', 'name', 'analysis(GIVEN).amount', 'analysis(GIVEN).purchaseUnitPrice',
                        'analysis(GIVEN).purchaseTradeAmount', 'analysis(GIVEN).marketUnitPrice',
                        'analysis(GIVEN).marketValue',
                        'analysis(GIVEN).totalNetProfitsOrig', 'analysis(GIVEN).twr', 'analysis(GIVEN).twrsec',
                        'security.securityTypeCode', 'analysis(GIVEN).exPostPfCostCat2']

    analytics_fields = get_data_points(['ISIN', 'name', 'amount', 'purchaseprice', 'bookvalue', 'price', 'mv',
                                        'profitsytd', 'twr', 'twrsec', 'securitytype', 'ongoingcharges', 'averagemv'])

    # Check if the reporting month is in this month or last month, to determine correct FA format
    if enddate.year != datetime.now().year:
        mtd_tag = "CALMONTH-1"
    elif enddate.month == datetime.now().month:
        mtd_tag = "CALMONTH-0"
    else:
        mtd_tag = "CALMONTH-" + str(int(datetime.now().month) - int(enddate.month))

    # Replace MTD with the correct month format
    reporting_fields = [x.replace("MTD", mtd_tag) for x in reporting_fields]
    analytics_fields = [x.replace("MTD", mtd_tag) for x in analytics_fields]

    # The dictionary start at the second field in df_columns ([1:]) as this value does not come from Analytics+
    # reporting_dict = dict(zip(df_columns, reporting_fields))

    # api_fields = [key + "=" + value for key, value in reporting_dict.items()]
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

    analysisFields = analytics_fields
    params1['analysisFields'] = analysisFields
    params1['dataTimePeriodCode'] = "GIVEN"
    params1['calculateIrr'] = "false"
    params1['calculateContribution'] = "false"
    timePeriodCodes = ["GIVEN", mtd_tag]
    params1['timePeriodCodes'] = timePeriodCodes
    params1['grouppedByProperties'] = ["PORTFOLIO", "SECTOR", "SECURITY"]
    params1['groupCode'] = "SimpleAssetAllocation"
    data['paramsSet'] = [params1]
    return json.dumps(data)


def get_analytics(payload):
    response = requests.request("POST", const.get_analytics_url(), data=payload, headers=const.headers)
    try:
        json_data = json.loads(response.text)
        return json_data['analytics']['grouppedAnalytics']['PORT_DATA']['grouppedAnalytics']
    except:
        return {"data": "Bad response from FA Solutions. Please try again"}


def return_positions(portfolio, startDate, endDate):
    params = create_parameters_json(portfolio, startDate, endDate)
    analytics_info = get_analytics(params)

    if not analytics_info:
        return (const.bad_resp for x in range(6))

    # positions = analytics_info[0]['fields']['grouppedAnalytics']
    topsum = analytics_info[0]['fields']
    positions = topsum.pop('grouppedAnalytics', None)
    print(topsum)
    print(positions)
    # Create dictionary with top and bottom return_positions
    positions_list = []
    for item in positions:
        item['fields']['profitsytdadjfees'] = item['fields']['profitsytd'] + item['fields']['ongoingcharges']
        item['fields']['perc_return'] = calc_perc_return(item['fields']['name'], item['fields']['twr'],
                                                         item['fields']['profitsytd'],
                                                         item['fields']['ongoingcharges'], item['fields']['averagemv'])
        for i in item['fields']['grouppedAnalytics']:
            i['fields']['profitsytdadjfees'] = i['fields']['profitsytd'] + i['fields']['ongoingcharges']
            i['fields']['perc_return'] = calc_perc_return(i['fields']['securitytype'], i['fields']['twr'],
                                                          i['fields']['profitsytd'],
                                                          i['fields']['ongoingcharges'], i['fields']['averagemv'])
            positions_list.append(i['fields'])
    top_bottom_df = pandas.DataFrame(positions_list)
    top_bottom_df = top_bottom_df.loc[top_bottom_df['securitytype'] != 'CURRENCY']
    top_bottom_df.sort_values(by='profitsytd', ascending=False, inplace=True)
    top = top_bottom_df[:3].to_dict('record')
    top_bottom_df.sort_values(by='profitsytd', ascending=True, inplace=True)
    bottom = top_bottom_df[:3].to_dict('record')

    total_twr = analytics_info[0]['fields']['twr']

    fees = {'fields': {'name': 'Portfolio Fees',
                       'profitsytdadjfees': -sum(x['fields']['ongoingcharges'] for x in positions),
                       'perc_return': -sum(x['fields']['ongoingcharges'] for x in positions) / sum(
                           x['fields']['averagemv'] for x in positions)}}
    profit_before_fees = {
        'fields': {
            'name': 'Total Before Fees',
            'bookvalue': sum(x['fields']['bookvalue'] for x in positions),
            'mv': sum(x['fields']['mv'] for x in positions),
            'profitsytdadjfees': sum(
                x['fields']['profitsytdadjfees'] for x in positions
            ),
            'perc_return': total_twr - fees['fields']['perc_return'],
        }
    }

    return positions, top, bottom, [profit_before_fees], [fees], [topsum]
