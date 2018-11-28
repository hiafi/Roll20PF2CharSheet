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
    ("Perception", "Wisdom", False, False),
    ("", "", False, False),
    ("Acrobatics", "Dexterity", True, False),
    ("Arcana", "Intelligence", False, False),
    ("Athletics", "Strength", True, False),
    ("Crafting", "Intelligence", False, False),
    ("Deception", "Charisma", False, False),
    ("Diplomacy", "Charisma", False, False),
    ("Intimidation", "Charisma", False, False),
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
    ("Fortitude", "Constitution"),
    ("Reflex", "Dexterity"),
    ("Will", "Wisdom"),
]


def gen_char_info():
    template = env.get_template('character_info.html')
    return template.render({})


def gen_roll_templates():
    template = env.get_template('roll_templates.html')
    return template.render({})


def get_teml_block(attr_name):
    template = env.get_template('TEML_template.html')
    return template.render({"attr_name": attr_name})


def gen_hp_block():
    template = env.get_template('hp_block.html')
    return template.render({"proper_hp_name": "HP", "hp_attr": "hp"})


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
        "armor_block": gen_def_block()
    })


def gen_powers_tab():
    template = env.get_template('tab_powers_tab.html')
    return template.render({
        "powers_section": gen_powers(),
        "magic_header": gen_magic_header(),
    })


def gen_feats_tab():
    template = env.get_template('tab_feats.html')
    return template.render({

    })


def gen_equip_tab():
    template = env.get_template('tab_equipment_tab.html')
    return template.render({

    })


def gen_char_data_tab():
    template = env.get_template('tab_character_data.html')
    return template.render({

    })


def gen_character_config():
    template = env.get_template('character_config.html')
    return template.render({"attr_options": gen_attribute_options()})


def gen_attribute_options():
    template = env.get_template('attr_options.html')
    return template.render({})


def gen_scripts():
    template = env.get_template('scripts.js')
    return template.render({})


def gen_powers():
    template = env.get_template('powers_section.html')
    return template.render({})


def gen_magic_header():
    template = env.get_template('magic_header.html')
    return template.render({})


def main():
    f = open("output.html", "w")
    template = env.get_template('sheet.html')
    f.write(template.render({
        "char_info": gen_char_info(),
        "main_tab": gen_first_tab(),
        "powers_tab": gen_powers_tab(),
        "feats_tab": gen_feats_tab(),
        "equip_tab": gen_equip_tab(),
        "character_config": gen_character_config(),
        "roll_templates": gen_roll_templates(),
        "scripts": gen_scripts()
    }))
    f.close()


if __name__ == "__main__":
    main()
