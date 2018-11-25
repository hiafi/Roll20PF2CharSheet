import requests
from lxml import html
import re
import json

from pyquery import PyQuery as pq
from unidecode import unidecode


class Section(object):

    def __init__(self, title):
        self.title = title
        self.contents = []

    @staticmethod
    def create(title):
        try:
            if re.search(r"Feat (\d+)", title.find("span").text):
                return Feat(title)
        except Exception:
            pass
        return Section(title)

    def find_term(self, regex_str, str_to_search=None):
        if str_to_search is None:
            for c in self.contents:
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
        return self.title.find("span").text

    def add_contents(self, content):

        self.contents.append(content)

    @property
    def key_name(self):
        return self.title_text

    def to_dict(self):
        return {
            "text": self.contents_text
        }

    def parse_children_str(self, child_obj):
        return str(html.tostring(child_obj))\
            .replace("<p>", "")\
            .replace("</p>", "")

    def content_text(self, content):
        if isinstance(content, Section):
            return content.contents_text
        elif len(content):
            return self.parse_children_str(content)
        else:
            return unidecode(content.text)

    @property
    def contents_text(self):
        element_text = []
        for c in self.contents:
            if isinstance(c, Section):
                element_text.append(c.contents_text)
            if len(c):
                element_text.append(self.parse_children_str(c))
            else:
                element_text.append(unidecode(c.text))
        return " ".join(element_text)

    def __str__(self):
        return "{}: {}".format(self.title_text, self.contents_text)

    def __repr__(self):
        return self.__str__()


class Feat(Section):

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

    def to_dict(self):
        return {
            "text": self.contents_text,
            "level": self.required_level,
            "prerequisite": self.prereq,
            "trigger": self.trigger,
            "requirements": self.requirements,
        }


class Spell(Section):

    @property
    def title_text(self):
        return self.title

    @property
    def level(self):
        return self.find_term(r"Power</a> (\d+)") or self.find_term(r"Spell</a> (\d+)")

    @property
    def traits(self):
        return self.find_term(r"<b>Traits</b> (.+)")

    @property
    def actions(self):
        return self.find_term(r"<b>Actions</b> (.+?)<br>")

    @property
    def area(self):
        return self.find_term(r"<b>Area</b> (.+)<br>")

    @property
    def duration(self):
        return self.find_term(r"<b>Duration</b> (.+)")

    @property
    def description(self):
        return self.find_term(r"Description (.+)", self.contents_text)

    def to_dict(self):
        return {
            "level": int(self.level) if self.level else None,
            "traits": self.traits,
            "actions": self.actions,
            "area": self.area,
            "duration": self.duration,
            "description": self.description,
        }


class GenericPage(object):

    def __init__(self, name):
        self.sections = {}
        self.name = name

    @property
    def url(self):
        return "http://pf2playtest.opengamingnetwork.com/"

    def get_page_content(self, url=None):
        if url is None:
            url = self.url
        bulk_html = pq(requests.get(url).text)
        return bulk_html(".article-content")

    def to_dict(self):
        return {
            s.key_name: s.to_dict()
            for s in self.sections.values()
        }

    def pprint(self):
        for name, txt in self.to_dict().items():
            print(name)
            print("\t", txt)

    def parse(self, create_method=Section.create):
        content = self.get_page_content()
        section = Section(None)
        for child in content.children():
            if child.tag in ("hr", ):
                continue
            if child.tag in ("h3", "h4"):
                if section:
                    self.sections[section.title_text] = section
                section = create_method(child)
            elif section:
                section.add_contents(child)
        self.sections[section.title_text] = section


class RacePage(GenericPage):

    @property
    def url(self):
        return "http://pf2playtest.opengamingnetwork.com/ancestries/{}/".format(self.name)

    def to_dict(self):
        return_dict = super(RacePage, self).to_dict()
        return_dict["hp"] = re.search(r"<b>Hit Points</b> (\d+)", self.sections.get("Overview").contents_text).group(1)
        return_dict["size"] = re.search(r"\| <strong>Size</strong> (.+) \|", self.sections.get("Overview").contents_text).group(1)
        return_dict["speed"] = re.search(r"\| <strong>Speed</strong> (\d+)", self.sections.get("Overview").contents_text).group(1)
        return return_dict


class ClassPage(GenericPage):

    @property
    def url(self):
        return "http://pf2playtest.opengamingnetwork.com/classes/{}/".format(self.name)


class FeatsPage(GenericPage):

    @property
    def url(self):
        return "http://pf2playtest.opengamingnetwork.com/feats/"


class SpellPage(GenericPage):

    @property
    def url(self):
        return "http://pf2playtest.opengamingnetwork.com/spells/all-spells/{}/{}/".format(self.name[0].lower(), self.name)

    def parse(self, create_method=Section.create):
        content = self.get_page_content()
        section = Spell(self.name)
        for child in content.children():
            if child.tag in ("hr", ):
                continue
            elif section:
                section.add_contents(child)
        self.sections["spell"] = section

    @staticmethod
    def get_all_spell_names():
        bulk_html = pq(requests.get("http://pf2playtest.opengamingnetwork.com/spells/all-spells/").text)
        content = bulk_html(".article-content")(".ogn-childpages")
        return [c.get("href").split("/")[-2] for c in content.find("li > ul > li > a")]

def main():
    ancestries = ["dwarf"]
    classes = ["barbarian"]
    spells = SpellPage.get_all_spell_names()

    # for a in ancestries:
    #     race = RacePage(a)
    #     race.parse()
    #
    # for c in classes:
    #     clas = ClassPage(c)
    #     clas.parse()
    #
    # feats = FeatsPage("")
    # feats.parse()

    f = open("spells.json", "w")
    spell_dict = {}
    for s in spells:
        spell = SpellPage(s)
        spell.parse()
        spell_dict[spell.name] = spell.to_dict()
    f.write(json.dumps(spell_dict))
    f.close()


if __name__ == "__main__":
    main()