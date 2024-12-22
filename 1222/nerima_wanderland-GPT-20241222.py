import streamlit as st
import requests
import folium
import pandas as pd
from datetime import datetime
from streamlit_folium import st_folium
import time
import openai
import os

# OpenAI APIキー
openai.api_key = st.secrets["OPENAI_API_KEY"]
API_KEY =  st.secrets["GoogleMap"]

# 天気APIのURLと都市コード
city_code = "130010"  # 東京の都市コード
url = f"https://weather.tsukumijima.net/api/forecast/city/{city_code}"

# 天気情報取得関数
def get_weather(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"天気情報取得エラー: {e}")
        return None

# GPTコメント生成関数
def generate_gpt_comment(destinations):
    try:
        messages = [
            {"role": "system", "content": "あなたは練馬の地元旅行ガイドのネリーです。"},
            {"role": "user", "content": (
                f"以下の情報を元に、場所1と場所2を組み合わせた冒険や旅行の提案を、100字以内でユニークでわくわくするコメントを作成してください。\n\n"
                f"場所1: {destinations[0]['場所']}\n解説: {destinations[0]['解説']}\n\n"
                f"場所2: {destinations[1]['場所']}\n解説: {destinations[1]['解説']}\n\n"
                "まとめコメント:"
            )}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"コメント生成中にエラーが発生しました: {e}"

# CSVデータ
# CSVデータを直接埋め込み
data = pd.DataFrame([
  {"今の気持ち": "わくわく巨大公園", "場所1": "光が丘公園", "画像1": "pic/002.jpg", "解説1": "光が丘団地に隣接する練馬区最大の公園。キャッチボール、サッカーなどボール遊びができる。近くにショッピングモールやレストランあり。", "住所1": "東京都練馬区光が丘４丁目１-１", "場所2": "久松湯", "画像2": "pic/003.jpg", "解説2": "2014年５月に新装開店。美術館のような斬新な建築の銭湯。大きな天然温泉の露天風呂、人工炭酸泉、電気マッサージ風呂、冷水風呂、冷水シャワー、サウナなどを設置。浴室でプロジェクションマッピングによる光の演出が楽しめる。", "住所2": "東京都練馬区桜台４丁目３２-１５"},
  {"今の気持ち": "平日の疲れを癒したい", "場所1": "石神井公園", "画像1": "pic/shakujiiーpark.jpg", "解説1": "２つの池を取り囲む緑あふれる公園。文豪や有名人が川のほとりの豪邸に住んでいる。なつかしのスワンボートに乗れる。池の周りを歩いて回ると自然を満喫できる。様々な鳥がいてバードウォッチングでも有名。", "住所1": "東京都練馬区石神井台１丁目２６-１", "場所2": "庭の湯", "画像2": "pic/niwanoーyu.jpg", "解説2": "日本を代表する造園設計家、小形研三氏による1,200坪の清閑な日本庭園を臨む「豊島園 庭の湯」。天然温泉をはじめ、健康促進に役立つバーデプールやサウナ、旬の味覚をお楽しみいただけるお食事処、日々の疲れを癒せるリラクゼーションエリアなど館内施設も充実している。こだわりの大人の癒し空間で都会の喧噪を忘れ、やすらぎの時間を過ごすには最高の場所。", "住所2": "練馬区向山3丁目25-1"},
  {"今の気持ち": "まったり散策", "場所1": "練馬城址公園", "画像1": "pic/nerimashoushi-park.jpg", "解説1": "ハリーポッタースタジオツアー東京から、川沿いに5分程度歩くとある。子供用の施設などもあり、芝生に座ったりゆったりできる。", "住所1": "東京都練馬区春日町１丁目", "場所2": "庭の湯", "画像2": "pic/niwanoーyu.jpg", "解説2": "日本を代表する造園設計家、小形研三氏による1,200坪の清閑な日本庭園を臨む「豊島園 庭の湯」。天然温泉をはじめ、健康促進に役立つバーデプールやサウナ、旬の味覚をお楽しみいただけるお食事処、日々の疲れを癒せるリラクゼーションエリアなど館内施設も充実している。こだわりの大人の癒し空間で都会の喧噪を忘れ、やすらぎの時間を過ごすには最高の場所。", "住所2": "練馬区向山3丁目25-1"},
  {"今の気持ち": "わくわく昭和レトロ", "場所1": "喫茶タイムマシン", "画像1": "pic/kissa-timemachine.jpg", "解説1": "レトロ＆ポップな1980年代にロックオンできる、テーマパーク的喫茶店。", "住所1": "東京都練馬区栄町34-5", "場所2": "江古田湯", "画像2": "pic/ekoda-yu.jpg", "解説2": "昭和の時代にタイムスリップできる、昭和レトロな浴場。", "住所2": "東京都練馬区旭丘１丁目１７-３ 江古田マンション 1F"},
  {"今の気持ち": "まったりアート", "場所1": "ぐすたふ珈琲", "画像1": "pic/gusutafu-coffee.jpg", "解説1": "アートや演劇人も愛する香りと空間。元スナックの色香漂う空間で、香り深き至福の一杯。", "住所1": "東京都練馬区旭丘１丁目５６−１３ マンション軽井沢", "場所2": "そるとぴーなっつ", "画像2": "pic/saltpeanuts-bar.jpg", "解説2": "1980年にオープンした自転車持ち込み可のユニークなジャズバー。金曜日と土曜日は「そるとでジャズ・ライブ」と称して、個性豊かなメンバーによるジャズの生演奏を行っている。また、ジャムセッションや新人プレイヤーが集う変則バンド、注目のリーダーライブなど、レアなライブも多数企画、開催している。席数はカウンター8席・テーブル18席で、グランドピアノが設置され、本格的なサウンドが楽しめる。", "住所2": "東京都練馬区栄町４−３ グレーシー マンション B1F"},
  {"今の気持ち": "ファミリーわくわく", "場所1": "練馬展望レストラン", "画像1": "pic/nerimatenbo-restaurant.jpg", "解説1": "練馬区役所20Fにある展望レストラン。練馬区在住の方以外には多分あまり知られていない穴場的なレストランではないでしょうか。展望台には以前訪れたことがあり、レストランが気になっていました。落ち着いていながら気取らない雰囲気で店員さんも感じ良く、窓側の席から夜景も綺麗に見えて楽しく過ごせました。", "住所1": "東京都練馬区豊玉北６-１２-１練馬区役所内２０Ｆ", "場所2": "トキワ荘マンガミュージアム", "画像2": "pic/tokiwaso-museum.jpg", "解説2": "かつて豊島区椎名町（現南長崎）にあったトキワ荘は、手塚治虫をはじめとするマンガの巨匠たちが住み集い、若き青春の日々を過ごした伝説のアパート。１９８２年１２月に解体されたが、多くの皆様のお力添えにより、マンガミュージアムとして開館した。当時の世界にタイムスリップできる。", "住所2": "東京都豊島区南長崎3-9-22南長崎花咲公園内"},
  {"今の気持ち": "どきどきアクティブ", "場所1": "春日町バッティングセンター", "画像1": "pic/kasugacho-batingcenter.jpg", "解説1": "バッティング練習に！運動不足・ストレスの解消に！200円から楽しめるレジャー。", "住所1": "東京都練馬区春日町2丁目14-11", "場所2": "志村電機珈琲焙煎所", "画像2": "pic/shimuradenki-coffee-baisenjo.jpg", "解説2": "電機店と珈琲焙煎所のコラボ。豊島園駅から歩いて行ける宝箱のような街喫茶。", "住所2": "東京都練馬区春日町1-11-1"}
])

# 固定出発地
fixed_origin = "豊島園駅"
st.session_state.setdefault("fixed_origin", fixed_origin)

# アプリタイトル
st.title("練馬ワンダーランド")

# サイドバー設定
with st.sidebar:
    st.header("設定")

    # 気分選択
    selected_mood = st.selectbox("今の気分を選んでください", data["今の気持ち"].unique())

    # 移動手段選択
    transport_mode = st.radio("移動手段を選んでください", ["徒歩", "自転車", "タクシー"])
    mode_map = {"徒歩": "walking", "自転車": "bicycling", "タクシー": "driving"}
    selected_mode = mode_map[transport_mode]

    # 食事希望チェック
    food_preference = st.checkbox("食事の希望がありますか？")
    st.write(f"食事希望: {'あり' if food_preference else 'なし'}")

    # 検索ボタン
    search_button = st.button("ルートを検索")

    # 天気情報表示
    st.markdown("---")
    st.subheader("練馬の天気（3日分）")
    weather_json = get_weather(url)
    if weather_json:
        for forecast in weather_json['forecasts']:
            st.image(forecast['image']['url'], width=85)
            st.write(f"{forecast['dateLabel']}: {forecast['telop']}")

# スライドショー
if not search_button and not st.session_state.get("search_completed", False):
    image_placeholder = st.empty()
    images = ["pic/0.png", "pic/1.png", "pic/2.png"]
    for img in images:
        if os.path.exists(img):
            image_placeholder.image(img, use_container_width=True)
        else:
            st.warning(f"画像が見つかりません: {img}")
        time.sleep(1)
        if st.session_state.get("search_completed"):
            break
else:
    st.session_state["search_completed"] = True

# ルート検索
if search_button:
    st.session_state["search_completed"] = True
    selected_data = data[data["今の気持ち"] == selected_mood].iloc[0]
    st.session_state["selected_data"] = selected_data.to_dict()

# ルート検索
if search_button:
    st.session_state["search_completed"] = True
    selected_data = data[data["今の気持ち"] == selected_mood].iloc[0]
    st.session_state["selected_data"] = selected_data.to_dict()

    origin = fixed_origin
    destination1 = selected_data["住所1"]
    destination2 = selected_data["住所2"]

    directions_url1 = (
        f"https://maps.googleapis.com/maps/api/directions/json"
        f"?origin={origin}&destination={destination1}&mode={selected_mode}&key={API_KEY}"
    )
    directions_url2 = (
        f"https://maps.googleapis.com/maps/api/directions/json"
        f"?origin={destination1}&destination={destination2}&mode={selected_mode}&key={API_KEY}"
    )
    directions_url3 = (
        f"https://maps.googleapis.com/maps/api/directions/json"
        f"?origin={destination2}&destination={origin}&mode={selected_mode}&key={API_KEY}"
    )

    res1 = requests.get(directions_url1)
    res2 = requests.get(directions_url2)
    res3 = requests.get(directions_url3)

    if res1.status_code == 200 and res2.status_code == 200 and res3.status_code == 200:
        data1 = res1.json()
        data2 = res2.json()
        data3 = res3.json()

        if all("routes" in d and len(d["routes"]) > 0 for d in [data1, data2, data3]):
            route1 = data1["routes"][0]["overview_polyline"]["points"]
            route2 = data2["routes"][0]["overview_polyline"]["points"]
            route3 = data3["routes"][0]["overview_polyline"]["points"]

            # Decode polyline
            def decode_polyline(polyline_str):
                index, lat, lng, coordinates = 0, 0, 0, []
                while index < len(polyline_str):
                    b, shift, result = 0, 0, 0
                    while True:
                        b = ord(polyline_str[index]) - 63
                        index += 1
                        result |= (b & 0x1F) << shift
                        shift += 5
                        if b < 0x20:
                            break
                    dlat = ~(result >> 1) if result & 1 else (result >> 1)
                    lat += dlat
                    shift, result = 0, 0
                    while True:
                        b = ord(polyline_str[index]) - 63
                        index += 1
                        result |= (b & 0x1F) << shift
                        shift += 5
                        if b < 0x20:
                            break
                    dlng = ~(result >> 1) if result & 1 else (result >> 1)
                    lng += dlng
                    coordinates.append((lat / 1e5, lng / 1e5))
                return coordinates

            route_coords1 = decode_polyline(route1)
            route_coords2 = decode_polyline(route2)
            route_coords3 = decode_polyline(route3)

            # セッションステートにルート情報を保存
            st.session_state["route_coords1"] = route_coords1
            st.session_state["route_coords2"] = route_coords2
            st.session_state["route_coords3"] = route_coords3

            # 各ルートの所要時間を取得
            duration1 = data1["routes"][0]["legs"][0]["duration"]["text"]
            duration2 = data2["routes"][0]["legs"][0]["duration"]["text"]
            duration3 = data3["routes"][0]["legs"][0]["duration"]["text"]

            st.session_state["route_table"] = pd.DataFrame({
                "出発地": [fixed_origin, selected_data["場所1"], selected_data["場所2"]],
                "目的地": [selected_data["場所1"], selected_data["場所2"], fixed_origin],
                "所要時間": [duration1, duration2, duration3]
            })

            # 地図データ作成
            m = folium.Map(location=route_coords1[0], zoom_start=13)
            folium.PolyLine(route_coords1, color="blue", weight=5, opacity=0.7).add_to(m)
            folium.PolyLine(route_coords2, color="purple", weight=5, opacity=0.7).add_to(m)
            folium.PolyLine(route_coords3, color="red", weight=5, opacity=0.7).add_to(m)

            # マーカー追加
            folium.Marker(
                location=route_coords1[0], popup="出発地: " + origin, icon=folium.Icon(color="green")
            ).add_to(m)
            folium.Marker(
                location=route_coords1[-1], popup="目的地1: " + selected_data["場所1"], icon=folium.Icon(color="orange")
            ).add_to(m)
            folium.Marker(
                location=route_coords2[-1], popup="目的地2: " + selected_data["場所2"], icon=folium.Icon(color="red")
            ).add_to(m)
            folium.Marker(
                location=route_coords3[-1], popup="戻り: " + origin, icon=folium.Icon(color="blue")
            ).add_to(m)

            st.session_state["map"] = m

    else:
        st.error("ルート情報の取得に失敗しました。APIキーやリクエスト内容を確認してください。")


# 選択した場所とルートの表示
if "selected_data" in st.session_state:
    selected_data = st.session_state["selected_data"]

    # 場所1と場所2の表示
    for i in range(1, 3):
        st.write(f"#### {selected_data[f'場所{i}']}")
        col1, col2 = st.columns([1, 3])
        with col1:
            if os.path.exists(selected_data[f'画像{i}']):
                st.image(selected_data[f'画像{i}'], caption=selected_data[f'場所{i}'], width=150)
            else:
                st.warning(f"画像が見つかりません: {selected_data[f'画像{i}']}")
        with col2:
            st.write(selected_data[f'解説{i}'])

    # GPTコメント表示
    with st.spinner("コメントを生成中です..."):
        adventure_comment = generate_gpt_comment([
            {"場所": selected_data["場所1"], "解説": selected_data["解説1"]},
            {"場所": selected_data["場所2"], "解説": selected_data["解説2"]}
        ])
    st.write("### ネリーからの提案")
    st.write(adventure_comment)

# 地図とルート情報の表示
if "route_table" in st.session_state:
    st.write("### ルート情報")
    st.table(st.session_state["route_table"])

if "map" in st.session_state:
    st.write("### 地図")
    st_folium(st.session_state["map"], width=725)
