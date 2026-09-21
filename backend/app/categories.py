# backend/app/categories.py

# 系統預設類別樹 (前端渲染選單用)
CATEGORY_TREE = [
    {"id": 0, "name": "機動車輛", "type": "bbox", "children": ["汽車", "公車", "卡車"]},
    {"id": 1, "name": "兩輪車輛", "type": "bbox", "children": ["機車", "腳踏車"]},
    {"id": 2, "name": "行人", "type": "bbox", "children": []},
    {"id": 3, "name": "交通號誌與標誌", "type": "bbox", "children": []},
    {"id": 4, "name": "車道線", "type": "polygon", "children": []},
    {"id": 5, "name": "路面標記", "type": "polygon", "children": ["斑馬線", "路面箭頭"]},
]

# YOLO 格式轉換對照表 (將大類別名稱映射到 class_id)
CATEGORY_NAME_TO_ID = {
    "機動車輛": 0,
    "兩輪車輛": 1,
    "行人": 2,
    "交通號誌與標誌": 3,
    "車道線": 4,
    "路面標記": 5
}

def get_category_tree():
    return CATEGORY_TREE