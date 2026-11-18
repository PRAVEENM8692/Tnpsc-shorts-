# Builds tools/story/tn3.json: Tamil Nadu history part 3 - Later Cholas, Vijayalaya to Rajaraja I (approved by the owner 2026-11-18).
import json
C = {
 "VIJ": "Vijayalaya Chola, a lean determined warrior king with a thick moustache, a small gold crown, a saffron-red cloth and a sword, tiger emblem on his shield",
 "ADI": "Aditya Chola, a powerful warrior king with a broad chest, a gold crown, a thick moustache and a bow, tiger emblem on his banner",
 "PAR": "Parantaka Chola, a regal king with a gold crown, heavy jewellery, a trimmed beard and a proud look, a tiger banner behind him",
 "KAR": "Aditya Karikalan, a handsome fierce young Chola prince with long hair, a gold headband and a sword",
 "SEM": "Sembiyan Mahadevi, an elegant elderly Chola queen in a simple white sari and jewellery, calm and devout",
 "RAJ": "Rajaraja Chola, a majestic king with a gold crown, a strong build, a trimmed moustache, rich jewellery and a calm commanding look, tiger banner behind him",
 "NAM": "Nambiyandar Nambi, an elderly temple priest with a shaved head, sacred ash on his forehead and a palm-leaf bundle",
}
G = [
("awed and mysterious, a huge temple tower at dawn, then a hint of secret",
 [("இந்தக் கோயிலோட கோபுரம் 216 அடி. 1,000 வருஷத்துக்கு முன்னாடி, கிரேன் இல்லாத காலத்துல கட்டினது.", "The huge Brihadisvara temple tower of Thanjavur rising into a golden sunrise sky, tiny people at its base, no machines anywhere.", "தஞ்சாவூர் பெரிய கோயில்", ""),
  ("கட்டினவன் ஒரு அரசன். ஆனா அவன் அரசனான கதை, ஒரு மர்மத்துல தொடங்குது.", "{RAJ} standing in shadow looking up at a glowing mystery question mark above the temple tower at dusk.", "", ""),
  ("தமிழ்நாட்டு வரலாறு, பகுதி 3. பிற்காலச் சோழர்கள்.", "An old open palm-leaf book glowing on a wooden table with a lit brass lamp and a tiger emblem, green Kaveri fields behind.", "", "")]),
("calm storyteller, the quiet rise of a small kingdom",
 [("பல்லவர் காலம் முடியுது. காவிரிக் கரையில ஒரு சின்ன அரசு மெல்ல எழுது.", "The green fertile banks of the Kaveri river at sunrise with a small village fort and a tiger flag slowly rising.", "", ""),
  ("சுமார் 850-ல விஜயாலய சோழன் தஞ்சாவூரைக் கைப்பற்றினான். அங்க நிசும்பசூதனிக்கு ஒரு கோயிலும் கட்டினான்.", "{VIJ} entering the gates of Thanjavur with his soldiers, a small goddess temple being built nearby.", "விஜயாலயன்", ""),
  ("அவன் மகன் ஆதித்த சோழன். பல்லவ மன்னன் அபராஜிதனை, திருப்புறம்பியம் போர்க்களத்துல தோற்கடிச்சான்.", "{ADI} on a war elephant charging in a fierce battlefield, a defeated Pallava lion banner falling.", "திருப்புறம்பியம்", ""),
  ("பல்லவ வம்சம் அத்தோட முடிஞ்சுது. காவிரிக் கரையில வரிசையா சிவன் கோயில்கள் கட்டினான்.", "A row of small stone Shiva temples along the green Kaveri river bank under a golden evening sky, a tiger flag over each.", "", ""),
  ("அவன் மகன் முதலாம் பராந்தகன். மதுரையைப் பிடிச்சு, மதுரை கொண்டான்னு பட்டம் வாங்கினான்.", "{PAR} entering the gates of Madurai on a decorated elephant, the Meenakshi temple towers behind, crowds watching.", "மதுரை கொண்டான்", ""),
  ("சிதம்பரம் நடராஜர் கோயில் கூரையில பொன் வேய்ஞ்சவனும் இவன்தான்னு சொல்றாங்க.", "Craftsmen covering the roof of the Chidambaram Nataraja temple with shining gold sheets, {PAR} watching from below.", "சிதம்பரம்", ""),
  ("ஆனா 949-ல தக்கோலம் போர்க்களத்துல, ராஷ்டிரகூடரிடம் சோழர் படை தோத்துச்சு. பட்டத்து இளவரசன் இராஜாதித்தன் யானை மேல இருக்கும்போதே கொல்லப்பட்டான்.", "A sad battlefield with a Chola prince falling from a war elephant, Rashtrakuta soldiers with green banners advancing, dusty sunset.", "தக்கோலம் 949", "")]),
("proud and amused, surprised that a thousand years ago people voted",
 [("ஆனா இவன் காலத்துக்கு ஒரு பெருமையும் இருக்கு. உத்தரமேரூர் கல்வெட்டு.", "A long stone wall of a village temple fully covered with carved Tamil inscriptions, a scholar pointing at the writing.", "உத்தரமேரூர்", ""),
  ("919-ஆம் ஆண்டு அந்த ஊர் சபை எப்படி நடந்ததுன்னு கல்லுல எழுதியிருக்காங்க.", "A village assembly of elders sitting in a pillared temple hall, a scribe carving words onto a stone wall.", "", ""),
  ("உறுப்பினர்களை குடவோலை முறையில தேர்ந்தெடுத்தாங்க. ஓலையில பேரு எழுதி, பானையில போட்டு, ஒரு சின்னப் பையன் எடுப்பான்.", "A small boy with closed eyes pulling a palm-leaf slip out of a large clay pot while elders and villagers watch, in a temple hall.", "குடவோலை", ""),
  ("ஆயிரம் வருஷத்துக்கு முன்னாடியே, தேர்தல் விதிகள் கல்லுல இருந்துச்சு. தகுதிக்கும் விதி. சொத்து கணக்கு காட்டாதவங்க நிற்க முடியாது.", "A village elder reading election rules from a stone wall to a crowd, one man being turned away at the door holding his empty ledger.", "", "")]),
("tense and dramatic, a palace mystery",
 [("அடுத்து சோழ அரசு தள்ளாடுச்சு. இளவரசன் ஆதித்த கரிகாலன், கடம்பூர் மாளிகையில மர்மமா கொல்லப்பட்டான்.", "{KAR} lying fallen in a dark palace hall at night with flickering lamps and shadowy figures at the doorway.", "கடம்பூர் மாளிகை", ""),
  ("யார் கொன்னாங்கன்னு இன்னும் முழுசா தெரியாது. இந்தக் கதையைத்தான் கல்கி பொன்னியின் செல்வன்னு எழுதினார்.", "A writer with a pen in an old study writing a novel, behind him a ghostly scene of the Chola palace and a large question mark.", "பொன்னியின் செல்வன்", ""),
  ("அந்தக் காலத்துல கண்டராதித்தரோட மனைவி, செம்பியன் மாதேவி, செங்கல் கோயில்களை கல் கோயில்களா மாத்தினாங்க.", "{SEM} watching workers replace an old brick temple with carved stone walls, sculptures being chiselled.", "செம்பியன் மாதேவி", "")]),
("excited and grand, the great king arrives",
 [("இப்போ 985. ஒரு இளவரசன் அரியணை ஏறுறான். அருண்மொழிவர்மன். காவிரியோட செல்லப் பிள்ளைன்னு, பொன்னியின் செல்வன்.", "{RAJ} being crowned in a grand golden court hall as ministers and priests pour sacred water, banners waving.", "985", ""),
  ("நாம அவனை இராஜராஜ சோழன்னு சொல்றோம்.", "{RAJ} standing on a palace balcony before a huge cheering crowd with a Chola tiger banner flying above.", "இராஜராஜ சோழன்", ""),
  ("முதல் வேலை, நாட்டை அளந்தான். நில அளவை செஞ்சு, வரிக் கணக்கு எழுதினான். இது 1001-ல நடந்த பெரிய அளவீடு.", "Surveyors with long measuring ropes marking green rice fields while scribes write the tax records on palm leaves.", "நில அளவை", ""),
  ("அப்புறம் போர். காந்தளூர்ச் சாலையில சேரரோட கடற்படையை அழிச்சான்.", "Chola warships with tiger sails attacking Chera ships on a stormy sea near the coast, arrows flying.", "காந்தளூர்ச் சாலை", ""),
  ("பாண்டியர், சேரர் ரெண்டு பேரையும் வென்றான். மூணு பேர் நாட்டையும் ஒரே குடையில கொண்டு வந்தான்.", "{RAJ} standing with the three royal banners of bow, fish and tiger together under one big royal umbrella.", "", ""),
  ("அவன் கடல் கடந்தான். இலங்கையோட வடபகுதியை பிடிச்சு, அங்க அனுராதபுரத்தை தாக்கினான்.", "A fleet of Chola ships landing soldiers on a Sri Lankan beach, an ancient stupa city in the distance.", "இலங்கை", ""),
  ("மாலத்தீவுகள் வரைக்கும் சோழர் கடற்படை போச்சுன்னு கல்வெட்டு சொல்லுது.", "A Chola fleet sailing among tiny green palm islands in a turquoise sea, a stone inscription showing the ships in a corner.", "மாலத்தீவு", "")]),
("storyteller, warm and curious about an old legend",
 [("இந்தத் தேவாரம் நமக்கு எப்படி கிடைச்சதுன்னு ஒரு கதை இருக்கு. அழிஞ்சு போகப்போன பாடல்களை, நம்பியாண்டார் நம்பி தொகுத்தார்னு சொல்றாங்க.", "{NAM} carefully holding old palm-leaf bundles in a temple corridor lit by oil lamps.", "தேவாரம்", ""),
  ("அரசன் அவரை வரவழைச்சு, சிதம்பரத்துல கரையான் அரிச்சதுபோக மிஞ்சின ஓலைகளை எடுத்து, தொகுக்க வச்சதா சொல்றாங்க.", "A sealed temple room opened to show palm-leaf bundles half eaten by termites, {RAJ} and {NAM} examining them by lamplight.", "", "")]),
("awestruck and proud, the great temple is built",
 [("1003-ல தஞ்சாவூர்ல பெரிய கோயில் கட்டத் தொடங்கினான். ஏழே வருஷத்துல முடிச்சான்.", "Thousands of workers, elephants and carts building the huge Thanjavur temple with giant granite blocks, scaffolds of earth ramps.", "1003", ""),
  ("கோயில் விமானம் 216 அடி. உச்சியில கலசத்துக்குக் கீழ இருக்கிற பெரிய கல்லை, சுமார் 80 டன்னு சொல்றாங்க.", "The towering stone vimana of the Thanjavur temple with a giant capstone at the very top, tiny workers beside it.", "216 அடி", ""),
  ("அந்தக் கல்லை எப்படி மேல ஏத்தினாங்கன்னு இன்னும் விவாதம். சாரப்பள்ளம்ங்கிற ஊர்ல இருந்து சாய்தளம் அமைச்சதா ஒரு கதை.", "A very long earth ramp with elephants and hundreds of men pulling a giant stone block on logs up towards the temple top.", "", ""),
  ("கோயில் கல்வெட்டுல எல்லாமே கணக்கா எழுதியிருக்கு. 400 நடனப் பெண்கள். இசைக் கலைஞர்கள். எத்தனை விளக்கு. எத்தனை ஆடு.", "Temple walls covered with Tamil inscriptions, a scribe counting lamps, goats, and dancers in a long line of 400 women in temple courtyard.", "400 நடனப் பெண்கள்", ""),
  ("1010-ல கோயிலுக்கு கும்பாபிஷேகம். 1987-ல யுனெஸ்கோ இதை உலகப் பாரம்பரிய இடமா அறிவிச்சது.", "A grand consecration ceremony at the Thanjavur temple with priests pouring holy water on the top kalasam and a huge festive crowd below.", "1010", ""),
  ("இராஜராஜன் ஒரு நாட்டை ஆளலை. ஒரு கடற்படைப் பேரரசுக்கு அடித்தளம் போட்டான். அதை பிரமாண்டமா வளர்த்தவன், அவன் மகன்.", "{RAJ} looking out over the sea from a coastal harbour full of Chola ships, a young prince standing behind him.", "", ""),
  ("அடுத்த பகுதியில, கங்கை வரை போய், கடல் கடந்து கடாரத்தை வென்ற இராஜேந்திர சோழன். சேனலை subscribe பண்ணுங்க.", "A young powerful Chola prince on a war elephant at the Ganga river shore with a gold crown and a tiger banner, a huge fleet behind.", "", "")]),
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
thumb = [next(s["n"] for s in out if s["nar"].startswith("இந்தக் கோயிலோட")), next(s["n"] for s in out if s["nar"].startswith("இப்போ 985")), next(s["n"] for s in out if s["nar"].startswith("1003-ல"))]
json.dump({"title": "ராஜராஜ சோழன் எப்படி அரசனானான்? பிற்காலச் சோழர்கள் – தமிழ்நாட்டு வரலாறு பகுதி 3", "shots": out, "scenes": scenes, "anims": {}, "thumb": thumb,
           "shorts": [[12, 14, "1000 வருஷம் முன்பே தேர்தல்!", "குடவோலைத் தேர்தல்"], [15, 16, "கொலையின் மர்மம் இன்னும் விடை இல்லை!", "பொன்னியின் செல்வன்"], [28, 30, "80 டன் கல் எப்படி மேலே ஏறியது?", "தஞ்சாவூர் பெரிய கோயில்"]],
           "exam_cards": [
             "பிற்காலச் சோழர்: விஜயாலயன் (சுமார் 850) தஞ்சாவூரைக் கைப்பற்றினார். ஆதித்த சோழன்: திருப்புறம்பியம் போர், பல்லவர் முடிவு.",
             "முதலாம் பராந்தகன்: மதுரை கொண்டான். தக்கோலம் போர் 949, ராஷ்டிரகூடர் வெற்றி.",
             "உத்தரமேரூர் கல்வெட்டு (919): குடவோலை முறையில் ஊராட்சித் தேர்தல்.",
             "இராஜராஜ சோழன் (985-1014): காந்தளூர்ச் சாலை வெற்றி, இலங்கை வெற்றி, நில அளவை 1001. பட்டம்: அருண்மொழிவர்மன்.",
             "தஞ்சாவூர் பெரிய கோயில்: தொடக்கம் 1003, கும்பாபிஷேகம் 1010, விமானம் 216 அடி. யுனெஸ்கோ 1987."]},
          open("tools/story/tn3.json", "w"), ensure_ascii=False, indent=1)
print(n, "shots", sum(len(s["nar"]) for s in out), "chars; thumb", thumb)
