import os

from aiohttp import web

import constants
import gitlab

if __name__ == "__main__":

    app = web.Application()
    # GitLab
    app.router.add_post('/eivor_gitlab/{integration_id}', gitlab.gitlab_entry)

    # GitHub
    # app.router.add_post("/eivor_github/{integration)id}",
    # github.github_entry)

    port = constants.SERVER_PORT

    port_variable = os.environ.get('PORT')
    if port_variable is not None:
        print(f'System env variable PORT is set, binding to {port_variable}')
        port = int(port_variable)

    web.run_app(app, port=port)
