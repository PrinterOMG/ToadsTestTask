import asyncio

from battles import ToadBattleSimulator


async def main():
    fights_count = 100
    simulator1 = ToadBattleSimulator(fights_count, simulation_id=1)
    simulator2 = ToadBattleSimulator(fights_count, simulation_id=2)

    await asyncio.gather(simulator1.run_simulation(), simulator2.run_simulation())

    wins1 = simulator1.get_results()
    wins2 = simulator2.get_results()

    print(
        f"Results of the first cycle: Toad1 wins = {wins1[0]}, Toad2 wins = {wins1[1]}"
    )
    print(
        f"Results of the second cycle: Toad1 wins = {wins2[0]}, Toad2 wins = {wins2[1]}"
    )

    print("\n---\n")

    simulator1.print_battles_stats()

    print("---\n")

    simulator2.print_battles_stats()


if __name__ == "__main__":
    asyncio.run(main())
