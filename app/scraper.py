import time
from typing import List

from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import logging
from trafilatura import fetch_url, extract
from tqdm import tqdm

logger = logging.getLogger('root')

# How recent articles to load (default 1 day)
HISTORY_LENGTH = 60 * 60 * 24 * 1
# How many articles to return per each source
RESULT_COUNT = 20

tqdm.pandas()


def _get_sitemap_urls(robots_url: str) -> List[str]:
    robots_txt = requests.get(robots_url).text
    sitemaps = [l for l in robots_txt.split('\n') if l.startswith('Sitemap')]
    news_sitemaps = [s.split()[1].strip() for s in sitemaps if 'news' in s or 'article' in s]
    return news_sitemaps


def get_urls_from_sitemaps(website_url: str, sitemap_urls: List[str]):
    for sitemap_url in sitemap_urls:
        sitemap_content = requests.get(sitemap_url).content
        sitemap_content = BeautifulSoup(sitemap_content, 'xml')

        if sitemap_content.find('sitemapindex'):
            new_sitemap_urls = sitemap_content.findAll('sitemap')
            new_sitemap_urls = [sm.find('loc').text for sm in new_sitemap_urls]
            yield from get_urls_from_sitemaps(website_url, new_sitemap_urls)
        elif sitemap_content.find('urlset'):
            article_urls = sitemap_content.findAll('url')
            for url in article_urls:
                if not url.find('news:news'):
                    # Those are some old weird articles, fuck them :D
                    continue

                news_info = url.find('news:news')
                pub_date = news_info.find('news:publication_date').text
                pub_date = pd.Timestamp(pub_date)
                title = news_info.find('news:title').text
                url = url.find('loc').text

                # TODO: alternatively we could do this filtering later, but this will be more memory efficient
                age = int(datetime.now().timestamp()) - int(pub_date.timestamp())
                if age > HISTORY_LENGTH:
                    continue

                yield {
                    'title': title,
                    'url': url,
                    'timestamp': int(pub_date.timestamp()),
                    'source': website_url
                }


def get_article_urls_from_web(website_url: str) -> List[dict]:
    # TODO: sanitize input, ensure the page base url was passed in
    sitemap_urls = _get_sitemap_urls(urljoin(website_url, 'robots.txt'))
    return list(get_urls_from_sitemaps(website_url, sitemap_urls))


def load_article_content(article_url: str) -> dict:
    downloaded = fetch_url(article_url)
    article = extract(downloaded, favor_precision=True)
    time.sleep(0.1)

    return article


def load_all_atricles(article_df_: pd.DataFrame) -> ...:
    article_df_['content'] = article_df_['url'].progress_apply(load_article_content)
    return article_df_


if __name__ == '__main__':
    websites = [
        #'https://www.novinky.cz',
        'https://www.bbc.com',
        'https://www.theguardian.com'
    ]
    urls = []
    for website_url in websites:
        urls.extend(get_article_urls_from_web(website_url))

    logger.info(f'Loaded a total of {len(urls)}')

    df = pd.DataFrame(urls)
    df = df.sort_values('timestamp', ascending=False).groupby('source').head(RESULT_COUNT).reset_index(drop=True)
    df.to_csv('articles.csv')

    load_all_atricles(df)
