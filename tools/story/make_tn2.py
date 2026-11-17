# Builds tools/story/tn2.json: Tamil Nadu history part 2 - Kalabhras and Pallavas (approved by the owner 2026-11-17).
import json
C = {
 "KAL": "a mysterious Kalabhra king with a stern face, a dark beard, a plain iron crown and a dark cloak, standing in shadow",
 "BUD": "Buddhadatta, a calm Buddhist monk with a shaved head and a saffron robe writing a manuscript",
 "VAJ": "Vajranandi, a Jain monk with a shaved head and a plain white cloth, teaching a small group of students",
 "SIM": "Simhavishnu Pallava, a strong warrior king with a thick moustache, a gold crown, a lion emblem on his chest and a sword",
 "MAH": "Mahendravarman Pallava, a cultured king with a thoughtful smile, a gold crown, fine jewellery and a palm-leaf scroll in one hand",
 "NAR": "Narasimhavarman Mamalla, a very muscular wrestler king with broad shoulders, a gold crown, a thick moustache and a victorious expression",
 "PUL": "Pulakeshin II, a proud Chalukya king with a turban, a heavy moustache and a gold-trimmed green tunic",
 "XUA": "Xuanzang, an old Chinese pilgrim monk with a round hat, a travelling bag of scrolls and a staff",
}
G = [
("intriguing and mysterious, like opening a secret file",
 [("ஒரு காலத்துல தமிழ்நாட்டை ஆண்ட வம்சம், தங்களோட கல்வெட்டுகளையே கிட்டத்தட்ட விட்டுவைக்கல.", "{KAL} in a dark empty stone hall, blank stone walls with no writing behind him.", "", ""),
  ("அவங்களைப் பத்தி நமக்குத் தெரிஞ்சது, அவங்க எதிரிகள் எழுதினதுதான்.", "A bronze plate with old writing lying on a table in candlelight, a silhouette of a scribe behind it.", "", ""),
  ("யாரு அவங்க? அவங்க காலத்தை ஏன் இருண்ட காலம்னு சொன்னாங்க?", "A dark misty ancient Tamil land at night with one glowing question mark in the sky above a silent fort.", "", ""),
  ("தமிழ்நாட்டு வரலாறு, பகுதி 2.", "An old open palm-leaf book glowing on a wooden table with a lit brass lamp, a feather and a green Tamil landscape behind.", "", "")]),
("calm storyteller, building mystery, serious about the copper plate",
 [("சங்க காலம் முடிஞ்சதும், சேரர், சோழர், பாண்டியர் மூணு பேரும் பலவீனமானாங்க.", "Three old royal banners (bow, tiger, fish) drooping and torn in a dusty empty courtyard.", "", ""),
  ("அப்போ வடக்கே இருந்து களப்பிரர் வந்தாங்க. சுமார் 300 வருஷம் தமிழகத்தை ஆண்டதா சொல்றாங்க.", "A dark army of Kalabhra warriors with iron helmets marching down from the northern hills at dusk, {KAL} on a horse in front.", "களப்பிரர்", "tm"),
  ("எட்டாம் நூற்றாண்டு வேள்விக்குடிச் செப்பேடு சொல்லுது: களப்பிரன்னு ஒரு அரசன் பல அரசர்களை வேரோட பிடுங்கி நாட்டைக் கைப்பற்றினான்.", "Ancient engraved copper plates tied with a ring lying on a stone table, a scholar reading them by a lamp.", "வேள்விக்குடிச் செப்பேடு", ""),
  ("ஆனா அவங்களோட சொந்தக் கல்வெட்டுகள் ரொம்பக் குறைவு. அதனால் ஆரம்பகால வரலாற்றாசிரியர்கள் இதை இருண்ட காலம்னு சொன்னாங்க.", "A dark empty room with a single lamp lighting a few blank stone slabs, a historian scratching his head with an open book.", "இருண்ட காலம்?", "")]),
("warm and surprised, turning the myth upside down with real facts",
 [("ஆனா இது முழு உண்மை இல்ல. அந்தக் காலத்துலதான் திருக்குறள் உட்பட பதினெண் கீழ்க்கணக்கு நூல்கள் எழுதப்பட்டுச்சு. நாலடியார் அதுல ஒண்ணு.", "A bright cosy scene of Tamil poets writing on palm leaves in a sunlit hall, stacks of manuscripts tied with cords.", "பதினெண் கீழ்க்கணக்கு", ""),
  ("புத்ததத்தர்ங்கற பௌத்தத் துறவி, அச்சுதவிக்கிராந்தன்ங்கற களப்பிர மன்னன் காலத்துல நூல் எழுதினார்.", "{BUD} writing by an oil lamp in a monastery beside the Kaveri river, a stone stupa in the background.", "", ""),
  ("470-ல ஜைனத் துறவி வஜ்ரநந்தி மதுரையில திராவிட சங்கத்தை உருவாக்கினார்.", "{VAJ} in a Madurai courtyard under a tree with a group of students sitting around him on the ground.", "", ""),
  ("அதனால இப்போ பல ஆய்வாளர்கள், இது இருண்ட காலம் இல்ல, ஆனா பதிவுகள் குறைவான காலம்னு சொல்றாங்க.", "A dim room slowly filling with golden light from a window, scattered scrolls glowing on the table.", "", "")]),
("energetic and triumphant, two armies from north and south closing in",
 [("ஆறாம் நூற்றாண்டுல, தெற்கே பாண்டியன் கடுங்கோனும், வடக்கே பல்லவன் சிம்மவிஷ்ணுவும் களப்பிரரை முறியடிச்சாங்க.", "{SIM} with his army charging from the north while a Pandya king with a fish banner charges from the south, the Kalabhra army caught between them.", "", ""),
  ("காஞ்சிபுரம் பல்லவரின் தலைநகரமாச்சு.", "The grand ancient city of Kanchipuram with tall temple towers, busy streets and a Pallava lion banner flying over the palace.", "காஞ்சிபுரம்", "")]),
("amused and delighted, talking about a clever and playful king",
 [("பல்லவ அரசர்களில் மிகச் சுவையான மனிதர், மகேந்திரவர்மன்.", "{MAH} smiling in a palace garden with a lute beside him.", "மகேந்திரவர்மன்", ""),
  ("அவர் அரசன் மட்டும் இல்ல. கவிஞர், இசைக் கலைஞர், ஓவியர்.", "{MAH} sitting between a painting easel, a veena and a stack of poems, looking happily at all of them.", "", ""),
  ("மத்தவிலாசப் பிரகசனம்னு ஒரு நகைச்சுவை நாடகமே எழுதினார். அதுல ஒரு குடிகாரத் துறவியைக் கேலி பண்றார்.", "A funny stage play in an ancient hall, an actor playing a tipsy monk stumbling with a clay pot while the audience laughs.", "", ""),
  ("மண்டகப்பட்டுக் கல்வெட்டுல அவர் பெருமையா எழுதியிருக்கார்: செங்கல், மரம், உலோகம், சாந்து இல்லாம கட்டின கோயில்னு.", "A rock cave temple carved into a hillside with pillars cut from the rock, a stone inscription beside the entrance, no bricks or wood anywhere.", "மண்டகப்பட்டு", ""),
  ("பாறையைக் குடைஞ்சு கோயில் கட்டுற பல்லவர் கலை இங்கதான் தொடங்குது.", "Sculptors chiselling a pillar inside a rock-cut cave temple as {MAH} watches proudly.", "", "")]),
("dramatic and heroic, a son taking revenge, building to a big victory",
 [("அவர் மகன் நரசிம்மவர்மன், மாமல்லன்னு பேரு. மாமல்லன்னா பெரிய மல்யுத்த வீரன்.", "{NAR} wrestling in a sand arena before cheering crowds, flexing his muscles.", "மாமல்லன்", ""),
  ("அவன் அப்பா காலத்துல சாளுக்கிய மன்னன் புலிகேசி காஞ்சியைத் தாக்கினான்.", "{PUL} leading a Chalukya army against the walls of Kanchipuram, arrows flying and smoke rising.", "", ""),
  ("மாமல்லன் அதுக்குப் பழி வாங்கினான். 642-ல புலிகேசியோட தலைநகர் வாதாபியையே கைப்பற்றினான்.", "{NAR} on a war elephant leading Pallava soldiers into the burning gates of the city of Vatapi, banners with a lion emblem rising.", "642", ""),
  ("அதனால அவனுக்கு வாதாபி கொண்டான்னு பட்டம்.", "{NAR} wearing a victory garland and a gold crown raising his sword as soldiers cheer around him.", "வாதாபி கொண்டான்", ""),
  ("சீனப் பயணி யுவான் சுவாங் அதே காலத்துல காஞ்சிக்கு வந்து, நகரத்தைப் புகழ்ந்து எழுதினார்.", "{XUA} walking through the streets of Kanchipuram with scrolls, looking amazed at the temples and busy markets.", "", "")]),
("proud and awed, like standing before the monuments at sunrise",
 [("அவன் பேரால உருவானதுதான் மாமல்லபுரம்.", "The seaside town of Mamallapuram at sunrise with carved rock monuments and the sea behind, golden light everywhere.", "மாமல்லபுரம்", ""),
  ("அங்க இருக்கிற பஞ்ச பாண்டவ ரதங்கள், ஒவ்வொண்ணும் ஒரே பாறையைச் செதுக்கி உருவாக்கினது.", "Five carved monolithic stone chariot temples of different shapes standing in a sandy courtyard in warm light.", "", ""),
  ("அர்ச்சுனன் தவம் புடைப்புச் சிற்பம் உலகப் புகழ்.", "A huge rock wall covered with carved elephants, people and animals in a lively crowd, tourists tiny at its foot.", "", ""),
  ("கடற்கரைக் கோயிலைக் கட்டினது இராஜசிம்மன். 1984-ல யுனெஸ்கோ மாமல்லபுரத்தை உலகப் பாரம்பரிய இடமா அறிவிச்சது.", "The tall stone Shore Temple beside the blue sea with waves breaking on the rocks, a bright sky.", "யுனெஸ்கோ 1984", "")]),
("friendly and inviting, then a teaser with rising excitement",
 [("கிட்டத்தட்ட 9-ம் நூற்றாண்டுல பல்லவ வம்சத்தை, ஆதித்த சோழன் முடிவுக்குக் கொண்டு வந்தான்.", "A young Chola king in red on a war elephant defeating the Pallava army, a Pallava lion banner falling and a tiger banner rising.", "", ""),
  ("மகாபலிபுரம் நீங்க நேர்ல போயிருக்கீங்களா? கமெண்ட்ல சொல்லுங்க.", "A happy Tamil family taking photos in front of the Mamallapuram stone chariots at sunset.", "உங்கள் அனுபவம்?", ""),
  ("அடுத்த பகுதியில, ஒரு சின்ன அரசு உலகையே ஆளும் பேரரசா மாறுது. சோழர்களின் எழுச்சி. சேனலை subscribe பண்ணுங்க.", "A small red tiger banner on a hill at dawn growing into a vast golden empire map behind it, glowing rays of light.", "", "")]),
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
ANIMS = {"tm": {"kind": "timeline", "items": [["சுமார் 300", "களப்பிரர் ஆட்சி தொடக்கம்"], ["6-ம் நூற்றாண்டு", "பல்லவர், பாண்டியர் வெற்றி"]],
                "fallback": "களப்பிரர்: சுமார் 3-6 நூற்றாண்டு"}}
thumb = [next(s["n"] for s in out if s["nar"].startswith("அப்போ வடக்கே")), next(s["n"] for s in out if s["nar"].startswith("அவன் பேரால"))]
json.dump({"title": "தமிழகத்தின் இருண்ட காலம் உண்மையா? களப்பிரர் முதல் பல்லவர் வரை – தமிழ்நாட்டு வரலாறு பகுதி 2", "shots": out, "scenes": scenes, "anims": ANIMS, "thumb": thumb,
           "exam_cards": [
             "களப்பிரர்: சுமார் 3 முதல் 6 நூற்றாண்டு. வேள்விக்குடிச் செப்பேடு (பாண்டியர்) குறிப்பிடுகிறது. அச்சுதவிக்கிராந்தன் (புத்ததத்தர் காலம்).",
             "பதினெண் கீழ்க்கணக்கு நூல்கள் இந்தக் காலம். வஜ்ரநந்தி, திராவிட சங்கம், மதுரை, 470.",
             "பல்லவர்: தலைநகரம் காஞ்சிபுரம். சிம்மவிஷ்ணு, களப்பிரரை வென்றவர்.",
             "மகேந்திரவர்மன்: மத்தவிலாசப் பிரகசனம், குடைவரைக் கோயில், மண்டகப்பட்டுக் கல்வெட்டு.",
             "நரசிம்மவர்மன் (மாமல்லன்): வாதாபி வெற்றி 642, வாதாபிகொண்டான். மாமல்லபுரம்: பஞ்சரதம், கடற்கரைக் கோயில் (இராஜசிம்மன்), யுனெஸ்கோ 1984."]},
          open("tools/story/tn2.json", "w"), ensure_ascii=False, indent=1)
print(n, "shots", sum(len(s["nar"]) for s in out), "chars; thumb", thumb)
