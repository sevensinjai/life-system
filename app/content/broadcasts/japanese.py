"""The trials the Japanese constellations set.

Twenty rungs each, E through S, and the rank is the ladder: E is minutes and
open to anyone, D is a sitting, C is a day, B is several and kept for players
a constellation has noticed, A is a week and kept for the ones it favours, S
is a fortnight and only ever put in front of a champion.

Every rung is clearable by anyone, anywhere, with nothing to buy.
"""

from app.content.entries import BroadcastEntry, trial
from app.models.enums import QuestDifficulty as Rank
from app.models.enums import StatName as Stat

JAPANESE_TRIALS: tuple[BroadcastEntry, ...] = (
    # -- Amaterasu 天照大神: coming back ---------------------------------------
    trial("amaterasu", "one_return", "The thing you stopped doing, once",
          "Whatever you were doing daily until you stopped — do it once more. Badly is "
          "fine. Briefly is fine.",
          Rank.E, 1, "returns"),
    trial("amaterasu", "open_the_curtains", "Let the light in first",
          "Before anything else tomorrow, open the curtains and stand in it for one "
          "minute. I am the sun; this is not a metaphor.",
          Rank.E, 1, "mornings"),
    trial("amaterasu", "same_hour_once", "Do one small thing at a set hour",
          "Pick the hour now. Do the thing at it. The hour is doing most of the work.",
          Rank.E, 1, "times"),
    trial("amaterasu", "come_out_of_the_room", "Leave the room you have been in all day",
          "Outside, for five minutes, whatever the weather. The cave door opens from the "
          "inside.",
          Rank.E, 5, "minutes"),
    trial("amaterasu", "reply_after_the_silence", "Answer somebody after too long",
          "Start with 'sorry for the delay' and then say the thing. The delay is never as "
          "large to them as it is to you.",
          Rank.E, 1, "messages"),
    trial("amaterasu", "same_hour", "Two days at the same hour",
          "Do one small thing at the same hour on two days running. Any hour, any thing. "
          "It is the sameness I am after.",
          Rank.D, 2, "days"),
    trial("amaterasu", "lights_out", "Lights out at the hour you chose",
          "Pick the hour now. Be in bed at it, once, in the next two nights. I keep the "
          "light so that you need not.",
          Rank.D, 1, "nights", stat=Stat.VITALITY),
    trial("amaterasu", "the_abandoned_project", "Ten minutes on the abandoned thing",
          "Not to finish it. To find out whether you still want it, which you cannot "
          "know from outside the room.",
          Rank.D, 10, "minutes"),
    trial("amaterasu", "go_back_to_the_place", "Return to a place you used to go",
          "The café, the park, the pool, the road. Places keep better than habits do.",
          Rank.D, 1, "returns"),
    trial("amaterasu", "the_morning_routine", "Do your morning properly, once",
          "Whatever it used to be when you were doing well. One morning of it, in order.",
          Rank.D, 1, "mornings"),
    trial("amaterasu", "come_back", "The thing you stopped doing",
          "Whatever you were doing daily until you stopped — do it once more. Badly is "
          "fine. Briefly is fine.",
          Rank.C, 1, "returns"),
    trial("amaterasu", "three_days_back", "Three days back at it",
          "The returned thing, three days running. A habit that survives three days has "
          "usually survived.",
          Rank.C, 3, "days"),
    trial("amaterasu", "reach_out_to_the_lapsed", "Contact somebody you let go quiet",
          "Not an apology for the silence. A continuation, as though no time had passed. "
          "It works far more often than people expect.",
          Rank.C, 1, "people"),
    trial("amaterasu", "the_daylight_hour", "An hour outdoors in daylight",
          "In whatever the sky is doing. Winter counts. Cloud counts. Being indoors from "
          "dark to dark is a modern arrangement and it does not suit anybody.",
          Rank.C, 60, "minutes", stat=Stat.VITALITY),
    trial("amaterasu", "restart_the_routine", "Rebuild one routine from its first step",
          "Not the whole system you used to run. Its first step, done three times.",
          Rank.C, 3, "times"),
    trial("amaterasu", "four_days_of_returning", "Four days, each one a return",
          "The same small thing on four days. The fourth is the one that persuades you it "
          "is yours again.",
          Rank.B, 4, "days"),
    trial("amaterasu", "the_hard_return", "Go back to what you failed at publicly",
          "The thing you stopped in front of other people. Go back once. Nobody remembers "
          "it as clearly as you do.",
          Rank.B, 1, "returns", penalty_exp=100),
    trial("amaterasu", "morning_light_four_days", "Daylight in the first hour, four days",
          "Outside, in the first hour of being awake, four days running. It resets "
          "everything downstream of it.",
          Rank.B, 4, "days", stat=Stat.VITALITY),
    trial("amaterasu", "a_week_of_coming_back", "Seven days of the returned thing",
          "Every day, however small on the bad days. The bad days are the ones I count, "
          "because I have had them.",
          Rank.A, 7, "days", stat=Stat.VITALITY, stat_amount=2),
    trial("amaterasu", "out_of_the_cave", "A fortnight of the thing you abandoned",
          "Fourteen days. At the end it will not be a return any more; it will be a "
          "thing you do. That is the whole of what I have to offer.",
          Rank.S, 14, "days", stat=Stat.VITALITY, stat_amount=3),

    # -- Sugawara no Michizane 菅原道真: study ----------------------------------
    trial("michizane", "five_hard_pages", "Five pages of something difficult",
          "Not the easy book. Five pages of the one that requires you to stop and go "
          "back. Difficulty is the entire nutrient.",
          Rank.E, 5, "pages"),
    trial("michizane", "look_it_up", "Look up the thing you keep not knowing",
          "The word, the date, the mechanism. Two minutes. You have wondered about it for "
          "years.",
          Rank.E, 1, "questions"),
    trial("michizane", "twenty_minutes_of_study", "Twenty minutes on one subject",
          "One thing, twenty minutes, no other tabs. Study is not reading; it is reading "
          "with intent to keep.",
          Rank.E, 20, "minutes"),
    trial("michizane", "one_flashcard", "Learn five words of another language",
          "Any language. Five words. Write them where you will see them tomorrow.",
          Rank.E, 5, "words"),
    trial("michizane", "the_book_you_own", "Open a book you own and have not read",
          "There is one. Read its first three pages. The plum tree followed me into "
          "exile; a book can make it off the shelf.",
          Rank.E, 3, "pages"),
    trial("michizane", "thirty_pages", "Thirty pages",
          "Thirty pages of anything you are not required to read.",
          Rank.D, 30, "pages", stat=Stat.INTELLIGENCE),
    trial("michizane", "one_lecture", "Watch or attend one proper lesson",
          "Forty minutes of somebody teaching, with notes taken. Passive watching does "
          "not count and you know the difference.",
          Rank.D, 1, "lessons"),
    trial("michizane", "the_exam_question", "Test yourself on something you claim to know",
          "Close the book and write down what you remember. The gap is the study plan.",
          Rank.D, 1, "tests"),
    trial("michizane", "learn_the_thing_at_work", "Learn the part of your work you fudge",
          "Everybody has one they have been getting away with. Thirty minutes on it.",
          Rank.D, 30, "minutes"),
    trial("michizane", "read_the_primary_source", "Read the original, not the summary",
          "The paper, the law, the document, the actual text. Summaries are other "
          "people's opinions wearing a coat.",
          Rank.D, 1, "sources"),
    trial("michizane", "explain_it", "Explain it to somebody",
          "Take one thing you learned this week and explain it out loud to another "
          "person. If you cannot, you had not learned it.",
          Rank.C, 1, "explanations"),
    trial("michizane", "three_study_days", "Study on three separate days",
          "The same subject. Spacing is not a study technique; it is the study "
          "technique.",
          Rank.C, 3, "days"),
    trial("michizane", "hundred_pages", "One hundred pages",
          "Across this window. It is roughly a third of a book and a whole evening you "
          "would otherwise not remember.",
          Rank.C, 100, "pages"),
    trial("michizane", "the_hard_chapter", "The chapter you skipped",
          "In the book you 'finished'. Go back and read the difficult part properly, with "
          "a pen.",
          Rank.C, 1, "chapters"),
    trial("michizane", "twenty_words", "Twenty words in another language",
          "Learned, tested, retained. Twenty is enough to order food and be treated "
          "differently for it.",
          Rank.C, 20, "words", stat=Stat.INTELLIGENCE),
    trial("michizane", "finish_it", "Finish the one you abandoned",
          "The book, the course, the half-written thing. Not all of it — one more "
          "session of it, today or tomorrow.",
          Rank.B, 1, "sessions", penalty_exp=100),
    trial("michizane", "a_week_of_study", "Study on five days out of seven",
          "Thirty minutes each. This is what everybody who is good at something did, "
          "quietly, while other people were discussing talent.",
          Rank.B, 5, "sessions", stat=Stat.INTELLIGENCE),
    trial("michizane", "teach_a_lesson", "Teach one proper lesson",
          "Thirty minutes, prepared, to somebody who wants to learn it. Teaching is the "
          "examination that matters.",
          Rank.B, 1, "lessons"),
    trial("michizane", "finish_the_book", "Finish a whole book",
          "One, cover to cover, within a fortnight. Most people have not done this in a "
          "year and feel worse about it than they admit.",
          Rank.A, 1, "books", stat=Stat.INTELLIGENCE, stat_amount=2),
    trial("michizane", "the_course", "Begin the course you have been meaning to take",
          "Enrol, and do the first two sessions inside a fortnight. Exile did not stop me "
          "writing; a busy month should not stop you starting.",
          Rank.S, 2, "sessions"),

    # -- Susanoo 須佐之男: one head at a time -----------------------------------
    trial("susanoo", "name_the_eight", "Write the eight heads down",
          "Take the thing that is too big and list its eight parts. You cannot cut at a "
          "neck you have not located.",
          Rank.E, 8, "heads"),
    trial("susanoo", "fifteen_minutes_of_storm", "Fifteen minutes of storm",
          "Next time you are angry, put it somewhere: fifteen minutes of hard physical "
          "effort. I wrecked my sister's hall with mine. Learn from that.",
          Rank.E, 15, "minutes"),
    trial("susanoo", "name_the_anger", "Name what you are actually angry about",
          "One sentence, written, honest. It is rarely the thing you were shouting "
          "about.",
          Rank.E, 1, "sentences"),
    trial("susanoo", "walk_away_once", "Leave the room instead",
          "Once, when it is going badly, go outside for two minutes before you say the "
          "thing. Exile taught me this and it took some years.",
          Rank.E, 2, "minutes"),
    trial("susanoo", "the_first_cut", "Start the thing you have been dreading",
          "Not finish. Start — the first ten minutes, the worst part, today.",
          Rank.E, 10, "minutes"),
    trial("susanoo", "two_heads", "Two of the eight",
          "Two pieces of the enormous thing, in one sitting. The serpent gets smaller "
          "with each one and it never grows them back as fast as you fear.",
          Rank.D, 2, "heads", stat=Stat.STRENGTH),
    trial("susanoo", "clear_the_wreckage", "Clean up one thing you made worse",
          "A mess, a mood, a misunderstanding you caused. I was thrown out of heaven for "
          "leaving mine.",
          Rank.D, 1, "repairs"),
    trial("susanoo", "hard_effort", "Twenty minutes of hard effort",
          "Whatever counts as hard for you today. Anger is fuel with nowhere to go; give "
          "it somewhere.",
          Rank.D, 20, "minutes"),
    trial("susanoo", "the_apology_after_the_storm", "Apologise for the way you said it",
          "You may still be right about the content. Say sorry for the delivery, which is "
          "the part that did the damage.",
          Rank.D, 1, "apologies"),
    trial("susanoo", "prepare_the_sake", "Prepare instead of charging in",
          "I beat the serpent with eight vats of sake, not with strength. Spend twenty "
          "minutes preparing for the fight you keep losing.",
          Rank.D, 20, "minutes"),
    trial("susanoo", "four_heads", "Four of the eight",
          "Half the serpent, across this window. You are past the point where quitting "
          "would feel neutral.",
          Rank.C, 4, "heads", stat=Stat.STRENGTH),
    trial("susanoo", "the_confrontation", "Have the difficult conversation, calmly",
          "The one you have been rehearsing angrily. Have it in the tone you would want "
          "used on you.",
          Rank.C, 1, "conversations"),
    trial("susanoo", "train_the_anger_out", "Three sessions of putting it somewhere",
          "Three hard efforts across three days, deliberately used to burn something off. "
          "It works and it is free.",
          Rank.C, 3, "sessions"),
    trial("susanoo", "protect_somebody", "Take the difficult thing off somebody else",
          "The awkward call, the heavy job, the conversation they are dreading. I turned "
          "up in disgrace and killed a serpent for strangers.",
          Rank.C, 1, "times"),
    trial("susanoo", "the_thing_you_broke", "Repair what your temper cost you",
          "A relationship, a reputation, a possession. One real act of repair, not an "
          "explanation.",
          Rank.C, 1, "repairs"),
    trial("susanoo", "all_eight_heads", "All eight",
          "Finish the whole serpent inside four days. It was never eight monsters; it was "
          "one, eight times.",
          Rank.B, 8, "heads", stat=Stat.STRENGTH, penalty_exp=100),
    trial("susanoo", "a_week_of_the_storm_used_well", "Five hard efforts in seven days",
          "Whatever is going on in your life, put it through the body five times this "
          "week rather than through the people around you.",
          Rank.B, 5, "sessions"),
    trial("susanoo", "make_amends_properly", "Go back to somebody you wronged",
          "Not a message. In person, or as close as you can get. Say what you did without "
          "softening it.",
          Rank.B, 1, "amends"),
    trial("susanoo", "the_monster_you_have_been_avoiding", "Take on the thing everyone else walked past",
          "The problem nobody in your household, team or family will touch. A week. "
          "Somebody has to and it turns out to be you.",
          Rank.A, 7, "days", stat=Stat.STRENGTH, stat_amount=2),
    trial("susanoo", "the_exile_years", "A fortnight of being useful while in disgrace",
          "Whatever you have most recently got wrong: fourteen days of quietly doing good "
          "work anyway, with no announcement. That is the whole of my rehabilitation.",
          Rank.S, 14, "days"),

    # -- Benzaiten 辯才天: making a sound ---------------------------------------
    trial("benzaiten", "one_song", "One song, all the way through",
          "Sing it, hum it, play it, badly. All the way to the end without stopping to be "
          "embarrassed. Alone counts, but not by much.",
          Rank.E, 1, "songs"),
    trial("benzaiten", "listen_to_water", "Sit by moving water for five minutes",
          "A river, a fountain, a shore, rain on a window. I live on every island and "
          "pond in the country for a reason.",
          Rank.E, 5, "minutes"),
    trial("benzaiten", "say_the_kind_thing", "Say the compliment you thought and swallowed",
          "Out loud, to the person. Unspoken praise helps nobody.",
          Rank.E, 1, "compliments"),
    trial("benzaiten", "put_music_on_properly", "Listen to one album without doing anything else",
          "Or twenty minutes of it. Music as an activity rather than as wallpaper.",
          Rank.E, 20, "minutes"),
    trial("benzaiten", "ten_minutes_of_playing", "Ten minutes on an instrument",
          "Any instrument, including your voice and the table. Ten minutes of making "
          "rather than consuming.",
          Rank.E, 10, "minutes"),
    trial("benzaiten", "the_sentence", "The sentence you have been avoiding",
          "There is one you have rehearsed and not said. Say it to the person it is for. "
          "Words are water: held too long they go stagnant.",
          Rank.D, 1, "sentences", stat=Stat.INTELLIGENCE),
    trial("benzaiten", "speak_up_in_the_room", "Say the thing in the meeting",
          "The point you were going to keep to yourself. Say it once, clearly, and do "
          "not trail off at the end.",
          Rank.D, 1, "times"),
    trial("benzaiten", "practise_the_hard_bit", "Twenty minutes on the passage you cannot play",
          "The bar, the phrase, the sentence, the pronunciation. Slowly, repeatedly, "
          "until it stops being the hard bit.",
          Rank.D, 20, "minutes"),
    trial("benzaiten", "read_it_aloud", "Read your own writing out loud",
          "Anything you wrote. Aloud. Every clumsy sentence announces itself immediately.",
          Rank.D, 1, "readings"),
    trial("benzaiten", "ask_for_what_you_want", "Ask for it in words",
          "Not hints, not hoping they notice. Say what you would like, plainly, to "
          "somebody who can give it.",
          Rank.D, 1, "requests"),
    trial("benzaiten", "three_sessions_of_practice", "Three sessions with the instrument",
          "The same instrument, voice, or language. Water shapes stone by returning, not "
          "by force.",
          Rank.C, 3, "sessions", stat=Stat.INTELLIGENCE),
    trial("benzaiten", "perform_for_one", "Play or sing for one person",
          "Live, in the room. The first audience is the hardest and it is nearly always "
          "somebody who already loves you.",
          Rank.C, 1, "performances"),
    trial("benzaiten", "write_something_to_be_heard", "Write something meant to be spoken",
          "A toast, a lyric, a speech, a story for a child. Different rules apply and "
          "learning them makes all your writing better.",
          Rank.C, 1, "pieces"),
    trial("benzaiten", "the_difficult_conversation_well", "Have the conversation with grace",
          "Not just have it — have it well. Prepare the first sentence and the tone. "
          "Eloquence is a kindness technology.",
          Rank.C, 1, "conversations"),
    trial("benzaiten", "learn_a_piece", "Learn one short piece properly",
          "A song, a poem, a passage, a joke that lands. Something you can produce on "
          "request for the rest of your life.",
          Rank.C, 1, "pieces"),
    trial("benzaiten", "play_with_others", "Make something with other people",
          "A jam, a choir, a band, a reading group, a game with actual conversation. "
          "Flowing things join up.",
          Rank.B, 1, "occasions"),
    trial("benzaiten", "five_practices", "Five days with the instrument",
          "Fifteen minutes each. The gap between people who play and people who used to "
          "play is exactly this.",
          Rank.B, 5, "sessions", stat=Stat.INTELLIGENCE),
    trial("benzaiten", "the_speech", "Speak in front of a group",
          "A toast, a presentation, a lesson, a eulogy. Prepared, delivered, survived.",
          Rank.B, 1, "speeches", penalty_exp=100),
    trial("benzaiten", "a_fortnight_of_flow", "Fourteen days of making sound",
          "Something musical or spoken every day for a fortnight, however short. Money, "
          "music and rivers were all put under my care because they behave the same way.",
          Rank.A, 14, "days", stat=Stat.INTELLIGENCE, stat_amount=2),
    trial("benzaiten", "finish_the_piece", "Finish and share one made thing",
          "A recording, a song, a written piece, a performance. Finished and given to at "
          "least one other person within a fortnight.",
          Rank.S, 1, "pieces"),

    # -- Sukunabikona 少彥名神: the small dose ----------------------------------
    trial("sukunabikona", "five_minutes", "Five minutes is enough",
          "The thing you keep not starting because it deserves an hour. Give it five "
          "minutes. I am the size of a thumb and I helped build a country.",
          Rank.E, 5, "minutes", stat=Stat.VITALITY),
    trial("sukunabikona", "one_remedy", "One small remedy",
          "One small thing done for the body: a glass of water, a window opened, a "
          "stretch, a plaster on the cut you have been ignoring.",
          Rank.E, 1, "remedies"),
    trial("sukunabikona", "one_percent", "Improve one thing by a fraction",
          "The chair height, the alarm, the route, the recipe. One tiny adjustment that "
          "you will benefit from a thousand times.",
          Rank.E, 1, "adjustments"),
    trial("sukunabikona", "two_minutes_of_tidying", "Two minutes of tidying",
          "A timer, one small area. Two minutes is beneath your dignity, which is exactly "
          "why it gets done.",
          Rank.E, 2, "minutes"),
    trial("sukunabikona", "the_smallest_kindness", "One small kindness, unannounced",
          "Refill something, move something out of somebody's way, send the useful link. "
          "Nobody has to know it was you.",
          Rank.E, 1, "kindnesses"),
    trial("sukunabikona", "ten_minutes_daily", "Ten minutes, two days running",
          "The same small thing on both. Small and repeated beats large and abandoned, "
          "every time, for everything.",
          Rank.D, 2, "days"),
    trial("sukunabikona", "the_tiny_habit", "Attach one small thing to something you already do",
          "Stretch while the kettle boils, water while you brush. This is the entire "
          "trick and it costs nothing.",
          Rank.D, 1, "habits"),
    trial("sukunabikona", "brew_something", "Make something that needs waiting",
          "Tea, bread, stock, a marinade, a cutting in water. I taught brewing among "
          "other things; waiting is a skill.",
          Rank.D, 1, "things"),
    trial("sukunabikona", "the_five_minute_favour", "Five minutes that saves somebody an hour",
          "An introduction, an answer, a template, a lift. Cheap for you, expensive for "
          "them to do alone.",
          Rank.D, 5, "minutes"),
    trial("sukunabikona", "fix_the_small_annoyance", "Fix the thing that annoys you daily",
          "The loose handle, the app notification, the badly placed bin. It has cost you "
          "hours in irritation and ten minutes in repair.",
          Rank.D, 1, "fixes"),
    trial("sukunabikona", "three_days_of_five_minutes", "Five minutes a day, three days",
          "The same thing. Fifteen minutes in total and it will do more than one "
          "two-hour session, which is unfair and true.",
          Rank.C, 3, "days", stat=Stat.VITALITY),
    trial("sukunabikona", "the_small_medicine", "Take the small treatment seriously",
          "The stretch for the injury, the drops, the exercise you were prescribed and "
          "abandoned. Three days of doing it properly.",
          Rank.C, 3, "days"),
    trial("sukunabikona", "one_thing_at_a_time", "Do one small thing per hour, for one day",
          "Six tiny tasks across a working day. The pile shrinks by more than it feels "
          "like it should.",
          Rank.C, 6, "tasks"),
    trial("sukunabikona", "make_it_easier_for_next_time", "Set the next version up",
          "Lay the clothes out, prep the ingredients, open the file to the right page. "
          "Small gods work on logistics.",
          Rank.C, 1, "preparations"),
    trial("sukunabikona", "the_five_minute_start", "Start three things you have been avoiding",
          "Five minutes each. You may stop after five. You will not, twice out of three "
          "times.",
          Rank.C, 3, "starts"),
    trial("sukunabikona", "a_week_of_five_minutes", "Five minutes a day for a week",
          "The same thing, seven days. This is the rung where people discover they have "
          "accidentally acquired a habit.",
          Rank.B, 7, "days", stat=Stat.VITALITY),
    trial("sukunabikona", "the_tiny_thing_that_scales", "Find the small change with the largest effect",
          "Spend half an hour identifying the one small adjustment that would improve the "
          "most days, then make it.",
          Rank.B, 1, "changes"),
    trial("sukunabikona", "help_build_something", "Help somebody else's project for an hour",
          "I arrived on a wave and helped build a country, then left. Give an hour to "
          "something that is not yours.",
          Rank.B, 60, "minutes"),
    trial("sukunabikona", "a_fortnight_of_small_doses", "Fourteen days of five minutes",
          "One thing, five minutes, every day, a fortnight. Seventy minutes in total. "
          "Watch what it does anyway.",
          Rank.A, 14, "days", stat=Stat.VITALITY, stat_amount=2),
    trial("sukunabikona", "ten_small_repairs", "Ten small repairs in a fortnight",
          "Ten of the tiny broken things in your life, fixed. Nobody notices a house "
          "where everything works, which is the highest compliment there is.",
          Rank.A, 10, "repairs"),

    # -- Sarutahiko 猿田彥: the fork --------------------------------------------
    trial("sarutahiko", "the_turn", "The turning you never take",
          "On a route you know by heart, take the other way once. You will arrive late "
          "and know one more thing about where you live.",
          Rank.E, 1, "turnings", stat=Stat.AGILITY),
    trial("sarutahiko", "answer_plainly", "Answer one question straight",
          "The next time somebody asks what you want, say it without hedging. I blocked "
          "the crossroads of heaven until somebody asked me directly.",
          Rank.E, 1, "answers"),
    trial("sarutahiko", "one_small_decision", "Decide one thing you have been leaving open",
          "Small. Now. Undecided things cost more than wrong ones.",
          Rank.E, 1, "decisions"),
    trial("sarutahiko", "ask_the_local", "Ask somebody who knows",
          "Instead of a search engine. A neighbour, a shopkeeper, a colleague. People are "
          "better maps and they enjoy being asked.",
          Rank.E, 1, "questions"),
    trial("sarutahiko", "stand_at_the_junction", "Look at where the roads actually go",
          "At one junction you pass daily, find out where the other way leads. Two "
          "minutes and a map.",
          Rank.E, 1, "junctions"),
    trial("sarutahiko", "show_the_way", "Show somebody the way",
          "Give somebody directions, walk them to the place, or explain the thing you "
          "know that they do not. Standing at the fork is only useful if you point.",
          Rank.D, 1, "times"),
    trial("sarutahiko", "the_unfamiliar_route", "Get somewhere by an unfamiliar route",
          "Different road, different line, different door. Your city is larger than the "
          "four paths you use.",
          Rank.D, 1, "journeys"),
    trial("sarutahiko", "make_the_choice_you_are_dodging", "Choose between two things you keep weighing",
          "You have had the information for weeks. The deciding is the work; the "
          "information was never the obstacle.",
          Rank.D, 1, "decisions"),
    trial("sarutahiko", "introduce_two_people", "Introduce two people who should know each other",
          "You can see the connection and they cannot. Standing where the roads meet has "
          "obligations.",
          Rank.D, 1, "introductions"),
    trial("sarutahiko", "say_what_you_are_here_for", "State plainly what you want from a situation",
          "At the start rather than the end. Enormous amounts of trouble come from "
          "everybody guessing.",
          Rank.D, 1, "times"),
    trial("sarutahiko", "explore_one_district", "Spend an hour in a part of your town you avoid",
          "Not dangerous — unfamiliar. There is a difference and most people have "
          "stopped checking which is which.",
          Rank.C, 60, "minutes", stat=Stat.AGILITY),
    trial("sarutahiko", "guide_somebody", "Guide somebody through something you have done",
          "A process, a city, an application, a first attempt. Go in front and look back "
          "to check they are following.",
          Rank.C, 1, "times"),
    trial("sarutahiko", "three_new_ways", "Three journeys by new routes",
          "Three, across this window. By the third you will have a different map of "
          "where you live.",
          Rank.C, 3, "journeys"),
    trial("sarutahiko", "the_decision_with_a_deadline", "Set a deadline on the open question",
          "Write the date you will decide by, tell one person, and keep it.",
          Rank.C, 1, "deadlines"),
    trial("sarutahiko", "block_the_wrong_road", "Say no to the thing heading the wrong way",
          "A commitment, an offer, a habit, a direction. Standing in the way is also "
          "guidance.",
          Rank.C, 1, "refusals"),
    trial("sarutahiko", "the_bigger_fork", "Take the first real step on the larger decision",
          "The move, the job, the course, the conversation. Not the decision — the first "
          "irreversible small step of it.",
          Rank.B, 1, "steps", penalty_exp=100),
    trial("sarutahiko", "a_week_of_new_ways", "A different route every day for four days",
          "Home, work, shop, walk. Four days of refusing the groove.",
          Rank.B, 4, "days"),
    trial("sarutahiko", "lead_something", "Organise something for other people",
          "A meal, a walk, a game, a meeting. Somebody has to pick the place and the "
          "hour, and everybody is relieved when it is not them.",
          Rank.B, 1, "occasions"),
    trial("sarutahiko", "a_week_of_deciding", "Clear seven open decisions in a week",
          "All the small undecided things. The relief is disproportionate and immediate.",
          Rank.A, 7, "decisions", stat=Stat.AGILITY, stat_amount=2),
    trial("sarutahiko", "walk_the_boundary", "Explore the edge of your own map",
          "A fortnight to visit four places within reach that you have never been. The "
          "crossroads of heaven was in nobody's plans either.",
          Rank.A, 4, "places"),

    # -- Yatagarasu 八咫烏: going in front --------------------------------------
    trial("yatagarasu", "three_living_things", "Three living things that are not people",
          "A bird, a weed through the pavement, a spider in the corner, a tree you pass "
          "daily. Three of them, properly looked at.",
          Rank.E, 3, "things", stat=Stat.PERCEPTION),
    trial("yatagarasu", "name_one_bird", "Learn the name of one bird near you",
          "By its look or its call. There are perhaps eight in your neighbourhood and "
          "you can probably name two.",
          Rank.E, 1, "birds"),
    trial("yatagarasu", "go_first_small", "Send the first message",
          "In a conversation that has gone quiet. Somebody has to and it is never going "
          "to be them.",
          Rank.E, 1, "messages"),
    trial("yatagarasu", "look_before_the_map", "Find your way once without checking",
          "A short journey you roughly know. Get there by looking rather than by "
          "following the blue dot.",
          Rank.E, 1, "journeys"),
    trial("yatagarasu", "notice_the_weather_properly", "Spend two minutes noticing the sky",
          "What it is doing, which way the wind is, what it means. Birds are extremely "
          "good at this and have no instruments.",
          Rank.E, 2, "minutes"),
    trial("yatagarasu", "go_first", "Go first, once",
          "Make the plan, send the message, pick the place, start the conversation. "
          "Somebody has to walk in front and it is usually the same person.",
          Rank.D, 1, "times"),
    trial("yatagarasu", "ask_the_awkward_question", "Ask the question everybody is thinking",
          "In a room where nobody will. It is almost always welcome and almost never "
          "volunteered.",
          Rank.D, 1, "questions"),
    trial("yatagarasu", "scout_ahead", "Find out what is coming",
          "For a thing you and others are walking into — read the document, ask the "
          "question, check the route. Then tell them.",
          Rank.D, 1, "scoutings"),
    trial("yatagarasu", "five_living_things", "Five living things, named properly",
          "Not 'a bird'. The actual species. Naming is the difference between scenery "
          "and neighbours.",
          Rank.D, 5, "species"),
    trial("yatagarasu", "walk_somebody_home", "Go the extra part of the way with somebody",
          "To the station, to the door, to the end of the road. Guides do not carry "
          "people; they accompany them.",
          Rank.D, 1, "times"),
    trial("yatagarasu", "an_hour_outdoors_watching", "An hour outdoors watching what lives there",
          "A park, a hedge, a shoreline, a window box. An hour. You are surrounded and "
          "you have not been counting.",
          Rank.C, 60, "minutes", stat=Stat.PERCEPTION),
    trial("yatagarasu", "lead_the_walk", "Take somebody somewhere they have not been",
          "You pick, you navigate, you take responsibility for it being worth it.",
          Rank.C, 1, "outings"),
    trial("yatagarasu", "make_the_plan_for_everyone", "Make the plan the group has been failing to make",
          "Pick the date, the place, the time. Send it. Watch how quickly everybody "
          "agrees once somebody decides.",
          Rank.C, 1, "plans"),
    trial("yatagarasu", "learn_the_local_ecology", "Learn what lives where you live",
          "Half an hour with a guide or an app, then a walk applying it. Emperors have "
          "been led through worse-mapped country.",
          Rank.C, 30, "minutes"),
    trial("yatagarasu", "check_the_route_for_someone", "Do the groundwork for somebody else",
          "Look up the thing, find the place, test the process, and hand them the "
          "answer. Going in front is a service.",
          Rank.C, 1, "times"),
    trial("yatagarasu", "four_days_of_going_first", "Go first on four separate days",
          "The message, the plan, the question, the offer. Four days of being the one who "
          "moves.",
          Rank.B, 4, "days"),
    trial("yatagarasu", "the_journey_you_lead", "Lead a day out for other people",
          "Plan it, propose it, take them. If it goes badly it is on you, which is what "
          "leading is.",
          Rank.B, 1, "journeys"),
    trial("yatagarasu", "twenty_species", "Twenty species, known by name",
          "Birds, trees, insects, weeds — twenty living things around you that you can "
          "name on sight by the end of four days.",
          Rank.B, 20, "species", stat=Stat.PERCEPTION),
    trial("yatagarasu", "a_week_in_front", "A week of being the one who starts things",
          "Every day, one thing initiated rather than waited for. It is exhausting and it "
          "changes how people treat you.",
          Rank.A, 7, "days", stat=Stat.PERCEPTION, stat_amount=2),
    trial("yatagarasu", "guide_somebody_through_a_fortnight", "Guide one person for a fortnight",
          "Somebody starting something you have already done. Check in, go ahead, look "
          "back. I led an emperor through mountains nobody could read; you can manage a "
          "beginner.",
          Rank.S, 14, "days"),

    # -- Ame-no-Uzume 天鈿女命: being ridiculous ---------------------------------
    trial("uzume", "three_minutes_dancing", "Three minutes of dancing badly",
          "Where nobody can see, if you must. Three minutes. I did this on an upturned "
          "tub in front of eight hundred gods and it ended a world-wide darkness.",
          Rank.E, 3, "minutes"),
    trial("uzume", "one_laugh_alone", "Laugh out loud on purpose",
          "At something genuinely funny, alone, without checking whether it is allowed.",
          Rank.E, 1, "laughs"),
    trial("uzume", "the_stupid_photo", "Take one ridiculous photograph",
          "Of yourself, on purpose, badly. Dignity is a very expensive thing to carry "
          "everywhere.",
          Rank.E, 1, "photographs"),
    trial("uzume", "say_the_silly_thing", "Say the daft thing you were going to keep in",
          "The pun, the joke, the ridiculous suggestion. The room is more grateful than "
          "you think.",
          Rank.E, 1, "times"),
    trial("uzume", "wear_the_thing", "Wear the thing you think is too much",
          "The colour, the coat, the hat at the back of the wardrobe. Once, out of the "
          "house.",
          Rank.E, 1, "days"),
    trial("uzume", "one_laugh", "Somebody else's laugh",
          "Make one other person laugh, on purpose. Not a good joke. A laugh. The gods I "
          "got were not laughing at anything clever.",
          Rank.D, 1, "laughs"),
    trial("uzume", "dance_with_somebody", "Dance where one other person can see",
          "A kitchen, a party, a bus stop. Badly, and without waiting for the right "
          "song.",
          Rank.D, 1, "times"),
    trial("uzume", "play_a_game", "Play something with no purpose",
          "A game, a sport, a silly competition. Twenty minutes of doing a thing that "
          "improves nothing.",
          Rank.D, 20, "minutes"),
    trial("uzume", "be_bad_at_something_publicly", "Try something in front of somebody who is better",
          "And be visibly bad at it. This is the entire toll on the bridge to being good "
          "at anything.",
          Rank.D, 1, "attempts"),
    trial("uzume", "cheer_somebody_up", "Deliberately lift one person's day",
          "A message, a snack, a stupid video, a visit. Aim at one specific person who is "
          "in the cave this week.",
          Rank.D, 1, "people"),
    trial("uzume", "make_three_people_laugh", "Three laughs, three people",
          "Across this window. It is a real skill and it responds to practice like any "
          "other.",
          Rank.C, 3, "laughs"),
    trial("uzume", "the_party_you_would_skip", "Go to the thing you were going to avoid",
          "And be good company when you get there. Half the darkness in the world is "
          "people who stayed in.",
          Rank.C, 1, "occasions"),
    trial("uzume", "try_the_beginner_class", "Go to a beginners' class in something",
          "Dance, pottery, boxing, language. Be the worst person in the room for an "
          "hour.",
          Rank.C, 1, "classes"),
    trial("uzume", "the_undignified_help", "Do the unglamorous job cheerfully",
          "Wash up at somebody else's party, carry the boxes, take the early shift. And "
          "be pleasant about it, which is the trial.",
          Rank.C, 1, "times"),
    trial("uzume", "sing_in_the_car", "Make noise with other people",
          "Karaoke, the car, the kitchen, the terraces. Loudly, together, badly.",
          Rank.C, 1, "occasions"),
    trial("uzume", "perform_the_ridiculous_thing", "Do something silly in front of a group",
          "A dance, a costume, an impression, a game you organise. Somebody in that room "
          "needed permission and you are giving it.",
          Rank.B, 1, "performances"),
    trial("uzume", "four_days_of_lightness", "Make somebody laugh on four separate days",
          "Four days, four people, or the same person four times. Either counts; both "
          "are work.",
          Rank.B, 4, "days"),
    trial("uzume", "open_somebody_elses_door", "Get one person out of their cave",
          "Somebody who has gone quiet. Do not ask if they want to; turn up, or make it "
          "easy, or be ridiculous at them until they come out.",
          Rank.B, 1, "people"),
    trial("uzume", "a_week_of_not_being_dignified", "Seven days with something undignified in each",
          "A dance, a joke, an attempt at something you are bad at. Seven days of "
          "spending dignity, which turns out to be renewable.",
          Rank.A, 7, "days"),
    trial("uzume", "the_thing_that_opens_the_cave", "Organise the thing that gets everybody out",
          "A fortnight to plan and hold it: a party, a game night, a trip, a reunion. "
          "Eight hundred gods laughed and the sun came out to see why. That was me, and "
          "it can be you.",
          Rank.S, 1, "occasions", stat=Stat.PERCEPTION, stat_amount=2),
)
