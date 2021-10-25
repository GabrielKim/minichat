import re
import pytest

def checkVaildIPAddressTnF(ipaddr: str) -> bool:
    # references : 
    # https://somjang.tistory.com/entry/leetCode-468-Validate-IP-Address-Python
    # https://www.geeksforgeeks.org/python-program-to-find-the-type-of-ip-address-using-regex/
    # https://gist.github.com/mnordhoff/2213179
    # for ipv4
    __ipv4re = '^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'

    if re.search(__ipv4re, ipaddr) is None:
        return False
    return True

def test_ipv4_success():
    assert checkVaildIPAddressTnF("192.168.0.1") is True
    assert checkVaildIPAddressTnF("10.0.1.1") is True

def test_ipv4_fail():
    assert checkVaildIPAddressTnF("asdadasdasd") is False
    assert checkVaildIPAddressTnF("1050:0:0:0:5:600:300c:326b") is False