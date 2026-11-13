# Builds tools/story/delhi2.json: the shot list for "Delhi Sultanate part 2 - the Khalji dynasty".
# nar = Tamil narration for that picture, scene = English picture description, text = on-screen text drawn in code,
# anim = id of a Manim animation drawn OVER the pictures (one step of the animation per picture that carries the id).
import json
C = {
 "JAL": "Jalaluddin Khalji, a gentle 70-year-old sultan with a long white beard, kind eyes, white turban with a green jewel, pale green robe",
 "ALA": "Alauddin Khalji, a tall fierce man in his thirties with a sharp black beard and thick eyebrows, dark red turban with a gold crest, black and gold armour",
 "KAF": "Malik Kafur, a lean clean-shaven general with sharp features, blue turban, silver armour with a blue cloak",
 "MON": "Mongol horsemen in fur hats and leather armour carrying bows",
}
S = [
# --- scene 1: the hook
("ஒரு மனிதன். தன்னை நம்பிய மாமனாரையே கொன்றான்.", "Silhouettes on a river bank at a blood-red sunset: an old king with open arms, behind him a tall man with a raised sword, dramatic, no blood.", "", ""),
("அந்தக் கறையோடு டெல்லி அரியணையில் அமர்ந்தான்.", "{ALA} sitting on a golden throne in a dark palace hall, cold hard stare, a single beam of light.", "", ""),
("ஆனால் அதே மனிதன், உலகை நடுங்க வைத்த மங்கோலியர்களை விரட்டினான்.", "{ALA} on a black horse with a raised sword, {MON} riding away in a cloud of dust.", "", ""),
("சந்தையில் ஒவ்வொரு பொருளுக்கும் விலை நிர்ணயித்தான்.", "A busy medieval Delhi market: an official holding a big brass weighing scale at a grain stall, merchants and buyers watching.", "", ""),
("அவனுடைய படை தமிழ்நாட்டின் மதுரை வரை வந்தது.", "A medieval army with war elephants and banners marching toward a tall South Indian temple tower among palm trees.", "", ""),
("அவன் வீரனா, வில்லனா? கடைசியில் நீங்களே சொல்லுங்கள்.", "Close portrait of {ALA}, one half of his face in warm golden light, the other half in deep shadow.", "வீரனா? வில்லனா?", ""),
("இது டெல்லி சுல்தானியத்தின் இரண்டாம் அத்தியாயம். கில்ஜி வம்சம்.", "An old open book glowing on a table, a red sunrise over the Delhi skyline with a tall tower rising out of its pages.", "டெல்லி சுல்தானியம் – பகுதி 2 | கில்ஜி வம்சம்", ""),
# --- scene 2: 1290, the gentle old king
("முந்தைய பகுதியில் பால்பனின் வம்சம் சரிந்ததைப் பார்த்தோம்.", "An empty dusty throne hall with a cracked crown lying on the floor, torn banners, evening light.", "", ""),
("1290. ஜலாலுதீன் கில்ஜி டெல்லியின் அரசரானார். கில்ஜி வம்சம் தொடங்கியது.", "{JAL} being crowned in a grand hall, nobles bowing on both sides.", "", "tl1"),
("ஆனால் ஆறே ஆண்டுகளில், 1296-இல், அந்த அரியணையில் வேறொருவன் அமர்ந்திருப்பான்.", "{JAL} sitting on a throne, far behind him a dark figure half hidden by a pillar watching him.", "", "tl1"),
("அரசராகும்போது ஜலாலுதீனுக்கு எழுபது வயது.", "Portrait of {JAL}, soft smile, warm golden glow behind his head.", "ஜலாலுதீன் கில்ஜி (1290 – 1296)", ""),
("மிகவும் மென்மையான மனிதர். எதிரிகளையும் மன்னித்துவிடுவார்.", "{JAL} gently raising his hand in forgiveness while guards unlock the chains of kneeling prisoners.", "", ""),
("அந்த மென்மையே அவருக்கு ஆபத்தானது.", "{JAL} walking alone in a palace garden, across the path in front of him falls the long dark shadow of a sword.", "", ""),
# --- scene 3: the ambitious nephew
("அவருடைய சகோதரனின் மகன் அலாவுதீன். அவனுக்குத் தன் மகளையே திருமணம் செய்து கொடுத்திருந்தார்.", "A royal wedding: {JAL} blessing a young bridegroom, {ALA}, and a bride in red and gold, flower garlands.", "அலாவுதீன் – மருமகன்", ""),
("மாமனாருக்கு அவன் மீது அளவில்லாத நம்பிக்கை. காரா என்ற பகுதியின் ஆளுநராக்கினார்.", "{JAL} handing a rolled scroll with a red seal to {ALA} who bows his head.", "காரா ஆளுநர் – அலாவுதீன்", ""),
("ஆனால் அலாவுதீனின் கண் டெல்லி அரியணை மீது இருந்தது.", "{ALA} standing on a balcony at night, staring at a distant glowing palace on the horizon.", "", ""),
("அரியணைக்குப் படை வேண்டும். படைக்குப் பணம் வேண்டும்.", "{ALA} at a table in a tent with two officers, an open empty treasure chest in front of them.", "", ""),
("1296. அரசரிடம் சொல்லாமலேயே, தெற்கே தேவகிரி மீது படையெடுத்தான்.", "Horsemen led by {ALA} riding fast through rocky hills toward a great fort on a hilltop.", "1296 – தேவகிரி படையெடுப்பு", ""),
("அங்கிருந்து மலை போல் தங்கம், வெள்ளி, முத்துக்களைக் கொண்டு வந்தான்.", "A long line of elephants and carts loaded with open chests of gold, silver and pearls on a road.", "", ""),
("இப்போது அவனிடம் பணம் இருந்தது. மீதி இருந்தது ஒரே ஒரு தடை.", "{ALA} standing among glowing chests of gold, looking down at a small royal crown in his hand.", "", ""),
# --- scene 4: Kara, the betrayal
("மருமகன் வெற்றியோடு திரும்பியதைக் கேட்டு ஜலாலுதீன் மகிழ்ந்தார்.", "{JAL} smiling happily as he reads a letter, a messenger kneeling in front of him.", "", ""),
("அமைச்சர்கள் எச்சரித்தார்கள். அவர் கேட்கவில்லை.", "Worried ministers with raised hands pleading with {JAL}, who smiles and waves them away.", "", ""),
("சில வீரர்களோடு மட்டும், படகில் கங்கையைக் கடந்து காராவுக்கு வந்தார்.", "A royal boat with a red canopy crossing a wide calm river, {JAL} seated in it with only a few guards.", "", ""),
("கரையில் அலாவுதீன் காத்திருந்தான். காலில் விழுந்து வணங்கினான்.", "On a sandy river bank {ALA} kneeling with folded hands at the feet of {JAL}.", "", ""),
("மாமனார் அன்போடு அவனைத் தூக்கி அணைத்துக்கொண்டார்.", "{JAL} warmly embracing {ALA} on a river bank, the boat behind them.", "", ""),
("அந்த நொடியில் அலாவுதீன் ஒரு சைகை செய்தான். வாள்கள் மின்னின.", "Dark silhouettes of soldiers with raised swords glinting against a red sunset on a river bank, no blood.", "", ""),
("1296. மாமனாரின் இரத்தத்தின் மீது அலாவுதீன் சுல்தானானான்.", "{ALA} lifting a golden crown high above his head on a river bank under a dark red sky.", "1296 – அலாவுதீன் கில்ஜி சுல்தான்", ""),
("நம்பியவரையே வீழ்த்துவது சரியா? உங்கள் கருத்தை கமெண்டில் சொல்லுங்கள்.", "An empty royal boat with a red canopy drifting alone on a wide river at dusk.", "உங்கள் கருத்து? கமெண்டில் சொல்லுங்கள்", ""),
# --- scene 5: the Mongols
("அரியணை கிடைத்தது. ஆனால் உடனே ஒரு பெரிய ஆபத்து வந்தது.", "{ALA} on a throne leaning forward as a dusty messenger rushes into the hall.", "", ""),
("மங்கோலியர்கள். உலகையே நடுங்க வைத்த படை, டெல்லியின் வாசல் வரை வந்தது.", "A huge army of {MON} on a wide plain, the walls and towers of Delhi far in the distance.", "", ""),
("1299. கிலி என்ற இடத்தில் அலாவுதீன் அவர்களை நேருக்கு நேர் எதிர்த்தான்.", "Two great armies facing each other on a plain, {ALA} at the front of one on a black horse.", "1299 – கிலி போர்", ""),
("மங்கோலியர்கள் பின்வாங்கினார்கள்.", "{MON} turning their horses and riding away at night, dust and torches.", "", ""),
("மீண்டும் வந்தால் தடுக்க, டெல்லியில் சிரி என்ற புதிய கோட்டையைக் கட்டினான்.", "Workers building thick stone fort walls and round towers, {ALA} watching with a plan in his hand.", "சிரி கோட்டை – அலாவுதீன்", ""),
("எல்லைக் கோட்டைகளைப் பலப்படுத்தி, பெரிய நிலையான படையை உருவாக்கினான்.", "Long straight rows of soldiers and horsemen on a parade ground, {ALA} inspecting them.", "", ""),
# --- scene 6: conquests of the north
("பிறகு வட இந்தியா முழுவதும் அவன் படை பாய்ந்தது.", "A cavalry charge with red banners across a plain, seen from the side, dust flying.", "", ""),
("1299-இல் குஜராத் விழுந்தது.", "An army entering a rich coastal city with sailing ships in the harbour.", "", "cq"),
("1301-இல் ரணதம்பூர் கோட்டை.", "A great fort on a steep rocky hill surrounded by an army camp with tents.", "", "cq"),
("1303-இல் சித்தூர்.", "A long fort wall with towers on top of a hill at dawn, an army climbing the winding road.", "", "cq"),
("1305-இல் மாளவம்.", "Horsemen with banners riding through a tall stone city gate.", "", "cq"),
("தன்னை இரண்டாம் அலெக்சாண்டர் என்று அழைத்துக்கொண்டான்.", "{ALA} standing proudly with one hand on his sword, behind him a huge gold coin.", "பட்டம்: இரண்டாம் அலெக்சாண்டர் (சிக்கந்தர்-இ-சானி)", ""),
# --- scene 7: the market reforms
("இவ்வளவு பெரிய படைக்கு எப்படிச் சம்பளம் கொடுப்பது?", "A very long queue of soldiers waiting at a pay table, {ALA} watching thoughtfully.", "", ""),
("அலாவுதீன் ஒரு புதிய வழி கண்டான். சம்பளத்தைக் குறைவாக வைத்தான்.", "A clerk handing a small bag of coins to a soldier at a table.", "", ""),
("அந்தக் குறைந்த சம்பளத்தில் வீரன் வாழ வேண்டுமானால், பொருட்களின் விலையும் குறைவாக இருக்க வேண்டும்.", "A soldier with his wife and child at a market stall looking at sacks of grain.", "", ""),
("அதனால் விலையை அரசே நிர்ணயித்தது. தானியத்துக்கு ஒரு சந்தை.", "A grain market with heaps of wheat and rice in sacks, a royal officer reading from a scroll.", "", "mk"),
("துணிக்கு ஒரு சந்தை.", "A cloth market with rolls of bright coloured fabric on stalls, buyers and merchants.", "", "mk"),
("குதிரைக்கும் கால்நடைக்கும் ஒரு சந்தை.", "A horse and cattle market in an open ground, fine horses tied in rows.", "", "mk"),
("சந்தையைக் கண்காணிக்க அதிகாரிகள். எடையில் ஏமாற்றினால் கடும் தண்டனை.", "A stern market officer checking a merchant's weighing scale, the merchant looking nervous.", "சந்தை அதிகாரி: ஷஹ்னா-இ-மண்டி", ""),
("படையிலும் ஏமாற்று கூடாது. குதிரைகளுக்கு முத்திரை. அதன் பெயர் தாக்.", "A royal stable: a fine horse with a small royal mark on its side, a soldier holding its reins.", "தாக் = குதிரைக்கு முத்திரை", ""),
("ஒவ்வொரு வீரனின் அடையாளமும் பதிவேட்டில். அதன் பெயர் சேரா.", "A clerk writing in a big register at a desk while a soldier stands in front of him.", "சேரா = வீரனின் அடையாளப் பதிவு", ""),
# --- scene 8: Malik Kafur and the march to the south
("அலாவுதீனின் மிகப் பெரிய ஆயுதம் ஒரு மனிதன். மாலிக் கபூர்.", "Portrait of {KAF}, calm confident eyes, golden glow.", "மாலிக் கபூர்", ""),
("குஜராத்தில் அடிமையாக வாங்கப்பட்டவன். திறமையால் படைத் தளபதியானான்.", "{KAF} kneeling to receive a sword from {ALA} in a palace hall.", "", ""),
("அலாவுதீன் அவனைத் தெற்கே அனுப்பினான்.", "{KAF} on a white horse leading a large army out of a tall city gate.", "", ""),
("1307-இல் தேவகிரி பணிந்தது.", "A great hill fort with an army in front of it, a white flag on the walls.", "", "rt"),
("1310-இல் வாரங்கல்.", "A stone fort with tall carved gateways, an army camped outside.", "", "rt"),
("1311-இல் ஹொய்சாளர்களின் துவாரசமுத்திரம்.", "A richly carved South Indian stone temple city beside a lake, an army approaching.", "", "rt"),
("அதே ஆண்டு, படை தமிழ்நாட்டுக்குள் நுழைந்தது. மதுரை.", "An army with elephants in front of tall South Indian temple towers and palm trees.", "", "rt"),
("மதுரையில் அப்போது பாண்டிய சகோதரர்கள் சுந்தர பாண்டியனும் வீர பாண்டியனும் அரியணைக்காக மோதிக்கொண்டிருந்தார்கள்.", "Two South Indian princes in white silk dhotis, gold ornaments and small golden crowns facing each other angrily in a temple courtyard.", "சுந்தர பாண்டியன் – வீர பாண்டியன்", ""),
("அந்தப் பிளவைப் பயன்படுத்தி, மாலிக் கபூர் பெரும் செல்வத்தோடு டெல்லி திரும்பினான்.", "A long line of elephants loaded with treasure chests leaving a South Indian temple city.", "1311 – மாலிக் கபூர் மதுரையில்", ""),
("சகோதரர்கள் ஒன்றாக நின்றிருந்தால் வரலாறு மாறியிருக்குமா?", "A royal banner with two golden fish torn into two halves, lying on stone steps.", "நீங்கள் என்ன நினைக்கிறீர்கள்?", ""),
# --- scene 9: the end of the Khaljis
("டெல்லியில் அலாவுதீன் அலாய் தர்வாசா என்ற அழகிய நுழைவாயிலைக் கட்டினான்.", "A beautiful domed gateway of red sandstone with white marble bands and arched doors, blue sky.", "அலாய் தர்வாசா – 1311", ""),
("அவன் அவையில் புகழ்பெற்ற கவிஞர் அமீர் குஸ்ரு இருந்தார்.", "A poet in a cream robe and turban reciting from a book in a royal court, courtiers listening.", "அவைக் கவிஞர்: அமீர் குஸ்ரு", ""),
("1316. அலாவுதீன் நோயுற்று இறந்தான்.", "An empty golden throne in a dim hall with a dark red turban resting on the seat.", "", "tl2"),
("நான்கே ஆண்டுகளில், 1320-இல், கில்ஜி வம்சமே முடிந்தது.", "A grand palace at dusk with its red banners falling from the walls.", "", "tl2"),
("வஞ்சகத்தில் தொடங்கிய ஆட்சி, வஞ்சகத்திலேயே முடிந்தது.", "A fallen golden crown on the floor of a dark palace hall, long shadows of men with swords on the wall.", "", ""),
("மங்கோலியரைத் தடுத்தவன். சந்தையைச் சீர்திருத்தியவன். ஆனால் மாமனாரைக் கொன்றவன்.", "Close portrait of {ALA}, one half of his face in warm golden light, the other half in deep shadow, looking straight ahead.", "", ""),
("அலாவுதீன் வீரனா, வில்லனா? உங்கள் பதிலை கமெண்டில் எழுதுங்கள்.", "A big brass balance scale on a table: a golden crown on one pan, a sword on the other.", "வீரனா? வில்லனா? – கமெண்டில் சொல்லுங்கள்", ""),
("அடுத்த பகுதியில்: தலைநகரையே தூக்கிக்கொண்டு போன அரசன்.", "A huge crowd of people with carts and bundles walking along a long road, a king on an elephant among them.", "அடுத்து: துக்ளக் வம்சம்", ""),
]
out = []
for i, (nar, scene, text, anim) in enumerate(S, 1):
    for k, v in C.items():
        scene = scene.replace("{" + k + "}", v)
    shot = {"n": i, "nar": nar, "scene": scene, "text": text}
    if anim:
        shot["anim"] = anim
        shot["text"] = ""
    out.append(shot)
SCENES = [  # (first picture, how the voice should feel)
 (1, "dark, gripping and fast, a shocking opening, then rising wonder, ending on a sharp direct question to the listener"),
 (8, "calm storyteller, then warm and gentle for the kind old king, ending with a quiet warning"),
 (14, "warm at first, then sly and hungry with ambition, quick and excited for the raid and the treasure, ending cold"),
 (21, "happy and innocent, then tense, slow and quiet at the river, a held breath before the betrayal, then heavy and shocked, the last line a direct question"),
 (29, "urgent and alarmed, big and fearful for the Mongols, then firm, brave and proud"),
 (35, "fast, bold and triumphant, the four conquests hit like drum beats, then proud and boastful"),
 (41, "curious and clever like explaining a smart trick, clear and brisk, the three markets counted crisply, then strict"),
 (50, "admiring, then marching and energetic, the four places counted like steps of a journey, then sad about the quarrelling brothers, ending on a thoughtful question"),
 (60, "calm and proud, then slow and grave for the death and the fall, then a strong direct question, ending with an exciting promise of the next part"),
]
ANIMS = {   # drawn by tools/story/overlay_anim.py (Manim) over the pictures; one item per picture carrying the id
 "tl1": {"kind": "timeline", "items": [["1290", "ஜலாலுதீன் கில்ஜி"], ["1296", "அலாவுதீன் கில்ஜி"]],
         "fallback": "1290 ஜலாலுதீன் கில்ஜி → 1296 அலாவுதீன் கில்ஜி"},
 "cq": {"kind": "list", "title": "அலாவுதீனின் வெற்றிகள்",
        "items": [["1299", "குஜராத்"], ["1301", "ரணதம்பூர்"], ["1303", "சித்தூர்"], ["1305", "மாளவம்"]],
        "fallback": "1299 குஜராத் | 1301 ரணதம்பூர் | 1303 சித்தூர் | 1305 மாளவம்"},
 "mk": {"kind": "table", "title": "சந்தைச் சீர்திருத்தம்", "head": ["சந்தை", "விலை"],
        "items": [["தானியம்", "அரசு விலை"], ["துணி", "அரசு விலை"], ["குதிரை, கால்நடை", "அரசு விலை"]],
        "fallback": "தானியம், துணி, குதிரை: தனித்தனிச் சந்தை, அரசு நிர்ணயித்த விலை"},
 "rt": {"kind": "route", "title": "மாலிக் கபூரின் தெற்குப் பயணம்", "start": ["டெல்லி", 77.2, 28.6],
        "items": [["1307", "தேவகிரி", 75.2, 19.9, "L"], ["1310", "வாரங்கல்", 79.6, 18.0, "R"],
                  ["1311", "துவாரசமுத்திரம்", 76.0, 13.2, "L"], ["1311", "மதுரை", 78.1, 9.9, "R"]],
        "fallback": "டெல்லி → தேவகிரி 1307 → வாரங்கல் 1310 → துவாரசமுத்திரம் 1311 → மதுரை 1311"},
 "tl2": {"kind": "timeline", "items": [["1316", "அலாவுதீன் மறைவு"], ["1320", "கில்ஜி வம்சம் முடிவு"]],
         "fallback": "1316 அலாவுதீன் மறைவு → 1320 கில்ஜி வம்சம் முடிவு"},
}
json.dump({"title": "மாமனாரைக் கொன்று அரசனானவன் – டெல்லி சுல்தானியம் பகுதி 2", "shots": out, "scenes": SCENES, "anims": ANIMS,
           "exam_cards": [
             "கில்ஜி வம்சம் தொடங்கிய ஆண்டு 1290. நிறுவியவர் ஜலாலுதீன் கில்ஜி.",
             "அலாவுதீன் கில்ஜியின் ஆட்சி 1296 முதல் 1316 வரை. பட்டம்: இரண்டாம் அலெக்சாண்டர்.",
             "சந்தைச் சீர்திருத்தம், தாக், சேரா முறைகள்: அலாவுதீன் கில்ஜி.",
             "தென்னிந்தியப் படையெடுப்பை நடத்தியவர் மாலிக் கபூர். மதுரைக்கு வந்த ஆண்டு 1311.",
             "அலாய் தர்வாசா, சிரி கோட்டை: அலாவுதீன் கில்ஜி. அவைக் கவிஞர்: அமீர் குஸ்ரு."]},
          open("tools/story/delhi2.json", "w"), ensure_ascii=False, indent=1)
print(len(out), "shots")
