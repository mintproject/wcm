# -*- coding: utf-8 -*-

import configparser
import functools
import importlib
import logging
import os
import time
from contextlib import contextmanager
from csv import DictReader, Sniffer
from pathlib import Path

from wcm import wings

log = logging.getLogger()


def init_logger():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if os.getenv("WINGS_DEBUG", False) else logging.INFO)


def locate_wings_config(wcm_credential_file=None):
    if not wcm_credential_file:
        wcm_credential_file = Path(
            os.getenv("WCM_CREDENTIALS_FILE", "~/.wcm/credentials")
        ).expanduser()
    return wcm_credential_file


def wings_config(wings_config):
    wings_config = locate_wings_config(wings_config)
    if not Path(wings_config).exists():
        raise ValueError(f"Invalid wings_config {wings_config}")

    config = configparser.ConfigParser()
    config.read(wings_config)

    wcm_profile = os.getenv("WCM_PROFILE", "default")
    return (
        {
            "server": os.getenv(
                "WCM_WINGS_SERVER", config[wcm_profile]["serverWings"]
            ).strip("/"),
            "exportURL": os.getenv(
                "WCM_WINGS_EXPORT_URL", config[wcm_profile]["exportWingsURL"]
            ),
            "userid": os.getenv("WCM_USER", config[wcm_profile]["userWings"]),
            "domain": os.getenv("WCM_DOMAIN", config[wcm_profile]["domainWings"]),
        },
        os.getenv("WCM_PASSWORD", config[wcm_profile]["passwordWings"]),
    )


def load_module(module_name):
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        log.error("Model <%s> not found" % module_name)
        raise


@contextmanager
def cli(cfg, template):
    config, passwd = wings_config(cfg)
    data = wings.ManageData(**config)
    planner = wings.Planner(template=template, **config)
    with login(data, passwd) as data, login(planner, passwd) as planner:
        yield data, planner


@contextmanager
def component_cli(cfg):
    config, passwd = wings_config(cfg)
    component = wings.ManageComponent(**config)
    data = wings.ManageData(**config)
    with login(component, passwd) as component, login(data, passwd) as data:
        yield component, data


@contextmanager
def login(w, password):
    if w.login(password):
        try:
            yield w
        finally:
            log.debug("Logout")
            w.logout()
    else:
        raise ValueError("WINGS login failed")


def upload_files(model, args):
    log.debug("Upload Files")

    cli = model.wings["data"]
    for k, v in args.items():
        if isinstance(v, Path):
            t = model.__IO_TYPES__[k]
            log.info("Upload file <%s> of type <%s>" % (v, t))
            cli.upload_data_for_type(v.resolve(), t)


def run_template(model, args):
    log.debug("Run Template")
    run_args = args.copy()
    for k, v in args.items():
        if isinstance(v, Path):
            run_args[k] = "file:%s" % v.name

    cli = model.wings["planner"]
    ret = cli.get_expansions(run_args)
    if ret and ret["success"]:
        templates = ret["data"]["templates"]
        log.debug(len(templates))
        runid = cli.run_workflow(templates[0], ret["data"]["seed"])
        log.info("Started run with id <%s>" % runid)


def throttle(chunk_size=15, wait=60):
    def wrap(f):
        @functools.wraps(f)
        def wrapped_f(*args, **kwargs):
            rv = f(*args)
            if rv is not None:
                if wrapped_f.count % chunk_size == 0 and wrapped_f.count != 0:
                    log.info(
                        "Sleep for %d seconds before iteration <%d>"
                        % (wait, wrapped_f.count)
                    )
                    time.sleep(wait)
                wrapped_f.count += 1

            return rv

        wrapped_f.count = 0
        return wrapped_f

    return wrap


def simulation_matrix(sim_file):
    if not Path(sim_file).exists():
        raise ValueError("Invalid simulation-matrix")

    with open(sim_file) as csvfile:
        dialect = Sniffer().sniff(csvfile.read(4096))
        csvfile.seek(0)
        reader = DictReader(csvfile, dialect=dialect)
        for row in reader:
            yield row
