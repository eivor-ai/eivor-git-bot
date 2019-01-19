import re

from aiohttp import web, ClientSession
from gidgetlab import aiohttp as gl_aio
from gidgetlab import routing, sansio

from database.declaratives import Integration, db_session, Settings

gitlab_router = routing.Router()


############# Routes

@gitlab_router.register("Merge Request Hook", action="open")
async def issue_opened(event, gl, *args, **kwargs):
    url = f"/projects/{event.project_id}/merge_requests/{event.object_attributes['iid']}/notes"

    integration = kwargs['integration']
    preference = db_session.query(Settings).filter(Settings.integration_id == integration.id).first()
    if preference.mr_matcher is not None:
        issue_expression = r'{}'.format(preference.mr_matcher)
    else:
        issue_expression = r'.*'

    mr_title = event.object_attributes['title']

    match = re.search(issue_expression, mr_title)
    if match is None:
        content = preference.mr_failed_content #.decode('utf-8')
        message = prepare_mr_failed_content(content, issue_expression)
    else:
        content = preference.mr_accepted_content #.decode('utf-8')
        message = prepare_mr_success_content(content, match)

    await gl.post(url, data={"body": message})


######## Utils

def prepare_mr_failed_content(message, expession):
    return '{}'.format(message).replace('{mr_matcher}', expession)


def prepare_mr_success_content(message, match):
    content = '{}'.format(message)
    for i in range(0, match.lastindex):
        str = 'match_{}'.format(i + 1)
        content = content.replace('{' + str + '}', match.group(i + 1))

    return content


########### Entries

async def gitlab_entry(request):
    # No integration id
    integration_id = request.match_info['integration_id']
    if integration_id is None:
        return web.Response(status=402)

    integration = db_session.query(Integration).filter(Integration.id == integration_id).first()
    if integration is None:
        return web.Response(status=404)

    # Read payload
    body = await request.read()

    # Read access variables from environment
    # GL_SECRET
    secret = integration.secret

    # GL_ACCESS_TOKEN
    access_token = integration.oauth_token

    event = sansio.Event.from_http(request.headers, body, secret=secret)

    # Decide GitLab server URL
    url = integration.server_url
    if url is None:
        url = "https://gitlab.com"
    async with ClientSession() as session:
        gl = gl_aio.GitLabAPI(
            session, integration.bot_username, access_token=access_token, url=url)
        await gitlab_router.dispatch(event, gl, integration=integration)
    return web.Response(status=200)
