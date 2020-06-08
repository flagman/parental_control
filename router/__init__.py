import router.auth as auth
import requests
import logging
import time
from urllib3.connectionpool import log

log.setLevel(logging.ERROR)


class RouterError(Exception):
    pass


class RouterDevice():
    def __init__(self, mac, is_enabled, is_online):
        self.mac = mac
        self.is_enabled = is_enabled
        self.is_online = is_online

    def __repr__(self):
        return 'RouterDevice(mac={}, is_enabled={}, is_online={})'.format(self.mac, self.is_enabled, self.is_online)

    @staticmethod
    def devices_with_router_dict(dict):
        return [RouterDevice(device['mac'],
                             device['authority']['wan'] == 1,
                             device['online'] == 1)
                for device in dict['list']]


class Router():
    TOKEN_TTL = 240
    LOGIN = "/cgi-bin/luci/api/xqsystem/login?username=admin&password={enc_password}&logtype=2&nonce={nonce}"
    DEVICE_LIST = "/cgi-bin/luci/;stok={token}/api/misystem/devicelist"
    MAC_FILTER = "/cgi-bin/luci/;stok={token}/api/xqsystem/set_mac_filter?mac={mac}&wan={zero_or_one}"

    def __init__(self, ip, password, key):
        self.ip = ip
        self.password = password
        self.key = key
        self.token = None
        self.token_timestamp = 0

    def _base_url(self):
        return "http://"+self.ip

    def _check_auth(self):
        if not self.token or int(time.time()) - self.token_timestamp > Router.TOKEN_TTL:
            self._login()

    def _login(self):
        logging.info("Logging in...")
        nonce = auth.nonce()
        password = auth.encoded_password(self.key, self.password, nonce)
        url = self._base_url() + \
            Router.LOGIN.format(enc_password=password, nonce=nonce)
        try:
            result = requests.get(url).json()
        except requests.RequestException as error:
            logging.error("Can't login: {0}".format(error))
            raise RouterError()

        if 'token' not in result:
            logging.error("Can't login: no token")
            raise RouterError()

        self.token = result['token']
        self.token_timestamp = int(time.time())

    def device_list(self):
        self._check_auth()
        try:
            url = self._base_url() + \
                Router.DEVICE_LIST.format(token=self.token)
            devices_dict = requests.get(url).json()
        except requests.RequestException as error:
            logging.error("Can't get device list: {0}".format(error))
            raise RouterError()
        return RouterDevice.devices_with_router_dict(devices_dict)

    def set_device_state(self, device: RouterDevice, is_enabled: bool):
        self._check_auth()
        try:
            url = self._base_url() + \
                Router.MAC_FILTER.format(
                    token=self.token, mac=device.mac, zero_or_one=1 if is_enabled else 0)
            result = requests.get(url).json()
        except requests.RequestException as error:
            logging.error("Can't change device state: {0}".format(error))
            raise RouterError()

        if result['code'] != 0:
            logging.error("Can't change device state")
            raise RouterError()
