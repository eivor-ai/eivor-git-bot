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
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)
