from typing import Type

from enum import Enum

import dataclasses

import random
from abc import ABC, abstractmethod
from collections import defaultdict


class DamageType(Enum):
    PURE = 1
    MELEE = 2


class Damage(ABC):
    type: DamageType

    def __init__(self, value):
        self.value = value


class PureDamage(Damage):
    """
    Pure damage ignores armor
    """

    type = DamageType.PURE


class MeleeDamage(Damage):
    """
    Just basic damage
    """

    type = DamageType.MELEE


class Toad(ABC):
    BASE_DAMAGE: int = 15
    BASE_ARMOR: int = 5
    BASE_HEALTH: int = 150

    ToadDamage = Type[Damage]

    def __init__(self):
        self._apply_class_bonuses()

        self.health = self.BASE_HEALTH
        self.is_alive = True

    @abstractmethod
    def _apply_class_bonuses(self) -> None:
        """
        Applies class bonuses, this method must be called very first in init
        """
        pass

    def get_effective_damage(self) -> Damage:
        """
        Calculates the damage dealt: a random number in the range [BASE_DAMAGE / 2, BASE_DAMAGE].
        The fractional part of the left border is discarded.

        Returns the Damage object
        """
        damage = random.randint(int(self.BASE_DAMAGE / 2), self.BASE_DAMAGE)
        return self.ToadDamage(value=damage)

    def get_effective_armor(self) -> int:
        """
        Calculates armor applied randomly in the range [0, BASE_ARMOR].

        Returns an int: effective armor (reflected damage)
        """
        return random.randint(0, self.BASE_ARMOR)

    def get_effective_armor_for_damage(self, damage: Damage) -> int:
        """
        Calculates applied armor based on damage taken.
        Works based on the get_effective_armor() method.

        Returns an int: reflected damage depending on damage type
        """
        if damage.type == DamageType.PURE:
            return 0

        return self.get_effective_armor()

    def take_damage(self, damage: Damage) -> None:
        """
        Take damage. Receives the damage object as input.
        The damage received is calculated using the formula: DAMAGE - EFFECTIVE_ARMOR_AGAINST_DAMAGE The damage
        received is subtracted from health points.
        At the end it is checked whether the toad has died
        """
        if not self.is_alive:
            return

        effective_armor = self.get_effective_armor_for_damage(damage)

        damage_taken = max(0, damage.value - effective_armor)
        self.health -= damage_taken

        self.check_death()

    def check_death(self) -> None:
        """
        Checks if the toad has died. If so, sets is_alive to False.
        Toad dies if health points are 0 or less
        """
        if self.health <= 0:
            self.is_alive = False


class AssassinToad(Toad):
    ToadDamage = PureDamage

    CRITICAL_CHANCE = 0.1

    def _apply_class_bonuses(self) -> None:
        self.BASE_HEALTH = int(self.BASE_HEALTH * 1.25)

    def get_effective_damage(self) -> Damage:
        effective_damage = super().get_effective_damage()
        if random.random() < self.CRITICAL_CHANCE:
            effective_damage.value = int(effective_damage.value * 1.5)

        return effective_damage


@dataclasses.dataclass(slots=True)
class DamageAdaptation:
    skill: float

    MAX: int = 20


class AdventurerToad(Toad):
    ToadDamage = MeleeDamage

    ADAPTATION_SKILL_GROWTH = 0.5

    def __init__(self):
        super().__init__()

        self.damage_types_adaptation = defaultdict(lambda: DamageAdaptation(skill=0))

    def _apply_class_bonuses(self) -> None:
        self.BASE_DAMAGE = int(self.BASE_DAMAGE * 1.5)

    def _increase_damage_type_adaptation(self, damage_type: DamageType) -> None:
        damage_adaptation = self.damage_types_adaptation[damage_type]

        if (
            new_skill := damage_adaptation.skill + self.ADAPTATION_SKILL_GROWTH
        ) > damage_adaptation.MAX:
            return

        damage_adaptation.skill = new_skill

    def _calculate_taken_damage(self, damage: Damage) -> int:
        damage_adaptation = self.damage_types_adaptation[damage.type].skill
        return int(damage.value * ((100 - damage_adaptation) / 100))

    def take_damage(self, damage: Damage) -> None:
        taken_damage = self._calculate_taken_damage(damage)
        damage.value = taken_damage

        super().take_damage(damage)

        self._increase_damage_type_adaptation(damage.type)


class ArtisanToad(Toad):
    ToadDamage = MeleeDamage

    def _apply_class_bonuses(self) -> None:
        self.BASE_ARMOR = int(self.BASE_ARMOR * 2)

    def get_effective_damage(self) -> Damage:
        effective_damage = super().get_effective_damage()
        effective_damage.value += self.get_effective_armor()
        return effective_damage


class ToadFactory:
    TOAD_TYPES = [AssassinToad, AdventurerToad, ArtisanToad]

    @staticmethod
    def create_random_toad():
        toad_class = random.choice(ToadFactory.TOAD_TYPES)
        return toad_class()
