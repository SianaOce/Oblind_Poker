import os
import json

from oblind.constants import CONFIG_DIR

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)
if os.path.isfile(os.path.join(CONFIG_DIR, "chips.json")):
    with open(os.path.join(CONFIG_DIR, "chips.json"), "r") as read_file:
        chips = json.load(read_file)
else:
    chips = {}


def verify_name(name):
    if name in chips:
        print(f"<{name}> : nom déjà existant")
        return False
    return True


def create_chip(name, qty_total):
    chips.update({name: {"qty_total": qty_total, "value": 0, "qty_use": 0, "n_use": 0}})
    save_json(chips)


def delete_chip(name):
    del chips[name]
    save_json(chips)


def chip_maj_qty(name, qty_total):
    chips[name]["qty_total"] = qty_total
    save_json(chips)


def chip_maj_val(name, val):
    if name in chips:
        chips[name]["value"] = val
        save_json(chips)


def chip_maj_nb(name, nb):
    if name in chips:
        chips[name]["qty_use"] = nb
        save_json(chips)


def chip_maj_use(name, n):
    chips[name]["n_use"] = n
    save_json(chips)


def value_cave():
    cave = 0
    for key, item in chips.items():
        if item["n_use"] != 0:
            cave += item["qty_use"] * item["value"]
    return str(cave)


def nbchips_cave():
    nb_chips = 0
    for key, item in chips.items():
        if item["n_use"] != 0:
            nb_chips += item["qty_use"]
    return str(nb_chips)


def chips_init_use():
    for key, item in chips.items():
        chips[key]["n_use"] = 0
    save_json(chips)


def list_chips():
    return chips


def save_json(dict_c):
    with open(os.path.join(CONFIG_DIR, "chips.json"), "w") as write_file:
        json.dump(dict_c, write_file, indent=4)


if __name__ == '__main__':
    print(chips)
