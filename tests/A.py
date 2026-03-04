import requests

url = "http://43.142.161.61:8003/api/data?token=mock_token_123456"

headers = {
    "X-Token": "mock_token_83ba55ff-34c7-45bd-9868-a00e37669c54"
}

data = {
    "name": "",
    "value": ""
}

r = requests.post(url, headers=headers, data=data)

print(r.status_code)
print(r.text)