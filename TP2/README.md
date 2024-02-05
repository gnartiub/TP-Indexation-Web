# TP-Indexation-Web
# NOM Prénom: BUI Thi Quynh Trang
## TP2: Construire un index minimal
### 1. Pour lancer le programme:

```
git clone https://github.com/gnartiub/TP-Indexation-Web.git
cd TP2
python main.py
```


### 2. Explication du code
Dans ce code, on crée une classe Index qui détient pour paramètres (attributs):
**Attributs définis par l'utilisateur:**

- urls_file (str): le chemin vers le fichier d’urls au format json
- stem (bool): Indiquer si vous souhaitez appliquer un stemmer pour créer un nouvel index - mon_stemmer.title.non_pos_index.json
- pos (bool):  Indiquer si vous souhaitez construire un index positionnel stocké dans title.pos_index.json
**Attributs non définis par l'utilisateur:**
- web_index (dict): index non positionnel par défaut de la liste d’urls 
- metadata (dict): Un dictionnaire contient metadata des urls crawlées

Dans le bloc "if __name__ == "__main__":" à la fin de main.py, vous pouvez définir des paramètres de votre choix de l'objet Index.
En lancant run(), le programme va:
- Importer des urls qui a été générée depuis un crawler dans le fichier .json
- Tokenizer tous les documents (title et content) pour l'analyse plus tard.
- Sortir des statistiques sur les documents en utilisant la fonction analyse_stat(). Ces informations enregistrées écrites dans un fichier metadata.json 
- Construire l'index

Les urls crawlées sont stockées sous forme d'un Pandas DataFrame pour faciliter le traitement des informations. Chaque ligne correspond à une url (ou document). Les colonnes sont "url", "title", "content", "h1".
 
**Tokenization**
Pour chaque url, on utilise la fonction word_tokenize() du paquet nltk pour tokenizer le title et le contenu. Les tokens seront ensuite stockés dans des nouvelles colonnes: tokens_title, tokens_content

**Pour les statistiques**
J'ai calculé:
- Le nombre de documents:
- Le nombre de tokens, global et par champs
- La moyenne des tokens par documents, global et par champs
Ces statistiques sont stockés sous format d'un dictionaire comme ci-dessous:
        self.metadata = {
            'Num_documents': 0,
            'total_tokens': 0,
            'doc': {'tokens_title': 0,
                    'tokens_content': 0
                },
            'Avg_tokens_per_document': 0
            'Avg_tokens_title_per_document': 0
            'Avg_tokens_content_per_document': 0
            }


**Pour la construction de l'index title**

Avant créer l'index, on souhaite à filtrer les ponctuations, par exemple: !"#$%&'()*+, -./:;<=>?@[\]^_`{|}~
Les tokens filtrés seront stockés dans une nouvelle colonnes 'tokens_title_filtered'
La construction de l'index est faite avec 'self.create_index(documents_df, 'tokens_title_filtered')'
On parcours tous les documents. Pour chaque token, on crée une liste inversée et on ajoute l'identifiant de Doc dans l’index
Finalement, l'index obtenu est un dictionnaire comme ci-dessous:
{
    "token1": [0,3,7,8,10],
    "token2": [2],
    ...
}

Si l'utilisateur souhaite appliquer un stemmer (stem = True), le processus de création d'un index est un peu près le même comme précédent. Sauf qu'on applique le stemming à chaque token avant parcourir la liste des tokens de chaque document en faisant 'stemmed_tokens = [stemmer.stem(token) for token in tokens]'

Si l'utilisateur souhaite construire un index positionnel (stem = True), cet index sera stocké dans la variable positional_index = defaultdict()
De même, on parcours chaque document et stocke les positions de chaque terme dans le document dans le dictionnaire term_positions sous forme: {token : [list_positions]}
On met à jour l'index positionnel avec les informations du document actuel en parcourant les éléments de dictionnaire term_positions: positional_index[token][doc_id]["position"] = list_positions

**Pour la construction de l'index content**

Dans la fonction run(), après avoir contruit l'index pour les titres, on a ajoute un bloc de code qui ressemble celui précédent en changant justement le nom de colonne en 'tokens_content' pour créer une nouvelle colonne 'tokens_content_filtered'. 
Maintenant la construction de l'index est faite en modifiant le paramètre 'type' de la fonction create_index(). Par défaut, type = title, maintenant en mettant type='content' et col_name= 'tokens_content_filtered', on a réussi à refaire les mêmes étapes. Les index sont enregistrés dans content.non_pos_index.json, content.pos_index or mon_stemmer.content.non_pos_index.json

Le nom de ces fichiers json sont générés d'une manière automatique pour correspondre au paramètre 'type' de la fonction create_index()
