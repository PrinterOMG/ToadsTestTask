import dataclasses
import itertools
from collections import defaultdict

import asyncio

from toads import Toad, ToadFactory


class Battle:
    @staticmethod
    def fight(toad1: Toad, toad2: Toad):
        """
        Simulate fight between two toads. Toads hit each other one by one until one of them dies.
        The first toad makes the first hit.

        Returns True if first toad is win.
        """
        while toad1.is_alive and toad2.is_alive:
            toad1.take_damage(toad2.get_effective_damage())

            toad2.take_damage(toad1.get_effective_damage())

        return toad1.is_alive


@dataclasses.dataclass(slots=True)
class BattleStats:
    wins: int
    total_fights: int


class ToadBattleSimulator:
    def __init__(self, fights_count, simulation_id=None):
        self.fights_count = fights_count
        self.wins = [0, 0]

        self.simulation_id = simulation_id

        self.battles_stats = defaultdict(lambda: defaultdict(BattleStats))
        self._create_battles_stats_matrix()

    def _create_battles_stats_matrix(self):
        for toad_class, opponent_class in itertools.product(
            ToadFactory.TOAD_TYPES, repeat=2
        ):
            self.battles_stats[toad_class.__name__][opponent_class.__name__] = (
                BattleStats(0, 0)
            )

    async def run_simulation(self):
        for _ in range(self.fights_count):
            toad1 = ToadFactory.create_random_toad()
            toad2 = ToadFactory.create_random_toad()
            toad1_class = toad1.__class__.__name__
            toad2_class = toad2.__class__.__name__

            # Если раскомментировать, то можно будет увидеть в консоли, что бои из симуляций 1 и 2 происходят поочередно
            # print(self.simulation_id)

            if Battle.fight(toad1, toad2):
                self.wins[0] += 1
                self.battles_stats[toad1_class][toad2_class].wins += 1
                self.battles_stats[toad1_class][toad2_class].total_fights += 1
                self.battles_stats[toad2_class][toad1_class].total_fights += 1
            else:
                self.wins[1] += 1
                self.battles_stats[toad2_class][toad1_class].wins += 1
                self.battles_stats[toad2_class][toad1_class].total_fights += 1
                self.battles_stats[toad1_class][toad2_class].total_fights += 1

            # await asyncio.sleep(0) - Нужно для переключения между событиям в цикле событий
            # Если убрать, то сначала просто выполниться первая симуляция, а затем вторая
            # Добавляя await, мы создаём момент для переключения событий и выполнение будет переключаться между
            # симуляциями после каждого боя
            # Так у нас симуляции будут выполняться "одновременно" и в использовании корутин будет смысл)
            await asyncio.sleep(0)

    def get_results(self):
        return self.wins

    def print_battles_stats(self):
        print("Matchup win statistics for the first cycle:")
        for toad_class, matchups in self.battles_stats.items():
            for opponent_class, battle_stats in matchups.items():
                print(f"{toad_class} vs {opponent_class}: ")
                win_rate = battle_stats.wins / battle_stats.total_fights * 100
                print(
                    f"{battle_stats.wins} wins | {battle_stats.total_fights} total fights | Winrate {win_rate:.2f}%"
                )
            print()
