import requests
from time import sleep
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET


def can_crawl(url, user_agent="TrangCrawler/1.0 (+https://ensai.fr/Trangcrawler)"):
    rp = RobotFileParser()
    rp.set_url(urljoin(url, '/robots.txt'))
    rp.read()

    return rp.can_fetch(user_agent, url)

def main(url, max_urls=50):
    visited_urls = set()
    to_visit_urls = [url]

    while to_visit_urls and len(visited_urls) < max_urls:
        current_url = to_visit_urls.pop(0)

        if current_url not in visited_urls and can_crawl(current_url):
            try:
                response = requests.get(url, stream=True,verify=False)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    with open("crawled_webpages1.txt", "a") as file:
                        file.write(current_url + "\n")

                    print(f"Page téléchargée avec succès: {current_url}")

                # Ajouter les liens de la page à la liste des URL à visiter
                    links = soup.find_all('a', href=True)  # Find all elements with the tag <a>
                    for link in links[:5]: # Limiter l'exploration de 5 liens maximum par page
                        new_url = link['href']
                        if new_url.startswith('http') and can_crawl(new_url):
                            to_visit_urls.append(new_url)

                    # Marquer l'URL actuelle comme visitée
                    visited_urls.add(current_url)
                else:
                    print(f"Échec du téléchargement de la page: {current_url}")

            except Exception as e:
                print(f"Erreur lors du téléchargement de la page {url}: {str(e)}")

            sleep(3)
    print(f"Fin de l'exploration. {len(visited_urls)} pages téléchargées.")


if __name__ == "__main__":
    # URL d'entrée
    start_url = "https://ensai.fr/"

    max_pages = 50

    # Liste des domaines interdits (à adapter selon les règles du site)
    #DISALLOWED_DOMAINS = ['example.com']

    main(start_url, max_urls=max_pages)