# Builds tools/story/con4.json: Indian Constitution series, part 4 - Directive Principles and Fundamental Duties (approved 2026-11-28, "Script ok").
# Facts checked 2026-11-28: Shah Bano (divorced 1978 aged 62; HC raised maintenance to Rs 179.20 on 1.7.1980; SC 23.4.1985, 5 judges, CJ Chandrachud,
# Art 44 'dead letter'; 1986 Act by Rajiv Gandhi govt - Wikipedia); Minerva Mills 1980 (5 judges, 4:1, Bhagwati dissent, Chandrachud quote - GKToday);
# Hussainara Khatoon 1979 (undertrials held 5-10 years for 2-3 year offences, Art 21, Art 39A - GKToday); original Art 45 ten-year deadline, 86th Amendment 2002;
# Fundamental Duties: 42nd Amendment 1976, Swaran Singh Committee, 10 duties, 11th by 86th Amendment 2002 (GKToday); P.S. Deshmukh 30.8.1947 Irish remark (constitutionofindia.net).
import json
C = {
 "SHA": "an elderly Indian Muslim woman in a simple white cotton saree with a head covering, standing outside a court building holding a small bundle of papers, dignified and tired",
 "CHA": "Chief Justice Y. V. Chandrachud, an elderly Indian judge in a black robe and white bands, seated at the centre of a five-judge bench",
 "BHA": "Justice P. N. Bhagwati, a thoughtful Indian judge in a black robe and white bands, seated alone at the end of a bench with a dissenting note",
 "PRI": "thin Indian undertrial prisoners in grey cotton clothes behind an old iron jail gate, hopeful faces turned toward a golden light",
 "KID": "three small Indian school children in uniform standing respectfully and silently in a school assembly while others sing, a teacher looking on",
 "PEO": "ordinary Indian citizens, farmers, women, students and workers, standing together in a crowd looking hopeful, golden light",
 "AMB": "Dr B. R. Ambedkar, a dignified Indian scholar in a dark three-piece suit and round glasses, holding a thick draft book",
}
G = [
("tense and curious, a small sum that shook India",
 [("1978-ல ஷா பானோவுக்கு 62 வயசு. அவருக்கு விவாகரத்து ஆச்சு. உயர் நீதிமன்றம் மாசம் 179 ரூபாய் 20 பைசா ஜீவனாம்சம் தந்துச்சு. அந்தச் சின்னத் தொகைக்காக நடந்த வழக்கு, இந்தியாவையே உலுக்கிச்சு.", "{SHA}, with a bold glowing number 179.20 floating in the sky above her, dramatic light.", "₹179.20", ""),
  ("1985 ஏப்ரல் 23. 5 நீதிபதிகள். தலைமை நீதிபதி சந்திரசூட். ஜீவனாம்சம் தரணும்னு தீர்ப்பு. அவர் சொன்னார், சரத்து 44 இறந்த எழுத்தா கிடக்குதுன்னு. அது என்ன சரத்து? அதுதான் இந்த பகுதியோட கதை. இந்திய அரசியலமைப்பு உருவான கதை, பகுதி 4.", "{CHA} reading out a verdict, a glowing page marked 44 floating above the bench, a lit lamp, courtroom shadows.", "சரத்து 44?", "")]),
("steady storyteller, the Directive Principles",
 [("அரசியலமைப்போட நாலாவது பகுதி, சரத்து 36 முதல் 51 வரை. இதுதான் வழிகாட்டு நெறிகள். அரசாங்கம் நாட்டை எப்படி நடத்தணும்னு அரசியலமைப்பு தர்ற பட்டியல்.", "A glowing checklist scroll unrolling over the Indian Parliament building with golden ticks, deep blue sky.", "சரத்து 36 – 51", ""),
  ("1947-ல விவாதத்தப்ப, பி.எஸ். தேஷ்முக் குறை சொன்னார். நாம அயர்லாந்து அரசியலமைப்பையே காப்பி அடிக்கிறோம்னு. அந்த அளவுக்கு அந்த நாட்டோட தாக்கம் இதுல இருந்துச்சு.", "A Constituent Assembly member in a white cap pointing at an open book with a green Irish flag symbol while others listen, a packed hall.", "அயர்லாந்து தாக்கம்", ""),
  ("இதுல ஒரு விசித்திரம் இருக்கு. சரத்து 37 சொல்லுது, இந்த நெறிகளை அரசு நிறைவேத்தலைன்னா, நீதிமன்றத்துல வழக்குப் போட முடியாது. அதனால இது கோர்ட்டில் கேட்க முடியாத சட்டம். ஆனா நாட்டை நடத்த வேண்டிய கடமை அரசுக்கு உண்டு.", "A courtroom door with a golden lock and a glowing scroll beyond it that nobody can reach, a worried citizen at the door.", "கோர்ட்டில் கேட்க முடியாது!", ""),
  ("இதுக்கு ஒரு உதாரணம், சம்பகம் வழக்கு, 1951. பகுதி 1-ல பார்த்தது. வழிகாட்டு நெறி எவ்வளவு பெரிசா இருந்தாலும், அடிப்படை உரிமையை மீற முடியாதுன்னு நீதிமன்றம் அப்போ சொன்னது.", "A balance scale in a dim courtroom where the Fundamental Rights side is heavier than a small Directive scroll, dramatic side light.", "சம்பகம் 1951", "")]),
("clear and moving, examples that changed lives",
 [("சரத்து 39A, ஏழைக்கு இலவசச் சட்ட உதவி. உதாரணம், ஹுசைனாரா காத்துன் வழக்கு, 1979. இந்தியன் எக்ஸ்பிரஸ் செய்தித்தாளோட செய்திகளுக்குப் பிறகு, கபிலா ஹிங்கோரணி சரத்து 32-ல மனு போட்டார்.", "{PRI}, a newspaper headline page glowing in the foreground, a lawyer woman in a black coat walking toward a court.", "ஹுசைனாரா காத்துன்", ""),
  ("பீகார் சிறைகளில் ஆயிரக்கணக்கான விசாரணைக் கைதிகள். 2 அல்லது 3 வருஷ தண்டனைக்கான குற்றத்துக்கு, 5 முதல் 10 வருஷமா, விசாரணையே இல்லாம கிடந்தாங்க.", "A long prison corridor with many cells and calendars on the walls showing years passing, grey and amber light.", "5 – 10 வருஷம்!", ""),
  ("தீர்ப்பு, விரைவான விசாரணை சரத்து 21-ன் பகுதி. ஏழைக்கு இலவச வழக்கறிஞர் அரசோட கடமை. தண்டனைக்காலத்தை விட அதிகமா சிறையில இருந்தவங்க உடனே விடுதலை.", "{PRI} walking out of an open prison gate into a bright golden dawn, family members waiting with open arms.", "கைதிகளுக்கு விடுதலை", ""),
  ("சரத்து 45-ல ஒரு காலக்கெடு இருந்துச்சு. 1950-ல சொன்னது, 10 வருஷத்துல 14 வயசு வரை எல்லாக் குழந்தைக்கும் இலவசக் கட்டாயக் கல்வி. அதாவது 1960-க்குள்ள.", "A calendar page showing the year 1960 circled in red, a school gate behind it with an empty classroom and a tired teacher.", "10 வருஷ காலக்கெடு", ""),
  ("நிஜமா நடந்தது 2002-ல. 86-வது திருத்தத்துல சரத்து 21A வந்துச்சு. 42 வருஷம் தாமதம்.", "A huge old clock wheel turning with a glowing number 42 and a new bright school with children running in at sunrise.", "42 வருஷ தாமதம்", ""),
  ("சரத்து 40, கிராமப் பஞ்சாயத்து. காந்தியோட கிராம சுயராஜ்ய கனவு. அது நிஜமானது 1992-ல, 73-வது திருத்தத்துல.", "A village panchayat meeting under a banyan tree with men and women of all ages sitting in a circle, warm golden evening light.", "73-வது திருத்தம்", ""),
  ("சரத்து 44, பொது சிவில் சட்டம். ஷா பானோ தீர்ப்புக்குப் பிறகு, 1986-ல ராஜீவ் காந்தி அரசு அந்தத் தீர்ப்பைச் சரிசெய்ய ஒரு சட்டம் இயற்றுச்சு. இந்த விவாதம் இன்னைக்கும் தொடருது.", "A glowing question mark over the Indian Parliament with a crowd split in two groups below, tense dusk light.", "பொது சிவில் சட்டம்", "")]),
("dramatic, rights versus principles",
 [("1976 அவசரநிலை காலத்துல 42-வது திருத்தம் வந்துச்சு. வழிகாட்டு நெறிகளுக்கு அடிப்படை உரிமைகளை விட முன்னுரிமை தர முயற்சி.", "A giant stamp labelled 42 pressing down on a book labelled Fundamental Rights, dark red emergency-era mood, a lit lamp flickering.", "42-வது திருத்தம்", ""),
  ("மினர்வா மில்ஸ், 1980. கர்நாடகாவோட ஜவுளி ஆலை, அரசு தேசியமாக்கினதை எதிர்த்தது. அவங்க அந்தத் திருத்தத்தையே சவால் பண்ணினாங்க. 5 நீதிபதிகள், 4க்கு 1 தீர்ப்பு.", "A textile mill with spinning looms and idle workers outside, a five-judge bench glowing in a frame above, the numbers 4 and 1 in gold.", "மினர்வா மில்ஸ் 1980", ""),
  ("அந்த ஒரு நீதிபதி பகவதி. மேனகா காந்தி தீர்ப்பு எழுதினவர் அவர்தான். பகுதி 3-ல பார்த்தோம். இங்க அவர் தனியா எதிர்த்தார்.", "{BHA} alone at the end of the bench with his hand raised in disagreement, the other four judges looking at him, dramatic light.", "பகவதியின் தனி எதிர்ப்பு", ""),
  ("தீர்ப்பு, உரிமைகளுக்கும் நெறிகளுக்கும் இடையில இணக்கம் இருக்கணும், அது அரசியலமைப்போட அடிப்படைக் கட்டமைப்பு. சந்திரசூட் சொன்னார், ஒண்ணுக்கு முழு முன்னுரிமை தந்தா, அரசியலமைப்போட இசையே கெட்டுடும்.", "{CHA} speaking from the bench with two golden pillars labelled Rights and Principles standing balanced beside him, a harmonious golden glow.", "இணக்கம் வேணும்", "")]),
("hopeful and clear, the Fundamental Duties",
 [("1976-ல ஸ்வரண் சிங் குழு பரிந்துரை செஞ்சுது. அதே 42-வது திருத்தம் பகுதி IVA-வையும், சரத்து 51A-வையும் சேர்த்துச்சு. முதல்ல 10 அடிப்படைக் கடமைகள்.", "A glowing document labelled 51A being added to the Indian Constitution book by a pen, ten golden icons around it, deep blue background.", "சரத்து 51A", ""),
  ("முதல் கடமை, அரசியலமைப்பு, தேசியக் கொடி, தேசிய கீதத்துக்கு மரியாதை. பகுதி 3-ல பார்த்த பிஜோ இம்மானுவேல் குழந்தைகள் நினைவிருக்கா? அவங்க பாடலை, ஆனா மரியாதையா எழுந்து நின்னாங்க. அதை நீதிமன்றம் மதிச்சது.", "{KID}, warm morning light, a tricolour on the wall behind them.", "மரியாதையா நின்னாங்க", ""),
  ("சுற்றுச்சூழலைக் காக்கணும், அறிவியல் மனப்பான்மை வளர்க்கணும், பொதுச் சொத்தைப் பாதுகாக்கணும். இவையும் கடமைகளே.", "Citizens planting trees and cleaning a river bank, a tricolour and a lit lamp, bright morning light.", "மரம், சொத்து, அறிவியல்", ""),
  ("2002-ல அதே 86-வது திருத்தம் 11-வது கடமையைச் சேர்த்துச்சு. 6 முதல் 14 வயசு வரை குழந்தைக்கு கல்வி தர வேண்டியது பெற்றோரோட கடமை. அதாவது உரிமையும் கடமையும் ஒரே திருத்தத்துல.", "A mother and father walking a small child to a school gate under a golden sunrise, a glowing number 11 above them.", "11-வது கடமை", ""),
  ("ஏய்ம்ஸ் மாணவர் சங்க வழக்குல நீதிமன்றம் சொன்னது, கடமைகள் வெறும் அலங்காரமா இருக்கக் கூடாது. சட்டங்களைப் புரிஞ்சுக்க உதவணும்.", "A judge's gavel resting on an open copy of Article 51A with golden light spilling out of it, a students' union banner behind.", "அலங்காரம் இல்லை", "")]),
("calm and forward-looking, the close",
 [("தேர்வுக்கு நினைவு வச்சுக்கோங்க. சரத்து 36 முதல் 51, நெறிகள். சரத்து 51A, கடமைகள். 42-வது திருத்தம், 1976. 86-வது திருத்தம், 2002. மினர்வா மில்ஸ், 1980.", "A chalkboard style golden notice with five short glowing tags beside the Indian Constitution book, a lit lamp, warm light.", "தேர்வு குறிப்பு", ""),
  ("அடுத்த பகுதியில நாடாளுமன்றம், குடியரசுத் தலைவர், நீதித்துறை பத்திப் பார்க்கலாம். சேனலை subscribe பண்ணுங்க.", "Hands holding a glowing palm-leaf scroll beside the Indian Constitution book, a lit lamp, warm golden light, a promise of the next part.", "", "")]),
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
thumb = [first("1978-ல ஷா"), first("மினர்வா"), first("நிஜமா நடந்தது")]
json.dump({"title": "கோர்ட்டில் கேட்க முடியாத சட்டம்! வழிகாட்டு நெறிகளும் கடமைகளும் – பகுதி 4", "shots": out, "scenes": scenes, "anims": {}, "thumb": thumb,
           "shorts": [[first("1978-ல ஷா"), first("1985 ஏப்ரல்"), "179 ரூபாய் வழக்கு இந்தியாவை உலுக்கியது!", "ஷா பானோ வழக்கு"],
                      [first("சரத்து 45-ல"), first("நிஜமா நடந்தது"), "42 வருஷம் தாமதமான கல்வி உரிமை!", "சரத்து 45, 21A"],
                      [first("மினர்வா"), first("அந்த ஒரு நீதிபதி"), "நீதிபதி பகவதியின் தனி எதிர்ப்பு!", "மினர்வா மில்ஸ் வழக்கு"]],
           "exam_cards": [
             "வழிகாட்டு நெறிகள்: பகுதி IV, சரத்து 36–51; அயர்லாந்து அரசியலமைப்பின் தாக்கம்; சரத்து 37: நீதிமன்றத்தில் அமல்படுத்த முடியாது. சம்பகம் 1951: உரிமை மேலானது.",
             "சரத்து 39A இலவசச் சட்ட உதவி; ஹுசைனாரா காத்துன் 1979: விரைவான விசாரணை சரத்து 21. சரத்து 40 பஞ்சாயத்து: 73-வது திருத்தம் 1992.",
             "சரத்து 45 (1950): 10 ஆண்டுக் காலக்கெடு; 86-வது திருத்தம் 2002: சரத்து 21A (6–14 வயது), சரத்து 45 இப்போது 6 வயதுக்குக் கீழ்.",
             "ஷா பானோ 23.4.1985: 5 நீதிபதிகள், தலைமை நீதிபதி சந்திரசூட், சரத்து 44; 1986 சட்டம். மினர்வா மில்ஸ் 1980: 5 நீதிபதிகள், 4-1, உரிமை-நெறி இணக்கம் அடிப்படைக் கட்டமைப்பு.",
             "அடிப்படைக் கடமைகள்: 42-வது திருத்தம் 1976, ஸ்வரண் சிங் குழு, சரத்து 51A, பகுதி IVA, 10 கடமைகள்; 86-வது திருத்தம் 2002: 11-வது கடமை."]},
          open("tools/story/con4.json", "w"), ensure_ascii=False, indent=1)
print(n, "shots", sum(len(s["nar"]) for s in out), "chars; thumb", thumb)
