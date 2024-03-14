from src.bot import DiscordClient

from src.settings import settings

def main() -> None:
    discord_bot = DiscordClient()

    discord_bot.startup(
        token=settings.discord_token,
    )

if __name__ == "__main__":
    main()
