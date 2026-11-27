# Builds tools/story/con3.json: Indian Constitution series, part 3 - Fundamental Rights and the Maneka Gandhi case
# (richer script approved by the owner 2026-11-27, "ஸ்கிரிப்ட் ஓகே ரெடி பண்ணு").
# Facts checked 2026-11-27: Puttaswamy 24.8.2017, 9 judges, unanimous, overruled M.P. Sharma and Kharak Singh (SC Observer);
# Ambedkar called Article 32 the "heart and soul" of the Constitution (Outlook India); Article 21A by the 86th Amendment 2002.
import json
C = {
 "MAN": "an Indian woman journalist in a simple 1970s cotton saree holding a passport booklet, standing outside a government office, worried but dignified",
 "OFF": "a stern Indian government clerk in a grey safari suit stamping a file marked IMPOUNDED at a wooden desk in a 1970s passport office",
 "BEG": "Chief Justice M. H. Beg, an elderly Indian judge in a black robe and white bands, seated at the centre of a seven-judge Supreme Court bench",
 "BHA": "Justice P. N. Bhagwati, a thoughtful Indian judge in a black robe and white bands, writing a judgment at a large desk piled with law books",
 "KID": "three small Indian school children in uniform standing respectfully and silently in a school assembly while others sing, a teacher looking on",
 "KRI": "J. B. Kripalani, an elderly Indian leader in a white khadi dhoti-kurta with spectacles, leading a committee meeting around a long table with draft papers",
 "AMB": "Dr B. R. Ambedkar, a dignified Indian scholar in a dark three-piece suit and round glasses, holding a thick draft book",
 "PEO": "ordinary Indian citizens, farmers, women, students and workers, standing together in a crowd looking hopeful, golden light",
}
G = [
("tense and curious, a surprising opening",
 [("1977 ஜூலை 2. மேனகா காந்தி வெளிநாடு போக தயாரா இருந்தாங்க. அரசு திடீர்னு அவங்க பாஸ்போர்ட்டைப் பறிமுதல் செஞ்சுது. 7 நாள்ல ஒப்படைக்கணும்னு உத்தரவு. காரணம் கேட்டா, சொல்ல முடியாதுன்னு பதில்.", "{MAN}, with a bold official order paper in her hand and a red IMPOUNDED stamp glowing on the passport, dramatic light.", "பாஸ்போர்ட் பறிமுதல்!", ""),
  ("ஒரு குடிமகனோட பாஸ்போர்ட்டை, காரணமே சொல்லாம பறிக்க முடியுமா? இந்தக் கேள்வி இந்தியாவோட உரிமைகளையே மாத்திச்சு. இந்திய அரசியலமைப்பு உருவான கதை, பகுதி 3.", "A glowing question mark made of golden light above the closed Indian Constitution book, a lit lamp on a dark wooden table.", "", "")]),
("steady storyteller, the history of rights",
 [("இந்த உரிமைகள் திடீர்னு வரலை. 1928-ல மோதிலால் நேரு அறிக்கையிலேயே அடிப்படை உரிமைகளைக் கேட்டாங்க. சுதந்திரப் போராட்டத்தோட கனவு அது.", "Indian freedom fighters in khadi around a table reading a thick report titled with the year 1928, sepia and golden light.", "நேரு அறிக்கை 1928", ""),
  ("1947-ல அரசியலமைப்புச் சபையோட ஆலோசனைக் குழு, சர்தார் படேல் தலைமையில அமைஞ்சுது. அதுக்குள்ள, ஜே.பி. கிருபளானி தலைமையில ஒரு உப குழு உரிமைகளை வடிவமைச்சுது. அமெரிக்க உரிமைச் சட்டத்தையும் பார்த்தாங்க.", "{KRI}, a map of the world and an old American Bill of Rights scroll on the table, warm lamp light.", "கிருபளானி உப குழு", ""),
  ("அந்த உரிமைகள் அரசியலமைப்போட மூன்றாம் பகுதியில, சரத்து 12 முதல் 35 வரை இருக்கு. இதை இந்தியாவோட மேக்னா கார்ட்டான்னு சொல்வாங்க.", "A grand golden gate labelled with the numbers 12 and 35 opening onto a bright field with the Indian tricolour, deep blue sky.", "சரத்து 12 – 35", "")]),
("clear and rhythmic, the six rights with examples",
 [("ஆறு அடிப்படை உரிமைகள் இருக்கு. சமத்துவம், சுதந்திரம், சுரண்டலுக்கு எதிரான உரிமை, சமய சுதந்திரம், கலாச்சார கல்வி உரிமை, அரசியலமைப்பு தீர்வு உரிமை.", "Six glowing golden medallions arranged in a circle around a small Indian Constitution book, each with a different symbol, deep blue background.", "6 அடிப்படை உரிமைகள்", ""),
  ("சமத்துவத்துல சரத்து 17 தீண்டாமையை ஒழிச்சுது. பகுதி 1-ல பார்த்த சம்பகம் வழக்கும் இந்தச் சம வாய்ப்பு உரிமை பத்தினதுதான். அதனாலதான் 1951-ல முதல் திருத்தம் வந்துச்சு.", "A broken chain falling from many hands of different people raised together under a golden sunrise, a lit lamp beside them.", "சரத்து 17", ""),
  ("பேச்சு சுதந்திரத்துக்கு ஒரு உதாரணம், பிஜோ இம்மானுவேல் வழக்கு. 1985-ல கேரளாவுல மூணு குழந்தைகள் தேசிய கீதம் பாட மறுத்ததால பள்ளியிலிருந்து நீக்கப்பட்டாங்க. அவங்க மரியாதையா எழுந்து நின்னாங்க, பாடலை. 1986-ல உச்ச நீதிமன்றம், பாடாம இருக்கிறதும் ஒரு உரிமைன்னு சொல்லி, நீக்கத்தை ரத்து செஞ்சுது.", "{KID}, warm morning light, a tricolour on the wall behind them.", "பிஜோ இம்மானுவேல் வழக்கு", ""),
  ("சரத்து 23, கட்டாய உழைப்பையும் மனிதக் கடத்தலையும் தடை செய்யுது. சரத்து 24, 14 வயசுக்குக் கீழே குழந்தைகளை ஆபத்தான வேலைகளுக்கு அனுப்பக் கூடாதுன்னு சொல்லுது.", "A child dropping a heavy brick and running joyfully toward a school gate, a golden rising sun, a hand removing a chain from a worker's wrist.", "சரத்து 23, 24", ""),
  ("சரத்து 25 முதல் 28, சமய சுதந்திரம். சரத்து 29, 30, சிறுபான்மையினர் தங்கள் மொழி, கலாச்சாரத்தைக் காக்கவும், தங்கள் பள்ளிகளை நடத்தவும் உரிமை தருது.", "A temple, a mosque, a church and a gurdwara standing side by side under one tricolour sky, golden light, children of all communities playing in front.", "சரத்து 25 – 30", ""),
  ("ஆரம்பத்துல சொத்துரிமையும் அடிப்படை உரிமைதான். 1978-ல 44-வது திருத்தம் அதை நீக்குச்சு. இப்போ சரத்து 300A-ல சட்ட உரிமையா மட்டும் இருக்கு.", "A wooden farm gate and a small house with a title deed paper moving from one shelf marked fundamental to another marked legal, calm light.", "சொத்துரிமை 1978", "")]),
("dramatic, the court battle for Article 21",
 [("மறுபடி மேனகா காந்தி கதைக்கு வருவோம். அவங்க சரத்து 32-ல நேரா உச்ச நீதிமன்றம் போனாங்க. 7 நீதிபதிகள் அமர்வு விசாரிச்சுது.", "{MAN} walking up the wide steps of the Supreme Court of India with a file under her arm, reporters and a crowd watching, dramatic dawn light.", "உச்ச நீதிமன்றத்தில்", ""),
  ("இதுக்கு முன்னாடி 1950-ல ஏ.கே. கோபாலன் வழக்குல நீதிமன்றம் சொன்னது இது. சரத்து 21, சட்டம் வகுத்த நடைமுறைன்னு சொல்லுது. சட்டம் இருந்தா போதும், நியாயமா இருக்கணும்னு அவசியமில்லை. அதனால அரசு பலமா இருந்துச்சு.", "A heavy law book labelled 1950 with a thin line of text, a tall government official standing proudly behind it, a dim courtroom.", "கோபாலன் வழக்கு 1950", ""),
  ("1978 ஜனவரி 25. தலைமை நீதிபதி எம்.எச். பேக் தலைமையில தீர்ப்பு வந்துச்சு. நீதிபதி பகவதி சொன்னார். நடைமுறை சரியானதா, நியாயமானதா, முறையானதா இருக்கணும். தன்னிச்சையா இருக்கக் கூடாது.", "{BHA} reading out a verdict while {BEG} listens on the bench, the words RIGHT, JUST AND FAIR glowing in gold above them.", "சரியான, நியாயமான, முறையான", ""),
  ("இதுதான் தங்க முக்கோணம். சரத்து 14 சமத்துவம், சரத்து 19 சுதந்திரம், சரத்து 21 உயிர் வாழும் உரிமை. எந்தச் சட்டமும் இந்த மூணையும் தாண்டியாகணும்.", "A glowing golden triangle with Article 14, 19 and 21 on its three corners, shining over the Supreme Court building at dusk.", "தங்க முக்கோணம்", ""),
  ("ஆனா சுவாரஸ்யம் என்னன்னா, அந்த பாஸ்போர்ட் உத்தரவை நீதிமன்றம் ரத்து செய்யலை. ஆனா சட்டத்துக்குப் புது அளவுகோல் குடுத்துச்சு. இனிமே எந்த அரசும், எந்தக் குடிமகனோட சுதந்திரத்தையும் தன்னிச்சையா பறிக்க முடியாது.", "A stamped IMPOUNDED order paper still lying on a desk but a golden shield now standing over a citizen's silhouette, courtroom background.", "புது அளவுகோல்", ""),
  ("இந்தத் தீர்ப்புக்குப் பிறகு சரத்து 21-க்குப் பெரிய பொருள் கிடைச்சுது. சுத்தமான சுற்றுச்சூழல், விரைவான விசாரணை, கண்ணியத்தோட வாழும் உரிமை எல்லாம் இதுக்குள்ள வந்துச்சு.", "{PEO}, with a clean river, a school and a hospital glowing behind them, bright optimistic light.", "சரத்து 21-ன் வளர்ச்சி", "")]),
("hopeful and sharp, the impact today",
 [("2017 ஆகஸ்ட் 24. ஆதார் வழக்குல, ஓய்வு பெற்ற நீதிபதி கே.எஸ். புட்டசாமி தொடுத்த மனுவுல 9 நீதிபதிகள் ஒருமனதா தீர்ப்பு சொன்னாங்க. தனிநபர் தனிமை, அதாவது ப்ரைவசி, அடிப்படை உரிமை. அதுவும் சரத்து 21-ல இருந்துதான்.", "A glowing padlock hovering over a smartphone and a fingerprint, nine judges' silhouettes in a golden arc behind, dark blue background.", "தனிமை உரிமை 2017", ""),
  ("2002-ல 86-வது திருத்தம், சரத்து 21A-ஐச் சேர்த்து, 6 முதல் 14 வயசு வரை இலவசக் கட்டாயக் கல்வியை அடிப்படை உரிமையாக்குச்சு.", "Smiling Indian school children running into a bright school with books, a glowing number 21A above the gate.", "சரத்து 21A", ""),
  ("உரிமை இருந்தும், அதைக் காக்க வழி இல்லன்னா பயன் இல்லை. அதனாலதான் சரத்து 32. நேரா உச்ச நீதிமன்றம் போகலாம். அம்பேத்கர் இதை அரசியலமைப்போட இதயமும் ஆன்மாவும்னு சொன்னார்.", "{AMB} with a hand on his heart in the Constituent Assembly, a glowing heart shape of golden light over the Constitution book.", "சரத்து 32", ""),
  ("தேர்வுக்கு நினைவு வச்சுக்கோங்க. சரத்து 12 முதல் 35, ஆறு உரிமைகள், மேனகா காந்தி 1978, 7 நீதிபதிகள், தங்க முக்கோணம், சரத்து 14, 19, 21.", "A chalkboard style golden notice with five short glowing tags beside the Indian Constitution book, a lit lamp, warm light.", "தேர்வு குறிப்பு", ""),
  ("அடுத்த பகுதியில வழிகாட்டு நெறிகளையும், அடிப்படைக் கடமைகளையும் பார்க்கலாம். சேனலை subscribe பண்ணுங்க.", "Hands holding a glowing palm-leaf scroll beside the Indian Constitution book, a lit lamp, warm golden light, a promise of the next part.", "", "")]),
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
thumb = [first("1977 ஜூலை"), first("1978 ஜனவரி"), first("இதுதான் தங்க")]
json.dump({"title": "பாஸ்போர்ட்டைப் பறித்த அரசு! உரிமைகளையே மாற்றிய மேனகா காந்தி வழக்கு – பகுதி 3", "shots": out, "scenes": scenes, "anims": {}, "thumb": thumb,
           "shorts": [[first("1977 ஜூலை"), first("ஒரு குடிமகனோட"), "காரணமே சொல்லாம பாஸ்போர்ட் பறிப்பு!", "மேனகா காந்தி வழக்கு"],
                      [first("பேச்சு சுதந்திரத்துக்கு"), first("பேச்சு சுதந்திரத்துக்கு"), "தேசிய கீதம் பாட மறுத்த குழந்தைகள்!", "பிஜோ இம்மானுவேல் வழக்கு"],
                      [first("1978 ஜனவரி"), first("இதுதான் தங்க"), "நீதிமன்றம் தந்த தங்க முக்கோணம்!", "சரத்து 14, 19, 21"]],
           "exam_cards": [
             "அடிப்படை உரிமைகள்: பகுதி III, சரத்து 12–35. ஆறு உரிமைகள்: சமத்துவம், சுதந்திரம், சுரண்டலுக்கு எதிரான, சமய, கலாச்சார-கல்வி, அரசியலமைப்பு தீர்வு.",
             "நேரு அறிக்கை 1928 உரிமைகளைக் கேட்டது. அடிப்படை உரிமைகள் உப குழு தலைவர்: ஜே.பி. கிருபளானி. ஆலோசனைக் குழு தலைவர்: சர்தார் படேல்.",
             "மேனகா காந்தி 25.1.1978: 7 நீதிபதிகள், தலைமை நீதிபதி எம்.எச். பேக். சரத்து 14, 19, 21 தங்க முக்கோணம். நடைமுறை சரியான, நியாயமான, முறையானதாக இருக்கணும். ஏ.கே. கோபாலன் 1950.",
             "பிஜோ இம்மானுவேல் 1986: தேசிய கீதம் பாட மறுப்பு சரத்து 19(1)(a), 25-ல் பாதுகாப்பு. சொத்துரிமை 44-வது திருத்தம் 1978: சரத்து 300A.",
             "புட்டசாமி 24.8.2017: 9 நீதிபதிகள், தனிமை உரிமை சரத்து 21-ல். சரத்து 21A (86-வது திருத்தம் 2002): 6–14 வயது கல்வி. சரத்து 32: அம்பேத்கர் 'இதயமும் ஆன்மாவும்'."]},
          open("tools/story/con3.json", "w"), ensure_ascii=False, indent=1)
print(n, "shots", sum(len(s["nar"]) for s in out), "chars; thumb", thumb)
