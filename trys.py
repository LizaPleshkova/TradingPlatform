from pathlib import Path
import pandas as pd

# from trading.serializers import CurrencySerializer
import pyexcel as pe

def export_to_excel():
    file_name = 'test.xlsx'
    # file_name = 'file.xls'
    file_path = Path('test.xlsx')
    # file_path = Path('file.xls')
    if file_path.suffix == '.xlsx':
        df = pd.read_excel(file_name, engine='openpyxl')
        print(df)
        d1 = df.head()
        print('d1', d1)
        d2 = d1.to_dict('records')
        print(d2)
        for i in d2:
            print(i)
        print('after d2', d2)
        # ser = CurrencySerializer(d2, many=True)
        # print(ser, ser.data)
    elif file_path.suffix == '.xls':
        # records = pe.get_records(file_name="file.xls")
        # for record in records:
        #     print(record)
        df = pd.read_excel(file_name)
        print(df)
    else:
        # handle other file types
        pass
    # data = Currency.objects.all()
    # ser = CurrencySerializer(data, many=True)
    # sheet = pyexcel.get_dict(file_name="est_file.xls", name_columns_by_row=0)
    # data = xls_get(file_name="est_file.xls", column_limit=4)
    # print(sheet.context)


if __name__ == "__main__":
    # records = pe.get_records(file_name="file.xls")
    # for record in records:
    #     print(record)
    export_to_excel()
#
# file_name = 'new_file.xlsx'
# file_path = Path('new_file.xlsx')
#
# if file_path.suffix == '.xlsx':
#     print('xslx')
#     df = pd.read_excel(file_name, engine='openpyxl')
#     print(df)
#
# elif file_path.suffix == '.xls':
#     df = pd.read_excel(file_name)
#     print(df)
# else:
#     # handle other file types
#     pass
