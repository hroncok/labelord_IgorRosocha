# This is skeleton for labelord module
# MI-PYT, task 1 (requests+click)
# File: labelord.py

import click
import requests
import configparser
import json


def create_request(url, session):
    """Create a GitHub request and return the json."""
    r = session.get(url)
    if r.status_code == 404:
        click.echo('GitHub: ERROR 404 - Not Found')
        exit(5)

    if r.status_code == 401:
        click.echo('GitHub: ERROR 401 - Bad credentials')
        exit(4)

    if r.status_code != 200:
        exit(10)

    return get_json(r, session)


def get_json(request, session):
    """Get the json from request and return all of the URLs."""
    result = request.json()
    if request.links:
        while 'next' in request.links:
            next_url = request.links['next']['url']
            request = session.get(next_url)
            result = result + request.json()
    return result


def parse_labels(labels):
    """Parse the labels."""
    parsed_labels = {}
    for label in labels:
        parsed_labels[label['name']] = label['color']
    return parsed_labels


def get_labels(session, reposlug, configuration):
    """Get all of the labels from the specified repository."""
    quiet = configuration['quiet']
    verbose = configuration['verbose']
    url = 'https://api.github.com/repos/{}/labels?per_page=100&page=1'.format(reposlug)
    r = session.get(url)
    if r.status_code == 404:
        if (not quiet and not verbose) or (quiet and verbose):
            click.echo('ERROR: LBL; {}; 404 - Not Found'.format(reposlug))
        else:
            if not quiet:
                click.echo('[LBL][ERR] {}; 404 - Not Found'.format(reposlug))
        return None

    if r.status_code == 401:
        click.echo('GitHub: ERROR 401 - Bad credentials')

    if r.status_code != 200:
        exit(10)

    return get_json(r, session)


def create_label(session, reposlug, name, color, configuration):
    """Create the specified label and add to the specified GitHub repository."""
    dry_run = configuration['dry_run']
    quiet = configuration['quiet']
    verbose = configuration['verbose']
    if not dry_run:
        header = {'name': name, 'color': color}
        url = 'https://api.github.com/repos/' + reposlug + '/labels'
        response = session.post(url, json.dumps(header))

        if (not quiet and not verbose) or (quiet and verbose):
            if response.status_code != 201:
                error_string = response.json()['message']
                click.echo('ERROR: ADD; {}; {}; {}; {} - {}'.format(reposlug, name, color, response.status_code,
                                                                    error_string))
                return False
            else:
                return True

        if response.status_code == 201:
            if verbose:
                click.echo('[ADD][SUC] {}; {}; {}'.format(reposlug, name, response.json()['color']))
            return True
        else:
            if verbose:
                error_string = response.json()['message']
                click.echo('[ADD][ERR] {}; {}; {}; {} - {}'.format(reposlug, name, color, response.status_code,
                                                                   error_string))
                return False
    else:
        if verbose:
            click.echo('[ADD][DRY] {}; {}; {}'.format(reposlug, name, color))
        return True


def remove_label(session, reposlug, name, color, configuration):
    """Remove the specified label from the specified GitHub repository."""
    dry_run = configuration['dry_run']
    quiet = configuration['quiet']
    verbose = configuration['verbose']
    if not dry_run:
        url = 'https://api.github.com/repos/' + reposlug + '/labels/' + name
        response = session.delete(url)

        if (not quiet and not verbose) or (quiet and verbose):
            if response.status_code != 204:
                error_string = response.json()['message']
                click.echo('ERROR: DEL: {}; {}; {}'.format(reposlug, name, error_string))
                return False
            else:
                return True

        if response.status_code == 204:
            if verbose:
                click.echo('[DEL][SUC] {}; {}; {}'.format(reposlug, name, color))
            return True
        else:
            if verbose:
                error_string = response.json()['message']
                click.echo('[DEL][ERR] {}; {}; {}; {} - {}'.format(reposlug, name, color, response.status_code,
                                                                   error_string))
                return False
    else:
        if verbose:
            click.echo('[DEL][DRY] {}; {}; {}'.format(reposlug, name, color))
        return True


def edit_label(session, reposlug, old_name, new_name, color, configuration):
    """Edit the specified label (name, color or both) in the specified GitHub repository."""
    dry_run = configuration['dry_run']
    quiet = configuration['quiet']
    verbose = configuration['verbose']
    if not dry_run:
        header = {'name': new_name, 'color': color}
        url = 'https://api.github.com/repos/' + reposlug + '/labels/' + old_name
        response = session.patch(url, json.dumps(header))

        if (not quiet and not verbose) or (quiet and verbose):
            if response.status_code != 200:
                error_string = response.json()['message']
                click.echo('ERROR: UPD; {}; {}; {}; {} - {}'.format(reposlug, new_name, color, response.status_code,
                                                                    error_string))
                return False
            else:
                return True

        if response.status_code == 200:
            if verbose:
                click.echo('[UPD][SUC] {}; {}; {}'.format(reposlug, new_name, color))
            return True
        else:
            if verbose:
                error_string = response.json()['message']
                click.echo('[UPD][ERR] {}; {}; {}; {} - {}'.format(reposlug, new_name, color, response.status_code,
                                                                   error_string))
                return False
    else:
        if verbose:
            click.echo('[UPD][DRY] {}; {}; {}'.format(reposlug, new_name, color))
        return True


def diff(first, second):
    """Compute the difference between two lists."""
    second = set(second)
    return [item for item in first if item not in second]


def print_version(ctx, param, value):
    """Print version of the app."""
    if not value or ctx.resilient_parsing:
        return
    click.echo('labelord, version 0.1')
    ctx.exit()


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


@click.group('labelord')
@click.option('-c', '--config', default='./config.cfg',
              help='Path to the config containing the GitHub token.')
@click.option('-t', '--token', envvar='GITHUB_TOKEN',
              help='GitHub token')
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="Show the version and exit.")
@click.pass_context
def cli(ctx, config, token):
    ctx.obj['token'] = token
    ctx.obj['config'] = config


@cli.command()
@click.pass_context
def list_repos(ctx):
    """List all of the repositories"""
    validate_token(ctx)
    session = ctx.obj['session']
    r = create_request('https://api.github.com/user/repos?per_page=100&page=1', session)
    for repository in r:
        click.echo(repository["full_name"])
    exit(0)


@cli.command()
@click.argument('reposlug', nargs=1)
@click.pass_context
def list_labels(ctx, reposlug):
    """List all of the labels from specified GitHub repository"""
    validate_token(ctx)
    session = ctx.obj['session']
    r = create_request('https://api.github.com/repos/' + reposlug + '/labels?per_page=100&page=1', session)
    for label in r:
        click.echo('#' + label['color'] + ' ' + label['name'])
    exit(0)


@cli.command()
@click.option('-r', '--template-repo', default='',
              help='Path to the template repository.')
@click.option('-a', '--all-repos', is_flag=True,
              help='Select all repositories.')
@click.option('-d', '--dry-run', is_flag=True,
              help='Perform a dry run (without editing on GitHub).')
@click.option('-v', '--verbose', is_flag=True,
              help='Print the result of dry run on the standard output.')
@click.option('-q', '--quiet', is_flag=True,
              help='Do not print the result of dry run on the standard output.')
@click.argument('mode', nargs=1, type=click.Choice(['update', 'replace']))
@click.pass_context
def run(ctx, mode, **configuration):
    """Update the labels (ADD, EDIT or DELETE)"""
    config = ctx.obj['config']
    quiet = configuration['quiet']
    verbose = configuration['verbose']
    all_repos = configuration['all_repos']
    template_repo = configuration['template_repo']

    errors = 0
    get = 0

    validate_token(ctx)
    session = ctx.obj['session']

    # Parse the config using ConfigParser and preserve the case sensitivity.
    config_file = configparser.ConfigParser()
    config_file.optionxform = str

    if not config_file.read(config):
        exit(3)

    if 'labels' not in config_file:
        click.echo('No labels specification has been found')
        exit(6)

    if 'repos' not in config_file:
        click.echo('No repositories specification has been found')
        exit(7)

    if not config_file['repos']:
        click.echo('SUMMARY: 0 repo(s) updated successfully')
        exit(0)

    repos = []
    repos_count = 0

    # If  -a / --all-repos switch is used, fill the repos list with all of the repositories,
    # else check which repositories in config file are allowed to be used.
    if all_repos:
        r = create_request('https://api.github.com/user/repos?per_page=100&page=1', session)
        for repository in r:
            repos.append(repository['full_name'])
            repos_count += 1
    else:
        config_repos = config_file['repos']
        for repository in config_repos:
            if config_file['repos'].getboolean(repository):
                repos.append(repository)
                repos_count += 1

    # If -r / --template-repo switch is used, define the labels from specified GitHub repository,
    # else define the labels from config file and parse them.
    if template_repo or 'others' in config_file:
        if template_repo:
            template_repository_name = template_repo
        else:
            template_repository_name = config_file['others']['template-repo']
        all_config_labels = get_labels(session, template_repository_name, configuration)
        parsed_all_config_labels = parse_labels(all_config_labels)
    else:
        parsed_all_config_labels = config_file['labels']

    # Get all of the labels included in specified repositories in repos list and parse their names and colors.
    for repository in repos:
        if not all_repos:
            if config_file['repos'].getboolean(repository):
                all_repo_labels = get_labels(session, repository, configuration)
        else:
            all_repo_labels = get_labels(session, repository, configuration)

        if all_repo_labels is not None:
            repo_labels_parsed = parse_labels(all_repo_labels)
            repo_labels_lower = [x.lower() for x in repo_labels_parsed]
            config_labels_lower = [x.lower() for x in parsed_all_config_labels]
            all_repo_labels_name = [x for x in repo_labels_parsed]

            # If the replace mode is chosen, find the difference between repository labels and labels specified and
            # delete the necessary.
            if mode == 'replace':
                labels_to_delete = diff(repo_labels_lower, config_labels_lower)
                for label in labels_to_delete:
                    i = repo_labels_lower.index(label)
                    label_name = all_repo_labels_name[i]
                    if not remove_label(session, repository, label_name, repo_labels_parsed[label_name],
                                        configuration):
                        errors += 1

            # Add or edit specified labels in GitHub repositories.
            for label_name in parsed_all_config_labels:
                config_label_name_lower = label_name.lower()
                config_label_color = parsed_all_config_labels[label_name]

                if config_label_name_lower in repo_labels_lower:
                    old_name_index = repo_labels_lower.index(config_label_name_lower)
                    old_label_name = all_repo_labels_name[old_name_index]

                    if label_name in repo_labels_parsed:
                        if config_label_color != repo_labels_parsed[label_name]:
                            if not edit_label(session, repository, old_label_name, label_name, config_label_color,
                                              configuration):
                                errors += 1
                    else:
                        if not edit_label(session, repository, old_label_name, label_name, config_label_color,
                                          configuration):
                            errors += 1
                else:
                    if not create_label(session, repository, label_name, config_label_color, configuration):
                        errors += 1
                    else:
                        get += 1
        else:
            errors += 1

    # Print the result of run depending on the configuration of switches and number of errors.
    if (not quiet and not verbose) or (quiet and verbose):
        if errors > 0:
            click.echo('SUMMARY: {} error(s) in total, please check log above'.format(errors))
            exit(10)
        else:
            click.echo('SUMMARY: {} repo(s) updated successfully'.format(repos_count))
            exit(0)

    if not quiet:
        if errors > 0:
            click.echo('[SUMMARY] {} error(s) in total, please check log above'.format(errors))
            exit(10)
        else:
            click.echo('[SUMMARY] {} repo(s) updated successfully'.format(repos_count))
            exit(0)
    else:
        if errors > 0:
            exit(10)
        else:
            exit(0)


if __name__ == '__main__':
    cli(obj={})
