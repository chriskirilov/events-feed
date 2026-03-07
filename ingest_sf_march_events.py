"""
Direct ingestion of SF Bay Area events for March 2026.
Events sourced from web searches of multiple SF event calendars:
- SF Funcheap, SFTourismTips, SFStandard, Eventbrite, Songkick,
  CrawlSF, DoTheBay, Haute Living SF, Secret San Francisco, etc.
"""
import pandas as pd
from datetime import datetime

CSV_PATH = "event_data.csv"
NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

NEW_EVENTS = [
    # === MARCH 7 (TODAY) ===
    {
        "title": "San Francisco Chinese New Year Parade 2026",
        "description": "Named one of the world's top ten parades, the Chinese New Year Parade in San Francisco is the largest celebration of its kind outside of Asia. Features lion dancers, giant dragons, traditional drums, firecrackers, colorful floats, and marching bands through Chinatown and downtown SF.",
        "start_time": "2026-03-07 17:00:00",
        "end_time": "2026-03-07 21:00:00",
        "source_url": "https://www.sftravel.com/article/san-francisco-festivals-events-march",
        "tags": '["Festival", "Culture", "Parade", "Chinese New Year"]',
        "category": "festival",
        "location": "San Francisco, CA"
    },
    {
        "title": "Chinese New Year Community Street Fair",
        "description": "Annual street fair celebrating the Lunar New Year in San Francisco's Chinatown. Browse vendor booths, enjoy traditional food, watch cultural performances, and experience the festive atmosphere. The fair spans two days with activities for the whole family.",
        "start_time": "2026-03-07 10:00:00",
        "end_time": "2026-03-08 18:00:00",
        "source_url": "https://sf.funcheap.com/city-guide/san-francisco-march-festivals-street-fairs/",
        "tags": '["Festival", "Culture", "Food", "Family"]',
        "category": "festival",
        "location": "San Francisco, CA"
    },
    {
        "title": "FOG Holi Festival of Colors at Dolores Park",
        "description": "Celebrate Holi, the Hindu festival of colors, love, and spring, at San Francisco's Dolores Park. Throw vibrant colored powders, dance to music, and welcome the arrival of spring in this joyful community celebration.",
        "start_time": "2026-03-07 12:00:00",
        "end_time": "2026-03-07 16:00:00",
        "source_url": "https://sf.funcheap.com/city-guide/san-francisco-march-festivals-street-fairs/",
        "tags": '["Festival", "Culture", "Outdoor", "Community"]',
        "category": "festival",
        "location": "San Francisco, CA"
    },
    {
        "title": "Non Stop Bhangra's Holi Festival of Colors",
        "description": "Non Stop Bhangra hosts a vibrant Holi celebration with Bhangra dancing, colorful powders, and energetic music. Experience the joy of this traditional Indian spring festival with a Bay Area twist.",
        "start_time": "2026-03-07 14:00:00",
        "end_time": "2026-03-07 18:00:00",
        "source_url": "https://www.sftourismtips.com/san-francisco-events-in-march.html",
        "tags": '["Festival", "Dance", "Culture", "Music"]',
        "category": "festival",
        "location": "San Francisco, CA"
    },
    {
        "title": "Solarpunkification 2026",
        "description": "Solarpunkification brings together artists, musicians, technologists, futurists, and community builders to prototype the futures we actually want. Explores what becomes possible when technology and nature work together. Free admission.",
        "start_time": "2026-03-06 10:00:00",
        "end_time": "2026-03-08 20:00:00",
        "source_url": "https://sfstandard.com/2026/03/04/17-best-events-sf-weekend-chinese-new-year-parade-floral-exhibits/",
        "tags": '["Art", "Technology", "Community", "Free"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },
    {
        "title": "REFRESH 2026 at Swissnex",
        "description": "Swissnex in San Francisco presents REFRESH 2026, a free 4-day festival at Pier 17 featuring keynotes, masterclasses, and an art exhibition running until April 10th. Explores innovation at the intersection of Swiss and San Francisco creativity.",
        "start_time": "2026-03-05 10:00:00",
        "end_time": "2026-03-08 18:00:00",
        "source_url": "https://sfstandard.com/2026/03/04/17-best-events-sf-weekend-chinese-new-year-parade-floral-exhibits/",
        "tags": '["Innovation", "Art", "Technology", "Free"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },
    {
        "title": "Monty Python's Spamalot at the Golden Gate Theatre",
        "description": "The Tony Award-winning musical comedy lovingly ripped off from the classic film Monty Python and the Holy Grail. Running March 3-22 at the Golden Gate Theatre.",
        "start_time": "2026-03-07 20:00:00",
        "end_time": "2026-03-07 22:30:00",
        "source_url": "https://www.broadwaysf.com/",
        "tags": '["Theater", "Comedy", "Musical", "Broadway"]',
        "category": "theater",
        "location": "San Francisco, CA"
    },
    {
        "title": "The Music Critic: John Malkovich with the SF Symphony",
        "description": "In an entertaining evening of music and comedy, acclaimed actor John Malkovich slips into the role of the evil critic who trashes some of the best music of all time in a gleeful romp with the San Francisco Symphony.",
        "start_time": "2026-03-07 19:30:00",
        "end_time": "2026-03-07 22:00:00",
        "source_url": "https://www.sfsymphony.org/",
        "tags": '["Classical Music", "Comedy", "Symphony", "Performance"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "42nd Annual Bouquets to Art at the de Young Museum",
        "description": "One hundred Bay Area floral designers bring spring early with fresh floral displays inspired by the permanent collection at the de Young Museum. A beloved San Francisco tradition running March 3-8.",
        "start_time": "2026-03-03 09:30:00",
        "end_time": "2026-03-08 17:00:00",
        "source_url": "https://www.sftourismtips.com/san-francisco-events-in-march.html",
        "tags": '["Art", "Flowers", "Museum", "Exhibition"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },
    {
        "title": "Dan Savage Presents 2026 HUMP! Film Festival: Spring Lineup",
        "description": "Dan Savage's annual amateur erotic film festival returns to San Francisco with a spring lineup of short films celebrating body positivity and creative expression. Running through March 14.",
        "start_time": "2026-03-07 19:00:00",
        "end_time": "2026-03-07 22:00:00",
        "source_url": "https://sfstandard.com/2026/03/04/17-best-events-sf-weekend-chinese-new-year-parade-floral-exhibits/",
        "tags": '["Film", "Festival", "Entertainment"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },
    {
        "title": "Happiest Place on Earth: The Disneyland Story at Walt Disney Family Museum",
        "description": "Explore the history and magic of Disneyland at the Walt Disney Family Museum in the Presidio. This special exhibit takes visitors through the creation, evolution, and cultural impact of the world's most famous theme park.",
        "start_time": "2026-03-07 10:00:00",
        "end_time": "2026-03-08 17:00:00",
        "source_url": "https://www.waltdisney.org/",
        "tags": '["Museum", "Exhibition", "Family", "History"]',
        "category": "museum",
        "location": "San Francisco, CA"
    },
    {
        "title": "Courage XL 2026 – Indie Showcase & GDC Pre-Party",
        "description": "Indie game developers showcase their latest creations at this annual GDC pre-party event. Play demos, meet developers, and celebrate the indie game community in San Francisco.",
        "start_time": "2026-03-07 18:00:00",
        "end_time": "2026-03-07 23:00:00",
        "source_url": "https://www.eventbrite.com/d/ca--san-francisco/events--this-weekend/",
        "tags": '["Gaming", "Technology", "Nightlife", "Networking"]',
        "category": "jobs_and_networking",
        "location": "San Francisco, CA"
    },
    {
        "title": "Introducing 1 Umbrella at Temple Nightclub",
        "description": "Experience the grand opening of 1 Umbrella at Temple Nightclub in San Francisco. A night of music, dancing, and celebration at one of SF's premier nightlife venues.",
        "start_time": "2026-03-07 22:00:00",
        "end_time": "2026-03-08 02:00:00",
        "source_url": "https://www.eventbrite.com/d/ca--san-francisco/events--this-weekend/",
        "tags": '["Nightlife", "Music", "Dance", "Club"]',
        "category": "nightlife",
        "location": "San Francisco, CA"
    },
    {
        "title": "Gettoblaster & J.Phlip at Great Northern",
        "description": "Gettoblaster and J.Phlip bring their signature electronic music vibes to Great Northern. An unforgettable night of house and techno music.",
        "start_time": "2026-03-07 22:00:00",
        "end_time": "2026-03-08 03:00:00",
        "source_url": "https://www.eventbrite.com/d/ca--san-francisco/events--this-weekend/",
        "tags": '["Music", "Nightlife", "Electronic", "DJ"]',
        "category": "live_music",
        "location": "San Francisco, CA"
    },
    {
        "title": "Illuminate LIVE Free Concert at Golden Gate Park Bandshell",
        "description": "Free outdoor concert at the Golden Gate Park Bandshell as part of the Illuminate LIVE sixth season. Enjoy live music in a beautiful park setting with a state-of-the-art sound system.",
        "start_time": "2026-03-07 14:00:00",
        "end_time": "2026-03-07 17:00:00",
        "source_url": "https://sf.funcheap.com/city-guide/san-francisco-march-festivals-street-fairs/",
        "tags": '["Music", "Free", "Outdoor", "Concert"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "KAWS Exhibition at SFMOMA",
        "description": "The first major KAWS museum exhibition on the West Coast at SFMOMA, featuring beloved characters COMPANION, BFF, and CHUM. Explore the artist's trajectory from street art to global recognition.",
        "start_time": "2026-03-07 10:00:00",
        "end_time": "2026-03-07 17:00:00",
        "source_url": "https://www.sfmoma.org/",
        "tags": '["Art", "Museum", "Exhibition", "Contemporary Art"]',
        "category": "museum",
        "location": "San Francisco, CA"
    },
    {
        "title": "Gods & Monsters at New Conservatory Theatre Center",
        "description": "A compelling theatrical production at the New Conservatory Theatre Center, running March 6 through April 5. Explores themes of identity, creativity, and the relationship between art and life.",
        "start_time": "2026-03-07 20:00:00",
        "end_time": "2026-03-07 22:00:00",
        "source_url": "https://www.san-francisco-theater.com/dates/2026/03",
        "tags": '["Theater", "Drama", "Performance"]',
        "category": "theater",
        "location": "San Francisco, CA"
    },
    {
        "title": "Entwined LED Installation in Golden Gate Park",
        "description": "Experience Charles Gadeken's Entwined, a sprawling immersive LED light installation in Golden Gate Park. Features a massive glowing 30-foot tree called Elder Mother that moves with the wind on JFK Promenade. Free.",
        "start_time": "2026-03-07 18:00:00",
        "end_time": "2026-03-07 22:00:00",
        "source_url": "https://sf.funcheap.com/city-guide/san-francisco-march-festivals-street-fairs/",
        "tags": '["Art", "Free", "Outdoor", "Light Installation"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },
    {
        "title": "Unwind by the Bay: Free Community Yoga",
        "description": "Free community yoga session by The Iron Mat by the San Francisco waterfront. All levels welcome. A perfect way to start the weekend with mindful movement.",
        "start_time": "2026-03-07 10:00:00",
        "end_time": "2026-03-07 11:30:00",
        "source_url": "https://sweatpals.com/blog/114026",
        "tags": '["Yoga", "Free", "Wellness", "Community"]',
        "category": "health_and_wellness",
        "location": "San Francisco, CA"
    },

    # === MARCH 8 (SUNDAY) ===
    {
        "title": "Monty Python's Spamalot - Sunday Matinee",
        "description": "Sunday matinee of the Tony Award-winning musical comedy at the Golden Gate Theatre. Based on Monty Python and the Holy Grail.",
        "start_time": "2026-03-08 14:00:00",
        "end_time": "2026-03-08 16:30:00",
        "source_url": "https://www.broadwaysf.com/",
        "tags": '["Theater", "Comedy", "Musical", "Broadway"]',
        "category": "theater",
        "location": "San Francisco, CA"
    },
    {
        "title": "Illuminate LIVE Sunday Concert at Golden Gate Park",
        "description": "Free Sunday outdoor concert at the Golden Gate Park Bandshell. Part of the Illuminate LIVE season with over 125 performances through mid-November.",
        "start_time": "2026-03-08 13:00:00",
        "end_time": "2026-03-08 16:00:00",
        "source_url": "https://sf.funcheap.com/city-guide/san-francisco-march-festivals-street-fairs/",
        "tags": '["Music", "Free", "Outdoor", "Concert"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "Dear San Francisco - A Circus Love Letter",
        "description": "Arts collective The 7 Fingers presents Dear San Francisco, a breathtaking circus show as a love letter to the City by the Bay. Acrobatics, storytelling, and heart-stopping performances at Club Fugazi.",
        "start_time": "2026-03-08 17:00:00",
        "end_time": "2026-03-08 19:00:00",
        "source_url": "https://www.san-francisco-theater.com/dates/2026/03",
        "tags": '["Circus", "Theater", "Performance", "Entertainment"]',
        "category": "theater",
        "location": "San Francisco, CA"
    },
    {
        "title": "San Francisco Ballet: Don Quixote",
        "description": "A ravishing traditional Spanish-inspired three-act story ballet featuring costumes by Tony Award-winning designer Martin Pakledinaz at the War Memorial Opera House.",
        "start_time": "2026-03-08 14:00:00",
        "end_time": "2026-03-08 17:00:00",
        "source_url": "https://www.sfballet.org/",
        "tags": '["Ballet", "Dance", "Performance", "Classical"]',
        "category": "theater",
        "location": "San Francisco, CA"
    },

    # === MARCH 9 ===
    {
        "title": "Union Square Free Sketch Class",
        "description": "Free sketch class in Union Square Plaza led by City Studio artist/educators using a wide range of materials. Part of the free park programs running through March 31.",
        "start_time": "2026-03-09 13:00:00",
        "end_time": "2026-03-09 15:00:00",
        "source_url": "https://visitunionsquaresf.com/park-programs",
        "tags": '["Art", "Free", "Community", "Outdoor"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },
    {
        "title": "Free Outdoor Fitness Class at Union Square",
        "description": "Free outdoor fitness class led by Rae Studios at Union Square Plaza. Break a sweat and meet new people in this community workout session.",
        "start_time": "2026-03-09 09:00:00",
        "end_time": "2026-03-09 10:00:00",
        "source_url": "https://visitunionsquaresf.com/park-programs",
        "tags": '["Fitness", "Free", "Outdoor", "Community"]',
        "category": "health_and_wellness",
        "location": "San Francisco, CA"
    },
    {
        "title": "Sonic Vinyasa Outdoor Yoga",
        "description": "Donation-based outdoor yoga session combining music and movement. A unique wellness experience that brings together yoga, sound, and the San Francisco outdoors.",
        "start_time": "2026-03-09 10:00:00",
        "end_time": "2026-03-09 11:30:00",
        "source_url": "https://sweatpals.com/blog/114026",
        "tags": '["Yoga", "Wellness", "Outdoor", "Music"]',
        "category": "health_and_wellness",
        "location": "San Francisco, CA"
    },
    {
        "title": "Itzhak Perlman at Davies Symphony Hall",
        "description": "World-renowned violinist Itzhak Perlman returns for a one-night-only concert in his 80th birthday season. Features Bach's Violin Concerto No. 1 and Brahms's Academic Festival Overture.",
        "start_time": "2026-03-09 19:30:00",
        "end_time": "2026-03-09 22:00:00",
        "source_url": "https://www.sfsymphony.org/",
        "tags": '["Classical Music", "Violin", "Concert", "Symphony"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },

    # === MARCH 10-11 ===
    {
        "title": "Golden State Warriors vs Detroit Pistons",
        "description": "Golden State Warriors take on the Detroit Pistons at Chase Center. Catch the Warriors in one of their final regular-season home games.",
        "start_time": "2026-03-10 19:30:00",
        "end_time": "2026-03-10 22:00:00",
        "source_url": "https://www.sftourismtips.com/san-francisco-events-in-march.html",
        "tags": '["Sports", "Basketball", "NBA", "Warriors"]',
        "category": "sports",
        "location": "San Francisco, CA"
    },
    {
        "title": "Free Happy Hour Concert in Golden Gate Park",
        "description": "Free live music at the Spreckels Temple of Music (Golden Gate Park Bandshell) from 4-7 PM. Part of the Wednesday concert series running through November.",
        "start_time": "2026-03-11 16:00:00",
        "end_time": "2026-03-11 19:00:00",
        "source_url": "https://sf.funcheap.com/city-guide/san-francisco-march-festivals-street-fairs/",
        "tags": '["Music", "Free", "Outdoor", "Happy Hour"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "NightLife at the California Academy of Sciences",
        "description": "Thursday night festivities at the California Academy of Sciences with live DJs, outdoor bars, ambiance lighting, and access to the museum's nearly 40,000 animal residents. Ages 21+.",
        "start_time": "2026-03-11 18:00:00",
        "end_time": "2026-03-11 22:00:00",
        "source_url": "https://www.calacademy.org/nightlife",
        "tags": '["Nightlife", "Science", "Music", "Museum"]',
        "category": "nightlife",
        "location": "San Francisco, CA"
    },

    # === MARCH 12 ===
    {
        "title": "Whitney at The Fillmore",
        "description": "Indie rock band Whitney performs live at the legendary Fillmore. Known for their dreamy, harmony-rich sound blending indie rock, soul, and folk influences.",
        "start_time": "2026-03-12 20:00:00",
        "end_time": "2026-03-12 23:00:00",
        "source_url": "https://www.songkick.com/metro-areas/26330-us-sf-bay-area/march-2026",
        "tags": '["Concert", "Indie Rock", "Live Music"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "Miguel – Chaos Tour at Bill Graham Civic Auditorium",
        "description": "Grammy-winning R&B artist Miguel brings his Chaos Tour to Bill Graham Civic Auditorium. Experience his signature blend of R&B, funk, and pop.",
        "start_time": "2026-03-12 20:00:00",
        "end_time": "2026-03-12 23:00:00",
        "source_url": "https://www.songkick.com/metro-areas/26330-us-sf-bay-area/march-2026",
        "tags": '["Concert", "R&B", "Live Music"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "Oakland Restaurant Week 2026",
        "description": "Oakland Restaurant Week runs March 12-22 with special prix-fixe menus and deals at restaurants throughout Oakland. Explore the diverse culinary scene across Oakland's vibrant neighborhoods.",
        "start_time": "2026-03-12 11:00:00",
        "end_time": "2026-03-22 22:00:00",
        "source_url": "https://sf.funcheap.com/city-guide/san-francisco-march-festivals-street-fairs/",
        "tags": '["Food", "Restaurant", "Dining", "Deals"]',
        "category": "food_and_dining",
        "location": "Oakland, CA"
    },
    {
        "title": "San Francisco Startup & Entrepreneur Networking Soiree",
        "description": "San Francisco's largest tech startup, business, and entrepreneur networking event. Connect with founders, investors, and tech professionals.",
        "start_time": "2026-03-12 18:00:00",
        "end_time": "2026-03-12 21:00:00",
        "source_url": "https://www.eventbrite.com/d/ca--san-francisco/events/",
        "tags": '["Networking", "Startup", "Tech", "Business"]',
        "category": "jobs_and_networking",
        "location": "San Francisco, CA"
    },
    {
        "title": "SFIF DocFest 2026",
        "description": "The San Francisco International Film Documentary Festival showcases compelling documentaries from around the world. Features screenings, filmmaker Q&As, and panel discussions. Running March 12-22.",
        "start_time": "2026-03-12 18:00:00",
        "end_time": "2026-03-22 22:00:00",
        "source_url": "https://www.eventbrite.com/d/ca--san-francisco/festival-march/",
        "tags": '["Film", "Documentary", "Festival", "Cinema"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },

    # === MARCH 13 ===
    {
        "title": "SF Symphony: Brahms 2 & Dvorak's Cello Concerto",
        "description": "The San Francisco Symphony performs Brahms's Symphony No. 2 and Dvorak's Cello Concerto at Davies Symphony Hall. A magnificent evening of Romantic-era masterpieces.",
        "start_time": "2026-03-13 19:30:00",
        "end_time": "2026-03-13 22:00:00",
        "source_url": "https://www.sfsymphony.org/",
        "tags": '["Classical Music", "Symphony", "Concert"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "LepraCon St. Patrick's Day Pub Crawl - Day 1",
        "description": "Three-day St. Patrick's Day pub crawl kicks off! Bar hop through SF's best pubs and bars with drink specials and festive fun.",
        "start_time": "2026-03-13 17:00:00",
        "end_time": "2026-03-13 23:00:00",
        "source_url": "https://www.eventbrite.com/d/ca--san-francisco/events/",
        "tags": '["Nightlife", "Bar Crawl", "St Patricks Day", "Social"]',
        "category": "bar_and_mixology",
        "location": "San Francisco, CA"
    },
    {
        "title": "Azteca Mexica New Year Festival",
        "description": "The nation's oldest and largest Aztec New Year ceremony at Emma Prusch Farm Regional Park. Unites Aztec dancers from across the US and Mexico for a three-day family-friendly celebration. Free.",
        "start_time": "2026-03-13 10:00:00",
        "end_time": "2026-03-15 18:00:00",
        "source_url": "https://sf.funcheap.com/city-guide/san-francisco-march-festivals-street-fairs/",
        "tags": '["Festival", "Culture", "Dance", "Free"]',
        "category": "festival",
        "location": "San Jose, CA"
    },

    # === MARCH 14 ===
    {
        "title": "175th Annual St. Patrick's Day Parade",
        "description": "The 175th anniversary of San Francisco's St. Patrick's Day Parade down Market Street. Over 100,000 spectators line the route for one of the largest St. Patrick's celebrations in the world, followed by a massive block party at Civic Center.",
        "start_time": "2026-03-14 11:30:00",
        "end_time": "2026-03-14 17:00:00",
        "source_url": "https://sf.funcheap.com/city-guide/san-francisco-march-festivals-street-fairs/",
        "tags": '["Parade", "Festival", "St Patricks Day", "Free"]',
        "category": "festival",
        "location": "San Francisco, CA"
    },
    {
        "title": "SF St. Patrick's Day Weekend Bar Crawl 2026",
        "description": "Massive 15,000+ strong St. Patrick's Day Saturday pub crawl through San Francisco. Ticket includes free entry to participating bars, drink specials, and a free after party.",
        "start_time": "2026-03-14 14:00:00",
        "end_time": "2026-03-14 22:00:00",
        "source_url": "https://www.eventbrite.com/e/san-francisco-st-patricks-day-weekend-bar-crawl-2026-tickets-1295804509169",
        "tags": '["Nightlife", "Bar Crawl", "St Patricks Day", "Social"]',
        "category": "bar_and_mixology",
        "location": "San Francisco, CA"
    },
    {
        "title": "SF Giants FanFest at Oracle Park",
        "description": "San Francisco Giants FanFest at Oracle Park. Meet players, get autographs, enjoy behind-the-scenes access, and gear up for the upcoming baseball season.",
        "start_time": "2026-03-14 10:00:00",
        "end_time": "2026-03-14 16:00:00",
        "source_url": "https://www.mlb.com/giants/fans/fanfest",
        "tags": '["Sports", "Baseball", "Family", "Fan Event"]',
        "category": "sports",
        "location": "San Francisco, CA"
    },
    {
        "title": "Pi Day Celebration at The Exploratorium",
        "description": "Celebrate Pi Day (3.14) at The Exploratorium with math-themed activities, pie eating, and hands-on science experiments.",
        "start_time": "2026-03-14 10:00:00",
        "end_time": "2026-03-14 17:00:00",
        "source_url": "https://www.exploratorium.edu/",
        "tags": '["Science", "Education", "Family", "Fun"]',
        "category": "education",
        "location": "San Francisco, CA"
    },
    {
        "title": "Brides of March Wedding Dress Pub Crawl",
        "description": "Don your finest wedding dress (thrift store finds welcome!) and join this hilarious annual pub crawl through San Francisco. A beloved SF tradition.",
        "start_time": "2026-03-14 13:00:00",
        "end_time": "2026-03-14 19:00:00",
        "source_url": "https://sf.funcheap.com/city-guide/san-francisco-march-festivals-street-fairs/",
        "tags": '["Nightlife", "Comedy", "Social", "Pub Crawl"]',
        "category": "community_and_social",
        "location": "San Francisco, CA"
    },
    {
        "title": "Artistica Creators Fest - Free Vendor Market",
        "description": "SF's coziest vendor market returns to SOMA featuring over 35 local artisans at a historic venue. Shop handmade goods, art, jewelry, and more. Free entry. March 14-15.",
        "start_time": "2026-03-14 11:00:00",
        "end_time": "2026-03-15 16:00:00",
        "source_url": "https://www.eventbrite.com/e/artistica-creators-fest-free-vendor-market-tickets-1983994595242",
        "tags": '["Art", "Market", "Shopping", "Free"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },
    {
        "title": "Comedians Roast San Francisco: Tech Roast Show",
        "description": "Comedians take aim at San Francisco's tech culture in this hilarious roast show. Sharp wit, tech industry jokes, and plenty of laughs.",
        "start_time": "2026-03-14 20:00:00",
        "end_time": "2026-03-14 22:00:00",
        "source_url": "https://www.eventbrite.com/d/ca--san-francisco/events/",
        "tags": '["Comedy", "Tech", "Stand-up", "Nightlife"]',
        "category": "comedy",
        "location": "San Francisco, CA"
    },
    {
        "title": "Cinema Jambu — A Brazilian Queer Film Festival",
        "description": "Cinema Jambu brings Brazilian queer cinema to San Francisco with a curated selection of films celebrating LGBTQ+ stories from Brazil. March 14-16.",
        "start_time": "2026-03-14 18:00:00",
        "end_time": "2026-03-16 22:00:00",
        "source_url": "https://www.eventbrite.com/d/ca--san-francisco/festival-march/",
        "tags": '["Film", "LGBTQ", "Brazilian", "Festival"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },
    {
        "title": "Pigs & Pinot Wine Weekend in Sonoma County",
        "description": "One of Sonoma County's most celebrated food and wine weekends, hosted by chef Charlie Palmer. World-class wines, gourmet food, and beautiful vineyard settings.",
        "start_time": "2026-03-14 11:00:00",
        "end_time": "2026-03-15 18:00:00",
        "source_url": "https://www.thomashenthorne.com/things-to-do-in-the-san-francisco-bay-area-march-2026/",
        "tags": '["Wine", "Food", "Dining", "Sonoma"]',
        "category": "food_and_dining",
        "location": "Healdsburg, CA"
    },
    {
        "title": "Artisan Cheese Festival 20th Anniversary",
        "description": "Celebrating its 20th anniversary, the Artisan Cheese Festival offers farm tours, a marketplace, and seminars for cheese lovers.",
        "start_time": "2026-03-14 10:00:00",
        "end_time": "2026-03-15 17:00:00",
        "source_url": "https://www.thomashenthorne.com/things-to-do-in-the-san-francisco-bay-area-march-2026/",
        "tags": '["Food", "Cheese", "Festival", "Tasting"]',
        "category": "food_and_dining",
        "location": "Petaluma, CA"
    },

    # === MARCH 15 ===
    {
        "title": "Chinese New Year 10K Run",
        "description": "Annual Chinese New Year 10K run through the streets of San Francisco. A scenic race celebrating the Lunar New Year with runners of all levels welcome.",
        "start_time": "2026-03-15 08:00:00",
        "end_time": "2026-03-15 11:00:00",
        "source_url": "https://sf.funcheap.com/city-guide/san-francisco-march-festivals-street-fairs/",
        "tags": '["Running", "Sports", "Chinese New Year", "Fitness"]',
        "category": "sports",
        "location": "San Francisco, CA"
    },
    {
        "title": "Nine Inch Nails – Peel It Back Tour at Chase Center",
        "description": "Grammy-winning band and Rock & Roll Hall of Fame inductee Nine Inch Nails brings their Peel It Back Tour 2026 to Chase Center.",
        "start_time": "2026-03-15 20:00:00",
        "end_time": "2026-03-15 23:00:00",
        "source_url": "https://www.songkick.com/metro-areas/26330-us-sf-bay-area/march-2026",
        "tags": '["Concert", "Rock", "Live Music"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "Golden State Warriors vs Portland Trail Blazers",
        "description": "Golden State Warriors face the Portland Trail Blazers at Chase Center. A Pacific Division matchup in the final stretch of the regular season.",
        "start_time": "2026-03-15 17:00:00",
        "end_time": "2026-03-15 19:30:00",
        "source_url": "https://www.sftourismtips.com/san-francisco-events-in-march.html",
        "tags": '["Sports", "Basketball", "NBA", "Warriors"]',
        "category": "sports",
        "location": "San Francisco, CA"
    },
    {
        "title": "Dublin's St. Patrick's Day Festival 2026",
        "description": "Free St. Patrick's Day Festival at Dublin Civic Center. Celebrate Irish culture and heritage with family-friendly activities, food, music, and entertainment.",
        "start_time": "2026-03-15 10:00:00",
        "end_time": "2026-03-15 17:00:00",
        "source_url": "https://sf.funcheap.com/city-guide/san-francisco-march-festivals-street-fairs/",
        "tags": '["Festival", "St Patricks Day", "Family", "Free"]',
        "category": "festival",
        "location": "Dublin, CA"
    },
    {
        "title": "Ring Mountain Spring Wildflower Hike",
        "description": "Guided spring wildflower hike on Ring Mountain offering spectacular Bay views and rare wildflowers just beginning to peak.",
        "start_time": "2026-03-15 10:00:00",
        "end_time": "2026-03-15 13:00:00",
        "source_url": "https://www.thomashenthorne.com/things-to-do-in-the-san-francisco-bay-area-march-2026/",
        "tags": '["Hiking", "Nature", "Outdoor", "Wildflowers"]',
        "category": "health_and_wellness",
        "location": "Tiburon, CA"
    },

    # === MARCH 16-17 ===
    {
        "title": "PG Connects Summit San Francisco 2026",
        "description": "PG Connects gaming industry summit brings together game developers, publishers, and investors for networking, talks, and deal-making. March 16-17.",
        "start_time": "2026-03-16 09:00:00",
        "end_time": "2026-03-17 18:00:00",
        "source_url": "https://www.eventbrite.com/d/ca--san-francisco/events/",
        "tags": '["Gaming", "Technology", "Conference", "Networking"]',
        "category": "jobs_and_networking",
        "location": "San Francisco, CA"
    },
    {
        "title": "LepraCon Pub Crawl - St. Patrick's Day",
        "description": "The grand finale of the three-day LepraCon pub crawl on actual St. Patrick's Day. Bar hop through SF's finest Irish pubs.",
        "start_time": "2026-03-17 14:00:00",
        "end_time": "2026-03-17 23:00:00",
        "source_url": "https://www.eventbrite.com/d/ca--san-francisco/events/",
        "tags": '["Nightlife", "Bar Crawl", "St Patricks Day"]',
        "category": "bar_and_mixology",
        "location": "San Francisco, CA"
    },
    {
        "title": "Unscripted: An Evening with Anne Lamott & Neal Allen",
        "description": "Join acclaimed author Anne Lamott and Neal Allen for an intimate evening of conversation about good writing and the creative life at the Curran Theatre.",
        "start_time": "2026-03-17 19:30:00",
        "end_time": "2026-03-17 21:30:00",
        "source_url": "https://www.san-francisco-theater.com/dates/2026/03",
        "tags": '["Literature", "Culture", "Talk", "Authors"]',
        "category": "panel",
        "location": "San Francisco, CA"
    },

    # === MARCH 19-22 ===
    {
        "title": "Superfair Art Fair at Fort Mason Center",
        "description": "The Spring Superfair features top local and global artists showcasing unique art, clothing, jewelry, and handcrafted items at Fort Mason Center. March 19-22.",
        "start_time": "2026-03-19 11:00:00",
        "end_time": "2026-03-22 18:00:00",
        "source_url": "https://www.sftourismtips.com/san-francisco-events-in-march.html",
        "tags": '["Art", "Fair", "Shopping", "Exhibition"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },
    {
        "title": "Michael McIntyre: Hello America Tour",
        "description": "One of Britain's most successful living comedians brings his Hello America tour to San Francisco. Having sold 1.5 million tickets worldwide.",
        "start_time": "2026-03-19 20:00:00",
        "end_time": "2026-03-19 22:00:00",
        "source_url": "https://www.san-francisco-theater.com/dates/2026/03",
        "tags": '["Comedy", "Stand-up", "Entertainment"]',
        "category": "comedy",
        "location": "San Francisco, CA"
    },
    {
        "title": "B2K – Boys 4 Life Tour at Oakland Arena",
        "description": "R&B group B2K reunites for their Boys 4 Life Tour at the Oakland Arena. Relive the early 2000s with hits like Bump Bump Bump.",
        "start_time": "2026-03-20 20:00:00",
        "end_time": "2026-03-20 23:00:00",
        "source_url": "https://www.songkick.com/metro-areas/26330-us-sf-bay-area/march-2026",
        "tags": '["Concert", "R&B", "Live Music", "Nostalgia"]',
        "category": "concert",
        "location": "Oakland, CA"
    },
    {
        "title": "Orozco-Estrada conducts Dvorak 7 – SF Symphony",
        "description": "Conductor Andres Orozco-Estrada leads the SF Symphony in Dvorak's Symphony No. 7 at Davies Symphony Hall. March 20-22.",
        "start_time": "2026-03-20 19:30:00",
        "end_time": "2026-03-20 22:00:00",
        "source_url": "https://www.sfsymphony.org/",
        "tags": '["Classical Music", "Symphony", "Concert"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "Castro Night Market 2026 Season Opening",
        "description": "The Castro Night Market returns! Two blocks of 18th Street transform into a pedestrian-friendly night market with food, music, and community. Free.",
        "start_time": "2026-03-20 17:00:00",
        "end_time": "2026-03-20 21:00:00",
        "source_url": "https://secretsanfrancisco.com/things-to-do-march/",
        "tags": '["Night Market", "Food", "Music", "Free"]',
        "category": "food_and_dining",
        "location": "San Francisco, CA"
    },
    {
        "title": "Palio Italian Dinner",
        "description": "A multicourse prix-fixe Italian dinner featuring classic flavors including antipasto mista and a trio of risottos at 640 Sacramento St. March 20-21.",
        "start_time": "2026-03-20 18:00:00",
        "end_time": "2026-03-21 22:00:00",
        "source_url": "https://www.hautelivingsf.com/2026/02/25/events-calendar-march-2026/",
        "tags": '["Food", "Italian", "Dining", "Prix Fixe"]',
        "category": "food_and_dining",
        "location": "San Francisco, CA"
    },
    {
        "title": "SF Silent Film Festival at Castro Theatre",
        "description": "The San Francisco Silent Film Festival returns to the newly renovated Castro Theatre. Classic silent films with live musical accompaniment. March 20-22.",
        "start_time": "2026-03-20 19:00:00",
        "end_time": "2026-03-22 22:00:00",
        "source_url": "https://www.thomashenthorne.com/things-to-do-in-the-san-francisco-bay-area-march-2026/",
        "tags": '["Film", "Silent Film", "Cinema", "Classic"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },
    {
        "title": "San Francisco Fashion Week: CULTURAL Fashion Festival",
        "description": "SF Fashion Week presents the CULTURAL Fashion Festival with diverse designers and fashion from around the world. Runway shows, exhibitions, and networking. March 20-22.",
        "start_time": "2026-03-20 18:00:00",
        "end_time": "2026-03-22 22:00:00",
        "source_url": "https://www.eventbrite.com/d/ca--san-francisco/festival-march/",
        "tags": '["Fashion", "Culture", "Show", "Design"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },

    # === MARCH 21 ===
    {
        "title": "Tulip Day at Union Square",
        "description": "More than 80,000 tulips cover Union Square — and all tulips are free for visitors to pick and take home! A colorful celebration of spring.",
        "start_time": "2026-03-21 10:00:00",
        "end_time": "2026-03-21 16:00:00",
        "source_url": "https://www.sftourismtips.com/san-francisco-events-in-march.html",
        "tags": '["Flowers", "Free", "Outdoor", "Spring"]',
        "category": "community_and_social",
        "location": "San Francisco, CA"
    },
    {
        "title": "SF Gay Men's Chorus: Totally 80s Spring Concert",
        "description": "A 1980s-themed extravaganza by the SF Gay Men's Chorus at the Curran Theatre. Songs by Madonna, Cyndi Lauper, Tina Turner. Shows at 1 PM and 7:30 PM.",
        "start_time": "2026-03-21 13:00:00",
        "end_time": "2026-03-21 22:00:00",
        "source_url": "https://www.sftourismtips.com/san-francisco-events-in-march.html",
        "tags": '["Music", "Chorus", "80s", "LGBTQ"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "San Francisco Rooftop Holi Music Festival",
        "description": "A rooftop Holi celebration with live music, DJ sets, colored powders, and panoramic views of San Francisco.",
        "start_time": "2026-03-21 14:00:00",
        "end_time": "2026-03-21 22:00:00",
        "source_url": "https://www.eventbrite.com/d/ca--san-francisco/events/",
        "tags": '["Festival", "Music", "Rooftop", "Dance"]',
        "category": "festival",
        "location": "San Francisco, CA"
    },
    {
        "title": "Castro Night Market",
        "description": "The Castro Night Market on 18th Street with food vendors, live music, local artisans, and community vibes. Free admission.",
        "start_time": "2026-03-21 17:00:00",
        "end_time": "2026-03-21 21:00:00",
        "source_url": "https://secretsanfrancisco.com/things-to-do-march/",
        "tags": '["Night Market", "Food", "Music", "Free"]',
        "category": "food_and_dining",
        "location": "San Francisco, CA"
    },

    # === MARCH 22 ===
    {
        "title": "Golden State Warriors vs Denver Nuggets",
        "description": "Golden State Warriors face the Denver Nuggets at Chase Center. A Western Conference showdown in the final month of the regular season.",
        "start_time": "2026-03-22 17:00:00",
        "end_time": "2026-03-22 19:30:00",
        "source_url": "https://www.sftourismtips.com/san-francisco-events-in-march.html",
        "tags": '["Sports", "Basketball", "NBA", "Warriors"]',
        "category": "sports",
        "location": "San Francisco, CA"
    },

    # === MARCH 24-25 ===
    {
        "title": "MJ, The Musical at the Orpheum Theatre",
        "description": "MJ, The Musical arrives at the Orpheum Theatre! This electrifying Broadway show takes audiences inside the creative genius of Michael Jackson, featuring over 25 hits. March 24 - April 5.",
        "start_time": "2026-03-24 19:30:00",
        "end_time": "2026-03-24 22:00:00",
        "source_url": "https://www.broadwaysf.com/",
        "tags": '["Theater", "Musical", "Broadway", "Michael Jackson"]',
        "category": "theater",
        "location": "San Francisco, CA"
    },
    {
        "title": "Father John Misty at The Castro Theatre",
        "description": "Singer-songwriter Father John Misty performs at the newly renovated Castro Theatre. Known for baroque pop and witty songwriting.",
        "start_time": "2026-03-24 20:00:00",
        "end_time": "2026-03-24 23:00:00",
        "source_url": "https://www.songkick.com/metro-areas/26330-us-sf-bay-area/march-2026",
        "tags": '["Concert", "Indie", "Live Music", "Singer-Songwriter"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },

    # === MARCH 26 ===
    {
        "title": "Jerry Harrison & Adrian Belew: REMAIN IN LIGHT",
        "description": "Talking Heads members Jerry Harrison and Adrian Belew perform REMAIN IN LIGHT in its entirety at The Guild Theatre.",
        "start_time": "2026-03-26 20:00:00",
        "end_time": "2026-03-26 23:00:00",
        "source_url": "https://www.songkick.com/metro-areas/26330-us-sf-bay-area/march-2026",
        "tags": '["Concert", "Rock", "Live Music", "Legendary"]',
        "category": "concert",
        "location": "Menlo Park, CA"
    },
    {
        "title": "Miles Davis: A Century of Cool at SFJAZZ Center",
        "description": "SFJAZZ Center celebrates the centennial of Miles Davis with a special concert exploring the legacy of one of jazz's greatest innovators.",
        "start_time": "2026-03-26 19:30:00",
        "end_time": "2026-03-26 22:00:00",
        "source_url": "https://www.sfjazz.org/",
        "tags": '["Jazz", "Concert", "Live Music", "Legend"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "SOMA Nights on Folsom Street",
        "description": "Free monthly art, food, and cultural event on Folsom St. (between 6th-12th). Over 20 businesses participate with pop-up vendors, performances, and street activations.",
        "start_time": "2026-03-26 17:00:00",
        "end_time": "2026-03-26 21:00:00",
        "source_url": "https://secretsanfrancisco.com/things-to-do-march/",
        "tags": '["Art", "Food", "Community", "Free"]',
        "category": "community_and_social",
        "location": "San Francisco, CA"
    },
    {
        "title": "Symphonie fantastique & Jean-Yves Thibaudet – SF Symphony",
        "description": "The SF Symphony performs Berlioz's Symphonie fantastique with acclaimed pianist Jean-Yves Thibaudet at Davies Symphony Hall. March 26-28.",
        "start_time": "2026-03-26 19:30:00",
        "end_time": "2026-03-26 22:00:00",
        "source_url": "https://www.sfsymphony.org/",
        "tags": '["Classical Music", "Symphony", "Piano", "Concert"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "NCAA Men's Basketball Tournament – West Regional (Session 1)",
        "description": "NCAA Tournament West Regional at Chase Center. Watch the best college basketball teams compete for a spot in the Final Four.",
        "start_time": "2026-03-26 16:00:00",
        "end_time": "2026-03-26 23:00:00",
        "source_url": "https://www.sftourismtips.com/san-francisco-events-in-march.html",
        "tags": '["Sports", "Basketball", "NCAA", "Tournament"]',
        "category": "sports",
        "location": "San Francisco, CA"
    },
    {
        "title": "Pink Skies at Brick & Mortar Music Hall",
        "description": "Catch Pink Skies live at the intimate Brick & Mortar Music Hall. An evening of dream pop and indie music.",
        "start_time": "2026-03-26 20:00:00",
        "end_time": "2026-03-26 23:00:00",
        "source_url": "https://www.songkick.com/metro-areas/26330-us-sf-bay-area/march-2026",
        "tags": '["Concert", "Indie", "Live Music"]',
        "category": "live_music",
        "location": "San Francisco, CA"
    },
    {
        "title": "Orianthi at Yoshi's Oakland",
        "description": "Guitar virtuoso Orianthi performs live at Yoshi's Oakland. Known for her work with Michael Jackson and Alice Cooper.",
        "start_time": "2026-03-26 20:00:00",
        "end_time": "2026-03-26 22:30:00",
        "source_url": "https://www.songkick.com/metro-areas/26330-us-sf-bay-area/march-2026",
        "tags": '["Concert", "Guitar", "Live Music", "Rock"]',
        "category": "live_music",
        "location": "Oakland, CA"
    },

    # === MARCH 27-28 ===
    {
        "title": "365 Night Market: Spring in Full Bloom",
        "description": "San Jose's Spring in Full Bloom Night Market with 50+ vendors, food, shopping, music, and cultural entertainment at Grand Century Mall. March 27-28.",
        "start_time": "2026-03-27 16:00:00",
        "end_time": "2026-03-28 22:00:00",
        "source_url": "https://secretsanfrancisco.com/things-to-do-march/",
        "tags": '["Night Market", "Food", "Shopping", "Culture"]',
        "category": "food_and_dining",
        "location": "San Jose, CA"
    },
    {
        "title": "NCAA Men's Basketball Tournament – West Regional (Session 2)",
        "description": "Second session of the NCAA West Regional at Chase Center. The final teams battle for a spot in the Final Four.",
        "start_time": "2026-03-28 14:00:00",
        "end_time": "2026-03-28 22:00:00",
        "source_url": "https://www.sftourismtips.com/san-francisco-events-in-march.html",
        "tags": '["Sports", "Basketball", "NCAA", "Tournament"]',
        "category": "sports",
        "location": "San Francisco, CA"
    },
    {
        "title": "Calum Scott at The Masonic",
        "description": "British singer-songwriter Calum Scott performs at The Masonic. Known for his powerful vocals and hit 'You Are the Reason.'",
        "start_time": "2026-03-28 20:00:00",
        "end_time": "2026-03-28 23:00:00",
        "source_url": "https://www.songkick.com/metro-areas/26330-us-sf-bay-area/march-2026",
        "tags": '["Concert", "Pop", "Live Music"]',
        "category": "concert",
        "location": "San Francisco, CA"
    },
    {
        "title": "San Francisco International Chocolate Salon",
        "description": "The 20th Annual SF Chocolate Salon at the County Fair Building in Golden Gate Park. Sample the finest artisan, gourmet, and premium chocolates.",
        "start_time": "2026-03-28 10:00:00",
        "end_time": "2026-03-28 17:00:00",
        "source_url": "https://www.sftourismtips.com/san-francisco-events-in-march.html",
        "tags": '["Food", "Chocolate", "Festival", "Tasting"]',
        "category": "food_and_dining",
        "location": "San Francisco, CA"
    },

    # === ONGOING / RECURRING MARCH EVENTS ===
    {
        "title": "Ocean Beach Bonfire Season Opens",
        "description": "Beach bonfire season is back at Ocean Beach! Bring friends and marshmallows for a free bonfire on the beach. Running March 1 through October 31.",
        "start_time": "2026-03-07 17:00:00",
        "end_time": "2026-03-07 22:00:00",
        "source_url": "https://sf.funcheap.com/city-guide/san-francisco-march-festivals-street-fairs/",
        "tags": '["Outdoor", "Beach", "Free", "Social"]',
        "category": "community_and_social",
        "location": "San Francisco, CA"
    },
    {
        "title": "About Place: Bay Area Artists at the de Young Museum",
        "description": "Explore 'About Place: Bay Area Artists from the Svane Gift' at the de Young Museum. Ongoing exhibition showcasing works by Bay Area artists.",
        "start_time": "2026-03-07 09:30:00",
        "end_time": "2026-03-31 17:00:00",
        "source_url": "https://www.thomashenthorne.com/things-to-do-in-the-san-francisco-bay-area-march-2026/",
        "tags": '["Art", "Museum", "Exhibition", "Bay Area"]',
        "category": "museum",
        "location": "San Francisco, CA"
    },
    {
        "title": "Berlin & Beyond Film Festival at Castro Theatre",
        "description": "The 30th annual Berlin & Beyond Film Festival at the newly renovated Castro Theatre. German-language cinema with feature films, shorts, and documentaries.",
        "start_time": "2026-03-07 18:00:00",
        "end_time": "2026-03-15 22:00:00",
        "source_url": "https://www.thomashenthorne.com/things-to-do-in-the-san-francisco-bay-area-march-2026/",
        "tags": '["Film", "Festival", "German", "Cinema"]',
        "category": "arts_and_culture",
        "location": "San Francisco, CA"
    },
    {
        "title": "Free Chess Programs at Union Square",
        "description": "Free chess programs led by the Mechanics' Institute at Union Square Plaza. Learn or improve your game. Running through March 31.",
        "start_time": "2026-03-07 11:00:00",
        "end_time": "2026-03-31 15:00:00",
        "source_url": "https://visitunionsquaresf.com/park-programs",
        "tags": '["Games", "Free", "Community", "Outdoor"]',
        "category": "community_and_social",
        "location": "San Francisco, CA"
    },
    {
        "title": "Jazz at Union Square",
        "description": "Free jazz performances curated by Jazz in the Neighborhood and Biscuits and Blues at Union Square Plaza.",
        "start_time": "2026-03-07 12:00:00",
        "end_time": "2026-03-31 14:00:00",
        "source_url": "https://visitunionsquaresf.com/park-programs",
        "tags": '["Jazz", "Music", "Free", "Outdoor"]',
        "category": "live_music",
        "location": "San Francisco, CA"
    },
    {
        "title": "Celebration of Women in Wine - Napa",
        "description": "An all-inclusive event with interactive, educational wine experiences including a grand tasting at CIA at Copia. Celebrating women winemakers and industry leaders.",
        "start_time": "2026-03-04 10:00:00",
        "end_time": "2026-03-08 18:00:00",
        "source_url": "https://www.thomashenthorne.com/things-to-do-in-the-san-francisco-bay-area-march-2026/",
        "tags": '["Wine", "Women", "Tasting", "Education"]',
        "category": "food_and_dining",
        "location": "Napa, CA"
    },
    {
        "title": "Bay Cruise: Golden Gate Bridge & Alcatraz",
        "description": "90-minute cruise under the Golden Gate Bridge and past Alcatraz. March is a great time to see San Francisco from the water as weather improves.",
        "start_time": "2026-03-07 10:00:00",
        "end_time": "2026-03-31 17:00:00",
        "source_url": "https://www.sftourismtips.com/san-francisco-events-in-march.html",
        "tags": '["Cruise", "Sightseeing", "Tourism", "Bay Area"]',
        "category": "community_and_social",
        "location": "San Francisco, CA"
    },
]


def main():
    df = pd.read_csv(CSV_PATH)
    print(f"Existing events: {len(df)}")

    new_df = pd.DataFrame(NEW_EVENTS)
    new_df["creation_date"] = NOW
    new_df["region"] = "us"

    # Match column order
    cols = df.columns.tolist()
    new_df = new_df[cols]

    # Dedup by title
    existing_titles = set(df["title"].str.lower().str.strip())
    mask = ~new_df["title"].str.lower().str.strip().isin(existing_titles)
    new_unique = new_df[mask]

    print(f"New events found: {len(new_df)}")
    print(f"After dedup: {len(new_unique)}")

    combined = pd.concat([df, new_unique], ignore_index=True)
    combined.to_csv(CSV_PATH, index=False)
    print(f"Total events after ingestion: {len(combined)}")

    # Stats
    new_unique_copy = new_unique.copy()
    new_unique_copy["start_dt"] = pd.to_datetime(new_unique_copy["start_time"], errors="coerce")
    date_counts = new_unique_copy.groupby(new_unique_copy["start_dt"].dt.date).size()
    print("\nNew events by start date:")
    for dt, count in sorted(date_counts.items()):
        print(f"  {dt}: {count}")

    cat_counts = new_unique_copy["category"].value_counts()
    print("\nNew events by category:")
    for cat, count in cat_counts.items():
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
