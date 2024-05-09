from src.services.service import AbstractService, ServiceTab
import time
import threading

PADDING = 5


class ServiceTabsManager:
    def __init__(self, master):
        self._master = master
        self._current_service_tab = ServiceTab(master=self._master)
        self._current_service = None
        self._service_threads = {}
        self._thread_lock = threading.Lock()

    def _is_service_running(self, service: AbstractService):
        return service in self._service_threads and self._service_threads[service].is_alive()

    def _switch_service_tab(self, service: AbstractService):
        with self._thread_lock:
            self._current_service_tab.grid_remove()
            self._current_service_tab = service.get_service_tab(master=self._master)
            self._current_service_tab.grid(row=0, column=0, padx=PADDING, pady=PADDING, sticky="nsew")

    def select_service(self, service: AbstractService):
        if service != self._current_service:
            self._current_service = service
            self._switch_service_tab(service)

        if not self._is_service_running(service):
            def task():
                while True:
                    try:
                        data = service.read()
                        if data:
                            with self._thread_lock:
                                self._master.after(0, lambda d=data: self._current_service_tab.update_data(d))
                        time.sleep(1)  # Consider adjusting sleep duration based on your application's needs
                    except Exception as e:
                        print(f"Error during updating data : {e}")

            thread = threading.Thread(target=task)
            thread.daemon = True
            self._service_threads[service] = thread
            thread.start()
