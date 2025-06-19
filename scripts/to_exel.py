import json
import pandas as pd

def json_to_exel_parse(data, sheet_names):
    for sheet_name in sheet_names:  
        df = pd.DataFrame([data])   
        df.to_excel(fr'C:\Users\Admin\projects\telegram_parser\files\report.xlsx',sheet_name=sheet_name, index=False)