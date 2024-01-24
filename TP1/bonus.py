import requests
from time import sleep
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET


def get_all_entries_from_xml(url) :
    r = requests.get(url, stream=True,verify=False)
    soup = BeautifulSoup(r.text, "xml")
    # URLS
    all_url_tags = soup.find_all("url")
    allUrls = []
    for urls in all_url_tags :
        allUrls.append(urls.findNext("loc").text)
    # SITEMAPS
    sitemapList = soup.find_all("sitemap")
    allSitemaps = []
    for sitemap in sitemapList:
        allSitemaps.append(sitemap.findNext("loc").text)
    return ({"sitemaps" : allSitemaps, "urls" : allUrls})

def get_urls_recursively(url) :
    xml = get_all_entries_from_xml(url)
    allUrls = xml['urls']
    sitemaps = xml['sitemaps']
    visitedSitemaps = []
    while (sitemaps) :
        for sitemap in sitemaps :
            if sitemap not in visitedSitemaps :
                visitedSitemaps.append(sitemap)
                xml = get_all_entries_from_xml(sitemap)
                sitemaps.extend(xml['sitemaps'])
                for elt in xml['urls'] :
                    allUrls.append(elt)
            else :
                sitemaps.remove(sitemap)
    return(allUrls)


def read_sitemap(url):

    r = requests.get(url)
    soup = BeautifulSoup(r.text,"xml")
    sitemapList = soup.find_all("sitemap")
    allSitemaps = []
    for sitemap in sitemapList:
        allSitemaps.append(sitemap.findNext("loc").text)


    return allSitemaps

def can_crawl(url, user_agent="TrangCrawler"):
    rp = RobotFileParser()
    rp.set_url(urljoin(url, '/robots.txt'))
    rp.read()

    return rp.can_fetch(user_agent, url)



def main(url, max_urls_per_page=5, max_total_urls=50):
    visited_urls = set()
    to_visit_urls = [url]

    while to_visit_urls and len(visited_urls) < max_total_urls:
        current_url = to_visit_urls.pop(0)

        if current_url not in visited_urls:
            try:
                response = requests.get(current_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "lxml")  # Use lxml parser

                    # Process the page content here

                    print(f"Page downloaded successfully: {current_url}")

                    # Extract links from the page
                    links = soup.find_all('a', href=True)
                    for link in links[:max_urls_per_page]:
                        new_url = link['href']
                        if new_url.startswith('http') and new_url not in visited_urls:
                            to_visit_urls.append(new_url)

                    visited_urls.add(current_url)
                else:
                    print(f"Failed to download page. Status Code: {response.status_code}")

            except requests.exceptions.Timeout:
                print("Timeout error. Retrying or handling appropriately...")
            except requests.exceptions.RequestException as e:
                print(f"Error during request: {e}")

            sleep(3)  # Politeness delay

    print(f"End of exploration. {len(visited_urls)} pages downloaded.")

    # Write the crawled URLs to a file
    with open("crawled_webpages.txt", "w") as file:
        for crawled_url in visited_urls:
            file.write(crawled_url + "\n")

if __name__ == "__main__":
    # URL du sitemap
    sitemap_url = "https://ensai.fr/sitemap.xml"
    
    # Lire le sitemap pour obtenir plus d'URLs
    urls_from_sitemap = read_sitemap(sitemap_url)

    # Ajouter les URLs du sitemap à la liste des URLs à visiter
    for sitemap_url in urls_from_sitemap:
        if sitemap_url.startswith('http'):
            main(sitemap_url, max_urls_per_page=10, max_total_urls=100)