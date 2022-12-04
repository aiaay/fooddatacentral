from urllib.request import Request, urlopen
import pandas as pd
import json
import warnings
from pint import UnitRegistry, UndefinedUnitError, DimensionalityError
ureg = UnitRegistry()
ureg.load_definitions('./Data/food_units.txt') 
import numpy as np

# See https://fdc.nal.usda.gov/api-key-signup.html for API key

import requests

def fdc_search(apikey, term, url = 'https://api.nal.usda.gov/fdc/v1/search'): 
    """
    Search Food Central Database, using apikey and string "term" as search criterion.

    Returns a pd.DataFrame of results.
    """
    parms = (('format', 'json'),('generalSearchInput', term),('api_key', apikey))
    r = requests.get(url, params = parms)

    if 'foods' in r.json():
        l = r.json()['foods']
    else: 
        return []

    return pd.DataFrame(l)

def fdc_report(apikey, fdc_id, url = 'https://api.nal.usda.gov/fdc/v1/'):
    """Construct a food report for food with given fdc_id.  

    Nutrients are given per 100 g or 100 ml of the food.
    """
    params = (('api_key', apikey),)

    try:
        r = requests.get(url+"%s" % fdc_id, params = params)

        L = r.json()['foodNutrients']
    except KeyError:
        warnings.warn("Couldn't find fdc_id=%s." % fdc_id)
        return None

    v = {}
    u = {}
    for l in L:
        if l['type'] == "FoodNutrient":
            v[l['nutrient']['name']] = l['nutrient']['number']  # Quantity
            u[l['nutrient']['name']] = l['nutrient']['unitName']  # Units

    #print(l)
    N = pd.DataFrame({'Quantity':v,'Units':u})

    return N

def fdc_units(q,u,ureg=ureg):
    """Convert quantity q of units u to 100g or 100ml."""
    try:
        x = ureg.Quantity(float(q),u)
    except UndefinedUnitError:
        return ureg.Quantity(np.NaN,'ml')

    try:
        return x.to(ureg.hectogram)
    except DimensionalityError:
        return x.to(ureg.deciliter)
