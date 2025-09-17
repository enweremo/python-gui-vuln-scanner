import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class WebCrawler:
    def __init__(self, max_pages=None, stop_flag=None):
        self.visited = set()
        self.max_pages = max_pages
        self.stop_flag = stop_flag  # A mutable object to check for cancel
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    def is_internal_link(self, base_url, link):
        base_netloc = urlparse(base_url).netloc
        link_netloc = urlparse(link).netloc
        return base_netloc == link_netloc or link_netloc == ''

    def crawl(self, start_url):
        queue = [start_url]
        self.visited = set()

        while queue:
            if self.stop_flag and self.stop_flag[0]:
                break

            url = queue.pop(0)
            if url in self.visited:
                continue

            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                title = soup.title.string.strip() if soup.title else 'No Title'
                desc_tag = soup.find('meta', attrs={'name': 'description'})
                description = desc_tag['content'].strip() if desc_tag else 'No Description'

                yield {
                    'URL': url,
                    'Title': title,
                    'Description': description
                }

                self.visited.add(url)

                for tag in soup.find_all('a', href=True):
                    link = urljoin(url, tag['href'])
                    if self.is_internal_link(start_url, link) and link not in self.visited and link not in queue:
                        queue.append(link)

                if self.max_pages and len(self.visited) >= self.max_pages:
                    break

            except Exception as e:
                yield {
                    'URL': url,
                    'Title': 'Error',
                    'Description': str(e)
                }
                self.visited.add(url)
