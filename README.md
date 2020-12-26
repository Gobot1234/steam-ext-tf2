# steam-ext-tf2

An extension to interact with the Team Fortress 2 Game Coordinator for 
[steam.py](https://github.com/Gobot1234/steam.py). `tf2.Client` and `tf2.Bot` are `steam.Client` and `commands.Bot` 
subclasses respectively, so whatever you did with `steam`/`ext.commands` you can do with `ext.tf2`

## Installation

To install this extension just run:

```sh
# Linux/macOS
python3 -m pip install -U "steam-ext-tf2 @ git+https://github.com/Gobot1234/steam-ext-tf2@master"
# Windows
py -m pip install -U "steam-ext-tf2 @ git+https://github.com/Gobot1234/steam-ext-tf2@master"
```

## Example Auto-crafting metal

```py
import steam
from steam.ext import tf2

bot = tf2.Bot(command_prefix="!")

@bot.event
async def on_ready() -> None:
    print("Bot is ready")

@bot.event
async def on_trade_accept(trade: steam.TradeOffer) -> None:
    refined_crafted = 0
    backpack = await bot.user.inventory(steam.TF2)
    scrap = backpack.filter_items("Scrap Metal")
    for scrap_triplet in steam.utils.chunk(scrap, 3):
        if len(scrap_triplet) != 3:
            break
        await bot.craft(scrap_triplet)
        await bot.wait_for("crafting_complete")

    backpack = await bot.user.inventory(steam.TF2)
    reclaimed = backpack.filter_items("Reclaimed Metal")
    for reclaimed_triplet in steam.utils.chunk(reclaimed, 3):
        if len(reclaimed_triplet) != 3:
            break
        await bot.craft(reclaimed_triplet)
        await bot.wait_for("crafting_complete")
        refined_crafted += 1

    print(f"Crafted {refined_crafted} Refined Metal")

bot.run("username", "password")
```
