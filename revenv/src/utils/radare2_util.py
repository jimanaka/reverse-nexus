import rzpipe
from flask import jsonify
from http import HTTPStatus as HTTP
from typing import Dict, Tuple, IO
from src.utils.request_util import corsify_response
from pprint import pprint


def _setup_rd2(filename: str) -> IO:
    r = rzpipe.open(filename)
    r.cmd("e log.level=5")
    r.cmd("aaa")
    return r


def get_file_info(request_details: Dict) -> Tuple[Dict, int]:
    filename = request_details["filename"]
    r = _setup_rd2(filename)
    payload = r.cmdj("iaj")
    payload["afl"] = r.cmdj("aflj")
    response = jsonify(msg="r2response", payload=payload)
    response = corsify_response(response)
    r.quit()
    return response, HTTP.OK.value


def disassemble_binary(filename: str, direction: str = None, target: str = "", mode: str = "add") -> Tuple[Dict, int]:
    r = _setup_rd2(filename)

    if (direction == "up"):
        sign = "-"
    else:
        sign = ""

    if not target:
        target = "entry0"

    payload = r.cmdj(f"pdJ {sign}64 @ {target}")
    response = jsonify(msg="r2response", payload=payload, direction=direction, mode=mode)
    response = corsify_response(response)
    r.quit()
    return response, HTTP.OK.value


def decompile_function(filename: str, address: str = "") -> Tuple[Dict, int]:
    r = _setup_rd2(filename)
    payload: str = r.cmd(f"pdg @ {address}")
    payload = payload.splitlines(keepends=True)
    response = jsonify(msg="r2response", payload=payload)
    response = corsify_response(response)
    r.quit()
    return response, HTTP.OK.value
