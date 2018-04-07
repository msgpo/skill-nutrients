from mycroft.skills.core import FallbackSkill, intent_handler, \
    intent_file_handler
from mycroft.util.log import LOG
import requests, json


__author__ = 'jarbas'


class NutrientsSkill(FallbackSkill):
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

    @intent_file_handler("ingredients.intent")
    def handle_ingredients_intent(self, message):
        sentence = message.data["sentence"]
        # TODO dialog file
        self.speak(self.pretty_nutrient(sentence))

    @intent_file_handler("calories.intent")
    def handle_calories_intent(self, message):
        sentence = message.data["sentence"]
        n = self.search_nutrient(sentence)
        if n is None:
            query = "1 gram of " + sentence
            n = self.search_nutrient(query)
            n["name"] = "1 gram of " + n["name"]
        if n is not None:
            # TODO dialog file
            self.speak(n["name"] + " has " + str(n["calories"]) + " calories")
        else:
            # TODO dialog file
            self.speak("unknown food")

    def search_recipe(self, query="chicken"):
        url = 'https://api.edamam.com/search?q=' + query + '&app_id=' + \
              self.settings["recipes_appid"] + '&app_key=' + \
              self.settings["recipes_appkey"]

        r = requests.get(url)
        hits = r.json()["hits"]

        recipes = {}
        for hit in hits:
            recipe = hit["recipe"]
            name = recipe["label"]
            recipes[name] = {}
            recipes[name]["nutrients"] = recipe["totalNutrients"]
            recipes[name]["cautions"] = recipe["cautions"]
            recipes[name]["health_labels"] = recipe["healthLabels"]
            recipes[name]["diet_labels"] = recipe["dietLabels"]
            recipes[name]["calories"] = recipe["calories"]
            recipes[name]["ingredients"] = recipe["ingredientLines"]
            recipes[name]["url"] = recipe["url"]
        return recipes

    def search_nutrient(self, query="1 large apple", servings=1):
        ingredient = self.search_food(query)
        ingredients = [{"quantity": ingredient.get("quantity"),
                        "foodURI": ingredient["food"]["uri"],
                        "measureURI": ingredient.get("measure", {}).get(
                            "uri")}]

        url = 'https://api.edamam.com/api/food-database/nutrients?app_id=' + self.settings["nutrition_appid"] + '&app_key=' + self.settings["nutrition_appkey"]

        data = {"ingredients": ingredients, "yield": servings}
        r = requests.post(url,
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(data))
        data = r.json()
        if "error" in data:
            return None
        data["ingredients"] = data["ingredients"][0]["parsed"][0]
        data["name"] = ingredient["food"]["label"]
        LOG.debug(str(data))
        return data

    def search_food(self, query="pizza"):
        query = query.replace(" ", "%20")
        url = 'https://api.edamam.com/api/food-database/parser?ingr=' + query + \
              '&app_id=' + self.settings["nutrition_appid"] + '&app_key=' + \
               self.settings["nutrition_appkey"] + '&page=0'
        r = requests.get(url)
        return r.json()["parsed"][0]

    def pretty_nutrient(self, query="cheese"):
        n = self.search_nutrient(query)
        if n is None:
            query = "100 grams of " + query
            n = self.search_nutrient(query)
            if n is None:
                return "could not find nutrients for " + query
        if not n["ingredients"]["status"] == "MISSING_QUANTITY":
            text = str(n["ingredients"]["quantity"]) + " " + \
                   n["ingredients"]["measure"] + " " + \
                   n["ingredients"]["food"] + " has;"
        else:
            text = n["ingredients"]["food"] + " has;"

        text += "\n" + str(n["calories"]) + " calories; "

        for nutrient in n["totalNutrients"]:
            nutrient = n["totalNutrients"][nutrient]
            text += "\n" + str(nutrient["quantity"]) + " " + nutrient[
                "unit"] + " of " + nutrient["label"]
        return text


def create_skill():
    return NutrientsSkill()
