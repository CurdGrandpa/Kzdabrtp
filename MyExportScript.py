def export_product():
    import xlwt
    myData = [["first_name", "second_name", "Grade"],
              ['Alex', 'Brian', 'A'],
              ['Tom', 'Smith', 'B']]

    book = xlwt.Workbook(encoding="utf-8")
    sheet1 = book.add_sheet("Sheet 1")

    for i in range(3):
        for j in range(3):
            sheet1.write(i, j, myData[i][j])

    book.save("ProductsData.xls")


if __name__ == '__main__':
    export_product()
