from aiohttp import ClientSession, web
from gidgetlab import aiohttp as gl_aio
from gidgetlab import sansio

from database.declaratives import Integration, db_session
from eivor_gitlab.routes import router
import cryptutils


async def gitlab_entry(request):
    # No integration id
    integration_id = request.match_info['integration_id']
    if integration_id is None:
        return web.Response(status=400)

    integration = db_session.query(Integration).filter(
        Integration.id == integration_id).first()
    if integration is None:
        return web.Response(status=404)

    # Read payload
    body = await request.read()

    # Read access variables from environment
    # GL_SECRET
    secret = cryptutils.decodestr(integration.secret)

    # GL_ACCESS_TOKEN
    access_token = cryptutils.decodestr(integration.oauth_token)

    event = sansio.Event.from_http(request.headers, body, secret=secret)

    # Decide GitLab server URL
    url = integration.server_url
    if url is None:
        url = "https://gitlab.com"
    async with ClientSession() as session:
        gl = gl_aio.GitLabAPI(session,
                              integration.bot_username,
                              access_token=access_token,
                              url=url)

        await router.dispatch(event, gl, integration=integration)
    return web.Response(status=200)
