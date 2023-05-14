import camelot
import PyPDF2
import pandas as pd
import re

class PDFtext2df:
    def __init__(self):
        pass
    
    def camelot_pdf_to_df(self, pdf_file):
        pdf_df = {}

        try:
            pdf_archive = camelot.read_pdf(pdf_file, pages="all", flavor="stream")
            if pdf_archive:
                for page, pdf_table in enumerate(pdf_archive):
                    pdf_df[page] = pdf_archive[page].df
        except:
            pass

        return pdf_df

    def pypdf2_pdf_to_df(self, pdf_file):
        pdf_df = {}

        try:
            with open(pdf_file, "rb") as file:
                pdf_reader = PyPDF2.PdfFileReader(file)

                for page_num in range(pdf_reader.numPages):
                    page = pdf_reader.getPage(page_num)
                    text = page.extractText()
                    lines = text.splitlines()

                    # Create a DataFrame with a single column for each page
                    df = pd.DataFrame(lines, columns=["Text"])
                    pdf_df[page_num] = df

        except:
            pass

        return pdf_df


    def text_to_dataframe(text, column_count=4):
        # Split the text into lines
        lines = text.split("\n")

        # Initialize an empty dataframe with the given number of columns
        df = pd.DataFrame(columns=range(column_count))

        # Iterate over the lines and extract values using regular expressions
        for line in lines:
            # Replace multiple spaces with a single space
            line = re.sub(r'\s+', ' ', line).strip()

            # Split the line into values using space as a delimiter
            values = line.split(" ")

            # If the number of values in the line matches the column count, add it as a row in the dataframe
            if len(values) <= column_count and len(values) > 0 :
                df.loc[len(df)] = values

        return df

    def pdf_to_df(self, pdf_file):
        # First, try to extract tables using camelot
        pdf_df = self.camelot_pdf_to_df(pdf_file)

        # If no tables were found, fall back to using PyPDF2
        if not pdf_df:
            pdf_df = self.pypdf2_pdf_to_df(pdf_file)

        return pdf_df
