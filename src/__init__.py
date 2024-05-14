from src.exemples.ble_json_service import JSONService, JSONServiceTab
from src.exemples.ble_uart_service import UARTService, UARTServiceTab
from typing import Dict, Type
from src.service import AbstractService
from src.service_tab import ServiceTab

STD_PADDING = 5
TAB_Y_PADDING = STD_PADDING
TAB_X_PADDING = STD_PADDING

BLUE_COLOR = "#3B8ED0"
TRANSPARENT_COLOR = "transparent"

# Service register mapping services to their corresponding tab classes
SERVICE_REGISTER: Dict[Type[AbstractService], Type[ServiceTab]] = {
    JSONService: JSONServiceTab,
    UARTService: UARTServiceTab
}
