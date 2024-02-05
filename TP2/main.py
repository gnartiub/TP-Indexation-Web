import json
import pandas as pd
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import string
from collections import defaultdict

def load_crawled_urls_file(file_path):
        '''
            Cette fonction importe des données crawlées dans le fichier .json

            Return:
                    crawled_urls (pd.DataFrame)
        '''
        with open(file_path,"r") as file:
            # Read the content of the file
            file_content = file.read()
            crawled_urls = json.loads(file_content)
        
        crawled_urls = pd.DataFrame(crawled_urls)
        return crawled_urls

class Index():
    def __init__(self, urls_file, stem=False, pos=False ):
        self.urls_file = urls_file
        self.stem = stem
        self.pos = pos
        self.metadata = {
            'Num_documents': 0,
            'total_tokens': 0,
            'doc': {'tokens_title': 0,
                    'tokens_content': 0
                },
            'Avg_tokens_per_document': 0
            }
        self.web_index = {}
    
    def analyse_stat(self, doc: pd.DataFrame):
        '''
            Cette fonction sort des statistiques sur les documents
            Paramètres:
                    doc (pd.DataFrame): documents à traiter
            Return:
                    metadata (dict)
        '''

        # On parcours tous les documents. Pour chacun, on prends les colonnes tokens_title et tokens_content pour faire l'analyse. 
        for i in range(len(doc)):
            tokens_title = doc.loc[i, 'tokens_title']
            tokens_content = doc.loc[i, 'tokens_content']
            
            # Le nombre de tokens global
            self.metadata['total_tokens'] += len(tokens_title) + len(tokens_content)
            # Le nombre de tokens en title
            self.metadata['doc']['tokens_title'] += len(tokens_title)
            # Le nombre de tokens en contenue
            self.metadata['doc']['tokens_content'] += len(tokens_content)

        return self.metadata


    #Fonction pour tokenizer le texte et construire l'index web
    def tokenize(self,doc: pd.DataFrame):
        '''
            Cette fonction va effectuer la tokenization sur l'ensemble des documents, y compris les titres et les contenus.
            Ces listes des tokens seront stockés dans nouvelles colonnes de DataFrame doc
            Paramètres:
                    doc (pd.DataFrame): documents à traiter
            Return:
                    doc (pd.DataFrame)
        '''
        # Tokenizer le titre et le contenu
        tokens_title = []
        tokens_content = []
        for i in range(len(doc)):
            tokens_title.append(word_tokenize(doc.loc[i,'title']))
            tokens_content.append(word_tokenize(doc.loc[i,'content']))

        doc['tokens_title'] = tokens_title
        doc['tokens_content'] = tokens_content
        return doc

        
        
    def create_index(self,doc, col_name, type = 'title'):
        '''
            Cette fonction va construire l'index web, par dé faut, un index non positionnel sera créé et enregistré dans un fichier title.non_pos_index.json
            Si stem = True ou pos = True, d'autres index pourront êtrés crées dans les fichiers différents.
            Paramètres:
                    type : créer un index pour le type d'informations choisi, par exemple pour title ou pour contenu,...
                    doc (pd.DataFrame): documents/urls à traiter
                    col_name: le nom de colonne qui contient des tokens à utiliser pour la construction de l'index.

        '''
        # Construire l'index web
        # Pour chaque token, on crée une liste inversée et on l’ajoute dans l’index

        for idx in doc.index:
            # Tokenizer le texte du document
            tokens = doc.loc[idx,col_name]
            # Ajouter chaque token à l'index web
            for token in tokens:
                if token in self.web_index:
                    self.web_index[token].append(idx)
                else:
                    self.web_index[token] = [idx]

            if self.stem:
                # Si stem = True, une traitement des tokens sera réalisé pour chaque title 
                web_index_stem = {}
                stemmer = SnowballStemmer("french")    
                # Appliquer le stemming à chaque token 
                stemmed_tokens = [stemmer.stem(token) for token in tokens]
                for token in stemmed_tokens:
                    if token in web_index_stem:
                        web_index_stem[token].append(idx)
                    else:
                        web_index_stem[token] = [idx]
                
        for token, token_idx in self.web_index.items():
            token_idx = list(set(token_idx))

        with open(f"TP2/{type}.non_pos_index.json", "w") as json_file:
                    json.dump(self.web_index, json_file) 

        # Si stem = True, un nouvel index - mon_stemmer.title.non_pos_index.json sera enregistré
        if self.stem:
            for token, token_idx in self.web_index.items():
                token_idx = list(set(token_idx))

            with open(f"TP2/mon_stemmer.{type}.non_pos_index.json", "w") as json_file:
                        json.dump(self.web_index, json_file) 
        
        if self.pos:
            positional_index = defaultdict(lambda: defaultdict(lambda: {"position": [], "count": 0}))

            for doc_id, document in enumerate(doc):
                terms = doc.at[doc_id, col_name]  
                term_positions = defaultdict(list)  # Pour stocker les positions de chaque terme dans le document
                for position, term in enumerate(terms):
                    term_positions[term].append(position)

                # Mettre à jour l'index positionnel avec les informations du document actuel
                for term, positions in term_positions.items():
                    positional_index[term][doc_id]["position"] = positions
                    positional_index[term][doc_id]["count"] = len(positions)

            with open(f"TP2/{type}.pos_index.json", "w") as json_file:
                        json.dump(positional_index, json_file) 
    def run(self):

        # Load documents
        documents_df = load_crawled_urls_file(self.urls_file)
        # Chaque document est tokenisé
        print("Tokenizing...")
        documents_df = self.tokenize(documents_df)

        # Sortir des statistiques sur les documents en utilisant la fonction analyse_stat() et calculant d'autres statistiques

        print("Analysing metadata...")
        # Le nombre de documents au total
        n_doc = len(documents_df)
        self.metadata["Num_documents"] = n_doc

        self.metadata = self.analyse_stat(documents_df)
        # La moyenne des tokens (title+contenu) par documents
        self.metadata['Avg_tokens_per_document'] = self.metadata['total_tokens'] / n_doc

        self.metadata['doc']['tokens_title']
        self.metadata['Avg_tokens_title_per_document'] = self.metadata['doc']['tokens_title'] / n_doc
        self.metadata['Avg_tokens_content_per_document'] = self.metadata['doc']['tokens_content'] / n_doc
        # les informations statistiques sont écrites dans un fichier metadata.json 
        with open("TP2/metadata.json", "w") as json_file:
            json.dump(self.metadata, json_file)  

        # Construire un index
        # Avant créer l'index, on souhaite à filtrer les ponctuations, par exemple: !"#$%&'()*+, -./:;<=>?@[\]^_`{|}~
        # Les tokens filtrés seront stockés dans une nouvelle colonnes 'tokens_title_filtered'

        documents_df['tokens_title_filtered'] = None  # Initialize a new column with None values

        for index, row in documents_df.iterrows():
            tokens_title = row['tokens_title']
            if tokens_title is not None:  # Check if tokens_title is not None
                filtered_tokens = [token.lower() for token in tokens_title if token.lower() not in string.punctuation]
                documents_df.at[index, 'tokens_title_filtered'] = filtered_tokens

        print("Start creating index for titles...")
        self.create_index(documents_df, 'tokens_title_filtered')
        print("Index web for titles is successfully created !")

        # OPTIONEL: Créer un index pour content

        documents_df['tokens_content_filtered'] = None  # Initialize a new column with None values
        for index, row in documents_df.iterrows():
            tokens_title = row['tokens_content']
            if tokens_title is not None:  # Check if tokens_title is not None
                filtered_tokens = [token.lower() for token in tokens_title if token.lower() not in string.punctuation]
                documents_df.at[index, 'tokens_content_filtered'] = filtered_tokens

        print("Start creating index for contents...")
        self.create_index(documents_df, 'tokens_content_filtered', type="content")
        print("Index web for contents is successfully created !")
        
        
if __name__ == "__main__":

    urls_file = "TP2/crawled_urls.json"
    Index(urls_file, stem = True, pos=True).run()
    
