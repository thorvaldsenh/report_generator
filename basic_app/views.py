from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.timezone import make_aware

from datetime import datetime, date
import json

from basic_app.twr import return_twr

import basic_app.analytics as analytics
from basic_app.query import get_cash
from basic_app import forms
from basic_app import currency_allocation
from basic_app import query
from basic_app.positions import return_positions
import basic_app.clients as clients
from .models import ClientList

User = get_user_model()

client_name = ''
today_date = date.today()
start = datetime(today_date.year, 1, 1)
client_start = datetime.strptime("2019-01-01", "%Y-%m-%d")
end = today_date
parentPf = []
allPf = []
currency = ''


def robots(request):
    data = {}
    return render(request, 'name_app/robots.txt', data, content_type='text/plain')


def documentation(request):
    return render(request, 'documentation.mht')


class HomeView(View):
    def get(self, request, *args, **kwargs):
        form = forms.FormName()
        return render(request, 'index.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = forms.FormName()

        if request.method == 'POST':
            form = forms.FormName(request.POST)
            if '_update' in request.POST:
                clients.get_clients()
                # form.update_clients()
                print("client list updated")
                return HttpResponseRedirect(self.request.path_info)

            else:
                if form.is_valid():
                    global client_name
                    global start
                    global end
                    global parentPf
                    global allPf
                    global currency
                    global client_start
                    client_code = form.cleaned_data['client']
                    start = form.cleaned_data['startDate']
                    end = form.cleaned_data['endDate']

                    client = ClientList.objects.get(code=client_code)
                    client_name = client.name
                    currency = client.currency
                    parentPf = json.loads(client.parent)
                    allPf = json.loads(client.portfolios)
                    client_start = client.start_date

                    print("Client code: " + client_code)
                    print("Client name: " + client_name)
                    print("Parent portfolio number: " + str(parentPf))
                    print("Subportfolio numbers: " + str(allPf))
                    print("Report Start Date: " + str(start))
                    print("Report End Date: " + str(end))
                    print("Client Start Date: " + str(client_start))
                    print("Client currency: " + currency)
                    print('--end of input data--')
                    return HttpResponseRedirect('/report/')
                else:
                    print('form not valid')
        else:
            print("request method not post")
        return render(request, 'index.html', {'form': form})


@never_cache
def report(request):
    names = {'client_name': client_name, 'start': start, 'end': end, 'currency': currency}
    overview, bm_note, topsum = analytics.return_analytics(parentPf, start, end)
    # top_bottom = get_top_bottom(start, end, allPf)
    cash = get_cash(start, end, allPf)
    try:
        chart_date = make_aware(datetime(end.year - 3, end.month, end.day))
    except:
        chart_date = make_aware(datetime(end.year - 3, end.month, end.day - 1))
    chart_date = max(chart_date, client_start)
    print("chart date is:")
    print(chart_date)
    twrdata, data2 = return_twr(allPf, chart_date, end)
    positions, top, bottom, profit_before_fees, fees, discard = return_positions(parentPf, start, end)
    dicret = {'names': names, 'overview': overview, 'topsum': topsum, 'bm_note': bm_note,
              'top': top, 'bottom': bottom, 'cash': cash, 'positions': positions,
              'profit_before_fees': profit_before_fees, 'fees': fees,
              'currency_chart': currency_allocation.return_currency_allocation(parentPf, start, end),
              'twr_chart': twrdata, 'commitment': query.get_commitment(allPf, end)}
    my_dict = {'data': dicret}
    months = min(36, ((end.year - client_start.year) * 12) + end.month - client_start.month + (
            end.day > client_start.day > 0))
    my_dict['months'] = months
    # print("********************")
    # print(json.dumps(my_dict, indent=4, default=str))
    return render(request, 'report.html', context=my_dict)
