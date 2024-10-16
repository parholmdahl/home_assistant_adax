"""The Adax heater integration."""
from .const import ACCOUNT_ID, DOMAIN, PLATFORMS
from homeassistant.const import CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .climate import AdaxDataHandler

async def async_setup(hass, config) -> bool:
    """Set up the Adax platform."""
    return True

async def async_setup_entry(hass, entry) -> bool:
    """Set up the Adax heater."""
    websession = async_get_clientsession(hass)
    adax_data_handler = AdaxDataHandler(entry.data[ACCOUNT_ID], entry.data[CONF_PASSWORD], websession)
    await adax_data_handler.async_update()
    hass.data[entry.entry_id] = adax_data_handler

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass, config_entry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
    return unload_ok
