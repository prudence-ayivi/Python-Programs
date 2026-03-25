import requests
import json

response = requests.get("https://data.minorplanetcenter.net/api/get-obs", json={"desigs": ["2023 AB"], "output_format":["XML"]})

if response.ok:
    xml_string = response.json()[1]['XML']
    print(xml_string)
else:
    print("Error: ", response.status_code, response.content)