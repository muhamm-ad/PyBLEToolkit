# Contributing to PyBLEToolkit

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Becoming a maintainer
- Proposing new features
- Proposing new GUI service
    - **Develop Your Service**: Create a new service class that inherits from `AbstractService` and a corresponding GUI
      class that inherits from `AbstractServiceTab`.
    - **Document the Protocol**: Clearly document the data transmission protocol used by your service. Include examples
      of the data format and how it should be interpreted. like [ExJSONService](services/json_service_exemple.png).
    - **Submit a Pull Request**: Fork the repository, add your service and GUI classes, update the `SERVICE_REGISTER`
      dictionary, and submit a pull request with your changes.

### How to Contribute Your Service

1. **Develop Your Service**: Create a new service class that inherits from `AbstractService` and a corresponding GUI
   class that inherits from `AbstractServiceTab`.
2. **Document the Protocol**: Clearly document the data transmission protocol used by your service. Include examples of
   the data format and how it should be interpreted.
3. **Submit a Pull Request**: Fork the repository, add your service and GUI classes, update the `SERVICE_REGISTER`
   dictionary, and submit a pull request with your changes.

## We Develop with GitHub

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## We Use [GitHub Flow](https://guides.github.com/introduction/flow/index.html), So All Code Changes Happen Through Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `master`.
2. If you've added code that should be tested, add tests.
3. Ensure the test suite passes.
4. Make sure your code lints.
5. Issue that pulls request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](LICENSE) that
covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issues](https://github.com/muhamm-ad/PyBLEToolkit/issues)

We use GitHub issues to track public bugs. Report a bug
by [opening a new issue](https://github.com/muhamm-ad/PyBLEToolkit/issues/new); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
    - Be specific!
    - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Use a Consistent Coding Style

* You can use an editor like VSCode with Python and PEP8 extensions installed to help follow our coding conventions.
* Make sure to run a linter before submitting your pull requests.

## License

By contributing, you agree that your contributions will be licensed under its MIT License.

## References

Here are a few other resources that you might find helpful:

- [How to Contribute to an Open Source Project on GitHub](https://opensource.guide/how-to-contribute/)

## Thank you for your contributions!
