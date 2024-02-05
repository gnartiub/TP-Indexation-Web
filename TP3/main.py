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
    def __init__(self, user_query, index_file , documents_file, filter_type = 'AND' ,weight = False):
        self.user_query = user_query
        self.index_file = index_file
        self.index = {}
        self.documents_file = documents_file
        self.documents = {}
        self.filter_type = filter_type
        self.weight = weight

    def load_index(self):
        '''
            Cette fonction va importer l'index au format json
            Return:
                data (dict): index des documents
        '''
        with open(self.index_file,"r") as file:
            # Read the content of the file
            file_content = file.read()
            data = json.loads(file_content)

        return data

    def load_documents(self):
        '''
            Cette fonction va importer documents au format json
            Return:
                data (list): une liste des dictionnaires de documents
        '''
        with open(self.documents_file,"r") as file:
            # Read the content of the file
            file_content = file.read()
            data = json.loads(file_content)

        return data
        

    def tokenize(self, textes):
        '''
            Cette fonction executera la tokenization sur le texte donnée. Tous les tokens seront ensuite lowerisés
            Returns:
                tokens (list): Liste des tokens lowerisés
        '''

        tokens = word_tokenize(textes)
        tokens = [token.lower() for token in tokens if token.lower() not in string.punctuation]
        
        return tokens
    ''' 
    def transform(self, doc):

        tokens = self.tokenize(doc)
        # Initialiser un stemmer NLTK pour le français
        stemmer = SnowballStemmer("french")    
        # Appliquer le stemming à chaque token de la requête
        stemmed_tokens = [stemmer.stem(token) for token in tokens]
        
        return stemmed_tokens
    
    '''
    def filter_documents(self, query_tokens_transformed):
        '''
            Cette fonction prend en entrée la liste des tokens de la requête pour filtrer les documents.

            Parameters:
                    query_tokens_transformed (list): liste des tokens de la requête
            Returns:
                    filtered_documents_id (list): List des docId qui ont survécu au filtre
        '''

        
        filtered_documents_id = []
        for token in query_tokens_transformed:
            if token in self.index.keys():
                # Fonction pour filtrer les documents qui contiennent tous les tokens de la requête
                if self.filter_type == 'AND':
                    # Filtrer les documents qui ont tous les tokens de la requête
                     # get all the docId which contains one 
                    doc_ids = set(self.index[token].keys())
                    if not filtered_documents_id:
                        filtered_documents_id = doc_ids
                    else:
                        filtered_documents_id &= doc_ids  # Intersection des ensembles de docIds

                # Fonction pour filtrer les documents qui contiennent au moins un token de la requête
                elif self.filter_type == 'OR':
                    # Filtrer les documents qui ont au moins un token de la requête
                    doc_ids = set(self.index[token].keys())
                    if not filtered_documents_id:
                        filtered_documents_id = doc_ids
                    else:
                        filtered_documents_id = filtered_documents_id | doc_ids 


        return filtered_documents_id

    def add_weight(self, token):
        '''
            BONUS:
            Cette fonction calcule le poids du token en fonction de s'il est un stop word ou non
            
            Parameters:
                    token (str): un token
            Returns:
                    int : les poids pour le token donné
        '''

        stop_words = set(stopwords.words('french'))
        if token.lower() in stop_words:
            return 1  # Poids plus faible pour les stop words
        else:
            return 10  # Poids plus fort pour les tokens significatifs

    def get_compteur(self, token, doc_id, filtered_documents_info):

        if token in filtered_documents_info and doc_id in filtered_documents_info[token]:
            count = filtered_documents_info[token][doc_id]['count']
            return count
        else:
            return 0

    def score_function(self, tokens_requete, doc_id, filtered_documents_info):
        '''
            Cette fonction calcule le score pour un document
            
            Parameters:
                    tokens_requete (list): liste des tokens de la requête
                    doc_id (str): Identifiant d'un document
                    filtered_documents_info (dict): contient informations sur les documents qui ont vécu au filtre, 
                                                    sous format de l'index: {token: {position: [position indices], count: int}}}
            Returns:
                    score (int) : le score du document
        '''       
        # Calculer un score pour un document en fonction de ses caractéristiques de token
        score = 0
        for token in tokens_requete:
            poid = self.add_weight(token) if self.weight  else 1
            # Ajouter le compte du document à la somme existante pour ce docId
            score += poid * self.get_compteur(token, doc_id, filtered_documents_info)
        return score

    # Fonction de ranking linéaire
    def ranking(self,tokens_requete,filtered_documents_id, filtered_documents_info):
        '''
            Cette fonction calcule le score pour tous les documents et les ordonner par leurs scores
            
            Parameters:
                    tokens_requete (list): liste des tokens de la requête
                    filtered_documents_id (list): liste des identifiants des documents qui on vécu au filtre
                    filtered_documents_info (dict): contient informations sur les documents qui ont vécu au filtre, 
                                                    sous format de l'index: {token: {position: [position indices], count: int}}}
            Returns:
                    ranked_doc_counts (list) : liste des tuple (id, score) en l'ordre décroissant de score
        '''     
        
        # Classer les doc_counts par ordre décroissant des scores
        docs_score = {}  # Dictionnaire pour stocker le scorefder pour chaque docId

        # Itérer la liste des documents pour calculer leurs scores
        for doc_id in filtered_documents_id:
            docs_score[doc_id]  = self.score_function(tokens_requete, doc_id, filtered_documents_info)

        # Trier les doc par l'ordre décroissant de score, ici x[1] correspond au score, l'output de la fonction sorted() est un liste des tuples de clé, valeur de docs_score
        ranked_doc_counts = sorted(docs_score.items(), key=lambda x: x[1], reverse=True)
        return ranked_doc_counts

    def get_document_by_id(self, doc_id):
        '''
            Cette fonction retrouve un document avec son document
            
            Parameters:
                    doc_id (str): identifiant de doc
                
            Returns:
                    document (dict) : a dictionnaire {url: ,id: , title:}
        '''      
        for document in self.documents:
            id_str = str(document['id'])
            if id_str == doc_id:
                return document
        return None  # Retourner None si aucun document n'est trouvé avec l'ID spécifié

    def run(self):

        # Charger l'index des documents
        self.index = self.load_index()
        self.documents = self.load_documents()

        # Preprocessing la requête de l'utilisateur: Tokenization + Lower
        print("Preprocessing...")

        transformed_query_tokens = self.tokenize(self.user_query)

        # Filtrer les documents avec la requête, filtered_documents_id est une liste des doc_id qui ont vécu 
        filtered_documents_id = self.filter_documents(transformed_query_tokens)

        # Ensuite, on souhaite retrouver des info des documents filtré par la requête sous forme de l'index {token: {docId: {position: [position indices], count: int}, cela va servir à la ranking
        # Cela serviraa à la computation des scores car on va utiliser les nombres d'occurrences.
        # Ces info seront stocké dans filtered_documents_info
        filtered_documents_info = {}
        for token in transformed_query_tokens:
            filtered_documents_info[token] = {}
            for doc_id, doc_info in self.index[token].items():
                if doc_id in filtered_documents_id:
                    filtered_documents_info[token][doc_id] = doc_info
        

        # Effectuer le ranking linéaire des documents filtrés
        print("Ranking...")
        ranked_documents = self.ranking(transformed_query_tokens,filtered_documents_id, filtered_documents_info)

        # Récupérer les titres et urls des documents
        documents_info = []
        
        # La fonction sorted() dans linear_ranking retourne une liste des tuples. Chaque tuple contient 2 éléments: DocID et score.
        # Ici, on itère sur ranked_documents 
        # la boucle for itère sur chaque tuple et, lors de chaque itération, elle déballe le tuple dans les variables doc_id et doc_info.
        for doc_id, doc_info in ranked_documents:
            document = self.get_document_by_id(doc_id) # Obtenir les informations du document à partir du fichier JSON des documents
            documents_info.append({
                'Titre': document.get('title', ''),
                'Url': document.get('url', '')
            })


        # Add summary sur le resultat
        resultat_info = {
            'N_document': len(self.documents),
            'N_document_filtre': len(ranked_documents)
        }

        print(resultat_info)

        # Enregistrer les informations des documents dans un fichier JSON
        with open('TP3/results.json', 'w', encoding='utf-8') as outfile:
            json.dump(resultat_info,outfile, indent=4, ensure_ascii=False)
            json.dump(documents_info, outfile, indent=4, ensure_ascii=False)

        
if __name__ == "__main__":

    user_query = "comment gérer les erreurs"
    Recherche(user_query, filter_type = 'AND', index_file="TP3/content_pos_index.json", documents_file="TP3/documents.json", weight = True).run()