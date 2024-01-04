from faker import Faker

TITLE_CHAR_CAP = 59


def generate_title(locale="en_US"):
    title = "".join(Faker(locale).sentence())
    return title[:TITLE_CHAR_CAP]


def generate_text(locale="en_US", amount=3):
    return "".join(Faker(locale).texts(nb_texts=amount))
