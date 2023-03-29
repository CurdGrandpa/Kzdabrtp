class Category(MPTTModel):
    name = models.CharField(verbose_name="Название", help_text="Нужно для выгрузки. Не менять.", max_length=255)
    inner_name = models.CharField(verbose_name="Внутреннее название (для сайта)", max_length=255, blank=True, null=True)

    url = models.SlugField(verbose_name="Url страницы. Заполнится автоматически, если оставить пустым.", blank=True, null=True)
    image = models.ImageField(verbose_name="Картинка для превью", upload_to=FOR_UPLOAD + "img/categories/", blank=True, null=True)
    title_image = models.ImageField(verbose_name="Фоновая картинка для заголовка", upload_to=FOR_UPLOAD + "img/categories/", blank=True, null=True)

    block_image_update = models.BooleanField(verbose_name="Не обновлять кратинку при автоматическом импорте", default=False)
    description = HTMLField(verbose_name="Текст описания", blank=True, null=True)
    is_hidden = models.BooleanField(verbose_name="Скрыть с сайта", default=False)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    # SEO
    title = models.CharField(max_length=100, verbose_name="Заголовок страницы для поиска (Title)", blank=True, null=True)
    seo_description = models.TextField(verbose_name="МЕТА-тег описания страницы (Description)", blank=True, null=True)
    seo_keywords = models.TextField(verbose_name="МЕТА-тег ключевых слов (Keywords) страницы", blank=True, null=True)

    def __str__(self):  # __str__ on Python 2
        return self.name

    def get_price_fork(self):
        cat_products = Product.objects.filter(category=self, categories__in=[self], price__gt=0).order_by("current_price")
        if cat_products:
            self.min_price = cat_products.first().current_price
            if len(cat_products) > 1:
                self.max_price = cat_products.last().current_price
            else:
                self.max_price = self.min_price + 1000
        else:
            self.min_price = 0
            self.max_price = 10000

    def get_absolute_url(self):
        return reverse('catalog:category', kwargs={'path': self.get_path()})

    class Meta:
        unique_together = ('url', 'parent')
        verbose_name = "категория"
        verbose_name_plural = "категории"


class Brand(models.Model):
    name = models.CharField(verbose_name="Название", max_length=255)
    url = models.SlugField(verbose_name="Url страницы. Заполнится автоматически, если оставить пустым.", blank=True, null=True)

    def __str__(self):  # __str__ on Python 2
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "бренд"
        verbose_name_plural = "бренды"


class Country(models.Model):
    value = models.CharField(verbose_name="Значение параметра", max_length=255)

    def __str__(self):  # __str__ on Python 2
        return self.value

    class Meta:
        verbose_name = "страна"
        verbose_name_plural = "страны"


class Unit(models.Model):
    value = models.CharField(verbose_name="Значение параметра", max_length=255)

    def __str__(self):  # __str__ on Python 2
        return self.value

    class Meta:
        verbose_name = "единица измерения"
        verbose_name_plural = "единицы измерения"

class Product(models.Model):
    name = models.CharField(verbose_name="Название", max_length=255)
    sku = models.CharField(verbose_name="Артикул", max_length=255, blank=True)
    inner_code = models.CharField(verbose_name="Внутренний код (1с или подобное)", max_length=255, blank=True)
    url = models.SlugField(verbose_name="Url страницы", blank=True, null=True,
                           help_text="Заполнится автоматически, если оставить пустым.", unique=True, max_length=150)

    hide_product = models.BooleanField(verbose_name="Скрыть товар", default=False)

    category = TreeForeignKey('catalog.Category', verbose_name="Основная категория", related_name="category", on_delete=models.CASCADE, blank=True, null=True)
    categories = TreeManyToManyField(Category, verbose_name="Категории", related_name="categories", blank=True, null=True)

    image = models.ImageField(verbose_name="Основное изображение товара", upload_to=FOR_UPLOAD + "img/products/", blank=True, null=True)
    block_image_update = models.BooleanField(verbose_name="Не обновлять картинку при автоматическом импорте", default=False)

    brand = models.ForeignKey(Brand, verbose_name="Производитель", on_delete=models.CASCADE, blank=True, null=True)
    country = models.ForeignKey('catalog.Country', verbose_name="Страна происхождения", on_delete=models.CASCADE, blank=True, null=True)
    price = models.IntegerField(verbose_name="Цена")
    discount_price = models.IntegerField(verbose_name="Цена со скидкой", blank=True, null=True,
                                         help_text="для корректного отображения укажите стандартную цену")
    size = models.CharField(verbose_name="Размер", max_length=100, blank=True, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.DO_NOTHING, verbose_name="Единица измерения", blank=True, null=True)

    available = models.BooleanField(verbose_name="Есть в наличии", default=1, blank=True, null=True)
    items_left = models.CharField(verbose_name="Остаток товара", blank=True, null=True, max_length=255)
    # hide_items_left = models.BooleanField(verbose_name="Скрыть остатки на странице товара", default=False)

    description = HTMLField(verbose_name="Описание товара", blank=True, null=True)
    parameters = HTMLField(verbose_name="Описание характеристик товара", blank=True, null=True)

    similar_products = models.ManyToManyField('self', verbose_name="Похожие товары", blank=True, symmetrical=False)
    complement_products = models.ManyToManyField('self', related_name='Complementary',
                                                 verbose_name="С этим товаром покупают", blank=True, symmetrical=False)
    # SEO
    title = models.CharField(max_length=100, verbose_name="Заголовок страницы для поиска (Title)",
                             blank=True, null=True)
    seo_description = models.TextField(verbose_name="МЕТА-тег описания страницы (Description)", blank=True, null=True)
    seo_keywords = models.TextField(verbose_name="МЕТА-тег ключевых слов (Keywords) страницы", blank=True, null=True)

    current_price = models.IntegerField(verbose_name="Текущая цена на товар", editable=False,
                                        help_text="Используется для сортировки товаров.", blank=True)

    sorting = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)

        if self.discount_price:
            discount_value = int(self.price) - int(self.discount_price)

            self.percent_discount = int(round((discount_value / self.price) * 100))
        else:
            self.percent_discount = 0

    def count_current_price(self):
        if self.discount_price:
            self.current_price = self.discount_price
        else:
            self.current_price = self.price

        return self.current_price

    def __str__(self):  # __str__ on Python 2
        if self.sku:
            return self.name + u" (" + str(self.sku) + u")"
        else:
            return self.name

    class Meta():
        ordering = ['sorting']
        verbose_name = "товар"
        verbose_name_plural = "товары"