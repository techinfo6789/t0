import pandas as pd
import json

default_excel = 'data/excel_data/default_fields.csv'
fields_excel = 'data/excel_data/c.csv'

def create_fields_prompt(pdf_text, default_excel = default_excel, fields_excel = fields_excel):
    df = pd.read_csv(default_excel)
    df2 = pd.read_csv(fields_excel)

    lowercase_paragraph = pdf_text.lower()
    

    default_items = df.to_dict(orient = 'records')
    non_default_items = df2.to_dict(orient = 'records')

    present_fields = [field for field in non_default_items if field['Field'].lower() in lowercase_paragraph]

    field_str = []

    for field in default_items:
        field_str.append(f"{field['Field']} ({field['Field Type']}) - {field['Definition']}")

    for field in present_fields:
        field_str.append(f"{field['Field']} ({field['Field Type']})")

    return '\n'.join(field_str)



