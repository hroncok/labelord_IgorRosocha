import click
import requests
import configparser
import json
import flask
import hmac
import os
from flask import request
from cli import cli


def config_repos_to_list(config):
    """Parse the repositories contained in config file and create a HTML list of them. (for the web usage)"""
    config_file = configparser.ConfigParser()
    config_file.optionxform = str

    if not config_file.read(config):
        exit(3)

    if 'token' not in config_file['github']:
        click.echo('No GitHub token has been provided', err=True)
        exit(3)

    if 'webhook_secret' not in config_file['github']:
        click.echo('No webhook secret has been provided', err=True)
        exit(8)

    if 'repos' not in config_file:
        click.echo('No repositories specification has been found', err=True)
        exit(7)

    repos = []
    config_repos = config_file['repos']
    for repo in config_repos:
        if config_file['repos'].getboolean(repo):
            repos.append(repo)

    url = "https://github.com/"
    result = "master-to-master labelord GitHub webhook" + '<ul>'
    for repo in repos:
        result = result + '<li> ' + url + repo + '</li>'

    result = result + '</ul>'
    return result


def get_server_config(path):
    """Get the path to the config on server."""
    config_path = os.path.isfile(path)
    if config_path:
        return path


def validate_token(ctx):
    """Validate the token specified in config and create session."""
    token = ctx.obj['token']
    config = ctx.obj['config']
    if not token:
        config_name = config
        config_file = configparser.ConfigParser()
        if not config_file.read(config_name):
            click.echo("No GitHub token has been provided")
            exit(3)
        token = config_file['github']['token']

    session = ctx.obj.get('session', requests.Session())
    session.headers = {'User-Agent': 'Python'}

    def token_auth(req):
        req.headers['Authorization'] = 'token ' + token
        return req

    session.auth = token_auth
    ctx.obj['session'] = session
    ctx.obj['config_file'] = config
    return ctx


def web_session(config_file):
    """Create a web session."""
    token = config_file['github']['token']
    session = requests.Session()
    session.headers = {'User-Agent': 'Python'}

    def token_auth(req):
        req.headers['Authorization'] = 'token ' + token
        return req

    session.auth = token_auth
    return session


def web_session_inject(config_file, session):
    """Create a web session."""
    token = config_file['github']['token']
    session.headers = {'User-Agent': 'Python'}

    def token_auth(req):
        req.headers['Authorization'] = 'token ' + token
        return req

    session.auth = token_auth
    return session


def web_create_label(session, reposlug, name, color):
    """
    Create the specified label and add to the specified GitHub repository.
    (simplified version for web)
    """
    header = {'name': name, 'color': color}
    url = 'https://api.github.com/repos/' + reposlug + '/labels'
    session.post(url, json.dumps(header))


def web_remove_label(session, reposlug, name):
    """
    Remove the specified label from the specified GitHub repository.
    (simplified version for web)
    """
    url = 'https://api.github.com/repos/' + reposlug + '/labels/' + name
    session.delete(url)


def web_edit_label(session, reposlug, old_name, new_name, color):
    """
    Edit the specified label (name, color or both) in the specified GitHub repository.
    (simplified version for web)
    """
    header = {'name': new_name, 'color': color}
    url = 'https://api.github.com/repos/' + reposlug + '/labels/' + old_name
    session.patch(url, json.dumps(header))


def get_repos_from_config(config_file):
    """Get the list of repositories which are allowed to work with from the config file."""
    repos = []
    config_repos = config_file['repos']
    for repository in config_repos:
        if config_file['repos'].getboolean(repository):
            repos.append(repository)
    return repos


class LabelordWeb(flask.Flask):
    new_session = None
    ctx = None
    config_web = None
    last_action = None
    last_label = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def inject_session(self, session):
        self.new_session = session

    def reload_config(self):
        if 'LABELORD_CONFIG' in os.environ:
            self.config_web = os.environ['LABELORD_CONFIG']

            config_file = configparser.ConfigParser()
            config_file.optionxform = str
            if not config_file.read(self.config_web):
                exit(3)

            if 'token' not in config_file['github']:
                click.echo('No GitHub token has been provided', err=True)
                exit(3)

            if 'webhook_secret' not in config_file['github']:
                click.echo('No webhook secret has been provided', err=True)
                exit(8)

            if 'repos' not in config_file:
                click.echo('No repositories specification has been found', err=True)
                exit(7)


app = LabelordWeb(__name__)


def secret_verification(signature, message):
    """Verification of webhook secret."""
    if app.ctx:
        config = app.ctx.obj['config_file']
    else:
        if app.config_web:
            config = app.config_web
        else:
            config = get_server_config('/config.cfg')

    config_file = configparser.ConfigParser()
    config_file.optionxform = str

    if not config_file.read(config):
        exit(3)

    secret = config_file['github']['webhook_secret']
    mac = hmac.new(bytes(secret, 'utf-8'), msg=message, digestmod='sha1')
    if not str(mac.hexdigest()) == signature:
        return False

    return True


@app.route('/', methods=['GET'])
def get():
    if app.ctx:
        config = app.ctx.obj['config_file']
        return config_repos_to_list(config)
    else:
        if app.config_web:
            config = app.config_web
            return config_repos_to_list(config)
        else:
            server_config = get_server_config('/config.cfg')
            if server_config:
                return config_repos_to_list(server_config)

    return 'OK GET'


@app.route('/', methods=['POST'])
def post():
    data = request.get_json()
    if 'X-Hub-Signature' not in request.headers:
        return 'UNAUTHORIZED', 401

    signature = request.headers['X-Hub-Signature'].split("=")[1]

    if not secret_verification(signature, request.data):
        return 'UNAUTHORIZED', 401

    if data:
        if app.ctx:
            config = app.ctx.obj['config_file']
        else:
            if app.config_web:
                config = app.config_web
            else:
                config = get_server_config('/config.cfg')

        config_file = configparser.ConfigParser()
        config_file.optionxform = str

        if not config_file.read(config):
            exit(3)

        repos = get_repos_from_config(config_file)

        repository_name = data['repository']['full_name']
        if repository_name not in repos:
            return 'BAD REQUEST', 400

        if app.new_session:
            session = app.new_session
            session = web_session_inject(config_file, session)
        else:
            session = web_session(config_file)

        if 'action' in data:
            if (app.last_label != data['label']['name']) or (app.last_action != data['action']):
                if data['action'] == "created":
                    label_name = data['label']['name']
                    label_color = data['label']['color']

                    app.last_action = 'created'
                    app.last_label = label_name

                    for repository in repos:
                        if repository != repository_name:
                            web_create_label(session, repository, label_name, label_color)

                if data['action'] == 'deleted':
                    label_name = data['label']['name']

                    app.last_action = 'deleted'
                    app.last_label = label_name

                    for repository in repos:
                        if repository != repository_name:
                            web_remove_label(session, repository, label_name)

                if data['action'] == 'edited':
                    label_name = data['label']['name']
                    label_color = data['label']['color']

                    app.last_action = 'edited'
                    app.last_label = label_name

                    if "name" in data["changes"]:
                        old_name = data["changes"]["name"]["from"]
                    else:
                        old_name = label_name

                    for repository in repos:
                        if repository != repository_name:
                            web_edit_label(session, repository, old_name, label_name, label_color)
        else:
            return 'OK', 200

    return 'OK', 200


@cli.command()
@click.pass_context
@click.option('-h', '--host', default='127.0.0.1',
              help='Specification of hostname.')
@click.option('-p', '--port', default='5000',
              help='Specification of port.')
@click.option('-d', '--debug', is_flag=True,
              help='Debug mode flag.')
def run_server(ctx, **configuration):
    """Runs the flask server with specified hostname, port and debug mode."""
    debug = configuration['debug']
    port = configuration['port']
    hostname = configuration['host']
    # from web import app
    validate_token(ctx)
    session = ctx.obj['session']
    app.new_session = session
    app.ctx = ctx
    app.run(
        debug=debug,
        host=hostname,
        port=int(port)
    )

