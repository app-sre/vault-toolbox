import logging

import click
import hvac

from . import kv, utils

class Ctx(object):
    def __init__(self, address, token, debug=False):
        if debug:
            logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
        else:
            logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

        self.client = hvac.Client(url=address, token=token)
        self.logging = logging.getLogger()


@click.group()
@click.option('--address', envvar='VAULT_ADDR', default='http://127.0.0.1:8200')
@click.option('--token', envvar='VAULT_TOKEN', default='')
@click.option('--debug', is_flag=True, default=False)
@click.pass_context
def cli(ctx, address, token, debug):
    ctx.obj = Ctx(address, token, debug)

@cli.group(name='kv')
@click.pass_obj
def kv_group(ctx):
    pass

@kv_group.command()
@click.argument('uri')
@click.option('-r', '--recursive', is_flag=True, default=False)
@click.pass_obj
def list(ctx, uri, recursive=False):
    p = utils.parse_vault_uri(uri)
    secrets = kv.list(ctx, p['mountpoint'], p['path'], recursive)
    for secret in secrets:
        print(secret)

@kv_group.command()
@click.argument('src_uri')
@click.argument('dst_uri')
@click.option('-r', '--recursive', is_flag=True, default=False)
@click.pass_obj
def copy(ctx, src_uri, dst_uri, recursive=False):
    p_src = utils.parse_vault_uri(src_uri)
    p_dst = utils.parse_vault_uri(dst_uri)

    kv.copy(ctx, p_src['mountpoint'], p_src['path'],
                 p_dst['mountpoint'], p_dst['path'])

@kv_group.command()
@click.argument('uri')
@click.option('-r', '--recursive', is_flag=True, default=False)
@click.pass_obj
def delete(ctx, uri, recursive=False):
    p = utils.parse_vault_uri(uri)
    kv.delete(ctx, p['mountpoint'], p['path'], recursive)
