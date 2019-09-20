from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.api.WLan import WLan
import requests
import argparse
import sys
import time

# manually set wlan off:
# in wlan basic setting page, run in developer mode
# xmlStr="<?xml version=\"1.0\" encoding=\"UTF-8\"?><request><Ssids><Ssid><Index>0</Index><WifiEnable>0</WifiEnable><WifiSsid>ORANGE4</WifiSsid><WifiMac></WifiMac><WifiBroadcast>0</WifiBroadcast><WifiIsolate>0</WifiIsolate><WifiAuthmode>WPA2-PSK</WifiAuthmode><WifiBasicencryptionmodes>WEP</WifiBasicencryptionmodes><WifiWpaencryptionmodes>AES</WifiWpaencryptionmodes><WifiWepKeyIndex>1</WifiWepKeyIndex><WifiWpsenbl>1</WifiWpsenbl><WifiWpscfg>0</WifiWpscfg><WifiRotationInterval>60</WifiRotationInterval><WifiAssociatedStationNum>0</WifiAssociatedStationNum><wifitotalswitch>1</wifitotalswitch></Ssid></Ssids><WifiRestart>0</WifiRestart></request>"
# saveAjaxData('api/wlan/multi-basic-settings', xmlStr, function($xml) {}, {sync:true, enp:false, enpstring:""})

class E5786_AuthorizedConnection(AuthorizedConnection):
    def _initialize_csrf_tokens_and_session(self):
        # Reset
        self.request_verification_tokens = []

        response = requests.get(self.url + "html/home.html")
        self.cookie_jar = response.cookies

        csrf_tokens = self.csrf_re.findall(response.content.decode('UTF-8'))
        if csrf_tokens:
            self.request_verification_tokens = csrf_tokens
        else:
            token = self._get_token()
            if token is not None:
                self.request_verification_tokens.append(token)

class E5786_WLan(WLan):
    def update_basic_settings(self, old_setting, **kwargs):
        new_setting = dict(old_setting)
        for k,v in kwargs.items():
            if k not in new_setting:
                raise Exception("WLan setting '{}' not exist in original settings".format(k))
            new_setting[k] = v
        return self._connection.post('wlan/basic-settings', new_setting)

parser = argparse.ArgumentParser()
parser.add_argument("--wlan", dest="wlan_status", choices=["on", "off"], help="set WLAN status on / off ", required=True)

if __name__ == "__main__":
    options = parser.parse_args()
    connection = E5786_AuthorizedConnection('http://admin:admin@192.168.1.1/')
    # connection = Connection('http://admin:admin@192.168.1.1/')
    client = Client(connection) # This just simplifies access to separate API groups, you can use device = Device(connection) if you want

    print(client.device.information())  # Needs valid authorization, will throw exception if invalid credentials are passed in URL
    print(client.device.signal())  # Can be accessed without authorization
    wlan = E5786_WLan(connection)
    wlan_basic_settings = wlan.basic_settings()
    print(wlan_basic_settings)
    print(wlan.multi_basic_settings())
    print(wlan.station_information())

    if options.wlan_status == "on":
        if wlan_basic_settings["WifiEnable"] == "1":
            print("wlan_status is already on")
            sys.exit()
        wlan.update_basic_settings(wlan_basic_settings, WifiEnable="1", WifiRestart="1")
    else:
        if wlan_basic_settings["WifiEnable"] == "0":
            print("wlan_status is already on")
            sys.exit()
        wlan.update_basic_settings(wlan_basic_settings, WifiEnable="10", WifiRestart="1")

    time.sleep(2)
    print("New settings:\n{}".format(wlan.basic_settings()))
    sys.exit()