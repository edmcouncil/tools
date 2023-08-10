import http.client

conn = http.client.HTTPSConnection("api.data.world")

headers = {
    'Accept': "application/rdf+xml",
    'Authorization': "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJwcm9kLXVzZXItY2xpZW50OnBhd2VsLWdhcmJhY3oiLCJpc3MiOiJhZ2VudDpwYXdlbC1nYXJiYWN6OjphNDIyYTNjZC1lZmZkLTRlYzQtYWExNC0yMzMxOTM5NmRjZTAiLCJpYXQiOjE1ODE2Njg4NDMsInJvbGUiOlsidXNlcl9hcGlfcmVhZCIsInVzZXJfYXBpX3dyaXRlIl0sImdlbmVyYWwtcHVycG9zZSI6dHJ1ZSwic2FtbCI6e319.sFFLMj7NqTUrdHzjz6loIAAGTpgC40aeojrmaPrhPaEkwE-vFFfv1g7eQZxl4iwJ13mNDt83ZSTdeI4hUqA9hg"
}

conn.request("GET", "/v0/sparql/edm-council/current-fibo-development-release?query=DESCRIBE+%3Chttps%3A%2F%2Fspec.edmcouncil.org%2Ffibo%2Fontology%2FFBC%2FFunctionalEntities%2FNorthAmericanEntities%2FUSExampleIndividuals%2FAlphabetIncCorporateAddress%3E", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))