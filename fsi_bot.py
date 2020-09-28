from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.error import Unauthorized, TelegramError
from telegram.bot import Bot, BotCommand
from telebot import TeleBot
from pyrogram import Client
import json
from typing import Union
from os.path import isfile

from errors import JSONFileNotFoundException, NoRecievingRoomsException
from advertisement import AdvertisementCategories, AdvertisementTypes, Advertisement


def read_config(conf_path: str) -> Union[dict, None]:
    if isfile(conf_path):
        with open(conf_path) as conf_file:
            return json.load(conf_file)
    return None


g_conf_data = read_config("config.json")
if g_conf_data is not None:
    bot = Bot(token=g_conf_data["telegram_token"])

class FSIBot:

    def __init__(self):
        conf_data = read_config("config.json")
        if conf_data is not None:
            self.__telegram_token = conf_data["telegram_token"]
            self.__recieving_chats = conf_data["recieving_rooms"]
            self.__debating_room = conf_data["debating_room"]
            if not self.__recieving_chats:
                raise NoRecievingRoomsException()
            self.__updater = Updater(self.__telegram_token, use_context=True)
            self.__bot = bot
            self.__commands_map = {
                "language": self.set_language,
                AdvertisementTypes.offer: self.set_type,
                AdvertisementTypes.searching_for: self.set_type,
                "grand_category": self.set_grand_category,
                "category": self.set_category,
                "no": self.get_precise_offer,
                "yes": self.get_precise_offer,
                "money": self.get_precise_offer,
                "something_else": self.get_precise_offer,
                "finish": self.finishing,
                "cancel": self.cancel,
            }
            self.__states = {
                "language": self.gather_lanuage,
                "type": self.gather_advert_type,
                "grand_category": self.gather_global_category,
                "category": self.gather_category,
                "title": self.gather_title,
            }
            self.__advertisement = None
            self.__language_tag = None
            self.__state = "language"
            self.__language_dict = self.create_language_dict()
            self.__add_handler()
        else:
            raise JSONFileNotFoundException()

    def __add_handler(self):
        self.__updater.dispatcher.add_handler(CommandHandler("start", self.start_chat))
        self.__updater.dispatcher.add_handler(CommandHandler("cancel", self.cancel))
        self.__updater.dispatcher.add_handler(CallbackQueryHandler(self.button_handler))
        self.__updater.dispatcher.add_handler(MessageHandler(Filters.text, self.set_user_input))
        #self.__updater.dispatcher.add_handler(CommandHandler('newadvert', self.start_user_chat))

    def send_welcome(self, user_id, chat_id):
        self.__bot.send_message(chat_id=user_id, text=self.__language_dict[self.__language_tag]["welcome"])
        self.__state = "type"
        self.gather_advert_type(user_id)

    def start_chat(self, update, context):
        user_id = update.message.from_user.id
        self.gather_lanuage(user_id)

    def gather_lanuage(self, user_id: int):
        self.__bot.send_message(chat_id=user_id, text="Please choose a language:",
                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("De", callback_data="/language ge"),
                                                           InlineKeyboardButton("En", callback_data="/language en")]]))

    def gather_advert_type(self, user_id: int):
        self.__bot.send_message(chat_id=user_id, text=self.__language_dict[self.__language_tag]["offer_text"],
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(AdvertisementTypes.language_dict[self.__language_tag]["offer"], callback_data="/offer"),
                                                           InlineKeyboardButton(AdvertisementTypes.language_dict[self.__language_tag]["searchingfor"], callback_data="/searchingfor"),
                                                           InlineKeyboardButton(self.__language_dict[self.__language_tag]["cancel"], callback_data="/cancel")]]))

    def gather_global_category(self, user_id: int):
        self.__bot.send_message(chat_id=user_id, text=self.__language_dict[self.__language_tag]["grand_category"],
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(element, callback_data="/grand_category " + key)
                                                                    for key, element in sub_dict.items() if self.__advertisement.get_type() == AdvertisementTypes.searching_for or element not in AdvertisementCategories.searching_for_categories]
                                                                   for sub_dict in AdvertisementCategories.get_splitted_language_dict(self.__language_tag)] +
                                                                    [[InlineKeyboardButton(self.__language_dict[self.__language_tag]["cancel"], callback_data="/cancel")]]))

    def gather_category(self, user_id: int):
        self.__bot.send_message(chat_id=user_id, text=self.__language_dict[self.__language_tag]["category"],
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(element, callback_data="/category " + key)
                                                                    for key, element in sub_dict.items() if self.__advertisement.get_type() == AdvertisementTypes.searching_for or element not in AdvertisementCategories.searching_for_categories]
                                                                   for sub_dict in AdvertisementCategories.get_splitted_language_dict(self.__language_tag, self.__advertisement.get_grand_category())] +
                                                                    [[InlineKeyboardButton(self.__language_dict[self.__language_tag]["cancel"], callback_data="/cancel")]]))

    def gather_title(self, user_id: int):
        self.__bot.send_message(chat_id=user_id, text=self.__language_dict[self.__language_tag]["title"],
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(self.__language_dict[self.__language_tag]["cancel"], callback_data="/cancel")]]))

    def gather_description(self, user_id: int):
        self.__bot.send_message(chat_id=user_id, text=self.__language_dict[self.__language_tag]["description"],
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(self.__language_dict[self.__language_tag]["cancel"], callback_data="/cancel")]]))

    def gather_price(self, user_id: int):
        self.__bot.send_message(chat_id=user_id, text=self.__language_dict[self.__language_tag]["price"],
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(self.__language_dict[self.__language_tag]["cancel"], callback_data="/cancel")]]))

    def gather_other_offer(self, user_id: int):
        self.__bot.send_message(chat_id=user_id, text=self.__language_dict[self.__language_tag]["something_else_wished_offer"],
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(self.__language_dict[self.__language_tag]["cancel"], callback_data="/cancel")]]))

    def gather_wished_offer(self, user_id: int):
        self.__bot.send_message(chat_id=user_id, text=self.__language_dict[self.__language_tag]["wished_offer"],
                                reply_markup=InlineKeyboardMarkup([
                                    [InlineKeyboardButton(self.__language_dict[self.__language_tag]["yes"], callback_data="/yes"),
                                     InlineKeyboardButton(self.__language_dict[self.__language_tag]["no"], callback_data="/no")],
                                    [InlineKeyboardButton(self.__language_dict[self.__language_tag]["cancel"], callback_data="/cancel")]]))

    def gather_exact_offer(self, user_id: int):
        self.__bot.send_message(chat_id=user_id, text=self.__language_dict[self.__language_tag]["confirmed_wished_offer"],
                                reply_markup=InlineKeyboardMarkup([
                                    [InlineKeyboardButton(self.__language_dict[self.__language_tag]["money"], callback_data="/money"),
                                     InlineKeyboardButton(self.__language_dict[self.__language_tag]["something_else"], callback_data="/something_else")],
                                    [InlineKeyboardButton(self.__language_dict[self.__language_tag]["cancel"], callback_data="/cancel")]]))

    def gather_location(self, user_id: int):
        self.__bot.send_message(chat_id=user_id, text=self.__language_dict[self.__language_tag]["location"],
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(self.__language_dict[self.__language_tag]["cancel"], callback_data="/cancel")]]))

    def gather_finishing(self, user_id: int):
        self.__bot.send_message(chat_id=user_id, text=self.__language_dict[self.__language_tag]["finish"],
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(self.__language_dict[self.__language_tag]["finishing"], callback_data="/finish")],
                                                                   [InlineKeyboardButton(self.__language_dict[self.__language_tag]["cancel"], callback_data="/cancel")]]))

    def button_handler(self, update, context):
        command, args = self.parse_message(update.callback_query.data)
        command = command[1:]
        self.__commands_map[command](command, args, update.callback_query.from_user, update.callback_query.message.chat.id)
        update.callback_query.message.edit_reply_markup()

    def get_precise_offer(self, command: str, args: str, from_user: "User", chat_id: int):
        if command == "yes":
            self.gather_exact_offer(from_user.id)
        elif command == "money":
            self.__state = "price"
            self.gather_price(from_user.id)
        elif command == "no":
            self.__advertisement.set_price("Vb")
            self.__state = "location"
            self.gather_location(from_user.id)
        else:
            self.gather_other_offer(from_user.id)

    def finishing(self, command: str, args: str, from_user: "User", chat_id: int):
        string_version = str(self.__advertisement)
        for chat in self.__recieving_chats:
            self.__bot.send_message(chat_id=f"-{chat}", text=string_version, parse_mode=ParseMode.HTML)
        self.gather_advert_type(from_user.id)

    def set_type(self, command: str, args: str, from_user: "User", chat_id: int):
        self.__advertisement = Advertisement(command, self.__language_tag, from_user.username, self.__debating_room)
        self.__state = "grand_category"
        self.gather_global_category(from_user.id)

    def set_language(self, command: str, args: str, from_user: "User", chat_id: int):
        if args in ["en", "ge"]:
            self.__language_tag = args
            self.send_welcome(from_user.id, chat_id)
        else:
            self.gather_lanuage(from_user.id)

    def set_grand_category(self, command: str, args: str, from_user: "User", chat_id: int):
        self.__advertisement.set_grand_category(args)
        if args == AdvertisementCategories.help:
            self.__advertisement.set_category(args)
            self.__state = "title"
            self.gather_title(from_user.id)
        else:
            self.__state = "category"
            self.gather_category(from_user.id)

    def set_category(self, command: str, args: str, from_user: "User", chat_id: int):
        self.__advertisement.set_category(args)
        self.__state = "title"
        self.gather_title(from_user.id)

    def set_user_input(self, update, context):
        if self.__state in ["title", "description", "price", "location", "other_offer"]:
            user_id = update.message.from_user.id
            if self.__state == "title":
                self.__advertisement.set_title(update.message.text)
                self.__state = "description"
                self.gather_description(user_id)
            elif self.__state == "description":
                self.__advertisement.set_description(update.message.text)
                if self.__advertisement.get_type() == AdvertisementTypes.searching_for:
                    self.__state = "other_offer"
                    self.gather_wished_offer(user_id)
                else:
                    self.__state = "price"
                    self.gather_price(user_id)
                # TODO difference between offer and searching
            elif self.__state == "price":
                try:
                    price = int(update.message.text)
                except ValueError:
                    price = update.message.text
                self.__advertisement.set_price(price)
                self.__state = "location"
                self.gather_location(user_id)
            elif self.__state == "location":
                self.__advertisement.set_location(update.message.text)
                self.__state = "finish"
                self.gather_finishing(user_id)
            elif self.__state == "other_offer":
                self.__advertisement.set_price(update.message.text)
                self.__state = "location"
                self.gather_location(user_id)

    def cancel(self, command: str, args: str, from_user: "User", chat_id: int):
        self.clear()
        user_id = from_user.id
        self.__bot.send_message(chat_id=user_id, text="Aktuelle Inseraterstellung wurde abgebrochen.")
        self.gather_advert_type(user_id)

    def clear(self):
        self.__advertisement = None

    @staticmethod
    def create_language_dict():
        language_dict = {
            "en": {
                "welcome": "Welcome! You want to create a new advertisement. Let me help you.",
                "offer_text": "Are you searching or offering?",
                "grand_category": "Please choose a general category: ",
                "category": "Please choose a category:",
                "title": "Please provide a title:",
                "description": "Please provide a description:",
                "price": "Please provide your desired price:",
                "location": "Where is the offer located?",
                "wished_offer": "Do you have something in mind to offer in regard?",
                "confirmed_wished_offer": "Do you want to offer money or something else?",
                "something_else_wished_offer": "What do you want to offer?",
                "yes": "Yes",
                "no": "No",
                "money": "Money",
                "something_else": "Other",
                "finish": "Do you want to finish the offer?",
                "finishing": "Finishing",
                "cancel": "Cancel",
            },
            "ge": {
                "welcome": "Willkommen! Du möchtest ein neues Inserat erstellen. Lass mich dir dabei helfen.",
                "offer_text": "Möchtest du etwas anbieten oder suchst du etwas?",
                "grand_category": "Bitte wähle eine generelle Kategorie:",
                "category": "Bitte wähle eine Kategorie:",
                "title": "Bitte gib einen Titel ein:",
                "description": "Bitte gib eine Beschreibung ein:",
                "price": "Bitte gib deinen gewünschten Preis an:",
                "location": "Wo kann das Angebot abgeholt/wahrgenommen werden?",
                "wished_offer": "Möchtest du etwas als Gegenleistung anbieten?",
                "confirmed_wished_offer": "Möchtest du Geld oder was anderes anbieten?",
                "something_else_wished_offer": "Was genau möchtest du anbieten?",
                "yes": "Ja",
                "no": "Nein",
                "money": "Geld",
                "something_else": "Sontiges",
                "finish": "Möchtest du das Angebot abschließen?",
                "finishing": "Abschließen",
                "cancel": "Abbrechen",
            }
        }
        return language_dict

    @staticmethod
    def parse_message(message: str):
        message_split = message.split(maxsplit=1)
        args = ""
        if len(message_split) > 1:
            command, args = message_split
        else:
            command = message_split[0]
        return command, args

    def start(self):
        self.__updater.start_polling()
        self.__updater.idle()


if __name__ == "__main__":
    fsibot = FSIBot()
    fsibot.start()