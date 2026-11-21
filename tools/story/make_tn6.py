# Builds tools/story/tn6.json: Tamil Nadu history part 6 - Europeans to the freedom struggle (approved by the owner 2026-11-21).
import json
C = {
 "VEL": "Velu Nachiyar, a brave Sivaganga queen in a royal sari with a sword and shield, a determined look",
 "KUY": "Kuyili, a fearless woman commander in simple warrior clothes with a torch in her hand",
 "KAT": "Veerapandiya Kattabomman, a proud Tamil chieftain with a big moustache, a turban and a sword, a fearless look",
 "MAR": "the Marudhu brothers, two stern Sivaganga warriors in turbans holding swords side by side",
 "VOC": "V. O. Chidambaram Pillai, a dignified Tamil leader in a white dhoti and shirt with a white turban, a steady stern look",
 "BHA": "Subramania Bharati, a Tamil poet with a large turban, a thick moustache and fiery eyes, holding a pen",
 "CLI": "Robert Clive, a young British officer in a red coat and a tricorn hat, leading a small group of soldiers",
 "ZIE": "Bartholomaeus Ziegenbalg, a German missionary in a black coat and white collar, standing by an old printing press",
 "RAJ": "C. Rajagopalachari, an elderly Tamil leader in white dhoti and shawl leading a salt march with followers",
 "VAN": "Vanchinathan, a young Tamil man in simple clothes at a railway platform, a determined look",
}
G = [
("tense and solemn, a shocking opening",
 [("1799-ல ஒரு மன்னனை, கயத்தாறுல தூக்குல போட்டாங்க. வரி கட்ட மாட்டேன்னு சொன்னதுதான் அவன் குற்றம்.", "{KAT} standing with his hands bound under a huge tamarind tree at dawn, British soldiers around him, a heavy sad mood.", "கயத்தாறு 1799", ""),
  ("தமிழ்நாட்டு வரலாறு, பகுதி 6. ஐரோப்பியர் வருகை முதல் சுதந்திரம் வரை.", "A rolled old map of South India on a wooden table with a compass, a sailing ship drawing and a candle, golden light.", "", "")]),
("steady storyteller, merchants arrive by sea",
 [("1498-ல வாஸ்கோ ட காமா இந்தியா வந்தார். அவரைத் தொடர்ந்து போர்த்துகீசியர் நம்ம கடற்கரைக்கு வந்து, 1522-ல சாந்தோம்ல குடியேறினாங்க.", "Portuguese sailing ships with red cross sails anchored near the Mylapore Santhome coast, a small church on the shore.", "போர்த்துகீசியர்", ""),
  ("அடுத்து டச்சுக்காரர்கள். 1609-ல பழவேற்காட்டுல கோட்டை கட்டினாங்க.", "Dutch merchants with tall hats overseeing workers building a brick fort by the Pulicat lake at sunrise, a Dutch flag.", "பழவேற்காடு 1609", ""),
  ("1620-ல டேனிஷ்காரர்கள் தரங்கம்பாடியில டேன்ஸ்போர்க் கோட்டை கட்டினாங்க. அங்க 1715-ல தமிழ் புதிய ஏற்பாடு அச்சாச்சு. இந்திய மொழிகள்ல முதலில் அச்சேறினது தமிழ்தான்னு சொல்றாங்க.", "{ZIE} beside an old wooden printing press printing Tamil letters, the sea and the Danish fort in the background.", "தரங்கம்பாடி", ""),
  ("1639-ல ஆங்கிலேயர் பிரான்சிஸ் டே, சென்னைப் பகுதியில நிலம் வாங்கினார். 1640-ல செயின்ட் ஜார்ஜ் கோட்டை கட்டினாங்க. அங்கதான் சென்னை பிறந்துச்சு.", "A white sea fort with an English flag rising on the Madras beach, fishermen boats and workers carrying stones, golden morning.", "செயின்ட் ஜார்ஜ் கோட்டை", ""),
  ("1674-ல பிரெஞ்சுக்காரர்கள் புதுச்சேரியில குடியேறினாங்க.", "French officers in blue coats at a seaside Pondicherry street with white colonial buildings and a French flag.", "புதுச்சேரி 1674", "")]),
("tense, from trade to war",
 [("வியாபாரம் செய்ய வந்தவங்க, ஆட்சிக்காக மோதத் தொடங்கினாங்க. 1746 முதல் 1763 வரை மூணு கர்நாடகப் போர்கள் நடந்துச்சு.", "British and French armies facing each other across a field with cannons and flags, smoke rising, a dramatic sky.", "கர்நாடகப் போர்கள்", ""),
  ("1751-ல ராபர்ட் கிளைவ், சில நூறு வீரர்களோட மட்டும் ஆற்காட்டைக் கைப்பற்றினார்.", "{CLI} charging through the gate of the Arcot fort with a few soldiers at night, torches and a startled defending guard.", "ஆற்காடு 1751", ""),
  ("1760-ல வந்தவாசிப் போர்ல பிரெஞ்சுப் படை தோத்துச்சு. 1763 பாரிஸ் ஒப்பந்தத்துக்குப் பிறகு, ஆங்கிலேயருக்குப் போட்டியே இல்லாம போச்சு.", "A defeated French army lowering its flag on a battlefield at Wandiwash while a British officer on horseback watches.", "வந்தவாசி 1760", "")]),
("proud and fiery, the heroes who resisted",
 [("ஆனா நம்ம மண்ணு பணியல. நெற்கட்டும்செவல் பூலித்தேவன், வரி கட்ட மறுத்து ஆங்கிலேயரை எதிர்த்தார்.", "Puli Thevar, a fearless Tamil chieftain with a thick moustache and a sword, refusing a tax collector with a paper in his hand, villagers behind him.", "பூலித்தேவன்", ""),
  ("சிவகங்கை ராணி வேலு நாச்சியார். 1772-ல ஆங்கிலப் படை அவங்க கணவர் முத்து வடுகநாதரைக் காளையார்கோவில்ல கொன்னுச்சு.", "{VEL} standing in grief at night outside a temple with her small daughter, soldiers' torches burning far behind her.", "வேலு நாச்சியார்", ""),
  ("ராணி சுமார் 8 வருஷம் தலைமறைவா இருந்து, ஹைதர் அலி உதவியோட படை திரட்டி, 1780-ல சிவகங்கையை மீட்டாங்க. ஆங்கிலேயரை எதிர்த்துப் போர் செஞ்ச முதல் ராணின்னு சொல்றாங்க.", "{VEL} leading her women warriors and soldiers on horseback into the Sivaganga fort, swords raised, banners flying.", "சிவகங்கை மீட்பு 1780", ""),
  ("அவங்க படைத் தளபதி குயிலி, ஆயுதக் கிடங்குக்குள்ள தன் மேல தீ வச்சுக்கிட்டுப் பாய்ஞ்சு, அதை அழிச்சாங்க. அதுதான் வெற்றிக்கு வழி விட்டுச்சு.", "{KUY} running with a flaming torch towards a dark British armoury door in a brave desperate dash, firelight on her face.", "குயிலி", ""),
  ("பாஞ்சாலங்குறிச்சி வீரபாண்டிய கட்டபொம்மன். 1799-ல கோட்டையை ஆங்கிலப் படை தாக்கிச்சு. அக்டோபர் 16-ல கயத்தாறுல தூக்குல போட்டாங்க. அப்போ வயசு 39.", "{KAT} standing defiant in the Panchalankurichi fort courtyard with soldiers around him and cannons firing outside the walls.", "கட்டபொம்மன்", ""),
  ("1801-ல மருது சகோதரர்கள், திருச்சிராப்பள்ளியில பிரகடனம் வெளியிட்டாங்க. எல்லா இந்தியர்களும் ஆங்கிலேயருக்கு எதிரா ஒண்ணு சேரணும்னு அதுல அழைப்பு இருந்துச்சு.", "{MAR} pasting a large proclamation on the wall of a temple gopuram at Tiruchirappalli, crowds gathering to read it.", "மருது சகோதரர்கள்", ""),
  ("1806 ஜூலை 10-ல வேலூர் கோட்டையில சிப்பாய்கள் கிளர்ச்சி செஞ்சாங்க. 1857 சிப்பாய் கலகத்துக்கு 51 வருஷம் முன்னாடியே இது நடந்துச்சு.", "Indian sepoys in old uniforms rising against their officers inside the grand Vellore fort at dawn, muskets and a flag.", "வேலூர் 1806", "")]),
("inspired and building to victory",
 [("தேசிய இயக்கம் வளர்ந்துச்சு. பாரதியாரோட பாடல்கள் மக்களை எழுப்பின.", "{BHA} reciting his poem to a large crowd on a Chennai beach at sunset, people listening with fists raised.", "பாரதியார்", ""),
  ("1906-ல வ.உ. சிதம்பரம் பிள்ளை, சுதேசி நீராவிக் கப்பல் கம்பெனி தொடங்கினார். தூத்துக்குடியிலிருந்து கொழும்புக்கு, ஆங்கிலக் கப்பல்களுக்குப் போட்டியா கப்பல் விட்டார்.", "{VOC} standing proudly on the deck of a steamship leaving Tuticorin harbour, a swadeshi flag flying, cheering crowds on the quay.", "வ.உ.சி", ""),
  ("1908-ல அவருக்கு 40 ஆண்டு தண்டனை. சிறையில செக்கிழுக்க வச்சாங்க. அதனால அவரைச் செக்கிழுத்த செம்மல்னு அழைக்கிறாங்க.", "{VOC} in a prison courtyard turning a heavy wooden oil press like an ox, tired but with an unbroken dignified look.", "செக்கிழுத்த செம்மல்", ""),
  ("1911-ல வாஞ்சிநாதன், திருநெல்வேலி கலெக்டர் ஆஷை மணியாச்சியில சுட்டுட்டு, தன்னையும் சுட்டுக்கிட்டார்.", "{VAN} standing on an old Tamil Nadu railway platform at Maniyachi with steam from a train, tense moment, shadows.", "வாஞ்சிநாதன்", ""),
  ("1930-ல ராஜாஜி, திருச்சியிலிருந்து வேதாரண்யம் வரை உப்பு சத்தியாகிரகப் பயணம் நடத்தினார்.", "{RAJ} leading a long line of volunteers marching on a dusty road towards the sea to make salt, Indian flags.", "வேதாரண்யம் 1930", ""),
  ("1947 ஆகஸ்ட் 15-ல நாடு விடுதலை பெற்றுச்சு. சென்னை மாநிலம், 1969-ல தமிழ்நாடுன்னு பெயர் மாறுச்சு.", "The Indian tricolour flag rising over Fort St George in Chennai at sunrise as a joyful crowd cheers, golden light.", "ஆகஸ்ட் 15, 1947", ""),
  ("சங்க காலம் முதல் சுதந்திரம் வரை, தமிழ்நாட்டு வரலாறு ஆறு பகுதிகளா இங்க முடிஞ்சுது. சேனலை subscribe பண்ணுங்க.", "A glowing palm-leaf book closing with golden light, six old coins from the six parts of the story resting on it, a lit lamp beside.", "", "")]),
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
thumb = [first("ராணி சுமார்"), first("பாஞ்சாலங்குறிச்சி"), first("1906-ல வ.உ.")]
json.dump({"title": "தூக்குமேடை வரை சென்ற வீரர்கள்! ஐரோப்பியர் முதல் சுதந்திரம் வரை – தமிழ்நாட்டு வரலாறு பகுதி 6", "shots": out, "scenes": scenes, "anims": {}, "thumb": thumb,
           "shorts": [[first("சிவகங்கை ராணி"), first("அவங்க படைத்"), "ஆயுதக் கிடங்கை அழித்த குயிலி!", "வேலு நாச்சியார் மற்றும் குயிலி"],
                      [first("பாஞ்சாலங்குறிச்சி"), first("1801-ல"), "வரி கட்ட மறுத்த மன்னன்!", "கட்டபொம்மன் மற்றும் மருது சகோதரர்கள்"],
                      [first("1906-ல வ.உ."), first("1908-ல"), "கப்பல் விட்டவருக்கு செக்கிழுப்புத் தண்டனை!", "வ.உ.சிதம்பரம் பிள்ளை"]],
           "exam_cards": [
             "போர்த்துகீசியர் சாந்தோம் 1522. டச்சு பழவேற்காடு 1609. டேனிஷ் தரங்கம்பாடி 1620. செயின்ட் ஜார்ஜ் கோட்டை 1640. பிரெஞ்சு புதுச்சேரி 1674.",
             "கர்நாடகப் போர்கள் 1746-1763. ஆற்காடு கைப்பற்றல் 1751 (கிளைவ்). வந்தவாசிப் போர் 1760. பாரிஸ் ஒப்பந்தம் 1763.",
             "வேலு நாச்சியார்: சிவகங்கை மீட்பு 1780, தளபதி குயிலி. கட்டபொம்மன்: தூக்கு 16 அக்டோபர் 1799, கயத்தாறு.",
             "மருது சகோதரர் பிரகடனம் 1801. வேலூர் சிப்பாய் கிளர்ச்சி 10 ஜூலை 1806.",
             "வ.உ.சி: சுதேசி நீராவிக் கப்பல் 1906, தண்டனை 1908. வாஞ்சிநாதன் 1911. உப்பு சத்தியாகிரகம் (வேதாரண்யம்) 1930. சுதந்திரம் 1947. தமிழ்நாடு பெயர் 1969."]},
          open("tools/story/tn6.json", "w"), ensure_ascii=False, indent=1)
print(n, "shots", sum(len(s["nar"]) for s in out), "chars; thumb", thumb)
