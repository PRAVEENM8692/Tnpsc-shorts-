# Builds tools/story/tn5.json: Tamil Nadu history part 5 - Pandyas, Nayaks, Marathas (approved by the owner 2026-11-19).
import json
C = {
 "GAN": "Gangadevi, an elegant Vijayanagara princess in a rich sari and jewellery, writing a poem on palm leaves with a stylus",
 "KUM": "Kumara Kampana, a Vijayanagara prince warrior with a turban, a sword and a proud look",
 "TIR": "Thirumalai Nayak, a regal Madurai Nayak king with a tall gold crown, a thick moustache and rich silk robes",
 "SER": "Serfoji II, a refined Maratha king of Thanjavur in a turban and fine robes, holding a manuscript, a scholar's calm face",
 "VIS": "Viswanatha Nayak, a Madurai Nayak founder king in a gold crown and rich robes pointing at a map",
 "MAR": "Marco Polo, a European traveller in a medieval cap and a long coat with a notebook",
 "KAF": "Malik Kafur, a fierce Delhi Sultanate general in a pointed helmet and chainmail on horseback",
}
G = [
("mysterious and curious, a poem about a conquest",
 [("ஒரு பெண் எழுதின காவியம்தான், மதுரையை ஒரு சுல்தான்கிட்டேருந்து மீட்ட கதையை நமக்குச் சொல்லுது.", "{GAN} writing a poem on palm leaves by lamplight, a ghostly Madurai temple tower and a battle shown in the smoke behind her.", "மதுரா விஜயம்", ""),
  ("அந்த சுல்தானியம், டெல்லியில இருந்து பிரிஞ்சு வந்தது. எப்படின்னு பார்ப்போம்.", "A Delhi Sultanate flag and a Madurai temple tower split apart by a glowing crack across the sky.", "", ""),
  ("தமிழ்நாட்டு வரலாறு, பகுதி 5. பாண்டியர், நாயக்கர், மராட்டியர்.", "An old open palm-leaf book on a wooden table with a fish emblem, a lion emblem and a Maratha flag drawn on its pages, a lit lamp beside it.", "", "")]),
("steady storyteller, the fading of an empire and the rise of the south",
 [("சோழர் வலிமை குறையுது. 1054-ல கொப்பம் போர்க்களத்துல இராஜாதிராஜன், யானை மேல இருக்கும்போதே உயிரிழந்தான்.", "A sad battlefield with a Chola king fallen on a war elephant and his soldiers rallying behind a tiger banner.", "கொப்பம் 1054", ""),
  ("சோழர் சரியச் சரிய, தெற்கே மதுரையில பாண்டியர் மெல்ல எழுந்தாங்க. 1216-ல முதலாம் மாறவர்மன் சுந்தர பாண்டியன், சோழ நாட்டுக்குள்ளேயே புகுந்து தாக்கினான்.", "A Pandya king on a war elephant with a fish banner entering the burning gates of an old Chola city, soldiers charging.", "பாண்டியர் எழுச்சி", ""),
  ("பாண்டியர் பொற்காலம் 13-ஆம் நூற்றாண்டு. குலசேகர பாண்டியன் காலத்துல வெனிஸ் பயணி மார்கோ போலோ, சுமார் 1288-ல இங்க வந்தார்.", "{MAR} arriving at a busy Pandya port with tall ships, merchants and a fish banner, noting things in his notebook.", "மார்கோ போலோ", ""),
  ("அவர் எழுதினாரு, முத்துக் குளிப்பும், அரபு நாட்டுல இருந்து வர்ற குதிரைகளும் இங்க பெரிய வணிகம்னு.", "Pearl divers surfacing with oysters near a boat while Arabian horses are being unloaded from a ship on the shore.", "முத்துக் குளிப்பு", "")]),
("tense, sudden invasion and a breakaway",
 [("ஆனா அரச குடும்பத்துல அண்ணன் தம்பி சண்டை. 1311-ல அலாவுதீன் கில்ஜியோட தளபதி மாலிக் கபூர், மதுரையைத் தாக்கிக் கொள்ளையடிச்சான்.", "{KAF} leading cavalry into Madurai as soldiers carry out treasure chests, the temple tower behind in smoke.", "மாலிக் கபூர் 1311", ""),
  ("அதுக்குப் பிறகு 1334-ல, டெல்லி சுல்தான் முகமது பின் துக்ளக்கோட ஆளுநர் ஜலாலுதீன் அஹ்சன் ஷா, தன்னைத் தனி சுல்தானா அறிவிச்சுக்கிட்டார். மதுரை சுல்தானியம் பிறந்தது.", "A governor in sultanate robes declaring himself ruler on a throne in a Madurai hall, courtiers bowing, a new green flag rising.", "மதுரை சுல்தானியம்", ""),
  ("சுமார் 1344-ல மொராக்கோ பயணி இபின் பட்டூட்டா மதுரைக்கு வந்து, அங்கே நடந்த கொடுமையான நோய், போர் பத்தி எழுதினார்னு சொல்றாங்க.", "A Moroccan traveller in a turban walking through a gloomy Madurai street with sick people and soldiers, writing in a notebook.", "இபின் பட்டூட்டா", ""),
  ("சுமார் 40 வருஷம் அந்த சுல்தானியம் நீடிச்சுது. அப்போ விஜயநகரப் பேரரசு எழுந்துச்சு.", "A mighty Vijayanagara army with boar-emblem banners marching south over rocky hills at sunrise.", "", ""),
  ("1370-களில் விஜயநகர இளவரசன் குமார கம்பணன், மதுரையை வென்று சுல்தானியத்தை முடிச்சான்.", "{KUM} riding into Madurai at the head of his army as the sultanate flag is pulled down, crowds cheering.", "குமார கம்பணன்", ""),
  ("அவன் மனைவி கங்காதேவி, மதுரா விஜயம்னு ஒரு காவியம் எழுதினாங்க. அந்த வெற்றியோட கதை அதுல இருக்கு.", "{GAN} reading her finished poem aloud to a court of poets with palm-leaf manuscripts around, warm lamplight.", "மதுரா விஜயம்", "")]),
("proud and grand, the Nayak age",
 [("இப்போ தமிழ்நாடு விஜயநகரத்தோட கீழே. அவங்க நியமிச்ச ஆளுநர்கள்தான் நாயக்கர்கள்.", "A Vijayanagara emperor on a throne handing a royal sword and seal to a kneeling Nayak governor, court officials watching.", "", ""),
  ("மதுரையில விஸ்வநாத நாயக்கர், சுமார் 1529-ல ஆட்சியைத் தொடங்கினார். பாளையக்காரர் முறையை உருவாக்கினது இவர்தான்னு சொல்றாங்க.", "{VIS} pointing at a map of the Tamil country divided into small regions with his minister beside him.", "விஸ்வநாத நாயக்கர்", ""),
  ("நாடு 72 பாளையங்களா பிரிக்கப்பட்டுச்சு. ஒவ்வொரு பாளையக்காரரும் ஒரு கோட்டையும், படையும் வச்சு, அரசுக்கு வரியும் கட்டினாங்க.", "A small hill fort with guards and a chieftain offering a bag of tax to a royal officer, seventy tiny forts shown on a map behind.", "72 பாளையங்கள்", ""),
  ("1565-ல தலைக்கோட்டைப் போர்ல விஜயநகரம் வீழ்ந்துச்சு. நாயக்கர்கள் சுதந்திரமா ஆளத் தொடங்கினாங்க.", "A fierce battle of elephants and cannons with a falling Vijayanagara banner while distant Nayak governors watch.", "தலைக்கோட்டை 1565", ""),
  ("மதுரையின் புகழ்பெற்ற நாயக்கன் திருமலை நாயக்கர். 1636-ல தன் அரண்மனை கட்டினார்.", "{TIR} standing before his newly built grand white palace with huge arches, courtiers behind him.", "திருமலை நாயக்கர்", ""),
  ("அந்த அரண்மனையோட தூண்கள் சுமார் 80 அடி உயரம். வடிவமைப்பில ஒரு ஐரோப்பிய கட்டடக் கலைஞரோட தாக்கம் இருக்குன்னு சொல்றாங்க.", "The grand courtyard of the Thirumalai Nayak palace with very tall carved pillars and arches, tiny visitors for scale.", "80 அடித் தூண்கள்", ""),
  ("மீனாட்சியம்மன் கோயிலுக்கு புது மண்டபம் கட்டினதும், தெப்பக்குளம் வெட்டினதும் இவர்தான்.", "A huge float festival on a temple tank with lamps glowing, a carved pillared hall beside the Meenakshi temple at dusk.", "", ""),
  ("தஞ்சாவூர் நாயக்கர்களும் ஒண்ணு செஞ்சாங்க. சரஸ்வதி மகால் நூலகத்தை ஆரம்பிச்சாங்க.", "A grand old library hall in Thanjavur with shelves of palm-leaf manuscripts, scholars reading by oil lamps.", "சரஸ்வதி மகால்", "")]),
("excited and respectful, the Maratha chapter",
 [("1674-ல ஏகோஜி, அதாவது சிவாஜியோட தம்பி, தஞ்சாவூரைக் கைப்பற்றினார். தஞ்சை மராட்டிய ஆட்சி தொடங்குச்சு.", "A Maratha ruler in a turban entering the gates of Thanjavur with saffron flags and soldiers, the great temple tower behind.", "ஏகோஜி 1674", ""),
  ("சிவாஜி 1677-ல செஞ்சிக் கோட்டையைப் பிடிச்சார். ஆங்கிலேயர் அதை கிழக்கின் டிராய்னு சொன்னாங்க. 2025-ல யுனெஸ்கோ பாரம்பரிய அங்கீகாரம் கிடைச்சுது.", "The mighty Gingee fort on three steep rocky hills with long stone walls and a saffron flag at its peak at sunrise.", "செஞ்சிக் கோட்டை", ""),
  ("தஞ்சை மராட்டிய ஆட்சியில் மிகச் சிறந்தவர் இரண்டாம் சரபோஜி. சுமார் 1798-ல் அரியணை ஏறினார்.", "{SER} being crowned in a Thanjavur palace hall, ministers and priests around, saffron banners.", "இரண்டாம் சரபோஜி", ""),
  ("அவர் மன்னர் மட்டுமில்ல. அறிஞர். பழைய ஓலைச்சுவடிகளையும், நூல்களையும் சரஸ்வதி மகால்ல சேர்த்து, அதை உலகப் புகழ் பெற்ற நூலகமா மாத்தினார்.", "{SER} in a grand library with towering shelves of manuscripts and old books, scribes copying works.", "", ""),
  ("தடுப்பூசி போடுறதையும், ஐரோப்பிய மருத்துவத்தையும் தன் நாட்டுல ஊக்குவிச்சார்னு சொல்றாங்க.", "A doctor vaccinating a child in a Thanjavur palace courtyard while the king and villagers watch curiously.", "", ""),
  ("இந்த நேரத்துல கடல் வழியா ஐரோப்பியர்கள் வந்துட்டாங்க. அதுதான் நம்ம கதையோட அடுத்த திருப்பம்.", "European sailing ships with white sails arriving at the Tamil coast at dawn, local fishermen watching from the beach.", "", ""),
  ("அடுத்த பகுதியில, ஐரோப்பியர்கள் முதல் சுதந்திரப் போராட்டம் வரை. சேனலை subscribe பண்ணுங்க.", "A sailing ship, a fort flag and a young freedom fighter holding a sword at sunrise on a Tamil seashore.", "", "")]),
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
thumb = [next(s["n"] for s in out if s["nar"].startswith("அவன் மனைவி")), next(s["n"] for s in out if s["nar"].startswith("அந்த அரண்மனையோட")), next(s["n"] for s in out if s["nar"].startswith("அவர் மன்னர் மட்டுமில்ல"))]
json.dump({"title": "மதுரையை ஆண்ட சுல்தான்கள்! பாண்டியர், நாயக்கர், மராட்டியர் – தமிழ்நாட்டு வரலாறு பகுதி 5", "shots": out, "scenes": scenes, "anims": {}, "thumb": thumb,
           "shorts": [[12, 13, "காவியம் சொன்ன மதுரை மீட்பு!", "மதுரா விஜயம்"], [18, 20, "80 அடித் தூண்கள் கொண்ட அரண்மனை!", "திருமலை நாயக்கர்"], [24, 26, "நூலகத்தை உலகப் புகழ் பெறச் செய்த மன்னன்!", "இரண்டாம் சரபோஜி"]],
           "exam_cards": [
             "கொப்பம் போர் 1054: இராஜாதிராஜன் மறைவு. பாண்டியர் எழுச்சி: முதலாம் மாறவர்மன் சுந்தர பாண்டியன் (1216). மார்கோ போலோ வருகை சுமார் 1288.",
             "மாலிக் கபூர் மதுரைத் தாக்குதல் 1311. மதுரை சுல்தானியம் 1334 (ஜலாலுதீன் அஹ்சன் ஷா). இபின் பட்டூட்டா வருகை சுமார் 1344.",
             "குமார கம்பணன் மதுரை வெற்றி (1370-கள்). கங்காதேவி: மதுரா விஜயம்.",
             "நாயக்கர்: விஸ்வநாத நாயக்கர் (சுமார் 1529), பாளையக்காரர் முறை (72 பாளையங்கள்). தலைக்கோட்டைப் போர் 1565.",
             "திருமலை நாயக்கர் மகால் (1636). தஞ்சை மராட்டியர்: ஏகோஜி 1674, இரண்டாம் சரபோஜி, சரஸ்வதி மகால் நூலகம். செஞ்சிக் கோட்டை 1677."]},
          open("tools/story/tn5.json", "w"), ensure_ascii=False, indent=1)
print(n, "shots", sum(len(s["nar"]) for s in out), "chars; thumb", thumb)
