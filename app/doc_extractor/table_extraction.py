import camelot

from scipy.spatial.distance import cosine
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
import numpy as np
from app.utils import pdf_to_df
from config.table_headers import coa_table_header_list as header_list
import argparse


class PDFTableExtractor:
    def __init__(self, header_list):
        self.header_list = header_list
        self.model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
        self.header_embeddings = self.get_headers_embeddings()
        

    @staticmethod
    def calculate_similarity(embedding1, embedding2):
        similarity = 1 - cosine(embedding1, embedding2)
        return similarity

    def get_embeddings(self,text):
        
        return self.model.encode([text])[0]

    def get_headers_embeddings(self):
        header_list_str = " ".join([" ".join(header) for header in self.header_list])
        return self.get_embeddings(header_list_str)

    def find_header_row(self, page_df, sim_thresh=0.7):
        max_similarity = 0
        best_match_row = None

        for index, row in page_df.iterrows():
            row_text = " ".join(row)
            row_embedding = self.get_embeddings(row_text)
            similarity = self.calculate_similarity(row_embedding, self.header_embeddings)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match_row = row_text

                if similarity > 0.7:
                    return best_match_row

        if max_similarity < 0.20:
            return None

        return best_match_row

    def get_coa_table(self, page_df):
        max_similarity = 0
        best_match_row = None

        best_match_row = self.find_header_row(page_df)
        if best_match_row is None:
            return page_df, ''

        row_idx = page_df.index[page_df.apply(lambda row: best_match_row in " ".join(row), axis=1)][0]
        page_df = page_df.iloc[row_idx:]
        page_df = page_df.reset_index(drop=True)

        return page_df, best_match_row

    def get_text_from_pdf(self, pdf_file):
        # need to add ocr functionality here later
        return pdf_to_df(pdf_file)

    def process_pdf(self, pdf_file):
        coa_df_dict = {}
        header_df_dict = {}
        text_df = self.get_text_from_pdf(pdf_file)

        if text_df:
            for page in text_df.keys():
                page_df = text_df[page]
                coa_df, header_df = self.get_coa_table(page_df)
                coa_df_dict[page] = coa_df
                header_df_dict[page] = header_df
            return coa_df_dict, header_df_dict
        return None, None


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_data")

    opt = parser.parse_args()

    extractor = PDFTableExtractor(header_list=header_list)
    print(extractor.process_pdf(opt.input_data))
