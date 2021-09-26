fa_token_name = "irrtesttoken"
fa_token_value = "n257t6tkstj287bnl7puhl7j3saif4i42s96eagp"

client_installation = "hoegh"
asset_class = "SimpleAssetAllocation"
query_name = ""
fa_api_key = "PORT_DATA"

def get_analytics_url():
    return "https://"+client_installation+".fasolutions.com/rs/secure/fa/api/v2.0/analytics?includesubs=true"

def get_query_url(query_name):
    return "https://"+client_installation+".fasolutions.com/rs/secure/fa/api/v1.0/query/"+query_name+"/run"

headers = {
    'Content-Type': "application/json",
    'Accept': "application/json",
    'fa-token-name': fa_token_name,
    'fa-token-value': fa_token_value,
    'cache-control': "no-cache",
    }

# Bad response error message
bad_resp = {"data": "Bad response from FA Solutions. Please try again"}
