from typing import List

from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import datetime


HISTORY_LENGTH = 60 * 60 * 24 * 1


def _get_sitemap_urls(robots_url: str) -> List[str]:
    robots_txt = requests.get(robots_url).text
    sitemaps = [l for l in robots_txt.split('\n') if l.startswith('Sitemap')]
    news_sitemaps = [s.split()[1].strip() for s in sitemaps if 'news' in s or 'article' in s]
    return news_sitemaps


def get_article_urls_from_web(url: str) -> List[dict]:
    # TODO: sanitize input, ensure the page base url was passed in
    sitemap_urls = _get_sitemap_urls(urljoin(url, 'robots.txt'))
    article_urls = []
    while sitemap_urls:
        sitemap_url = sitemap_urls.pop()
        sitemap_content = requests.get(sitemap_url).content
        sitemap_xml = BeautifulSoup(sitemap_content, 'xml')

        if sitemap_xml.find('sitemapindex'):
            sitemaps = sitemap_xml.findAll('sitemap')
            print(f'Found new {len(sitemaps)} sitemaps...')
            for sitemap in sitemaps:
                sitemap_urls.append(sitemap.find('loc').text)
        elif sitemap_xml.find('urlset'):
            urls = sitemap_xml.findAll('url')
            print(f'Processing {len(urls)} URLs...')
            for url in urls:
                if not url.find('news:news'):
                    # Those are some old weird articles, fuck them :D
                    continue

                news_info = url.find('news:news')
                pub_date = news_info.find('news:publication_date').text
                pub_date = pd.Timestamp(pub_date)
                title = news_info.find('news:title')
                url = url.find('loc').text

                # TODO: alternatively we could do this filtering later, but this will be more memory efficient
                age = int(datetime.now().timestamp()) - int(pub_date.timestamp())
                if age > HISTORY_LENGTH:
                    continue

                article_urls.append({
                    'title': title,
                    'url': url,
                    'timestamp': int(pub_date.timestamp()),
                    'source': website_url
                })

    return article_urls


if __name__ == '__main__':
    websites = [
        'https://www.novinky.cz',
        'https://www.bbc.com',
        'https://www.theguardian.com'
    ]
    urls = []
    for website_url in websites:
        urls.extend(get_article_urls_from_web(website_url))

    print(f'Loaded a total of {len(urls)}')

    df = pd.DataFrame(urls)
    df.to_csv('articles.csv')
    print(df.head())
