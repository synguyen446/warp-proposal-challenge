import pandas

PRICE_CONFIG = pandas.read_csv(
    r"data/pricing_config.csv"
)
PRICE_CONFIG_DICT = dict(
    zip(
        PRICE_CONFIG["key"].tolist(),
        PRICE_CONFIG["value"].tolist(),
    )
)
RATE_CARD_DF = pandas.read_csv(r"data/rate_card.csv")
SERVICE_LEVELS_DF = pandas.read_csv(
    r"data/service_levels.csv"
)
ACCESSORIALS_RATE_DF = pandas.read_csv(
    r"data/accessorials.csv"
)
VOLUME_TIERS_DF = pandas.read_csv(
    r"data/volume_tiers.csv"
)
