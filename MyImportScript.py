def import_products():
    with open('shop_items-NEW.csv', mode='r', encoding='utf-8') as csv_file:                # Открываем табличку с данными
        # 0-Артикул, 1-Категория, 2-Подкатегория, 3-Подкатегория категории, 4-Номенклатура с упаковкой,
        # 5-Текстовое описание номенклатуры, 6-Имя файла картинки, 7-цена, 8-валюта
        csv_reader = csv.reader(csv_file, delimiter=';')                            # Создаёт объект reader, который итерирует файл построчно. Грубо говоря, он его тупо читает
        line_count = 0                                                              # Переменная, которая считает строки
        for row in csv_reader:                                                      # Читает строчки, что-то делает
            line_count += 1  # Добавляет строчку в счётчик

            if line_count <= 2:                                                         # Так мы пропускаем шапку таблицы
                continue

            try:                                                                        # Если цена указана
                price = float(row[7].replace(" ", ""))                                  # то он её считывает
            except:                                                                     # Если не указана, то ловит ошибку
                print(f'no price: line {line_count}')
                price = 0                                                               # и ставит цену, равную нулю

            if price <= 0:                                                               # Если цена указана (если товар существует. Ну, или строка заполнена, там)
                continue

            try:
                product = Product.objects.get(inner_code=row[0])        # Чекает, есть ли уже такой продукт (продукт с таким внутренним номером)
            except:                                                     # Если продукта с таким внутренним номером нет
                product = Product(inner_code=row[0])                    # Создаётся новый

            try:
                # if not product.block_image_update:							#Если Изменение фотографии при апдейте не заблокированно
                #     img_name = row[1].split("/")[-1]							#Берём название картинки
                #
                #     saved_image = save_img(img_name, row[1])					#Функция какая-то. ХЗ шо делает
                #     if saved_image:											#
                #         product.image = saved_image							#
                #         product.hide_product = False							#
                #     else:														#
                #         product.hide_product = True							#
                product.price = price
                product.current_price = product.count_current_price()
                product.sku = row[0]
                product.url = row[0]
                if row[5] != "NULL":
                    product.description = row[5]
                product.category = Category.objects.get(name=row[1])        # Вот здесь осторожно
                product.image = "static/img/products/imported/" + row[6]
                product.name = row[4].split(', ')[0]
                product.save()
            except:
                print(product.name)

                # if str(row[2]) != "":										#Тестово смотрит на столбец (сейчас это столбец подкатегорий, раньше, видимо, столбец с фотками)
                #     for link in str(row[2]).split(","):					#Делит строку и для каждого элемента в строке ПОНЕСЛАСЬ РОДИМАЯ!
                #         img_name = link.split("/")[-1]					#
                #         saved_image = save_img(img_name, link)			#
                #         if saved_image:									#
                #             product_extra_image = ProductImage(image=saved_image, name=saved_product.name, product=saved_product).save()


        print(f'Processed {line_count} lines.')                                             # Это полезно

        return "OK"                                                                         # Это приятно

# Это всё надо доработать
# Надо бы добавить сборщик мусора. Чтобы мусор собирал и на сервере проблем не было.
#Буду работать над этим