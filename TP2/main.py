import json
import pandas as pd
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

def load_crawled_urls_file(file_path):
        with open(file_path,"r") as file:
            # Read the content of the file
            file_content = file.read()
            crawled_urls = json.loads(file_content)
        
        crawled_urls = pd.DataFrame(crawled_urls)
        return crawled_urls

class Index():
    def __init__(self, urls_file, options_processing ):
        self.urls_file = urls_file
        self.options_processing = options_processing
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

        '''
        
        for i in range(len(doc)):
            tokens_title = doc.loc[i, 'tokens_title']
            tokens_content = doc.loc[i, 'tokens_content']
            self.metadata['total_tokens'] += len(tokens_title) + len(tokens_content)
            self.metadata['doc']['tokens_title'] += len(tokens_title)
            self.metadata['doc']['tokens_content'] += len(tokens_content)

        return self.metadata


    #Fonction pour tokenizer le texte et construire l'index web
    def tokenize(self,doc: pd.DataFrame):
        # Tokenizer le titre et le contenu
        tokens_title = []
        tokens_content = []
        for i in range(len(doc)):
            tokens_title.append(word_tokenize(doc.loc[i,'title']))
            tokens_content.append(word_tokenize(doc.loc[i,'content']))

        doc['tokens_title'] = tokens_title
        doc['tokens_content'] = tokens_content
        doc['all_tokens'] = doc['tokens_title'] + doc['tokens_content']
        return doc

        
        
    def create_index(self, doc):

        # Construire l'index web
        # Pour chaque token, on crée une liste inversée et on l’ajoute dans l’index

        for idx in doc.index:
            # Tokenizer le texte du document
            tokens = doc.loc[idx,'all_tokens']
            # Ajouter chaque token à l'index web
            for token in tokens:
                if token in self.web_index:
                    self.web_index[token].append(idx)
                else:
                    self.web_index[token] = [idx]

        with open("TP2/title.non_pos_index.json", "w") as json_file:
                    json.dump(self.web_index, json_file)  
        

    def run(self):

        documents_df = load_crawled_urls_file(self.urls_file)
        # Chaque document est tokenisé
        print("Tokenizing...")
        documents_df = self.tokenize(documents_df)
        # on process chaque token en fonction des options sélectionnées



        # Sortir des stats

        print("Analysing metadata...")
        n_doc = len(documents_df)
        self.metadata["Num_documents"] = n_doc
        self.metadata = self.analyse_stat(documents_df)
        self.metadata['Avg_tokens_per_document'] = self.metadata['total_tokens'] / n_doc

        with open("TP2/metadata.json", "w") as json_file:
            json.dump(self.metadata, json_file)  


        # Construire un index
        # Filtrer les mots vides et la ponctuation
        stop_words = set(stopwords.words('french'))
        for i in range(n_doc):

            documents_df.loc[i,'tokens_title'] = [token.lower() for token in documents_df.loc[i,'tokens_title'] if token.lower() not in stop_words and token.lower() not in string.punctuation]
            documents_df.loc[i,'tokens_content'] = [token.lower() for token in documents_df.loc[i,'tokens_content'] if token.lower() not in stop_words and token.lower() not in string.punctuation]
            documents_df.loc[i,'all_tokens'] = documents_df.loc['tokens_title'] + documents_df.loc[i,'tokens_content']

        print("Start creating index ...")
        self.create_index(documents_df)
        print("Index web created !")
        
if __name__ == "__main__":

    urls_file = "TP2/crawled_urls.json"
    documents_df = load_crawled_urls_file(urls_file)

    Index(urls_file, options_processing= []).run()
    
