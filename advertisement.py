from errors import UnallowedAdvertisementType, UnallowedAdvertisementCategory

from typing import Union


class AdvertisementTypes:
    offer = "offer"
    searching_for = "searchingfor"

    interpret_dict = {
        offer: "Biete",
        searching_for: "Suche"
    }

    allowed_types = (offer, searching_for)

    language_dict = {
        "en": {
            "offer": "Offer",
            "searchingfor": "Searching"
        },
        "ge": {
            "offer": "Biete",
            "searchingfor": "Suche"
        }
    }


class AdvertisementCategories:
    help = "help"
    tools = "tools"
    tech = "tech"
    furniture = "furniture"
    clothing = "clothing"
    apartment = "apartment"
    media = "media"
    car = "car"
    games = "games"
    instruments = "instruments"
    living_tools = "living_tools"
    anything = "anything"

    category_classes = {
        "living": (furniture, apartment, living_tools),
        "tech_car": (tech, car),
        "lifestyle": (clothing, games, instruments),
        "anything": (media, tools, anything),
        help: help
    }

    language_dict_grand = {
        "en": {
            "living": "Living",
            "tech_car": "Tech/Car",
            "lifestyle": "Lifestyle",
            anything: "Anything",
            help: "Help"
        },
        "ge": {
            "living": "Wohnen",
            "tech_car": "Technik/Auto",
            "lifestyle": "Lifestyle",
            anything: "Sonstiges",
            help: "Hilfe"
        }
    }

    @classmethod
    def get_splitted_language_dict(cls, language: str, category: str = None) -> list:
        lang_dict = cls.language_dict_grand if category is None else cls.language_dict
        if language in lang_dict:
            lang_dict = lang_dict[language]
            lang_dict = lang_dict if category is None else lang_dict[category]
            return_list = []
            append_list = {}
            for key, element in lang_dict.items():
                append_list[key] = element
                if len(append_list) == 2:
                    return_list.append(append_list)
                    append_list = {}
            if append_list:
                return_list.append(append_list)
            return return_list
        else:
            return []

    language_dict = {
        "en": {
            "living": {
                furniture: "Furniture",
                apartment: "Apartments",
                living_tools: "Living Tools"
            },
            "tech_car": {
                tech: "Tech",
                car: "Car"
            },
            "lifestyle": {
                clothing: "Clothing",
                games: "Games",
                instruments: "Instruments"
            },
            anything: {
                media: "Media",
                tools: "Tools",
                anything: "Anything"
            },
            help: {
                help: "Help",
            }
        },
        "ge": {
            "living": {
                furniture: "Möbel",
                apartment: "Wohnungen",
                living_tools: "Haushaltsgeräte"
            },
            "tech_car": {
                tech: "Technik",
                car: "Auto"
            },
            "lifestyle": {
                clothing: "Kleidung",
                games: "Spiele",
                instruments: "Instrumente"
            },
            anything: {
                media: "Medien",
                tools: "Werkzeug",
                anything: "Sonstiges"
            },
            help: {
                help: "Hilfe",
            }
        }
    }

    searching_for_categories = ["help", "tools"]

    allowed_categories = (
        help,
        tools,
        tech,
        furniture,
        clothing,
        apartment,
        media,
        car,
        games,
        instruments,
        living_tools,
        anything
    )


class Advertisement:

    def __init__(self, advert_type: str, language: str, offering_user: str, debating_room: str):
        if advert_type not in AdvertisementTypes.allowed_types:
            raise UnallowedAdvertisementType()
        self.__language = language
        self.__type = advert_type
        self.__category = None
        self.__title = None
        self.__description = None
        self.__price = None
        self.__location = None
        self.__contact = None
        self.__grand_category = None
        self.__offering_user = offering_user
        self.__debating_room = debating_room
        self.__translate_dict = {
            "en": {
                "offer_to": "Offers please directly to:",
                "questions": "Questions can be asked in:",
                "free": "Free",
            },
            "ge": {
                "offer_to": "Angebote bitte direkt an:",
                "questions": "Fragen können hier gestellt werden:",
                "free": "Kostenlos",
            }
        }

    def get_type(self) -> str:
        return self.__type

    def set_type(self, new_type: str) -> None:
        if new_type not in AdvertisementTypes.allowed_types:
            raise UnallowedAdvertisementType()
        self.__type = new_type

    def set_category(self, new_category: str) -> None:
        if new_category not in AdvertisementCategories.allowed_categories:
            raise UnallowedAdvertisementCategory()
        self.__category = new_category

    def set_title(self, new_title: str) -> bool:
        if new_title:
            self.__title = new_title
            return True
        return False

    def set_grand_category(self, new_grand_category: str) -> bool:
        if new_grand_category in AdvertisementCategories.category_classes.keys():
            self.__grand_category = new_grand_category
            return True
        return False

    def get_grand_category(self) -> Union[str, None]:
        return self.__grand_category

    def get_price(self) -> Union[str, int]:
        return_price = self.__price
        if isinstance(self.__price, int) and self.__price == 0:
            return_price = self.__translate_dict[self.__language]["free"]
        return return_price

    def set_description(self, new_description: str) -> bool:
        if new_description:
            self.__description = new_description
            return True
        return False

    def set_price(self, new_price: Union[int, str]) -> bool:
        if isinstance(new_price, int) and new_price >= 0:
            self.__price = new_price
            return True
        elif self.__type == AdvertisementTypes.searching_for and isinstance(new_price, str) and new_price:
            self.__price = new_price
            return True
        return False

    def set_location(self, new_locaiton: str) -> bool:
        if new_locaiton:
            self.__location = new_locaiton
            return True
        return False

    def set_contact(self, new_contact: str) -> bool:
        if len(new_contact) > 1 and new_contact.startswith("@"):
            self.__contact = new_contact
            return True
        return False

    def __str__(self):
        str_repr = f"[{AdvertisementTypes.language_dict[self.__language][self.__type]}]\n" \
                   f"<b>{self.__title}</b>\n" \
                   f"{self.__description}\n" \
                   f"{'Price' if self.__language == 'en' else 'Preis'}: {self.get_price()}\n" \
                   f"{self.__translate_dict[self.__language]['offer_to']} @{self.__offering_user}\n" \
                   f"{self.__translate_dict[self.__language]['questions']} {self.__debating_room}\n"
        return str_repr
