import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from secrets import API_key

class Octopus:
    API_entry_point = "https://api.octopus.energy/v1/"
    def __init__(self):
        pass

    def fetch_tariff(self):
        tariffs_endpoint = "products/AGILE-18-02-21/electricity-tariffs/E-1R-AGILE-18-02-21-C/standard-unit-rates/"
        link = self.API_entry_point + tariffs_endpoint
        r = requests.get(link, auth = (API_key,"")).json()
        tariffs = pd.json_normalize(r["results"])
        tariffs ['valid_from'] = [(datetime.strptime( timestamps, "%Y-%m-%dT%H:%M:%SZ")) for timestamps in tariffs['valid_from']]
        tariffs['valid_to'] = [(datetime.strptime(timestamps, "%Y-%m-%dT%H:%M:%SZ")) for timestamps in tariffs['valid_to']]
        #tariffs.to_excel(r'C:\Users\Davide Solla\PycharmProjects\OctopusQuery\sink\tariffs.xlsx')
        return tariffs

    def plot_tariff(self):
        tariffs = self.fetch_tariff()
        print(tariffs)
        plt.plot(tariffs['valid_from'],tariffs['value_exc_vat'])
        plt.title('Energy Cost Projection')
        plt.xlabel('Time Period')
        plt.ylabel('Energy Price per Kwh (GBP excl VAT)')
        plt.style.use('seaborn-paper')
        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()
        plt.show()

    def fetch_energ_consumption(self):
        endpoint= "electricity-meter-points/1200050242456/meters/21L4369794/consumption/"
        link = self.API_entry_point + endpoint
        r = requests.get(link, auth=(API_key, "")).json()
        consumptions = pd.json_normalize(r["results"])
        if consumptions.empty:
            print("-------------------------------------------------------")
            print("No data on energy consumptions available at this time")
            print("Check the website or reach out to your energy provider")
            print("-------------------------------------------------------")
        else:
            print (consumptions)
        return consumptions

run=Octopus()
run.fetch_energ_consumption()
run.plot_tariff()

'typing some comment to test first push from mac'