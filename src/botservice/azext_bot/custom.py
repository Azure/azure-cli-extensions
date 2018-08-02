# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import shutil
import adal  # pylint: disable=import-error
from knack.prompting import prompt_y_n  # pylint: disable=unused-import
from knack.util import CLIError
from knack.log import get_logger
from azext_bot.botservice.models import Bot, BotProperties, sku, BotChannel
from azure.cli.command_modules.appservice.custom import (enable_zip_deploy, config_source_control, get_app_settings,
                                                         _get_site_credential, _get_scm_url)
from azure.cli.command_modules.resource.custom import deploy_arm_template
from azure.cli.core._profile import Profile

logger = get_logger(__name__)


def provisionConvergedApp(bot_name):
    botfirstpartyid = 'f3723d34-6ff5-4ceb-a148-d99dcd2511fc'
    aadclientid = '1950a258-227b-4e31-a9cf-717495945fc2'
    tenantid = '72f988bf-86f1-41af-91ab-2d7cd011db47'

    authority = 'https://login.windows.net/{0}'.format(tenantid)
    context = adal.AuthenticationContext(
        authority=authority,
        validate_authority=True,
        api_version=None
    )

    code = context.acquire_user_code(
        resource=botfirstpartyid,
        client_id=aadclientid,
    )

    logger.warning(code['message'])

    token = context.acquire_token_with_device_code(
        resource=botfirstpartyid,
        user_code_info=code,
        client_id=aadclientid
    )
    access_token = token['accessToken']

    import requests
    headers = {'Authorization': 'Bearer {0}'.format(access_token)}
    response = requests.post(
        'https://dev.botframework.com/api/botApp/provisionConvergedApp?name={0}'.format(bot_name),
        headers=headers
    )
    if response.status_code not in [201]:
        raise CLIError('Unable to provision appid and password for supplied credentials')
    response_content = json.loads(response.content.decode('utf-8'))
    msa_app_id = response_content['AppId']
    password = response_content['Password']

    return msa_app_id, password


def create(cmd, client, resource_group_name, resource_name, kind, description=None, display_name=None,
           endpoint=None, msa_app_id=None, password=None, tags=None, storageAccountName=None,
           location='Central US', sku_name='F0', appInsightsLocation='South Central US', bot_json=None,
           language='Csharp'):
    if tags:
        raise CLIError('Tags not supported yet')

    display_name = display_name or resource_name
    kind = kind.lower()

    if not msa_app_id:
        msa_app_id, password = provisionConvergedApp(resource_name)
        logger.warning('obtained msa app id and password. Provisioning bot now.')

    if kind == 'registration':
        kind = 'bot'
        if not endpoint or not msa_app_id:
            raise CLIError('Endpoint and msa app id are required for creating a registration bot')
        parameters = Bot(
            location='global',
            sku=sku.Sku(sku_name),
            kind=kind,
            properties=BotProperties(
                display_name=display_name,
                description=description,
                endpoint=endpoint,
                msa_app_id=msa_app_id
            )
        )
        return client.bots.create(
            resource_group_name=resource_group_name,
            resource_name=resource_name,
            parameters=parameters
        )
    elif kind == 'webapp' or kind == 'function':
        return create_app(cmd, client, resource_group_name, resource_name, description, kind, msa_app_id, password,
                          storageAccountName, location, sku_name, appInsightsLocation, bot_json, language)
    else:
        raise CLIError('Invalid Bot Parameter : Kind')


def update(client, parameters, resource_group_name):
    try:
        return client.bots.update(
            resource_group_name=resource_group_name,
            resource_name=parameters.name,
            **(parameters.__dict__)
        )
    except AttributeError:
        return None


def delete_bot(client, resource_group_name, resource_name):
    # temporary workaround - delete every channel first and then delete bot
    for channel in ['facebook', 'email', 'msTeams', 'skype', 'kik', 'directLine', 'telegram', 'sms', 'slack']:
        channelName = '{}Channel'.format(channel)
        channelName = channelName[:1].upper() + channelName[1:]
        client.channels.delete(
            resource_group_name=resource_group_name,
            resource_name=resource_name,
            channel_name=channelName
        )
    return client.bots.delete(
        resource_group_name=resource_group_name,
        resource_name=resource_name
    )


def create_bot_json(cmd, client, resource_group_name, resource_name, app_password=None, raw_bot_properties=None):
    if not raw_bot_properties:
        raw_bot_properties = client.bots.get(
            resource_group_name=resource_group_name,
            resource_name=resource_name
        )
    if not app_password:
        app_settings = get_app_settings(
            cmd=cmd,
            resource_group_name=resource_group_name,
            name=resource_name
        )
        app_password = [item['value'] for item in app_settings if item['name'] == 'MicrosoftAppPassword'][0]

    profile = Profile(cli_ctx=cmd.cli_ctx)
    return {
        'type': 'abs',
        'id': raw_bot_properties.name,
        'name': raw_bot_properties.properties.display_name,
        'appId': raw_bot_properties.properties.msa_app_id,
        'appPassword': app_password,
        'endpoint': raw_bot_properties.properties.endpoint,
        'resourceGroup': str(resource_group_name),
        'tenantId': profile.get_subscription(subscription=client.config.subscription_id)['tenantId'],
        'subscriptionId': client.config.subscription_id
    }


def get_bot(cmd, client, resource_group_name, resource_name, bot_json=None):
    raw_bot_properties = client.bots.get(
        resource_group_name=resource_group_name,
        resource_name=resource_name
    )
    if bot_json:
        return create_bot_json(cmd, client, resource_group_name, resource_name, raw_bot_properties=raw_bot_properties)

    return raw_bot_properties


def get_connections(client, resource_group_name, resource_name):
    return client.bot_connection.list_by_bot_service(resource_group_name, resource_name)


def get_connection(client, resource_group_name, resource_name, connection_name):
    return client.bot_connection.get(resource_group_name, resource_name, connection_name)


def create_connection(client, resource_group_name, resource_name, connection_name, client_id,
                      client_secret, scopes, service_provider_name, parameters=None):
    from azext_bot.botservice.models import ConnectionSetting, ConnectionSettingProperties, ConnectionSettingParameter
    service_provider = get_service_providers(client, name=service_provider_name)
    if not service_provider:
        raise CLIError('Invalid Service Provider Name passed. Use listprovider command to see all available providers')
    connection_parameters = []
    if parameters:
        for parameter in parameters:
            pair = parameter.split('=', 1)
            if len(pair) == 1:
                raise CLIError('usage error: --parameters STRING=STRING STRING=STRING')
            connection_parameters.append(ConnectionSettingParameter(key=pair[0], value=pair[1]))
    setting = ConnectionSetting(
        location='global',
        properties=ConnectionSettingProperties(
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
            service_provider_id=service_provider.properties.id,
            parameters=connection_parameters
        )
    )
    return client.bot_connection.create(resource_group_name, resource_name, connection_name, setting)


def delete_connection(client, resource_group_name, resource_name, connection_name):
    return client.bot_connection.delete(resource_group_name, resource_name, connection_name)


def get_service_providers(client, name=None):
    service_provider_response = client.bot_connection.list_service_providers()
    name = name and name.lower()
    if name:
        try:
            return next((item for item in service_provider_response.value if item.properties.service_provider_name.lower() == name.lower()))  # pylint: disable=line-too-long
        except StopIteration:
            raise CLIError('A service provider with the name {0} was not found'.format(name))
    return service_provider_response


def create_app(cmd, client, resource_group_name, resource_name, description, kind, appid, password, storageAccountName,  # pylint: disable=inconsistent-return-statements
               location, sku_name, appInsightsLocation, bot_json, language):
    if kind == 'function':
        template_name = 'functionapp.template.json'
        if language == 'Csharp':
            zip_url = 'https://connectorprod.blob.core.windows.net/bot-packages/csharp-abs-functions_emptybot.zip'
        else:
            zip_url = 'https://connectorprod.blob.core.windows.net/bot-packages/node.js-abs-functions_emptybot_funcpack.zip'  # pylint: disable=line-too-long

    else:
        kind = 'sdk'
        template_name = 'webapp.template.json'
        if language == 'Csharp':
            zip_url = 'https://connectorprod.blob.core.windows.net/bot-packages/csharp-abs-webapp_simpleechobot_precompiled.zip'  # pylint: disable=line-too-long
        else:
            zip_url = 'https://connectorprod.blob.core.windows.net/bot-packages/node.js-abs-webapp_hello-chatconnector.zip'  # pylint: disable=line-too-long

    create_new_storage = False
    if not storageAccountName:
        import re
        import string
        import random
        create_new_storage = True
        storageAccountName = re.sub(r'[^a-z0-9]', '', resource_name[:10] +
                                    ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4)))

    paramsdict = {
        "location": location,
        "kind": kind,
        "sku": sku_name,
        "siteName": resource_name,
        "appId": appid,
        "appSecret": password,
        "storageAccountResourceId": "",
        "serverFarmId": "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Web/serverfarms/{2}".format(
            client.config.subscription_id, resource_group_name, resource_name),
        "zipUrl": zip_url,
        "createNewStorage": create_new_storage,
        "storageAccountName": storageAccountName,
        "botEnv": "prod",
        "useAppInsights": True,
        "appInsightsLocation": appInsightsLocation,
        "createServerFarm": True,
        "serverFarmLocation": location.lower().replace(' ', ''),
        "azureWebJobsBotFrameworkDirectLineSecret": "",
        "botId": resource_name
    }
    if description:
        paramsdict['description'] = description
    params = {k: {'value': v} for k, v in paramsdict.items()}

    dir_path = os.path.dirname(os.path.realpath(__file__))
    deploy_result = deploy_arm_template(
        cmd=cmd,
        resource_group_name=resource_group_name,
        template_file=os.path.join(dir_path, template_name),
        parameters=[[json.dumps(params)]],
        deployment_name=resource_name,
        mode='Incremental'
    )

    deploy_result.wait()
    if bot_json:
        return create_bot_json(cmd, client, resource_group_name, resource_name, app_password=password)


def publish_app(cmd, resource_group_name, resource_name, git_url=None, git_token=None, git_branch='master',  # pylint: disable=inconsistent-return-statements
                code_dir=None):
    # if given msbot json, use that to update environment settings like luis settings
    if git_url:
        return config_source_control(
            cmd=cmd,
            name=resource_name,
            resource_group_name=resource_group_name,
            repo_url=git_url,
            branch=git_branch,
            git_token=git_token
        )

    # since there is no git url it's definitely publish from local
    if not code_dir:
        code_dir = os.getcwd()

    if code_dir:
        if not os.path.isdir(code_dir):
            raise CLIError('Please supply a valid directory path containing your source code')
        # ensure that the directory contains appropriate post deploy scripts folder
        if 'PostDeployScripts' not in os.listdir(code_dir):
            raise CLIError('Not a valid azure publish directory. missing post deploy scripts')
        shutil.make_archive('upload', 'zip', code_dir)
        output = enable_zip_deploy(cmd, resource_group_name, resource_name, 'upload.zip')
        os.remove('upload.zip')
        return output


def download_app(cmd, client, resource_group_name, resource_name, file_save_path=None):
    # get the bot and ensure it's not a registration only bot
    raw_bot_properties = client.bots.get(
        resource_group_name=resource_group_name,
        resource_name=resource_name
    )
    if raw_bot_properties.kind == 'bot':
        raise CLIError('Source download is not supported for registration only bots')
    file_save_path = file_save_path or os.getcwd()
    if not os.path.isdir(file_save_path):
        raise CLIError('Path name not valid')
    folder_path = os.path.join(file_save_path, resource_name)
    if os.path.exists(folder_path):
        raise CLIError('The path {0} already exists. Please delete it or specify an alternate path'.format(folder_path))
    os.mkdir(folder_path)

    user_name, password = _get_site_credential(cmd.cli_ctx, resource_group_name, resource_name, None)
    scm_url = _get_scm_url(cmd, resource_group_name, resource_name, None)

    import urllib3
    authorization = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(user_name, password))
    headers = authorization
    headers['content-type'] = 'application/json'

    payload = {
        'command': 'PostDeployScripts\\prepareSrc.cmd {0}'.format(password),
        'dir': r'site\wwwroot'
    }

    import requests
    response = requests.post(scm_url + '/api/command', data=json.dumps(payload), headers=headers)
    if response.status_code != 200:
        raise CLIError('Zip Download failed with status code {} and reason {}'.format(
            response.status_code, response.text))
    response = requests.get(scm_url + '/api/vfs/site/bot-src.zip', headers=authorization)
    if response.status_code != 200:
        raise CLIError('Zip Download failed with status code {} and reason {}'.format(
            response.status_code, response.text))
    download_path = os.path.join(file_save_path, 'download.zip')
    with open(os.path.join(file_save_path, 'download.zip'), 'wb') as f:
        f.write(response.content)
    import zipfile
    zip_ref = zipfile.ZipFile(download_path)
    zip_ref.extractall(folder_path)
    zip_ref.close()
    os.remove(download_path)
    return {'downloadPath': folder_path}


def create_channel(client, channel, channel_name, resource_group_name, resource_name):
    botChannel = BotChannel(
        location='global',
        properties=channel
    )
    return client.channels.create(
        resource_group_name=resource_group_name,
        resource_name=resource_name,
        channel_name=channel_name,
        parameters=botChannel
    )


def facebook_create(client, resource_group_name, resource_name, page_id, app_id, app_secret, access_token, is_disabled=None):  # pylint: disable=line-too-long
    from azext_bot.botservice.models import FacebookChannel, FacebookChannelProperties, FacebookPage
    channel = FacebookChannel(
        properties=FacebookChannelProperties(
            pages=[FacebookPage(id=page_id, access_token=access_token)],
            app_id=app_id,
            app_secret=app_secret,
            is_enabled=not is_disabled
        )
    )
    return create_channel(client, channel, 'FacebookChannel', resource_group_name, resource_name)


def email_create(client, resource_group_name, resource_name, email_address, password, is_disabled=None):
    from azext_bot.botservice.models import EmailChannel, EmailChannelProperties
    channel = EmailChannel(
        properties=EmailChannelProperties(
            email_address=email_address,
            password=password,
            is_enabled=not is_disabled
        )
    )
    return create_channel(client, channel, 'EmailChannel', resource_group_name, resource_name)


def msteams_create(client, resource_group_name, resource_name, is_disabled=None, enable_messaging=None,
                   enable_media_cards=None, enable_video=None, enable_calling=None):
    from azext_bot.botservice.models import MsTeamsChannel, MsTeamsChannelProperties
    channel = MsTeamsChannel(
        properties=MsTeamsChannelProperties(
            is_enabled=not is_disabled,
            enable_messaging=enable_messaging,
            enable_media_cards=enable_media_cards,
            enable_video=enable_video,
            enable_calling=enable_calling
        )
    )
    return create_channel(client, channel, 'MsTeamsChannel', resource_group_name, resource_name)


def skype_create(client, resource_group_name, resource_name, is_disabled=None, enable_messaging=None,
                 enable_media_cards=None, enable_video=None, enable_calling=None,
                 enable_screen_sharing=None, enable_groups=None, calling_web_hook=None):
    from azext_bot.botservice.models import SkypeChannel, SkypeChannelProperties
    channel = SkypeChannel(
        properties=SkypeChannelProperties(
            is_enabled=not is_disabled,
            enable_messaging=enable_messaging,
            enable_media_cards=enable_media_cards,
            enable_video=enable_video,
            enable_calling=enable_calling,
            enable_screen_sharing=enable_screen_sharing,
            enable_groups=enable_groups,
            calling_web_hook=calling_web_hook
        )
    )
    return create_channel(client, channel, 'SkypeChannel', resource_group_name, resource_name)


def kik_create(client, resource_group_name, resource_name, user_name, api_key, is_disabled=None, is_validated=None):
    from azext_bot.botservice.models import KikChannel, KikChannelProperties
    channel = KikChannel(
        properties=KikChannelProperties(
            user_name=user_name,
            api_key=api_key,
            is_enabled=not is_disabled,
            is_validated=is_validated
        )
    )
    return create_channel(client, channel, 'KikChannel', resource_group_name, resource_name)


def webchat_create(client, resource_group_name, resource_name, is_disabled=None, enable_preview=None, site_name='default'):  # pylint: disable=line-too-long
    if not enable_preview:
        enable_preview = False
    from azext_bot.botservice.models import WebChatChannel, WebChatChannelProperties, WebChatSite
    channel = WebChatChannel(
        properties=WebChatChannelProperties(
            sites=[WebChatSite(
                site_name=site_name,
                is_enabled=not is_disabled,
                enable_preview=enable_preview,
            )]
        )
    )
    return create_channel(client, channel, 'WebChatChannel', resource_group_name, resource_name)


def directline_create(client, resource_group_name, resource_name, is_disabled=None,
                      is_v1_disabled=None, is_v3_disabled=None, site_name='default'):
    from azext_bot.botservice.models import DirectLineChannel, DirectLineChannelProperties, DirectLineSite
    channel = DirectLineChannel(
        properties=DirectLineChannelProperties(
            sites=[DirectLineSite(
                site_name=site_name,
                is_enabled=not is_disabled,
                is_v1_enabled=not is_v1_disabled,
                is_v3_enabled=not is_v3_disabled
            )]
        )
    )
    return create_channel(client, channel, 'DirectLineChannel', resource_group_name, resource_name)


def telegram_create(client, resource_group_name, resource_name, access_token, is_disabled=None, is_validated=None):
    from azext_bot.botservice.models import TelegramChannel, TelegramChannelProperties
    channel = TelegramChannel(
        properties=TelegramChannelProperties(
            access_token=access_token,
            is_enabled=not is_disabled,
            is_validated=is_validated
        )
    )
    return create_channel(client, channel, 'TelegramChannel', resource_group_name, resource_name)


def sms_create(client, resource_group_name, resource_name, phone, account_sid, auth_token, is_disabled=None, is_validated=None):  # pylint: disable=line-too-long
    from azext_bot.botservice.models import SmsChannel, SmsChannelProperties
    channel = SmsChannel(
        properties=SmsChannelProperties(
            phone=phone,
            account_sid=account_sid,
            auth_token=auth_token,
            is_enabled=not is_disabled,
            is_validated=is_validated
        )
    )
    return create_channel(client, channel, 'SmsChannel', resource_group_name, resource_name)


def slack_create(client, resource_group_name, resource_name, client_id, client_secret, verification_token,
                 is_disabled=None, landing_page_url=None):
    from azext_bot.botservice.models import SlackChannel, SlackChannelProperties
    channel = SlackChannel(
        properties=SlackChannelProperties(
            client_id=client_id,
            client_secret=client_secret,
            verification_token=verification_token,
            landing_page_url=landing_page_url,
            is_enabled=not is_disabled
        )
    )
    return create_channel(client, channel, 'SlackChannel', resource_group_name, resource_name)


class ChannelOperations(object):  # pylint: disable=too-few-public-methods
    def __init__(self):
        for channel in ['facebook', 'email', 'msTeams', 'skype', 'kik', 'webChat', 'directLine', 'telegram', 'sms', 'slack']:  # pylint: disable=line-too-long
            channelName = '{}Channel'.format(channel)
            channelName = channelName[:1].upper() + channelName[1:]

            def get_wrapper(channel_name):
                def get(self, resource_group_name, resource_name):
                    return self.get(
                        resource_group_name=resource_group_name,
                        resource_name=resource_name,
                        channel_name=channel_name
                    )
                return get

            def delete_wrapper(channel_name):
                def delete(self, resource_group_name, resource_name):
                    return self.delete(
                        resource_group_name=resource_group_name,
                        resource_name=resource_name,
                        channel_name=channel_name
                    )
                return delete
            setattr(self, '{}_get'.format(channel.lower()), get_wrapper(channelName))
            setattr(self, '{}_delete'.format(channel.lower()), delete_wrapper(channelName))


channelOperationsInstance = ChannelOperations()
