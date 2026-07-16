from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Race, Difficulty
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.ids.unit_typeid import UnitTypeId

class MinimalBot(BotAI):
    """Minimal bot - builds Pylons and that's it"""
    
    async def on_step(self, iteration: int):
        await self.distribute_workers()
        # Build Pylons
        await self.build_smart_pylons()
        # Train Probes
        if self.can_afford(UnitTypeId.PROBE) and self.supply_left > 0:
            for nexus in self.townhalls:
                if nexus.is_idle:
                    nexus.train(UnitTypeId.PROBE)

    async def build_smart_pylons(self):
        """Build pylons based on supply calculations, not spam!"""
        
        # 1. Get current state
        current_supply_used = self.supply_used
        current_supply_cap = self.supply_cap
        
        # 2. Count buildings under construction
        building_pylons = self.already_pending(UnitTypeId.PYLON)
        building_nexuses = self.already_pending(UnitTypeId.NEXUS)
        
        # 3. Supply constants
        SUPPLY_PER_PYLON = 8
        SUPPLY_PER_NEXUS = 15
        SUPPLY_BUFFER = 8
        
        # 4. Calculate future supply
        future_supply_cap = (
            current_supply_cap 
            + (building_pylons * SUPPLY_PER_PYLON) 
            + (building_nexuses * SUPPLY_PER_NEXUS)
        )
        
        # 5. Calculate supply left after builds
        supply_left_after_builds = future_supply_cap - current_supply_used
        
        # 6. Check if we need a pylon
        need_pylon = supply_left_after_builds < SUPPLY_BUFFER

        print(current_supply_used, "used")
        print(current_supply_cap, "all")
        print(building_pylons, "pylones in progress")
        print(building_nexuses, "nexuses in progress")
        print(future_supply_cap, "future all suply")
        print(supply_left_after_builds, "future available supply")
        print(need_pylon, "need pylon")
        
        # 7. Build if needed
        if (need_pylon) and self.can_afford(UnitTypeId.PYLON):
            if not self.structures(UnitTypeId.PYLON).not_ready:
                await self.build(UnitTypeId.PYLON, near=self.townhalls.first)

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