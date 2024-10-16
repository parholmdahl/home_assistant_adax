"""Support for Adax wifi-enabled home heaters."""
import logging

import voluptuous as vol
from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_PASSWORD,
    PRECISION_WHOLE,
    UnitOfTemperature,
)
from homeassistant.helpers import config_validation as cv

from .const import ACCOUNT_ID
from .data_handler import AdaxDataHandler
from .sensor import AdaxEnergySensor

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(ACCOUNT_ID): cv.string, vol.Required(CONF_PASSWORD): cv.string}
)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Adax thermostat with config flow."""
    adax_data_handler = hass.data[entry.entry_id]
    climate_entities = []

    for room in adax_data_handler._rooms:
        climate_entities.append(AdaxDevice(adax_data_handler, room))
    
    async_add_entities(climate_entities, True)

class AdaxDevice(ClimateEntity):
    """Representation of a heater."""

    def __init__(self, adax_data_handler, room):
        """Initialize the heater."""
        self._adax_data_handler = adax_data_handler
        self._heater_data = room
        self._energy_sensor = AdaxEnergySensor(adax_data_handler, room)

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return ClimateEntityFeature.TARGET_TEMPERATURE

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._heater_data['homeId']}_{self._heater_data['id']}"

    @property
    def name(self):
        """Return the name of the device, if any."""
        return self._heater_data["name"]

    @property
    def hvac_mode(self):
        """Return hvac operation ie. heat, cool mode."""
        if self._heater_data["heatingEnabled"]:
            return HVACMode.HEAT
        return HVACMode.OFF

    @property
    def icon(self):
        """Return nice icon for heater."""
        if self.hvac_mode == HVACMode.HEAT:
            return "mdi:radiator"
        return "mdi:radiator-off"

    @property
    def hvac_modes(self):
        """Return the list of available hvac operation modes."""
        return [HVACMode.HEAT, HVACMode.OFF]

    async def async_set_hvac_mode(self, hvac_mode):
        """Set hvac mode."""
        if hvac_mode == HVACMode.HEAT:
            temperature = max(
                self.min_temp, self._heater_data.get("targetTemperature", self.min_temp)
            )
            await self._adax_data_handler.set_room_target_temperature(
                self._heater_data["id"], temperature, True
            )
        elif hvac_mode == HVACMode.OFF:
            await self._adax_data_handler.set_room_target_temperature(
                self._heater_data["id"], self.min_temp, False
            )            
        else:
            return

    @property
    def temperature_unit(self):
        """Return the unit of measurement which this device uses."""
        return UnitOfTemperature.CELSIUS

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return 5

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return 35

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._heater_data.get("temperature")

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._heater_data.get("targetTemperature")

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return PRECISION_WHOLE

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        await self._adax_data_handler.set_room_target_temperature(
            self._heater_data["id"], temperature, True
        )

    async def async_update(self):
        _LOGGER.debug("Updating AdaxDevice for room ID %s", self._heater_data["id"])
        await self._adax_data_handler.async_update()
        room = self._adax_data_handler.get_room(self._heater_data["id"])
        if room:
            self._heater_data = room
            await self._energy_sensor.async_update()
            _LOGGER.debug("Updated heater data for room ID %s", self._heater_data["id"])
        else:
            _LOGGER.warning("Room ID %s not found in data handler", self._heater_data["id"])