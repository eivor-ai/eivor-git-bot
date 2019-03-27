import re

from gidgetlab import routing

from database.declaratives import Settings, db_session

router = routing.Router()


@router.register("Merge Request Hook", action="open")
async def merge_request_opened(event, gl, *args, **kwargs):
    url = get_mr_base_url(event)

    integration = kwargs['integration']

    preference = db_session.query(Settings).filter(
        Settings.integration_id == integration.id).first()

    mr_matcher = preference.mr_matcher
    issue_expression = r'.*' if mr_matcher is None else rf'{mr_matcher}'

    mr_title = event.object_attributes['title']

    match = re.search(issue_expression, mr_title)
    if match is None:
        content = preference.mr_failed_content  # .decode('utf-8')
        message = prepare_mr_failed_content(content, issue_expression)
        await gl.put(url,
                     data={
                         'state_event': 'close',
                         'title': f'CLOSED - {mr_title}'
                     })
    else:
        content = preference.mr_accepted_content  # .decode('utf-8')
        message = prepare_mr_success_content(content, match)

    await gl.post(f'{url}/notes', data={'body': message})


@router.register("Merge Request Hook", action="update")
async def merge_request_updated(event, gl, *args, **kwargs):
    url = get_mr_base_url(event)

    # If the MR was closed, it needs to be re-opened if the title is proper.
    if event.object_attributes['state'] == 'closed':
        integration = kwargs['integration']
        preference = db_session.query(Settings).filter(
            Settings.integration_id == integration.id).first()

        mr_matcher = preference.mr_matcher
        issue_expression = r'.*' if mr_matcher is None else rf'{mr_matcher}'

        match = re.search(issue_expression, event.object_attributes['title'])
        if match is not None:
            await gl.put(url,
                         data={
                             'state_event': 'reopen'
                         })
            content = preference.mr_accepted_content
            message = prepare_mr_success_content(content, match)

            await gl.post(f'{url}/notes', data={'body': message})


@router.register("Merge Request Hook", action="merge")
async def merge_request_approved(event, gl, *args, **kwargs):
    url = get_mr_base_url(event)

    integration = kwargs["integration"]
    preference = db_session.query(Settings).filter(
        Settings.integration_id == integration.id).first()

    default_assignee = preference.mr_default_assignee
    if default_assignee:
        message = f"MR Approved.\n\n --- \n\n /cc @{default_assignee}"
        await gl.post(f"{url}/notes", data={"body": message})


# Utils

def get_mr_base_url(event):
    event_iid = event.object_attributes['iid']
    return f'/projects/{event.project_id}/merge_requests/{event_iid}'


def prepare_mr_failed_content(message, expession):
    return f'{message}'.replace('{mr_matcher}', expession)


def prepare_mr_success_content(message, match):
    content = f'{message}'
    for i in range(0, match.lastindex):
        str = f'match_{i + 1}'
        content = content.replace('{' + str + '}', match.group(i + 1))

    return content
