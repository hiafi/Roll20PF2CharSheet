from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("char_sheet", "html"),
    autoescape=select_autoescape(['html', 'xml'])
)

attrs = [
    "Strength",
    "Dexterity",
    "Constitution",
    "Intelligence",
    "Wisdom",
    "Charisma",
]

skills = [
    ("Acrobatics", "Dexterity", True, False),
    ("Arcana", "Intelligence", False, False),
    ("Athletics", "Strength", True, False),
    ("Crafting", "Intelligence", False, False),
    ("Deception", "Charisma", False, False),
    ("Diplomacy", "Charisma", False, False),
    ("Intimidation", "Charisma", False, False),
    ("Lore", "Intelligence", False, False),
    ("Lore", "Intelligence", False, False),
    ("Medicine", "Wisdom", False, False),
    ("Nature", "Wisdom", False, False),
    ("Occultism", "Intelligence", False, False),
    ("Performance", "Charisma", False, False),
    ("Religion", "Wisdom", False, False),
    ("Society", "Intelligence", False, False),
    ("Stealth", "Dexterity", True, False),
    ("Survival", "Wisdom", False, False),
    ("Thievery", "Dexterity", True, False),
]

defenses = [
    ("Fortitude", "Strength"),
    ("Reflex", "Dexterity"),
    ("Will", "Wisdom"),
]


def get_teml_block(attr_name):
    template = env.get_template('TEML_template.html')
    return template.render({"attr_name": attr_name})


def gen_hp_block():
    template = env.get_template('hp_block.html')
    return template.render({"proper_hp_name": "HP", "hp_attr": "hp"})


def gen_stam_block():
    template = env.get_template('hp_block.html')
    return template.render({"proper_hp_name": "Stamina", "hp_attr": "stam"})


def gen_def_block():
    template = env.get_template('armor_block.html')
    return template.render({
        "defenses": defenses,
        "ac_prof": get_teml_block("def_AC_prof"),
        "tac_prof": get_teml_block("def_tAC_prof"),

    })


def gen_attrs_block():
    template = env.get_template('attributes_block.html')
    return template.render({"attributes": attrs})


def gen_skills_block():
    template = env.get_template('skills_block.html')
    return template.render({"skills": skills})


def gen_attack_block():
    template = env.get_template('attacks_block.html')
    return template.render({})


def gen_first_tab():
    template = env.get_template('tab_main_tab.html')
    return template.render({
        "attributes_block": gen_attrs_block(),
        "skills_block": gen_skills_block(),
        "attacks_block": gen_attack_block(),
        "hp_block": gen_hp_block(),
        "stam_block": gen_stam_block(),
        "armor_block": gen_def_block()
    })


def gen_powers_tab():
    template = env.get_template('tab_powers_tab.html')
    return template.render({

    })


def gen_feats_tab():
    template = env.get_template('tab_feats.html')
    return template.render({

    })


def main():
    f = open("output.html", "w")
    template = env.get_template('sheet.html')
    f.write(template.render({
        "main_tab": gen_first_tab(),
        "powers_tab": gen_powers_tab(),
        "feats_tab": gen_feats_tab(),
    }))
    f.close()


if __name__ == "__main__":
    main()
