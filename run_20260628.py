# -*- coding: utf-8 -*-
"""Build + publish the 8 articles for the 2026-06-28 run (knockout-eve)."""
import json, os, sys, time
from bodies import b1, b2, b3, b4, b5, b6, b7, b8

RUN_ID = "run-20260628-knockouts-r32"
GENERATED_AT = "2026-06-28T07:30:00Z"
ENDPOINT = "https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles"

IMG = {
 1:"https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Spanish_pre-match_preparations_-_Japan_vs._Spain%2C_2024_Summer_Olympic_men%27s_association_football%2C_2024-08-02.jpg/1280px-Spanish_pre-match_preparations_-_Japan_vs._Spain%2C_2024_Summer_Olympic_men%27s_association_football%2C_2024-08-02.jpg",
 2:"https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Jan_Paul_van_Hecke_24012026_%282%29_%28cropped%29.jpg/1280px-Jan_Paul_van_Hecke_24012026_%282%29_%28cropped%29.jpg",
 3:"https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/FWC_2018_-_Group_D_-_ARG_v_ISL_-_Messi_penalty_kick.jpg/1280px-FWC_2018_-_Group_D_-_ARG_v_ISL_-_Messi_penalty_kick.jpg",
 4:"https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/SoFi_Stadium_2023.jpg/1280px-SoFi_Stadium_2023.jpg",
 5:"https://upload.wikimedia.org/wikipedia/commons/c/cb/2022_FIFA_World_Cup_England_6%E2%80%932_Iran_-_%2815%29.jpg",
 6:"https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Kylian_Mbappe_France_v_Senegal_16_June_2026-344.jpg/1280px-Kylian_Mbappe_France_v_Senegal_16_June_2026-344.jpg",
 7:"https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Uzbekistan_vs._Spain%2C_2024_Summer_Olympic_men%27s_association_football%2C_2024-07-24_%28120%29.jpg/1280px-Uzbekistan_vs._Spain%2C_2024_Summer_Olympic_men%27s_association_football%2C_2024-07-24_%28120%29.jpg",
 8:"https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Cristiano_Ronaldo_%28L%29%2C_Luka_Modric_%28R%29_-_Croatia_vs._Portugal%2C_10th_June_2013.jpg/1280px-Cristiano_Ronaldo_%28L%29%2C_Luka_Modric_%28R%29_-_Croatia_vs._Portugal%2C_10th_June_2013.jpg",
}

articles = [
 {"title":"Испания обыграла Уругвай 1:0 и выиграла группу H на ЧМ-2026",
  "slug":"spain-1-0-uruguay-baena-world-cup-2026-group-h","body":b1,
  "excerpt":"Гол Алекса Баэны после ошибки Фернандо Муслеры принёс Испании победу над Уругваем 1:0 и первое место в группе H. Команда Марсело Бьелсы вылетела с чемпионата мира.",
  "category":"Отчёты о матчах","type":"match_report","image_url":IMG[1],"image_base64":None,
  "sources":["https://www.skysports.com/football/news/12098/13556686/world-cup-2026-uruguay-0-1-spain-alex-baena-goal-after-fernando-muslera-error-sends-marcelo-bielsas-team-out","https://www.aljazeera.com/sports/2026/6/27/spain-beat-uruguay-1-0-to-clinch-world-cup-group-h-top-spot","https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/uruguay-spain-match-report-highlights"],
  "source_type":"news"},

 {"title":"«Тоттенхэм» подписал защитника сборной Нидерландов ван Хекке за 52 млн фунтов",
  "slug":"van-hecke-tottenham-brighton-transfer-june-2026","body":b2,
  "excerpt":"«Тоттенхэм» оформил трансфер центрального защитника сборной Нидерландов Яна Пауля ван Хекке из «Брайтона». По данным Sky Sports, сумма сделки – около 52 млн фунтов.",
  "category":"Новости игроков","type":"transfer","image_url":IMG[2],"image_base64":None,
  "sources":["https://www.skysports.com/football/news/11095/13546618/transfer-news-summer-transfer-window-2026-premier-league-deals-ins-and-outs"],
  "source_type":"news"},

 {"title":"Аргентина обыграла Иорданию 3:1, Месси снова забил на ЧМ-2026",
  "slug":"argentina-3-1-jordan-messi-world-cup-2026-group-j","body":b3,
  "excerpt":"Аргентина победила Иорданию 3:1 и с девятью очками выиграла группу J. Месси отметился голом со штрафного, а в 1/16 финала чемпионов мира ждёт Кабо-Верде.",
  "category":"Отчёты о матчах","type":"match_report","image_url":IMG[3],"image_base64":None,
  "sources":["https://www.espn.com/soccer/report/_/gameId/760483","https://www.outlookindia.com/sports/football/jordan-vs-argentina-fifa-world-cup-2026-group-j-match-report-dallas-stadium"],
  "source_type":"news"},

 {"title":"Плей-офф ЧМ-2026 стартует 28 июня: расписание и пары 1/16 финала",
  "slug":"world-cup-2026-round-of-32-knockouts-begin-june-28","body":b4,
  "excerpt":"Чемпионат мира 2026 года выходит в плей-офф: 28 июня матчем ЮАР – Канада стартует новая стадия 1/16 финала. Рассказываем о формате, расписании и главных парах.",
  "category":"ЧМ-2026","type":"preview","image_url":IMG[4],"image_base64":None,
  "sources":["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_knockout_stage","https://www.skysports.com/football/news/11095/13556636/world-cup-2026-bracket-and-knockout-fixtures-whos-facing-who-in-the-last-32-and-route-to-final","https://www.aljazeera.com/sports/2026/6/27/which-teams-have-qualified-for-the-world-cup-2026-knockouts-round-of-32"],
  "source_type":"news"},

 {"title":"Англия обыграла Панаму 2:0, Кейн установил рекорд сборной на ЧМ",
  "slug":"england-2-0-panama-kane-record-world-cup-2026-group-l","body":b5,
  "excerpt":"Беллингем забил и отдал передачу, а Гарри Кейн 11-м голом на чемпионатах мира установил рекорд сборной Англии. «Три льва» обыграли Панаму 2:0 и выиграли группу L.",
  "category":"Отчёты о матчах","type":"match_report","image_url":IMG[5],"image_base64":None,
  "sources":["https://www.skysports.com/football/panama-vs-england/549837","https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/panama-england-match-report-highlights","https://www.englandfootball.com/england/mens-senior-team/fixtures-results/2025-26/World-Cup/panama-v-england-fifa-world-cup-saturday-27-june-2026-match-centre"],
  "source_type":"news"},

 {"title":"Топ-7 претендентов на титул ЧМ-2026 перед стадией плей-офф",
  "slug":"top-7-title-favourites-world-cup-2026-knockouts","body":b6,
  "excerpt":"Групповой этап чемпионата мира 2026 года завершён. Разбираем семь сборных, которые перед плей-офф выглядят главными претендентами на золото – от Испании до Португалии.",
  "category":"Тренды","type":"ranking","image_url":IMG[6],"image_base64":None,
  "sources":["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_knockout_stage","https://www.aljazeera.com/sports/2026/6/27/which-teams-have-qualified-for-the-world-cup-2026-knockouts-round-of-32","https://www.espn.com/soccer/story/_/id/48939282/2026-fifa-world-cup-fixtures-results-match-schedule-group-stage-knockout-rounds-bracket"],
  "source_type":"trend"},

 {"title":"Узбекистан завершил дебютный ЧМ без очков: 1:3 от ДР Конго",
  "slug":"dr-congo-3-1-uzbekistan-world-cup-2026-debut-ends","body":b7,
  "excerpt":"Сборная Узбекистана повела в матче с ДР Конго, но уступила 1:3 и завершила первый в истории чемпионат мира без набранных очков. ДР Конго впервые вышла в плей-офф.",
  "category":"Сборные","type":"match_report","image_url":IMG[7],"image_base64":None,
  "sources":["https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/congo-dr-uzbekistan-match-report-highlights","https://www.espn.com/soccer/match/_/gameId/760482/uzbekistan-congo-dr","https://www.outlookindia.com/sports/football/dr-congo-vs-uzbekistan-live-score-fifa-world-cup-2026-group-k-cod-vs-uzb-updates-atlanta-stadium-highlights"],
  "source_type":"trend"},

 {"title":"Португалия – Хорватия в 1/16 финала ЧМ-2026: дуэль Роналду и Модрича",
  "slug":"portugal-vs-croatia-round-of-32-preview-world-cup-2026","body":b8,
  "excerpt":"Превью матча 1/16 финала ЧМ-2026 Португалия – Хорватия (2 июля, Торонто): расклад перед игрой, дуэль Роналду и Модрича, ключевые факторы и прогноз.",
  "category":"ЧМ-2026","type":"preview","image_url":IMG[8],"image_base64":None,
  "sources":["https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_knockout_stage","https://www.skysports.com/football/news/11095/13556636/world-cup-2026-bracket-and-knockout-fixtures-whos-facing-who-in-the-last-32-and-route-to-final"],
  "source_type":"trend"},
]

def build_manifest():
    manifest = {"generated_at":GENERATED_AT,"run_id":RUN_ID,"articles":articles}
    with open(os.path.join(os.path.dirname(__file__),"run_20260628_manifest.json"),"w",encoding="utf-8") as f:
        json.dump(manifest,f,ensure_ascii=False,indent=2)
    return manifest

def publish(items):
    import requests
    secret = os.environ.get("AGENT_PUBLISH_SECRET")
    if not secret:
        print("ERROR: AGENT_PUBLISH_SECRET missing"); sys.exit(2)
    headers = {"Content-Type":"application/json","x-agent-secret":secret}
    payload = {"articles":items}
    r = requests.post(ENDPOINT, headers=headers, data=json.dumps(payload), timeout=120)
    print("HTTP", r.status_code)
    try:
        return r.status_code, r.json()
    except Exception:
        print("non-JSON response:", r.text[:500]); return r.status_code, None

if __name__ == "__main__":
    build_manifest()
    print("manifest written:", len(articles), "articles")
    if "--publish" in sys.argv:
        code, resp = publish(articles)
        print(json.dumps(resp, ensure_ascii=False, indent=2) if resp else "no json")
