from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Race, Difficulty
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId


class MinimalBot(BotAI):
    """Minimal bot - builds Pylons and that's it"""

    async def on_step(self, iteration: int):
        await self.distribute_workers()
        # Build Pylons
        if self.can_afford(UnitTypeId.PYLON):
            await self.build(UnitTypeId.PYLON, near=self.start_location)

        if self.can_afford(UnitTypeId.PROBE) and self.supply_left > 0:
            if self.units(UnitTypeId.PROBE).amount < 20:
                for nexus in self.townhalls:
                    if nexus.is_idle:
                        nexus.train(UnitTypeId.PROBE)

        nexus = self.townhalls.ready.random
        if not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST) and not nexus.is_idle:
                if nexus.energy >= 50:
                    nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)

def main():
    run_game(
        maps.get("PylonAIE_v4"),
        [
            Bot(Race.Protoss, MinimalBot()),
            Computer(Race.Zerg, Difficulty.Easy)
        ],
        realtime=False
    )


if __name__ == "__main__":
    main()
