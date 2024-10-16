# custom_components/adax/data_handler.py
from adax import Adax

class AdaxDataHandler:
    def __init__(self, account_id, password, websession):
        self._adax = Adax(account_id, password, websession=websession)
        self._rooms = None

    async def async_update(self):
        self._rooms = await self._adax.get_rooms()
        return self._rooms

    def get_room(self, room_id):
        if self._rooms is None:
            return None
        for room in self._rooms:
            if room["id"] == room_id:
                return room
        return None