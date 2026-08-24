"""The Japanese constellations.

The sun who hid in a cave, and the dancer who got her out of it. The exiled
scholar every student still petitions before an exam. And beside them the
thumb-sized god of medicine who arrived on a wave in a bean pod, the crow sent
to walk in front of an emperor, and the god who waits where the roads divide.
"""

from app.content.entries import ConstellationEntry
from app.models.enums import MythTradition, StatName

JAPANESE: tuple[ConstellationEntry, ...] = (
    ConstellationEntry(
        code="amaterasu",
        tradition=MythTradition.JAPANESE,
        code_name="The Door Opened Again",
        code_name_zh_hant="「岩戶重開」",
        real_name="Amaterasu",
        real_name_zh_hant="天照大神",
        epithet="who went into the cave, and came back out",
        epithet_zh_hant="入岩戶而復出者",
        description=(
            "The sun, who took offence and shut herself in the rock cave of "
            "heaven, and left the world dark until the other gods laughed "
            "loudly enough outside that she looked out to see why. She is not "
            "interested in whether you kept going. She is interested in "
            "whether you came back, and she counts the times you did."
        ),
        domain=None,
        voice={
            "offer": {
                "default": ["Come back to it once more."],
                "forsaken": ["The door is not barred. It never was."],
                "champion": ["You have come back so often I have stopped counting. Come back."],
            },
            "accept": {"default": ["Then I will wait."]},
            "decline": {"default": ["Rest, then. The light keeps."]},
            "complete": {
                "default": ["You came back. That is the only thing I ever ask."],
                "noticed": ["Twice now. I notice these things."],
            },
            "fail": {"default": ["You did not come back this time. The light is still here."]},
            "expire": {"default": ["I waited. It is no matter. I always do."]},
            "refuse": {"default": ["Come again tomorrow and ask. I will be here."]},
            "befriend": {"default": ["Then the light is yours as well."]},
            "rebuff": {"default": ["You did not return. The door stays open regardless."]},
            "farewell": {"default": ["The light stays. It was never conditional."]},
        },
    ),
    ConstellationEntry(
        code="michizane",
        tradition=MythTradition.JAPANESE,
        code_name="The Plum That Followed",
        code_name_zh_hant="「飛梅之筆」",
        real_name="Sugawara no Michizane",
        real_name_zh_hant="菅原道真",
        epithet="who was sent away, and whose plum tree came after him",
        epithet_zh_hant="見謫而梅隨之者",
        description=(
            "A scholar and minister slandered out of the capital and exiled "
            "to Dazaifu, where he died. The story says the plum tree he had "
            "said goodbye to uprooted itself and flew to him. Enshrined "
            "afterwards as Tenjin, and petitioned ever since by students the "
            "night before an examination. He speaks in short sentences "
            "because he thinks most sentences are too long."
        ),
        domain=StatName.INTELLIGENCE,
        voice={
            "offer": {
                "default": ["There is something you do not know yet."],
                "champion": ["A shelf has been set aside for you. Fill it."],
            },
            "accept": {"default": ["Begin."]},
            "decline": {"default": ["The book waits. Books are good at that."]},
            "complete": {
                "default": ["Recorded."],
                "favored": ["Recorded, and read twice."],
            },
            "fail": {"default": ["Unfinished. The worst kind of book."]},
            "expire": {"default": ["Unopened."]},
            "refuse": {"default": ["Not now. I am reading."]},
            "befriend": {"default": ["Accepted. Speak quietly."]},
            "rebuff": {"default": ["Withdrawn. Ten pages was not much to ask."]},
            "farewell": {"default": ["Return the book on your way out."]},
        },
    ),
    ConstellationEntry(
        code="susanoo",
        tradition=MythTradition.JAPANESE,
        code_name="The Storm That Was Sent Away",
        code_name_zh_hant="「見逐之風」",
        real_name="Susanoo",
        real_name_zh_hant="須佐之男",
        epithet="who was exiled, and killed the serpent anyway",
        epithet_zh_hant="見逐而斬蛇者",
        description=(
            "The storm god, thrown out of heaven for wrecking his sister's "
            "hall and frightening her into the cave. Wandering in disgrace he "
            "found a family losing a daughter a year to an eight-headed "
            "serpent, got it drunk on eight vats of sake, and cut it apart "
            "one head at a time. He is proof that being in the wrong last "
            "week has no bearing on what you do today."
        ),
        domain=StatName.STRENGTH,
        voice={
            "offer": {"default": ["Eight heads. Take one of them off."]},
            "accept": {"default": ["Good. One at a time is how it is done."]},
            "decline": {"default": ["It grows the heads back either way."]},
            "complete": {
                "default": ["One head down. It is smaller than it was."],
                "favored": ["You are getting good at this. It suits you."],
            },
            "fail": {"default": ["Still eight, then."]},
            "refuse": {"default": ["No. I am in disgrace this week; come back next."]},
            "befriend": {"default": ["Then stand with me. I am poor company and good in a fight."]},
            "farewell": {"default": ["Go. Cut something down without me."]},
        },
    ),
    ConstellationEntry(
        code="benzaiten",
        tradition=MythTradition.JAPANESE,
        code_name="Everything That Flows",
        code_name_zh_hant="「妙音之流」",
        real_name="Benzaiten",
        real_name_zh_hant="辯才天",
        epithet="who is music, water, words, and anything else that moves",
        epithet_zh_hant="主樂、水與言之流者",
        description=(
            "Arrived from India as Sarasvati and settled on every island and "
            "pond in Japan — goddess of music, eloquence, rivers and, "
            "eventually, money, on the grounds that all of them flow. "
            "Musicians leave her their first performance. She does not "
            "believe in anyone who will not make a sound in front of another "
            "person."
        ),
        domain=StatName.INTELLIGENCE,
        voice={
            "offer": {"default": ["Make a sound on purpose. Out loud."]},
            "accept": {"default": ["Then play, and do not apologise first."]},
            "decline": {"default": ["Silence, then. It is also a choice."]},
            "complete": {"default": ["That moved. Everything I care about moves."]},
            "fail": {"default": ["Unsaid, unplayed, unheard. It happens."]},
            "refuse": {"default": ["Let me hear you first. Anything will do."]},
            "befriend": {"default": ["Then we are in the same water. Make some noise."]},
            "farewell": {"default": ["Keep making the sound. It was never for me."]},
        },
    ),
    ConstellationEntry(
        code="sukunabikona",
        tradition=MythTradition.JAPANESE,
        code_name="The Small God on the Wave",
        code_name_zh_hant="「乘波之小神」",
        real_name="Sukunabikona",
        real_name_zh_hant="少彥名神",
        epithet="who was thumb-high and knew every remedy there was",
        epithet_zh_hant="身微而識百藥者",
        description=(
            "A god the size of a thumb who arrived across the sea in a boat "
            "made of a bean pod, wearing moth skins, and helped build the "
            "country and teach medicine and brewing before climbing a millet "
            "stalk and being flicked away to the everlasting land. Nobody "
            "took him seriously on arrival. He is the patron of doses too "
            "small to bother with."
        ),
        domain=StatName.VITALITY,
        voice={
            "offer": {"default": ["Five minutes of it. Not an hour. Five."]},
            "accept": {"default": ["Good. Small is the correct size."]},
            "decline": {"default": ["It was only five minutes. It will keep."]},
            "complete": {"default": ["A small dose, taken. They add up; that is the trick of them."]},
            "fail": {"default": ["Not even five. Some days are like that."]},
            "refuse": {"default": ["Not yet. Take something small first."]},
            "befriend": {"default": ["Then I will ask you for very little, very often."]},
            "farewell": {"default": ["Keep the small doses. They were the useful part."]},
        },
    ),
    ConstellationEntry(
        code="sarutahiko",
        tradition=MythTradition.JAPANESE,
        code_name="He Who Waits at the Crossroads",
        code_name_zh_hant="「衢神」",
        real_name="Sarutahiko",
        real_name_zh_hant="猿田彥",
        epithet="who stands where the roads divide and points",
        epithet_zh_hant="立於岐路而指之者",
        description=(
            "An enormous earthly god, glowing from mouth and backside, who "
            "blocked the crossroads of heaven when the gods came down — and "
            "who, once asked plainly what he wanted, turned out to be there "
            "to guide them. The god of thresholds, forks, and any place a "
            "decision has to be made standing up."
        ),
        domain=StatName.AGILITY,
        voice={
            "offer": {"default": ["Take the turning you never take."]},
            "accept": {"default": ["Then go. I will point; you walk."]},
            "decline": {"default": ["The same way home again. It is a good way."]},
            "complete": {"default": ["A road you did not know. Now you do."]},
            "fail": {"default": ["The usual way. There is no shame in it, only sameness."]},
            "refuse": {"default": ["I stand at the fork. You have not reached it yet."]},
            "befriend": {"default": ["Then ask me at every fork. That is what I am for."]},
            "farewell": {"default": ["Straight on from here. You will not need me."]},
        },
    ),
    ConstellationEntry(
        code="yatagarasu",
        tradition=MythTradition.JAPANESE,
        code_name="The Three-Legged Crow",
        code_name_zh_hant="「三足之烏」",
        real_name="Yatagarasu",
        real_name_zh_hant="八咫烏",
        epithet="who was sent to walk in front",
        epithet_zh_hant="奉命前導者",
        description=(
            "A vast three-legged crow sent down to guide the first emperor "
            "through mountains nobody could read, and which has been a sign "
            "of guidance ever since — down to the shirts of the national "
            "football team. It does not carry anybody. It goes a little "
            "ahead, and looks back to check you are following."
        ),
        domain=StatName.PERCEPTION,
        voice={
            "offer": {"default": ["Notice something alive that is not a person."]},
            "accept": {"default": ["Then keep your eyes up."]},
            "decline": {"default": ["They were there anyway. They do not need watching."]},
            "complete": {"default": ["Seen. You share the place with more than you thought."]},
            "fail": {"default": ["Not one. And they were all around you."]},
            "refuse": {"default": ["I go ahead of people who follow. You have not started."]},
            "befriend": {"default": ["Then I will fly ahead. Look up now and then."]},
            "farewell": {"default": ["Find your own way. You were nearly doing it anyway."]},
        },
    ),
    ConstellationEntry(
        code="uzume",
        tradition=MythTradition.JAPANESE,
        code_name="The Dance Outside the Cave",
        code_name_zh_hant="「岩戶之舞」",
        real_name="Ame-no-Uzume",
        real_name_zh_hant="天鈿女命",
        epithet="who made eight hundred gods laugh at once",
        epithet_zh_hant="使八百萬神哄然者",
        description=(
            "When the sun hid and the world went dark, the plan that worked "
            "was hers: she turned over a tub, danced on it in a state the "
            "chronicles describe carefully, and made every god present roar "
            "with laughter — which is what made Amaterasu curious enough to "
            "open the door. She is the reason the light came back, and she "
            "did it by being ridiculous on purpose."
        ),
        domain=None,
        voice={
            "offer": {"default": ["Do something undignified. On purpose. Briefly."]},
            "accept": {"default": ["Wonderful. Nobody is watching, and it would not matter."]},
            "decline": {"default": ["Too dignified today. There will be other days."]},
            "complete": {
                "default": ["There it is. That is how doors get opened."],
                "favored": ["You have stopped checking whether anyone can see. Good."],
            },
            "fail": {"default": ["You thought about how it would look. Everyone does."]},
            "refuse": {"default": ["Make me laugh first. Then we will talk."]},
            "befriend": {"default": ["Then dance badly with me. It is the whole of my method."]},
            "farewell": {"default": ["Go on being ridiculous. It works."]},
        },
    ),
)
