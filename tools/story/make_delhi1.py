# Builds tools/story/delhi1.json: the shot list for "Delhi Sultanate part 1" (one picture per spoken sentence).
# nar = Tamil narration for that picture, scene = English picture description, text = on-screen text drawn in code.
import json
C = {
 "BOY": "a thin 10-year-old boy with short black hair, big dark eyes, plain brown sleeveless tunic",
 "AIBAK": "Qutb-ud-din Aibak, a strong man with a short black beard, red turban with a gold brooch, red robe",
 "YAIBAK": "young Aibak, a lean young man with a short black beard, simple cream cloth cap, brown tunic",
 "GHORI": "Muhammad Ghori, a king with a pointed golden helmet, dark beard, royal blue robe",
 "ILT": "Iltutmish, a dignified man with a trimmed grey-black beard, green turban with a pearl, teal robe",
 "RAZ": "Razia Sultana, a brave young woman with long dark hair, a golden crown, orange-red and gold armour",
 "BAL": "Balban, a stern heavy-set man with a long white beard, dark turban, black and steel armour",
 "FORTY": "forty noblemen in dark robes and tall turbans",
}
S = [
# --- scene 1
("எட்டுநூறு ஆண்டுகளுக்கு முன். ஒரு சந்தை.", "A busy 12th-century Central Asian bazaar seen down a long street, cloth stalls, camels, merchants, dusty golden light.", ""),
("அங்கே காய்கறி விற்கவில்லை. மனிதர்களை விற்றார்கள்.", "A slave market: a wooden platform with a row of sad people standing, a rich merchant in a big orange turban pointing at them, buyers watching.", ""),
("விற்பனைக்கு நிற்கும் அந்தச் சிறுவனை யாரும் கவனிக்கவில்லை.", "Close-up of {BOY} standing alone on a wooden platform, worried but determined face, the crowd behind him looking away.", ""),
("ஆனால் அவன் ஒரு நாள் டெல்லியின் அரசனாவான்.", "{BOY} standing against a sunlit wall, his long shadow on the wall is the shape of a king with a crown.", ""),
("அவன் கட்டத் தொடங்கிய கோபுரம் இன்றும் நிற்கிறது.", "The Qutb Minar tower in Delhi today, tall red sandstone tower against a clear sky, small tourists at its base, green lawns.", ""),
("அதைவிட ஆச்சரியம்: அவனுக்குப் பிறகு அரசரான இரண்டு பேரும் அடிமைகளாக இருந்தவர்கள்தான்.", "Two kings sitting on thrones in a palace hall, old iron shackles lying on the floor at their feet.", ""),
("அவர்களுக்கு நடுவில், ஒரு பெண்ணும் அந்த அரியணையில் அமர்ந்தாள்.", "Three thrones in a row: a bearded king on the left, {RAZ} in the centre, an older king on the right.", ""),
("இது டெல்லி சுல்தானியத்தின் முதல் அத்தியாயம்.", "An old open book glowing on a table, with a golden sunrise over the Delhi skyline rising out of its pages.", "டெல்லி சுல்தானியம் – பகுதி 1"),
# --- scene 2
("அந்தச் சிறுவனின் பெயர் குத்புதீன் ஐபக்.", "Portrait of {BOY} with a warm golden glow behind his head, looking straight ahead.", "குத்புதீன் ஐபக்"),
("அவனை வாங்கியவர் ஆப்கானிஸ்தானின் அரசர் முகமது கோரி.", "{GHORI} sitting on a horse, looking down kindly at {BOY} standing in front of him in a market.", ""),
("ஐபக் குதிரைகளைப் பராமரிக்கும் வேலையில் தொடங்கினான்.", "A royal stable: {YAIBAK} as a servant brushing a fine brown horse.", ""),
("திறமையால் படிப்படியாக உயர்ந்து,", "{YAIBAK} in a soldier's uniform climbing a long wide stone staircase toward a bright palace gate.", ""),
("கோரியின் மிக நம்பகமான தளபதியானான்.", "{AIBAK} in steel armour standing beside {GHORI} in a war tent, a map on the table.", ""),
("கோரி இந்தியாவில் வென்ற பகுதிகளை ஆளும் பொறுப்பு ஐபகிடம் வந்தது.", "{GHORI} handing a rolled scroll with a red seal to {AIBAK}, with a map of India behind them.", ""),
("1206. கோரி கொல்லப்பட்டார்.", "A dark night in a tent: a fallen golden pointed helmet on the ground, a single candle, long shadows.", "1206"),
("அவருக்கு மகன் இல்லை. இந்தியப் பகுதிகளை இனி யார் ஆள்வது?", "Worried generals around a table with a map, an empty throne behind them, tense mood.", ""),
("அடிமையாக வந்த ஐபக், லாகூரில் அரசனாக முடிசூடினான்.", "{AIBAK} being crowned in a grand hall in Lahore, nobles kneeling around him.", ""),
("டெல்லி சுல்தானியம் பிறந்தது.", "Sunrise over a fortified medieval city, a new green banner raised on the fort walls.", "1206 – டெல்லி சுல்தானியம் தொடக்கம் | அடிமை (மம்லுக்) வம்சம்"),
# --- scene 3
("ஐபக் கை நிறையக் கொடுப்பவன்.", "{AIBAK} giving handfuls of gold coins to poor villagers, smiling.", ""),
("மக்கள் அவனை \"லாக் பக்ஷ்\" என்று அழைத்தனர். லட்சங்களை அள்ளித் தருபவன் என்று பொருள்.", "A cheering crowd with raised hands, gold coins glittering in the air, {AIBAK} in the middle.", "லாக் பக்ஷ் = லட்சங்களை அள்ளித் தருபவன்"),
("டெல்லியில் அவன் ஒரு பிரம்மாண்டமான கோபுரத்தைக் கட்டத் தொடங்கினான்.", "Workers building a huge red sandstone tower with bamboo scaffolding, {AIBAK} watching from below.", ""),
("அதுதான் குதுப் மினார்.", "The Qutb Minar seen from a low angle, tall and dramatic, red sandstone, golden light.", ""),
("ஆனால் அதை முடிக்க அவனுக்கு நேரம் கிடைக்கவில்லை.", "A half-built tall tower at sunset, in the foreground an hourglass with the sand almost run out.", ""),
("1210. லாகூரில் குதிரை மீது அமர்ந்து சௌகான் என்ற போலோ விளையாடிக்கொண்டிருந்தான்.", "A medieval polo game: horsemen with long sticks chasing a ball on a green field, crowd watching.", "1210"),
("குதிரை தடுமாறியது. ஐபக் கீழே விழுந்தான்.", "A brown horse stumbling in a polo game, the rider thrown off and falling, dust flying, shocked onlookers.", ""),
("நான்கே ஆண்டு ஆட்சி, அதோடு முடிந்தது.", "An empty throne in a dim hall with a golden crown resting on the cushion, a single beam of light.", "ஐபக் இறப்பு – 1210, சௌகான் விளையாட்டில்"),
("கோபுரம் பாதியில் நின்றது. அதை முடிக்கப் போவது யார்?", "A half-built tower at dusk, a mysterious figure seen from behind at its base looking up.", "குதுப் மினார் – தொடங்கியவர் ஐபக்"),
# --- scene 4
("ஐபக் ஒரு காலத்தில் தானே ஒரு அடிமையை வாங்கியிருந்தான்.", "{AIBAK} at a slave market looking at a young man in simple clothes standing on a wooden platform.", ""),
("அவன் பெயர் இல்துமிஷ்.", "Portrait of young {ILT}, calm confident eyes, soft golden glow.", "இல்துமிஷ்"),
("அவனுடைய திறமையைப் பார்த்து, தன் மகளையே அவனுக்குத் திருமணம் செய்து கொடுத்தான்.", "An Indian royal wedding: {ILT} and a bride in red and gold, {AIBAK} blessing them, flower garlands.", ""),
("ஐபக் இறந்த பிறகு, இல்துமிஷ் அரசனானான்.", "{ILT} being crowned in a grand hall, nobles bowing.", ""),
("உண்மையில் சுல்தானியத்தை வலுவாக நிறுவியவன் இவன்தான்.", "{ILT} standing proudly on a fort wall, a strong army and city behind him.", ""),
("மூன்று பெரிய வேலைகள் செய்தான்.", "{ILT} sitting at a desk with three rolled scrolls tied with red ribbons in front of him.", "3 பெரிய வேலைகள்"),
("ஒன்று: தலைநகரை லாகூரிலிருந்து டெல்லிக்கு மாற்றினான்.", "A long caravan of elephants, carts and soldiers travelling along a road toward the gate of a big city.", "1. தலைநகர் லாகூர் → டெல்லி"),
("பாதியில் நின்ற குதுப் மினாரைக் கட்டி முடித்தான்.", "The finished tall red sandstone tower with workers cheering and waving at the top.", "2. குதுப் மினார் – கட்டி முடித்தவர் இல்துமிஷ்"),
("இரண்டு: நாட்டுக்கு ஒரே நாணயம் கொடுத்தான்.", "A royal mint workshop: craftsmen hammering shiny coins, sparks and coins on a table.", ""),
("வெள்ளியில் டங்கா. செப்பில் ஜிட்டால்.", "Close-up of one silver coin and one copper coin on a dark table, plain with no writing.", "டங்கா (வெள்ளி) | ஜிட்டால் (செப்பு)"),
("மூன்று: பெரிய நாட்டைத் தான் ஒருவனாக ஆள முடியாது என்பதால்,", "{ILT} looking at a huge map of his kingdom spread across a table, thoughtful.", ""),
("நிலத்தைப் பகுதிகளாகப் பிரித்து அதிகாரிகளிடம் கொடுத்தான்.", "A map divided into colourful regions, officers in turbans receiving a scroll each from {ILT}.", ""),
("அவர்கள் வரி வசூலித்து, படையையும் பார்த்துக்கொள்வார்கள். இதற்குப் பெயர் இக்தா முறை.", "An officer on a horse collecting sacks of grain from farmers while soldiers stand guard behind him.", "இக்தா முறை"),
("தனக்கு உதவ நாற்பது வலிமையான பிரபுக்களைக் கொண்ட ஒரு குழுவையும் அமைத்தான்.", "{FORTY} sitting in rows in a grand council hall, seen from the front.", ""),
("இந்த நாற்பது பேரை நினைவில் வையுங்கள். கதையின் வில்லன்கள் இவர்கள்தான்.", "{FORTY}, dramatic dark lighting, glowing eyes, ominous mood.", "நாற்பதின்மர் குழு (சகல்கானி)"),
# --- scene 5
("இல்துமிஷுக்கு வயதானது. அடுத்த அரசர் யார்?", "An old white-bearded {ILT} sitting alone and thinking on a cushioned seat, evening light.", ""),
("அவனுக்கு மகன்கள் இருந்தார்கள். ஆனால் அவர்கள் மீது அவனுக்கு நம்பிக்கை இல்லை.", "Lazy young princes feasting and laughing, their old father frowning at them from the doorway.", ""),
("அவன் தேர்ந்தெடுத்தது தன் மகளை. அவள் பெயர் ரசியா.", "Portrait of {RAZ}, determined eyes, golden light.", "ரசியா"),
("அந்தக் காலத்தில் இது யாரும் எதிர்பார்க்காத முடிவு.", "Shocked courtiers with wide eyes and open mouths in a palace hall.", ""),
("நாற்பது பிரபுக்களுக்கும் அது பிடிக்கவில்லை.", "{FORTY} whispering angrily with their heads together.", ""),
("இல்துமிஷ் இறந்ததும், அவர்கள் அவனுடைய மகன் ஒருவனை அரியணையில் அமர்த்தினார்கள்.", "Nobles pushing a weak, scared young prince onto a golden throne.", ""),
("அந்த மகன் ஆட்சியைக் கவனிக்கவில்லை. சில மாதங்களிலேயே மக்கள் கொதித்தெழுந்தனர்.", "A young prince lounging with cups of wine inside a palace while an angry crowd shouts outside the gate.", ""),
# --- scene 6
("டெல்லி மக்களின் ஆதரவோடு ரசியா அரியணை ஏறினாள்.", "{RAZ} climbing the steps to a throne while a cheering crowd throws flowers.", "1236"),
("டெல்லியை ஆண்ட முதல் பெண். சுல்தானிய வரலாற்றில் ஒரே பெண்.", "{RAZ} sitting on the golden throne, sunlight streaming in, proud and calm.", "டெல்லியின் முதல் & ஒரே பெண் ஆட்சியாளர்"),
("அவள் திரைக்குப் பின்னால் இருந்து ஆளவில்லை.", "{RAZ} pulling aside a thick curtain and stepping out into the light.", ""),
("ஆண் உடை அணிந்தாள். யானை மீது ஏறி மக்கள் முன் வந்தாள்.", "{RAZ} in a coat and turban riding a decorated elephant in a procession through a crowded street.", ""),
("தானே நீதி வழங்கினாள்.", "{RAZ} on a throne judging a case in an open court, a man pleading in front of her.", ""),
("தானே படையை நடத்தினாள்.", "{RAZ} on a white horse leading an army, sword raised, banners flying.", ""),
("நாற்பது பிரபுக்களுக்கு இது தாங்கவில்லை. ஒரு பெண் தங்களுக்கு உத்தரவிடுவதா?", "{FORTY}, angry faces, pointing fingers, in a shadowy hall.", ""),
("அதுவும், அவள் துருக்கியர் அல்லாத ஒருவருக்கு உயர் பதவி கொடுத்தபோது, அவர்களின் கோபம் எல்லை மீறியது.", "{RAZ} giving a robe of honour to a loyal dark-skinned man while the noblemen behind them scowl.", ""),
("கிளர்ச்சி வெடித்தது.", "Rebel soldiers with torches storming a palace gate at night.", ""),
("ரசியா சிறைபிடிக்கப்பட்டாள்.", "{RAZ} standing dignified in a stone fort room behind iron bars, a small window with moonlight.", ""),
("திரும்பவும் டெல்லியை மீட்கப் போராடினாள். தோற்றாள். 1240-இல் கொல்லப்பட்டாள்.", "A last battle at dusk: {RAZ} on a horse among fighting soldiers, a fallen banner in the foreground, smoke.", "1240"),
("நான்கே ஆண்டுகள். ஆனால் எட்டுநூறு ஆண்டுகள் கடந்தும் அவள் பெயர் மறக்கப்படவில்லை.", "A huge glowing portrait of {RAZ} in the evening sky over the old Delhi skyline.", "ரசியா சுல்தானா – 1236 முதல் 1240"),
# --- scene 7
("ரசியாவை வீழ்த்திய பிறகு, நாற்பது பிரபுக்களே உண்மையான ஆட்சியாளர்களானார்கள்.", "{FORTY} standing behind a throne, holding long strings that go up to a king's hands.", ""),
("அரசர்கள் வெறும் பொம்மைகள்.", "A king on a throne with puppet strings attached to his arms, looking helpless.", ""),
("அந்த நாற்பது பேரில் ஒருவன் அமைதியாக மேலே ஏறிக்கொண்டிருந்தான்.", "{BAL} in a lighter robe, calmly climbing a staircase in a palace, noblemen below him.", ""),
("அவனும் ஒரு காலத்தில் அடிமையாக விற்கப்பட்டவன்தான். அவன் பெயர் பால்பன்.", "Portrait of {BAL}, cold eyes, a faint old iron shackle beside him.", "பால்பன்"),
("பால்பன் அரசனானான்.", "{BAL} sitting on the throne in black and steel, hall silent.", "1266"),
("அவனுக்கு ஒன்று நன்றாகத் தெரியும்: இந்த நாற்பது பேர் இருக்கும் வரை எந்த அரசனும் பாதுகாப்பாக இல்லை.", "Close-up of {BAL} narrowing his eyes, looking at rows of noblemen.", ""),
("ஏனென்றால் அவனே அவர்களில் ஒருவன்.", "{BAL} standing in the same line among the nobles, wearing the same dark robes.", ""),
("அவன் அந்தக் குழுவையே அழித்தான்.", "An empty council hall, rows of empty chairs, {BAL} sitting alone at the far end in darkness.", ""),
("பால்பனின் ஆட்சிக் கொள்கைக்கு ஒரு பெயர் உண்டு: \"இரத்தமும் இரும்பும்\".", "A steel armoured fist gripping a sword, a red banner behind it.", "இரத்தமும் இரும்பும்"),
("எதிர்த்தவர்களுக்கு இரக்கமே இல்லை.", "Guards marching a line of prisoners through the street while {BAL} watches from a balcony.", ""),
("அரசனை சாதாரண மனிதனாக யாரும் நினைக்கக் கூடாது என்பதற்காக,", "{BAL} on a very high golden throne with steps below, a magnificent glowing court.", ""),
("அவைக்கு வருபவர் தரையில் விழுந்து வணங்க வேண்டும், அரசனின் பாதத்தை முத்தமிட வேண்டும் என்ற வழக்கங்களைக் கொண்டுவந்தான்.", "Courtiers lying flat on the floor bowing before the high throne of {BAL}.", "சிஜ்தா (தரையில் வணக்கம்) | பைபோஸ் (பாத முத்தம்)"),
# --- scene 8
("பால்பன் இருபது ஆண்டுகள் இரும்புக் கரம் கொண்டு ஆண்டான்.", "An old {BAL} with an iron-gloved hand gripping the arm of his throne.", ""),
("ஆனால் அவன் ஒன்றை மறந்துவிட்டான். பயத்தால் கட்டிய ஆட்சி, பயமுறுத்துபவன் போனதும் உடைந்துவிடும்.", "A throne room with cracks spreading across the stone walls and pillars, the throne empty, dust falling.", ""),
("அவன் இறந்த மூன்றே ஆண்டுகளில், 1290-இல், அடிமை வம்சமே முடிந்தது.", "A green dynasty banner falling from a tower into the dust.", "1290 – அடிமை வம்சம் முடிவு"),
("அரியணையைக் கைப்பற்றியது ஒரு புதிய குடும்பம்.", "New soldiers in crimson and gold marching into the palace hall, banners raised.", ""),
("அந்தக் குடும்பத்தில் ஒருவன் இருந்தான்.", "A mysterious man in the shadows, only his glowing eyes and a turban visible.", ""),
("தன் சொந்த மாமனாரைக் கொன்று அரசனானவன்.", "On a dark wall, the shadow of a man holding a dagger behind another man sitting.", ""),
("தமிழ்நாட்டின் மதுரை வரை தன் படையை அனுப்பியவன்.", "A huge army marching south toward a tall colourful South Indian temple gopuram, palm trees.", ""),
("அவன் கதை, அடுத்த பகுதியில்.", "A silhouette of a man with a sword on a hill against a blood-red sunset.", "அடுத்த பகுதி: அலாவுதீன் கில்ஜி"),
]
out = []
for i, (nar, scene, text) in enumerate(S, 1):
    for k, v in C.items():
        scene = scene.replace("{" + k + "}", v)
    out.append({"n": i, "nar": nar, "scene": scene, "text": text})
json.dump({"title": "அடிமையிலிருந்து அரசன் – டெல்லி சுல்தானியம் பகுதி 1", "shots": out,
           "exam_cards": [
             "டெல்லி சுல்தானியம் தொடங்கிய ஆண்டு 1206. நிறுவியவர் குத்புதீன் ஐபக். பட்டம்: லாக் பக்ஷ்.",
             "குதுப் மினாரைத் தொடங்கியவர் ஐபக், முடித்தவர் இல்துமிஷ்.",
             "டங்கா, ஜிட்டால் நாணயங்கள், இக்தா முறை, நாற்பதின்மர் குழு: இல்துமிஷ்.",
             "டெல்லியின் முதல் மற்றும் ஒரே பெண் ஆட்சியாளர் ரசியா சுல்தானா, 1236 முதல் 1240 வரை.",
             "இரத்தமும் இரும்பும் கொள்கை, சிஜ்தா, பைபோஸ்: பால்பன்."]},
          open("tools/story/delhi1.json", "w"), ensure_ascii=False, indent=1)
print(len(out), "shots")
