"""
Supplemental event ingestion from deeper scraping of funcheap, dothebay, and lu.ma.
Adds events discovered from thorough web search crawls of these platforms.
"""
import pandas as pd
from datetime import datetime

CSV_PATH = "event_data.csv"
NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

NEW_EVENTS = [
    # ===================== FUNCHEAP EVENTS =====================
    # Source: sf.funcheap.com daily pages

    # Mar 7
    {
        "title": "FREE San Francisco Black History Month Comedy Festival 2026",
        "description": "Celebrate Black History Month with live stand-up at The Function (1414 Market St), San Francisco's first Black-owned comedy club. Featuring the Bay Area's best rising Black comedians with rotating lineups, 4-5 pro comedians performing 70-90 minutes. Free with RSVP for first 40 people, two drink minimum.",
        "start_time": "2026-03-07 19:00:00",
        "end_time": "2026-03-07 22:00:00",
        "source_url": "https://sf.funcheap.com/free-san-francisco-black-history-month-comedy-festival-2026-6/",
        "tags": '["Comedy", "Free", "Black History Month", "Stand-up"]',
        "category": "comedy",
        "location": "San Francisco, CA"
    },
    {
        "title": "FREE Oakland Black History Comedy Night 2026 (Final Weekend)",
        "description": "Six nights of free comedy in Uptown Oakland hosted by Bryant Hicks. Final weekend of the Black History Month comedy celebration.",
        "start_time": "2026-03-07 19:00:00",
        "end_time": "2026-03-07 22:30:00",
        "source_url": "https://sf.funcheap.com/free-oakland-black-history-comedy-night-2026/",
        "tags": '["Comedy", "Free", "Black History Month", "Oakland"]',
        "category": "comedy",
        "location": "Oakland, CA"
    },
    {
        "title": "HellaSecret Speakeasy Comedy Show & Cocktail Night (Oakland)",
        "description": "Pop-up live comedy show at a secret location in the Bay Area. Get an email with the secret location after getting free tickets with code FUNCHEAP. A unique comedy and cocktail experience.",
        "start_time": "2026-03-07 19:00:00",
        "end_time": "2026-03-07 22:00:00",
        "source_url": "https://sf.funcheap.com/hellasecret-speakeasy-comedy/",
        "tags": '["Comedy", "Free", "Speakeasy", "Cocktails"]',
        "category": "comedy",
        "location": "Oakland, CA"
    },
    {
        "title": "2nd Annual Supercar Showcase at Cityline",
        "description": "The Bay Area chapter of Fast Lane Drive returns to Cityline for the 2nd Annual Supercar Showcase, featuring an incredible lineup of 50+ elite supercars in a curated exhibit. Free admission.",
        "start_time": "2026-03-07 11:00:00",
        "end_time": "2026-03-07 15:00:00",
        "source_url": "https://sf.funcheap.com/cityline-supercar-showcase/",
        "tags": '["Cars", "Free", "Exhibit", "Family"]',
        "category": "community_and_social",
        "location": "San Francisco, CA"
    },
    {
        "title": "North Beach Community Cleanup with Free Food",
        "description": "Volunteer cleanup of the North Beach neighborhood. Meet at Luke's Local (580 Green St) at 11am to grab supplies and form crews. Free food for volunteers after the cleanup.",
        "start_time": "2026-03-07 11:00:00",
        "end_time": "2026-03-07 12:30:00",
        "source_url": "https://sf.funcheap.com/north-beach-cleanup/",
        "tags": '["Volunteer", "Community", "Free", "North Beach"]',
        "category": "community_and_social",
        "location": "San Francisco, CA"
    },
    {
        "title": "Bank of America Museums On Us Free Weekend",
        "description": "Free admission for Bank of America or Merrill Lynch cardholders to six Bay Area museums and over 225 cultural institutions nationwide. First full weekend each month.",
        "start_time": "2026-03-07 09:00:00",
        "end_time": "2026-03-08 17:00:00",
        "source_url": "https://sf.funcheap.com/bank-of-america-museums-on-us/",
        "tags": '["Museum", "Free", "Art", "Culture"]',
        "category": "museum",
        "location": "San Francisco, CA"
    },
    {
        "title": "Legion of Honor – Free Saturday Admission for Bay Area Residents",
        "description": "Free general admission for Bay Area residents with valid ID or proof of residency to the Legion of Honor. Permanent collection galleries only. Advanced timed tickets required.",
        "start_time": "2026-03-07 09:30:00",
        "end_time": "2026-03-07 17:15:00",
        "source_url": "https://sf.funcheap.com/legion-of-honor-free-saturday/",
        "tags": '["Museum", "Free", "Art", "History"]',
        "category": "museum",
        "location": "San Francisco, CA"
    },

    # Mar 8
    {
        "title": "Oakland 68s FanFest at Fruitvale Village",
        "description": "If you bleed green and gold, head to the Oakland 68s' annual free FanFest at Fruitvale Village. Meet players, enjoy activities, and celebrate Oakland baseball.",
        "start_time": "2026-03-08 11:00:00",
        "end_time": "2026-03-08 16:00:00",
        "source_url": "https://sf.funcheap.com/oakland-68s-fanfest/",
        "tags": '["Sports", "Baseball", "Free", "Family"]',
        "category": "sports",
        "location": "Oakland, CA"
    },
    {
        "title": "Roller Skating at Golden Gate Park",
        "description": "Weekly Sunday roller skating party at Golden Gate Park. Bring your skates and boogie to the funky beat on wheels. A beloved Bay Area tradition.",
        "start_time": "2026-03-08 11:00:00",
        "end_time": "2026-03-08 17:00:00",
        "source_url": "https://sf.funcheap.com/roller-skating-golden-gate-park/",
        "tags": '["Sports", "Free", "Outdoor", "Fun"]',
        "category": "sports",
        "location": "San Francisco, CA"
    },

    # Mar 12
    {
        "title": "Oakland's Celebration Rally for Olympic Gold Medalist Alysa Liu",
        "description": "Oakland hosts a free community rally at Frank Ogawa Plaza to honor figure skater Alysa Liu's Olympic gold medal win. A proud celebration for the city.",
        "start_time": "2026-03-12 12:00:00",
        "end_time": "2026-03-12 13:30:00",
        "source_url": "https://sf.funcheap.com/oakland-alysa-liu-rally/",
        "tags": '["Sports", "Free", "Community", "Celebration"]',
        "category": "community_and_social",
        "location": "Oakland, CA"
    },
    {
        "title": "Level Up Thursday at Raven Bar & Lounge",
        "description": "Every Thursday night, Raven Bar & Lounge hosts a free dance party with DJ Mark Andrus playing throwback jams. No cover charge.",
        "start_time": "2026-03-12 21:00:00",
        "end_time": "2026-03-13 02:00:00",
        "source_url": "https://sf.funcheap.com/level-up-thursday-raven/",
        "tags": '["Nightlife", "Free", "Dance", "DJ"]',
        "category": "nightlife",
        "location": "San Francisco, CA"
    },

    # Mar 13
    {
        "title": "FREE St. Patrick's Day Comedy Festival (March 13-17)",
        "description": "Free with RSVP for first 50 people; two-drink minimum. A laugh-filled St. Patrick's Day celebration at The Function, San Francisco's newest comedy club. Multiple nights of stand-up comedy.",
        "start_time": "2026-03-13 19:00:00",
        "end_time": "2026-03-13 22:00:00",
        "source_url": "https://sf.funcheap.com/free-st-patricks-comedy-festival/",
        "tags": '["Comedy", "Free", "St Patricks Day", "Stand-up"]',
        "category": "comedy",
        "location": "San Francisco, CA"
    },

    # Mar 14
    {
        "title": "3rd Annual Live Cantonese Opera",
        "description": "Yerba Buena Center for the Arts presents the 3rd Annual Live Cantonese Opera on March 14-15. Featuring renowned artists from Hong Kong performing traditional Cantonese opera.",
        "start_time": "2026-03-14 14:00:00",
        "end_time": "2026-03-15 17:00:00",
        "source_url": "https://sf.funcheap.com/cantonese-opera-ybca/",
        "tags": '["Opera", "Culture", "Performance", "Chinese"]',
        "category": "theater",
        "location": "San Francisco, CA"
    },
    {
        "title": "Singing in the Park – Free Community Singing at Golden Gate Park",
        "description": "Free monthly community singing event, meeting the second Saturday of every month at Golden Gate Park. All voices and skill levels welcome.",
        "start_time": "2026-03-14 10:30:00",
        "end_time": "2026-03-14 11:30:00",
        "source_url": "https://sf.funcheap.com/singing-in-the-park/",
        "tags": '["Music", "Free", "Community", "Outdoor"]',
        "category": "community_and_social",
        "location": "San Francisco, CA"
    },
    {
        "title": "HellaFunny Olympics Comedy Show – SF vs Oakland",
        "description": "The best SF comedians go head-to-head against the best Oakland comedians in a Battle of the Bay comedy showdown. Free admission.",
        "start_time": "2026-03-14 22:00:00",
        "end_time": "2026-03-14 23:30:00",
        "source_url": "https://sf.funcheap.com/hellafunny-olympics/",
        "tags": '["Comedy", "Free", "Stand-up", "Competition"]',
        "category": "comedy",
        "location": "San Francisco, CA"
    },
    {
        "title": "Mortified Live: Embarrassing Teen Diary Storytelling (Berkeley)",
        "description": "Adults read aloud from their actual childhood journals, love letters, and other artifacts in front of total strangers. Hilarious and heartwarming.",
        "start_time": "2026-03-14 19:30:00",
        "end_time": "2026-03-14 21:30:00",
        "source_url": "https://sf.funcheap.com/mortified-live-berkeley/",
        "tags": '["Comedy", "Storytelling", "Entertainment"]',
        "category": "comedy",
        "location": "Berkeley, CA"
    },
    {
        "title": "SFMOMA Discounted Admission ($15) through April 17",
        "description": "From March 2 through April 17, 2026, SFMOMA offers discounted admission at $15, giving visitors full access at nearly half the regular price.",
        "start_time": "2026-03-14 10:00:00",
        "end_time": "2026-04-17 17:00:00",
        "source_url": "https://sf.funcheap.com/sfmoma-discount/",
        "tags": '["Museum", "Art", "Discount", "SFMOMA"]',
        "category": "museum",
        "location": "San Francisco, CA"
    },

    # Mar 15
    {
        "title": "Free Reggae in the Park: Crucial Sundays (Golden Gate Park)",
        "description": "Free reggae music at the Spreckels Temple of Music in Golden Gate Park. Part of the Sunday concert series, enjoy reggae vibes in a beautiful outdoor setting.",
        "start_time": "2026-03-15 16:30:00",
        "end_time": "2026-03-15 19:30:00",
        "source_url": "https://sf.funcheap.com/free-reggae-golden-gate-park/",
        "tags": '["Music", "Reggae", "Free", "Outdoor"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "Lindy in the Park – Free Swing Dance (Golden Gate Park)",
        "description": "Weekly free swing dance event near the de Young Museum in Golden Gate Park every sunny Sunday. All levels welcome, no partner needed.",
        "start_time": "2026-03-15 11:00:00",
        "end_time": "2026-03-15 14:00:00",
        "source_url": "https://sf.funcheap.com/lindy-in-the-park/",
        "tags": '["Dance", "Free", "Outdoor", "Swing"]',
        "category": "community_and_social",
        "location": "San Francisco, CA"
    },

    # Mar 28-29
    {
        "title": "2026 Renegade Craft Fair at Fort Mason",
        "description": "Shop from over 250 artists at Renegade San Francisco featuring the best craft designers, artists, and creatives from SF and beyond, plus food trucks. Free entry ($5 suggested donation).",
        "start_time": "2026-03-28 11:00:00",
        "end_time": "2026-03-29 17:00:00",
        "source_url": "https://sf.funcheap.com/renegade-craft-fair-fort-mason/",
        "tags": '["Art", "Market", "Shopping", "Free"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },

    # ===================== DOTHEBAY EVENTS =====================
    # Source: dothebay.com daily pages

    # Mar 7
    {
        "title": "Gogol Bordello – We Mean It, Man! Tour 2026",
        "description": "Gypsy punk legends Gogol Bordello bring their high-energy We Mean It, Man! Tour to San Francisco. Expect a wild, multi-cultural rock spectacle.",
        "start_time": "2026-03-07 20:00:00",
        "end_time": "2026-03-07 23:00:00",
        "source_url": "https://dothebay.com/events/2026/3/7/gogol-bordello-tickets",
        "tags": '["Concert", "Rock", "Live Music", "Punk"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "Sam Smith – To Be Free: San Francisco Residency",
        "description": "Grammy-winning artist Sam Smith performs their San Francisco residency 'To Be Free.' An intimate concert experience with one of pop's most powerful vocalists.",
        "start_time": "2026-03-07 20:00:00",
        "end_time": "2026-03-07 23:00:00",
        "source_url": "https://dothebay.com/events/2026/3/7/sam-smith-tickets",
        "tags": '["Concert", "Pop", "Live Music", "Residency"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "Fashion Week: One of a Kind Fashion Show at Clift Royal Sonesta",
        "description": "A one-of-a-kind fashion show at The Clift Royal Sonesta Hotel as part of SF Fashion Week. Showcasing unique designs from emerging and established designers.",
        "start_time": "2026-03-07 19:00:00",
        "end_time": "2026-03-07 22:00:00",
        "source_url": "https://dothebay.com/events/2026/3/7/fashion-week-one-of-a-kind-fashion-show-tickets",
        "tags": '["Fashion", "Show", "Design", "Nightlife"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },
    {
        "title": "Best Medicine Comedy – Bit City at Mr. Bing's",
        "description": "Weekly Saturday comedy show featuring San Francisco's best up-and-coming comedians at Mr. Bing's in Chinatown.",
        "start_time": "2026-03-07 20:00:00",
        "end_time": "2026-03-07 22:00:00",
        "source_url": "https://dothebay.com/events/2026/3/7/best-medicine-comedy-bit-city",
        "tags": '["Comedy", "Stand-up", "Weekly", "Chinatown"]',
        "category": "comedy",
        "location": "San Francisco, CA"
    },
    {
        "title": "Tenderloin Museum: The Compton's Cafeteria Riot (through Mar 28)",
        "description": "The Tenderloin Museum presents a special exhibition on the historic 1966 Compton's Cafeteria Riot, a pivotal moment in LGBTQ+ history that predated Stonewall by three years.",
        "start_time": "2026-03-07 10:00:00",
        "end_time": "2026-03-28 17:00:00",
        "source_url": "https://dothebay.com/events/2026/3/7/comptons-cafeteria-riot",
        "tags": '["Museum", "LGBTQ", "History", "Exhibition"]',
        "category": "museum",
        "location": "San Francisco, CA"
    },

    # Mar 10
    {
        "title": "The Technicolors at Bottom Of The Hill",
        "description": "The Technicolors perform live at Bottom Of The Hill, one of SF's most legendary small venues for live music.",
        "start_time": "2026-03-10 19:30:00",
        "end_time": "2026-03-10 22:30:00",
        "source_url": "https://dothebay.com/events/2026/3/10/the-technicolors-tickets",
        "tags": '["Concert", "Indie", "Live Music"]',
        "category": "live_music",
        "location": "San Francisco, CA"
    },
    {
        "title": "Alejandro Ochoa & Friends at Punch Line San Francisco",
        "description": "Comedian Alejandro Ochoa brings friends for a night of laughs at the legendary Punch Line San Francisco comedy club.",
        "start_time": "2026-03-10 19:30:00",
        "end_time": "2026-03-10 21:30:00",
        "source_url": "https://dothebay.com/events/2026/3/10/alejandro-ochoa-tickets",
        "tags": '["Comedy", "Stand-up", "Live"]',
        "category": "comedy",
        "location": "San Francisco, CA"
    },
    {
        "title": "Alex Sampson at Cafe du Nord",
        "description": "Singer-songwriter Alex Sampson performs at Cafe du Nord, one of SF's most intimate and storied music venues.",
        "start_time": "2026-03-10 20:00:00",
        "end_time": "2026-03-10 22:00:00",
        "source_url": "https://dothebay.com/events/2026/3/10/alex-sampson-tickets",
        "tags": '["Concert", "Singer-Songwriter", "Live Music"]',
        "category": "live_music",
        "location": "San Francisco, CA"
    },
    {
        "title": "We've Got Sole: Hip Hop, Hoops and the Rise of Sneaker Culture",
        "description": "Free exhibit at SF Public Library Main Branch exploring the intersection of hip hop, basketball, and sneaker culture. Running through May 15.",
        "start_time": "2026-03-07 10:00:00",
        "end_time": "2026-05-15 17:00:00",
        "source_url": "https://dothebay.com/events/2026/3/7/weve-got-sole",
        "tags": '["Exhibition", "Free", "Hip Hop", "Culture"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },

    # Mar 11
    {
        "title": "Holly Bowling at The Guild Theatre",
        "description": "Pianist Holly Bowling performs her acclaimed interpretations of Grateful Dead and Phish music at The Guild Theatre in Menlo Park.",
        "start_time": "2026-03-11 20:00:00",
        "end_time": "2026-03-11 22:30:00",
        "source_url": "https://dothebay.com/events/2026/3/11/holly-bowling-tickets",
        "tags": '["Concert", "Piano", "Live Music", "Grateful Dead"]',
        "category": "concert",
        "location": "Menlo Park, CA"
    },
    {
        "title": "Rick Estrin & The Nightcats at Yoshi's Oakland",
        "description": "Blues harmonica master Rick Estrin and The Nightcats bring their award-winning blues to Yoshi's Oakland.",
        "start_time": "2026-03-11 19:30:00",
        "end_time": "2026-03-11 22:00:00",
        "source_url": "https://dothebay.com/events/2026/3/11/rick-estrin-tickets",
        "tags": '["Concert", "Blues", "Live Music"]',
        "category": "live_music",
        "location": "Oakland, CA"
    },
    {
        "title": "Josh Levi at Cafe du Nord",
        "description": "R&B artist Josh Levi performs at Cafe du Nord in San Francisco.",
        "start_time": "2026-03-11 19:00:00",
        "end_time": "2026-03-11 21:30:00",
        "source_url": "https://dothebay.com/events/2026/3/11/josh-levi-tickets",
        "tags": '["Concert", "R&B", "Live Music"]',
        "category": "live_music",
        "location": "San Francisco, CA"
    },
    {
        "title": "Cheaper Than Therapy: Stand-Up Comedy at Shelton Theater",
        "description": "Weekly stand-up comedy show at the Shelton Theater. A rotating lineup of Bay Area's funniest comedians for a fraction of therapy costs.",
        "start_time": "2026-03-11 19:45:00",
        "end_time": "2026-03-11 21:30:00",
        "source_url": "https://dothebay.com/events/2026/3/11/cheaper-than-therapy",
        "tags": '["Comedy", "Stand-up", "Weekly"]',
        "category": "comedy",
        "location": "San Francisco, CA"
    },

    # Mar 12
    {
        "title": "LOVE with Johnny Echols at The Chapel",
        "description": "Johnny Echols, original guitarist of the legendary band Love, performs at The Chapel in San Francisco.",
        "start_time": "2026-03-12 20:00:00",
        "end_time": "2026-03-12 22:30:00",
        "source_url": "https://dothebay.com/events/2026/3/12/love-johnny-echols-tickets",
        "tags": '["Concert", "Rock", "Live Music", "Classic"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "Jonah Kagen – Sunflowers & Leather Tour at August Hall",
        "description": "Singer-songwriter Jonah Kagen brings his Sunflowers & Leather Tour to August Hall in San Francisco.",
        "start_time": "2026-03-12 20:00:00",
        "end_time": "2026-03-12 22:30:00",
        "source_url": "https://dothebay.com/events/2026/3/12/jonah-kagen-tickets",
        "tags": '["Concert", "Folk", "Live Music", "Singer-Songwriter"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "Choir!Choir!Choir! Landslide – Fleetwood Mac Singalong at UC Theatre",
        "description": "Join hundreds of voices for a massive Fleetwood Mac singalong led by Choir!Choir!Choir! at the UC Theatre in Berkeley. No experience needed.",
        "start_time": "2026-03-12 19:00:00",
        "end_time": "2026-03-12 21:30:00",
        "source_url": "https://dothebay.com/events/2026/3/12/choir-choir-choir-fleetwood-mac",
        "tags": '["Music", "Singalong", "Community", "Fun"]',
        "category": "concert",
        "location": "Berkeley, CA"
    },
    {
        "title": "BEAUZ & Part Time Killer at 1015 Folsom",
        "description": "Electronic music duo BEAUZ and Part Time Killer bring high-energy dance music to 1015 Folsom, one of SF's premier nightlife venues.",
        "start_time": "2026-03-12 21:00:00",
        "end_time": "2026-03-13 02:00:00",
        "source_url": "https://dothebay.com/events/2026/3/12/beauz-1015-folsom",
        "tags": '["Electronic", "DJ", "Nightlife", "Dance"]',
        "category": "nightlife",
        "location": "San Francisco, CA"
    },
    {
        "title": "Edna Vazquez (of Pink Martini) at The Freight",
        "description": "Vocalist Edna Vazquez, known for her work with Pink Martini, performs at The Freight in Berkeley.",
        "start_time": "2026-03-12 19:00:00",
        "end_time": "2026-03-12 21:30:00",
        "source_url": "https://dothebay.com/events/2026/3/12/edna-vazquez-tickets",
        "tags": '["Concert", "Latin", "Live Music", "Vocal"]',
        "category": "concert",
        "location": "Berkeley, CA"
    },

    # Mar 14
    {
        "title": "Oakland Roots SC vs. New Mexico United",
        "description": "Oakland Roots SC take on New Mexico United at the Oakland-Alameda County Coliseum. Support local soccer!",
        "start_time": "2026-03-14 19:00:00",
        "end_time": "2026-03-14 21:00:00",
        "source_url": "https://dothebay.com/events/2026/3/14/oakland-roots-new-mexico",
        "tags": '["Sports", "Soccer", "Oakland"]',
        "category": "sports",
        "location": "Oakland, CA"
    },
    {
        "title": "Bay FC vs. Denver Summit FC at PayPal Park",
        "description": "Bay FC women's soccer team faces Denver Summit FC at PayPal Park in San Jose.",
        "start_time": "2026-03-14 15:30:00",
        "end_time": "2026-03-14 17:30:00",
        "source_url": "https://dothebay.com/events/2026/3/14/bay-fc-denver",
        "tags": '["Sports", "Soccer", "Women", "NWSL"]',
        "category": "sports",
        "location": "San Jose, CA"
    },
    {
        "title": "WCC WAVES at Fort Mason – Gateway Pavilion",
        "description": "Free art and culture event at Fort Mason's Gateway Pavilion. Part of the West Coast Contemporary creative programming.",
        "start_time": "2026-03-14 11:00:00",
        "end_time": "2026-03-14 17:00:00",
        "source_url": "https://dothebay.com/events/2026/3/14/wcc-waves-fort-mason",
        "tags": '["Art", "Free", "Culture", "Exhibition"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },

    # Mar 16
    {
        "title": "Yung Kai – stay with the ocean, i'll find you tour at August Hall",
        "description": "Rising indie artist Yung Kai brings his 'stay with the ocean, i'll find you' tour to August Hall in San Francisco.",
        "start_time": "2026-03-16 20:00:00",
        "end_time": "2026-03-16 22:30:00",
        "source_url": "https://dothebay.com/events/2026/3/16/yung-kai-tickets",
        "tags": '["Concert", "Indie", "Live Music"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "Band Of Skulls + Ghostwoman at The Ritz",
        "description": "British rock band Band Of Skulls performs with Ghostwoman at The Ritz in San Jose.",
        "start_time": "2026-03-16 19:00:00",
        "end_time": "2026-03-16 22:00:00",
        "source_url": "https://dothebay.com/events/2026/3/16/band-of-skulls-tickets",
        "tags": '["Concert", "Rock", "Live Music"]',
        "category": "concert",
        "location": "San Jose, CA"
    },
    {
        "title": "Anna von Hausswolff at Brick & Mortar Music Hall",
        "description": "Swedish musician Anna von Hausswolff performs her dramatic, organ-driven compositions at Brick & Mortar Music Hall.",
        "start_time": "2026-03-16 20:00:00",
        "end_time": "2026-03-16 22:30:00",
        "source_url": "https://dothebay.com/events/2026/3/16/anna-von-hausswolff-tickets",
        "tags": '["Concert", "Experimental", "Live Music"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },

    # Mar 21
    {
        "title": "Samantha Bee: How to Survive Menopause at Brava Theater",
        "description": "Comedian and TV host Samantha Bee presents her show 'How to Survive Menopause' at Brava Theater.",
        "start_time": "2026-03-21 16:00:00",
        "end_time": "2026-03-21 18:00:00",
        "source_url": "https://dothebay.com/events/2026/3/21/samantha-bee-tickets",
        "tags": '["Comedy", "Stand-up", "Entertainment"]',
        "category": "comedy",
        "location": "San Francisco, CA"
    },
    {
        "title": "An Evening With CAKE at Channel 24",
        "description": "Alt-rock icons CAKE perform at Channel 24. Known for hits like 'Short Skirt/Long Jacket' and 'The Distance.'",
        "start_time": "2026-03-21 19:00:00",
        "end_time": "2026-03-21 22:00:00",
        "source_url": "https://dothebay.com/events/2026/3/21/cake-tickets",
        "tags": '["Concert", "Rock", "Live Music", "Alt-Rock"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "Corey Holcomb at Cobb's Comedy Club",
        "description": "Comedian Corey Holcomb brings his sharp, unfiltered humor to Cobb's Comedy Club. Two shows at 7 PM and 9:15 PM.",
        "start_time": "2026-03-21 19:00:00",
        "end_time": "2026-03-21 23:00:00",
        "source_url": "https://dothebay.com/events/2026/3/21/corey-holcomb-tickets",
        "tags": '["Comedy", "Stand-up", "Live"]',
        "category": "comedy",
        "location": "San Francisco, CA"
    },
    {
        "title": "David Nihill: Taking Tangents Tour at Punch Line",
        "description": "Irish comedian David Nihill brings his Taking Tangents Tour to the Punch Line San Francisco. Two shows at 7 PM and 9:15 PM.",
        "start_time": "2026-03-21 19:00:00",
        "end_time": "2026-03-21 23:00:00",
        "source_url": "https://dothebay.com/events/2026/3/21/david-nihill-tickets",
        "tags": '["Comedy", "Stand-up", "Irish"]',
        "category": "comedy",
        "location": "San Francisco, CA"
    },
    {
        "title": "Ashnikko at The Warfield",
        "description": "Pop and hip-hop artist Ashnikko performs at The Warfield, presented by Goldenvoice.",
        "start_time": "2026-03-21 20:00:00",
        "end_time": "2026-03-21 23:00:00",
        "source_url": "https://dothebay.com/events/2026/3/21/ashnikko-tickets",
        "tags": '["Concert", "Pop", "Hip-Hop", "Live Music"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "The Barr Brothers at Great American Music Hall",
        "description": "Montreal's The Barr Brothers bring their folk-rock sound to the Great American Music Hall.",
        "start_time": "2026-03-21 21:00:00",
        "end_time": "2026-03-21 23:30:00",
        "source_url": "https://dothebay.com/events/2026/3/21/barr-brothers-tickets",
        "tags": '["Concert", "Folk", "Rock", "Live Music"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "Bay FC vs. Angel City FC at PayPal Park",
        "description": "Bay FC women's soccer team takes on Angel City FC at PayPal Park in San Jose. NWSL action.",
        "start_time": "2026-03-21 15:00:00",
        "end_time": "2026-03-21 17:00:00",
        "source_url": "https://dothebay.com/events/2026/3/21/bay-fc-angel-city",
        "tags": '["Sports", "Soccer", "Women", "NWSL"]',
        "category": "sports",
        "location": "San Jose, CA"
    },
    {
        "title": "Women's History Month: Women in Math Exhibit at Exploratorium",
        "description": "Special Women's History Month exhibit celebrating women in mathematics at the Exploratorium. Running through March 31.",
        "start_time": "2026-03-07 10:00:00",
        "end_time": "2026-03-31 17:00:00",
        "source_url": "https://dothebay.com/events/2026/3/7/women-in-math-exploratorium",
        "tags": '["Exhibition", "Science", "Women", "Education"]',
        "category": "education",
        "location": "San Francisco, CA"
    },

    # Mar 23
    {
        "title": "Johnny Marr at Uptown Theatre Napa",
        "description": "The Smiths guitarist and solo artist Johnny Marr performs at the Uptown Theatre in Napa.",
        "start_time": "2026-03-23 20:00:00",
        "end_time": "2026-03-23 22:30:00",
        "source_url": "https://dothebay.com/events/2026/3/23/johnny-marr-tickets",
        "tags": '["Concert", "Rock", "Live Music", "Indie"]',
        "category": "concert",
        "location": "Napa, CA"
    },

    # Mar 25
    {
        "title": "Golden State Warriors vs Brooklyn Nets",
        "description": "Golden State Warriors take on the Brooklyn Nets at Chase Center.",
        "start_time": "2026-03-25 19:00:00",
        "end_time": "2026-03-25 21:30:00",
        "source_url": "https://dothebay.com/events/2026/3/25/warriors-nets",
        "tags": '["Sports", "Basketball", "NBA", "Warriors"]',
        "category": "sports",
        "location": "San Francisco, CA"
    },

    # Mar 26
    {
        "title": "Jeff Tweedy at The Fillmore",
        "description": "Wilco frontman Jeff Tweedy performs a solo show at The Fillmore. An intimate evening with one of indie rock's most celebrated songwriters.",
        "start_time": "2026-03-26 20:00:00",
        "end_time": "2026-03-26 22:30:00",
        "source_url": "https://dothebay.com/events/2026/3/26/jeff-tweedy-tickets",
        "tags": '["Concert", "Indie Rock", "Live Music", "Singer-Songwriter"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "Hippie Sabotage at 1015 Folsom",
        "description": "Electronic duo Hippie Sabotage bring their bass-heavy sound to 1015 Folsom for a high-energy late night show.",
        "start_time": "2026-03-26 21:00:00",
        "end_time": "2026-03-27 02:00:00",
        "source_url": "https://dothebay.com/events/2026/3/26/hippie-sabotage-tickets",
        "tags": '["Electronic", "DJ", "Nightlife", "Dance"]',
        "category": "nightlife",
        "location": "San Francisco, CA"
    },
    {
        "title": "Glassjaw – Aries World Tour at The Regency Ballroom",
        "description": "Post-hardcore band Glassjaw brings their Aries World Tour to The Regency Ballroom.",
        "start_time": "2026-03-26 20:00:00",
        "end_time": "2026-03-26 23:00:00",
        "source_url": "https://dothebay.com/events/2026/3/26/glassjaw-tickets",
        "tags": '["Concert", "Rock", "Post-Hardcore", "Live Music"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "The Record Company at Great American Music Hall",
        "description": "Blues-rock trio The Record Company performs at the Great American Music Hall.",
        "start_time": "2026-03-26 19:30:00",
        "end_time": "2026-03-26 22:00:00",
        "source_url": "https://dothebay.com/events/2026/3/26/record-company-tickets",
        "tags": '["Concert", "Blues Rock", "Live Music"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "SF Pancakes & Booze Art Show at Public Works",
        "description": "All-you-can-eat pancakes, unlimited booze, 50+ live painters, DJs, body painting, and more at Public Works. One of SF's wildest art events.",
        "start_time": "2026-03-26 20:00:00",
        "end_time": "2026-03-27 01:00:00",
        "source_url": "https://dothebay.com/events/2026/3/26/pancakes-booze-art-show",
        "tags": '["Art", "Nightlife", "Party", "Live Painting"]',
        "category": "nightlife",
        "location": "San Francisco, CA"
    },
    {
        "title": "Burnal Equinox 2026: The Cosmic Treehouse at Public Works",
        "description": "Burning Man community presents Burnal Equinox 2026 at Public Works. Art, music, and community celebrating the spring equinox.",
        "start_time": "2026-03-26 19:00:00",
        "end_time": "2026-03-27 02:00:00",
        "source_url": "https://dothebay.com/events/2026/3/26/burnal-equinox",
        "tags": '["Art", "Burning Man", "Music", "Community"]',
        "category": "nightlife",
        "location": "San Francisco, CA"
    },

    # Mar 27
    {
        "title": "Foreigner & Rock Orchestra at Uptown Theatre Napa",
        "description": "Classic rock legends Foreigner perform with a full rock orchestra at the Uptown Theatre in Napa.",
        "start_time": "2026-03-27 20:00:00",
        "end_time": "2026-03-27 22:30:00",
        "source_url": "https://dothebay.com/events/2026/3/27/foreigner-tickets",
        "tags": '["Concert", "Classic Rock", "Live Music"]',
        "category": "concert",
        "location": "Napa, CA"
    },
    {
        "title": "DrawBridge: The Art of SF at Embarcadero Center (Free, through Sept 30)",
        "description": "Free public art exhibition at Embarcadero Center showcasing works that capture the spirit and beauty of San Francisco. Running through September 30.",
        "start_time": "2026-03-07 10:00:00",
        "end_time": "2026-09-30 20:00:00",
        "source_url": "https://dothebay.com/events/2026/3/7/drawbridge-art-sf",
        "tags": '["Art", "Free", "Public Art", "Exhibition"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },

    # ===================== LU.MA EVENTS =====================
    # Source: lu.ma SF calendars and event pages

    {
        "title": "AGI Builders Meetup SF with Entrepreneurs First",
        "description": "AGI Builders meetup in San Francisco co-hosted with Entrepreneurs First. Eight teams showcase their AI work to the San Francisco tech community in a Demo Night format.",
        "start_time": "2026-03-06 18:00:00",
        "end_time": "2026-03-06 21:00:00",
        "source_url": "https://lu.ma/bejuyv7i",
        "tags": '["AI", "Tech", "Startup", "Demo Night"]',
        "category": "jobs_and_networking",
        "location": "San Francisco, CA"
    },
    {
        "title": "SF Demo Night at SHACK15 (Ferry Building)",
        "description": "SF's #1 Tech Showcase at SHACK15 in the iconic San Francisco Ferry Building. Features the sharpest minds and boldest new tech in one electric night with panoramic Bay views.",
        "start_time": "2026-03-12 18:00:00",
        "end_time": "2026-03-12 21:00:00",
        "source_url": "https://lu.ma/demo-night",
        "tags": '["Tech", "Startup", "Demo Night", "Networking"]',
        "category": "jobs_and_networking",
        "location": "San Francisco, CA"
    },
    {
        "title": "Silicon Valley Demo Night (The AI Collective & Atlassian)",
        "description": "Monthly demo night gathering the Bay Area's top builders, sharpest minds, and boldest new ideas for a showcase of frontier tech. Co-hosted by The AI Collective and Atlassian.",
        "start_time": "2026-03-18 18:00:00",
        "end_time": "2026-03-18 21:00:00",
        "source_url": "https://lu.ma/sv-demo-night",
        "tags": '["AI", "Tech", "Startup", "Demo Night"]',
        "category": "jobs_and_networking",
        "location": "Mountain View, CA"
    },
    {
        "title": "Monthly Robotics & AI Meetup at Frontier Tower",
        "description": "Live robotics demos, hands-on tinkering, and show-and-tell sessions from innovative hackathon-winning teams at Frontier Tower in San Francisco.",
        "start_time": "2026-03-19 18:00:00",
        "end_time": "2026-03-19 21:00:00",
        "source_url": "https://lu.ma/monthly-robotics-ai-meetup",
        "tags": '["Robotics", "AI", "Tech", "Meetup"]',
        "category": "jobs_and_networking",
        "location": "San Francisco, CA"
    },
    {
        "title": "AI & Machine Learning Networking SF",
        "description": "AI & Machine Learning start-ups, professionals, and investors networking event at 245 Front St, San Francisco. Connect with the Bay Area AI community.",
        "start_time": "2026-03-09 19:00:00",
        "end_time": "2026-03-09 22:00:00",
        "source_url": "https://www.eventbrite.com/e/ai-machine-learning-start-ups-professionals-investors-networking-sf-tickets-1981743772972",
        "tags": '["AI", "Machine Learning", "Networking", "Tech"]',
        "category": "jobs_and_networking",
        "location": "San Francisco, CA"
    },
    {
        "title": "Founders Live San Francisco",
        "description": "Founders Live SF connects founders, entrepreneurs, and the startup community for pitches, networking, and community building. A regular monthly event.",
        "start_time": "2026-03-13 18:00:00",
        "end_time": "2026-03-13 21:00:00",
        "source_url": "https://lu.ma/founderslivesf",
        "tags": '["Startup", "Founders", "Pitch", "Networking"]',
        "category": "jobs_and_networking",
        "location": "San Francisco, CA"
    },
    {
        "title": "Open Source AI Meetup SF",
        "description": "Monthly meetup for open source AI developers and enthusiasts in San Francisco. Demos, talks, and networking focused on open source machine learning tools and models.",
        "start_time": "2026-03-20 18:00:00",
        "end_time": "2026-03-20 21:00:00",
        "source_url": "https://lu.ma/ucgvu3v0",
        "tags": '["AI", "Open Source", "Tech", "Meetup"]',
        "category": "jobs_and_networking",
        "location": "San Francisco, CA"
    },
    {
        "title": "GenAI Collective SF Demo Extravaganza",
        "description": "The GenAI Collective hosts a demo extravaganza showcasing the most exciting generative AI startups and projects in San Francisco.",
        "start_time": "2026-03-25 18:00:00",
        "end_time": "2026-03-25 21:00:00",
        "source_url": "https://lu.ma/sf-demo",
        "tags": '["AI", "GenAI", "Demo", "Startup"]',
        "category": "jobs_and_networking",
        "location": "San Francisco, CA"
    },
    {
        "title": "Startup Social SF: Dinner with Friends",
        "description": "Startup Social hosts private dinners for the SF tech community. If you're looking to make new friends or switch up your routine, join for good food and genuine conversation.",
        "start_time": "2026-03-15 19:00:00",
        "end_time": "2026-03-15 22:00:00",
        "source_url": "https://lu.ma/startup-dinner",
        "tags": '["Startup", "Dinner", "Social", "Networking"]',
        "category": "jobs_and_networking",
        "location": "San Francisco, CA"
    },
    {
        "title": "SF Bay Area Founder & Investors Party by Pilot",
        "description": "Meet your next founder friend, business partner, or investor in a casual, pitch-free environment. Genuine connection and making friends in the Bay Area startup community.",
        "start_time": "2026-03-21 18:00:00",
        "end_time": "2026-03-21 21:00:00",
        "source_url": "https://luma.com/sf-founders",
        "tags": '["Startup", "Founders", "Investors", "Networking"]',
        "category": "jobs_and_networking",
        "location": "San Francisco, CA"
    },
    {
        "title": "Pre AI Conference Hack Day in San Francisco",
        "description": "A full-day hackathon in San Francisco ahead of the AI conference. Build, hack, and collaborate with other AI developers and researchers.",
        "start_time": "2026-03-22 09:00:00",
        "end_time": "2026-03-22 18:00:00",
        "source_url": "https://lu.ma/bsype6t6",
        "tags": '["AI", "Hackathon", "Tech", "Developer"]',
        "category": "jobs_and_networking",
        "location": "San Francisco, CA"
    },
]


def main():
    df = pd.read_csv(CSV_PATH)
    print(f"Existing events: {len(df)}")

    new_df = pd.DataFrame(NEW_EVENTS)
    new_df["creation_date"] = NOW
    new_df["region"] = "us"

    cols = df.columns.tolist()
    new_df = new_df[cols]

    # Dedup by title (case-insensitive)
    existing_titles = set(df["title"].str.lower().str.strip())
    mask = ~new_df["title"].str.lower().str.strip().isin(existing_titles)
    new_unique = new_df[mask]

    print(f"New events found: {len(new_df)}")
    print(f"After dedup: {len(new_unique)}")

    combined = pd.concat([df, new_unique], ignore_index=True)
    combined.to_csv(CSV_PATH, index=False)
    print(f"Total events after ingestion: {len(combined)}")

    # Stats by source
    new_unique_copy = new_unique.copy()
    new_unique_copy["domain"] = new_unique_copy["source_url"].apply(
        lambda u: u.split("//")[-1].split("/")[0].replace("www.", "") if pd.notna(u) else "unknown"
    )
    domain_counts = new_unique_copy.groupby("domain").size().sort_values(ascending=False)
    print("\nNew events by source:")
    for domain, count in domain_counts.items():
        print(f"  {domain}: {count}")

    new_unique_copy["start_dt"] = pd.to_datetime(new_unique_copy["start_time"], errors="coerce")
    date_counts = new_unique_copy.groupby(new_unique_copy["start_dt"].dt.date).size()
    print("\nNew events by date:")
    for dt, count in sorted(date_counts.items()):
        print(f"  {dt}: {count}")


if __name__ == "__main__":
    main()
