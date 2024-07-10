# PyBLEToolkit

PyBLEToolkit is a Python toolkit designed to provide a streamlined environment for Bluetooth Low Energy (BLE) services
using customtkinter. This toolkit simplifies the development of custom BLE service interfaces, enabling developers to
focus on functionality and data handling while easily integrating with a GUI framework.

<img src="animated-images.svg" title="" alt="Animated Images" data-align="center">

## Features

- **Easy GUI Integration**: Quickly add custom frames to display and interact with BLE services.
- **Python and customtkinter Based**: Uses Python for logic and customtkinter for a user-friendly interface.
- **Extensible Framework**: Designed to be flexible, allowing developers to implement and showcase their BLE services
  seamlessly.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.6 or newer
- pip (Python package installer)
- Check [requirements.txt](requirements.txt) for necessary python packages

## Usage

After installation, you can start by creating a new BLE service frame. Here are the steps to integrate a new service
into the toolkit:

1. Create two objects: one for the service itself that inherits from [AbstractService](src/abstract_service.py), and
   another for the GUI of your service that inherits from [AbstractServiceTab](src/abstract_service_tab.py).
   See [examples](docs/services).

2. Register your service and GUI in the dictionary [SERVICE_REGISTER](src/service_register.py) like this:

```python
# Service register mapping services to their corresponding tab classes
SERVICE_REGISTER: Dict[Type[AbstractService], Type[AbstractServiceTab]] = {
    MyServiceObject: MyServiceObjectTab,
    # ...
}
```

Once registered, you can run the application and connect to your service.

## Contributing

We welcome contributions to PyBLEToolkit! To make this project more interesting and useful, we encourage developers to
contribute their services with pre-prepared GUIs for various applications. Please document the protocol for data
transmission.

If you have suggestions for improvements or new features, feel free to submit a pull request. Check out
our [CONTRIBUTING](docs/CONTRIBUTING.md) for guidelines on how to contribute.

## License

This project is licensed under the MIT License—see the [LICENSE](docs/LICENSE) file for details.

## Authors

- [muhamm-ad · GitHub](https://github.com/muhamm-ad)

## Acknowledgments

- Inspiration from the BLE community and various open-source projects that have paved the way for this toolkit,
  especially [Adafruit](https://github.com/adafruit)
