class NoRecievingRoomsException(Exception):
    message = "Wrong numger of recieving rooms. At least one room_id has to be given."


class JSONFileNotFoundException(Exception):
    message = "The JSON File was not found. Make sure the json file with the telegram token and recieving rooms id exists."


class UnallowedAdvertisementType(Exception):
    message = "The given advertisement type is not allowed."

class UnallowedAdvertisementCategory(Exception):
    message = "The given advertisement category is not allowed."