from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import ENERGY_WATT_HOUR, POWER_WATT, Platform

"""Constants for Adax integration."""

ACCOUNT_ID = "account_id"
DOMAIN = "adax"

PLATFORMS = [Platform.SENSOR, Platform.CLIMATE]