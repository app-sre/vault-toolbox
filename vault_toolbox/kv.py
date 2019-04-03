import json
import hvac.exceptions

from . import utils

def _get_secret(client, mountpoint, path):
    try:
        res = client.secrets.kv.v2.read_secret_version(path, version=None, mount_point=mountpoint)
        return res.get('data', {}).get('data', {})
    except:
        return {}

def _write_secret(client, mountpoint, path, secret):
    try:
        res = client.secrets.kv.v2.create_or_update_secret(path, secret, mount_point=mountpoint)
        return res
    except:
        return {}

def _delete_secret(client, mountpoint, path):
    try:
        res = client.secrets.kv.v2.delete_metadata_and_all_versions(path, mount_point=mountpoint)
        return res
    except:
        return []

def _list_secrets(client, mountpoint, path):
    try:
        res = client.secrets.kv.v2.list_secrets(path, mount_point=mountpoint)
        return res.get('data', {}).get('keys', [])
    except:
        return []

def _copy_secret(ctx, src_mountpoint, src_path, dst_mountpoint, dst_path, secret):
    client = ctx.client
    logging = ctx.logging
    
    # Ensure destination secret URI doesn't exist (TODO: allow overwriting existing secrets)
    dst_secret = _get_secret(client, dst_mountpoint, dst_path)
    if dst_secret:
        logging.error("Destination secret already exists `{}/{}`".format(dst_mountpoint, dst_path))
        return

    # Write the source secret to the destination
    return _write_secret(client, dst_mountpoint, dst_path, secret)

def _copy_recursive(ctx, copymap, dst_mountpoint, dst_path):
    client = ctx.client
    logging = ctx.logging

    # Ensure destination path doesn't exist (TODO: allow overwriting secrets in existing paths?)
    path = list(ctx, dst_mountpoint, dst_path)
    if path:
        logging.error("Destination path already exists `{}/{}`".format(dst_mountpoint, dst_path))
        return

    for c in copymap:
        secret = _get_secret(client, c['src_mountpoint'], c['src_path']+'/'+c['src_rel_path'])
        _copy_secret(ctx,
            c['src_mountpoint'],
            c['src_path']+'/'+c['src_rel_path'],
            c['dst_mountpoint'],
            c['dst_path']+'/'+c['src_rel_path'],
            secret
        )

    return

def copy(ctx, src_mountpoint, src_path, dst_mountpoint, dst_path):
    client = ctx.client
    logging = ctx.logging

    secret = _get_secret(client, src_mountpoint, src_path)
    if secret:
        logging.info("Will copy the following secret:")
        logging.info("{} -> {}".format(src_mountpoint+'/'+src_path, dst_mountpoint+'/'+dst_path))
        if utils.yesno("Do you want to continue?"):
            return _copy_secret(ctx, src_mountpoint, src_path, dst_mountpoint, dst_path, secret)
        else:
            return False

    secrets = list(ctx, src_mountpoint, src_path, recursive=True)
    if secrets:
        copymap = []
        for secret in secrets:
            src_rel_path = secret[len(src_mountpoint+'/'+src_path)+1:]
            copymap.append({
                "src_mountpoint": src_mountpoint,
                "src_path": src_path,
                "src_rel_path": src_rel_path,
                "dst_mountpoint": dst_mountpoint,
                "dst_path": dst_path,
            })
        logging.info("Will copy the following secrets:")
        for c in copymap:
            src_full_path = c['src_mountpoint']+'/'+c['src_path']+'/'+c['src_rel_path']
            dst_full_path = c['dst_mountpoint']+'/'+c['dst_path']+'/'+c['src_rel_path']
            logging.info("{} -> {}".format(
                src_full_path,
                dst_full_path
            ))
        if utils.yesno("Do you want to continue?"):
            return _copy_recursive(ctx, copymap, dst_mountpoint, dst_path)
        else:
            return False
    
    print("Source not found!")
    return

def list(ctx, mountpoint, path, recursive=False, secrets=None, paths=None):
    client = ctx.client
    logging = ctx.logging

    if secrets is None:
        secrets = []
    
    if paths is None:
        paths = []

    path = path.lstrip('/')

    logging.debug("Listing secrets in {}/{}".format(mountpoint, path))

    res = _list_secrets(client, mountpoint, path)

    for secret in res:
        if not secret.endswith('/'):
            # We got a secret
            secrets.append(utils.join_paths(mountpoint, path, secret))
        else:
            if recursive:
                new_path = "{}/{}".format(path, secret)
                list(ctx, mountpoint, new_path, recursive, secrets, paths)

    return secrets

def delete(ctx, mountpoint, path, recursive=False, versions=[]):
    client = ctx.client
    logging = ctx.logging

    res = None
    if not recursive:
        if _get_secret(client, mountpoint, path):
            logging.debug("Deleting secret {}/{}".format(mountpoint, path))
            res = _delete_secret(client, mountpoint, path)
        else:
            logging.error("No secret found at {}/{}".format(mountpoint, path))
    else:
        secrets = list(ctx, mountpoint, path, recursive=True)
        if len(secrets) == 0:
            logging.info("No secrets found at {}".format(utils.join_paths(mountpoint, path)))
            return res
        logging.info("Will DELETE the following secret:")
        for secret in secrets:
            logging.info("{}".format(secret))
        if utils.yesno("Do you want to continue?"):
            for secret in secrets:
                p = utils.parse_vault_uri(secret)
                logging.debug("Deleting secret {}".format(utils.join_paths(p['mountpoint'], p['path'])))
                _delete_secret(client, p['mountpoint'], p['path'])
        else:
            return res
            
    return res
