import requests
import json

response = requests.get('https://oda.ft.dk/api/Afstemning?$inlinecount=allpages')

for data in (response.json()['value']):
    print(data['id','konklusion'])
