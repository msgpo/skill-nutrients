from mycroft.skills.core import MycroftSkill, intent_file_handler
from mycroft.audio import wait_while_speaking
from py_edamam import Edaman


__author__ = 'jarbas'


class NutrientsSkill(MycroftSkill):
    def __init__(self):
        super(NutrientsSkill, self).__init__()
        # free keys for the people
        if "recipes_appid" not in self.settings:
            self.settings["recipes_appid"] = 'eceecbfb'
        if "recipes_appkey" not in self.settings:
            self.settings["recipes_appkey"] = \
                '83347a87348057d5ab183aade8106646'
        if "nutrition_appid" not in self.settings:
            self.settings["nutrition_appid"] = '5a32958e'
        if "nutrition_appkey" not in self.settings:
            self.settings["nutrition_appkey"] = \
                'cabec6b9addb1666e1365303e509f450'

        self.edamam = Edaman(nutrition_appid=self.settings["nutrition_appid"],
                           nutrition_appkey=self.settings["nutrition_appkey"],
                           recipes_appid=self.settings["recipes_appid"],
                           recipes_appkey=self.settings["recipes_appkey"])

    @intent_file_handler("ingredients.intent")
    def handle_ingredients_intent(self, message):
        sentence = message.data["sentence"]
        # TODO use dialog file
        sentences = self.edamam.pretty_nutrient(sentence).split("\n")
        self.enclosure.deactivate_mouth_events()
        for idx, s in enumerate(sentences):
            self.speak(s)
            if idx >= 2:
                self.enclosure.mouth_text(s)
            wait_while_speaking()
        self.enclosure.activate_mouth_events()

    @intent_file_handler("calories.intent")
    def handle_calories_intent(self, message):
        sentence = message.data["sentence"]
        n = self.edamam.search_nutrient(sentence)
        if n is None:
            query = "1 gram of " + sentence
            n = self.edamam.search_nutrient(query)
            n["name"] = "1 gram of " + n["name"]
        if n is not None:
            # TODO dialog file
            self.speak(n["name"] + " has " + str(n["calories"]) + " calories")
        else:
            # TODO dialog file
            self.speak("unknown food")

def create_skill():
    return NutrientsSkill()
