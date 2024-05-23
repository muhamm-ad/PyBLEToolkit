import threading
from threading import Thread
from typing import Dict, Tuple
from src.utils import STD_PADDING
from src import SERVICE_REGISTER
from abstract_service import AbstractService
from abstract_service_tab import AbstractServiceTab
import time


class ServiceTabsManager:
    def __init__(self, master):
        self._master = master
        self._current_service_tab = AbstractServiceTab(master=self._master)
        self._current_service = None
        self._service_threads: Dict[AbstractService, Tuple[Thread, AbstractServiceTab, bool]] = {}
        self._thread_lock = threading.Lock()
        self._running = True  # Add a flag to control the running state

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

            def task(running_flag):
                while running_flag():
                    try:
                        data = service.read()
                        if data:
                            self._master.after(0, lambda d=data: service_tab.update_data(d))
                        time.sleep(1)
                    except Exception as e:
                        print(f"ServiceTabsManager Error during updating data: {e}")

            running_flag = lambda: self._running

            with self._thread_lock:
                self._service_threads[service] = (Thread(target=task, args=(running_flag,), daemon=True), service_tab, running_flag)
                self._service_threads[service][0].start()

        if need_switch:
            self._switch_service_tab(service)

    def quit(self):
        if self._service_threads:  # Check if it is not empty
            with self._thread_lock:
                self._running = False  # Set the flag to stop all threads
                for service, (thread, service_tab, running_flag) in self._service_threads.items():
                    thread.join()  # Wait for each thread to finish
