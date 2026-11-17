# Builds tools/story/tn1.json: the shot list for "Tamil Nadu history part 1 - the Sangam age".
# Groups = scenes; each group has the feeling the voice should have, then shots (nar, scene, text, anim).
import json
C = {
 "KAR": "Karikala Chola, a strong young Tamil king with a broad chest, dark skin, a gold crown with a small tiger emblem, a white dhoti and a red shoulder cloth",
 "SEN": "Senguttuvan Chera, a tall majestic Tamil king with a thick moustache, a gold crown, heavy jewellery and a bow emblem on his chest",
 "NED": "Nedunchezhiyan Pandya, a dignified middle-aged Tamil king with a neat moustache, a gold crown with a fish emblem and a cream silk dhoti",
 "KAN": "Kannagi, a young Tamil woman with flowing black hair, burning angry eyes, a simple saree and one golden anklet in her hand",
 "ILA": "Ilango Adigal, a calm thin ascetic poet with a shaved head, a saffron cloth and a palm-leaf manuscript in his hand",
 "POE": "an old Tamil poet in a white dhoti with a long white beard, holding a palm-leaf manuscript and an iron stylus",
 "ROM": "a Roman trader with a short curly beard, a white tunic with a red border and a leather bag of gold coins",
}
G = [
("intriguing, a puzzle: an old dam still working after two thousand years, then a proud introduction to the series",
 [("2000 வருஷத்துக்கு முன்னாடி, ஒரு தமிழ் மன்னன் ஆற்றுக்குக் குறுக்கே கல்லை வச்சு அணை கட்டினான்.", "Thousands of workers lifting huge stones to build a long stone dam across a wide river, an ancient Tamil king watching from a platform.", "", ""),
  ("அந்த அணை இன்னைக்கும் தண்ணி பாய்ச்சுது.", "A very old stone dam with water rushing over it today, green rice fields glowing in the golden evening light.", "", ""),
  ("அது எந்த அணை? யார் கட்டினது?", "A glowing question mark of golden light floating above an ancient stone dam in the mist, a lone farmer looking up at it.", "", ""),
  ("தமிழ்நாட்டு வரலாறு, பகுதி 1. சங்க காலம்.", "An old open palm-leaf book glowing on a wooden table with a lit brass lamp, a feather and a green Tamil landscape behind.", "", "")]),
("warm and proud, like a friendly teacher introducing the three great kings with a smile",
 [("நண்பர்களே, அந்தக் காலத்துல தமிழ்நாட்டை மூணு பேர் ஆண்டாங்க. சேரர், சோழர், பாண்டியர். இவங்களுக்கு மூவேந்தர்னு பேரு.", "Three Tamil kings standing side by side in front of a grand ancient hall, each wearing a gold crown, a bow emblem, a tiger emblem and a fish emblem.", "மூவேந்தர்", "mv"),
  ("ஒவ்வொருத்தருக்கும் ஒரு அடையாளம் இருந்துச்சு. சேரருக்கு வில்.", "A great Chera king in a green forest hall holding a long bow, a banner with a bow emblem behind him.", "", ""),
  ("சோழருக்குப் புலி.", "A Chola king on a throne beside a golden tiger statue, a red banner with a tiger emblem fluttering behind.", "", ""),
  ("பாண்டியருக்கு மீன்.", "A Pandya king in a sunlit palace with a big golden fish emblem on a blue banner behind him.", "", ""),
  ("கொடிமட்டும் இல்ல, பூவும் உண்டு. சேரர் பனம்பூ. சோழர் ஆத்திப்பூ. பாண்டியர் வேப்பம்பூ.", "Three garlands side by side on a table: one of palm flowers, one of yellow cassia flowers and one of white neem flowers.", "", ""),
  ("சேரர் மேற்குல, சோழர் காவிரிக் கரையில, பாண்டியர் தெற்குல மதுரையில இருந்து ஆண்டாங்க.", "An old hand-drawn map of the Tamil land with three coloured regions: green in the west, red along a river in the east and blue in the south.", "", ""),
  ("அசோகர் கல்வெட்டுகளிலேயே இவங்க மூணு பேரும் குறிப்பிடப்பட்டிருக்காங்க. அவ்வளவு பழமையான அரசுகள்.", "An ancient carved stone pillar with inscriptions standing on a hill, a robed scholar reading it while a map of kingdoms lies on a stone table.", "", "")]),
("excited and proud about poetry, then curious about the legend",
 [("இப்போ, சங்க காலம்னா என்ன? மதுரையில பாண்டிய மன்னர்கள் புலவர்களுக்காக ஒரு சங்கம் வச்சாங்க.", "A grand ancient Madurai hall full of Tamil poets sitting on mats before a Pandya king, palm-leaf manuscripts in their hands.", "சங்கம்", ""),
  ("அங்க கவிதைகள் அரங்கேறும்.", "{POE} reciting verses on a raised platform while the audience listens in silence, oil lamps glowing.", "", ""),
  ("மூணு சங்கம் இருந்ததா மரபு சொல்லுது.", "Three old golden lamps burning one after another in a dark hall, three ancient doorways behind them.", "", ""),
  ("இந்தக் காலத்து நூல்கள்தான் தொல்காப்பியம், எட்டுத்தொகை, பத்துப்பாட்டு.", "A neat stack of palm-leaf manuscripts tied with cords on a wooden stand, three bundles of different thickness.", "", ""),
  ("கபிலர், ஔவையார் மாதிரி புலவர்கள் வாழ்ந்தது இந்தக் காலத்துலதான்.", "An old Tamil woman poet with white hair in a simple white saree sitting under a banyan tree and a poet beside her, village children listening.", "", ""),
  ("சங்கப் பாடல்கள் ரெண்டு வகை. அகம், அதாவது காதல். புறம், அதாவது போர், கொடை, வீரம்.", "A split scene: on one side a young couple meeting by a lotus pond at sunrise, on the other a hero in battle and a king giving gifts to poets.", "அகம் | புறம்", ""),
  ("சுமார் கி.மு. 300 முதல் கி.பி. 300 வரை இதைச் சங்க காலம்னு சொல்றாங்க.", "A long stone road stretching into the horizon with two ancient milestones, one at the start and one far in the distance.", "சங்க காலம்", "tm")]),
("dramatic and heroic for Karikalan and the war, then proud and amazed for the dam",
 [("இப்போ அந்த அணைக்கு வருவோம். சோழ மன்னன் கரிகால சோழன்.", "{KAR} standing on a hill, looking proudly over a green delta with a river.", "கரிகாலன்", ""),
  ("வெண்ணிப் போர்ல சேரரையும் பாண்டியரையும் ஒரே நேரத்துல தோற்கடிச்சான்.", "{KAR} on a war elephant in the middle of a huge battle, the Chera and Pandya armies scattering on both sides.", "", ""),
  ("அவன் காவிரி ஆத்துல கல்லணை கட்டினான்.", "Workers placing great stones into a wide river as {KAR} points and gives orders, ropes and bullock carts everywhere.", "கல்லணை", ""),
  ("உலகத்துல இன்னும் பயன்பாட்டுல இருக்கிற பழமையான அணைகள்ல இதுவும் ஒண்ணு.", "The old stone dam Kallanai today with water flowing over its long wall, a bright blue sky and farmers walking across it.", "", ""),
  ("கல்லணை சுமார் 300 மீட்டருக்கு மேல நீளம். பின்னாடி ஆங்கிலேய பொறியாளர் ஆர்தர் காட்டன் இதைப் படிச்சுத்தான் கோதாவரியில அணை கட்டினார்னு சொல்லுவாங்க.", "A 19th century English engineer in a hat and coat studying the old stone dam with a roll of drawings, Tamil workers standing beside him.", "", ""),
  ("காவிரி வெள்ளத்தை பிரிச்சு வயல்களுக்குத் தண்ணி கொடுத்தான்.", "A flooded river being split into many small canals flowing into golden rice fields as farmers cheer.", "", ""),
  ("அவனுடைய தலைநகரம் பூம்புகார். அதைப் பத்தி பட்டினப்பாலை பாடுது.", "The busy ancient port city of Poompuhar with ships, warehouses and a lighthouse by the sea, a poet writing on a palm leaf in the foreground.", "பூம்புகார்", "")]),
("sad, gentle and dramatic, like telling an old legend by the fire",
 [("சங்க காலக் கதைகள்ல மிகப் பிரபலம், கண்ணகி கதை.", "{KAN} standing alone on a dusty road at dusk holding a golden anklet, a glowing red sky behind her.", "கண்ணகி", ""),
  ("சிலப்பதிகாரத்தை எழுதினவர் இளங்கோவடிகள்.", "{ILA} writing slowly with an iron stylus on a palm leaf by a small oil lamp in a quiet room.", "இளங்கோவடிகள்", ""),
  ("கோவலன் தவறா தண்டிக்கப்பட்டான்.", "A young Tamil merchant with a worried face being wrongly led away by guards through a silent street.", "", ""),
  ("கோபம் கொண்ட கண்ணகி மதுரைக்கு வந்து நீதி கேட்டாள்.", "{KAN} walking furiously into a grand Madurai court hall, the nobles shocked as she holds up an anklet.", "", ""),
  ("அன்றைய பாண்டிய மன்னன் நெடுஞ்செழியன். தன் தவறைத் தெரிஞ்சதும் உயிரை விட்டான்னு கதை சொல்லுது.", "{NED} sitting on the throne with a stunned and grieving face, the anklet shining before him, courtiers silent.", "நெடுஞ்செழியன்", ""),
  ("கண்ணகிக்குச் சிலை வைக்க இமயமலைக் கல் கொண்டு வந்தவன், சேரன் செங்குட்டுவன்.", "{SEN} with soldiers carrying a huge stone on a wooden cart through snowy mountains for a statue.", "செங்குட்டுவன்", "")]),
("lively and excited about trade, like showing the world arriving in Tamil land",
 [("தமிழ்நாடு அப்போ ஒரு வியாபார மையம். ரோமானியர்கள், அதாவது யவனர்கள், கப்பல்ல வந்தாங்க.", "A large wooden Roman ship with a red sail arriving at a busy Tamil harbour, workers waving from the dock.", "", ""),
  ("மிளகு, முத்து, பருத்தித் துணி வாங்கிட்டுப் பொன்னைக் கொடுத்தாங்க.", "{ROM} handing a bag of gold coins to a Tamil merchant beside sacks of pepper, a tray of pearls and rolls of cotton cloth.", "", ""),
  ("ரோமானிய நாணயங்கள் தமிழ்நாட்டுல பல இடங்கள்ல கிடைச்சிருக்கு. ரோமின் தங்கம் இந்தியாவுக்குப் போகுதேன்னு ரோமானிய அறிஞர் பிளினி புலம்பினாராம்.", "An old Roman scholar in a toga counting gold coins on a table with a sad face while a map shows a ship route to India.", "", ""),
  ("சேரர்களின் முசிறித் துறைமுகம். பாண்டியரின் கொற்கை முத்துக்கு உலகப் புகழ்.", "Pearl divers surfacing from blue sea beside a wooden boat, a basket of shining white pearls on the deck.", "", "pt"),
  ("புதுச்சேரி பக்கத்துல இருக்கிற அரிக்கமேடு, ரோமானிய வணிகத் தளம்.", "An ancient coastal trading yard with Roman clay jars, coins and warehouses beside the sea at sunset.", "", "")]),
("friendly and inviting, a warm question to the viewer, then a teaser of what comes next",
 [("மூணு வேந்தர்ல உங்களுக்குப் பிடிச்சவர் யாரு? சேரனா, சோழனா, பாண்டியனா? கமெண்ட்ல சொல்லுங்க.", "Three ancient Tamil kings standing in a row, each with a glowing question mark above, soft golden light behind them.", "உங்கள் விருப்பம்?", ""),
  ("அடுத்த பகுதியில, தமிழகத்தை இருண்ட காலம்னு சொல்றாங்களே, அது உண்மையா?", "A dark moonless night over an ancient Tamil land with a single faint lamp glowing in the distance, a mystery.", "", ""),
  ("களப்பிரர் யாரு? பல்லவர் எப்படி வந்தாங்க? தவறவிடாம இருக்க சேனலை subscribe பண்ணுங்க.", "A mysterious hooded warrior on a hill at dawn with a new banner rising far away behind an ancient stone temple outline.", "", "")]),
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
 "mv": {"kind": "list", "title": "மூவேந்தர் அடையாளம்",
        "items": [["வில்", "சேரர்"], ["புலி", "சோழர்"], ["மீன்", "பாண்டியர்"]],
        "fallback": "வில் சேரர் | புலி சோழர் | மீன் பாண்டியர்"},
 "tm": {"kind": "timeline", "items": [["கி.மு. 300", "சங்க காலம் தொடக்கம்"], ["கி.பி. 300", "சங்க காலம் முடிவு"]],
        "fallback": "கி.மு. 300 முதல் கி.பி. 300 வரை"},
 "pt": {"kind": "list", "title": "வணிகத் துறைமுகங்கள்",
        "items": [["சேரர்", "முசிறி"], ["சோழர்", "பூம்புகார்"], ["பாண்டியர்", "கொற்கை"]],
        "fallback": "சேரர் முசிறி | சோழர் பூம்புகார் | பாண்டியர் கொற்கை"},
}
json.dump({"title": "2000 வருஷம் முன் கட்டிய அணை, இன்றும் ஓடுது! – தமிழ்நாட்டு வரலாறு பகுதி 1", "shots": out, "scenes": scenes, "anims": ANIMS,
           "exam_cards": [
             "மூவேந்தர் அடையாளம்: சேரர் – வில், சோழர் – புலி, பாண்டியர் – மீன். பூ: பனம்பூ, ஆத்திப்பூ, வேப்பம்பூ.",
             "சங்க காலம்: சுமார் கி.மு. 300 – கி.பி. 300. மையம் மதுரை. நூல்கள்: தொல்காப்பியம், எட்டுத்தொகை, பத்துப்பாட்டு.",
             "கரிகால சோழன்: வெண்ணிப் போர், கல்லணை, தலைநகரம் பூம்புகார். பட்டினப்பாலையின் பாட்டுடைத் தலைவன்.",
             "சிலப்பதிகாரம்: இளங்கோவடிகள். நெடுஞ்செழியன் (பாண்டியன்), செங்குட்டுவன் (சேரன்).",
             "வணிகம்: ரோமானியத் தொடர்பு. முசிறி (சேரர்), கொற்கை (பாண்டியர்), பூம்புகார் (சோழர்), அரிக்கமேடு."]},
          open("tools/story/tn1.json", "w"), ensure_ascii=False, indent=1)
print(n, "shots", sum(len(s["nar"]) for s in out), "chars")
