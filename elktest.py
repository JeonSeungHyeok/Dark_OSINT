import requests

addresses = [
    "5 The Cres, Cheadle And Gatley Ward, Cheshire, SK8 1PS, United Kingdom",
    "1120 Avenue of the Americas Fl 4, New York City, New York, 10036, United States",
    "7 Deansgate Lancaster Buildings Fl 3, Manchester, Lancashire, M3 2BW, United Kingdom"
]

url = "https://nominatim.openstreetmap.org/search"
headers = {
    "User-Agent": "MyAppName/1.0 (contact: your_email@example.com)"
}

for address in addresses:
    parts = [p.strip() for p in address.split(',')]

    # 뒤에서 2번째, 3번째 값 추출
    if len(parts) < 3:
        print(f"주소가 너무 짧습니다: {address}")
        continue

    second_last = parts[-2]  # 검색어로 사용할 값
    third_last = parts[-3]   # 결과 필터링 조건

    params = {
        "format": "json",
        "q": second_last
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if not data:
            print(f"해당 주소로 검색된 결과가 없습니다. ({address})")
        else:
            # 검색 결과가 하나만 있는 경우 -> 필터링 없이 바로 출력
            if len(data) == 1:
                lat = data[0].get("lat", "N/A")
                lon = data[0].get("lon", "N/A")
                print(f"주소: {address}")
                print(f"위도, 경도: {lat}, {lon}")
                print("-" * 40)
            else:
                # 결과가 여러 개일 경우 third_last를 display_name에 포함하는 결과만 필터링
                filtered_results = [res for res in data if third_last in res.get("display_name", "")]

                if not filtered_results:
                    print(f"'{third_last}'를 포함하는 결과가 없습니다. ({address})")
                else:
                    for result in filtered_results:
                        lat = result.get("lat", "N/A")
                        lon = result.get("lon", "N/A")
                        print(f"주소: {address}")
                        print(f"위도, 경도: {lat}, {lon}")
                        print("-" * 40)
    else:
        print(f"요청 실패: {response.status_code}, {response.text} (주소: {address})")
