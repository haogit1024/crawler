import xlrd3 as xlrd

def run():
    excel_path = r'D:\baike\城市名缩写.xlsx'
    book = xlrd.open_workbook(excel_path)
    print("The number of worksheets is {0}".format(book.nsheets))
    print("Worksheet name(s): {0}".format(book.sheet_names()))
    sh = book.sheet_by_index(1)
    print("{0} {1} {2}".format(sh.name, sh.nrows, sh.ncols))
    print("Cell D30 is {0}".format(sh.cell_value(rowx=29, colx=3)))
#     for rx in range(sh.nrows):
#         print(sh.row(rx))
    for i in range(10):
        print(sh.row(i))

if __name__ == '__main__':
    run()