from pandas import DataFrame, concat
from tabula import read_pdf
from os import listdir
from re import findall

class String:
    def __init__(self, my_string):
        self.str_as_list = [my_string]

    def change_str(self, new_str):
        self.str_as_list = [new_str]

    def __str__(self):
        return self.str_as_list[0]

# merge rows in column that look like one value
def clean_column(data: DataFrame, reduce_to: int):
    """
    reduce column by logically merging records
    :param data: DataFrame with one column
    :param reduce_to: maximum record number after return
    :return: void
    """

    records = len(data.index)

    # remove rows with small letters on start
    for row in range(1, records):
        if records <= reduce_to:
            return

        record = data.iat[row, 0]

        if findall(r"[^\s]", record)[0].isalpha() and not findall(r"[^\s]", record)[0].isupper():
            data.iat[row - 1, 0] = data.iat[row - 1, 0] + " " + data.iat[row, 0]
            data.drop(row, inplace=True)
            records -= 1

    # remove rows with symbols on start
    for row in range(1, records):
        if records <= reduce_to:
            return

        record = data.iat[row, 0]

        if not findall(r"[^\s]", record)[0].isupper() and not findall(r"[^\s]", record)[0].isnumeric():
            data.iat[row - 1, 0] = data.iat[row - 1, 0] + " " + data.iat[row, 0]
            data.drop(row, inplace=True)
            records -= 1

    # remove rows with numbers on start
    for row in range(1, records):
        if records <= reduce_to:
            return

        record = data.iat[row, 0]

        if findall(r"[^\s]", record)[0].isnumeric():
            data.iat[row - 1, 0] = data.iat[row - 1, 0] + " " + data.iat[row, 0]
            data.drop(row, inplace=True)
            records -= 1

    # remove rows with numbers on start
    for row in range(1, records):
        if records <= reduce_to:
            return

        record = data.iat[row, 0]

        if not findall(r"[^\s]", record)[0].isalpha():
            data.iat[row - 1, 0] = data.iat[row - 1, 0] + " " + data.iat[row, 0]
            data.drop(row, inplace=True)
            records -= 1

def get_customer_and_type(pdf_path: str, customer: String, nip: String) -> int:
    """
    identify uber invoice type
    :param pdf_path: path to pdf
    :param customer: variable to save customer name
    :param nip: variable to save customer nip
    :return: 0 if cash payment; 1 if card payment
    """

    data = read_pdf(pdf_path, pages=1, guess=False, area=[0, 0, 112.32, 339.84], multiple_tables=True, pandas_options={'header': None})[0]

    if len(data.columns) > 1:
        customer.change_str(data.iat[1, 0])
        inv_type = 0
    else:
        customer.change_str(data.iat[0, 0])
        inv_type = 1

    if len(data.index) > 3:
        nip.change_str(data.iat[2 + (0 if inv_type == 1 else 1),0][5:])

    return inv_type

def process_invoice(pdf_path):
    """
    extract table data from uber TRIP invoice
    :param pdf_path: path to pdf
    :return: extracted table data in DataFrame
    """

    customer = String("")
    nip = String("")
    pdf_type = get_customer_and_type(pdf_path, customer, nip)
    top = 215.0 if pdf_type == 1 else 240.0

    # area [top (y), left(x), top+height(y), left+width(x)]
    areas = [
        [top, 0, 685.44, 52.56],
        [top, 52.56, 685.44, 122.4],
        [top, 122.4, 685.44, 311.76],
        [top, 311.76, 685.44, 342.72],
        [top, 342.72, 685.44, 409.68],
        [top, 409.68, 685.44, 459.36],
        [top, 459.36, 685.44, 498.24],
        [top, 498.24, 685.44, 595.28]
    ]
    tripData = []
    data = read_pdf(pdf_path, pages=1, guess=False, area=areas, multiple_tables=True, pandas_options={'header': None})
    records = 0

    for it in range(len(data)):
        if it == 0:
            records = max(data[it])
        if it == 2:
            clean_column(data[it], records)
        if it == 4:
            data[it].iat[0, 0] += data[it].iat[0, 1]
            data[it].drop(1, inplace=True, axis=1)
            data[it].drop(data[it].tail(2).index, inplace=True)
        if it == 5:
            data[it].drop(data[it].tail(3).index, inplace=True)
        if it == 6:
            data[it].drop(data[it].tail(3).index, inplace=True)
        if it == 7:
            for i in range(-3, 0):
                tripData.append(data[it][0].iloc[i])
            data[it].drop(data[it].tail(3).index, inplace=True)
            data[it].iat[0, 0] = data[it].iat[0, 0].split(" ")[0]

    # additional payment data
    data.append(DataFrame({
        "a":[tripData[0].split(" ")[0]],
        "b":[tripData[1].split(" ")[0]],
        "c":[tripData[2].split(" ")[0]],
        "d":[customer.__str__()],
        "e":["gotówka" if pdf_type == 0 else "karta"],
        "f":[pdf_path[-28:-4]],
        "g":[nip],
        "h":[tripData[0].split(" ")[1]]
    }))

    df = data[0]
    for i in range(1, len(data)):
        df = df.join(data[i], lsuffix=i - 1, rsuffix=i)

    return df

def extract(pdf_dir, update_progress):
    if pdf_dir == "":
        print("Working directory is not selected")
        return
    print(pdf_dir)

    counter = 1
    files_num = len(listdir(pdf_dir))
    print(files_num)
    invoices = []
    for filename in listdir(pdf_dir):
        print("FILE " + str(counter))
        update_progress(counter, files_num)
        counter += 1
        if filename.endswith(".pdf"):
            path = pdf_dir + "/" + filename
            invoices.append(process_invoice(path))
            print("Done")
        else:
            print("File is not pdf!")

    invoices = concat(invoices)
    invoices.columns = [
        "Lp.",
        "Data sprzedaży",
        "Opis",
        "Ilość",
        "Jm.",
        "Stawka VAT",
        "Kwota VAT",
        "Wartość Netto",
        "Razem po potrąceniu PTU",
        "Wartość całkowita VAT",
        "Wartość brutto",
        "Klient",
        "Typ opłaty",
        "Numer Faktury",
        "NIP",
        "Waluta"
    ]

    invoices.to_csv(pdf_dir + "/" + 'invoices.csv', index=False)
