# Builds tools/story/con2.json: Indian Constitution series, part 2 - the Preamble (approved by the owner 2026-11-25, "Script ok").
# Facts checked on 2026-11-25 against Drishti IAS (Objectives Resolution moved 13.12.1946 and adopted 22.1.1947; 42nd Amendment 1976),
# PW / Drishti (Berubari 1960), LiveLaw and GKToday (Kesavananda Bharati 1973: 13 judges, 7-6, 24.4.1973, 68 days; S.R. Bommai 1994).
import json
C = {
 "NEH": "Jawaharlal Nehru, an Indian leader in a white sherwani and Gandhi cap with a red rose, speaking in a large assembly hall",
 "AMB": "Dr B. R. Ambedkar, a dignified Indian scholar in a dark three-piece suit and round glasses, holding a thick draft book",
 "PAL": "Nani Palkhivala, a tall elegant Indian lawyer in a black coat and white bands arguing before a bench of judges in the Supreme Court",
 "KES": "Kesavananda Bharati, a young Kerala monastery head in saffron robes with rudraksha beads, standing in front of a coconut grove and a temple",
 "SIK": "Chief Justice Sikri, an elderly Indian judge in a black robe and white bands, with thick glasses, seated at the centre of a 13-judge bench",
 "BOM": "S. R. Bommai, a Karnataka chief minister in a simple white shirt and dhoti holding a government file, standing in front of the Vidhana Soudha",
 "PEO": "ordinary Indian citizens, farmers, women, students and workers, standing together in a crowd looking hopeful, golden light",
}
G = [
("tense and curious, a surprising opening",
 [("ஒரு புத்தகத்தோட முதல் பக்கத்துல ஒரு நாட்டோட ஆன்மாவே இருக்க முடியுமா? நம்ம அரசியலமைப்புல இருக்கு. அதுதான் முகவுரை.", "A glowing first page of an old handwritten book floating above a lit lamp, golden words, a dark blue library behind, dramatic light.", "முகவுரை", ""),
  ("இந்திய அரசியலமைப்பு உருவான கதை, பகுதி 2.", "The Indian Constitution book resting on a wooden table with a tricolour ribbon and a brass lamp, dawn light through a window.", "", "")]),
("steady storyteller, the Preamble begins",
 [("முகவுரை \"நாங்கள், இந்திய மக்கள்\"ன்னு தொடங்குது. மன்னர் பெயர் இல்லை, அரசாங்கம் பெயர் இல்லை. அதிகாரத்தோட மூலம் மக்கள்தான்னு முதல் வரியிலேயே சொல்லிடுது.", "{PEO}, with the words 'We the People' glowing in the sky above them.", "நாங்கள், இந்திய மக்கள்", ""),
  ("இதோட விதை, 1946 டிசம்பர் 13-ல நேரு சபையில முன்வச்ச குறிக்கோள் தீர்மானம். 1947 ஜனவரி 22-ல சபை அதை ஏத்துக்கிச்சு. அதை வச்சுதான் முகவுரை எழுதப்பட்டுச்சு.", "{NEH} presenting a resolution to a packed Constituent Assembly hall, members listening, a large tricolour behind him.", "குறிக்கோள் தீர்மானம்", "")]),
("clear and rhythmic, the five words",
 [("இறையாண்மை, சமதர்மம், மதச்சார்பின்மை, மக்களாட்சி, குடியரசு. இந்த ஐந்து சொல்லும் இந்தியாவோட அடையாளம்.", "Five glowing golden Tamil-style medallions arranged in an arc over a map of India, a deep blue background.", "5 முக்கிய சொற்கள்", ""),
  ("இறையாண்மைன்னா, நம்ம முடிவுகளை நாமே எடுக்கிறோம், வேறு எந்த நாடும் ஆணையிட முடியாது. குடியரசுன்னா, நாட்டோட தலைவர் பிறப்பால வரமாட்டார், தேர்தல்ல வருவார்.", "An Indian voter's inked finger raised in front of a polling booth, a tricolour fluttering behind, sunlight and pride.", "இறையாண்மை, குடியரசு", ""),
  ("இதுல சமதர்மம், மதச்சார்பின்மை இந்த ரெண்டு சொல்லும் முதல்ல முகவுரையில இல்லை. 1976-ல 42-வது திருத்தத்துல சேர்த்தாங்க. அதே திருத்தத்துல \"நாட்டின் ஒற்றுமை\"ங்கிறது \"ஒற்றுமையும் ஒருமைப்பாடும்\"னு மாறிச்சு.", "A pen adding two glowing golden words into a printed page of the Preamble, a dated stamp reading 1976 beside it, a lamp lit.", "42-வது திருத்தம் 1976", ""),
  ("மதச்சார்பின்மைக்கு ஒரு உதாரணம், எஸ்.ஆர். பொம்மை வழக்கு. 1989-ல கர்நாடகாவுல பொம்மை அரசு கலைக்கப்பட்டுச்சு. அவர் உச்ச நீதிமன்றம் போனார். 1994 மார்ச் 11-ல 9 நீதிபதிகள் தீர்ப்பு சொன்னாங்க. மதச்சார்பின்மை அரசியலமைப்போட அடிப்படைக் கட்டமைப்பு, அதை மீறுற அரசை கலைக்கலாம். ஆனா குடியரசுத் தலைவர் ஆட்சி போடுறதையும் நீதிமன்றம் ஆய்வு செய்யலாம், சட்டசபையில பலத்தை நிரூபிக்கணும்னு சொன்னாங்க.", "{BOM} standing outside a grand state government building holding a file while a nine-judge bench of the Supreme Court is shown in a glowing frame above him.", "எஸ்.ஆர். பொம்மை வழக்கு", ""),
  ("நீதி, சுதந்திரம், சமத்துவம், சகோதரத்துவம். இந்த நாலும் நம்ம அரசியலமைப்போட குறிக்கோள்கள்.", "Four tall glowing pillars labelled in gold with symbols of balance scales, a broken chain, equal hands and joined hands, against a blue sky.", "நீதி, சுதந்திரம், சமத்துவம், சகோதரத்துவம்", "")]),
("dramatic, a legal battle begins",
 [("இப்போ ஒரு கேள்வி. இந்த முகவுரை அரசியலமைப்போட பகுதியா? இல்லை வெறும் அறிமுகமா? இதுக்கு விடை தேடி ரெண்டு வழக்குகள் நடந்துச்சு.", "Two doors in a grand court corridor, one marked with a scroll and one with a book, a lawyer standing and thinking in between.", "பகுதியா? அறிமுகமா?", ""),
  ("முதல் வழக்கு, பெருபாரி, 1960. இந்தியாவும் பாகிஸ்தானும் 1958-ல நேரு-நூன் ஒப்பந்தம் போட்டாங்க. மேற்கு வங்காளத்தோட பெருபாரி பகுதியை பாகிஸ்தானுக்குக் கொடுக்கணும்னு. மேற்கு வங்காளம் எதிர்த்துச்சு. குடியரசுத் தலைவர் இதைப்பத்தி உச்ச நீதிமன்றத்துகிட்ட கருத்துக் கேட்டார்.", "A map of West Bengal with a border village marked and a dotted line drawn through it, worried villagers holding placards, a signed treaty paper in the corner.", "பெருபாரி வழக்கு 1960", ""),
  ("நீதிமன்றம் சொன்னது இது, முகவுரை அரசியலமைப்புக்கான சாவி மாதிரி, சரிதான். ஆனா அது அரசியலமைப்போட பகுதி இல்லை.", "A heavy golden key lying on top of a closed legal book in a dim courtroom, dramatic side light.", "பகுதி இல்லை", ""),
  ("13 வருஷம் கழிச்சு கதை மாறுச்சு. கேரளாவுல ஒரு மடத்தோட தலைவர் கேசவானந்த பாரதி. நில சீர்திருத்தச் சட்டத்துனால மடத்தோட நிலம் போகப் போச்சு. அவர் உச்ச நீதிமன்றம் போனார்.", "{KES} standing at the edge of a green paddy field next to a temple, holding a legal notice, worried but determined.", "கேசவானந்த பாரதி", ""),
  ("1972 அக்டோபர் 31-ல இருந்து 1973 மார்ச் 22 வரை, 68 நாள் விசாரணை. 13 நீதிபதிகள் கொண்ட மிகப் பெரிய அமர்வு அமர்ந்துச்சு. மனுதாரர்களுக்காக நானி பால்கிவாலா 31 நாள் வாதாடினார்.", "{PAL} arguing passionately before a bench of thirteen judges in the Supreme Court, thick law books stacked, a crowded gallery.", "68 நாள், 13 நீதிபதிகள்", ""),
  ("1973 ஏப்ரல் 24. தலைமை நீதிபதி சிக்ரி ஓய்வு பெற்ற அதே நாள் தீர்ப்பு வந்துச்சு. 7க்கு 6. வெறும் ஒரு ஓட்டு வித்தியாசம்.", "{SIK} holding a verdict on the final day of his career, a dramatic split bench of seven judges on one side and six on the other, the gallery tense.", "7 – 6", ""),
  ("தீர்ப்பு என்ன? ஒண்ணு, முகவுரை அரசியலமைப்போட பகுதிதான். பெருபாரி தீர்ப்பு மாறிடுச்சு. ரெண்டு, நாடாளுமன்றம் அரசியலமைப்பைத் திருத்தலாம், ஆனா அதோட அடிப்படைக் கட்டமைப்பை மாத்த முடியாது.", "A glowing constitution book with an unbreakable golden shield around it while hands of lawmakers try to reach it and are stopped, courtroom backdrop.", "அடிப்படைக் கட்டமைப்பு", ""),
  ("இன்னொரு சுவாரஸ்யம். 1975 அவசரநிலை காலத்துல இந்தத் தீர்ப்பை மறுபரிசீலனை செய்ய ஒரு பெரிய அமர்வு கூடிச்சு. மூணு நாள்லயே அதைக் கலைச்சுட்டாங்க. தீர்ப்பு அப்படியே நிலைச்சுது.", "A large bench of judges abruptly rising and leaving a courtroom, papers on the table, a clock on the wall, a dramatic tense mood.", "1975-ல் மறுபரிசீலனை", ""),
  ("முகவுரை இதுவரை ஒரே ஒரு தடவைதான் திருத்தப்பட்டிருக்கு, 1976-ல. அதோட ஆன்மா இன்னைக்கும் பாதுகாப்பா இருக்கு.", "The Preamble page glowing within a transparent shield, a lit lamp and a tricolour ribbon, calm golden light.", "ஒரே ஒரு திருத்தம்", ""),
  ("அடுத்த பகுதியில அடிப்படை உரிமைகளையும், மேனகா காந்தி வழக்கையும் பார்க்கலாம். சேனலை subscribe பண்ணுங்க.", "Hands holding a glowing palm-leaf scroll beside the Indian Constitution book, a lit lamp, warm golden light, a promise of the next part.", "", "")]),
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
thumb = [first("முகவுரை \"நாங்கள்"), first("13 வருஷம்"), first("1973 ஏப்ரல்")]
json.dump({"title": "ஒரே ஒரு ஓட்டில் காப்பாற்றப்பட்ட அரசியலமைப்பு! முகவுரையின் கதை – பகுதி 2", "shots": out, "scenes": scenes, "anims": {}, "thumb": thumb,
           "shorts": [[first("முகவுரை \"நாங்கள்"), first("இதோட விதை"), "அரசியலமைப்பின் முதல் 3 சொற்கள்!", "இந்திய அரசியலமைப்பு"],
                      [first("மதச்சார்பின்மைக்கு"), first("மதச்சார்பின்மைக்கு"), "மதச்சார்பின்மையைக் காப்பாற்றிய பொம்மை வழக்கு!", "எஸ்.ஆர். பொம்மை வழக்கு"],
                      [first("1972 அக்டோபர்"), first("1973 ஏப்ரல்"), "வெறும் ஒரு ஓட்டில் அரசியலமைப்பு தப்பியது!", "கேசவானந்த பாரதி வழக்கு"]],
           "exam_cards": [
             "முகவுரை: குறிக்கோள் தீர்மானம் (நேரு) 13.12.1946 முன்வைப்பு, 22.1.1947 ஏற்பு. அரசியலமைப்பு ஏற்பு 26.11.1949. தொடக்கம்: \"நாங்கள், இந்திய மக்கள்\".",
             "5 சொற்கள்: இறையாண்மை, சமதர்மம், மதச்சார்பின்மை, மக்களாட்சி, குடியரசு. நோக்கங்கள்: நீதி, சுதந்திரம், சமத்துவம், சகோதரத்துவம்.",
             "42-வது திருத்தம் 1976: \"சமதர்மம்\", \"மதச்சார்பின்மை\" சேர்ப்பு, \"ஒற்றுமை\" என்பது \"ஒற்றுமையும் ஒருமைப்பாடும்\". முகவுரை இதுவரை ஒரே ஒரு முறை திருத்தம்.",
             "பெருபாரி வழக்கு 1960 (நேரு-நூன் ஒப்பந்தம் 1958): முகவுரை அரசியலமைப்பின் பகுதி இல்லை. கேசவானந்த பாரதி 1973: முகவுரை பகுதிதான்.",
             "கேசவானந்த பாரதி 24.4.1973: 13 நீதிபதிகள், 7-6, 68 நாள் விசாரணை, அடிப்படைக் கட்டமைப்புக் கொள்கை. எஸ்.ஆர். பொம்மை 11.3.1994: 9 நீதிபதிகள், மதச்சார்பின்மை அடிப்படைக் கட்டமைப்பு."]},
          open("tools/story/con2.json", "w"), ensure_ascii=False, indent=1)
print(n, "shots", sum(len(s["nar"]) for s in out), "chars; thumb", thumb)
