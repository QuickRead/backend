import requests
"""
articles = [
    'https://www.novinky.cz/clanek/ekonomika-svycarsko-zvazuje-i-zestatneni-credit-suisse-40426251#dop_ab_variant=0&dop_source_zone_name=novinky.sznhp.box&dop_req_id=fnNrSFQyREe-202303191706&dop_id=40426251&source=hp&seq_no=2&utm_campaign=&utm_medium=z-boxiku&utm_source=www.seznam.cz',
    'https://www.novinky.cz/clanek/zahranicni-evropa-na-kolotoci-v-nemeckem-munsteru-byl-ubodan-muz-40426240#dop_ab_variant=0&dop_source_zone_name=novinky.web.nexttoart&dop_req_id=zjQlRlKbNei-202303191706&dop_id=40426240'
]

r = requests.post('http://localhost/summarize', json={
    "urls": articles
})

print(f"Status Code: {r.status_code}, Response: {r.json()}")
"""

r = requests.post('http://localhost/api/list_articles', json={
    "url": "https://www.bbc.com"
})

print(f"Status Code: {r.status_code}, Response: {r.json()}")
#"""