from elasticsearch import Elasticsearch
from geopy.geocoders import Nominatim
from datetime import *
import requests
import json
import pytz
import os

class ELK:
    def __init__(self):
        self.es = None
        self.INDEX_NAME = "RansomwareGroups".lower()
        self.KIBANA_URL = "http://kibana:5601"
        self.elasticsearch = "http://elasticsearch:9200"
        self.HEADERS = {"kbn-xsrf": "true", "Content-Type": "application/json"}
        self.panel_idx = 1

    def init_elk(self):
        self.es = Elasticsearch(self.elasticsearch)

    def geocoding(self, doc):
        geolocoder = Nominatim(user_agent = doc['country'], timeout=None)
        if doc['region']=="N/A":
            crd = {"lat": str(0.0), "lon": str(0.0)}   
        else: 
            geo = geolocoder.geocode(doc['region'])
            crd = {"lat": str(geo.latitude), "lon": str(geo.longitude)}
        doc['region'] = crd

        return doc

    def create_mapping(self):
        mapping = {
            "mappings": {
                "properties": {
                    "title": {"type": "keyword"}, 
                    "Description": {"type": "text"},
                    "site": {"type": "keyword"}, 
                    "address": {"type": "text"}, 
                    "country": {"type": "keyword"}, 
                    "region": {"type": "geo_point"},
                    "all data": {"type": "text"},
                    "tel": {"type": "keyword"}, 
                    "link": {"type": "keyword"},
                    "images": {"type": "text"},
                    "attacker": {"type": "keyword"},
                    "@timestamp": {"type": "date"}
                }
            }
        }
        if not self.check_index_pattern():
            self.es.indices.create(index=self.INDEX_NAME, body=mapping)
            print(f"Index '{self.INDEX_NAME}' created with mapping.")
        else:
            print(f"Index '{self.INDEX_NAME}' already exists.")

    def delete_all_documents(self):
        try:
            response = self.es.delete_by_query(
                index=self.INDEX_NAME,
                body={
                    "query": {
                        "match_all": {}  # 모든 문서에 일치
                    }
                }
            )
            print(f"Deleted documents in index '{self.INDEX_NAME}': {response['deleted']} documents")
        except Exception as e:
            print(f"Error deleting documents: {e}")


    def upload_data_view(self):
        docs = {}

        path = "./OUT/"
        file_list = os.listdir(path)
        file_list_json = [file for file in file_list if file.endswith(".json")]

        for json_file in file_list_json:
            tmp={}
            with open(path+json_file) as f:
                tmp.update(json.load(f))
            attacker = json_file[:json_file.find('_')]
            for key, value in tmp.items():
                value.update({"attacker":attacker})
            if "N/A" in tmp:
                tmp.pop("N/A")
            docs.update(tmp)

        for index, doc in docs.items():
            doc = self.geocoding(doc)
            utc_now = datetime.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            doc.update({"@timestamp": utc_now})

            self.es.index(index=self.INDEX_NAME, body=doc)


    def create_data_view(self):
        url = f"{self.KIBANA_URL}/api/data_views/data_view"
        payload = {
            "data_view": {
                "title": self.INDEX_NAME,
                "timeFieldName": "@timestamp"
            }
        }
        if self.check_data_view():
            self.delete_data_view()
        response = requests.post(url, headers=self.HEADERS, json=payload)
        if response.status_code == 200:
            print(f"Data View '{self.INDEX_NAME}' created successfully in Kibana.")
        else:
            print(f"Failed to create Data View: {response.status_code}, {response.text}")

    def get_index_pattern_id(self):
        url = f"{self.KIBANA_URL}/api/data_views"
        response = requests.get(url, headers=self.HEADERS)
        if response.status_code == 200:
            data_views = response.json()["data_view"]
            for view in data_views:
                if view["title"] == self.INDEX_NAME:
                    return view["id"]
        print(f"Data view '{self.INDEX_NAME}' not found.")
        return None

    def create_table_visualization(self,index_pattern_id):
        """
        선언 example
        create_table_visualization(get_index_pattern_id('blackbasta'), 'blackbasta')

        위 선언의 'blackbasta'부분은 INDEX_NAME으로 수정할 것

        """
        url = f"{self.KIBANA_URL}/api/saved_objects/visualization"
        payload = {
            "attributes": {
                "title": self.INDEX_NAME,
                "visState": json.dumps({
                    "title": self.INDEX_NAME,
                    "type": "table",
                    "params": {
                        "perPage": 10,  # 테이블 당 표시할 페이지 크기
                        "showMetricsAtAllLevels": False,
                        "showPartialRows": False,
                        "showTotal": False
                    },
                    "aggs": [
                        # title 필드의 상위 값 표시
                        {
                            "id": "1",
                            "enabled": True,
                            "type": "terms",
                            "schema": "bucket",
                            "params": {
                                "field": "attacker",
                                "size": 5,  # 상위 5개의 값만 표시
                                "order": {"type": "alphabetical", "direction": "desc"}  # 내림차순 정렬
                            }
                        },
                        {
                            "id": "2",
                            "enabled": True,
                            "type": "terms",
                            "schema": "bucket",
                            "params": {
                                "field": "title",
                                "size": 5,  # 상위 5개의 값만 표시
                                "order": {"type": "alphabetical", "direction": "desc"}  # 내림차순 정렬
                            }
                        },
                        # country 필드의 상위 값 표시
                        {
                            "id": "3",
                            "enabled": True,
                            "type": "terms",
                            "schema": "bucket",
                            "params": {
                                "field": "country",
                                "size": 5,
                                "order": {"type": "alphabetical", "direction": "desc"}
                            }
                        },
                        # site 필드의 상위 값 표시
                        {
                            "id": "4",
                            "enabled": True,
                            "type": "terms",
                            "schema": "bucket",
                            "params": {
                                "field": "site",
                                "size": 5,
                                "order": {"type": "alphabetical", "direction": "desc"}
                            }
                        },
                        # link 필드의 상위 값 표시
                        {
                            "id": "5",
                            "enabled": True,
                            "type": "terms",
                            "schema": "bucket",
                            "params": {
                                "field": "link",
                                "size": 5,
                                "order": {"type": "alphabetical", "direction": "desc"}
                            }
                        }
                    ]
                }),
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": json.dumps({
                        "index": index_pattern_id,  # 데이터를 가져올 인덱스 패턴 ID
                        "query": {"language": "kuery", "query": ""},  # 기본 쿼리
                        "filter": []  # 필터를 지정하지 않음
                    })
                }
            }
        }
        if self.check_visualization():
            self.delete_visualization()
        response = requests.post(url, headers=self.HEADERS, json=payload)
        if response.status_code == 200:
            visualization_id = response.json()["id"]
            print(f"Table visualization '{self.INDEX_NAME}' created successfully with ID: {visualization_id}")
            return visualization_id, 'visualization'
        else:
            print(f"Failed to create Table visualization: {response.status_code}, {response.text}")
            return None, None


    def create_map_with_es_layer(self,data_view_id, geo_field='region'):
        # Saved Objects API URL
        url = f"{self.KIBANA_URL}/api/saved_objects/map"

        # 맵 생성 및 레이어 추가를 위한 payload
        payload = {
            "attributes": {
                "title": self.INDEX_NAME,  # 맵 이름
                "description": "Map created using Python automation",
                "mapStateJSON": json.dumps({
                    "zoom": 2,  # 초기 맵 줌 레벨
                    "center": {"lon": 0, "lat": 0},  # 초기 중심 좌표
                    "timeFilters": {"from": "now-1h", "to": "now"},  # 기본 시간 필터
                    "query": {"query": "", "language": "kuery"},  # 쿼리
                    "filters": []  # 기본 필터 없음
                }),
                "layerListJSON": json.dumps([
                    {
                        "id": "basemap_layer",
                        "type": "EMS_VECTOR_TILE",
                        "sourceDescriptor": {
                            "type":"EMS_TMS",
                            "isAutoSelect":True,
                            "lightModeDefault":"road_map_desaturated"
                        },
                        "visible": True,
                        "label":"Basemap",
                        "minZoom":0,
                        "maxZoom":24,
                        "alpha":1,
                        "includeInFitToBounds":True,
                        "locale":"autoselect",
                        "style": {
                            "type": "EMS_VECTOR_TILE",
                            "color":""
                        }
                    },
                    {
                        "id": "layer_1",  # 레이어 ID
                        "type": "MVT_VECTOR",  # 벡터 레이어
                        "sourceDescriptor": {
                            "type": "ES_SEARCH",  # Elasticsearch 문서 기반 레이어
                            "indexPatternId": data_view_id,  # Data View ID
                            "geoField": geo_field,  # 지리적 필드 이름
                            "scalingType": "limit",  # 데이터 스케일링 타입
                            "sortField":"attacker",
                            "sortOrder":"desc",
                            "applyGlobalQuery": True  # 글로벌 쿼리 적용 여부
                        },
                        "style": {
                            "type": "STATIC",  # 벡터 스타일
                            "properties": {
                                "fillColor": {"type": "DYNAMIC", "options": {"field":{"name":"attacker","origin":"source"},"type":"CATEGORICAL","useCustomColorPalette":False,"colorCategory":"palette_0"}},  # 채우기 색상
                                "lineColor": {"type": "STATIC", "options": {"color": "#000000"}},  # 테두리 색상
                                "iconSize": {"type": "STATIC", "options": {"size": 6}},  # 아이콘 크기
                                "icon": {"type": "STATIC", "options": {"value": "marker"}},  # 아이콘 모양
                                "labelText":{"type":"STATIC", "options":{"value":"{attacker}"}},
                                "labelColor":{"type":"DYNAMIC","options":{"field":{"name":"attacker","origin":"source"},"type":"CATEGORICAL","useCustomColorPalette":False,"colorCategory":"palette_0"}},
                                "labelSize":{"type":"STATIC","options":{"size":12}}
                            }
                        }
                    }
                ])
            }
        }

        # API 호출
        if self.check_map():
            self.delete_map()
        response = requests.post(url, headers=self.HEADERS, json=payload)

        # 응답 처리
        if response.status_code == 200:
            print("Map created successfully")
            map_id = response.json()["id"]
            return map_id, 'map'
        else:
            print(f"Failed to create map: {response.status_code}, {response.text}")
            return None, None

    def create_dashboard(self):
        url = f"{self.KIBANA_URL}/api/saved_objects/dashboard/"
        payload = {
            "attributes": {
                "title": self.INDEX_NAME,
                "description": "Auto-generated dashboard",
            }
        }
        if self.check_dashboard():
            self.delete_dashboard()
        response = requests.post(url, headers=self.HEADERS, json=payload)
        if response.status_code == 200:
            dashboard_id = response.json().get("id")
            print(f"Dashboard '{self.INDEX_NAME}' created with ID: {dashboard_id}")
            return dashboard_id
        else:
            print(f"Failed to create dashboard: {response.status_code}, {response.text}")
            return None

    def get_dashboard_id(self):
        url = f"{self.KIBANA_URL}/api/saved_objects/_find?type=dashboard&search_fields=title&search={self.INDEX_NAME}"
        response = requests.get(url, headers=self.HEADERS)
        if response.status_code == 200:
            results = response.json().get("saved_objects", [])
            if results:
                dashboard_id = results[0].get("id")
                print(f"Dashboard '{self.INDEX_NAME}' found with ID: {dashboard_id}")
                return dashboard_id
            else:
                print(f"Dashboard '{self.INDEX_NAME}' not found.")
                return None
        else:
            print(f"Failed to search for dashboard: {response.status_code}, {response.text}")
            return None
    
    def add_visualization_to_dashboard(self,dashboard_id, id):
        # API Endpoint for updating the dashboard
        panel_index=str(self.panel_idx)
        url = f"{self.KIBANA_URL}/api/saved_objects/dashboard/{dashboard_id}"

        # Load the current Dashboard's saved object
        response = requests.get(url, headers=self.HEADERS)
        if response.status_code != 200:
            print(f"Failed to fetch dashboard: {response.status_code}, {response.text}")
            return

        dashboard = response.json()
        # Update the 'panelsJSON' to add the new visualization
        existing_panels = json.loads(dashboard["attributes"].get("panelsJSON", "[]"))
        new_panel = {
            "panelIndex": panel_index,
            "gridData": {
                "x": 24,  # 위치: 대시보드의 x축 (수동으로 조정 가능)
                "y": len(existing_panels) * 15,  # 위치: y축, 기존 패널 아래에 추가
                "w": 24,  # 너비
                "h": 15,  # 높이
                "i": panel_index  # ID (중복되지 않도록 설정)
            },
            "version": "8.15.1",  # Kibana 버전
            "type": "visualization",
            "id": id  # 추가할 시각화 ID
        }

        # Append the new panel to the list of existing panels
        existing_panels.append(new_panel)
        #print(existing_panels)
        #Update the dashboard payload
        updated_dashboard = {
            "attributes": {
                **dashboard["attributes"],
                "panelsJSON": json.dumps(existing_panels),
                "timeRestore": False,
                "kibanaSavedObjectMeta":
                    {
                        "searchSourceJSON": json.dumps(
                            {"query": {"query": "", "language": "lucene"}, "filter": [], "highlightAll": True,
                             "version": True})
                    },
                "optionsJSON": json.dumps({"darkTheme": False, "useMargins": True, "hidePanelTitles": False}),
            },
        }
        data = json.dumps(updated_dashboard)
        # API Call to update the dashboard
        response = requests.post(url+"?overwrite=true", headers=self.HEADERS, data=data)
        if response.status_code == 200:
            print(f"Visualization '{id}' added to Dashboard '{dashboard_id}'.")
        else:
            print(f"Failed to update dashboard: {response.status_code}, {response.text}")

        self.panel_idx+=1

    def add_map_to_dashboard(self,dashboard_id, id):
        panel_index=str(self.panel_idx)
        # API Endpoint for updating the dashboard
        url = f"{self.KIBANA_URL}/api/saved_objects/dashboard/{dashboard_id}"

        # Load the current Dashboard's saved object
        response = requests.get(url, headers=self.HEADERS)
        if response.status_code != 200:
            print(f"Failed to fetch dashboard: {response.status_code}, {response.text}")
            return

        dashboard = response.json()
        # Update the 'panelsJSON' to add the new visualization
        existing_panels = json.loads(dashboard["attributes"].get("panelsJSON", "[]"))
        new_panel = {
            "panelIndex": panel_index,
            "gridData": {
                "x": 0,  # 위치: 대시보드의 x축 (수동으로 조정 가능)
                "y": len(existing_panels) * 15,  # 위치: y축, 기존 패널 아래에 추가
                "w": 24,  # 너비
                "h": 15,  # 높이
                "i": panel_index  # ID (중복되지 않도록 설정)
            },
            "version": "8.15.1",  # Kibana 버전
            "type": "map",
            "id": id  # 추가할 시각화 ID
        }

        # Append the new panel to the list of existing panels
        existing_panels.append(new_panel)
        #print(existing_panels)
        #Update the dashboard payload
        updated_dashboard = {
            "attributes": {
                **dashboard["attributes"],
                "panelsJSON": json.dumps(existing_panels),
                "timeRestore": False,
                "kibanaSavedObjectMeta":
                    {
                        "searchSourceJSON": json.dumps(
                            {"query": {"query": "", "language": "lucene"}, "filter": [], "highlightAll": True,
                             "version": True})
                    },
                "optionsJSON": json.dumps({"darkTheme": False, "useMargins": True, "hidePanelTitles": False}),
            },
        }
        data = json.dumps(updated_dashboard)
        # API Call to update the dashboard
        response = requests.post(url+"?overwrite=true", headers=self.HEADERS, data=data)
        if response.status_code == 200:
            print(f"Visualization '{id}' added to Dashboard '{dashboard_id}'.")
        else:
            print(f"Failed to update dashboard: {response.status_code}, {response.text}")

        self.panel_idx+=1

    def check_index_pattern(self):
        response = self.es.indices.exists(index=self.INDEX_NAME)
        return response

    def delete_index_pattern(self):
        response = self.es.indices.delete(index=self.INDEX_NAME)
        print(response)

    def check_data_view(self):
        search_url = f"{self.KIBANA_URL}/api/saved_objects/_find?type=index-pattern&search_fields=title&search={self.INDEX_NAME}" 
        response = requests.get(search_url, headers=self.HEADERS) 
        return response.json()['total']>0

    def delete_data_view(self): 
        """ Kibana에서 주어진 이름의 데이터 뷰를 삭제하는 함수 :param data_view_name: 삭제할 데이터 뷰의 이름 """ 
        # 데이터 뷰 ID 검색 
        search_url = f"{self.KIBANA_URL}/api/saved_objects/_find?type=index-pattern&search_fields=title&search={self.INDEX_NAME}" 
        response = requests.get(search_url, headers=self.HEADERS) 
        if response.status_code == 200: 
            result = response.json() 
            if result['total'] > 0: 
                data_view_id = result['saved_objects'][0]['id'] 
                # 데이터 뷰 삭제 
                delete_url = f"{self.KIBANA_URL}/api/saved_objects/index-pattern/{data_view_id}" 
                delete_response = requests.delete(delete_url, headers=self.HEADERS) 
                if delete_response.status_code == 200: 
                    print(f"Data view '{self.INDEX_NAME}' has been successfully deleted.") 
                else: 
                    print(f"Failed to delete data view '{self.INDEX_NAME}': {delete_response.status_code}, {delete_response.text}") 
            else: 
                print(f"Data view '{self.INDEX_NAME}' not found.") 
        else: 
            print(f"Failed to search for data view '{self.INDEX_NAME}': {response.status_code}, {response.text}")

    def check_map(self):
        url = f"{self.KIBANA_URL}/api/saved_objects/_find?type=map&search_fields=title&search={self.INDEX_NAME}"
        response = requests.get(url, headers=self.HEADERS)
        return response.json()['total']>0

    def delete_map(self):
        url = f"{self.KIBANA_URL}/api/saved_objects/_find?type=map&search_fields=title&search={self.INDEX_NAME}"
        response = requests.get(url, headers=self.HEADERS)
        if response.status_code == 200:
            visualizations = response.json().get("saved_objects", [])
            for viz in visualizations:
                if viz["attributes"]["title"] == self.INDEX_NAME:
                    viz_id = viz["id"]
                    delete_url = f"{self.KIBANA_URL}/api/saved_objects/map/{viz_id}"
                    delete_response = requests.delete(delete_url, headers=self.HEADERS)
                    if delete_response.status_code == 200:
                        print(f"map '{self.INDEX_NAME}' deleted successfully.")
                    else:
                        print(f"Failed to delete map '{self.INDEX_NAME}': {delete_response.status_code}, {delete_response.text}")
        else:
            print(f"Failed to fetch Visualizations: {response.status_code}, {response.text}")

    def check_visualization(self):
        url = f"{self.KIBANA_URL}/api/saved_objects/_find?type=visualization&search_fields=title&search={self.INDEX_NAME}"
        response = requests.get(url, headers=self.HEADERS)
        return response.json()['total']>0

    def delete_visualization(self):
        url = f"{self.KIBANA_URL}/api/saved_objects/_find?type=visualization&search_fields=title&search={self.INDEX_NAME}"
        response = requests.get(url, headers=self.HEADERS)
        if response.status_code == 200:
            visualizations = response.json().get("saved_objects", [])
            for viz in visualizations:
                if viz["attributes"]["title"] == self.INDEX_NAME:
                    viz_id = viz["id"]
                    delete_url = f"{self.KIBANA_URL}/api/saved_objects/visualization/{viz_id}"
                    delete_response = requests.delete(delete_url, headers=self.HEADERS)
                    if delete_response.status_code == 200:
                        print(f"Visualization '{self.INDEX_NAME}' deleted successfully.")
                    else:
                        print(f"Failed to delete Visualization '{self.INDEX_NAME}': {delete_response.status_code}, {delete_response.text}")
        else:
            print(f"Failed to fetch Visualizations: {response.status_code}, {response.text}")

    def check_dashboard(self):
        url = f"{self.KIBANA_URL}/api/saved_objects/_find?type=dashboard&search_fields=title&search={self.INDEX_NAME}"
        response = requests.get(url, headers=self.HEADERS)
        return response.json()['total']>0

    def delete_dashboard(self):
        url = f"{self.KIBANA_URL}/api/saved_objects/_find?type=dashboard&search_fields=title&search={self.INDEX_NAME}"
        response = requests.get(url, headers=self.HEADERS)
        if response.status_code == 200:
            dashboards = response.json().get("saved_objects", [])
            for dashboard in dashboards:
                if dashboard["attributes"]["title"] == self.INDEX_NAME:
                    dashboard_id = dashboard["id"]
                    delete_url = f"{self.KIBANA_URL}/api/saved_objects/dashboard/{dashboard_id}"
                    delete_response = requests.delete(delete_url, headers=self.HEADERS)
                    if delete_response.status_code == 200:
                        print(f"Dashboard '{self.INDEX_NAME}' deleted successfully.")
                    else:
                        print(f"Failed to delete Dashboard '{self.INDEX_NAME}': {delete_response.status_code}, {delete_response.text}")
        else:
            print(f"Failed to fetch Dashboards: {response.status_code}, {response.text}")

    def process(self):
        self.init_elk()
        self.delete_all_documents()
        self.create_mapping()
        self.upload_data_view()
        self.create_data_view()
        vis_id = self.create_table_visualization(self.get_index_pattern_id())
        map_id = self.create_map_with_es_layer(self.get_index_pattern_id())

        board_id = self.get_dashboard_id()
        self.create_dashboard()
        board_id = self.get_dashboard_id()

        ids = [vis_id,map_id]
        for id, type in ids:
            if type=='visualization':
                self.add_visualization_to_dashboard(board_id,id)
            elif type=='map':
                self.add_map_to_dashboard(board_id,id)
#