import json
import requests

from .models import ClientList
from basic_app import const


class FaApiRequests:

    def __init__(self, start_date, end_date, client):
        self.start_date = start_date
        self.end_date = end_date
        self.client = client
        self.headers = {'Content-Type': "application/json",
                        'Accept': "application/json",
                        'fa-token-name': const.fa_token_name,
                        'fa-token-value': const.fa_token_value,
                        'cache-control': "no-cache", }
        self.parent_id = client['portfolio_ids']
        self.ultimate_parent = client['ultimate_parent']
        self.asset_class = const.asset_class
        self.installation = const.client_installation
        self.portfolios = [client['portfolio_ids']]

    def get_query(self, query_name, start_date=None, end_date=None, portfolios=None):
        params = {}
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if portfolios:
            params['portfolioId'] = portfolios
        params = json.dumps(params) if bool(params) else None
        print(query_name)
        print(type(query_name))
        query_name = query_name.replace(" ", "%20")
        print(params)
        url = "https://" + self.installation + ".fasolutions.com/rs/secure/fa/api/v1.0/query/" + query_name + "/run"
        response_fa = requests.request("POST", url=url, data=params, headers=self.headers)
        if response_fa:
            return json.loads(response_fa.text)
        else:
            return None

    def get_fa_portfolio_info(self):
        url = f"https://{self.installation}.fasolutions.com/rs/secure/fa/api/v1.0/portfolio/{self.parent_id}"
        response_fa = requests.request("GET", url=url, headers=self.headers)
        if response_fa:
            return json.loads(response_fa.text)
        print("bad response")
        return const.bad_resp

    def get_strategy_api(self, portfolios, end_date=None):
        url = "https://" + self.installation + ".fasolutions.com/rs/secure/fa/api/v1.0/strategy/" + \
              str(portfolios)
        if end_date:
            url = url + "?date=" + end_date
        response_fa = requests.request("GET", url=url, headers=self.headers)
        if not response_fa:
            return None
        strategy = json.loads(response_fa.text)['root']['strategy']
        if len(strategy) > 0:
            return strategy
        else:
            return None

    # Not in use
    def get_fa_account_info(self, portfolios, cash_only="true"):
        portfolios = "%2C".join(str(i) for i in portfolios)
        api_url = ".fasolutions.com/rs/secure/fa/api/v1.0/accounts/bankStatement?portfolio_ids="
        url = f"https://{self.installation}{api_url}{portfolios}&startdate={self.end_date}" \
              f"&enddate={self.end_date}&cash_only={cash_only}"
        print(url)
        response_fa = requests.request("GET", url=url, headers=self.headers)
        print(response_fa)
        if response_fa:
            return json.loads(response_fa.text)
        else:
            return None

    def get_pe_portfolios(self):
        data = self.get_query("ysFrontGetPePorts", portfolios=self.portfolios)
        print(data)
        if data:
            self.pe_ports = [i['portfolios'] for i in data]
        return self.pe_ports

    def get_direct_portfolios(self, input_portfolios):
        data = self.get_query("ysFrontGetDirectPorts", portfolios=input_portfolios)
        if data:
            self.direct_portfolios = [i['portfolios'] for i in data]
        return self.direct_portfolios

    def create_parameters_json(self, analytics_fields, start_date=None, groups=None, group_code=None,
                               frequency=None, irr="false", portfolios=None, drilldown_setting=None,
                               data_time_period_code=None, custom_columns=None, sort_by=None):
        # Check if the reporting month is in this month or last month, to determine correct FA format
        data = {'startDate': start_date or self.start_date,
                'endDate': self.end_date,
                'pfIds': portfolios or [self.parent_id]
                }

        if drilldown_setting:
            data['includeDrilldownPositions'] = 'true'

        params1 = {'key': "PORT_DATA"}
        # params1['key'] = "PORT_DATA"  # Optional way to name a group of groupped analytics. If left blank= 1,2,3...
        if start_date:
            params1[
                'startDate'] = start_date  # Start used if GIVEN time period code used. Otherwise can be left out
        params1['endDate'] = self.end_date  # Analysis date
        params1['locale'] = "en_US"  # Locale in which language to return the group names etc.
        # Whether to include groups and sub groups. If false, only top level (total) analyzed
        params1['includeChildren'] = "true"
        if drilldown_setting:
            params1['drilldownEnabled'] = 'true'
        params1['includeData'] = "false"  # Whether to include the time series of indexed return data
        # Optional time period code to define for which period the data is to be included.
        # Default is from start to end date, if time period code not given.
        params1['dataFields'] = ["date",
                                 "indexedValue"]
        params1['analysisFields'] = analytics_fields
        if custom_columns:
            params1['customColumnDefinitions'] = custom_columns
        if data_time_period_code:
            params1['dataTimePeriodCode'] = "GIVEN"
        params1['calculateIrr'] = irr  # Whether to include IRR calculation
        params1['calculateContribution'] = "false"  # Whether to include twr contribution calculation
        params1['timePeriodCodes'] = ["GIVEN", "CALMONTH-0",
                                      "CALYEAR-0"]  # Comma separated list of time period codes that are analyzed
        # If given, analysis is done over time e.g monthly as in this case. If left out, only one analysis is done.
        # Do not use with sorting or limit!
        if frequency:
            params1[
                'frequency'] = frequency
        if groups:
            params1['grouppedByProperties'] = groups  # Comma separated list of groups and sub groups
        if group_code:
            params1['groupCode'] = group_code
        if sort_by:
            params1['sortBy'] = sort_by  # Sort the sub groups by their market value...
        # params1['ascending'] = 'false'  # ... descending
        # params1['limit'] = 5  # return top 5
        data['paramsSet'] = [params1]
        print(json.dumps(data))
        return json.dumps(data)

    def get_analytics(self, payload, subs="true"):
        url = "https://" + self.installation + ".fasolutions.com/rs/secure/fa/api/v2.0/analytics?includesubs=" + subs
        print(url)
        response = requests.request("POST", url, data=payload, headers=self.headers)
        if response:
            return json.loads(response.text)
        elif response.status_code == 404:
            return "No response from FA"
        else:
            print(response)
            print(response.text)
            return None

    def get_strategy_analyzer(self, portfolio=None, monthly=None, twr_type="GROSS", rebalance="MONTHLY"):
        portfolio_ids = portfolio or self.parent_id

        params_set = [{"rebalanceFrequency": rebalance,
                       "twrType": twr_type,
                       "strategyPortfolioId": portfolio_ids,
                       "locale": "en_US"}]
        if monthly:
            monthly_analysis_parameter = {"rebalanceFrequency": rebalance,
                                          "twrType": twr_type,
                                          "strategyPortfolioId": portfolio_ids,
                                          "analysisFrequency": "CALMONTHS-1",
                                          "locale": "en_US"}
            params_set.append(monthly_analysis_parameter)
        url = f"https://{self.installation}.fasolutions.com/rs/secure/fa/api/v1.0/strategyAnalyzer"
        print(url)
        params = {"startDate": self.start_date,
                  "endDate": self.end_date,
                  "portfolioIds": [portfolio_ids],
                  "includeSubPortfolios": "true",
                  "paramsSet": params_set}
        print(json.dumps(params))
        response = requests.request(method="POST", url=url, data=json.dumps(params), headers=self.headers)
        print(bool(response))
        if response:
            return json.loads(response.text)
        print(response.text)
        return None

    def get_transactions(self, start_date=None, end_date=None, portfolio=None):
        if not portfolio:
            portfolio = ",".join(str(i) for i in self.portfolios)
        url = f"https://{self.installation}.fasolutions.com/rs/secure/fa/api/v2.0/transaction/{portfolio}?status=OK"

        if start_date:
            url = url + f"&startdate={start_date}"
        if end_date:
            url = url + f"&enddate={end_date}"
        print(url)
        response = requests.request(method="GET", url=url, headers=self.headers)
        if response:
            return json.loads(response.text)
        else:
            return None

    def create_client_info(self):
        json_data = self.get_fa_portfolio_info()
        self.portfolios = [self.parent_id] + [x['id'] for x in json_data['portfolios'] if 'portfolios' in json_data]
        self.currency_code = json_data['currency']['name'] if 'currency' in json_data else self.currency_code
        return {'portfolios': self.portfolios,
                'primaryContact': json_data['primaryContact']['name'] if 'primaryContact' in json_data else None,
                'contacts': [x['name'] for x in json_data['contacts'] if 'contacts' in json_data],
                'mandatePortfolios': [dict(zip(('id', 'name'), values)) for values in
                                      [(x['id'], x['name']) for x in json_data['portfolios'] if
                                       ' #MANDATE' in x['tagList'] and 'portfolios' in json_data]],
                'privateEquityPortfolios': [dict(zip(('id', 'name'), values)) for values in
                                            [(x['id'], x['name']) for x in json_data['portfolios'] if
                                             '#PRIVATE_EQUITY' in x['tagList'] and 'portfolios' in json_data]],
                'limitGroupCode': [dict(zip(('id', 'name'), values)) for values in
                                   {(x['limitDefinition']['limitGroup']['code'],
                                     x['limitDefinition']['limitGroup']['name']) for x in json_data['allLimits'] if
                                    'limitDefinition' in x and 'limitGroup' in x['limitDefinition']}],
                'country': json_data['country']['name'] if 'country' in json_data else None,
                'currency': self.currency_code,
                'benchmark': {
                    'name': json_data['benchmark']['name'] if 'benchmark' in json_data and
                                                              'name' in json_data['benchmark'] else None,
                    'benchmarkDataString': json_data[
                        'benchmarkDataString'] if 'benchmarkDataString' in json_data else None}
                }

    def retrieve_client_info(self):
        client = ClientList.objects.get(code=self.client['client_code'])
        client_info = ClientList.objects.get(client=client)
        print(client_info)
        self.portfolios = client_info.portfolios
        self.currency_code = client_info.currency
        self.benchmark = client_info.benchmark
        return "success"

        # json_data = json.loads(response_fa.text)
        # self.currency_code = json_data['currency']['name']
        # self.benchmark = json_data['benchmarkDataString']
        # portfolios = [self.parent_id] + [x['id'] for x in json_data['portfolios']]
        # self.portfolios = self.portfolios + portfolios
