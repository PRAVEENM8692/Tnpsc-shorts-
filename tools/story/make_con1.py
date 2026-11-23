# Builds tools/story/con1.json: Indian Constitution series, part 1 - how the Constitution was made (approved by the owner 2026-11-23).
# Facts checked against Wikipedia (Constituent Assembly), PRS, PIB and the Champakam Dorairajan case summaries on 2026-11-23.
import json
C = {
 "SIN": "Sachchidananda Sinha, an elderly Indian statesman with white hair and a white moustache in a dark coat, presiding with dignity",
 "PRA": "Dr Rajendra Prasad, a calm Indian leader with round glasses in a white dhoti kurta and Gandhi cap, presiding over a large hall",
 "AMB": "Dr B. R. Ambedkar, a dignified Indian scholar in a dark three-piece suit and round glasses, holding a thick draft book",
 "RAU": "B. N. Rau, a thoughtful Indian civil servant in a suit writing at a desk piled with foreign law books",
 "RAI": "Prem Behari Narain Raizada, a calligrapher in a white kurta writing on a large parchment with a steel nib pen, ink bottles around him",
 "NAN": "Nandalal Bose, an Indian artist in a white kurta painting a floral border on a manuscript page with fine brushes, students beside him",
 "DAK": "Dakshayani Velayudhan, an Indian woman in a simple white cotton sari speaking in a legislative hall, with other members listening",
 "AMM": "Ammu Swaminathan, an Indian woman in a sari with spectacles sitting among the members of a legislative hall, taking notes",
 "CHA": "Champakam Dorairajan, a young Tamil woman student in a simple sari holding a college application and a certificate, looking worried in a Madras college office",
}
G = [
("tense and curious, a surprising opening",
 [("ஒரு புத்தகத்தை எழுத 2 ஆண்டு, 11 மாதம், 18 நாள் ஆச்சு. அந்தப் புத்தகம்தான் உலகத்தோட மிக நீளமான எழுதப்பட்ட அரசியலமைப்பு.", "A gigantic old handwritten book lying open on a wooden table under a golden lamp, hundreds of pages, quill pens and ink, a dramatic glow.", "2 ஆண்டு 11 மாதம் 18 நாள்", ""),
  ("இந்திய அரசியலமைப்பு உருவான கதை, பகுதி 1.", "The Indian Parliament building at dawn with a tricolour flag and a flock of birds, golden sky.", "", "")]),
("steady storyteller, the Assembly begins",
 [("1946-ல ஆங்கிலேயர் கிளம்புற நேரம் வந்துச்சு. கேபினட் மிஷன் திட்டப்படி, நம்ம அரசியலமைப்பை எழுத ஒரு அரசியல் நிர்ணய சபை அமைச்சாங்க.", "Three British ministers with papers meeting Indian leaders around a large table in a grand Delhi hall in 1946, serious mood.", "கேபினட் மிஷன் 1946", ""),
  ("1946 டிசம்பர் 9-ல டெல்லியில சபை முதல் தடவையா கூடிச்சு. சச்சிதானந்த சின்ஹா தற்காலிகத் தலைவரா இருந்தார். இரண்டு நாள் கழிச்சு ராஜேந்திர பிரசாத் தலைவரா தேர்வானார்.", "{SIN} opening the first session in a packed round hall with hundreds of members; later {PRA} being congratulated, warm light.", "டிசம்பர் 9, 1946", ""),
  ("முதல்ல சபையில 389 உறுப்பினர்கள். நாடு பிரிஞ்ச பிறகு 299 பேர் மிச்சம் இருந்தாங்க.", "A huge hall with rows of Indian members in white clothes seated in a semicircle, then half the seats empty, a sad mood about partition.", "389 → 299", ""),
  ("அவங்கள்ல 15 பேர் பெண்கள். சென்னை மாகாணத்திலிருந்து அம்மு சுவாமிநாதன், தாட்சாயணி வேலாயுதம் இருந்தாங்க. தாட்சாயணி வேலாயுதம், சபையில இருந்த ஒரே தலித் பெண்.", "{AMM} and {DAK} sitting together among male members in the Assembly hall, a proud and historic moment.", "பெண் உறுப்பினர்கள்", "")]),
("focused, the drafting work",
 [("முதல் வரைவை எழுதினவர், அரசியலமைப்பு ஆலோசகர் பி.என். ராவ். அதை வச்சுதான் வேலை தொடங்குச்சு.", "{RAU} at a desk surrounded by foreign constitutions and law books under a lamp, late-night work.", "பி.என். ராவ்", ""),
  ("1947 ஆகஸ்ட் 29-ல வரைவுக்குழு அமைச்சாங்க. தலைவர் டாக்டர் அம்பேத்கர். மொத்தம் 7 உறுப்பினர்கள்.", "{AMB} sitting at the head of a long table with six committee members, papers spread, a serious meeting.", "வரைவுக்குழு 1947", ""),
  ("அந்த ஏழு பேர்ல மூணு பேர் சென்னை மாகாணத்துக்காரங்க. என். கோபாலசாமி ஐயங்கார், அல்லாடி கிருஷ்ணசாமி ஐயர், டி.டி. கிருஷ்ணமாச்சாரி.", "Three Tamil gentlemen from Madras in traditional dhotis, angavastrams and caps, with files and a map of the Madras Presidency behind them.", "சென்னை மாகாணத்தின் மூவர்", ""),
  ("சட்டத்தை எழுத உலக நாடுகளோட அரசியலமைப்புகளைப் படிச்சாங்க. நாடாளுமன்ற முறை இங்கிலாந்துல இருந்து, அடிப்படை உரிமைகள் அமெரிக்காவுல இருந்து, வழிகாட்டும் நெறிகள் அயர்லாந்துல இருந்து வந்துச்சு.", "A world map with glowing threads from Britain, America and Ireland leading to India, books of each country's laws open on a table.", "உலகிலிருந்து கற்றவை", ""),
  ("அதனால \"இது கடன் வாங்கின அரசியலமைப்பு\"ன்னு விமர்சனம் வந்துச்சு. நல்லதை எங்கிருந்தும் எடுத்துக்கிறதுல தப்பில்லன்னு அம்பேத்கர் பதில் சொன்னார்.", "{AMB} calmly answering critics in the Assembly hall, members listening, one pointing a finger in objection.", "விமர்சனமும் பதிலும்", ""),
  ("சபை 165 நாள் கூடிச்சு. 53,000-க்கும் மேல மக்கள் பார்வையாளர் மாடத்துல உட்கார்ந்து, விவாதங்களைப் பார்த்தாங்க.", "A large public gallery filled with ordinary Indian citizens leaning forward to watch a debate on the floor of the Assembly hall below.", "165 நாள்", "")]),
("proud and ceremonial, the Constitution is born",
 [("1949 நவம்பர் 26-ல அரசியலமைப்பை ஏத்துக்கிட்டாங்க. அதனாலதான் அந்த நாளை அரசியலமைப்பு தினம்னு கொண்டாடுறோம்.", "{PRA} holding the final Constitution document while members applaud in the hall, evening light.", "நவம்பர் 26, 1949", ""),
  ("ஆனா அது நடைமுறைக்கு வந்தது 1950 ஜனவரி 26-ல. ஏன் அந்த நாள்? 1930 ஜனவரி 26-ல தான் காங்கிரஸ் பூரண சுதந்திரத்தை அறிவிச்சது. அதை நினைவுபடுத்தத்தான்.", "Leaders in 1930 raising the Indian tricolour at a Lahore gathering, a huge crowd taking the pledge of full independence.", "ஜனவரி 26", ""),
  ("1950 ஜனவரி 24-ல உறுப்பினர்கள் கையெழுத்துப் போட்டாங்க. 284 பேர் கையெழுத்து போட்டாங்க.", "Members in white lining up to sign a large document at a long table in the Constitution Hall, pens and inkpots, solemn pride.", "284 கையெழுத்துகள்", ""),
  ("இதுல ஒரு ஆச்சரியம். இந்த அரசியலமைப்பு அச்சடிக்கப்படலை, கையால எழுதினது. பிரேம் பிஹாரி நாராயண் ரைசாடா, கிட்டத்தட்ட ஆறு மாசத்துல அழகான கையெழுத்துல எழுதினார். சம்பளம் வாங்கலை, ஒவ்வொரு பக்கத்துலயும் தன் பெயரை எழுத மட்டும் அனுமதி கேட்டார்.", "{RAI} writing slowly in beautiful flowing script, hundreds of finished pages stacked beside him, a lamp and ink bottles, quiet determination.", "கையால் எழுதியது", ""),
  ("நந்தலால் போஸ் தலைமையில சாந்திநிகேதன் கலைஞர்கள் பக்கங்களை ஓவியங்களால அலங்கரிச்சாங்க. அசல் பிரதிகள் நைட்ரஜன் வாயு நிரப்பின பெட்டியில, நாடாளுமன்ற நூலகத்துல பாதுகாக்கப்படுது.", "{NAN} and his students painting colourful floral borders and miniature scenes on a manuscript page, brushes and paint cups around.", "நந்தலால் போஸ்", ""),
  ("அன்னைக்கு அதுல 395 சரிகள், 22 பகுதிகள், 8 அட்டவணைகள் இருந்துச்சு. இன்னைக்கு 470-க்கும் மேல சரிகள், 25 பகுதிகள், 12 அட்டவணைகள். காலத்துக்கு ஏத்த மாதிரி மாறுற, வாழுற ஆவணம் இது.", "A thick glowing book opening and growing with new pages and glowing numbers floating above it, a futuristic yet warm library.", "395 → 470+", ""),
  ("அமலுக்கு வந்த அடுத்த வருஷமே, ஒரு தமிழ்நாட்டுப் பெண்தான் அதை மாத்த வச்சாங்க. சம்பகம் துரைராஜன் வழக்கு, 1951. சென்னை மாகாணம், கல்லூரி சேர்க்கையில சாதி, மதம் வாரியா இடஒதுக்கீடு வச்சிருந்துச்சு. மருத்துவக் கல்லூரியில இடம் கிடைக்காத சம்பகம், அது தன் அடிப்படை உரிமையை மீறுதுன்னு உச்ச நீதிமன்றம் போனாங்க. 1951 ஏப்ரல் 9-ல நீதிமன்றம் அந்த ஆணையை ரத்து செஞ்சுது. அதுக்குப் பிறகு முதல் அரசியலமைப்புத் திருத்தம் வந்துச்சு, சரி 15(4) சேர்ந்துச்சு. அப்போதான் இடஒதுக்கீட்டுக்கு அரசியலமைப்பு ஆதரவு கிடைச்சுது.", "{CHA} standing before a grand Supreme Court building with pillars and a staircase, holding her papers, determined, golden morning light.", "சம்பகம் துரைராஜன் வழக்கு", ""),
  ("அடுத்த பகுதியில முகவுரையையும் அடிப்படை உரிமைகளையும் பார்க்கலாம். சேனலை subscribe பண்ணுங்க.", "A glowing palm-leaf scroll and a lit lamp beside the Indian Constitution book, a tricolour ribbon, warm golden light.", "", "")]),
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
def first(prefix):
    return next(s["n"] for s in out if s["nar"].startswith(prefix))
thumb = [first("1947 ஆகஸ்ட் 29"), first("இதுல ஒரு ஆச்சரியம்"), first("அமலுக்கு வந்த")]
json.dump({"title": "உலகின் மிக நீளமான புத்தகம்! இந்திய அரசியலமைப்பு உருவான கதை – பகுதி 1", "shots": out, "scenes": scenes, "anims": {}, "thumb": thumb,
           "shorts": [[first("முதல் வரைவை"), first("அந்த ஏழு"), "அரசியலமைப்பை எழுதிய தமிழ்நாட்டு மூவர்!", "இந்திய அரசியலமைப்பு"],
                      [first("இதுல ஒரு ஆச்சரியம்"), first("நந்தலால்"), "அச்சடிக்கவே இல்லை! கையால் எழுதிய அரசியலமைப்பு", "இந்திய அரசியலமைப்பு"],
                      [first("அமலுக்கு வந்த"), first("அமலுக்கு வந்த"), "ஒரு தமிழ்ப் பெண் அரசியலமைப்பையே மாற்றினார்!", "சம்பகம் துரைராஜன் வழக்கு"]],
           "exam_cards": [
             "அரசியல் நிர்ணய சபை: முதல் கூட்டம் 9.12.1946. தற்காலிகத் தலைவர் சச்சிதானந்த சின்ஹா. தலைவர் ராஜேந்திர பிரசாத். உறுப்பினர்கள் 389, பிரிவினைக்குப் பிறகு 299.",
             "வரைவுக்குழு 29.8.1947, தலைவர் அம்பேத்கர், 7 உறுப்பினர்கள். ஆலோசகர் பி.என். ராவ். சென்னை மாகாணம்: கோபாலசாமி ஐயங்கார், அல்லாடி கிருஷ்ணசாமி ஐயர், டி.டி. கிருஷ்ணமாச்சாரி.",
             "ஏற்பு 26.11.1949 (அரசியலமைப்பு தினம்). கையெழுத்து 24.1.1950, 284 பேர். நடைமுறை 26.1.1950. சபை 165 நாள் கூடியது.",
             "அசல்: 395 சரிகள், 22 பகுதிகள், 8 அட்டவணைகள். கையால் எழுதியவர் பிரேம் பிஹாரி நாராயண் ரைசாடா. ஓவியம்: நந்தலால் போஸ் குழு.",
             "சம்பகம் துரைராஜன் வழக்கு (சென்னை மாகாணம்) 9.4.1951: சரிகள் 15(1), 29(2) மீறல். முதல் திருத்தம் 1951: சரி 15(4) சேர்ப்பு."]},
          open("tools/story/con1.json", "w"), ensure_ascii=False, indent=1)
print(n, "shots", sum(len(s["nar"]) for s in out), "chars; thumb", thumb)
