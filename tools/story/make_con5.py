# Builds tools/story/con5.json: Indian Constitution series, part 5 (final) - Parliament, President, judiciary (approved 2026-11-28, "Script ok").
# Facts checked 2026-11-28: Kesavananda Bharati (13 judges, 7:6, hearing 31.10.1972-22.3.1973 = 68 days, judgment 24.4.1973 on CJ Sikri's retirement day,
# 703 pages, 11 opinions, Palkhivala argued 31 days and never met his client, A.N. Ray appointed CJ 25.4.1973 over Shelat, Hegde, Grover; review bench Nov 1975 dissolved - LiveLaw);
# Indira Gandhi v Raj Narain (Rae Bareli 1971, margin over 1,10,000, Yashpal Kapoor, Justice Sinha 12.6.1975, 6 years, first sitting PM to testify, Shanti Bhushan, Krishna Iyer 24.6.1975 conditional stay,
# Emergency 25.6.1975 - Bar & Bench); S.R. Bommai (dismissed 20.4.1989, Governor P. Venkatasubbaiah, 9 judges, 11.3.1994 - Wikipedia).
# Zail Singh pocket veto: only 'postal bill withheld unsigned' is confirmed (The Week); no dates stated on purpose.
import json
C = {
 "SWA": "Kesavananda Bharati, a calm Indian monk in saffron robes with a gentle face, standing in front of a small Kerala temple-mutt with coconut palms",
 "PAL": "Nani Palkhivala, a distinguished Indian senior advocate in a black coat and white bands, arguing passionately before a large bench of judges",
 "BEN": "a very large bench of thirteen Indian Supreme Court judges in black robes seated in a long curved row, dramatic courtroom light",
 "SIK": "Chief Justice S. M. Sikri, an elderly Indian judge in a black robe, reading out a thick judgment, a farewell garland beside him",
 "IND": "an Indian woman prime minister of the 1970s in a cotton saree with a white streak in her hair, standing stern before a microphone",
 "JUD": "Justice Jagmohanlal Sinha, an Indian High Court judge in a black robe, seated in a small crowded courtroom, pen in hand, serious",
 "PRE": "an elderly Indian President in a dark bandhgala suit seated at a large desk in Rashtrapati Bhavan, a thick file in front of him, undecided",
 "BOM": "S. R. Bommai, a mild Indian chief minister in a white shirt and cap, standing in a state assembly hall with supporters, hopeful",
 "PEO": "ordinary Indian citizens, farmers, women, students and workers, standing together in a crowd looking hopeful, golden light",
}
G = [
("curious and warm, a monk and a big question",
 [("கேரளா, எடநீர் மடம். அதோட தலைவர் கேசவானந்த பாரதி. அந்த மடத்தோட நிலத்தை நில சீர்திருத்தச் சட்டத்துல அரசு எடுக்கப் பார்த்தது. ஒரு துறவி நீதிமன்றம் போனார். ஆனா அவரோட வழக்கு நிலத்தைப் பத்தி மட்டும் இல்ல. நம்ம எல்லாரோட அரசியலமைப்பையே காப்பாத்தின வழக்கா மாறிச்சு.", "{SWA}, a glowing scroll labelled with a question mark rising above the temple, deep blue evening sky.", "ஒரு துறவியின் வழக்கு", ""),
  ("இந்திய அரசியலமைப்பு உருவான கதை, இறுதிப் பகுதி 5. நாடாளுமன்றம், குடியரசுத் தலைவர், நீதித்துறை. இவங்க மூணு பேருக்கும் இடையில யாருக்கு எவ்வளவு அதிகாரம்னு பார்க்கப் போறோம்.", "Three golden pillars standing in front of the Indian Parliament, the President's house and the Supreme Court, joined by one shining ribbon, sunrise.", "மூன்று தூண்கள்", "")]),
("steady storyteller, the Parliament and the big question",
 [("முதல்ல நாடாளுமன்றம். மக்களவை, மாநிலங்களவை. சட்டம் இயற்றுறது இவங்க வேலை. சரத்து 368 இந்த அரசியலமைப்பையே திருத்தவும் இவங்களுக்கு அதிகாரம் தருது. கேள்வி இதுதான். எவ்வளவு வரை திருத்தலாம்?", "The Indian Parliament building glowing at dusk with a golden pen hovering over an open Constitution book, deep blue sky.", "சரத்து 368", ""),
  ("பகுதி 3-ல பார்த்த கோலக்நாத் வழக்கு, 1967-ல சொன்னது, அடிப்படை உரிமைகளை நாடாளுமன்றம் திருத்தவே முடியாது. அரசு பதிலுக்கு 24, 25, 29-வது திருத்தங்களைக் கொண்டு வந்துச்சு. அந்தத் திருத்தங்களைத்தான் கேசவானந்தா சவால் பண்ணினார்.", "A tug of war between a large Parliament building and a large Supreme Court building pulling a glowing Constitution book between them, dramatic light.", "நாடாளுமன்றம் vs நீதிமன்றம்", "")]),
("tense and dramatic, the 68-day hearing",
 [("1972 அக்டோபர் 31. உச்ச நீதிமன்றம் இதுவரை பார்க்காத அளவுக்குப் பெரிய அமர்வு. 13 நீதிபதிகள்.", "{BEN}", "13 நீதிபதிகள்", ""),
  ("மனுதாரர் தரப்புல வாதாடினவர் நானி பால்கிவாலா. 31 நாள் வாதாடினார். இதுல ஒரு விசித்திரம், அவர் தன் கட்சிக்காரர் கேசவானந்தாவை ஒருமுறை கூடச் சந்திச்சதும் இல்ல, பேசினதும் இல்ல.", "{PAL}, a glowing stopwatch showing 31 days beside him.", "31 நாள் வாதம்", ""),
  ("1973 மார்ச் 22 வரை 68 நாள், ஐந்து மாசம் வாதம் நடந்துச்சு. நீதிபதி கன்னா பால்கிவாலாவோட வாதத்தை 'அவர் வழியா தெய்வமே பேசுது'ன்னு சொன்னதா சொல்லப்படுது.", "A packed courtroom with advocates leaning forward and a wall calendar with pages flying away, warm lamp light.", "68 நாள் விவாதம்", "")]),
("hushed then explosive, the judgment",
 [("1973 ஏப்ரல் 24. தலைமை நீதிபதி சிக்ரி ஓய்வு பெறும் நாள். அதே நாள் தீர்ப்பு. 703 பக்கங்கள், 11 தனித்தனித் தீர்ப்புகள்.", "{SIK}", "703 பக்கம், 11 தீர்ப்புகள்", ""),
  ("வாக்கு 7க்கு 6. ஒரே ஓட்டு வித்தியாசம். தீர்ப்பு என்ன? நாடாளுமன்றம் அரசியலமைப்பைத் திருத்தலாம். ஆனா அதோட அடிப்படைக் கட்டமைப்பை மாற்ற முடியாது.", "{BEN}, a glowing scale tipped by one single vote, the numbers 7 and 6 in gold above.", "7 : 6", ""),
  ("அடிப்படைக் கட்டமைப்புன்னா என்ன? நீதிமன்றம் முழுப் பட்டியல் தரல. ஆனா சட்டத்தின் ஆட்சி, அதிகாரப் பிரிவினை, ஜனநாயகம், மதச்சார்பின்மை, நீதித்துறை சுதந்திரம் போன்றவை இதுல வரும்னு பின்னாடி தீர்ப்புகள்ல வந்துச்சு.", "A glowing fortress with five golden walls labelled with small icons of a book, a balance, a ballot box, a lamp and a gavel, protecting the Constitution inside, dusk sky.", "அடிப்படைக் கட்டமைப்பு", ""),
  ("மறுநாளே, 25 ஏப்ரல், அரசு ஏ.என். ரேவைத் தலைமை நீதிபதி ஆக்கிச்சு. ஷெலட், ஹெக்டே, குரோவர்னு மூணு மூத்த நீதிபதிகளை ஒதுக்கிட்டு. நீதிபதி கன்னா இதை நீதித்துறை சுதந்திரத்துக்கு கடும் அடின்னார்.", "Three senior judges' empty chairs on the bench while a fourth judge takes the central chair, a long dramatic shadow, deep red tones.", "மூன்று மூத்த நீதிபதிகள் புறக்கணிப்பு", "")]),
("dramatic and sharp, the Prime Minister in court",
 [("இன்னொரு பக்கம் 1971 தேர்தல். ரேபரேலி தொகுதியில இந்திரா காந்தி ராஜ் நாராயணை 1,10,000-க்கும் மேல வாக்கு வித்தியாசத்துல தோற்கடிச்சார்.", "{IND}, a ballot box overflowing and a glowing winning margin banner, a victorious crowd behind her, warm light.", "ரேபரேலி 1971", ""),
  ("ராஜ் நாராயண் தேர்தல் முறைகேடு வழக்குப் போட்டார். முக்கியக் குற்றச்சாட்டு, இந்திராவோட தேர்தல் முகவர் யஷ்பால் கபூர், அப்போ அரசு அதிகாரியா இருந்தார்.", "A government clerk's desk with a stamp and a campaign poster in the same frame, a magnifying glass over the stamp, tense light.", "யஷ்பால் கபூர்", ""),
  ("1975 பிப்ரவரி. இந்திரா நீதிமன்றத்துல சாட்சிக் கூண்டுல நின்னார். பதவியில இருந்த பிரதமர் ஒருத்தர் சாட்சி சொன்னது அதுவே முதல் முறை. குறுக்கு விசாரணை செய்தவர் சாந்தி பூஷண்.", "{IND} standing in a witness box in a small courtroom while a lawyer questions her, the whole room silent, dramatic light.", "பிரதமர் சாட்சிக் கூண்டில்", ""),
  ("1975 ஜூன் 12. அலகாபாத் உயர் நீதிமன்ற நீதிபதி ஜகன்மோகன்லால் சின்ஹா தீர்ப்பு சொன்னார். இந்திரா காந்தி 6 வருஷம் பதவி வகிக்கத் தகுதியில்லைன்னு.", "{JUD}, a glowing calendar page marked 12 June above his desk, the courtroom frozen in shock.", "12 ஜூன் 1975", "")]),
("tense, the Emergency night and the review attempt",
 [("ஜூன் 24, உச்ச நீதிமன்ற விடுமுறை நீதிபதி கிருஷ்ண ஐயர் நிபந்தனையோட தடை தந்தார். இந்திரா பிரதமரா தொடரலாம்னு தெளிவுபடுத்தினார். அன்னைக்கு நள்ளிரவு எதிர்க்கட்சித் தலைவர்கள் கைது. ஜூன் 25 காலை, நெருக்கடி நிலை.", "A dark city street at midnight with police vans and a single lit lamp, a newspaper blowing in the wind with a bold date 25 June, deep red and grey tones.", "நெருக்கடி நிலை", ""),
  ("1975 நவம்பர். தலைமை நீதிபதி ரே, கேசவானந்தா தீர்ப்பையே மறுஆய்வு செய்ய 13 நீதிபதி அமர்வை உருவாக்கினார். விசாரணை தொடங்கிச் சில நாளிலேயே அந்த அமர்வு கலைக்கப்பட்டது. அடிப்படைக் கட்டமைப்பு தப்பிச்சது.", "{BEN}, a glowing shield with the Constitution book safe behind it as dark clouds part, a ray of golden light.", "அமர்வு கலைக்கப்பட்டது", "")]),
("clear and gentle, the President",
 [("இப்போ குடியரசுத் தலைவர். சரத்து 52 முதல் 62. நாட்டோட முதல் குடிமகன், பெயருக்குத் தலைவரா, உண்மையான அதிகாரம் யாருக்கு? சரத்து 74 சொல்லுது, அமைச்சரவையோட ஆலோசனைப்படிதான் செயல்படணும். ஷம்ஷேர் சிங் வழக்கு, 1974-லயும் உச்ச நீதிமன்றம் இதையே உறுதி செஞ்சுது.", "{PRE}, a glowing council of ministers sitting in a circle around him whispering advice, warm light.", "சரத்து 74", ""),
  ("ஆனா ஜெயில் சிங் குடியரசுத் தலைவரா இருந்தப்போ ராஜீவ் காந்தி அரசு ஒரு அஞ்சல் மசோதா கொண்டு வந்துச்சு. அவருக்கு அது பிடிக்கல. திருப்பி அனுப்பவும் இல்ல, கையெழுத்தும் போடல. மசோதா உயிரும் இல்ல, செத்ததும் இல்ல. இதுக்குப் பேரு பாக்கெட் வீட்டோ.", "{PRE}, a thick bill file resting inside his coat pocket with a pen unused on the desk, a clock behind him, quiet suspense.", "பாக்கெட் வீட்டோ", ""),
  ("நாடாளுமன்றம் கூடாத சமயத்துல அவசரத்துக்கு குடியரசுத் தலைவரே சரத்து 123-ல அவசரச் சட்டம் பிறப்பிக்கலாம். அதையும் நாடாளுமன்றம் கூடின 6 வாரத்துக்குள்ள ஒப்புக்கணும்.", "A midnight desk lamp, an urgent glowing ordinance paper and an hourglass labelled 6 weeks, deep blue night.", "அவசரச் சட்டம்", "")]),
("dramatic and fair, a state government and the final lesson",
 [("இனி மாநிலங்கள். சரத்து 356, குடியரசுத் தலைவர் ஆட்சி. 1989 ஏப்ரல் 20, கர்நாடகாவோட முதல்வர் எஸ்.ஆர். போம்மை அரசு கலைக்கப்பட்டது. ஆளுநர் பெண்டேகண்டி வெங்கடசுப்பையா அறிக்கையோட அடிப்படையில.", "{BOM}, a stamp labelled 20 April 1989 pressing down on his government file, shocked supporters behind him.", "20 ஏப்ரல் 1989", ""),
  ("19 எம்.எல்.ஏ.க்கள் ஆதரவை விலக்கிக்கிட்டதா சொல்லப்பட்டுச்சு. அடுத்த நாள் அதுல ஏழு பேர், எங்க கையெழுத்து ஏமாத்தி வாங்கப்பட்டதுன்னு மறுத்தாங்க. போம்மை சட்டசபையில பெரும்பான்மையை நிரூபிக்கத் தயாரா இருந்தார். அதுக்கு வாய்ப்பே தரல.", "{BOM}, a ballot-count board in the assembly hall with some names crossed out and seven glowing names restored, tense light.", "ஏழு பேர் மறுத்தாங்க", ""),
  ("1994 மார்ச் 11. 9 நீதிபதிகள் அமர்வு தீர்ப்பு. பெரும்பான்மையை நிரூபிக்கிற இடம் சட்டசபைக்குள்ள வாக்கெடுப்புதான். ஆளுநரோட கருத்து இல்ல. சரத்து 356-ஐயும் நீதிமன்றம் மறுஆய்வு செய்யலாம். மதச்சார்பின்மையும் அடிப்படைக் கட்டமைப்புதான்.", "A nine-judge bench with a glowing assembly vote box in front of them and a golden lock opening on an Article 356 file, hopeful light.", "போம்மை தீர்ப்பு 1994", ""),
  ("உயர் நீதிமன்றம் சரத்து 226, உச்ச நீதிமன்றம் சரத்து 32. உரிமை பறிபோனா நாம நீதிமன்றம் போகலாம். இந்த நீதிமன்றங்கள்தான் நம்ம அரசியலமைப்பின் காவலர்கள்.", "{PEO}, a golden gate of the Supreme Court open to them with a lit lamp at its entrance, warm sunrise.", "நீதிமன்றம் காவலன்", "")]),
("calm and forward-looking, the close",
 [("தேர்வுக்கு நினைவு வச்சுக்கோங்க. கேசவானந்தா, 1973, 13 நீதிபதிகள், 7க்கு 6. சரத்து 74. போம்மை, 1994, 9 நீதிபதிகள். ராஜ் நாராயண், 12 ஜூன் 1975. சரத்து 123, 226, 32.", "A glowing chalk-style notice with five short golden tags beside the Indian Constitution book, a lit lamp, warm light.", "தேர்வு குறிப்பு", ""),
  ("5 பகுதிகள் முடிஞ்சது. ஒரு துறவியோட வழக்கு நமக்கெல்லாம் பாதுகாப்பு வேலியா ஆச்சு. அரசியலமைப்பு காகிதத்துல இல்ல, நாம காக்கும்போதுதான் உயிரோட இருக்கு. சேனலை subscribe பண்ணுங்க.", "{PEO}, holding up a glowing Constitution book together, a lit lamp, warm golden sunrise, a quiet smiling finale.", "", "")]),
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
thumb = [first("கேரளா, எடநீர்"), first("வாக்கு 7க்கு"), first("1975 ஜூன் 12")]
json.dump({"title": "ஒரு துறவி, ஒரு பிரதமர், 13 நீதிபதிகள்! அரசியலமைப்பைக் காத்த வழக்கு – பகுதி 5", "shots": out, "scenes": scenes, "anims": {}, "thumb": thumb,
           "shorts": [[first("கேரளா, எடநீர்"), first("இந்திய அரசியலமைப்பு உருவான கதை, இறுதி"), "ஒரு துறவி அரசியலமைப்பையே காப்பாத்தினார்!", "கேசவானந்தா வழக்கு"],
                      [first("1975 பிப்ரவரி"), first("1975 ஜூன் 12"), "பிரதமரைப் பதவி நீக்கிய நீதிபதி!", "இந்திரா – ராஜ் நாராயண்"],
                      [first("இனி மாநிலங்கள்"), first("19 எம்.எல்.ஏ."), "அரசைக் கலைச்சாங்க, பெரும்பான்மை?", "போம்மை வழக்கு"]],
           "exam_cards": [
             "கேசவானந்த பாரதி 1973: 13 நீதிபதிகள், 7-6, அடிப்படைக் கட்டமைப்புக் கோட்பாடு; 68 நாள் விசாரணை; தீர்ப்பு 24.4.1973; வழக்கறிஞர் நானி பால்கிவாலா.",
             "சரத்து 368: அரசியலமைப்புத் திருத்தம். கோலக்நாத் 1967: உரிமைகளைத் திருத்த முடியாது. 24, 25, 29-வது திருத்தங்கள் சவால் செய்யப்பட்டன.",
             "குடியரசுத் தலைவர்: சரத்து 52–62; சரத்து 74 அமைச்சரவை ஆலோசனை (ஷம்ஷேர் சிங் 1974); சரத்து 123 அவசரச் சட்டம்; பாக்கெட் வீட்டோ: மசோதாவில் கையெழுத்திடாமல் வைத்தல்.",
             "இந்திரா காந்தி - ராஜ் நாராயண்: ரேபரேலி 1971; அலகாபாத் உயர் நீதிமன்றம் 12.6.1975; நீதிபதி சின்ஹா; நெருக்கடி நிலை 25.6.1975.",
             "எஸ்.ஆர். போம்மை 11.3.1994: 9 நீதிபதிகள்; சரத்து 356 மறுஆய்வுக்கு உட்பட்டது; பெரும்பான்மை சட்டசபையில்; சரத்து 32 உச்ச நீதிமன்றம், சரத்து 226 உயர் நீதிமன்றம்."]},
          open("tools/story/con5.json", "w"), ensure_ascii=False, indent=1)
print(n, "shots", sum(len(s["nar"]) for s in out), "chars; thumb", thumb)
