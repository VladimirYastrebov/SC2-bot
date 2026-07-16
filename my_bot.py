import sc2
from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Race, Difficulty
from sc2.main import run_game
from sc2.player import Bot, Human, Computer
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId


class MyProtossBot(BotAI):

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
        """Run once per game step."""

        await self.distribute_workers()

        nexus = self.townhalls.ready.random
        if not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST) and not nexus.is_idle:
                if nexus.energy >= 50:
                    nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)

        if not self.townhalls:
            if self.can_afford(UnitTypeId.NEXUS) and self.start_location:
                await self.build(UnitTypeId.NEXUS, near=self.start_location)
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

        if self.can_afford(UnitTypeId.ROBOTICSFACILITY) and not self.structures(UnitTypeId.ROBOTICSFACILITY):
            await self.build(UnitTypeId.ROBOTICSFACILITY, near=self.townhalls.first)

        cybernetics = self.structures(UnitTypeId.CYBERNETICSCORE).ready
        if cybernetics and self.can_afford(UpgradeId.WARPGATERESEARCH):
            self.research(UpgradeId.WARPGATERESEARCH)

        if iteration % 50 == 0:
            await self.warp_new_units()

        for gateway in self.structures(UnitTypeId.GATEWAY).ready:
            if gateway.is_idle and self.can_afford(UnitTypeId.ZEALOT):
                gateway.train(UnitTypeId.ZEALOT)

        robotics = self.structures(UnitTypeId.ROBOTICSFACILITY)
        if robotics and self.can_afford(UnitTypeId.IMMORTAL):
            if robotics.first.is_idle:
                robotics.first.train(UnitTypeId.IMMORTAL)

        for gateway in self.structures(UnitTypeId.GATEWAY).ready:
            if gateway.is_idle and self.can_afford(UnitTypeId.SENTRY):
                zealot_count = self.units(UnitTypeId.ZEALOT).amount
                sentry_count = self.units(UnitTypeId.SENTRY).amount
                if sentry_count < zealot_count // 3:
                    gateway.train(UnitTypeId.SENTRY)

        army_size = self.units(UnitTypeId.ZEALOT).amount + self.units(UnitTypeId.IMMORTAL).amount + self.units(UnitTypeId.SENTRY).amount + self.units(UnitTypeId.STALKER).amount
        if army_size > 20 and self.enemy_start_locations:
            enemy_base = self.enemy_start_locations[0]
            for unit in self.units({UnitTypeId.ZEALOT, UnitTypeId.IMMORTAL, UnitTypeId.SENTRY, UnitTypeId.STALKER}):
                unit.attack(enemy_base)

# for 1V1
# def main():
#     run_game(
#         maps.get("PylonAIE_v4"),
#         [
#             Human(Race.Protoss),  # You as human
#             Bot(Race.Protoss, MyProtossBot()),  # Your Protoss bot
#         ],
#         realtime=True
#     )

# for bot VS AI
def main():
    run_game(
        maps.get("PylonAIE_v4"),
        [
            Bot(Race.Protoss, MyProtossBot()),  # Your Protoss bot
            Computer(Race.Zerg, Difficulty.Easy), # SC2 AI
        ],
        realtime=False
    )

if __name__ == "__main__":
    main()
