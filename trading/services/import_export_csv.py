from pathlib import Path
import pandas as pd
from trading.models import Currency
from trading.serializers import (
    CurrencySerializer,
)

DELIMITER = ';'


class ImportCsv:
    @staticmethod
    def import_from_csv(file_name):
        ''' import data from csv-file to dict'''
        file_path = Path(file_name)
        if file_path.suffix == '.csv':
            df_file = pd.read_csv(file_name, sep=DELIMITER)
            return df_file.to_dict('records')
        else:
            raise ValueError('needs the format file .csv')


class ExportCsv:
    @staticmethod
    def export_to_csv(file_name):
        ''' export data from csv '''

        file_path = Path(file_name)
        if file_path.suffix == '.csv':
            curr_fields = [
                'id',
                'code',
                'name',
            ]

            currencies = Currency.objects.all()
            ser = CurrencySerializer(currencies, many=True)

            currency_dataframe = pd.DataFrame(ser.data)
            currency_dataframe.to_csv(
                file_name, index=False,
                columns=curr_fields, sep=DELIMITER
            )
