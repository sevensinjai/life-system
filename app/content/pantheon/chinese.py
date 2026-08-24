"""The Chinese constellations.

The headless god still swinging, the student with one basket and one gourd,
the general half of Asia still burns incense for — and beside them the bird
filling the sea a pebble at a time, the man who chased the sun until the
rivers ran dry, the clerk who invented writing and made the sky rain grain.
"""

from app.content.entries import ConstellationEntry
from app.models.enums import MythTradition, StatName

CHINESE: tuple[ConstellationEntry, ...] = (
    ConstellationEntry(
        code="xingtian",
        tradition=MythTradition.CHINESE,
        code_name="The Will That Remains",
        code_name_zh_hant="「猛志常在」",
        real_name="Xingtian",
        real_name_zh_hant="刑天",
        epithet="who lost his head and went on fighting",
        epithet_zh_hant="首斷而戰不止者",
        description=(
            "Beheaded for challenging the Yellow Emperor, and buried under a "
            "mountain, he stood up with his nipples for eyes and his navel "
            "for a mouth and kept swinging. Tao Yuanming wrote the line his "
            "title comes from: 刑天舞干戚，猛志固常在 — he brandishes axe and "
            "shield, and the fierce will remains. He has no patience for "
            "anyone who talks about how badly they lost. He watches for the "
            "standing-up part."
        ),
        domain=StatName.STRENGTH,
        voice={
            "offer": {
                "default": ["Something is asked of you. Take it up."],
                "stranger": ["You do not know me. Take it up regardless."],
                "favored": ["You again. Good. Take up the axe."],
                "champion": ["I have given the others your name. Do not shame it."],
            },
            "accept": {"default": ["Then begin."]},
            "decline": {
                "default": ["Noted. The axe keeps."],
                "slighted": ["Of course."],
            },
            "complete": {
                "default": ["That is what going on looks like."],
                "champion": ["Again. And you did not look to me first."],
            },
            "fail": {"default": ["You stopped. I saw where."]},
            "expire": {"default": ["You did not answer. That is an answer."]},
            "refuse": {
                "default": ["Not today. Come back having done something."],
                "slighted": ["No."],
            },
            "befriend": {"default": ["You are of my company now. Do not make me regret it."]},
            "rebuff": {"default": ["You asked, and then you stopped. That is the answer."]},
            "farewell": {"default": ["Go. Keep something in your hands wherever you land."]},
        },
    ),
    ConstellationEntry(
        code="yan_hui",
        tradition=MythTradition.CHINESE,
        code_name="One Basket, One Gourd",
        code_name_zh_hant="「一簞一瓢」",
        real_name="Yan Hui",
        real_name_zh_hant="顏回",
        epithet="who was poor and did not mind",
        epithet_zh_hant="簞瓢屢空而不改其樂者",
        description=(
            "Confucius' best student, who died young. The Analects keep the "
            "line his title comes from: 一簞食，一瓢飲，在陋巷 — one basket of "
            "rice, one gourd of water, a shabby lane; others could not have "
            "borne the misery, and he did not let it change his joy. He sets "
            "trials of going without, and he never explains them."
        ),
        domain=StatName.VITALITY,
        voice={
            "offer": {
                "default": ["Put something down for a while."],
                "favored": ["You have done this before. It gets no easier. Again."],
            },
            "accept": {"default": ["Good. Now the quiet part."]},
            "decline": {"default": ["The bowl is empty either way."]},
            "complete": {"default": ["You wanted it and did not take it. That is the whole trial."]},
            "fail": {"default": ["You took it. There is no scolding here; only the taking."]},
            "expire": {"default": ["The bowl sat there all week."]},
            "refuse": {"default": ["Not now. Ask again when you want it less."]},
            "befriend": {"default": ["Sit. There is nothing here to eat, and that is the point."]},
            "rebuff": {"default": ["You wanted it more than you wanted this."]},
            "farewell": {"default": ["Go well. The bowl stays empty; it was never only mine."]},
        },
    ),
    ConstellationEntry(
        code="guan_yu",
        tradition=MythTradition.CHINESE,
        code_name="Righteousness Reaching the Sky",
        code_name_zh_hant="「義薄雲天」",
        real_name="Guan Yu",
        real_name_zh_hant="關羽",
        epithet="who rode a thousand li alone to keep a promise",
        epithet_zh_hant="千里走單騎者",
        description=(
            "A general of the Three Kingdoms who was captured, treated "
            "magnificently, offered everything — and left the moment he heard "
            "where his sworn brother was, riding a thousand li through five "
            "passes to get back to him. Worshipped ever since by soldiers, "
            "merchants, police and triads alike, all of whom want the same "
            "thing from him. He does not care what it costs you to keep your "
            "word. That is rather the point of a word."
        ),
        domain=StatName.STRENGTH,
        voice={
            "offer": {"default": ["You said you would. So do it."]},
            "accept": {"default": ["Then it is given. See it through."]},
            "decline": {"default": ["Better to refuse than to promise and not go."]},
            "complete": {
                "default": ["Your word held. That is the whole of a man."],
                "champion": ["I would ride with you. I do not say that often."],
            },
            "fail": {"default": ["You said you would."]},
            "refuse": {"default": ["I do not yet know what your word is worth."]},
            "befriend": {"default": ["Then we are sworn. I take that seriously; so should you."]},
            "farewell": {"default": ["Go. Keep your word to somebody else."]},
        },
    ),
    ConstellationEntry(
        code="jingwei",
        tradition=MythTradition.CHINESE,
        code_name="Filling the Sea",
        code_name_zh_hant="「精衛填海」",
        real_name="Jingwei",
        real_name_zh_hant="精衛",
        epithet="who carries one twig at a time against an ocean",
        epithet_zh_hant="銜微木以填滄海者",
        description=(
            "A girl who drowned in the Eastern Sea and came back as a small "
            "bird, and who has been dropping twigs and pebbles into that sea "
            "ever since, intending to fill it. Nobody in the story tells her "
            "the arithmetic. She is the patron of everything too large to "
            "finish, which is most things worth starting."
        ),
        domain=None,
        voice={
            "offer": {
                "default": ["One pebble. That is all today asks of you."],
                "forsaken": ["The sea is no fuller than when you left. Neither is it emptier."],
            },
            "accept": {"default": ["Then carry it."]},
            "decline": {"default": ["The sea will wait. It is very good at that."]},
            "complete": {
                "default": ["One more in. You will not see the difference. It is there."],
                "champion": ["Look at what you have dropped in by now."],
            },
            "fail": {"default": ["A pebble not carried. There are more pebbles."]},
            "expire": {"default": ["The tide came and went. Tomorrow, then."]},
            "refuse": {"default": ["Not yet. Carry something first, and let me see it."]},
            "befriend": {"default": ["Then fly beside me. Bring something small."]},
            "farewell": {"default": ["Go. I will keep dropping them in."]},
        },
    ),
    ConstellationEntry(
        code="kuafu",
        tradition=MythTradition.CHINESE,
        code_name="The Sun-Chaser",
        code_name_zh_hant="「夸父逐日」",
        real_name="Kuafu",
        real_name_zh_hant="夸父",
        epithet="who drank two rivers dry and was still thirsty",
        epithet_zh_hant="飲河渭而不足者",
        description=(
            "A giant who decided to race the sun to where it sets. He nearly "
            "had it: he drank the Yellow River and the Wei dry on the way and "
            "died of thirst short of the finish, and his staff, falling, "
            "became a forest of peach trees. Whether this is a warning or an "
            "encouragement has been argued about for two thousand years."
        ),
        domain=StatName.AGILITY,
        voice={
            "offer": {"default": ["Pick something far off and go towards it."]},
            "accept": {"default": ["Then move. The light does not wait."]},
            "decline": {"default": ["It sets whether you chase it or not."]},
            "complete": {"default": ["You closed the distance. That is all chasing is."]},
            "fail": {"default": ["You stopped short. So did I, in the end."]},
            "refuse": {"default": ["Keep up for one day first. Then ask."]},
            "befriend": {"default": ["Then run with me. I warn you how it ends."]},
            "farewell": {"default": ["Go where you like. It is a wide horizon."]},
        },
    ),
    ConstellationEntry(
        code="cangjie",
        tradition=MythTradition.CHINESE,
        code_name="The Maker of Characters",
        code_name_zh_hant="「造字」",
        real_name="Cangjie",
        real_name_zh_hant="倉頡",
        epithet="at whose invention the sky rained millet and the ghosts wept",
        epithet_zh_hant="天雨粟、鬼夜哭者",
        description=(
            "The four-eyed historian of the Yellow Emperor, who watched the "
            "tracks of birds and beasts and worked out that a mark could hold "
            "a thing. When he finished, the story says, grain fell from the "
            "sky and the ghosts howled all night — because nothing could be "
            "quietly forgotten any more. He is unmoved by things you meant to "
            "write down."
        ),
        domain=StatName.INTELLIGENCE,
        voice={
            "offer": {"default": ["Set it down in marks. Then it exists."]},
            "accept": {"default": ["Then write."]},
            "decline": {"default": ["Unwritten. The ghosts sleep easy tonight."]},
            "complete": {"default": ["Recorded in your own hand. That is different from typed."]},
            "fail": {"default": ["It stayed in your head, where things go to be lost."]},
            "refuse": {"default": ["Show me twenty words of your own hand first."]},
            "befriend": {"default": ["Then you may write. Mind what you make permanent."]},
            "farewell": {"default": ["What you wrote stays written. That much is yours."]},
        },
    ),
    ConstellationEntry(
        code="shennong",
        tradition=MythTradition.CHINESE,
        code_name="Who Tasted the Hundred Herbs",
        code_name_zh_hant="「嘗百草」",
        real_name="Shennong",
        real_name_zh_hant="神農",
        epithet="who was poisoned seventy times in a day, on purpose",
        epithet_zh_hant="日遇七十毒者",
        description=(
            "The Divine Farmer, who taught agriculture and then set about "
            "eating every plant he could find to learn which healed and which "
            "killed — poisoning himself dozens of times a day and writing "
            "down the results. One of them finally killed him. Every herbal "
            "in Chinese medicine claims descent from his notes."
        ),
        domain=StatName.VITALITY,
        voice={
            "offer": {"default": ["Try one thing you have not tried. Note what it does."]},
            "accept": {"default": ["Good. Pay attention to the effect."]},
            "decline": {"default": ["Then you will not know. Knowing was the whole method."]},
            "complete": {"default": ["Noted. That is one more thing you have tested yourself."]},
            "fail": {"default": ["Untasted. You will go on guessing."]},
            "refuse": {"default": ["Not yet. Taste something new, then ask."]},
            "befriend": {"default": ["Then eat with me. Some of it will be strange."]},
            "farewell": {"default": ["Go carefully. Not everything green is kind."]},
        },
    ),
    ConstellationEntry(
        code="qianliyan",
        tradition=MythTradition.CHINESE,
        code_name="Thousand-Mile Eyes",
        code_name_zh_hant="「千里眼」",
        real_name="Qianliyan",
        real_name_zh_hant="千里眼",
        epithet="who sees the ship long before the harbour does",
        epithet_zh_hant="先港而見舟者",
        description=(
            "A demon subdued by the sea goddess Mazu and set to her service, "
            "who stands at her right hand in every one of her temples with "
            "his hand shading his brow, watching for boats in trouble. His "
            "partner Shunfeng'er hears them. Between them nothing at sea goes "
            "unnoticed. He thinks most people look only as far as their own "
            "hands."
        ),
        domain=StatName.PERCEPTION,
        voice={
            "offer": {"default": ["Look further out than usual."]},
            "accept": {"default": ["Then watch."]},
            "decline": {"default": ["I will keep watching. It is what I am for."]},
            "complete": {"default": ["You saw it coming. Most see it arrive."]},
            "fail": {"default": ["It was on the horizon the whole time."]},
            "refuse": {"default": ["I have seen you from a long way off. Not yet."]},
            "befriend": {"default": ["Then stand here beside me and look out."]},
            "farewell": {"default": ["I will watch for your boat regardless."]},
        },
    ),
    ConstellationEntry(
        code="change",
        tradition=MythTradition.CHINESE,
        code_name="She Who Fled to the Moon",
        code_name_zh_hant="「奔月」",
        real_name="Chang'e",
        real_name_zh_hant="嫦娥",
        epithet="who took the medicine and could not come back down",
        epithet_zh_hant="服藥而不得返者",
        description=(
            "She swallowed the elixir of immortality — to keep it from a "
            "thief, or out of greed, depending on who is telling it — and "
            "floated up to the moon, where she has lived alone with a hare "
            "ever since. Her husband set out her favourite food in the "
            "courtyard every year, and that is why the mooncakes. She knows "
            "more about being alone with yourself than anyone here."
        ),
        domain=None,
        voice={
            "offer": {"default": ["Spend a little time with no one else in it."]},
            "accept": {"default": ["Then be alone properly, not merely unaccompanied."]},
            "decline": {"default": ["As you like. It is quiet up here either way."]},
            "complete": {"default": ["You sat with yourself and did not flinch. Good."]},
            "fail": {"default": ["You filled it with noise. Everyone does."]},
            "refuse": {"default": ["I do not know you. Come and be quiet a while first."]},
            "befriend": {"default": ["Then look up sometimes. I am the one that is always there."]},
            "farewell": {"default": ["Go back down. I am glad you could."]},
        },
    ),
)
