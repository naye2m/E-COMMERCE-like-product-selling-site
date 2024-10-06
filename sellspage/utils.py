from django.utils.translation import ugettext_lazy as _
import datetime as dt

getFromPromoCode = None


productTypes: list = [
    "Others", #default
    "Fashion",
    "Toys",
    "Electronics",
    "Home",
]

max_promo_length: int = 8

contractsTypes: list = [
    "Facebook",
    "Whatsapp",
    "Imo",
    "Messenger",
    "Bkash",
    "Nagad",
]

def filter_dict(data, keys):
    return {key: data[key] for key in keys if key in data}



def choiceListGen(items: list):
    return ((_(x), _(x)) for x in items)


def timestampFormatter(timestamp: dt.datetime) -> str:
    return timestamp.strftime("%b %d %Y, %I:%M %p")
def timeFormatterLocal(timestamp: dt.datetime) -> str:
    return timestamp.strftime("%d/%m/%Y") # 01/12/2024
    return timestamp.strftime("%d/%m/%y") # 01/12/24
def dateFormatterLocal(timestamp: dt.datetime) -> str:
    return timestamp.strftime("%b %d %Y, %I:%M %p")# 
