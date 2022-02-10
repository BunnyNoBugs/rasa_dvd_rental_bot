# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

FILMS_DB = {
    'action': ['film1', 'film2'],
    'comedy': ['film1', 'film2'],
    'drama': ['film1', 'film2'],
    'horror': ['film1', 'film2'],
    'thriller': ['film1', 'film2'],
    'romance': ['film1', 'film2']
}

MOOD_GENRE_RECOMMENDATIONS = {
    'bored': ['action', 'thriller'],
    'great': ['thriller', 'comedy'],
    'unhappy': ['comedy'],
    'lonely': ['romance']
}


class AskForPreferredGenreAction(Action):
    def name(self) -> Text:
        return "action_ask_preferred_genre"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        filtered_genres = [g for g in FILMS_DB if g not in tracker.get_slot('avoided_genres')]
        dispatcher.utter_message(
            text=f"What film genre do you prefer?",
            buttons=[{"title": g, "payload": g} for g in filtered_genres],
        )
        return []


class AskForFilmNameAction(Action):
    def name(self) -> Text:
        return "action_ask_film_name"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(
            text=f"What film would you like to rent?",
            buttons=[{"title": f, "payload": f} for f in FILMS_DB[tracker.get_slot('preferred_genre')]],
        )
        return []


class AskForRentalPeriod(Action):
    def name(self) -> Text:
        return "action_ask_rental_period"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(text=f"For how many days you would like to rent?")
        return []


class ValidateFilmRentalForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_film_rental_form"

    def validate_preferred_genre(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `preferred_genre` value."""

        if slot_value not in FILMS_DB:
            dispatcher.utter_message(text=f"Please choose a genre from our list.")
            return {"preferred_genre": None}
        dispatcher.utter_message(text=f"OK! Your preferred genre is {slot_value}")
        return {"preferred_genre": slot_value}

    def validate_film_name(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `film_name` value."""

        if slot_value not in FILMS_DB[tracker.get_slot('preferred_genre')]:
            dispatcher.utter_message(
                text='Please choose a film from our list.'
            )
            return {"film_name": None}
        if not slot_value:
            dispatcher.utter_message(
                text='Please choose a film from our list.'
            )
            return {"film_name": None}
        dispatcher.utter_message(text=f"OK! You would like to rent \"{slot_value}\".")
        return {"film_name": slot_value}

    def validate_rental_period(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `rental_period` value."""

        if 1 <= int(slot_value) <= 14:
            dispatcher.utter_message(text=f'OK! You would like to rent for {slot_value} days.')
            return {'rental_period': slot_value}
        else:
            dispatcher.utter_message(text='Please choose a number of days between 1 and 14.')
            return {'rental_period': None}


class RecommendGenreAction(Action):
    def name(self) -> Text:
        return "action_recommend_genre"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        recommended_genre = MOOD_GENRE_RECOMMENDATIONS[tracker.get_slot('current_mood')][0]
        dispatcher.utter_message(text=f'Do you feel like watching a {recommended_genre} film?')
        return [SlotSet('recommended_genre', recommended_genre)]


class SetPreferredGenreAction(Action):
    def name(self) -> Text:
        return "action_set_preferred_genre"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        recommended_genre = tracker.get_slot('recommended_genre')
        dispatcher.utter_message(text=f'OK, I will remember that you prefer {recommended_genre}')
        return [SlotSet('recommended_genre', None), SlotSet('preferred_genre', recommended_genre)]


class AddAvoidedGenreAction(Action):
    def name(self) -> Text:
        return "action_add_avoided_genre"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        recommended_genre = tracker.get_slot('recommended_genre')
        avoided_genres = tracker.get_slot('avoided_genres')
        if not avoided_genres:
            avoided_genres = []
        avoided_genres.append(recommended_genre)
        dispatcher.utter_message(text=f'OK, I will remember that you don\'t like {recommended_genre}')
        return [SlotSet('avoided_genres', avoided_genres)]
