- Head to your user settings at `https://pypi.org` and setup PyPI trusted publishing.
  In order to do so, you have to head to the "Publishing" tab, scroll to the bottom
  and add a "new pending publisher". The relevant information is:
  - PyPI project name: `teddy_hospital`
  - Owner: `None`
  - Repository name: `teddy-hospital`
  - Workflow name: `pypi.yml`
  - Environment name: not required
- Enable the integration with `codecov.io` by heading to the [Codecov.io Website](https://codecov.io),
  log in (e.g. with your Github credentials) and enable integration for your repository. In order to do
  so, you need to select it from the list of repositories (potentially re-syncing with GitHub). Then, head
  to the "Settings" Tab and select "Global Upload Token". Here, you should select the "not required" option.

- password protected links
- make ui more responsive (e.g: need feedback when picture has been uploaded successfully)
- add exception handler to seafile errors.
- password protected api
- config with frontend configure
- carrousel

- BUGS:
  - firefox doens't scan QR codes
