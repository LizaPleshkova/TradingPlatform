from trading.models import Currency, Item
from trading.serializers import (
    CurrencySerializer, ItemSerializer,
)
from pathlib import Path
import pandas as pd


def _sheets_to_dict(excel_file):
    data_records = {}
    for sheet in excel_file.sheet_names:
        d = excel_file.parse(sheet, index_col=1, index=False).fillna('').to_dict('records')
        data_records[sheet] = d
    return data_records


def _validate_excel_data_columns(data_dict_sheets):
    for sheet in data_dict_sheets:
        if 'id' in data_dict_sheets[sheet]:
            data_dict_sheets[sheet] = data_dict_sheets[sheet].drop(columns='id')
        if 'code' in data_dict_sheets[sheet] or 'name' in data_dict_sheets[sheet]:
            data_dict_sheets[sheet] = data_dict_sheets[sheet].to_dict('records')
            _save_excel_data(data_dict_sheets[sheet])
    return data_dict_sheets


def _save_excel_data(excel_data_dict):
    ser = CurrencySerializer(data=excel_data_dict, many=True)
    ser.is_valid(raise_exception=True)
    cur_list = [Currency(code=i['code'], name=i['name']) for i in ser.validated_data]
    Currency.objects.bulk_create(cur_list)
    return cur_list


class ImportExcelService:
    ''' writing data from excel-file '''

    @staticmethod
    def import_excel_sheets(file_name):
        ''' import data from all sheets of the excel-file '''
        file_path = Path(file_name)
        if file_path.suffix == '.xlsx' or file_path.suffix == '.xls':
            xl = pd.ExcelFile(file_name)
            return _sheets_to_dict(xl)
        else:
            raise ValueError('needs the format file .xlsx or .xls')

    @staticmethod
    def import_currency_to_excel(file_name):
        ''' import currency data to excel-file '''
        file_path = Path(file_name)
        if file_path.suffix == '.xlsx' or file_path.suffix == '.xls':
            xl = pd.ExcelFile(file_name)
            sheets = xl.sheet_names
            data_dict_sheets = {}
            for sheet in sheets:
                d = xl.parse(sheet)
                data_dict_sheets[sheet] = d
            data_dict_sheets = _validate_excel_data_columns(data_dict_sheets)
            return data_dict_sheets
        else:
            raise ValueError('needs the format file .xlsx or .xls')


def _get_data_items_currencies():
    data_dict_sheets = {}
    cur = Currency.objects.all()
    ser_cur = CurrencySerializer(cur, many=True)
    items = Item.objects.all()
    ser_item = ItemSerializer(items, many=True)

    data_dict_sheets['items'] = pd.DataFrame(ser_item.data)
    data_dict_sheets['currrencies'] = pd.DataFrame(ser_cur.data)
    return data_dict_sheets


def _write_sheets(file_name):
    writer = pd.ExcelWriter(file_name)
    data_dict_sheets = _get_data_items_currencies()
    for sheet in data_dict_sheets:
        data_dict_sheets[sheet].to_excel(writer, sheet)
    writer.save()


class ExportExcelService:
    ''' writing data from db to excel-file '''

    @staticmethod
    def export_to_excel(file_name):
        file_path = Path(file_name)
        if file_path.suffix == '.xlsx' or file_path.suffix == '.xls':
            _write_sheets(file_name)
        else:
            raise ValueError('needs the format file .xlsx or .xls')
