from src.exemples.ble_json_service import ExJSONService, ExJSONServiceTab
from src.exemples.ble_uart_service import UARTService, UARTServiceTab
from typing import Dict, Type
from src.service import AbstractService
from src.service_tab import ServiceTab


# Service register mapping services to their corresponding tab classes
SERVICE_REGISTER: Dict[Type[AbstractService], Type[ServiceTab]] = {
    ExJSONService: ExJSONServiceTab,
    UARTService: UARTServiceTab
}
