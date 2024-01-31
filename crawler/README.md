# TP-Indexation-Web
# NOM Prénom: BUI Thi Quynh Trang
## TP1: Creation d'un web crawler
### 1. Pour lancer le programme:

```
git clone https://github.com/gnartiub/TP-Indexation-Web.git
cd crawler
python main.py
```

### 2. Pour afficher le database via terminal:
```
sqlite3 web_pages.db
select * from WebPages;
```

### 3. Explication du code
Dans ce code, on cree une classe Crawler qui détient pour paramètres (attributs):
**Attributs définis par l'utilisateur:**
- visited_urls (list):List des urls visités et téléchargés
- max_urls_per_page (int): Le nombre de liens maximum à explorer par page. Par défaut, il vaut 5 (le programme s’arrêtes à l’exploration de 5 liens maximum par page)
- max_urls (int):  Le nombre de liens maximum à télécharger 
- get_sitemaps (bool): Pour indiquer si vous souhaiter lire le fichier sitemap.xml des sites pour réduire les requêtes aux urls
**Attributs non définis par l'utilisateur:**
- urls_to_visit (list): List des urls trouvée à visiter (frontier)
- start_url (str): Il s'agit d'un seed, l'url de départ

Globalement, on va partir avec le lien de départ ("https://ensai.fr/") (le seed). En partant de ce lien, l'utilisateur peut mettre les paramètres de son choix (détaillé là-dessous). En parcourant les urls dans le frontier (les nouvelles urls sont y ajoutés au fur et à mesure lorsque des nouveaux liens sont découvert dans un page), le programme enregistre les pages trouvées et téléchargées dans un fichier crawled_webpages.txt. Les informations sur ces pages sont aussi stockées dans une base de donnée relationnelle.

On va utiliser SQLite3 pour  créer une base de données relationnelle simple pour stocker les pages web trouvées (url) ainsi que leur
âge, date de dernière modification. D'abord, on commence par la création de la table. 


### 4. Limites/ Points à améliorer pour ce travail
- Ce programme utilise les 'Last Modif' dates disponibles dans les sitemaps.xml pour chaque url. Je n'arrive pas encore à récupérer la date de dernière modification pour n'importe quelle url donnée depuis son html). Pour cette raison, pour les sites en dehors de ces sitemaps, je considère son age comme étant 0

- La partie Multi threader n'est pas encore réalisée.