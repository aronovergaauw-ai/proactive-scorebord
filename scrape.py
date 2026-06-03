from playwright.sync_api import sync_playwright
import os
import json

def haal_scores_op():
    email = os.environ.get('SPOULE_EMAIL')
    wachtwoord = os.environ.get('SPOULE_WACHTWOORD')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Log in
        page.goto("https://app.sportspoule.com/login")
        page.fill("input[type='email']", email)
        page.fill("input[type='password']", wachtwoord)
        page.keyboard.press("Enter")
        page.wait_for_url("**/tabs/**", timeout=15000)

        # 2. Vang de onzichtbare data op
        with page.expect_response(lambda response: "api.sportspoule.com/groups/4285" in response.url and response.request.method == "GET") as response_info:
            page.goto("https://app.sportspoule.com/tabs/groups/4285")
        
        # 3. Lees de data
        data = response_info.value.json()
        deelnemers = data.get('users', [])
        
        # 4. Sorteer deelnemers op punten (hoogste eerst)
        deelnemers.sort(key=lambda x: x.get('points', 0), reverse=True)

        # --- UPDATE: Beperk de lijst tot de TOP 30 ---
        deelnemers = deelnemers[:30]

        # 5. Splits de groep in tweeën voor de 2 kolommen (max 15 per kolom)
        midden = (len(deelnemers) + 1) // 2
        groep1 = deelnemers[:midden]
        groep2 = deelnemers[midden:]

        def bouw_rij(user, positie):
            volledige_naam = user.get('name', 'Unknown')
            voornaam = volledige_naam.split()[0]
            punten = user.get('points', 0)
            
            rij_class = ""
            if positie == 1: rij_class = ' class="podium-1"'
            elif positie == 2: rij_class = ' class="podium-2"'
            elif positie == 3: rij_class = ' class="podium-3"'
            
            return f"<tr{rij_class}><td>{positie}</td><td>{voornaam}</td><td><strong>{punten}</strong></td></tr>\n"

        # Bouw de twee losse tabellen op
        tabel1_rijen = ""
        for i, user in enumerate(groep1, start=1):
            tabel1_rijen += bouw_rij(user, i)
            
        tabel2_rijen = ""
        for i, user in enumerate(groep2, start=midden + 1):
            tabel2_rijen += bouw_rij(user, i)

        # 6. Bouw de HTML (Compactere TV Modus voor 30 man)
        webpagina = f"""
        <html>
            <head>
                <title>ProActive Scoreboard</title>
                <meta http-equiv="refresh" content="900"> 
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #121212; margin: 0; padding: 2vh 2vw; color: #e0e0e0; overflow: hidden; }}
                    h1 {{ text-align: center; color: #ffffff; font-size: 5vh; margin: 1vh 0 2vh 0; letter-spacing: 2px; text-transform: uppercase; }}
                    .container {{ background: #1e1e1e; padding: 2vh 3vw; border-radius: 20px; width: 95vw; margin: 0 auto; box-shadow: 0 10px 30px rgba(0,0,0,0.5); box-sizing: border-box; }}
                    
                    .twee-kolommen {{ display: flex; gap: 4vw; justify-content: space-between; }}
                    
                    /* Tekstgrootte verlaagd van 3.5vh naar 2.6vh voor meer rijen */
                    table {{ width: 48%; border-collapse: collapse; font-size: 2.6vh; }}
                    th, td {{ padding: 1vh 1.5vw; text-align: left; border-bottom: 2px solid #333333; }}
                    th {{ background-color: #2c3e50; color: #ffffff; font-size: 3vh; text-transform: uppercase; }}
                    tr:nth-child(even) {{ background-color: #252525; }}
                    
                    /* Gekleurde top 3 blijft behouden */
                    .podium-1 td {{ font-weight: bold; background-color: #3a2e00; color: #ffd700; }}
                    .podium-2 td {{ font-weight: bold; color: #cccccc; }}
                    .podium-3 td {{ font-weight: bold; color: #cd7f32; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>ProActive World Cup Leaderboard</h1>
                    <div class="twee-kolommen">
                        <table>
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Name</th>
                                    <th>Points</th>
                                </tr>
                            </thead>
                            <tbody>
                                {tabel1_rijen}
                            </tbody>
                        </table>
                        
                        <table>
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Name</th>
                                    <th>Points</th>
                                </tr>
                            </thead>
                            <tbody>
                                {tabel2_rijen}
                            </tbody>
                        </table>
                    </div>
                </div>
            </body>
        </html>
        """

        with open("index.html", "w", encoding="utf-8") as file:
            file.write(webpagina)

        browser.close()

if __name__ == "__main__":
    haal_scores_op()
