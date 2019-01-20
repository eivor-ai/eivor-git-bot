import os

from aiohttp import web

import constants
import gitlab

if __name__ == "__main__":

    app = web.Application()
    # GitLab
    app.router.add_post("/gitlab/{integration_id}", gitlab.gitlab_entry)

    # GitHub
    # app.router.add_post("/github/{integration)id}", github.github_entry)

    port = constants.SERVER_PORT

    port_variable = os.environ.get('PORT')
    if port_variable is not None:
      print('System env variable PORT is set, binding to {}'.format(port_variable))
      port = int(port_variable)

    if port is not None:
        port = int(port)

    web.run_app(app, port=port)
