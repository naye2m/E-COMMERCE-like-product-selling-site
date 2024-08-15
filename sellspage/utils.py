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


def choiceListGen(items: list):
    return [(x, x) for x in items]


def timestampFormatter(timestamp: dt.datetime) -> str:
    return timestamp.strftime("%b %d %Y, %I:%M %p")


def recDir(Obj, escapeFunction=True) -> dict:
    tmp: dict = {}
    for k in dir(Obj):
        if "__" in k:
            continue
        try:
            prop = eval(f"Obj.{k}") #todo wtf😑
        except KeyError:
            continue
        t = type(prop)
        # print(k,t,prop)
        if t in [type(lambda x: x), callable]:
            if not escapeFunction:
                tmp[k] = str(t)
            continue
        elif t in [str, list, int, float, complex, tuple, set]:
            tmp[k] = [str(t), prop]
        else:
            tmp[k] = recDir(prop, escapeFunction)
    return tmp


def recKeys(Obj, escapeFunction=True) -> dict:
    tmp: dict = {}
    for k in Obj.keys():
        if "__" in k:
            continue
        try:
            # prop = eval(f"Obj.{k}")
            prop = Obj[k]
        except KeyError:
            continue
        t = type(prop)
        # print(k,t,prop)
        if t in [type(lambda x: x), callable]:
            if not escapeFunction:
                tmp[k] = str(t)
            continue
        elif t in [str, list, int, float, complex, tuple, set]:
            tmp[k] = [str(t), prop]
        else:
            tmp[k] = recKeys(prop, escapeFunction)
    return tmp




def recAny(Obj, escapeFunction=True) -> dict:

    tmp: dict = {}
    if type(Obj) is dict:
        Obkeys = Obj.keys()
    else:
        Obkeys = dir(Obj)
    for k in Obkeys:
        if "__" in k:
            continue
        try:
            if type(Obj) is dict:
                prop = Obj[k]
            else:
                prop = eval(f"Obj.{k}")
        except KeyError:
            continue
        t = type(prop)
        # print(k,t,prop)
        if t in [type(lambda x: x), callable]:
            if not escapeFunction or 1:
                tmp[k] = [prop.__doc__,str(t)]
            continue
        elif t in [str, list, int, float, complex, tuple, set]:
            tmp[k] = [str(t), prop]
        else:
            tmp[k] = recAny(prop, escapeFunction)
    return tmp


import django
def init():
    recAny(django)