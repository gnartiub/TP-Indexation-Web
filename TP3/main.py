import json
import pandas as pd
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import string



class Recherche():
    def __init__(self, user_query, index_file , documents_file, type_filter = None ):
        self.user_query = user_query
        self.index_file = index_file
        self.index = {}
        self.documents_file = documents_file
        self.documents = {}
        self.type_filter = type_filter

    def load_index(self):
        with open(self.index_file,"r") as file:
            # Read the content of the file
            file_content = file.read()
            data = json.loads(file_content)

        return data

    def load_documents(self):
        with open(self.documents_file,"r") as file:
            # Read the content of the file
            file_content = file.read()
            data = json.loads(file_content)

        return data
        

    def linear_ranking(doc):
        return len(doc[1]['tokens'])

 #Fonction de recherche et de classement de documents
    def search_and_rank_documents(index, query):
        # Lire la requête utilisateur et la tokenizer
        query_tokens = query.lower().split()

        # Filtrer les documents pour ne conserver que ceux qui contiennent tous les tokens de la requête
        filtered_documents = []
        for doc_id, doc in index.items():
            if all(token in doc['tokens'] for token in query_tokens):
                filtered_documents.append((doc_id, doc))

    def tokenize(self, textes):
        '''
            une tokenization avec un split sur les espaces
            Tous les tokens ont été lowerisés
        '''

        stop_words = set(stopwords.words('french'))

        tokens = word_tokenize(textes)
        tokens = [token.lower() for token in tokens if token.lower() not in stop_words and token.lower() not in string.punctuation]
        
        return tokens

    def transform(self, tokens):
        # Initialiser un stemmer NLTK pour le français
        stemmer = SnowballStemmer("french")    
        # Appliquer le stemming à chaque token de la requête
        stemmed_tokens = [stemmer.stem(token) for token in tokens]
        
        return stemmed_tokens
        
    def filter_documents(self, query_tokens_transformed):
        # Fonction pour filtrer les documents qui contiennent tous les tokens de la requête
        filtered_documents = {}
        for token in query_tokens_transformed:
            if token in self.index:
                for doc_id, doc_info in self.index[token].items():
                    if all(t in doc_info['positions'] for t in query_tokens_transformed):
                        if doc_id not in filtered_documents:
                            filtered_documents[doc_id] = doc_info
                        else:
                            # Mise à jour du count et des positions pour les documents existants
                            filtered_documents[doc_id]['count'] += doc_info['count']
                            filtered_documents[doc_id]['positions'].extend(doc_info['positions'])
        return filtered_documents

    def preprocessing(self,doc):
        tokens = self.tokenize(doc)
        transformed_tokens = self.transform(tokens)
        return transformed_tokens

    def linear_ranking(self, filtered_documents):
        # Fonction de ranking linéaire
        # Tri des documents par count (nombre total d'occurrences des tokens)
        return sorted(filtered_documents.items(), key=lambda x: x[1]['count'], reverse=True)

    def run(self):
        # Charger l'index des documents
        self.index = self.load_index()
        self.documents = self.load_documents()
        # Preprocessing la requête de l'utilisateur
        print("Preprocessing...")
        transformed_query_tokens = self.preprocessing(self.user_query)

        filtered_documents = self.filter_documents(transformed_query_tokens)
        print("Ranking...")
        # Effectuer le ranking linéaire des documents filtrés
        ranked_documents = self.linear_ranking(filtered_documents)
        print(ranked_documents)
        # Récupérer les titres et urls des documents
        documents_info = []

        for doc_id, doc_info in ranked_documents:
            document = self.documents.get(doc_id, {})  # Obtenir les informations du document à partir du fichier JSON des documents
            documents_info.append({
                'Titre': document.get('title', ''),
                'Url': document.get('url', '')
            })

        # Enregistrer les informations des documents dans un fichier JSON
        with open('TP3/results.json', 'w', encoding='utf-8') as outfile:
            json.dump(documents_info, outfile, indent=4, ensure_ascii=False)




        
if __name__ == "__main__":

    user_query = 'taille de sa culotte'
    Recherche(user_query, index_file="TP3/content_pos_index.json", documents_file="TP3/documents.json").run()