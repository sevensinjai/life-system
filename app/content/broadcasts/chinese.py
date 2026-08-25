"""The trials the Chinese constellations set.

Twenty rungs each, E through S, and the rank is the ladder: E is minutes and
open to anyone, D is a sitting, C is a day, B is several and kept for players
a constellation has noticed, A is a week and kept for the ones it favours, S
is a fortnight and only ever put in front of a champion.

Every rung is clearable by anyone, anywhere, with nothing to buy.
"""

from app.content.entries import BroadcastEntry, trial
from app.models.enums import QuestDifficulty as Rank
from app.models.enums import StatName as Stat

CHINESE_TRIALS: tuple[BroadcastEntry, ...] = (
    # -- Xingtian 刑天: going on ---------------------------------------------
    trial("xingtian", "ten_more", "Ten more than you meant to",
          "Whatever you were going to stop at today, go ten past it. Ten. That is where "
          "the whole of it happens.",
          Rank.E, 10, "reps"),
    trial("xingtian", "stand_up_now", "Stand up and do one thing",
          "Whatever you have been sitting over. Stand, and do the first physical part of "
          "it. Bodies start before minds do.",
          Rank.E, 1, "things"),
    trial("xingtian", "one_after_the_no", "One more after being told no",
          "Next time something refuses you today — a machine, a person, your own body — "
          "make one further attempt before you accept it.",
          Rank.E, 1, "attempts"),
    trial("xingtian", "cold_water", "Thirty seconds of cold",
          "The end of a shower, a face full of it, whatever is available. Thirty seconds "
          "of deciding to stay.",
          Rank.E, 30, "seconds"),
    trial("xingtian", "before_dawn", "Up before you want to be",
          "Once, get up the first time you wake and do not lie back down. That is the "
          "whole trial. It is harder than the hundred.",
          Rank.E, 1, "mornings"),
    trial("xingtian", "fifty_in_a_day", "Fifty, across the day",
          "Fifty repetitions of anything, in as many sets as you like. Split it; I am "
          "counting the fifty.",
          Rank.D, 50, "reps"),
    trial("xingtian", "the_set_you_skipped", "The set you skipped yesterday",
          "Do it today, in addition. Not as penance — as arithmetic.",
          Rank.D, 1, "sets"),
    trial("xingtian", "hold_the_position", "Hold something until it burns",
          "A plank, a hang, a squat against a wall. Hold it past the point where you want "
          "to stop, then ten seconds more.",
          Rank.D, 1, "holds"),
    trial("xingtian", "the_argument_you_avoided", "Say the thing you swallowed",
          "There was something this week you did not say because it was easier. Say it, "
          "plainly and without heat.",
          Rank.D, 1, "conversations"),
    trial("xingtian", "carry_it_up", "Carry something up a hill",
          "Or up the stairs, or up the road. Loaded, uphill, once. Everything I am about "
          "is in that sentence.",
          Rank.D, 1, "climbs"),
    trial("xingtian", "hundred", "One hundred, in one day",
          "A hundred of whatever you do to make yourself stronger. Push-ups, squats, the "
          "stairs. Split them across the day if you like — I am counting the hundred, not "
          "the manner of it.",
          Rank.C, 100, "reps", stat=Stat.STRENGTH),
    trial("xingtian", "three_days_of_effort", "Three days with effort in them",
          "Three separate days, something hard on each. Consecutive is better; separate "
          "will do.",
          Rank.C, 3, "days"),
    trial("xingtian", "finish_what_beat_you", "Return to the thing that beat you",
          "Whatever defeated you most recently — a lift, a task, a conversation. Go back "
          "to it once, on purpose.",
          Rank.C, 1, "returns"),
    trial("xingtian", "do_it_tired", "Do it on the day you are tired",
          "Not the day you feel strong. The other day. That is the one that decides who "
          "you are in a year.",
          Rank.C, 1, "sessions"),
    trial("xingtian", "the_uncomfortable_ask", "Ask for the thing you want",
          "The raise, the favour, the answer, the day off. Ask plainly. Being refused is "
          "not a wound; not asking is.",
          Rank.C, 1, "requests"),
    trial("xingtian", "after_the_fall", "The set after the one you failed",
          "Find the thing you gave up on this week and do one more of it. One. Not the "
          "whole thing — the one after the one that stopped you.",
          Rank.B, 1, "attempts", penalty_exp=100),
    trial("xingtian", "four_days_hard", "Four days, something hard on each",
          "Four out of four. By the third you will have wanted to negotiate with me. I do "
          "not negotiate; I have no mouth to do it with.",
          Rank.B, 4, "days", stat=Stat.STRENGTH),
    trial("xingtian", "the_thing_you_are_afraid_of", "Do the thing you are afraid of, small",
          "Not the whole fear. The smallest real version of it — one call, one length, "
          "one flight of the stairs you avoid.",
          Rank.B, 1, "attempts"),
    trial("xingtian", "a_week_of_standing_up", "Seven days of getting up",
          "Something hard every day for a week, however small on the bad days. The bad "
          "days are the ones I am counting.",
          Rank.A, 7, "days", stat=Stat.STRENGTH, stat_amount=2),
    trial("xingtian", "the_long_defeat", "A fortnight at the thing you keep losing to",
          "Fourteen days at whatever has beaten you repeatedly. You may still lose. I "
          "lost; I am still here, still swinging.",
          Rank.S, 14, "days", stat=Stat.STRENGTH, stat_amount=3),

    # -- Yan Hui 顏回: going without -------------------------------------------
    trial("yan_hui", "eight_glasses", "Eight glasses of water",
          "Plain water, eight times, before this closes. An unglamorous trial. Most of "
          "them are.",
          Rank.E, 8, "glasses"),
    trial("yan_hui", "one_meal_plain", "One plain meal",
          "Rice, bread, vegetables, whatever is simplest in your kitchen. Eat it without "
          "improving it.",
          Rank.E, 1, "meals"),
    trial("yan_hui", "an_hour_without_buying", "Notice the wanting once",
          "The next time you want to buy something small, do not, and sit with the "
          "wanting for ten minutes. It passes. That is the finding.",
          Rank.E, 10, "minutes"),
    trial("yan_hui", "no_second_helping", "Stop before you are full",
          "One meal, once. Put the fork down slightly before you would like to.",
          Rank.E, 1, "meals"),
    trial("yan_hui", "the_unopened_thing", "Use something you already own",
          "Instead of getting the new one. The pen, the notebook, the coat, the "
          "ingredient at the back. One basket is enough for a life.",
          Rank.E, 1, "things"),
    trial("yan_hui", "one_day", "A day without the one thing",
          "You know what it is. You thought of it as you read this line. One day without "
          "it.",
          Rank.D, 1, "days", stat=Stat.VITALITY),
    trial("yan_hui", "half_the_portion", "Half of what you would have had",
          "One occasion. Not a diet — an observation of how much of it was appetite and "
          "how much was habit.",
          Rank.D, 1, "occasions"),
    trial("yan_hui", "no_delivery", "Cook rather than order, once",
          "Whatever is in the house, made by you. Cheaper, slower, better; two out of "
          "three is enough.",
          Rank.D, 1, "meals"),
    trial("yan_hui", "give_one_thing_away", "Give one thing you like away",
          "Not the rubbish. Something you would have kept. It is a small experiment in "
          "how little you need.",
          Rank.D, 1, "things"),
    trial("yan_hui", "sit_in_the_shabby_lane", "Ten minutes of doing nothing",
          "No screen, no book, no music, no plan. Ten minutes. Others could not bear the "
          "misery of my lane; I liked it well enough.",
          Rank.D, 10, "minutes"),
    trial("yan_hui", "hour_of_quiet", "One hour, nothing in your hands",
          "An hour awake with no screen, no book, no music. Sit with the quiet or walk in "
          "it. Do not fill it.",
          Rank.C, 60, "minutes"),
    trial("yan_hui", "three_days_without", "Three days without it",
          "The same thing you gave up for a day. Three days is where the wanting stops "
          "being noise and starts being information.",
          Rank.C, 3, "days"),
    trial("yan_hui", "spend_nothing", "One day spending nothing",
          "Not a single transaction. It requires a small amount of planning, which is "
          "most of what it teaches.",
          Rank.C, 1, "days"),
    trial("yan_hui", "eat_the_same_thing", "The same simple meal, three times",
          "Three days, the same plain food. Variety is a luxury, not a need; it is worth "
          "knowing the difference from the inside.",
          Rank.C, 3, "meals"),
    trial("yan_hui", "keep_your_temper", "Keep your temper once, deliberately",
          "In the next situation that would ordinarily take it. Not suppression — "
          "choosing. He did not let it change his joy.",
          Rank.C, 1, "occasions"),
    trial("yan_hui", "four_days_without", "Four days without it",
          "Whatever it is. By the fourth day you will have discovered what it was "
          "standing in for, which was always the point.",
          Rank.B, 4, "days", stat=Stat.VITALITY),
    trial("yan_hui", "one_in_one_out", "Nothing new comes in",
          "Four days in which you acquire nothing that is not food. Notice how often the "
          "impulse arrives, and what triggers it.",
          Rank.B, 4, "days"),
    trial("yan_hui", "empty_one_shelf", "Own less by one shelf",
          "Clear a shelf's worth of possessions out of your life for good. Sell, give, "
          "discard. The shelf stays empty.",
          Rank.B, 1, "shelves"),
    trial("yan_hui", "a_week_of_the_lane", "Seven days in the shabby lane",
          "A week without the one thing, with plain food and no acquiring. It is a very "
          "old technology and nobody has improved on it.",
          Rank.A, 7, "days", stat=Stat.VITALITY, stat_amount=2),
    trial("yan_hui", "a_fortnight_of_enough", "Fourteen days of enough",
          "A fortnight in which you decide, each day, that what you have is sufficient. "
          "The joy is not in the going without. The joy is what turns up in its place.",
          Rank.S, 14, "days", stat=Stat.VITALITY, stat_amount=3),

    # -- Guan Yu 關羽: keeping your word ---------------------------------------
    trial("guan_yu", "count_your_promises", "Write down what you have promised",
          "Everything you have told somebody you would do and not yet done. The list is "
          "the trial; you may be surprised how long it is.",
          Rank.E, 1, "lists"),
    trial("guan_yu", "reply_to_the_message", "Answer the message you have left sitting",
          "The one from the person who deserves better. Two lines is enough; silence is "
          "not.",
          Rank.E, 1, "messages"),
    trial("guan_yu", "be_on_time", "Be early once",
          "To one thing, on purpose. Lateness is a statement about whose time matters and "
          "everybody hears it.",
          Rank.E, 1, "occasions"),
    trial("guan_yu", "say_no_clearly", "Refuse one thing plainly",
          "No maybe, no drifting. A clear refusal is a kindness; an unkept yes is not.",
          Rank.E, 1, "refusals"),
    trial("guan_yu", "thank_by_name", "Thank somebody properly",
          "Not in passing. Say what they did and why it mattered, to their face or in "
          "writing.",
          Rank.E, 1, "thanks"),
    trial("guan_yu", "out_of_your_way", "Out of your way, once",
          "Do one thing for somebody that costs you real time and gets you nothing. I "
          "rode a thousand li through five passes for this. You may take a bus.",
          Rank.D, 1, "favours"),
    trial("guan_yu", "the_apology_you_owe", "Apologise for the thing you did",
          "Without the word 'but'. One sentence of what you did and one of what you will "
          "do instead.",
          Rank.D, 1, "apologies"),
    trial("guan_yu", "defend_someone_absent", "Speak up for somebody not in the room",
          "When they are being talked about and cannot answer. It costs a little and it "
          "is the whole of loyalty.",
          Rank.D, 1, "times"),
    trial("guan_yu", "pay_what_you_owe", "Settle one debt",
          "Money, time, a favour, a returned item. Small ones rot friendships faster than "
          "large ones.",
          Rank.D, 1, "debts"),
    trial("guan_yu", "keep_the_boring_promise", "Keep the promise nobody is checking",
          "The one you made to yourself, or to somebody who has forgotten it. Especially "
          "that one.",
          Rank.D, 1, "promises"),
    trial("guan_yu", "the_difficult_visit", "Go and see the person you have been avoiding",
          "Not because it will be pleasant. Because you said you would, or because you "
          "should have.",
          Rank.C, 1, "visits", stat=Stat.STRENGTH),
    trial("guan_yu", "three_promises", "Three promises, all kept",
          "Make three small commitments at the start of this window and keep all of "
          "them. Choose ones you can actually keep; that is a skill in itself.",
          Rank.C, 3, "promises"),
    trial("guan_yu", "refuse_the_easy_gain", "Turn down something you should not take",
          "The shortcut, the discount you are not entitled to, the credit for somebody "
          "else's work. Cao Cao offered me a great deal more.",
          Rank.C, 1, "refusals"),
    trial("guan_yu", "tell_the_inconvenient_truth", "Say the true thing that costs you",
          "To one person, once, kindly. The version where you come out slightly worse.",
          Rank.C, 1, "truths"),
    trial("guan_yu", "show_up_for_the_dull_thing", "Attend the thing you promised to attend",
          "The one you have been hoping would be cancelled. Go, and be good company while "
          "you are there.",
          Rank.C, 1, "occasions"),
    trial("guan_yu", "the_thousand_li", "Travel to keep your word",
          "A real journey — an hour or more each way — to be somewhere you said you "
          "would be, or to see somebody who needs you there.",
          Rank.B, 1, "journeys", penalty_exp=100),
    trial("guan_yu", "a_week_of_being_on_time", "A week of being where you said",
          "Seven days, every commitment met at the hour you gave. You will discover how "
          "many you make carelessly.",
          Rank.B, 7, "days"),
    trial("guan_yu", "stand_between", "Stand between somebody and trouble",
          "Take the awkward part, the blame that is partly yours, the difficult "
          "conversation somebody else is dreading.",
          Rank.B, 1, "times"),
    trial("guan_yu", "the_promise_you_broke", "Repair the thing you let fall",
          "There is a person you let down badly enough that it is still there. A week to "
          "do something real about it.",
          Rank.A, 1, "repairs", stat=Stat.STRENGTH, stat_amount=2),
    trial("guan_yu", "a_fortnight_of_your_word", "Fourteen days of keeping your word",
          "Every promise, large and small, kept or honestly withdrawn, for a fortnight. "
          "It is the hardest trial I set and the only one that changes what people say "
          "about you.",
          Rank.S, 14, "days", stat=Stat.STRENGTH, stat_amount=3),

    # -- Jingwei 精衛: one pebble at a time ------------------------------------
    trial("jingwei", "one_minute", "One minute of the impossible thing",
          "The project too big to start. Set a timer for one minute and work on it. Then "
          "stop, even if you want to go on.",
          Rank.E, 1, "minutes"),
    trial("jingwei", "name_the_sea", "Write down what the impossible thing is",
          "One sentence naming the thing you have been not-starting for months. Naming it "
          "makes it a task rather than a weather system.",
          Rank.E, 1, "sentences"),
    trial("jingwei", "the_first_pebble", "Do the very first step, only",
          "Not the project. The first physical action of the project: open the account, "
          "find the file, buy the stamp, measure the wall.",
          Rank.E, 1, "steps"),
    trial("jingwei", "five_minutes_on_it", "Five minutes, then stop",
          "On the big thing. Stopping while you still want to continue is what makes you "
          "willing to come back tomorrow.",
          Rank.E, 5, "minutes"),
    trial("jingwei", "one_line_of_it", "One line, one row, one brick",
          "The smallest indivisible unit of the thing. Do exactly one of them.",
          Rank.E, 1, "units"),
    trial("jingwei", "ten_minutes_daily", "Ten minutes, on two days",
          "The same enormous thing, ten minutes each, two days. The sea does not know the "
          "difference between this and nothing. You will.",
          Rank.D, 2, "days"),
    trial("jingwei", "break_it_into_twenty", "Break it into twenty pebbles",
          "Write the impossible thing out as twenty small tasks. It stops being an ocean "
          "somewhere around the eleventh.",
          Rank.D, 20, "tasks"),
    trial("jingwei", "the_worst_pebble", "Do the piece you dread most",
          "Out of the twenty. It is almost always smaller than the dread attached to it.",
          Rank.D, 1, "tasks"),
    trial("jingwei", "tell_one_person", "Tell one person you have started",
          "Not the whole plan. Just that you have begun. Saying it out loud puts a small "
          "cost on stopping.",
          Rank.D, 1, "people"),
    trial("jingwei", "same_time_tomorrow", "Book the time in advance",
          "Put the next session in the calendar with a real hour on it. Intentions "
          "evaporate; appointments do not.",
          Rank.D, 1, "appointments"),
    trial("jingwei", "three_stones", "Three days, one stone each",
          "The same impossible thing, touched on three separate days. Five minutes each "
          "is plenty. I have been at this for three thousand years and the method has not "
          "changed.",
          Rank.C, 3, "days"),
    trial("jingwei", "an_hour_on_the_sea", "One unbroken hour on it",
          "Not spread out. One hour, one sitting, the big thing. You will get further "
          "than three separate twenty-minute attempts.",
          Rank.C, 60, "minutes"),
    trial("jingwei", "show_the_progress", "Look at how much is already in",
          "Twenty minutes measuring what you have done rather than what remains. The pile "
          "is invisible until you go and stand next to it.",
          Rank.C, 1, "reviews"),
    trial("jingwei", "the_boring_middle_bit", "Do the unglamorous part",
          "Every large thing has a stretch nobody would ever post about. That stretch is "
          "the thing.",
          Rank.C, 1, "sessions"),
    trial("jingwei", "carry_on_after_a_bad_day", "Return the day after a bad session",
          "The session that went badly is not the test. The next day is.",
          Rank.C, 1, "returns"),
    trial("jingwei", "four_days_of_pebbles", "Four days running",
          "Something on the big thing every day for four days, however small. This is the "
          "rung where people usually find out it is possible.",
          Rank.B, 4, "days"),
    trial("jingwei", "finish_a_visible_piece", "Finish one piece that shows",
          "A chapter, a wall, a module, a room. Something you can point at. Momentum runs "
          "on visible pieces.",
          Rank.B, 1, "pieces", penalty_exp=100),
    trial("jingwei", "twice_as_long_as_comfortable", "Stay an hour past wanting to stop",
          "Once. Not as a habit — as evidence that the wanting-to-stop was not a limit.",
          Rank.B, 60, "minutes"),
    trial("jingwei", "a_week_of_twigs", "Seven days, seven twigs",
          "A week of daily work on the impossible thing. The sea is exactly as full as it "
          "was. Keep going.",
          Rank.A, 7, "days"),
    trial("jingwei", "a_fortnight_at_the_ocean", "Fourteen days at the sea",
          "Every day, however little, for a fortnight. At the end look at what has "
          "accumulated. Then pick up the next twig.",
          Rank.S, 14, "days", stat=Stat.INTELLIGENCE, stat_amount=2),

    # -- Kuafu 夸父: closing the distance --------------------------------------
    trial("kuafu", "one_street_further", "One street further than usual",
          "Wherever you normally turn back, keep going for one more street and then "
          "turn. The horizon moves; that is its habit.",
          Rank.E, 1, "journeys"),
    trial("kuafu", "five_more_minutes", "Five minutes further than planned",
          "Wherever you were going to turn around, go five minutes past it first.",
          Rank.E, 5, "minutes"),
    trial("kuafu", "drink_the_river", "Drink a litre of water on a moving day",
          "I drank the Yellow River and it was not enough. You will manage a litre.",
          Rank.E, 1, "litres"),
    trial("kuafu", "watch_a_sunset", "Watch the sun go down, all the way",
          "Start to finish, without leaving. I chased it my whole life; you can spare it "
          "fifteen minutes.",
          Rank.E, 1, "sunsets"),
    trial("kuafu", "the_high_point", "Get to the highest point nearby",
          "A hill, a roof terrace, the top floor, a bridge. Somewhere you can see further "
          "from than usual.",
          Rank.E, 1, "climbs"),
    trial("kuafu", "before_the_sun", "Move before the sun does",
          "Once, be outside and moving before sunrise. I raced the thing and lost; you "
          "only have to start before it.",
          Rank.D, 1, "mornings"),
    trial("kuafu", "an_hour_outward", "An hour outward, then turn",
          "Walk away from home for an hour and then walk back. Two hours, no destination, "
          "one decision.",
          Rank.D, 1, "walks"),
    trial("kuafu", "the_place_you_have_never_been", "Go somewhere in your own city you have never been",
          "There are dozens. Pick one and be standing in it before this closes.",
          Rank.D, 1, "places", stat=Stat.AGILITY),
    trial("kuafu", "go_further_than_last_time", "Beat your own distance",
          "Any distance you have done before, exceeded by any margin. I only ever "
          "competed with the horizon.",
          Rank.D, 1, "attempts"),
    trial("kuafu", "plant_something", "Put something in the ground",
          "A seed, a cutting, a tree if you have room. My staff fell and became a forest "
          "of peaches; that was the part that lasted.",
          Rank.D, 1, "plantings"),
    trial("kuafu", "reach_it", "Reach the thing you can see",
          "Pick something visible from where you are standing — a tower, a hill, the end "
          "of the street — and go to it on foot. Then come back, or do not.",
          Rank.C, 1, "journeys", stat=Stat.AGILITY),
    trial("kuafu", "a_day_outdoors", "Four hours outdoors in one day",
          "Not consecutive. Four hours in total under the sky, doing anything at all.",
          Rank.C, 4, "hours"),
    trial("kuafu", "the_long_walk", "Ten kilometres on foot",
          "In one go or across a day. It is further than most people walk in a week and "
          "closer than most people think.",
          Rank.C, 10, "kilometres"),
    trial("kuafu", "chase_the_ambition", "Spend an hour on the thing you actually want",
          "Not the job, not the errand. The thing you would chase across the sky if you "
          "thought you were allowed.",
          Rank.C, 60, "minutes"),
    trial("kuafu", "the_map", "Plan a journey you have not taken",
          "Properly: dates, route, cost. Planning is not doing, but nothing gets done "
          "that was never planned.",
          Rank.C, 1, "plans"),
    trial("kuafu", "twenty_kilometres", "Twenty kilometres across four days",
          "On foot, in whatever pieces suit you. The sun sets four times while you do "
          "this; that is the joke.",
          Rank.B, 20, "kilometres", stat=Stat.AGILITY),
    trial("kuafu", "sunrise_and_sunset", "See both ends of one day",
          "Sunrise and sunset on the same day, both outdoors. Almost nobody does this "
          "twice a year.",
          Rank.B, 1, "days"),
    trial("kuafu", "the_day_trip", "Go somewhere for the day",
          "Out of your town, back by night, no particular reason. Distance for its own "
          "sake is the only luxury I ever wanted.",
          Rank.B, 1, "trips"),
    trial("kuafu", "a_week_of_outward", "Seven days, some distance on each",
          "A week where every day contains real movement outdoors. The rivers will hold "
          "out; they held out for me for most of the way.",
          Rank.A, 7, "days", stat=Stat.AGILITY, stat_amount=2),
    trial("kuafu", "the_journey_you_keep_postponing", "Take the trip you keep postponing",
          "A fortnight to plan it and go, or at least to book it beyond cancellation. I "
          "died short of the horizon and would do it again.",
          Rank.S, 1, "journeys"),

    # -- Cangjie 倉頡: setting it down ------------------------------------------
    trial("cangjie", "one_kept_sentence", "One sentence worth keeping",
          "Write down one true sentence about today, by hand, and put it somewhere it "
          "will survive. Marks outlast the people who make them.",
          Rank.E, 1, "sentences"),
    trial("cangjie", "proper_name", "The proper name for it",
          "Something you have been calling 'the thing' — a bird, a part, a feeling, a "
          "tool. Find out what it is actually called.",
          Rank.E, 1, "names"),
    trial("cangjie", "label_something", "Label one thing in your house",
          "The mystery cable, the jar, the switch nobody understands. A name is a handle.",
          Rank.E, 1, "labels"),
    trial("cangjie", "write_the_list_by_hand", "Write tomorrow's list on paper",
          "Not in an app. On paper, tonight, where you will see it in the morning.",
          Rank.E, 1, "lists"),
    trial("cangjie", "one_new_character", "Learn one character or one word",
          "In any language, including your own. Write it five times. That is how they "
          "stick.",
          Rank.E, 5, "repetitions"),
    trial("cangjie", "hundred_words", "One hundred words, by hand",
          "On paper, in your own handwriting. About anything. The hand remembers "
          "differently from the keyboard; that is not sentimentality, it is why I "
          "bothered.",
          Rank.D, 100, "words", stat=Stat.INTELLIGENCE),
    trial("cangjie", "write_the_letter", "Write one letter to a person",
          "By hand, in an envelope, with a stamp. It will take twenty minutes and they "
          "will keep it for thirty years.",
          Rank.D, 1, "letters"),
    trial("cangjie", "explain_in_writing", "Explain one thing in writing",
          "A process you know, written clearly enough that somebody else could follow it. "
          "You will find the gap immediately.",
          Rank.D, 1, "explanations"),
    trial("cangjie", "the_notes_you_never_made", "Write down what you learned today",
          "Half a page. Learning that is not recorded is mostly weather.",
          Rank.D, 1, "pages"),
    trial("cangjie", "read_your_own_writing", "Read something you wrote a year ago",
          "Messages, notes, a document. Fifteen minutes with the person you used to be.",
          Rank.D, 15, "minutes"),
    trial("cangjie", "five_hundred_words", "Five hundred words",
          "On anything. Typed is acceptable at this length. Finishing is the trial; "
          "quality is between you and the page.",
          Rank.C, 500, "words", stat=Stat.INTELLIGENCE),
    trial("cangjie", "write_three_days", "Write on three separate days",
          "Anything, any length, three days. Writers are simply people who wrote on "
          "Tuesday as well.",
          Rank.C, 3, "days"),
    trial("cangjie", "document_the_thing", "Write down how the thing works",
          "The household system, the process at work, the recipe in your head. Nobody "
          "else knows it and you are not immortal.",
          Rank.C, 1, "documents"),
    trial("cangjie", "the_difficult_email", "Write the difficult message properly",
          "Draft it, leave it an hour, rewrite it, then send. The rewriting is where the "
          "damage gets removed.",
          Rank.C, 1, "messages"),
    trial("cangjie", "copy_something_beautiful", "Copy out something well written",
          "By hand. A paragraph you admire. Every writer who ever got good did this and "
          "most of them are quiet about it.",
          Rank.C, 1, "passages"),
    trial("cangjie", "a_thousand_words", "One thousand words across four days",
          "In pieces or in one go. Somewhere in the second half you will stop performing "
          "and start writing.",
          Rank.B, 1000, "words", stat=Stat.INTELLIGENCE),
    trial("cangjie", "publish_something", "Put something you wrote where somebody can read it",
          "A post, a letter, a note on a noticeboard, a message to a group. Written and "
          "unread is only half of the invention.",
          Rank.B, 1, "publications", penalty_exp=100),
    trial("cangjie", "keep_the_record", "Four days of writing down what happened",
          "Not feelings. Facts: what you did, what it cost, what worked. This is how "
          "every useful record in history began.",
          Rank.B, 4, "days"),
    trial("cangjie", "a_week_of_words", "Seven days of writing",
          "Every day, any length, no excuses about not feeling inspired. The sky rained "
          "millet for this; the least you can do is a paragraph.",
          Rank.A, 7, "days", stat=Stat.INTELLIGENCE, stat_amount=2),
    trial("cangjie", "the_thing_you_have_to_write", "Write the thing you have been avoiding writing",
          "The application, the chapter, the eulogy, the resignation, the truth. A "
          "fortnight. It will not write itself and it is not going away.",
          Rank.S, 1, "documents"),

    # -- Shennong 神農: tasting ------------------------------------------------
    trial("shennong", "never_eaten", "Something you have never eaten",
          "One food you have genuinely never tried. Note what it does to you. This is how "
          "the entire pharmacopoeia was written, though I had a rougher time of it.",
          Rank.E, 1, "tastings"),
    trial("shennong", "one_vegetable", "One vegetable you would not normally buy",
          "Buy it, cook it badly, eat it. Ninety per cent of people eat the same eleven "
          "plants for life.",
          Rank.E, 1, "vegetables"),
    trial("shennong", "read_the_label", "Read what is actually in it",
          "One thing you eat regularly. The full label, once. Knowledge first; opinions "
          "afterwards.",
          Rank.E, 1, "labels"),
    trial("shennong", "a_herb", "Use a herb or spice you have never used",
          "It is in the cupboard already, or it costs very little. Taste is a skill and "
          "it improves with attempts.",
          Rank.E, 1, "attempts"),
    trial("shennong", "notice_after_eating", "Notice how you feel an hour after eating",
          "Once, deliberately. Most people never connect the two and then wonder about "
          "the afternoon.",
          Rank.E, 1, "observations"),
    trial("shennong", "three_plants", "Three different plants, one day",
          "Three distinct plants eaten in a single day. Herbs count. This is a low bar "
          "that most days do not clear.",
          Rank.D, 3, "plants", stat=Stat.VITALITY),
    trial("shennong", "cook_from_scratch", "Cook one thing from raw ingredients",
          "Nothing pre-made. However simple. You are allowed to be bad at it; I poisoned "
          "myself seventy times a day.",
          Rank.D, 1, "meals"),
    trial("shennong", "the_bitter_thing", "Eat something bitter",
          "Bitter is the taste modern food has removed, and it is the one most of the "
          "medicine was in.",
          Rank.D, 1, "tastings"),
    trial("shennong", "one_meal_from_the_cupboard", "Make a meal from what is already there",
          "No shopping. The back of the cupboard is where invention lives and where "
          "waste dies.",
          Rank.D, 1, "meals"),
    trial("shennong", "ask_the_recipe", "Get one recipe from a person, not a screen",
          "Ask somebody how they make the thing they make well. Write it down as they say "
          "it.",
          Rank.D, 1, "recipes"),
    trial("shennong", "seven_plants", "Seven different plants in one day",
          "Vegetables, fruit, grains, nuts, herbs — seven distinct species. Considerably "
          "harder than it sounds and worth doing once to find out.",
          Rank.C, 7, "plants", stat=Stat.VITALITY),
    trial("shennong", "three_new_things", "Three foods you have never had",
          "Across this window. By the third you will be choosing differently in shops, "
          "which is the actual purpose.",
          Rank.C, 3, "tastings"),
    trial("shennong", "cook_for_the_week", "Cook once, eat three times",
          "One session, three meals' worth. The oldest labour-saving device there is.",
          Rank.C, 3, "meals"),
    trial("shennong", "the_cuisine_you_dont_know", "Cook a dish from a cuisine you have never cooked",
          "Find a recipe, get the ingredients, make it. Badly is expected and is not the "
          "point.",
          Rank.C, 1, "dishes"),
    trial("shennong", "test_one_thing_on_yourself", "Run one experiment on yourself",
          "Remove or add one thing — caffeine after noon, breakfast, the late snack — for "
          "three days and write down what happens. My entire method.",
          Rank.C, 3, "days"),
    trial("shennong", "a_week_of_plants", "Thirty plants in a week",
          "Distinct species across seven days, counted honestly. It is the single "
          "best-evidenced thing on my whole list.",
          Rank.B, 30, "plants", stat=Stat.VITALITY),
    trial("shennong", "grow_something_edible", "Grow something you can eat",
          "Herbs on a sill will do. Weeks before it is food; plant it anyway, today.",
          Rank.B, 1, "plantings"),
    trial("shennong", "cook_for_others_from_scratch", "Cook a full meal for other people",
          "From raw ingredients, for at least two others. Teaching agriculture was the "
          "easy half; the eating together was the point of it.",
          Rank.B, 1, "meals"),
    trial("shennong", "a_fortnight_of_experiments", "A fortnight of noticing what food does",
          "Fourteen days of eating attentively and writing down the effects. You will "
          "learn more about your own body than a decade of articles.",
          Rank.A, 14, "days", stat=Stat.VITALITY, stat_amount=2),
    trial("shennong", "learn_five_dishes", "Learn five dishes properly",
          "Five things you can cook without a recipe by the end of a fortnight. That is a "
          "kitchen; everything after it is refinement.",
          Rank.A, 5, "dishes"),

    # -- Qianliyan 千里眼: looking further --------------------------------------
    trial("qianliyan", "five_sounds", "Five sounds, named",
          "Sit still and name five separate sounds you can hear. It takes longer than you "
          "would think.",
          Rank.E, 5, "sounds"),
    trial("qianliyan", "horizon", "Two minutes at the furthest thing",
          "Find the most distant thing you can see from where you are and look at it for "
          "two minutes. Your eyes have been at arm's length all week.",
          Rank.E, 2, "minutes"),
    trial("qianliyan", "look_up_at_night", "Find one thing in the night sky",
          "A planet, a constellation, the moon's phase. Know its name before you go in.",
          Rank.E, 1, "sightings"),
    trial("qianliyan", "the_weather_tomorrow", "Predict tomorrow before you check",
          "Look at the sky, decide, then check. Do it enough times and you will stop "
          "needing to check.",
          Rank.E, 1, "predictions"),
    trial("qianliyan", "check_on_someone_far", "Check on somebody at a distance",
          "A message to a person in another city or country, asking how they actually "
          "are. Watching for boats in trouble is my whole occupation.",
          Rank.E, 1, "messages"),
    trial("qianliyan", "ten_sounds", "Ten sounds, named",
          "Sit still and name ten separate sounds you can hear. My partner does the "
          "hearing; I am told it takes longer than people expect.",
          Rank.D, 10, "sounds", stat=Stat.PERCEPTION),
    trial("qianliyan", "the_early_sign", "Name one problem before it arrives",
          "Something in your life is heading somewhere. Write down what it is and what "
          "the first sign would be.",
          Rank.D, 1, "predictions"),
    trial("qianliyan", "look_at_the_numbers", "Look at the number you have been avoiding",
          "The balance, the weight, the deadline, the test result. Looking is not the "
          "same as fixing and it always comes first.",
          Rank.D, 1, "numbers"),
    trial("qianliyan", "the_far_view", "Get somewhere with a long view",
          "A hill, a roof, a shore, a top floor. Twenty minutes of seeing further than a "
          "room.",
          Rank.D, 20, "minutes"),
    trial("qianliyan", "watch_the_tide", "Watch something slow for ten minutes",
          "Water, clouds, a queue, traffic. Slow things reveal their pattern only to "
          "people who stay.",
          Rank.D, 10, "minutes"),
    trial("qianliyan", "an_hour_of_watching", "An hour watching one stretch of water or road",
          "One place, one hour, no screen. Everything I know about boats I learned by "
          "being extremely bored, repeatedly.",
          Rank.C, 60, "minutes", stat=Stat.PERCEPTION),
    trial("qianliyan", "the_thing_nobody_has_said", "Name the thing everybody is avoiding",
          "In your household, your team, your family. Say it once, kindly, out loud.",
          Rank.C, 1, "conversations"),
    trial("qianliyan", "three_horizons", "Look properly at three distant things",
          "On three separate days. Eyes that only ever focus at arm's length forget how "
          "to do anything else.",
          Rank.C, 3, "days"),
    trial("qianliyan", "check_on_three", "Reach three people you have lost sight of",
          "Three messages to three people you have not spoken to in months. Some of them "
          "are in trouble and none of them will say so first.",
          Rank.C, 3, "messages"),
    trial("qianliyan", "read_the_room_ahead", "Prepare for the thing you can see coming",
          "One hour spent on the difficulty that is obviously approaching. Early is "
          "cheap; late is not.",
          Rank.C, 60, "minutes"),
    trial("qianliyan", "the_annual_look", "Look at the whole year",
          "An hour with a calendar: what is coming, what you have not prepared for, what "
          "you keep meaning to book. Storms are visible long before they arrive.",
          Rank.B, 60, "minutes", stat=Stat.PERCEPTION),
    trial("qianliyan", "the_stargazing_night", "A night looking up properly",
          "Get somewhere dark, stay an hour, learn three things you can find again. This "
          "is what the whole app is named after.",
          Rank.B, 1, "nights"),
    trial("qianliyan", "act_on_the_early_sign", "Act on the thing you predicted",
          "You named it. Now do the small thing that stops it, while it is still small.",
          Rank.B, 1, "actions", penalty_exp=100),
    trial("qianliyan", "a_week_of_watching", "A week of watching one thing closely",
          "One person, one habit, one number, one horizon. Seven days of paying it real "
          "attention and writing down what you see.",
          Rank.A, 7, "days", stat=Stat.PERCEPTION, stat_amount=2),
    trial("qianliyan", "the_long_look_at_your_life", "Look at your own life from a distance",
          "A fortnight, and at the end of it write one honest page about where it is "
          "going. I stand in a temple doing this for strangers; do it once for yourself.",
          Rank.S, 1, "pages"),

    # -- Chang'e 嫦娥: being alone ----------------------------------------------
    trial("change", "five_minutes_of_sky", "Five minutes of sky",
          "Go outside and look up for five minutes. If I am there, you will see me. If I "
          "am not, look anyway.",
          Rank.E, 5, "minutes"),
    trial("change", "silence_one_journey", "One journey in silence",
          "No music, no podcast, no call. Just the trip and whoever you are when nothing "
          "is being poured in.",
          Rank.E, 1, "journeys"),
    trial("change", "eat_one_meal_alone", "Eat one meal alone, deliberately",
          "Not lonely — alone. No screen propped against the jar. Just you and the food.",
          Rank.E, 1, "meals"),
    trial("change", "walk_without_headphones", "One walk in silence",
          "No music, no podcast, no call. Twenty minutes with only your own company.",
          Rank.E, 20, "minutes"),
    trial("change", "the_moon_tonight", "Find out what the moon is doing",
          "Its phase, tonight, by looking. I have been up here a very long time and "
          "almost nobody checks.",
          Rank.E, 1, "sightings"),
    trial("change", "an_hour_alone", "An hour by yourself",
          "One hour with no other person and nothing playing. Alone is not the same as "
          "unaccompanied, and most people have not tried the first one in years.",
          Rank.D, 1, "hours"),
    trial("change", "sit_with_the_feeling", "Sit with the thing you keep distracting yourself from",
          "Fifteen minutes, no input. It is smaller when you look at it directly. It "
          "usually is.",
          Rank.D, 15, "minutes"),
    trial("change", "go_somewhere_alone", "Go somewhere on your own",
          "A café, a gallery, a walk, a film. Alone, in public, without apologising for "
          "it to anybody including yourself.",
          Rank.D, 1, "outings"),
    trial("change", "write_what_you_actually_think", "Write one honest page nobody will read",
          "Then keep it or burn it. Solitude is where people find out what they think.",
          Rank.D, 1, "pages"),
    trial("change", "one_evening_unreachable", "One evening unreachable",
          "Phone off or away, for an evening. The world managed without you; it always "
          "does.",
          Rank.D, 1, "evenings"),
    trial("change", "half_a_day_alone", "Half a day in your own company",
          "Four hours, alone, awake, no scrolling. The first hour is uncomfortable, the "
          "third is the reason people do this.",
          Rank.C, 4, "hours"),
    trial("change", "the_decision_you_keep_deferring", "Decide one thing, alone",
          "Not by asking six people. Sit with it by yourself until you know, and then say "
          "it out loud.",
          Rank.C, 1, "decisions"),
    trial("change", "a_night_without_noise", "An evening with no screens at all",
          "From dinner to sleep. Read, cook, sit, go out. You will remember it, which is "
          "more than can be said for most evenings.",
          Rank.C, 1, "evenings"),
    trial("change", "three_solitary_hours", "Three separate hours alone",
          "On three days. Solitude is a practice, not a mood, and it needs a rhythm.",
          Rank.C, 3, "hours"),
    trial("change", "make_something_only_for_you", "Make something nobody will see",
          "A meal, a drawing, a piece of music, a garden corner. Made for one person, "
          "who is you.",
          Rank.C, 1, "things"),
    trial("change", "a_day_alone", "A whole day alone",
          "One day, by choice, without arranging company to avoid it. Immortality has "
          "given me a certain expertise here.",
          Rank.B, 1, "days"),
    trial("change", "the_solo_journey", "Go somewhere overnight alone",
          "Or a full day out of your town by yourself. Nobody to agree with about where "
          "to eat.",
          Rank.B, 1, "journeys"),
    trial("change", "no_input_for_a_day", "A day without other people's opinions",
          "No feed, no news, no comment sections. One day inside your own head to find "
          "out which thoughts were actually yours.",
          Rank.B, 1, "days"),
    trial("change", "a_week_of_an_hour", "An hour alone, every day for a week",
          "Seven hours across seven days. By the fifth you will start protecting it, "
          "which is when it has worked.",
          Rank.A, 7, "days"),
    trial("change", "a_fortnight_of_your_own_company", "Fourteen days of real solitude",
          "An hour each day, alone and undistracted, for a fortnight. At the end write "
          "one line about what you found. There is somebody up here who would like to "
          "know.",
          Rank.S, 14, "days", stat=Stat.PERCEPTION, stat_amount=2),

    # -- Han E 韓娥: making a sound ---------------------------------------------
    trial("han_e", "one_song_alone", "Sing one song, alone",
          "All the way through, out loud, where nobody can hear. Everybody begins in the "
          "kitchen.",
          Rank.E, 1, "songs"),
    trial("han_e", "hum_in_public", "Hum where somebody could hear",
          "The bus, the corridor, the queue. Barely audible counts. The point is that it "
          "left your body.",
          Rank.E, 1, "times"),
    trial("han_e", "learn_four_lines", "Learn four lines of a song by heart",
          "Any song, any language. You will need them later when somebody asks.",
          Rank.E, 4, "lines"),
    trial("han_e", "say_it_out_loud", "Read something aloud",
          "A paragraph, to the room. Voices are instruments that go out of tune from "
          "disuse.",
          Rank.E, 1, "readings"),
    trial("han_e", "breathe_properly", "Five minutes of breathing like a singer",
          "Slow, low, into the belly. It is the first thing anybody is taught and the "
          "thing everybody skips.",
          Rank.E, 5, "minutes"),
    trial("han_e", "one_song_for_one_person", "Sing to one person",
          "A child, a partner, a friend, a cat if you must start there. One song, badly, "
          "for one listener.",
          Rank.D, 1, "songs"),
    trial("han_e", "record_yourself", "Record yourself and listen back",
          "Thirty seconds. It is horrible the first time and useful every time after.",
          Rank.D, 1, "recordings"),
    trial("han_e", "the_toast", "Say something in front of the table",
          "A toast, a thank-you, a short piece of praise, out loud, to a group. Thirty "
          "seconds of being the one who is speaking.",
          Rank.D, 1, "toasts"),
    trial("han_e", "learn_the_whole_song", "Learn one song end to end",
          "Words and all, well enough to perform it without looking. You are building a "
          "repertoire, which is a thing people used to have.",
          Rank.D, 1, "songs"),
    trial("han_e", "move_while_you_sing", "Sing standing up",
          "Not hunched at a desk. Upright, planted, taking up room. Half of a voice is "
          "posture.",
          Rank.D, 1, "songs"),
    trial("han_e", "sing_where_they_can_hear", "Sing where somebody can hear you",
          "A room with another person in it, and let them hear the whole thing. This is "
          "the rung that separates people who sing from people who used to.",
          Rank.C, 1, "performances"),
    trial("han_e", "three_practices", "Three days of singing practice",
          "Twenty minutes each. Voices improve on exactly the same schedule as muscles, "
          "and go the same way when neglected.",
          Rank.C, 3, "sessions"),
    trial("han_e", "join_the_singing", "Join in where singing is happening",
          "A karaoke room, a congregation, a football stand, a birthday. Sing the whole "
          "thing rather than mouthing it.",
          Rank.C, 1, "occasions"),
    trial("han_e", "perform_the_thing_you_do", "Show somebody the thing you make",
          "It does not have to be singing. The drawing, the code, the poem, the cooking. "
          "Made and hidden is only half of it.",
          Rank.C, 1, "showings"),
    trial("han_e", "the_room_you_can_move", "Change the mood of one room",
          "With a song, a story, a joke, a question. I made a village weep and then got "
          "them dancing; you may start smaller.",
          Rank.C, 1, "rooms"),
    trial("han_e", "sing_for_strangers", "Perform in front of people who did not have to be there",
          "Open mic, karaoke with a queue, busking, a class showcase. The audience must "
          "not be obliged to be kind to you.",
          Rank.B, 1, "performances", penalty_exp=100),
    trial("han_e", "a_week_of_practice", "Five days of singing in a week",
          "Twenty minutes each. This is the difference between having a voice and having "
          "an instrument.",
          Rank.B, 5, "sessions"),
    trial("han_e", "record_something_finished", "Record one finished take",
          "One song, one performance, start to finish, kept. Send it to one person or do "
          "not — but finish it.",
          Rank.B, 1, "recordings"),
    trial("han_e", "the_repertoire", "Three songs, performance-ready",
          "By the end of a fortnight, three you can do from memory, on request, without "
          "the apology first.",
          Rank.A, 3, "songs", stat=Stat.INTELLIGENCE, stat_amount=2),
    trial("han_e", "the_rafters", "Perform something that stays with people",
          "A fortnight to prepare, and then do it in front of an audience — sing, speak, "
          "play, tell. Three days later somebody will still be humming it. That is the "
          "whole of my reputation and it is available to anybody who will stand up.",
          Rank.S, 1, "performances", stat=Stat.PERCEPTION, stat_amount=2),
)
