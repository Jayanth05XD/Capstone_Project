import requests

url = "https://books.toscrape.com/"

response = requests.get(url)

print(response.status_code)
print(response.text[:500])