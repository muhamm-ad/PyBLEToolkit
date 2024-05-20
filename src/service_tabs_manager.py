import threading
from threading import Thread
from typing import Dict, Tuple
from src.utils import STD_PADDING
from src import SERVICE_REGISTER
from service import AbstractService
from service_tab import ServiceTab
import time


class ServiceTabsManager:
    def __init__(self, master):
        self._master = master
        self._current_service_tab = ServiceTab(master=self._master)
        self._current_service = None
        self._service_threads: Dict[AbstractService, Tuple[Thread, ServiceTab]] = {}
        self._thread_lock = threading.Lock()

    def _is_service_running(self, service: AbstractService) -> bool:
        return service in self._service_threads and self._service_threads[service][0].is_alive()

    def _switch_service_tab(self, service: AbstractService):
        with self._thread_lock:
            self._current_service_tab.grid_remove()
            self._current_service_tab = self._service_threads[service][1]
            self._current_service_tab.grid(row=0, column=0, padx=STD_PADDING, pady=STD_PADDING, sticky="nsew")

    def select_service(self, service: AbstractService):
        need_switch = (service != self._current_service)

        if need_switch:
            self._current_service = service

        if not self._is_service_running(service):
            service_tab = SERVICE_REGISTER[type(service)](self._master)

            def task():
                while True:
                    try:
                        data = service.read()
                        if data:
                            # Ensure the update happens in the main thread
                            self._master.after(0, lambda d=data: service_tab.update_data(d))
                        time.sleep(1)  # Consider adjusting sleep duration based on your application's needs
                    except Exception as e:
                        print(f"ServiceTabsManager Error during updating data: {e}")

            with self._thread_lock:
                self._service_threads[service] = (Thread(target=task, daemon=True), service_tab)
                self._service_threads[service][0].start()

        if need_switch:
            self._switch_service_tab(service)
