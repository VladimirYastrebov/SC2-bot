from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Race, Difficulty
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2

class TestWarpBot(BotAI):
    """Bot to test Warp Gate functionality."""

    async def warp_new_units(self):
        for warpgate in self.structures(UnitTypeId.WARPGATE).ready:
            abilities = await self.get_available_abilities([warpgate])
            # all the units have the same cooldown anyway so let's just look at ZEALOT
            if AbilityId.WARPGATETRAIN_STALKER in abilities[0]:
                pylon = self.structures(UnitTypeId.PYLON).ready.random
                pos = pylon.position.to2.random_on_distance(4)
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
                if placement is None:
                    # return ActionResult.CantFindPlacementLocation
                    print("can't place")
                    return
                warpgate.warp_in(UnitTypeId.STALKER, placement)

    async def on_step(self, iteration: int):
        await self.distribute_workers()

        if not self.townhalls:
            return

        if self.supply_left < 5 and self.can_afford(UnitTypeId.PYLON):
            await self.build(UnitTypeId.PYLON, near=self.townhalls.first)

        if self.can_afford(UnitTypeId.PROBE) and self.supply_left > 0:
            if self.units(UnitTypeId.PROBE).amount < 20:
                for nexus in self.townhalls:
                    if nexus.is_idle:
                        nexus.train(UnitTypeId.PROBE)

        if self.can_afford(UnitTypeId.GATEWAY):
            total_gateways = self.structures(UnitTypeId.GATEWAY).amount + self.structures(UnitTypeId.WARPGATE).amount
            if total_gateways < 3:
                await self.build(UnitTypeId.GATEWAY, near=self.townhalls.first)

        if self.structures(UnitTypeId.ASSIMILATOR).amount < 2:
            for geyser in self.vespene_geyser:
                if self.townhalls.first.distance_to(geyser) < 20:
                    assimilator_on_geyser = self.structures(UnitTypeId.ASSIMILATOR).closer_than(5, geyser)
                    if not assimilator_on_geyser:
                        await self.build(UnitTypeId.ASSIMILATOR, near=geyser)
                        break

        if self.can_afford(UnitTypeId.CYBERNETICSCORE) and not self.structures(UnitTypeId.CYBERNETICSCORE):
            await self.build(UnitTypeId.CYBERNETICSCORE, near=self.townhalls.first)

        cybernetics = self.structures(UnitTypeId.CYBERNETICSCORE).ready
        if cybernetics and self.can_afford(UpgradeId.WARPGATERESEARCH):
            self.research(UpgradeId.WARPGATERESEARCH)

        if iteration % 50 == 0:
            await self.warp_new_units()

        if not self.structures(UnitTypeId.WARPGATE).ready:
            for gateway in self.structures(UnitTypeId.GATEWAY).ready:
                if gateway.is_idle and self.can_afford(UnitTypeId.ZEALOT):
                    gateway.train(UnitTypeId.ZEALOT)

    # async def try_warp(self):
    #     """Attempt to warp in a Zealot."""
    #     warpgates = [gate for gate in self.structures(UnitTypeId.WARPGATE).ready if gate.is_idle]
    #     pylons = [pylon for pylon in self.structures(UnitTypeId.PYLON).ready if pylon.is_ready]

    #     if not warpgates or not pylons:
    #         return
    #     if not self.can_afford(UnitTypeId.ZEALOT) or self.supply_left <= 0:
    #         return

    #     for pylon in pylons:
    #         target_position = pylon.position
    #         if self.can_place(UnitTypeId.ZEALOT, target_position):
    #             warpgates[0].warp_in(UnitTypeId.ZEALOT, target_position)
    #             return

def main():
    run_game(
        maps.get("PylonAIE_v4"),
        [
            Bot(Race.Protoss, TestWarpBot()),
            Computer(Race.Zerg, Difficulty.Easy)
        ],
        realtime=False
    )

if __name__ == "__main__":
    main()