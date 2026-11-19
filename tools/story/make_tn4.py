# Builds tools/story/tn4.json: Tamil Nadu history part 4 - Rajendra Chola (approved by the owner 2026-11-19).
import json
C = {
 "RJE": "Rajendra Chola, a majestic young king with a gold crown, broad shoulders, a trimmed moustache, rich jewellery and a commanding look, tiger banner behind him",
 "MAH": "Mahinda V, a defeated Sri Lankan king in a simple crown and plain robes with a downcast face",
 "MHP": "Mahipala, a Bengal Pala king in a turban and white robes looking defeated",
 "SRI": "Sangrama Vijayottungavarman, a Srivijaya king with a tall ornate crown and a long Southeast Asian silk robe looking shocked",
}
G = [
("dramatic and astonished, a march across a whole subcontinent",
 [("ஒரு படை நடந்தே கங்கை வரை போச்சு. திரும்பி வரும்போது, தோத்த அரசர்களோட தலையில தண்ணி குடங்களை சுமக்க வச்சாங்கன்னு கல்வெட்டு சொல்லுது.", "A long Chola army marching home along a river with defeated kings carrying big brass water pots on their heads, tiger banners flying.", "கங்கை வரை", ""),
  ("அந்தத் தண்ணி எதுக்கு? ஒரு புது தலைநகரத்தை உருவாக்க.", "A huge sealed brass pot of Ganga water glowing, a half-built grand temple city rising behind it in golden dusk.", "", ""),
  ("தமிழ்நாட்டு வரலாறு, பகுதி 4. இராஜேந்திர சோழன்.", "An old open palm-leaf book glowing on a wooden table with a lit brass lamp, a tiger emblem and a Chola ship model beside it.", "", "")]),
("proud and energetic, a son surpassing his father",
 [("இராஜராஜனுக்குப் பிறகு அரியணை ஏறினவன் அவன் மகன். இராஜேந்திரன். அப்பா உருவாக்கின படையை, அப்பாவே மலைக்கிற அளவுக்கு வளர்த்தான்.", "{RJE} being crowned in a grand golden court hall, his elderly father's portrait glowing behind, banners waving.", "இராஜேந்திர சோழன்", ""),
  ("முதல்ல இலங்கை. அப்பா வடபகுதியைத்தான் பிடிச்சார். மகன் முழு தீவையும் பிடிச்சான்.", "A map-like scene of the whole island of Sri Lanka with Chola ships surrounding it and tiger banners on every coast.", "இலங்கை", ""),
  ("இலங்கை மன்னன் ஐந்தாம் மகிந்தனை சிறைபிடிச்சான். பாண்டியரோட கிரீடமும் நகைகளும் அங்கதான் ஒளிச்சு வச்சிருந்தாங்க. அதையும் மீட்டான்.", "{MAH} being led as a prisoner before {RJE}, a jewelled Pandya crown on a cushion between them.", "", "")]),
("tense and epic, a long march north",
 [("இப்போ பார்வை வடக்கே. கங்கை. சுமார் 1021-ல பெரிய படையை அனுப்பினான்.", "A giant Chola army of elephants, horsemen and foot soldiers marching north through a green plain at sunrise, tiger banners.", "1021", ""),
  ("வழியில கலிங்கம், அதாவது இப்போ ஒடிசா. அப்புறம் வங்காளம். அங்க பால மன்னன் மகிபாலனை தோற்கடிச்சதா கல்வெட்டு சொல்லுது.", "A fierce river battle in Bengal, Chola elephants charging, {MHP} fleeing on a boat.", "வங்காளம்", ""),
  ("படை கங்கை கரையில நின்னு, புனித நீரை குடங்கள்ல எடுத்துட்டு திரும்புச்சு. தோத்த அரசர்கள் அந்தக் குடங்களை சுமந்தாங்க.", "Chola soldiers filling brass pots with holy water at the Ganga bank at dawn while defeated kings in chains stand with pots on their heads.", "கங்கை நீர்க் குடங்கள்", ""),
  ("அதனால இராஜேந்திரனுக்கு ஒரு பட்டம். கங்கை கொண்ட சோழன்.", "{RJE} wearing a victory garland and raising a brass pot of Ganga water before cheering soldiers.", "கங்கை கொண்ட சோழன்", "")]),
("proud and amazed, a new capital rises",
 [("அந்த நீரை வச்சு, ஒரு புது தலைநகரத்தை உருவாக்கினான். கங்கைகொண்ட சோழபுரம்.", "A grand new Chola capital city rising with wide streets, palaces and a huge stone temple in golden light.", "கங்கைகொண்ட சோழபுரம்", ""),
  ("பக்கத்துல சோழ கங்கம்னு ஒரு பெரிய ஏரியையும் வெட்டினான். கங்கை நீரை அதுல ஊத்தினதா சொல்றாங்க.", "Thousands of workers digging a vast lake beside a temple city, priests pouring holy water into it.", "சோழ கங்கம்", ""),
  ("ஏரி கிட்டத்தட்ட பல கிலோமீட்டர் நீளம். வெள்ளக் காலத்துல தண்ணியைச் சேமிக்கவும் உதவுச்சு.", "A very long calm lake with stone embankments and sluice gates, farmers irrigating green fields below.", "", ""),
  ("அங்க அப்பா மாதிரியே ஒரு பெரிய சிவன் கோயில் கட்டினான். கங்கைகொண்ட சோழீஸ்வரம். அதோட விமானம் சுமார் 55 மீட்டர்.", "The majestic Gangaikonda Cholapuram temple with its tiered curved vimana tower against a bright sky, tiny people at its base.", "கங்கைகொண்ட சோழீஸ்வரம்", ""),
  ("2004-ல யுனெஸ்கோ இந்தக் கோயிலையும் உலகப் பாரம்பரிய இடப் பட்டியல்ல சேர்த்துச்சு.", "Visitors from many countries admiring the carved stone temple at sunset, a small world-heritage plaque in front.", "யுனெஸ்கோ 2004", "")]),
("excited and adventurous, the great sea voyage",
 [("ஆனா இராஜேந்திரனோட பெரிய சாதனை, நிலத்துல இல்ல. கடல்ல.", "A vast Chola fleet of tall ships with tiger-banner sails on a deep blue ocean at sunrise.", "", ""),
  ("சுமார் 1025-ல சோழக் கடற்படை கிளம்புச்சு. போன இடம் கடாரம். இப்போ மலேசியாவுல இருக்கிற கெடா.", "Chola warships leaving a harbour with cheering crowds, sailing east into a golden horizon.", "1025", ""),
  ("அங்க ஸ்ரீவிஜய அரசு, வெளிநாட்டு வணிகத்தை கையில வச்சிருந்தது. சோழர் வணிகக் கப்பல்களுக்கு அவங்க தடை போட்டாங்கன்னு ஒரு கருத்து இருக்கு.", "A busy Southeast Asian port with Srivijaya guards blocking a Tamil merchant ship, spices and cargo on the dock.", "ஸ்ரீவிஜயம்", ""),
  ("சோழக் கடற்படை அவங்களை வென்றது. அரசன் சங்கிராம விஜயோத்துங்கவர்மனைச் சிறை பிடிச்சாங்க.", "A sea battle near a tropical coast with Chola ships overpowering Srivijaya ships, {SRI} being captured on deck.", "கடாரம்", ""),
  ("தஞ்சாவூர் கல்வெட்டு, அந்த வெற்றியில கைப்பற்றின 14 இடங்களோட பேரை வரிசையா சொல்லுது. நிக்கோபார் தீவுகூட அதுல இருக்கு.", "A stone temple wall covered with a long Tamil inscription listing places, a small map of islands beside it.", "14 இடங்கள்", ""),
  ("அதனால அவனுக்கு இன்னொரு பட்டம். கடாரம் கொண்டான்.", "{RJE} wearing a victory garland on the deck of a Chola flagship with a sea of ships behind him.", "கடாரம் கொண்டான்", "")]),
("calm and reflective, trade and diplomacy",
 [("இது படையெடுப்பு மட்டும் இல்ல. கடல் வழி வணிகத்தை பாதுகாக்கிற நடவடிக்கையும்தான்.", "Chola ships escorting laden merchant vessels across a calm sea, guards watching the horizon.", "", ""),
  ("அந்தக் காலத்துல தமிழ் வணிகர்கள் தென்கிழக்காசியா, சீனா வரைக்கும் போனாங்க.", "Tamil merchants unloading pepper, cloth and gems at a distant foreign harbour with local traders.", "", ""),
  ("சோழர்கள் சீனாவுக்கு தூதுவர்களையும் அனுப்பினாங்க. 1015-ல ஒரு சோழத் தூதுக்குழு சீனப் பேரரசரைச் சந்திச்சதா சீனப் பதிவு சொல்லுது.", "A Chola delegation presenting gifts to a Chinese emperor in a red-and-gold palace hall.", "சீனா 1015", ""),
  ("உள்நாட்டுலயும் இராஜேந்திரன் ஆட்சி வலுவா இருந்துச்சு. கோயில்கள், பாசனம், நில அளவை எல்லாம் தொடர்ந்துச்சு.", "A prosperous Chola village with irrigation canals, rice fields, a stone temple and officials measuring land.", "", ""),
  ("சுமார் 1044-ல அவன் மறைஞ்சான். அவன் காலத்துல சோழ அரசு, இந்தியாவோட பெரிய கடல் சக்தியா இருந்துச்சு.", "{RJE} older and calm, looking out over the sea from a palace balcony at sunset as ships sail by.", "1044", ""),
  ("ஆனா எல்லா சாம்ராஜ்யத்துக்கும் ஒரு உச்சம் இருக்கு. உச்சம் தொட்ட பிறகு சரிவும் வரும்.", "A tall glowing temple tower at the peak of a hill with long evening shadows and a lone tiger banner.", "", ""),
  ("அடுத்த பகுதியில, சோழர் காலத்துக்குப் பிறகு பாண்டியர்கள், நாயக்கர்கள், மராட்டியர்கள். சேனலை subscribe பண்ணுங்க.", "Three royal banners of a fish emblem, a Nayak lion and a Maratha flag fluttering over an old fort at sunrise.", "", "")]),
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
thumb = [next(s["n"] for s in out if s["nar"].startswith("ஒரு படை")), next(s["n"] for s in out if s["nar"].startswith("அங்க அப்பா")), next(s["n"] for s in out if s["nar"].startswith("சுமார் 1025"))]
json.dump({"title": "கங்கையையும் கடலையும் வென்ற மன்னன்! இராஜேந்திர சோழன் – தமிழ்நாட்டு வரலாறு பகுதி 4", "shots": out, "scenes": scenes, "anims": {}, "thumb": thumb,
           "shorts": [[7, 11, "கங்கை நீரைச் சுமந்த தோற்ற அரசர்கள்!", "கங்கை கொண்ட சோழன்"], [17, 21, "கடல் கடந்து 14 இடங்களை வென்ற சோழர்!", "கடாரம் கொண்டான்"], [11, 13, "கங்கை நீர் ஊற்றிய ஏரி!", "சோழ கங்கம்"]],
           "exam_cards": [
             "இராஜேந்திர சோழன் (1014-1044): கங்கை கொண்ட சோழன், கடாரம் கொண்டான். இலங்கை முழுவதும் வெற்றி, ஐந்தாம் மகிந்தன் சிறை.",
             "கங்கைப் படையெடுப்பு சுமார் 1021: கலிங்கம், வங்காளம் (மகிபாலன்). புதிய தலைநகரம் கங்கைகொண்ட சோழபுரம்.",
             "சோழ கங்கம் ஏரி. கங்கைகொண்ட சோழீஸ்வரம் கோயில், விமானம் சுமார் 55 மீட்டர். யுனெஸ்கோ 2004.",
             "கடாரம் (கெடா, மலேசியா) படையெடுப்பு சுமார் 1025: ஸ்ரீவிஜய அரசு, சங்கிராம விஜயோத்துங்கவர்மன். தஞ்சாவூர் கல்வெட்டில் 14 இடங்கள்.",
             "சோழர் தூதுக்குழு சீனா 1015. இராஜேந்திரன் மறைவு சுமார் 1044."]},
          open("tools/story/tn4.json", "w"), ensure_ascii=False, indent=1)
print(n, "shots", sum(len(s["nar"]) for s in out), "chars; thumb", thumb)
