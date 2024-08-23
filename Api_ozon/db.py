from peewee import *

db = SqliteDatabase('categories_values.db')


class Category(Model):
    name = CharField(index=True, unique=True)
    description_category_id = IntegerField()
    type_id = IntegerField()
    ozon_category_name = CharField()

    class Meta:
        database = db

    def __str__(self):
        return self.name


class Characteristic(Model):
    category = ForeignKeyField(Category, backref='characteristics', on_delete='CASCADE')  # Связь с категорией
    id_ozon_character = IntegerField()
    name = CharField(index=True)
    description = TextField(null=True)
    type = CharField()  # Например, тип данных характеристики
    is_collection = BooleanField(default=False)  # Это коллекция?
    is_required = BooleanField(default=False)  # Обязательная характеристика?
    dictionary_id = IntegerField(null=True)  # Идентификатор словаря
    max_value_count = IntegerField(null=True)  # Максимальное количество значений
    default = CharField(null=True)

    class Meta:
        database = db

    def __str__(self):
        return self.name


class Parameter(Model):
    name = CharField()
    category = ForeignKeyField(Category, backref='characteristics', on_delete='CASCADE')  # Связь с категорией
    num = IntegerField()
    size = CharField()
    width = IntegerField(verbose_name="Ширина упаковки.")
    depth = IntegerField(verbose_name="Глубина упаковки.")
    height = IntegerField(verbose_name="Высота упаковки.")
    weight = IntegerField(verbose_name="Вес товара в упаковке.")
    weight_product = IntegerField(verbose_name="Вес товара")
    price = CharField(verbose_name="Цена товара с учётом скидок", null=True)
    old_price = CharField(verbose_name="Цена до скидок", null=True)

    class Meta:
        database = db

    def __str__(self):
        return self.name


if __name__ == '__main__':
    db.connect()
    db.create_tables([Category, Characteristic, Parameter])
    db.close()
