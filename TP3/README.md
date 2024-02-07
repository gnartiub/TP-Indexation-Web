# TP-Indexation-Web
# NOM Prénom: BUI Thi Quynh Trang
## TP3: Expansion de requête et ranking
### 1. Pour lancer le programme:

```
git clone https://github.com/gnartiub/TP-Indexation-Web.git
cd TP3
python main.py
```


### 2. Explication du code
Dans ce code, on va utiliser des fichiers donnés fournis au format json: title_pos_index.json/content_pos_index.json et documents.json

Comme les deux TP précédents, on va créer une classe Recherche qui présente notre moteur de recherche et détient comme attributs:

**Attributs définis par l'utilisateur:**
- user_query: requête de l'utilisateur
- index_file (str): chemin vers l'index
- documents_file (str): chemin vers le fichier des documents crawlés
- filter_type (str): 'AND' ou 'OR
- weight (bool): False par défaut

**Attributs non définis par l'utilisateur:**
- documents (list): liste des documents 
- index (dict): l'index


Vous trouverez les étapes de processus dans la méthode run(). D'autres méthodes ont été créées pour faciliter la gestion du code.

**a. Chargement des données**
D'abord, on commence par le chargement des fichiers documents.json et title_pos_index.json/content_pos_index.json (selon votre choix, vous pouvez choisir à rechercher au sein des contenus ou juste des titre, ici on suppose que le système cherche uniquement sur les titres des documents)

**b. Pre-processing**
Tout prétraitement fait sur la requête doit être le même que celui fait sur les documents. Ici, on part d'un prétraitement minimal qui contient uniquement 2 étapes: 
- Tokenization: par la fonction word_tokenize() de nltk
- Lowerisation des tokens
Elles sont faite par la fonction tokenize() de la class Recherche
Comme les index fournis ont été appliqués ces transformation, on va faire la même chose sur la requête.

**c. Filtrage**
La fonction filter_documents() a été implémentée pour filtrer les documents en prenant en entrée la liste des tokens de la requête. En itérant sur cette liste de tokens, nous cherchons les documents qui les contiennent.
Selon la dé finition de filter_type ('AND' ou 'OR'), on prend respectivement l'intersection ou union des ensembles.

Ensuite, on souhaite retrouver des informations des documents filtré par la requête sous forme de l'index {token: {docId: {position: [position indices], count: int}, cela va servir à l'étape de ranking pour calculer des scores car on va utiliser les nombres d'occurrences. Ces info seront stocké dans filtered_documents_info

**d. Ranking**
Il existe plusieurs manières de définir une fonction de score pour le classement. Ici, on prend en compte l'importance du nombre d'occurrences des tokens dans les documents. De plus, on applique un poids plus important aux tokens qui ont du sens par rapport aux stop words (la liste des stop words est prédéfinie par nltk.corpus). Les poids sont fixés à 1 si le token est un stop word et à 10 sinon. Finalement, la fonction de score est définie comme suit :
Score <- Somme (weight * count(token))
Cette fonction est implémenté dans la méthode score_function() qui prend en entrée la liste des tokens de la requête, doc_id et filtered_documents_info (dictionnaire qui contient des informations des comptage des documents)

La méthode score_function() sera appelée dans la méthode ranking() qui va itérer sur la liste des documents ayant passé le filtre et les trier par ordre décroissant de score.

**e. Results**

La sortie de la fonction ranking() est sous forme d'une list des tuples. Chaque tuple contient 2 éléments: DocID et score.
Afin de renvoyer une liste de documents au format json (results.json), on va itérer sur les éléments de ranked_documents pour obtenir l'identifiant de document. La méthode get_document_by_id() facilite la récupération de titre et url à partir de son id. Les résultat est stocké dans la liste documents_info.

De plus, on souhaite ajouter quelques statistiques sur le filtrage, par exempl le nombre de documents dans l’index et le nombre de documents qui ont survécu au filtre.

resultat_info = {
    'N_document': len(self.documents),
    'N_document_filtre': len(ranked_documents)
}

En utilisant json.dump, on peut exporter ces résultats dans le fichier results.json

### 3. Point à améliorer
- La fonction ranking peut être amélioré en ajoutant d'autres features, comme par exemple les positions des tokens au sein de document.
- Calculer le  score de bm25 pour