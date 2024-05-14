from src.services.exemple_ble_json_service import JSONService, JSONServiceTab
from src.services.exemple_ble_uart_service import UARTService, UARTServiceTab
from typing import Dict, Tuple, Type
from src.services.service import AbstractService, ServiceTab

STD_PADDING = 5
TAB_Y_PADDING = 5
TAB_X_PADDING = 5

BLUE_COLOR = "#3B8ED0"
TRANSPARENT_COLOR = "transparent"

# Service register mapping services to their corresponding tab classes
SERVICE_REGISTER: Dict[Type[AbstractService], Type[ServiceTab]] = {
    JSONService: JSONServiceTab,
    UARTService: UARTServiceTab
}