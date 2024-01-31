import requests
from time import sleep
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET
from protego import Protego
import sqlite3
from datetime import datetime
import hashlib

# Connexion à la base de données (créera la base de données si elle n'existe pas)
conn = sqlite3.connect('web_pages.db')

# Création d'un curseur pour exécuter des requêtes SQL
cur = conn.cursor()

# Création de la table pour stocker les pages web
# Comme une page a un âge de 0 jusqu'à ce qu'elle soit modifiée, par défaut, on va assigner son age comme étant 0 une fois qu'on a crawlé
cur.execute('''CREATE TABLE IF NOT EXISTS WebPages (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL UNIQUE,
                last_modified TEXT,
                age INTEGER NOT NULL DEFAULT 0
            )''')

class Crawler:

    def __init__(self, start_url, max_urls_per_page = 5, max_urls = 50, get_sitemaps = True):
        self.visited_urls = []
        self.urls_to_visit = [start_url]
        self.start_url = start_url
        self.max_urls_per_page= max_urls_per_page
        self.max_urls=max_urls
        self.get_sitemaps = get_sitemaps

    def can_crawl(self, url, user_agent="*"):
        '''
            Fonction qui vérifie si la page web est interdite au crawler
        '''
        r = requests.get(urljoin(self.start_url, "/robots.txt"))
        rp = Protego.parse(r.text)
        # On respecte la politeness en attendant 3 secondes entre chaque appel
        sleep(3)
        return rp.can_fetch(url,user_agent)

    def get_sitemaps_links(self):
        '''
            Cette fonction récupère les sitemaps disponibles dans le fichier 'robots.txt'
            en utilisation le package Protego
        '''
        r = requests.get(urljoin(self.start_url, "/robots.txt"))
        rp = Protego.parse(r.text)
        # On respecte la politeness en attendant 3 secondes entre chaque appel
        sleep(3)
        return rp.sitemaps

    def get_info_from_sitemap(self,sm: str) -> dict:
        '''
            Cette fonction récupère les urls dans un sitemaps.xml 
            en utilisation le package requests pour parser 
        '''
        url_date = {}
        response = requests.get(sm, timeout=10)
        if response.status_code == 200:
            # Parse the XML sitemap to extract URLs
            root = ET.fromstring(response.content)
            for child in root:
                # Pour chaque ligne, on cherche les urls et leurs dates LastMod.
                if child.tag.endswith('url'):
                    loc = child.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
                    lastmod = child.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod').text
                    url_date[loc] = lastmod
            return url_date
        

    def download_url(self, url: str):
        '''
            Cette fonction télécharge les pages web en utilisant leurs urls
            Les liens des pages téléchargées seront stockés dans le fichier crawled_webpages.txt
   
        '''
        response = requests.get(url)
        # Vérifier si le téléchargement est bon
        if response.status_code == 200:
            with open("crawled_webpages.txt", "a") as file:
                file.write(url + "\n")

            print(f"Page téléchargée avec succès: {url}")
            return response.text
        else:
            print(f"Échec du téléchargement de la page: {url}")

    def get_linked_urls(self, url, html):
        '''
            Cette fonction cherche d'autres pages à explorer en analysant les balises des liens
            trouvées dans l'url actuelle
   
        '''        
        # Parser la page html
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            # Chercher tous les liens disponible
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url):
        '''
            Cette fonction ajoute un url dans la liste des urls à visiter (frontier).
            Avant l'ajouter, elle va vérifier si le lien satisfait certaines conditions:
                - le lien n'est pas encore exploré
                - le lien n'est pas encore mis dans la list urls_to_visit (éviter des doublons)
                - le lien peut être crawlé.

   
        '''   
        if url not in self.visited_urls and url not in self.urls_to_visit and self.can_crawl(url):
            self.urls_to_visit.append(url)

    def add_or_update_bdd(self, url, last_modified):
        '''
            Cette fonction ajouter ou met à jours l'élément dans la base de donnée 
            Parce que les dates last_modified sont pris dans les sitemaps, certaines pages en dehors peuvent ne pas voir une date de 
            dernière modification. Pour cela, jon va considérer son age comme etant 0
        '''
        # Chaque document a pour identifiant unique un hash de l’URL
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Vérifier si la page existe déjà dans la base de données
        cur.execute("SELECT * FROM WebPages WHERE url=?", (url,))
        existing_page = cur.fetchone()
        if last_modified is not None:
            age = (datetime.now() - datetime.strptime(last_modified,"%Y-%m-%dT%H:%M:%S+00:00")).days

        if existing_page:
            # Calculer l'âge de la page en jours
            if last_modified is not None:
                age = (datetime.now() - datetime.strptime(last_modified,"%Y-%m-%dT%H:%M:%S+00:00")).days
            else:
                age = 0
            # Mettre à jour l'âge de la page
            cur.execute("UPDATE WebPages SET last_modified=?, age=? WHERE url=?", (last_modified, age, url))
        else:
            # Ajouter la nouvelle page avec un âge initial de 0
            cur.execute("INSERT INTO WebPages (id, url, last_modified) VALUES (?, ?, ?)", (url_hash, url, last_modified))

        conn.commit()
        
    def crawl(self, url: str):
        '''
            Cette fonction va crawler une page avec son url. 
            Ici on va limiter le nombre de lien maximum à explorer par page en utilisant l'attribut max_urls_per_page défini par l'utilisateur

        '''
        # télécharger la page
        html = self.download_url(url)
        # Créer un compteur i pour limiter le nombre de lien maximum à explorer par page
        i = 0
        for url in self.get_linked_urls(url, html):
            # Vérifier si le nombre maximum a été atteint. Continuer
            if i <= self.max_urls_per_page:
                if url not in self.visited_urls and url not in self.urls_to_visit and self.can_crawl(url):
                    self.urls_to_visit.append(url)
                    i += 1
                else:
                    continue
            else:
                break


    def run(self):
        '''
            Cette fonction va lancer le crawler pour les tâches demandées dans le sujet
        '''
        
        url_date = {}
        if self.get_sitemaps:
            # Lire le fichier sitemap.xml des sites pour réduire les requêtes aux urls
            sitemaps = self.get_sitemaps_links()
            for sm in sitemaps:
                dict_url  = self.get_info_from_sitemap(sm)
                for loc in dict_url.keys():
                    self.urls_to_visit.append(loc)
                url_date.update(dict_url)

        while self.urls_to_visit and len(self.visited_urls) < self.max_urls:
            url = self.urls_to_visit.pop(0)
            print(f'Crawling: {url}')
            # Pour gérer des Exceptions qui peuvent être levé durant le processus de crawling et éviter l'arrêt inattendu de code, on va les mettre dans un try bloc
            try:
                self.crawl(url)
                last_modified = url_date.get(url) 
                self.add_or_update_bdd(url, last_modified)
        
            except Exception as e:
                print(f'Failed to crawl {url}: {str(e)}')
            finally:
                self.visited_urls.append(url)
            # Respecter la politesse en attendant 5 secondes entre chaque appel
            sleep(5)


if __name__ == "__main__":
    # URL d'entrée
    start_url = "https://ensai.fr/"

    max_pages = 50
    # Connexion à la base de données (créera la base de données si elle n'existe pas)
    conn = sqlite3.connect('web_pages.db')

    # Création d'un curseur pour exécuter des requêtes SQL
    cur = conn.cursor()

    # Création de la table pour stocker les pages web
    # Comme une page a un âge de 0 jusqu'à ce qu'elle soit modifiée, par défaut, on va assigner son age comme étant 0 une fois qu'on a crawlé

    cur.execute('''CREATE TABLE IF NOT EXISTS WebPages (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL UNIQUE,
                    last_modified TEXT,
                    age INTEGER NOT NULL DEFAULT 0
                )''')
    Crawler(start_url=start_url, max_urls_per_page = 5, max_urls = 50, get_sitemaps = True).run()
    