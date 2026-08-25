"""The trials the Greek constellations set.

Twenty rungs each, E through A, and the rank is the ladder: E is minutes and
open to anyone, D is a sitting, C is a day, B is several and kept for players
a constellation has noticed, A is a week and kept for the ones it favours.

Every rung is clearable by anyone, anywhere, with nothing to buy. That is a
rule of the catalogue, not a coincidence — these go out to everybody at once.
"""

from app.content.entries import BroadcastEntry, trial
from app.models.enums import QuestDifficulty as Rank
from app.models.enums import StatName as Stat

GREEK_TRIALS: tuple[BroadcastEntry, ...] = (
    # -- Hermes 赫爾墨斯: ground covered ------------------------------------
    trial("hermes", "one_stop_early", "Get off one stop early",
          "Or park further away, or leave the car. One journey made slightly longer on "
          "purpose.",
          Rank.E, 1, "journeys"),
    trial("hermes", "one_flight", "The stairs, once",
          "One flight you would normally have ridden. I am the god of thresholds; "
          "this is a very small one.",
          Rank.E, 1, "flights"),
    trial("hermes", "five_minutes_out", "Five minutes outside",
          "Out of the door, five minutes, no destination, back in. The going out is "
          "the whole of it.",
          Rank.E, 5, "minutes"),
    trial("hermes", "long_way", "The long way round",
          "Once, take the longer route somewhere you were going anyway. You will be "
          "late. That is the trial.",
          Rank.E, 1, "journeys"),
    trial("hermes", "stand_hourly", "Stand up every hour",
          "Six times in one day, get up and go somewhere — the window, the kettle, "
          "the street. Sitting still is the only thing I have never understood.",
          Rank.E, 6, "times"),
    trial("hermes", "three_walks", "Three walks, any length",
          "Three times, go outside and walk with no destination. Ten minutes counts. "
          "The point is the going out, three separate times.",
          Rank.D, 3, "walks"),
    trial("hermes", "walk_and_talk", "Take the call walking",
          "One conversation held on your feet and outdoors. It changes what gets said; "
          "I do not know why.",
          Rank.D, 1, "calls"),
    trial("hermes", "walked_not_ridden", "One journey walked, not ridden",
          "A trip you would normally take a vehicle for, done on foot. Choose a short "
          "one; I am not trying to ruin your day.",
          Rank.D, 1, "journeys"),
    trial("hermes", "morning_air", "Outside within the hour",
          "One morning, be out of doors within an hour of waking. Even for two minutes.",
          Rank.D, 1, "mornings"),
    trial("hermes", "errand_on_foot", "The errand, on foot",
          "One small errand — post, shop, return, drop-off — done by walking. "
          "Messages were my whole profession.",
          Rank.D, 1, "errands"),
    trial("hermes", "ten_thousand", "Ten thousand steps",
          "Cover ten thousand steps before this closes. They do not have to be fast "
          "and they do not have to be anywhere.",
          Rank.C, 10000, "steps", stat=Stat.AGILITY),
    trial("hermes", "new_street", "A street you have never walked",
          "There is one within a mile of where you sleep. Walk down it and come back "
          "knowing something you did not.",
          Rank.C, 1, "streets"),
    trial("hermes", "hour_on_foot", "An hour on foot, unbroken",
          "Sixty minutes of walking in one piece. Not sixty minutes across a day — one "
          "hour, one road.",
          Rank.C, 60, "minutes"),
    trial("hermes", "by_hand", "Deliver something by hand",
          "A note, a returned book, a thing you have been meaning to give somebody. "
          "Carry it there yourself. I invented the profession.",
          Rank.C, 1, "deliveries"),
    trial("hermes", "three_days_moving", "Three days, moving on each",
          "Some deliberate walking on three separate days. The gaps between them are "
          "what this is testing.",
          Rank.C, 3, "days"),
    trial("hermes", "twenty_thousand", "Twenty thousand in a day",
          "Twice the usual, in one day. Plan it, or discover halfway through that you "
          "have not.",
          Rank.B, 20000, "steps"),
    trial("hermes", "to_the_boundary", "Walk to the edge of where you live",
          "Pick the boundary of your town, your district, your island — and walk until "
          "you are standing on it.",
          Rank.B, 1, "journeys"),
    trial("hermes", "cross_to_see_them", "Cross something to see somebody",
          "A river, a city, a border, an hour of travel. Go and see the person you keep "
          "saying you should go and see.",
          Rank.B, 1, "visits", stat=Stat.AGILITY),
    trial("hermes", "fifty_thousand_week", "Fifty thousand in a week",
          "Over seven days. It is not a hard number; it is a number that punishes three "
          "days of forgetting.",
          Rank.A, 50000, "steps", stat=Stat.AGILITY, stat_amount=2),
    trial("hermes", "a_day_on_foot", "A whole day without wheels",
          "One entire day in which nothing carries you but your own legs. Plan the day "
          "around it, which is the point.",
          Rank.A, 1, "days"),

    # -- Argus Panoptes 阿爾戈斯: attention ----------------------------------
    trial("argus", "ten_minutes", "Ten minutes at the window",
          "Ten minutes looking out of a window at whatever is out there. No phone. This "
          "is not meditation; it is just looking.",
          Rank.E, 10, "minutes"),
    trial("argus", "five_things", "Five things you had not noticed",
          "Find five things on a route you take every day that you have never actually "
          "looked at. Write them down or do not; I will know.",
          Rank.E, 5, "things", stat=Stat.PERCEPTION),
    trial("argus", "one_face", "Look at one person properly",
          "One person you see often and have never really looked at. Not a stare. One "
          "honest look.",
          Rank.E, 1, "people"),
    trial("argus", "colours_of_one_thing", "Every colour in one small thing",
          "A leaf, a brick, your own hand. Name every distinct colour in it. There are "
          "more than you are about to guess.",
          Rank.E, 1, "things"),
    trial("argus", "the_ceiling", "Look up",
          "In three separate buildings, look at the ceiling. Nobody does this and there "
          "is often something there.",
          Rank.E, 3, "ceilings"),
    trial("argus", "ask_once", "Ask somebody how they actually are",
          "Once, ask a person you see often and wait through the first answer for the "
          "second one.",
          Rank.D, 1, "conversations"),
    trial("argus", "what_changed", "What changed on your street",
          "Something has, this month. A shop, a tree, a window, a person. Find one thing "
          "and know when it happened.",
          Rank.D, 1, "changes"),
    trial("argus", "the_slow_route", "Walk one route at half speed",
          "A route you know, taken deliberately slowly, once. Speed is the main thing "
          "that stops people seeing.",
          Rank.D, 1, "journeys"),
    trial("argus", "listen_whole", "One song, listened to and nothing else",
          "Sit down. Play it. Do nothing else at all until it ends. You have not done "
          "this in some years.",
          Rank.D, 1, "songs"),
    trial("argus", "read_the_room", "Name what everybody wants",
          "In one room with other people in it, work out what each of them is trying to "
          "get. You will be wrong about somebody. Notice that too.",
          Rank.D, 1, "rooms"),
    trial("argus", "hour_of_watching", "An hour of watching one place",
          "A window, a bench, a square. One hour, one place, no screen. Everything I know "
          "I learned this way.",
          Rank.C, 60, "minutes", stat=Stat.PERCEPTION),
    trial("argus", "the_thing_youve_ignored", "The thing you have been not-seeing",
          "There is something in your home you have stopped registering — a pile, a "
          "stain, a photograph. Look at it, and then decide about it.",
          Rank.C, 1, "things"),
    trial("argus", "twenty_details", "Twenty details in one building",
          "A station, a hall, a shop you use weekly. Twenty things you had never noticed. "
          "The last five are the real trial.",
          Rank.C, 20, "details"),
    trial("argus", "watch_the_sky_change", "Watch one sky change",
          "Sunrise or sunset, start to finish, without leaving. Fifteen minutes of it are "
          "boring. That is where it happens.",
          Rank.C, 1, "skies"),
    trial("argus", "notice_the_kind_thing", "Catch three people being kind",
          "Three separate acts of ordinary decency, seen and registered. They are "
          "constant and invisible.",
          Rank.C, 3, "acts"),
    trial("argus", "a_week_of_five", "Five things a day, for four days",
          "Twenty in total, five on each of four days. By the third day you will have "
          "started seeing before you go looking.",
          Rank.B, 20, "things", stat=Stat.PERCEPTION),
    trial("argus", "the_person_you_overlook", "The person you have been overlooking",
          "There is somebody in your week you have never really spoken to. Change that, "
          "once, properly.",
          Rank.B, 1, "people"),
    trial("argus", "draw_it", "Draw one thing badly",
          "Twenty minutes drawing something in front of you. Drawing is only looking "
          "with consequences; the result is nobody's business.",
          Rank.B, 20, "minutes"),
    trial("argus", "a_week_unwatched", "A week of noticing one person",
          "Seven days paying real attention to one person you love and have stopped "
          "seeing. Tell them one thing you noticed at the end of it.",
          Rank.A, 7, "days", stat=Stat.PERCEPTION, stat_amount=2),
    trial("argus", "map_your_mile", "Map the mile around you",
          "Walk it over a week and draw the map from memory: what is where, who is "
          "where, what has changed. You live there. You should know it.",
          Rank.A, 1, "maps"),

    # -- Athena 雅典娜: the craft --------------------------------------------
    trial("athena", "learn_one_word", "One word you have been faking",
          "There is a term you nod along to. Look it up properly, today, and be able to "
          "define it out loud.",
          Rank.E, 1, "words"),
    trial("athena", "read_the_manual", "Read the actual instructions",
          "For one thing you own and use wrong. Ten minutes. You will find at least one "
          "feature you did not know about.",
          Rank.E, 10, "minutes"),
    trial("athena", "sharpen_something", "Sharpen, oil, or tighten one tool",
          "A knife, a hinge, a bicycle, a keyboard. Tools that are maintained are tools "
          "that get used.",
          Rank.E, 1, "tools"),
    trial("athena", "one_shortcut", "Learn one shortcut properly",
          "In software you use daily, learn one keystroke that saves you a movement. Use "
          "it five times so it sticks.",
          Rank.E, 5, "uses"),
    trial("athena", "plan_before_doing", "Five minutes of planning first",
          "Before the next thing you were going to blunder into, sit for five minutes "
          "and decide the order. I back the clever heroes; this is why.",
          Rank.E, 5, "minutes"),
    trial("athena", "one_thing_made", "One thing, made by hand",
          "Make something. Badly is expected. A meal from nothing, a shelf, a drawing, a "
          "repair — the requirement is that it did not exist this morning and does now.",
          Rank.D, 1, "things"),
    trial("athena", "mend_dont_replace", "Mend one thing you would have replaced",
          "A seam, a handle, a cable, a chipped bowl. Badly mended is still mended.",
          Rank.D, 1, "repairs"),
    trial("athena", "watch_someone_good", "Watch somebody excellent, on purpose",
          "Twenty minutes watching a person who is very good at a craft — any craft — "
          "with the intent of stealing something.",
          Rank.D, 20, "minutes"),
    trial("athena", "one_page_of_notes", "Take notes on one thing you know",
          "One page, written out, on something you can already do. You will find the hole "
          "in it immediately.",
          Rank.D, 1, "pages"),
    trial("athena", "the_second_draft", "Do one thing twice",
          "Anything you made or wrote today: do it again, better. The first attempt is "
          "never the work; it is the research.",
          Rank.D, 1, "second attempts"),
    trial("athena", "learn_the_tool", "Learn the tool you use every day",
          "Half an hour on something you have used for years without ever reading about "
          "— the software, the knife, the instrument, the language. You are almost "
          "certainly using it at a quarter of it.",
          Rank.C, 30, "minutes", stat=Stat.INTELLIGENCE),
    trial("athena", "the_strategy_not_the_effort", "Solve it by thinking, not working",
          "One task you have been grinding at. Spend twenty minutes finding a cleverer "
          "way instead of another hour of the same way.",
          Rank.C, 1, "tasks"),
    trial("athena", "make_for_someone", "Make something for one other person",
          "It must be made rather than bought, and given rather than kept. The making is "
          "half; the giving is the other half.",
          Rank.C, 1, "gifts"),
    trial("athena", "three_sessions", "Three sessions on one craft",
          "The same skill, three separate times. Skills are not learned in one sitting; "
          "they are learned in the gaps between sittings.",
          Rank.C, 3, "sessions"),
    trial("athena", "teach_the_basics", "Teach somebody the first step",
          "Of a thing you can do and they cannot. Half an hour. You will discover what "
          "you actually understand.",
          Rank.C, 1, "lessons"),
    trial("athena", "the_hard_technique", "The technique you have avoided",
          "Every craft has one. Spend an hour on the part you have been routing around "
          "for a year.",
          Rank.B, 60, "minutes", stat=Stat.INTELLIGENCE),
    trial("athena", "finish_to_a_standard", "Finish one thing properly",
          "Take something you made to eighty per cent and take it to done — the sanding, "
          "the edit, the tidy-up nobody sees. That last fifth is the whole craft.",
          Rank.B, 1, "things", penalty_exp=100),
    trial("athena", "show_it_to_someone_who_knows", "Show your work to somebody better",
          "Find a person who can actually judge it and ask them what is wrong with it. "
          "Then listen without explaining yourself.",
          Rank.B, 1, "critiques"),
    trial("athena", "a_week_of_the_craft", "A week at one craft",
          "Seven days, some work on the same skill each day, however little. This is how "
          "everything I patronise was ever made.",
          Rank.A, 7, "days", stat=Stat.INTELLIGENCE, stat_amount=2),
    trial("athena", "make_the_ambitious_thing", "Make the thing you think is beyond you",
          "You have had it in mind for months. A week. Make a bad version of it rather "
          "than no version of it.",
          Rank.A, 1, "things"),

    # -- Heracles 赫拉克勒斯: the list ----------------------------------------
    trial("heracles", "one_small_task", "The two-minute thing",
          "The task you have been carrying for a fortnight that takes two minutes. Do it "
          "now and notice how little it cost.",
          Rank.E, 1, "tasks"),
    trial("heracles", "write_the_list", "Write the list",
          "Everything you are avoiding, in one place, unsorted. The list is shorter than "
          "the dread of the list. It always is.",
          Rank.E, 1, "lists"),
    trial("heracles", "one_email", "The message you have not sent",
          "Send it. Three lines is a fine length for a thing that has been sitting on you "
          "for a month.",
          Rank.E, 1, "messages"),
    trial("heracles", "carry_it", "Ten minutes carrying something heavy",
          "Shopping, water, a bag, a child, your own body up a hill. Ten minutes under "
          "load. None of my labours were more complicated than this.",
          Rank.E, 10, "minutes"),
    trial("heracles", "clear_one_surface", "Clear one surface entirely",
          "A desk, a table, a chair that has become a shelf. Empty it. Ten minutes.",
          Rank.E, 1, "surfaces"),
    trial("heracles", "the_list", "Write the list, then take one off it",
          "Every task you have been avoiding, written down in one place. Then do the "
          "smallest one. The list is not the trial; the list is how you find out how "
          "short the trial is.",
          Rank.D, 1, "tasks", stat=Stat.STRENGTH),
    trial("heracles", "the_call_you_dread", "Make the call you have been dreading",
          "The dentist, the bank, the relative, the landlord. One call. It will take "
          "eight minutes and you have spent longer than that dreading it.",
          Rank.D, 1, "calls"),
    trial("heracles", "three_off_the_list", "Three off the list in one sitting",
          "Small ones. Speed is the point: momentum is the only trick I know.",
          Rank.D, 3, "tasks"),
    trial("heracles", "the_stables", "Half an hour on the worst room",
          "You know which one. I cleaned stables that had not been touched in thirty "
          "years; I diverted a river to do it. You may use a bin bag.",
          Rank.D, 30, "minutes"),
    trial("heracles", "one_form", "Fill in the form",
          "The tax thing, the application, the claim, the renewal. Start it, at least. "
          "Started is a different country from not started.",
          Rank.D, 1, "forms"),
    trial("heracles", "the_oldest_item", "The oldest thing on the list",
          "Not the easiest — the oldest. The one that has been there so long it has "
          "stopped looking like a task and started looking like furniture.",
          Rank.C, 1, "tasks"),
    trial("heracles", "an_hour_of_the_backlog", "One hour, straight at the backlog",
          "A timer, the list, no music with words. One hour. You will not finish it and "
          "you will finish more than you expect.",
          Rank.C, 60, "minutes"),
    trial("heracles", "carry_the_shopping", "Carry it all in one trip",
          "The whole load, one journey, no complaints. A small labour, but a labour.",
          Rank.C, 1, "trips", stat=Stat.STRENGTH),
    trial("heracles", "help_with_the_heavy", "Help somebody move something heavy",
          "A sofa, a delivery, a move, a garden. Offer before you are asked; that is the "
          "part that counts.",
          Rank.C, 1, "times"),
    trial("heracles", "five_off_the_list", "Five in one day",
          "From the list you wrote. By the fourth you will be looking for more, which is "
          "the state I am trying to get you into.",
          Rank.C, 5, "tasks"),
    trial("heracles", "the_thing_with_consequences", "The one with a deadline you have passed",
          "There is a task whose lateness is now its own problem. Deal with it, late, "
          "which is better than never and cheaper than next week.",
          Rank.B, 1, "tasks", penalty_exp=100),
    trial("heracles", "the_whole_room", "One room, entirely finished",
          "Not tidied — finished. Everything in it either belongs there or is gone. Two "
          "days if you need them.",
          Rank.B, 1, "rooms"),
    trial("heracles", "carry_something_far", "Carry a real load a real distance",
          "A rucksack with weight in it, an hour of walking. This is the whole of "
          "strength training in one sentence and it is free.",
          Rank.B, 60, "minutes", stat=Stat.STRENGTH),
    trial("heracles", "clear_the_list", "Empty the list",
          "All of it. A week. When you are done, write the next one — that is not a "
          "punishment, it is what having a life consists of.",
          Rank.A, 1, "lists", stat=Stat.STRENGTH, stat_amount=2),
    trial("heracles", "the_labour_you_owe_yourself", "The labour nobody set you",
          "The one thing you would be proudest to have finished this year. A week on it, "
          "starting today, whether or not that is enough time.",
          Rank.A, 7, "days"),

    # -- Sisyphus 薛西弗斯: beginning again -----------------------------------
    trial("sisyphus", "one_rep", "One repetition of the thing you quit",
          "Not the habit back. Not the streak. One repetition, today, and then you may "
          "stop again.",
          Rank.E, 1, "attempts"),
    trial("sisyphus", "open_the_file", "Open it. That is all.",
          "The document, the app, the instrument, the drawer. Open it, look at it for one "
          "minute, close it. Starting is a separate skill from doing.",
          Rank.E, 1, "minutes"),
    trial("sisyphus", "smallest_version", "The smallest possible version",
          "One press-up. One sentence. One phone call's worth. Whatever it is, do a "
          "version so small it is embarrassing.",
          Rank.E, 1, "attempts"),
    trial("sisyphus", "put_it_where_you_see_it", "Leave the thing out",
          "The guitar out of the case, the book on the pillow, the shoes by the door. "
          "Half of beginning again is logistics.",
          Rank.E, 1, "things"),
    trial("sisyphus", "forgive_the_gap", "Write down when you stopped, and start",
          "One line: what you stopped and roughly when. No explanation. Then do one "
          "minute of it.",
          Rank.E, 1, "lines"),
    trial("sisyphus", "twice_running", "The same thing, two days running",
          "Anything, as long as it is the same on both days and neither day is easy. The "
          "second one is the entire trial. The first is just how you get to it.",
          Rank.D, 2, "days"),
    trial("sisyphus", "after_the_break", "Restart within a day of stopping",
          "Miss one, then do the next one anyway. Missing twice is what ends things; "
          "missing once is just Tuesday.",
          Rank.D, 1, "restarts"),
    trial("sisyphus", "the_same_hour", "The same hour, twice",
          "One small thing at roughly the same time on two days. The clock is a better "
          "ally than motivation.",
          Rank.D, 2, "days"),
    trial("sisyphus", "half_of_what_you_planned", "Do half of what you planned",
          "Deliberately. Plan a session and do fifty per cent of it, on purpose, without "
          "guilt. Half is a rate you can sustain.",
          Rank.D, 1, "sessions"),
    trial("sisyphus", "one_more_after_failing", "One more after it went badly",
          "Straight after something goes wrong today, do one small thing anyway. The "
          "stone rolls back; that is the arrangement.",
          Rank.D, 1, "attempts"),
    trial("sisyphus", "three_days_running", "Three days running",
          "Same thing, three days, no gaps. Day two is the hard one. Everyone expects it "
          "to be day three.",
          Rank.C, 3, "days"),
    trial("sisyphus", "the_thing_you_restart_yearly", "The one you begin every January",
          "You know the one. Begin it now instead, in the middle of a month, with no "
          "ceremony at all.",
          Rank.C, 1, "beginnings"),
    trial("sisyphus", "shrink_it_till_it_sticks", "Shrink it until you cannot miss",
          "Take the habit you keep failing and cut it to a tenth. Do the tenth for three "
          "days. Sustainable is not the same as impressive.",
          Rank.C, 3, "days"),
    trial("sisyphus", "start_badly_on_purpose", "Begin without preparing",
          "No setup, no research, no perfect conditions. Begin the thing badly, today, in "
          "whatever state you are in.",
          Rank.C, 1, "beginnings"),
    trial("sisyphus", "the_dropped_conversation", "Pick up the dropped thread",
          "A friendship, a message, a plan that went quiet because you let it. Say "
          "something. Not an apology — a continuation.",
          Rank.C, 1, "threads"),
    trial("sisyphus", "four_days_unbroken", "Four days, unbroken",
          "Same thing, four days. By now you will have had a genuinely bad day in the "
          "middle of it, which is the only part I am watching.",
          Rank.B, 4, "days"),
    trial("sisyphus", "restart_the_big_one", "Restart the thing you gave up on years ago",
          "Not for good. For four days. You are allowed to abandon it again afterwards, "
          "and you may find you do not.",
          Rank.B, 4, "days", penalty_exp=100),
    trial("sisyphus", "the_boring_middle", "Do it on the day you least want to",
          "Wait for the day you would obviously skip. Do it that day. That is the entire "
          "difference between people who keep things and people who do not.",
          Rank.B, 1, "days"),
    trial("sisyphus", "a_week_from_the_bottom", "Seven days from the bottom of the hill",
          "Same thing, every day, a week. Start from wherever you actually are rather "
          "than where you were when you were good at it.",
          Rank.A, 7, "days"),
    trial("sisyphus", "thirty_days_of_one_minute", "A fortnight of one minute",
          "One minute of the same thing, every day, for fourteen days. Nothing about "
          "this is impressive except that almost nobody does it.",
          Rank.A, 14, "days", stat=Stat.STRENGTH, stat_amount=2),

    # -- Milo of Croton 米洛: a little more than last time --------------------
    trial("milo", "ten_slow", "Ten repetitions, slowly",
          "Three seconds down, three back. The same ten reps you would rattle off in "
          "twenty seconds, made to take a minute. Tempo is free weight.",
          Rank.E, 10, "reps"),
    trial("milo", "one_more_than_last_time", "One more than last time",
          "Whatever your usual set is, add a single repetition. One. The whole method "
          "fits in this sentence.",
          Rank.E, 1, "reps"),
    trial("milo", "hold_it", "Hold a position for sixty seconds",
          "A plank, a hang, a wall sit, a heavy bag at arm's length. One minute. Time "
          "under load is the currency.",
          Rank.E, 60, "seconds"),
    trial("milo", "write_down_the_number", "Write down what you lifted",
          "The weight, the reps, the time. Untracked training is just exercise; I was "
          "counting for four years.",
          Rank.E, 1, "entries"),
    trial("milo", "the_stairs_twice", "Take the stairs twice today",
          "Up, both times, on purpose. Legs carry the rest of you around; they are worth "
          "the two minutes.",
          Rank.E, 2, "flights"),
    trial("milo", "three_sets", "Three sets of one movement",
          "Press-ups, squats, rows, carries — one movement, three sets, in a single "
          "session. Simple beats varied at the start.",
          Rank.D, 3, "sets", stat=Stat.STRENGTH),
    trial("milo", "push_pull_legs", "One push, one pull, one squat",
          "Three movements, one session. That is a whole body and it takes twenty "
          "minutes.",
          Rank.D, 3, "movements"),
    trial("milo", "carry_for_distance", "Carry something heavy two hundred paces",
          "Two bags, a crate, a child. Two hundred paces without setting it down. Nothing "
          "in a gym is more useful than this.",
          Rank.D, 200, "paces"),
    trial("milo", "the_full_range", "Ten repetitions, all the way down",
          "Half repetitions are a way of lying to yourself about the number. Ten honest "
          "ones, slower than you want to.",
          Rank.D, 10, "reps"),
    trial("milo", "eat_the_protein", "Eat like somebody who trains",
          "One day where every meal has real protein in it. You cannot build a bull out "
          "of nothing.",
          Rank.D, 1, "days"),
    trial("milo", "two_sessions", "Two sessions in three days",
          "Not one heroic session. Two ordinary ones with a rest between them. The rest "
          "is where you get stronger; the session only asks for it.",
          Rank.C, 2, "sessions", stat=Stat.STRENGTH),
    trial("milo", "add_the_smallest_increment", "Add the smallest amount you can",
          "The next plate, the next band, the next notch, one more rep on every set. "
          "Small enough that it is not a decision.",
          Rank.C, 1, "increments"),
    trial("milo", "learn_one_lift", "Learn one movement properly",
          "Half an hour on the form of a single lift — filmed, watched, corrected. Twenty "
          "years of bad squats is a long time.",
          Rank.C, 30, "minutes"),
    trial("milo", "the_neglected_half", "Train the half you skip",
          "Everybody has one: legs, back, the left side, the mobility work. One session "
          "on it. It is skipped because it is unglamorous, not because it is optional.",
          Rank.C, 1, "sessions"),
    trial("milo", "sleep_for_the_lift", "Eight hours, twice",
          "Two nights of real sleep in this window. You do not grow in the gym. Nobody "
          "believes this until they try the alternative for a year.",
          Rank.C, 2, "nights", stat=Stat.VITALITY),
    trial("milo", "three_sessions_one_week", "Three sessions in one week",
          "The actual rate at which people get strong. Not four, not six — three, every "
          "week, for the rest of your life.",
          Rank.B, 3, "sessions", stat=Stat.STRENGTH),
    trial("milo", "the_log_book", "Log every session for a week",
          "Weight, reps, how it felt. A week of honest entries will tell you more than a "
          "year of guessing.",
          Rank.B, 7, "days"),
    trial("milo", "beat_last_month", "Beat what you did a month ago",
          "One lift, one number, exceeded. If you cannot find the number because you did "
          "not write it down, that is the lesson and you may start writing.",
          Rank.B, 1, "lifts", penalty_exp=100),
    trial("milo", "a_month_of_carrying", "A fortnight, three sessions a week",
          "Six sessions in fourteen days, progressing every time. This is the calf, and "
          "it is starting to get heavy.",
          Rank.A, 6, "sessions", stat=Stat.STRENGTH, stat_amount=2),
    trial("milo", "the_bull", "Carry the bull",
          "Compare today's numbers with the ones from when you started. If the gap is not "
          "yet embarrassing, keep going until it is. Then come back and tell me.",
          Rank.S, 1, "comparisons", stat=Stat.STRENGTH, stat_amount=3),

    # -- Asclepius 阿斯克勒庇俄斯: mending -------------------------------------
    trial("asclepius", "a_glass_of_water", "A glass of water, now",
          "Not eight. One, in the next few minutes. A great deal of what people bring me "
          "is this.",
          Rank.E, 1, "glasses"),
    trial("asclepius", "the_part_that_hurts", "Ten minutes on the part that hurts",
          "The shoulder, the back, the knee, the wrist — the one that has been "
          "complaining for months. Ten minutes of stretching it, resting it, or reading "
          "about it properly.",
          Rank.E, 10, "minutes"),
    trial("asclepius", "open_a_window", "Open a window for ten minutes",
          "Wherever you have been sitting all day. The air in there is older than you "
          "think.",
          Rank.E, 10, "minutes"),
    trial("asclepius", "the_small_wound", "Treat the small thing",
          "The cut, the blister, the tooth, the ache you have been ignoring because it is "
          "minor. Minor is when it is cheap to fix.",
          Rank.E, 1, "treatments"),
    trial("asclepius", "put_the_screen_down_early", "Screens down thirty minutes before bed",
          "Once. I am told this is the least popular instruction anybody gives, which is "
          "how I know it works.",
          Rank.E, 30, "minutes"),
    trial("asclepius", "an_hour_earlier", "An hour earlier, once",
          "One night, go to bed an hour before you normally would. Not a new regime. One "
          "night. Most of what people bring me would have been solved by this.",
          Rank.D, 1, "nights", stat=Stat.VITALITY),
    trial("asclepius", "ten_minutes_of_stretching", "Ten minutes of moving slowly",
          "Stretching, mobility, whatever you call it. Slow, deliberate, unimpressive. "
          "Bodies that are never taken through their range lose it.",
          Rank.D, 10, "minutes"),
    trial("asclepius", "eat_before_you_are_starving", "Eat at a sensible hour",
          "One day where you do not skip until you are ravenous and then eat badly. Plan "
          "one meal in advance; that is all this is.",
          Rank.D, 1, "days"),
    trial("asclepius", "the_appointment", "Book the appointment",
          "The doctor, the dentist, the optician, the physio. Book it — you do not have "
          "to attend it inside this window, only stop postponing it.",
          Rank.D, 1, "appointments"),
    trial("asclepius", "walk_after_eating", "Walk after a meal",
          "Ten minutes on your feet after eating, twice. An old remedy, still the best "
          "value in medicine.",
          Rank.D, 2, "walks"),
    trial("asclepius", "three_nights", "Three nights, properly slept",
          "Same rough hour, three nights, no heroics. Sleep is the only treatment I have "
          "that works on everything.",
          Rank.C, 3, "nights", stat=Stat.VITALITY),
    trial("asclepius", "the_thing_you_googled", "Learn the truth about your own complaint",
          "You have half-read about it at two in the morning. Spend twenty minutes on a "
          "real source instead, in daylight.",
          Rank.C, 20, "minutes"),
    trial("asclepius", "a_day_without_the_crutch", "One day without the thing you lean on",
          "The coffee after four, the drink in the evening, the scroll in bed. One day. "
          "Notice what it was holding up.",
          Rank.C, 1, "days"),
    trial("asclepius", "move_every_day", "Some movement on three days",
          "Not training. Movement: a walk, a stretch, a swim, stairs. Three days out of "
          "three.",
          Rank.C, 3, "days"),
    trial("asclepius", "tell_somebody_the_symptom", "Say it out loud to one person",
          "The thing you have not mentioned to anybody. Saying it is the first half of "
          "every recovery I have ever presided over.",
          Rank.C, 1, "conversations"),
    trial("asclepius", "a_week_of_sleep", "A week of going to bed on time",
          "Seven nights, the same rough hour. It will be dull, and by the fifth day you "
          "will be a different person.",
          Rank.B, 7, "nights", stat=Stat.VITALITY),
    trial("asclepius", "attend_the_appointment", "Attend the thing you booked",
          "Go. Whatever they find, it is smaller today than next year. I was killed for "
          "insisting on this sort of thing.",
          Rank.B, 1, "appointments", penalty_exp=100),
    trial("asclepius", "a_dry_stretch", "Four days off the substance",
          "Whatever it is — alcohol, nicotine, sugar, the screen at midnight. Four days "
          "is long enough to feel the shape of it.",
          Rank.B, 4, "days"),
    trial("asclepius", "the_full_fortnight", "A fortnight of the boring things",
          "Sleep, water, movement, food at reasonable hours, fourteen days. There is no "
          "secret. There has never been a secret.",
          Rank.A, 14, "days", stat=Stat.VITALITY, stat_amount=2),
    trial("asclepius", "fix_the_chronic_thing", "Begin properly on the long-standing thing",
          "The back, the sleep, the tooth, the knee you have had for years. A week of "
          "actually addressing it — appointments, exercises, whatever it takes.",
          Rank.A, 7, "days"),

    # -- Mnemosyne 謨涅摩敘涅: keeping -----------------------------------------
    trial("mnemosyne", "what_you_ate", "What did you eat yesterday?",
          "Write it down before you check anything. Most people cannot do this, which "
          "tells you what a day is worth unrecorded.",
          Rank.E, 1, "recollections"),
    trial("mnemosyne", "one_line_a_day", "One line, before sleeping",
          "A single sentence about the day, written down. In ten years the unimportant "
          "days are the ones you will want back.",
          Rank.E, 1, "lines"),
    trial("mnemosyne", "name_the_song", "Find out what it was",
          "The song, the film, the book you half-remember. Track it down and write the "
          "name somewhere it will keep.",
          Rank.E, 1, "names"),
    trial("mnemosyne", "one_photograph", "Take one photograph of something ordinary",
          "Not the view. The kitchen, the commute, the desk as it actually is. Ordinary "
          "is what disappears.",
          Rank.E, 1, "photographs"),
    trial("mnemosyne", "write_the_number_down", "Learn one number by heart",
          "A phone number, an address, a date that matters. Batteries die; you do not, "
          "yet.",
          Rank.E, 1, "numbers"),
    trial("mnemosyne", "by_heart", "Four lines, by heart",
          "A verse, a passage, a set of directions. Four lines held in your own head "
          "where no battery is required.",
          Rank.D, 4, "lines", stat=Stat.INTELLIGENCE),
    trial("mnemosyne", "ask_an_older_person", "Ask somebody older for one story",
          "One story you have never heard, from somebody who will not always be there to "
          "tell it. Write down the bones of it afterwards.",
          Rank.D, 1, "stories"),
    trial("mnemosyne", "the_old_photographs", "Twenty minutes in the old photographs",
          "Yours or your family's. Name the people in three of them while there is still "
          "somebody to ask.",
          Rank.D, 20, "minutes"),
    trial("mnemosyne", "write_it_down_immediately", "Catch one idea before it goes",
          "The next good thought you have — in the shower, on the walk, half asleep. "
          "Write it down within a minute. They do not come back.",
          Rank.D, 1, "ideas"),
    trial("mnemosyne", "the_week_in_review", "What actually happened this week",
          "Ten minutes reconstructing your own week from memory, written. You will find "
          "two whole days missing.",
          Rank.D, 1, "reviews"),
    trial("mnemosyne", "three_days_of_lines", "Three days, one line each",
          "The smallest possible diary, kept for three days. Almost everybody who keeps "
          "one for a year started with three days.",
          Rank.C, 3, "days"),
    trial("mnemosyne", "learn_a_poem", "One poem, whole",
          "Short is fine. Learn it well enough to say it with your eyes closed. You are "
          "buying something nobody can take off you.",
          Rank.C, 1, "poems", stat=Stat.INTELLIGENCE),
    trial("mnemosyne", "the_letter_to_the_future", "Write to yourself in a year",
          "What you are worried about, what you want, what today was like. Put it "
          "somewhere you will find it.",
          Rank.C, 1, "letters"),
    trial("mnemosyne", "recover_the_lost_skill", "Do the thing you used to be able to do",
          "The language, the instrument, the sport. One session. Memory is a muscle in "
          "exactly the way people say it is not.",
          Rank.C, 1, "sessions"),
    trial("mnemosyne", "record_a_voice", "Record somebody's voice",
          "Ask permission, then record a person you love talking about anything at all. "
          "One minute. You will understand later.",
          Rank.C, 1, "recordings"),
    trial("mnemosyne", "a_week_of_lines", "A week of one line a day",
          "Seven days, seven sentences. The gaps in it will tell you which days you were "
          "not really present for.",
          Rank.B, 7, "days"),
    trial("mnemosyne", "the_family_thing", "Write down one family story properly",
          "A page. The version you were told, with the names and the dates you can "
          "verify. Nobody else is going to.",
          Rank.B, 1, "pages", stat=Stat.INTELLIGENCE),
    trial("mnemosyne", "twenty_lines_by_heart", "Twenty lines, held",
          "A long poem, a speech, a passage of scripture, a set of lyrics. Twenty lines. "
          "It takes four days and lasts decades.",
          Rank.B, 20, "lines"),
    trial("mnemosyne", "a_fortnight_of_keeping", "Fourteen days, kept",
          "One line every day for a fortnight, with no missing days papered over "
          "afterwards. Honest gaps are allowed; invented entries are not.",
          Rank.A, 14, "days", stat=Stat.INTELLIGENCE, stat_amount=2),
    trial("mnemosyne", "interview_someone", "Sit somebody down and ask them everything",
          "An hour, recorded, with a person whose life you only know the outline of. "
          "This is the single most valuable thing on my list.",
          Rank.A, 60, "minutes"),

    # -- Atalanta 亞特蘭妲: not stopping ---------------------------------------
    trial("atalanta", "two_at_a_time", "Take the stairs two at a time",
          "Once, wherever you next meet stairs. It is faster and it is more fun and it "
          "costs nothing.",
          Rank.E, 1, "flights"),
    trial("atalanta", "one_minute_fast", "One minute at your limit",
          "Run, cycle, climb stairs, skip — one minute of genuine effort. You will be "
          "surprised how long a minute is.",
          Rank.E, 60, "seconds"),
    trial("atalanta", "phone_in_another_room", "Twenty minutes with the phone elsewhere",
          "Somebody rolled gold across my track once and I have never stopped hearing "
          "about it. Put the apples in another room.",
          Rank.E, 20, "minutes"),
    trial("atalanta", "once_quicker", "Once, quicker than usual",
          "A route you walk often, done faster than you normally do it. Once. You do not "
          "have to enjoy it.",
          Rank.E, 1, "journeys"),
    trial("atalanta", "outside_before_the_screen", "Outdoors before the first screen",
          "One morning, get outside before you look at anything with a battery in it.",
          Rank.E, 1, "mornings"),
    trial("atalanta", "no_apples", "Twenty minutes, no apples",
          "Twenty minutes of moving with the phone away — pocket, bag, another room.",
          Rank.D, 20, "minutes", stat=Stat.AGILITY),
    trial("atalanta", "six_sprints", "Six short efforts",
          "Six bursts of about twenty seconds, hard, with rest between. Twelve minutes "
          "total. There is no cheaper way to get fitter.",
          Rank.D, 6, "efforts"),
    trial("atalanta", "beat_the_lift", "Beat the lift up the stairs",
          "Race it once, on foot. Childish, unquestionably. I was raised by a bear.",
          Rank.D, 1, "races"),
    trial("atalanta", "chase_something", "Chase something, badly",
          "A ball, a dog, a child, a bus you might miss. Move at speed for a reason other "
          "than exercise.",
          Rank.D, 1, "chases"),
    trial("atalanta", "the_hunt", "Find one thing you have been putting off finding",
          "The lost document, the right part, the cheapest option, the person's new "
          "address. Track it down; I hunted the boar the others were still discussing.",
          Rank.D, 1, "hunts"),
    trial("atalanta", "twenty_minutes_running", "Twenty minutes of running",
          "Slowly is fine. Walk-run is fine. Twenty minutes with your feet leaving the "
          "ground more than usual.",
          Rank.C, 20, "minutes", stat=Stat.AGILITY),
    trial("atalanta", "two_efforts_this_week", "Two sessions of real effort",
          "Two separate occasions where you were properly out of breath. Not one. Two is "
          "where it starts to be a habit rather than an anecdote.",
          Rank.C, 2, "sessions"),
    trial("atalanta", "the_race_you_did_not_enter", "Enter something",
          "A race, a class, a game, a competition. Sign up. Entering is the trial; the "
          "event is your own business.",
          Rank.C, 1, "entries"),
    trial("atalanta", "an_hour_undistracted", "One hour of undivided work",
          "One task, one hour, nothing else open. You stop for nothing gold-coloured.",
          Rank.C, 60, "minutes"),
    trial("atalanta", "outrun_your_own_time", "Beat your own time",
          "Any route, any distance you have done before. Beat it, by a second. Only "
          "yourself; I never cared about anybody else's pace.",
          Rank.C, 1, "attempts"),
    trial("atalanta", "three_sessions_this_week", "Three efforts in a week",
          "Three times out of breath in seven days. That is the actual dose. Everything "
          "beyond it is preference.",
          Rank.B, 3, "sessions", stat=Stat.AGILITY),
    trial("atalanta", "five_kilometres", "Five kilometres, however slowly",
          "Run, walk, or a mix. Five. Take as long as you like; there is no gold on this "
          "track.",
          Rank.B, 5, "kilometres"),
    trial("atalanta", "a_day_without_the_apples", "A whole day off the feed",
          "One day with no infinite scroll of any kind. Not a detox, not a philosophy. "
          "One day of noticing what you reach for.",
          Rank.B, 1, "days"),
    trial("atalanta", "a_week_of_moving_fast", "A week with speed in it",
          "Seven days, four of them containing some genuine effort. This is the week that "
          "makes the next month easier.",
          Rank.A, 4, "sessions", stat=Stat.AGILITY, stat_amount=2),
    trial("atalanta", "the_distance_that_scares_you", "The distance you do not think you can do",
          "Whatever it is for you — five kilometres, ten, the hill, the swim. A "
          "fortnight to get there. Finish it however you have to.",
          Rank.A, 1, "attempts"),

    # -- Hestia 赫斯提亞: keeping the fire -------------------------------------
    trial("hestia", "one_corner", "One corner, put right",
          "One small area of where you live, restored to how you would like it. A drawer. "
          "A shelf. The table. Not the whole room; I am not unreasonable.",
          Rank.E, 1, "corners"),
    trial("hestia", "the_washing_up", "Leave the sink empty",
          "Once, go to bed with nothing in it. A very small thing that changes the whole "
          "shape of a morning.",
          Rank.E, 1, "evenings"),
    trial("hestia", "one_meal_at_a_table", "One meal at a table",
          "Sitting down, at a table, with nothing playing. One meal. It is the oldest "
          "thing I ask and the one people find hardest.",
          Rank.E, 1, "meals"),
    trial("hestia", "light_something", "Light a candle, or a lamp you never use",
          "Change the light in one room for one evening. Householders kept a fire for me "
          "for a reason; it was not only warmth.",
          Rank.E, 1, "evenings"),
    trial("hestia", "throw_five_things_away", "Five things gone",
          "Five objects out of the house — bin, charity, given away. Five is small enough "
          "to start and large enough to feel.",
          Rank.E, 5, "things"),
    trial("hestia", "make_the_bed", "Make the bed, three days running",
          "Three mornings. There is a great deal of nonsense written about this and it is "
          "still worth doing.",
          Rank.D, 3, "mornings"),
    trial("hestia", "cook_one_thing", "Cook one thing from its parts",
          "Not assembled — cooked. However simple. A household that cannot feed itself is "
          "a household on a permanent emergency footing.",
          Rank.D, 1, "meals"),
    trial("hestia", "feed_somebody", "Feed one other person",
          "Anything, however plain. Hospitality was the whole of my portfolio and it "
          "costs almost nothing.",
          Rank.D, 1, "guests"),
    trial("hestia", "the_broken_thing", "Fix or discard the broken thing",
          "The one that has been broken so long it has become furniture. Either mend it "
          "this week or let it go.",
          Rank.D, 1, "things"),
    trial("hestia", "twenty_minutes_of_order", "Twenty minutes of putting away",
          "A timer, one room, no decisions about anything sentimental. Just putting things "
          "where they live.",
          Rank.D, 20, "minutes"),
    trial("hestia", "one_room_finished", "One room, actually finished",
          "Everything in it either belongs there or is gone. One room. Not the whole "
          "house — I have seen what happens when people try that.",
          Rank.C, 1, "rooms"),
    trial("hestia", "sunday_of_preparation", "An hour spent on next week",
          "Food, clothes, plans, the small logistics. An hour now buys back four later.",
          Rank.C, 60, "minutes"),
    trial("hestia", "invite_someone", "Invite somebody over",
          "Actually invite them, with a date. The house does not have to be ready. It "
          "never is; that is not what anybody comes for.",
          Rank.C, 1, "invitations"),
    trial("hestia", "three_meals_at_a_table", "Three meals at a table",
          "Three, this week, sitting down, no screen. Watch what happens to how much you "
          "eat and how much you notice.",
          Rank.C, 3, "meals", stat=Stat.VITALITY),
    trial("hestia", "the_drawer_of_shame", "The drawer, the cupboard, the box",
          "Every home has one. Empty it onto the floor, keep a third of it, and put the "
          "rest somewhere else entirely.",
          Rank.C, 1, "drawers"),
    trial("hestia", "a_week_of_the_sink", "Seven evenings, empty sink",
          "A week of going to bed with the kitchen done. Small, daily, invisible — which "
          "is the description of every important thing I do.",
          Rank.B, 7, "evenings"),
    trial("hestia", "cook_for_four", "Cook for a table of people",
          "Three or more, at your place, food you made. It will not be perfect. Nobody "
          "has ever remembered a dinner for being perfect.",
          Rank.B, 1, "dinners"),
    trial("hestia", "the_thing_you_moved_house_with", "Open the box you never unpacked",
          "It has moved with you at least once. Open it, deal with all of it, and be done.",
          Rank.B, 1, "boxes"),
    trial("hestia", "a_fortnight_of_keeping", "Fourteen days of keeping the place",
          "Sink empty, bed made, one surface clear, every day for a fortnight. Nobody "
          "will notice. You will.",
          Rank.A, 14, "days", stat=Stat.VITALITY, stat_amount=2),
    trial("hestia", "make_it_yours", "Change one room so that it is yours",
          "Paint, rearrange, hang the pictures that have been leaning against the wall "
          "for a year. A week. Live somewhere that looks like somebody lives there.",
          Rank.A, 1, "rooms"),

)
