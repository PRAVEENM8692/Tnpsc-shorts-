# Builds tools/story/delhi4.json: the shot list for "Delhi Sultanate part 4 - the Sayyid and Lodi dynasties, and Babur".
# Groups = scenes; each group has the feeling the voice should have, then shots (nar, scene, text, anim).
import json
C = {
 "KHI": "Khizr Khan, a cautious middle-aged governor with a trimmed grey beard, plain white turban and a simple brown robe",
 "ALM": "Alam Shah, a soft plump careless young sultan in a loose silk robe and a small jewelled cap",
 "BAH": "Bahlul Lodi, a sturdy old Afghan chieftain with a thick white moustache, red-and-brown turban and a leather jacket over a cotton shirt",
 "SIK": "Sikandar Lodi, a tall strict king with a dark beard, green turban with a gold brooch and a heavy dark robe",
 "IBR": "Ibrahim Lodi, a proud stubborn young king with a thin black moustache, a high red turban and an expensive embroidered robe",
 "BAB": "Babur, a determined warrior in his forties with a short beard, a fur-edged cap, chain mail and a curved sword",
 "DAU": "Daulat Khan Lodi, a scheming elderly governor with a long grey beard and a dark green turban",
}
G = [
("intriguing, a puzzle: how does a great sultanate end, not with a bang but with a whisper, then rising to a promise of the final battle",
 [("ஒரு சுல்தானியம் எப்படி முடிகிறது? பெரிய போரில் அல்ல. மெல்ல மெல்ல மறைந்து.", "A mighty old Delhi palace at dusk with its banner slowly fading to grey in the wind.", "", ""),
  ("சுமார் 320 ஆண்டுகள் இந்தியாவை ஆண்ட டெல்லி சுல்தானியத்தின் கடைசி அத்தியாயம் இது.", "An old golden hourglass on a table with almost all the sand run down, the Delhi skyline blurred behind it.", "", ""),
  ("இன்று, ஒரே ஒரு நாளில், ஒரு மன்னன் உயிரையும் ஒரு பேரரசையும் இழக்கப்போகிறான்.", "A lone king on an elephant on a vast battlefield at dawn, two huge armies facing each other in the distance.", "", ""),
  ("டெல்லி சுல்தானியம், பகுதி 4. சையது, லோடி வம்சங்கள். பாபர் வருகிறான்.", "An old open book glowing on a table with a green silk bookmark and a feather pen, one page turning.", "", "")]),
("calm and a little ironic for the weak Sayyids, a quiet shrug",
 [("1398-இல் தைமூர் டெல்லியைச் சூறையாடிவிட்டுப் போனான். டெல்லி இடிந்து கிடந்தது.", "Smoking ruins of Delhi with broken walls and empty streets after an invasion, a few survivors in the dust.", "", ""),
  ("தைமூரின் பிரதிநிதியாக இருந்தவர் கிசர் கான்.", "{KHI} standing beside a tent with Timur's black banner behind him, looking humble.", "", ""),
  ("1414. கிசர் கான் டெல்லியைக் கைப்பற்றினார். சையது வம்சம் தொடங்கியது.", "{KHI} quietly sitting on the Delhi throne in a half-empty hall, a few nobles watching.", "கிசர் கான்", "tl1"),
  ("ஆனால் அவர் தன்னை சுல்தான் என்றே அழைத்துக்கொள்ளவில்லை. தைமூரின் பெயரில் ஆட்சி செய்தார்.", "{KHI} signing a paper under the name of a far-away emperor, a small banner of Timur on the desk.", "", ""),
  ("இவர்களின் ஆட்சி டெல்லியையும் சுற்றி சில ஊர்களையும் மட்டுமே கட்டுப்படுத்தியது.", "A small map of Delhi with a tiny red circle and a few villages, the rest of the map belonging to other kingdoms.", "", ""),
  ("மற்ற இடங்களில் மாகாண ஆளுநர்கள் சுயமாக அரசர்கள் ஆனார்கள்.", "Several provincial governors each wearing a crown in different corners of a large map.", "", ""),
  ("சையது வம்சத்தில் நான்கு பேர் ஆண்டார்கள். 37 ஆண்டுகள் மட்டுமே.", "Four portraits in a row on a wall of an old hall, each fading.", "", "")]),
("amused and light for the famous saying, then serious for the handover",
 [("கடைசி சையது அரசர், ஆலம் ஷா. வரலாற்றில் பெயர் பெற்ற சோம்பேறி அரசன்.", "{ALM} lazily lying on cushions with a plate of sweets while his advisors worry in the background.", "ஆலம் ஷா", ""),
  ("அவரைப் பற்றி ஒரு பழமொழியே உண்டு: உலக மன்னன் ஆலம் ஷாவின் ஆட்சி, டெல்லியிலிருந்து பாலம் வரைதான்.", "A tiny king standing at the edge of a small village on a map where the lines show his kingdom ends a few miles from Delhi, a comic spirit.", "", ""),
  ("பாலம் என்பது டெல்லிக்குப் பக்கத்தில் இருக்கும் ஒரு சின்ன ஊர்.", "A small dusty village gate on the outskirts of a big city with a signboard shaped like an arrow pointing back to Delhi.", "", ""),
  ("1451. ஆலம் ஷா தானே அரியணையை விட்டுக்கொடுத்தார்.", "{ALM} handing his crown with a smile to a strong chieftain in a private room.", "", "tl2"),
  ("அவர் பதாயூன் நகரத்தில் அமைதியாக வாழ்ந்தார்.", "{ALM} resting in a small garden house with fruit trees, fanned by a servant.", "", "")]),
("energetic and warm for the rough Afghan tribal leader who is good at friendship",
 [("அரியணையைப் பெற்றவர், பகலோல் லோடி. ஆப்கானிய வீரர்.", "{BAH} riding with a cheerful group of armed horsemen in turbans through a dry plain.", "பகலோல் லோடி", "tl2"),
  ("1451. லோடி வம்சம் தொடங்கியது. இது டெல்லியின் முதல் ஆப்கானிய வம்சம்.", "{BAH} being crowned on the throne by his tribal chiefs in a rough dusty hall.", "", ""),
  ("இவர் அரசர்களைப் போல உயர்ந்த இடத்தில் அமரவில்லை. அவர் தம் தலைவர்களோடு தரையில் அமர்ந்து பேசினார்.", "{BAH} sitting on a carpet on the floor among his noble chiefs, sharing a meal and laughing together.", "", ""),
  ("அவர்களை நண்பர்கள் என்றே அழைத்தார்.", "{BAH} putting an arm around a chief's shoulder while all around them smile warmly.", "", ""),
  ("இதனால் அவருடைய சர்தார்கள் அவருக்கு உண்மையாக இருந்தார்கள். இழந்த பகுதிகள் மீண்டும் டெல்லியோடு சேர்ந்தன.", "A map slowly being coloured red again around Delhi as horsemen ride to the borders.", "", ""),
  ("ஜான்பூர் சுல்தானியத்தை வெற்றி கொண்டார். 1489-இல் அவர் இறந்தார்.", "{BAH} with a sword before the walls of a defeated city whose gates are open, soldiers cheering.", "", "")]),
("proud and strong for Sikandar, thoughtful and a little scolding for the faults",
 [("அடுத்து வந்தவர் அவருடைய மகன். சிக்கந்தர் லோடி.", "{SIK} stepping up to the Delhi throne in a grand hall, courtiers bowing.", "சிக்கந்தர் லோடி", "tl3"),
  ("1489 முதல் 1517 வரை ஆண்டார். லோடி வம்சத்தின் மிகச் சிறந்த அரசர்.", "{SIK} on a balcony looking proudly at a bustling busy capital street below.", "", ""),
  ("1504. அவர் ஆக்ரா நகரை உருவாக்கினார்.", "{SIK} laying a foundation stone at a riverside site with workers, and a city plan on a table.", "ஆக்ரா 1504", ""),
  ("பிற்காலத்தில் முகலாயரின் தலைநகரமே இதுதான்.", "A glowing view of Agra with a river and a grand fort as the sun rises, a distant white dome shape.", "", ""),
  ("வரி முறையை ஒழுங்குபடுத்தினார். நிலத்தை அளக்க ஒரு புதிய அளவுகோலைக் கொண்டுவந்தார். அதன் பெயர், கஸ்-இ-சிக்கந்தரி.", "Surveyors with long measuring ropes and sticks marking a golden field while a clerk writes in a register.", "", ""),
  ("அவர் கவிஞர். குல்ருக் என்ற பெயரில் பாடல்கள் எழுதினார்.", "{SIK} writing verses on a scroll by candlelight in a quiet library.", "", ""),
  ("ஆனால் அவர் கடுமையான கொள்கை கொண்டவர். அதனால் மக்களிடம் பெரிய அன்பு பெறவில்லை.", "{SIK} looking stern on his throne while a worried crowd waits at a distance in a dim hall.", "", "")]),
("dramatic and tense for the stubborn young king and his enemies",
 [("1517. சிக்கந்தர் இறந்தார். அவருடைய மகன் இப்ராகிம் லோடி மன்னனானார்.", "{IBR} sitting on the Delhi throne with a haughty smile, noblemen unhappy around him.", "இப்ராகிம் லோடி", "tl3"),
  ("இவன் மிகவும் பெருமைக்காரன். பழைய சர்தார்களை அவன் மதிக்கவில்லை.", "{IBR} turning his head away rudely from an old noble who is bowing, the court shocked.", "", ""),
  ("பலரைச் சிறையில் அடைத்தான். சிலரைக் கொன்றான்.", "A dark prison cell with an old noble behind iron bars, a guard with a torch at the door.", "", ""),
  ("இதனால் அவனுடைய சொந்தக் கூட்டமே அவனுக்கு எதிராகத் திரும்பியது.", "A group of angry nobles whispering around a candle in a dark room, shadows on the wall.", "", ""),
  ("பஞ்சாபின் ஆளுநர் தௌலத் கான் லோடி. அவனுடைய மகன் அவமானப்படுத்தப்பட்டான்.", "{DAU} receiving a bad news letter, his face dark with anger inside a tent.", "", ""),
  ("அவன் கோபத்தில் ஒரு தூதுவனை காபூலுக்கு அனுப்பினான்.", "A rider galloping through snowy mountains carrying a sealed letter at sunset.", "", ""),
  ("தூதுவன் போன இடம், பாபரிடம்.", "A tent in the snowy mountains of Kabul where {BAB} reads a letter by the fire.", "", "")]),
("exciting, a rising build to the great battle",
 [("பாபர் யார்? தைமூரின் வழித்தோன்றல். மங்கோலிய வீரனும்கூட.", "{BAB} standing on a mountain ridge, the wind blowing his cloak, looking over the plains toward India.", "பாபர்", ""),
  ("மத்திய ஆசியாவில் இருந்து துரத்தப்பட்டு, காபூலில் தங்கியிருந்தான். ஆனால் இந்தியாவை அடையும் கனவு அவனுக்கு இருந்தது.", "{BAB} sitting alone by a fire looking at a map of India in the mountains.", "", ""),
  ("அவனுடைய படை சிறியது. சுமார் 12 ஆயிரம் வீரர்கள். ஆனால் அவர்களிடம் துப்பாக்கிகளும் பீரங்கிகளும் இருந்தன.", "A smaller disciplined army with matchlock guns and iron cannons lined up in a snowy valley, banners flying.", "", "rt"),
  ("இப்ராகிமிடம் ஒரு லட்சம் வீரர்களும் நூற்றுக்கணக்கான யானைகளும் இருந்தன.", "A huge army with hundreds of war elephants stretching to the horizon on a dusty plain.", "", ""),
  ("1526 ஏப்ரல் 21. பானிப்பட் போர்க்களம்.", "A wide battlefield at dawn, two armies facing each other, banners fluttering, dust rising.", "பானிப்பட் 1526", "tl4"),
  ("பாபர் தன் வண்டிகளை வரிசையாக இணைத்து, நடுவில் துப்பாக்கி வீரர்களை நிறுத்தினான்.", "A line of carts chained together with matchlock gunmen behind them and cannons at the centre, {BAB} giving orders.", "", ""),
  ("இப்ராகிமின் யானைகள் இதுவரை எந்த பீரங்கி சத்தத்தையும் கேட்டதில்லை.", "A huge war elephant frightened by a cannon blast, trumpeting and turning around while soldiers panic.", "", ""),
  ("பயந்த யானைகள் திரும்பி, தங்கள் படைகளையே மிதித்தன.", "Frightened elephants stampeding through their own army in smoke and dust.", "", ""),
  ("சில மணி நேரங்களில் போர் முடிந்தது. இப்ராகிம் லோடி போர்க்களத்திலேயே உயிர் இழந்தான்.", "{IBR} fallen in a battlefield with a broken sword beside him, the smoke slowly clearing at sunset.", "", ""),
  ("1526. டெல்லி சுல்தானியம் முடிவுக்கு வந்தது. முகலாய அரசு தொடங்கியது.", "{BAB} sitting on the Delhi throne as nobles bow before him, a new green banner rising.", "", "tl4"),
  ("1206 முதல் 1526 வரை, ஐந்து வம்சங்கள் டெல்லியை ஆண்டன.", "Five old banners in different colours on a wall slowly fading one by one.", "", "dy"),
  ("டெல்லி சுல்தானியத்தின் கதை இத்துடன் முடிகிறது. உங்களுக்குப் பிடித்த சுல்தான் யார்? கமெண்டில் சொல்லுங்கள்.", "A big brass balance scale on a table: a crown on one pan, a book on the other, golden light from a window.", "உங்கள் விருப்பம்?", ""),
  ("அடுத்து, தமிழ்நாட்டின் வரலாறு. தவறவிடாமல் இருக்க சேனலை subscribe செய்யுங்கள்.", "A glowing ancient Tamil temple tower at sunrise with a river in front and birds flying.", "", "")]),
]
out, scenes, n = [], [], 0
for feel, shots in G:
    scenes.append((n + 1, feel))
    for nar, scene, text, anim in shots:
        n += 1
        for k, v in C.items():
            scene = scene.replace("{" + k + "}", v)
        shot = {"n": n, "nar": nar, "scene": scene, "text": "" if anim else text}
        if anim:
            shot["anim"] = anim
        out.append(shot)
ANIMS = {
 "tl1": {"kind": "timeline", "items": [["1398", "தைமூர் படையெடுப்பு"], ["1414", "கிசர் கான் (சையது)"]],
         "fallback": "1398 தைமூர் → 1414 கிசர் கான், சையது வம்சம்"},
 "tl2": {"kind": "timeline", "items": [["1414", "சையது வம்சம்"], ["1451", "லோடி வம்சம்"]],
         "fallback": "1414 சையது வம்சம் → 1451 லோடி வம்சம்"},
 "tl3": {"kind": "list", "title": "லோடி மன்னர்கள்",
         "items": [["1451", "பகலோல்"], ["1489", "சிக்கந்தர்"], ["1517", "இப்ராகிம்"]],
         "fallback": "1451 பகலோல் | 1489 சிக்கந்தர் | 1517 இப்ராகிம்"},
 "rt": {"kind": "route", "title": "பாபரின் வழி", "start": ["காபூல்", 69.2, 34.5],
        "items": [["1526", "பானிப்பட்", 77.0, 29.4, "R"], ["1526", "டெல்லி", 77.2, 28.6, "L"]],
        "fallback": "காபூல் → பானிப்பட் → டெல்லி 1526"},
 "tl4": {"kind": "timeline", "items": [["1526", "பானிப்பட் போர்"], ["1526", "முகலாயர் ஆட்சி"]],
         "fallback": "1526 பானிப்பட் போர் → முகலாயர் ஆட்சி"},
 "dy": {"kind": "list", "title": "ஐந்து வம்சங்கள்",
        "items": [["1206", "அடிமை"], ["1290", "கில்ஜி"], ["1320", "துக்ளக்"], ["1414", "சையது"], ["1451", "லோடி"]],
        "fallback": "1206 அடிமை | 1290 கில்ஜி | 1320 துக்ளக் | 1414 சையது | 1451 லோடி"},
}
json.dump({"title": "ஒரே நாளில் முடிந்த சுல்தானியம் – டெல்லி சுல்தானியம் பகுதி 4", "shots": out, "scenes": scenes, "anims": ANIMS,
           "exam_cards": [
             "சையது வம்சம்: 1414 முதல் 1451 வரை. நிறுவியவர் கிசர் கான். கடைசி அரசர் ஆலம் ஷா.",
             "லோடி வம்சம்: 1451 முதல் 1526 வரை. டெல்லியின் முதல் ஆப்கானிய வம்சம். நிறுவியவர் பகலோல் லோடி.",
             "சிக்கந்தர் லோடி: 1489 முதல் 1517. ஆக்ரா நகரை 1504-இல் உருவாக்கினார். கஸ்-இ-சிக்கந்தரி என்ற அளவு முறை.",
             "இப்ராகிம் லோடி: 1517 முதல் 1526. கடைசி டெல்லி சுல்தான். முதல் பானிப்பட் போர் 1526 ஏப்ரல் 21.",
             "டெல்லி சுல்தானியம்: 1206 முதல் 1526. ஐந்து வம்சங்கள்: அடிமை, கில்ஜி, துக்ளக், சையது, லோடி."]},
          open("tools/story/delhi4.json", "w"), ensure_ascii=False, indent=1)
print(n, "shots", sum(len(s["nar"]) for s in out), "chars")
