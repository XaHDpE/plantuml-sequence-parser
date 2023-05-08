import pandas as pd


def dump_to_excel(dict1, excel_file_name):
    df = pd.DataFrame(data=dict1)

    # Save the DataFrame to an Excel file
    df.to_excel(excel_file_name, index=False)

    print("Dictionary converted into excel...")
