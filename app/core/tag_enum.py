"""
Webtoon Tag Enum - All available tags for series
Includes both general tags and webtoon-specific tags
"""
from enum import Enum


class WebtoonTag(str, Enum):
    """All available webtoon tags"""
    
    # === GENRE TAGS ===
    ACTION = "action"
    ADVENTURE = "adventure"
    COMEDY = "comedy"
    DRAMA = "drama"
    FANTASY = "fantasy"
    HORROR = "horror"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    SCI_FI = "sci-fi"
    SLICE_OF_LIFE = "slice-of-life"
    SPORTS = "sports"
    SUPERNATURAL = "supernatural"
    THRILLER = "thriller"
    WESTERN = "western"
    
    # === THEME TAGS ===
    SCHOOL = "school"
    WORKPLACE = "workplace"
    HISTORICAL = "historical"
    MODERN = "modern"
    FUTURISTIC = "futuristic"
    MEDIEVAL = "medieval"
    URBAN = "urban"
    RURAL = "rural"
    
    # === CHARACTER TAGS ===
    STRONG_FEMALE_LEAD = "strong-female-lead"
    STRONG_MALE_LEAD = "strong-male-lead"
    VILLAIN_LEAD = "villain-lead"
    ANTI_HERO = "anti-hero"
    OP_MAIN_CHARACTER = "op-main-character"
    WEAK_TO_STRONG = "weak-to-strong"
    REINCARNATION = "reincarnation"
    TRANSMIGRATION = "transmigration"
    TIME_TRAVEL = "time-travel"
    
    # === WEBTOON-SPECIFIC TAGS (Very Common) ===
    SYSTEM = "system"  # System novels/manhwa
    RETURN = "return"  # Return/regression stories
    REBIRTH = "rebirth"  # Rebirth stories
    REGRESSION = "regression"  # Regression stories
    TRANSMIGRATION_NOVEL = "transmigration-novel"  # Transmigration into novel
    VILLAINESS = "villainess"  # Villainess stories
    DUKE_OF_THE_NORTH = "duke-of-the-north"  # Common trope
    MAGIC = "magic"
    MANA = "mana"
    CULTIVATION = "cultivation"
    MARTIAL_ARTS = "martial-arts"
    LEVELING = "leveling"
    GAME_ELEMENTS = "game-elements"
    STATUS_WINDOW = "status-window"
    SKILLS = "skills"
    EVOLUTION = "evolution"
    
    # === RELATIONSHIP TAGS ===
    HAREM = "harem"
    REVERSE_HAREM = "reverse-harem"
    LOVE_TRIANGLE = "love-triangle"
    POLYGAMY = "polygamy"
    YAOI = "yaoi"
    YURI = "yuri"
    BL = "bl"  # Boys' Love
    GL = "gl"  # Girls' Love
    SHOUJO = "shoujo"
    SHOUNEN = "shounen"
    SEINEN = "seinen"
    JOSEI = "josei"
    
    # === STORY TAGS ===
    REVENGE = "revenge"
    REDEMPTION = "redemption"
    BETRAYAL = "betrayal"
    FRIENDSHIP = "friendship"
    FAMILY = "family"
    RIVALRY = "rivalry"
    COMPETITION = "competition"
    TOURNAMENT = "tournament"
    ACADEMY = "academy"
    GUILD = "guild"
    ADVENTURER = "adventurer"
    MERCHANT = "merchant"
    NOBLE = "noble"
    ROYALTY = "royalty"
    COMMONER = "commoner"
    
    # === MOOD/STYLE TAGS ===
    DARK = "dark"
    LIGHTHEARTED = "lighthearted"
    MATURE = "mature"
    COMEDIC = "comedic"
    SERIOUS = "serious"
    TRAGIC = "tragic"
    HEARTWARMING = "heartwarming"
    INTENSE = "intense"
    SLOW_BURN = "slow-burn"
    FAST_PACED = "fast-paced"
    
    # === CONTENT TAGS ===
    GORE = "gore"
    VIOLENCE = "violence"
    SEXUAL_CONTENT = "sexual-content"
    MATURE_THEMES = "mature-themes"
    FLUFF = "fluff"
    ANGST = "angst"
    FLUFFY = "fluffy"
    WHOLESOME = "wholesome"
    
    # === ART/STYLE TAGS ===
    COLORED = "colored"
    BLACK_AND_WHITE = "black-and-white"
    FULL_COLOR = "full-color"
    MANGA_STYLE = "manga-style"
    MANHWA_STYLE = "manhwa-style"
    MANHUA_STYLE = "manhua-style"
    
    # === ADDITIONAL WEBTOON TAGS ===
    DUNGEON = "dungeon"
    TOWER = "tower"
    GATE = "gate"
    PORTAL = "portal"
    APOCALYPSE = "apocalypse"
    ZOMBIE = "zombie"
    MONSTER = "monster"
    DEMON = "demon"
    ANGEL = "angel"
    GOD = "god"
    DRAGON = "dragon"
    BEAST = "beast"
    SPIRIT = "spirit"
    GHOST = "ghost"
    
    # === MODERN WEBTOON TAGS ===
    CEO = "ceo"
    CONTRACT_MARRIAGE = "contract-marriage"
    ARRANGED_MARRIAGE = "arranged-marriage"
    CHILDHOOD_FRIENDS = "childhood-friends"
    ENEMIES_TO_LOVERS = "enemies-to-lovers"
    FRIENDS_TO_LOVERS = "friends-to-lovers"
    SECOND_CHANCE = "second-chance"
    SECRET_IDENTITY = "secret-identity"
    HIDDEN_IDENTITY = "hidden-identity"
    DISGUISE = "disguise"
    CROSSDRESSING = "crossdressing"
    
    # === POWER/ABILITY TAGS ===
    OVERPOWERED = "overpowered"
    UNDERDOG = "underdog"
    GENIUS = "genius"
    TALENTED = "talented"
    AVERAGE = "average"
    CHEAT = "cheat"
    CHEAT_SKILL = "cheat-skill"
    UNIQUE_SKILL = "unique-skill"
    RARE_SKILL = "rare-skill"
    LEGENDARY = "legendary"
    
    # === WORLD TAGS ===
    ALTERNATE_WORLD = "alternate-world"
    PARALLEL_WORLD = "parallel-world"
    ANOTHER_WORLD = "another-world"
    ISEKAI = "isekai"
    VIRTUAL_REALITY = "virtual-reality"
    GAME_WORLD = "game-world"
    NOVEL_WORLD = "novel-world"
    MANGA_WORLD = "manga-world"
    
    # === ADDITIONAL POPULAR TAGS ===
    FOOD = "food"
    COOKING = "cooking"
    MUSIC = "music"
    ART = "art"
    FASHION = "fashion"
    BUSINESS = "business"
    POLITICS = "politics"
    WAR = "war"
    PEACE = "peace"
    SURVIVAL = "survival"
    EXPLORATION = "exploration"
    TREASURE_HUNT = "treasure-hunt"
    MYSTERY_SOLVING = "mystery-solving"
    DETECTIVE = "detective"
    POLICE = "police"
    CRIMINAL = "criminal"
    MAFIA = "mafia"
    GANG = "gang"
    
    @classmethod
    def get_all_tags(cls) -> list:
        """Get all tag values as a list"""
        return [tag.value for tag in cls]
    
    @classmethod
    def get_genre_tags(cls) -> list:
        """Get only genre tags"""
        genre_tags = [
            cls.ACTION, cls.ADVENTURE, cls.COMEDY, cls.DRAMA, cls.FANTASY,
            cls.HORROR, cls.MYSTERY, cls.ROMANCE, cls.SCI_FI, cls.SLICE_OF_LIFE,
            cls.SPORTS, cls.SUPERNATURAL, cls.THRILLER, cls.WESTERN
        ]
        return [tag.value for tag in genre_tags]
    
    @classmethod
    def get_webtoon_specific_tags(cls) -> list:
        """Get webtoon-specific tags (system, return, etc.)"""
        webtoon_tags = [
            cls.SYSTEM, cls.RETURN, cls.REBIRTH, cls.REGRESSION,
            cls.TRANSMIGRATION_NOVEL, cls.VILLAINESS, cls.DUKE_OF_THE_NORTH,
            cls.MAGIC, cls.MANA, cls.CULTIVATION, cls.MARTIAL_ARTS,
            cls.LEVELING, cls.GAME_ELEMENTS, cls.STATUS_WINDOW, cls.SKILLS,
            cls.EVOLUTION, cls.DUNGEON, cls.TOWER, cls.GATE, cls.PORTAL,
            cls.ISEKAI, cls.ALTERNATE_WORLD, cls.PARALLEL_WORLD
        ]
        return [tag.value for tag in webtoon_tags]
    
    @classmethod
    def is_valid_tag(cls, tag_name: str) -> bool:
        """Check if a tag name is valid"""
        try:
            cls(tag_name.lower().replace(' ', '-'))
            return True
        except ValueError:
            return False
    
    @classmethod
    def normalize_tag(cls, tag_name: str) -> Optional[str]:
        """Normalize tag name to enum value"""
        if not tag_name:
            return None
        
        # Normalize: lowercase, replace spaces with hyphens
        normalized = tag_name.lower().strip().replace(' ', '-')
        
        try:
            return cls(normalized).value
        except ValueError:
            # Try fuzzy match
            for tag in cls:
                if normalized in tag.value or tag.value in normalized:
                    return tag.value
            return None

