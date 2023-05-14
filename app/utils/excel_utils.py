import camelot
import pandas as pd
import io

     
def pdf_to_df(pdf_file):
    pdf_df = ''
    try:
        pdf_archive = camelot.read_pdf(pdf_file, pages="all", flavor="stream")
        pdf_df = {}
        for page, pdf_table in enumerate(pdf_archive):
            # Get the data frame for the current page
            pdf_df[page] = pdf_archive[page].df
            #df = pdf_archive[page].df
    except:
        pass

    return pdf_df

def save_to_excel(pdf_data, filename):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    for page, df in pdf_data.items():
        df.to_excel(writer, sheet_name=f'Page {page+1}', index=False)
    writer.save()
    output.seek(0)
    with open(filename, 'wb') as f:
        f.write(output.read())
    return output.read()
