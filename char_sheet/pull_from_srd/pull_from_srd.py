import collections
import json
import re

from bs4 import BeautifulSoup
import requests
from unidecode import unidecode

from char_sheet.pull_from_srd.ignores import IGNORES
from char_sheet.pull_from_srd.overwrites import OVERWRITES

ability_name_regex_2 = r"(.+) (\d+)[rdstnh][rdstnh]"


class Section(object):

    def __init__(self, title):
        self.title = title
        self.contents = []

    @staticmethod
    def create(title):
        try:
            inner_html = title.find("span")
            if re.search(r"Feat (\d+)", title.find("span").text):
                return Feat(title)
            if re.search(ability_name_regex_2, title.find("span").text):
                return Feat(title)
        except Exception:
            pass
        return Section(title)

    def find_term(self, regex_str, str_to_search=None):
        if str_to_search is None:
            for c in self.contents:
                t = self.content_text(c)
                m = re.search(regex_str, self.content_text(c))
                if m:
                    return m.group(1)
        else:
            m = re.search(regex_str, str_to_search)
            if m:
                return m.group(1)
        return None

    @property
    def title_text(self):
        if self.title is None:
            return "Opening"
        if self.title.find("span").text is None:
            return None
        title_name = unidecode(self.title.find("span").text.strip())
        return title_name

    def add_contents(self, content):
        self.contents.append(content)

    @property
    def key_name(self):
        return self.title_text

    def to_dict(self, ignore=None):
        return {
            "text": self.contents_text
        }

    def content_text(self, content):
        if isinstance(content, Section):
            return content.contents_text
        return unidecode(content.text)

    @property
    def contents_text(self):
        element_text = []
        for c in self.contents:
            if isinstance(c, Section):
                element_text.append(c.contents_text)
            else:
                element_text.append(c.text)
        return unidecode(" ".join(element_text))

    def __str__(self):
        return "{}: {}".format(self.title_text, self.contents_text)

    def __repr__(self):
        return self.__str__()


class Feat(Section):

    @property
    def key_name(self):
        search1 = re.search("(.+) Feat \d+", self.title_text)
        if search1:
            return search1.group(1)
        return re.search(ability_name_regex_2, self.title_text).group(1)

    @property
    def required_level(self):
        return re.search(r"(\d+)", self.title_text).group(1)

    @property
    def prereq(self):
        return self.find_term(r"<b>Prerequisite\(s\)</b>: (.+)")

    @property
    def trigger(self):
        return self.find_term(r"<b>Trigger</b>: (.+)")

    @property
    def requirements(self):
        return self.find_term(r"<b>Requirements</b>: (.+)")

    def to_dict(self, ignore=None):
        return {
            "text": self.contents_text,
            "level": self.required_level,
            "prerequisite": self.prereq,
            "trigger": self.trigger,
            "requirements": self.requirements,
            "actions": "0",
        }


class Spell(Section):

    def find_property_in_contents(self, prop_name):
        next_prop = False
        for c in self.contents[2].contents:
            if next_prop:
                return c.strip().lstrip()
            try:
                if c.text == prop_name:
                    next_prop = True
            except Exception:
                pass
        return None

    def find_in_contents(self, term, group=None, node=None):
        if node is None:
            node = self.contents
        vals_to_return = []
        for c in node:
            try:
                if c.name == "ul":
                    ret_value = self.find_in_contents(term, group, c.contents)
                    if ret_value:
                        vals_to_return.append(self.find_in_contents(term, group, c.contents))
                else:
                    match = re.search(term, c.text)
                    if match is not None:
                        if group:
                            vals_to_return.append(match.group(group))
                        else:
                            vals_to_return.append(c.text)
            except Exception:
                pass
        if vals_to_return:
            return "\n".join(vals_to_return)
        return None

    @property
    def title_text(self):
        return self.title

    @property
    def level(self):
        return self.find_term(r"Power (\d+).*") or self.find_term(r"Spell (\d+).*")

    @property
    def power(self):
        return self.find_term(r"Power (\d+).*") is not None

    @property
    def cost(self):
        return "1"

    @property
    def traits(self):
        return self.find_term(r"Traits (.+)")

    @property
    def actions(self):
        return self.find_property_in_contents("Actions")

    @property
    def reaction(self):
        if self.actions is None:
            return False
        return re.search(r".*Reaction.*", self.actions) is not None

    @property
    def verbal(self):
        if self.actions is None:
            return False
        return re.search(r".*Verbal.*", self.actions) is not None

    @property
    def material(self):
        if self.actions is None:
            return False
        return re.search(r".*Material.*", self.actions) is not None

    @property
    def somatic(self):
        if self.actions is None:
            return False
        return re.search(r".*Somatic.*", self.actions) is not None

    @property
    def area(self):
        return self.find_property_in_contents("Area")

    @property
    def range(self):
        return self.find_property_in_contents("Range")

    @property
    def duration(self):
        return self.find_property_in_contents("Duration")

    @property
    def description(self):
        desc = []
        start_capturing = False
        for c in self.contents:
            if not start_capturing:
                if c.text == "Description":
                    start_capturing = True
                continue
            if c.name != "p":
                continue
            if re.match(r"^Success (.*)$", c.text):
                continue
            if re.match(r"^Failure (.*)$", c.text):
                continue
            if re.match(r"^Critical Failure (.*)$", c.text):
                continue
            if re.match(r"^Critical Success (.*)$", c.text):
                continue
            if re.match(r"^Critical Success (.*)$", c.text):
                continue
            if re.match(r"^Heightened (.*)$", c.text):
                continue
            desc.append(c.text)
        return "\n".join(desc)

    @property
    def heighten(self):
        heighten_regex = r"(Heightened \(.*\)) (.*)"
        heighten_text = self.find_in_contents(heighten_regex)
        if heighten_text is None:
            return None
        split_by_newline = heighten_text.split("\n")
        new_heighten = []
        for line in split_by_newline:
            match = re.match(heighten_regex, line)
            if match:
                new_heighten.append("**{}**".format(match.group(1)))
                new_heighten.append(match.group(2))

        return "\n".join(new_heighten)

    @property
    def crit_success(self):
        return self.find_in_contents(r"^Critical Success (.*)$", 1)

    @property
    def success(self):
        return self.find_in_contents(r"^Success (.*)$", 1)

    @property
    def failure(self):
        return self.find_in_contents(r"^Failure (.*)$", 1)

    @property
    def crit_failure(self):
        return self.find_in_contents(r"^Critical Failure (.*)$", 1)

    def to_dict(self, ignore=None):
        return {
            "level": int(self.level) if self.level else None,
            "power": self.power,
            "traits": self.traits,
            "range": self.range,
            "cost": self.cost,
            "actions": self.actions,
            "reaction": self.reaction,
            "verbal": self.verbal,
            "somatic": self.somatic,
            "material": self.material,
            "area": self.area,
            "duration": self.duration,
            "description": self.description,
            "heighten": self.heighten,
            "crit_success": self.crit_success,
            "success": self.success,
            "failure": self.failure,
            "crit_failure": self.crit_failure,
        }


class GenericPage(object):

    def __init__(self, name):
        self.sections = {}
        self.name = name

    @property
    def display_name(self):
        return self.name

    @property
    def url(self):
        return "http://pf2playtest.opengamingnetwork.com/"

    def get_page_content(self, url=None):
        if url is None:
            url = self.url
        response = requests.get(url)
        bulk_html = BeautifulSoup(unidecode(response.text), 'html5lib')
        return bulk_html.find("div", attrs={"class": "article-content"})

    def to_dict(self, ignore=None):
        return {
            s.key_name or "": s.to_dict()
            for s in self.sections.values() if ignore is None or s.key_name not in ignore
        }

    def pprint(self):
        for name, txt in self.to_dict().items():
            print(name)
            print("\t", txt)

    def parse(self, create_method=Section.create):
        content = self.get_page_content()
        section = Section(None)
        for child in content.find_all():
            if child.name == "h4":
                self.sections[section.title_text] = section
                section = create_method(child)
            elif child.name == "p":
                section.add_contents(child)
        self.sections[section.title_text] = section


class RacePage(GenericPage):

    @property
    def url(self):
        return "http://pf2playtest.opengamingnetwork.com/ancestries/{}/".format(self.name)

    def to_dict(self, ignore=None):
        return_dict = super(RacePage, self).to_dict(ignore)
        section_name = "Opening"
        return_dict["hp"] = int(re.search(r"(<b>)?Hit Points(</b>)? (?P<val>\d+)", self.sections.get(section_name).contents_text).group("val"))
        return_dict["size"] = re.search(r"\| (<strong>)?Size(</strong>)? (?P<val>.+) \|", self.sections.get(section_name).contents_text).group("val")
        return_dict["speed"] = re.search(r"\| (<strong>)?Speed(</strong>)? (?P<val>\d+)", self.sections.get(section_name).contents_text).group("val")
        return return_dict


class ClassPage(GenericPage):

    @property
    def url(self):
        return "http://pf2playtest.opengamingnetwork.com/classes/{}/".format(self.name)

    def to_dict(self, ignore=None):
        return_dict = super(ClassPage, self).to_dict(ignore)
        section_name = "Opening"
        return_dict["hp"] = int(re.search(r"(<b>)?Hit Points(</b>)? (?P<val>\d+)", self.sections.get(section_name).contents_text).group("val"))
        return return_dict


class FeatsPage(GenericPage):

    @property
    def url(self):
        return "http://pf2playtest.opengamingnetwork.com/feats/"


class SpellPage(GenericPage):

    @property
    def display_name(self):
        return self.name.replace("-", " ").title()

    def to_dict(self, ignore=None):
        return self.sections.get("spell").to_dict()

    @property
    def url(self):
        return "http://pf2playtest.opengamingnetwork.com/spells/all-spells/{}/{}/".format(self.name[0].lower(), self.name)

    def parse(self, create_method=Section.create):
        content = self.get_page_content()
        section = Spell(self.name)

        for child in content.find_all(recursive=False):
            if child.name in ("hr", ):
                continue
            elif section:
                section.add_contents(child)
        self.sections["spell"] = section

    @staticmethod
    def get_all_spell_names():
        url = "http://pf2playtest.opengamingnetwork.com/spells/all-spells/"
        bulk_html = BeautifulSoup(requests.get(url).text, 'html5lib')
        content = bulk_html.find("div", attrs={"class": "article-content"})
        return [c.get("href").split("/")[-2] for c in content.find_all("a") if len(c.get("href").split("/")[-2]) > 1]


def write_spells():
    spell_objs = write_objs(SpellPage, SpellPage.get_all_spell_names())
    spells = {k: v for k, v in spell_objs.items() if not v.get("power")}
    powers = {k: v for k, v in spell_objs.items() if v.get("power")}
    return {"spells": spells, "powers": powers}


def write_classes():
    classes = [
        "alchemist",
        "barbarian",
        "bard",
        "cleric",
        "druid",
        "fighter",
        "monk",
        "paladin",
        "ranger",
        "rogue",
        "sorcerer",
        "wizard",
    ]
    return write_objs(ClassPage, classes)


def write_races():
    classes = [
        "dwarf",
        "elf",
        "gnome",
        "goblin",
        "halfling",
        "human",
    ]
    return write_objs(RacePage, classes, ["Overview"])


def update_dict(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def write_gen_feats():
    feats = FeatsPage("")
    feats.parse()
    ret = {"general": feats.to_dict(IGNORES.get("general", set()) | IGNORES.get("ALL"))}
    ret = update_dict(ret, OVERWRITES.get("general", {}))
    return ret


def print_percent(val):
    print("{}%".format(round(val, 2)))


def write_objs(page_obj=None, objs_to_get=None, ignore_list=None):
    write_dict = {}
    for index, c in enumerate(objs_to_get):
        page = page_obj(c)
        page.parse()
        write_dict[page.display_name] = page.to_dict(IGNORES.get(c, set()) | IGNORES.get("ALL"))
        write_dict[page.display_name] = update_dict(write_dict[page.display_name], OVERWRITES.get(c, {}))
        print_percent(index / len(objs_to_get) * 100.0)
    return write_dict


def write_to_file(dict_obj, fname):
    f = open("{}.json".format(fname), "w")
    f.write(json.dumps(dict_obj, indent=4, sort_keys=True))
    f.close()


def main():
    output = {}
    output.update(write_races())
    output.update(write_classes())
    output.update(write_gen_feats())
    output.update(write_spells())
    write_to_file(output, "feats")


if __name__ == "__main__":
    main()
