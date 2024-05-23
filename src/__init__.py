from src.exemples.ble_json_service import ExJSONService, ExJSONServiceTab
from src.exemples.ble_uart_service import UARTService, UARTServiceTab
from typing import Dict, Type
from src.abstract_service import AbstractService
from src.abstract_service_tab import AbstractServiceTab

# Service register mapping services to their corresponding tab classes
SERVICE_REGISTER: Dict[Type[AbstractService], Type[AbstractServiceTab]] = {
    ExJSONService: ExJSONServiceTab,
    UARTService: UARTServiceTab
}
