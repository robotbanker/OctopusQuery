import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from secrets import API_key

pricekwh = 0.2017 # GBP VAT Incl
dailycharge = 0.2330 # GBP VAT Inc - standing charge per each day. this model runs by 30mins slots. Hence the daily
# charge is split across 48 daily periods
halfhrly_charge = dailycharge/48


class Octopus:
    API_entry_point = "https://api.octopus.energy/v1/"
    dailychrg = {
        '': dailycharge / 48,
        'hour': dailycharge / 24,
        'day': dailycharge,
        'week': dailycharge * 7,
        'month': dailycharge * 30
    }


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

    def fetch_energ_consumption(self, group_by='day', page_size=1000):
        endpoint = f"electricity-meter-points/1200050242456/meters/21L4369794/consumption/?page_size={page_size}&group_by={group_by}"
        link = self.API_entry_point + endpoint
        r = requests.get(link, auth=(API_key, "")).json()
        consumptions = pd.json_normalize(r["results"])
        consumptions['price']=consumptions['consumption']*pricekwh
        consumptions['standig charge'] = self.dailychrg[group_by]
        consumptions['totalprice'] = consumptions['price']+consumptions['standig charge']

        if consumptions.empty:
            print("-------------------------------------------------------")
            print("No data on energy consumptions available at this time")
            print("Check the website or reach out to your energy provider")
            print("-------------------------------------------------------")
        else:
            return consumptions

    def meter_reading(self):
        """this method returns the LTD energy consumption by first querying last 25,000 days from the API."""
        consumptions = self.fetch_energ_consumption('day', 25000)
        ltd_consumption = consumptions['consumption'].sum()
        print(f'Your life to date energy consumption is {ltd_consumption} kW/h')


run = Octopus()
run.fetch_energ_consumption()
# run.plot_tariff()
run.meter_reading()
