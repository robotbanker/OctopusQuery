import requests
import pandas as pd
from datetime import datetime, timedelta
import calendar
import matplotlib.pyplot as plt
from secrets import API_key


class OctopusConsumption:
    dailycharge = 0.2330  # GBP VAT Inc - standing charge per each day.
    pricekwh = 0.2017  # GBP VAT Incl
    API_entry_point = "https://api.octopus.energy/v1/"
    dailychrg = {
        '': dailycharge / 48,
        'hour': dailycharge / 24,
        'day': dailycharge,
        'week': dailycharge * 7,
        'month': dailycharge * 30
    }

    def __init__(self):

        self.daily_consumption = self.fetch_energ_consumption(group_by='day', page_size=25000)
        self.halfhrly_consumption = self.fetch_energ_consumption(group_by='', page_size=25000)

    def fetch_energ_consumption(self, group_by='', page_size=100):
        # sending request to API
        endpoint = f"electricity-meter-points/1200050242456/meters/21L4369794/consumption" \
                   f"/?page_size={page_size}&group_by={group_by}"
        link = self.API_entry_point + endpoint
        r = requests.get(link, auth=(API_key, "")).json()
        # cast and clean data
        consumptions = pd.json_normalize(r["results"])
        consumptions['price'] = consumptions['consumption'] * self.pricekwh
        consumptions['standing charge'] = self.dailychrg[group_by]
        consumptions['totalprice'] = consumptions['price'] + consumptions['standing charge']
        # parse date time strings as datetime
        consumptions['interval_start'] = [(datetime.strptime(timestamps, "%Y-%m-%dT%H:%M:%S%f%z")) for timestamps in
                                          consumptions['interval_start']]
        consumptions['interval_end'] = [(datetime.strptime(timestamps, "%Y-%m-%dT%H:%M:%S%f%z")) for timestamps in
                                        consumptions['interval_end']]
        consumptions['interval_start'] = pd.to_datetime(consumptions['interval_start'], utc=True)
        consumptions['interval_end'] = pd.to_datetime(consumptions['interval_end'], utc=True)
        # handle exception, if no data received print message to console:
        if consumptions.empty:
            print("-------------------------------------------------------")
            print("No data on energy consumptions available at this time")
            print("Check the website or reach out to your energy provider")
            print("-------------------------------------------------------")
        else:
            return consumptions


    def meter_reading(self):
        """this method returns the LTD energy consumption by first querying last 25,000 days from the API."""
        consumptions = self.daily_consumption
        ltd_consumption = consumptions['consumption'].sum()
        print(f'Your life to date energy consumption is {ltd_consumption} kWh.')

    def rolling_consumption(self):
        """return consumption as of yesterday and current month and prior month"""
        consumption = self.halfhrly_consumption  # use half hourly API
        # from octopus timestamp create two columns with time and day
        consumption['string time'] = [x.strftime('%Y-%m-%d') for x in consumption['interval_start']]
        consumption['timestamp'] = [x.strftime('%H:%M') for x in consumption['interval_start']]
        # find yesterday date
        yesterday = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d')
        # pull metrics for yesterday consumption
        yesterday_consumption = consumption.copy()[consumption['string time'] == yesterday]  # pandas permutations are
        # done on a copy of the original pandas
        busiest_hours = yesterday_consumption.nlargest(n=3, columns=['consumption', 'totalprice'])
        hours = []
        [hours.append(x) for x in busiest_hours['timestamp']]
        # find current and prior months
        current_month = datetime.today().strftime('%m')
        current_year = datetime.today().strftime('%Y')
        current_month_string = datetime.today().strftime('%B')
        prior_month_date = datetime.today().replace(day=1) - timedelta(1)
        prior_period_month = prior_month_date.strftime('%m')
        prior_period_year = prior_month_date.strftime('%Y')
        prior_month_string = prior_month_date.strftime('%B')
        # pull metrics for current and prior months
        current_month_data = consumption[(consumption['interval_start'].dt.month == int(current_month)) &
                                         (consumption['interval_start'].dt.year == int(current_year))]
        prior_month_data = consumption[(consumption['interval_start'].dt.month == int(prior_period_month)) &
                                       (consumption['interval_start'].dt.year == int(prior_period_year))]

        current_month_consumption = current_month_data['totalprice'].sum()
        prior_month_consumption = prior_month_data['totalprice'].sum()

        yesterday_float = float((datetime.today() - timedelta(1)).strftime('%d'))
        daily_average = round((current_month_consumption / yesterday_float),2)
        now = datetime.now()
        days_this_month = calendar.monthrange(now.year, now.month)[1]
        projected_expense = daily_average * days_this_month

        consumption_summary = f"Yesterday {yesterday} you consumed a total of " \
                              f"<b>{round(yesterday_consumption['consumption'].sum(), 2)}kWh </b>, "\
                              f"this amount of energy cost you <b>£" \
                              f"{round(yesterday_consumption['totalprice'].sum(), 2)}.\n</b> <br><br> " \
                              f"The busiest 30 minutes periods were the ones at: {', '.join(hours)}, where the total " \
                              f"cost charged was <b>£{round(busiest_hours['totalprice'].sum(), 2)}.</b> <br>" \
                              f" For the month of {current_month_string} you spent <b>£" \
                              f"{round(current_month_consumption, 2)}</b> so far, " \
                              f"while in {prior_month_string} you spent a total of " \
                              f"£ {round(prior_month_consumption, 2)}.<br><br>" \
                              f"Your daily average energy expense for this month is " \
                              f"<b>£{daily_average}</b>.<br>" \
                              f"At this pace, your estimated total expense for the current month equals <b>£{projected_expense}</b>"

        return consumption_summary



class OctopusTariffs:
    API_entry_point = "https://api.octopus.energy/v1/"

    def fetch_tariff(self):
        tariffs_endpoint = "products/AGILE-18-02-21/electricity-tariffs/E-1R-AGILE-18-02-21-C/standard-unit-rates/"
        link = self.API_entry_point + tariffs_endpoint
        r = requests.get(link, auth=(API_key, "")).json()
        tariffs = pd.json_normalize(r["results"])
        tariffs['valid_from'] = [(datetime.strptime(timestamps, "%Y-%m-%dT%H:%M:%SZ")) for timestamps in
                                 tariffs['valid_from']]
        tariffs['valid_to'] = [(datetime.strptime(timestamps, "%Y-%m-%dT%H:%M:%SZ")) for timestamps in
                               tariffs['valid_to']]
        # tariffs.to_excel(r'C:\Users\Davide Solla\PycharmProjects\OctopusQuery\sink\tariffs.xlsx')
        return tariffs

    def plot_tariff(self):
        tariffs = self.fetch_tariff()
        plt.plot(tariffs['valid_from'], tariffs['value_exc_vat'])
        plt.title('Energy Cost Projection')
        plt.xlabel('Time Period')
        plt.ylabel('Energy Price per Kwh (GBP excl VAT)')
        plt.style.use('seaborn-paper')
        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()
        plt.show()
