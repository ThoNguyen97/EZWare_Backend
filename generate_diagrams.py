"""
Sinh 6 hình minh hoạ cho báo cáo đồ án EZWare:
  hinh1_er_diagram.png        - Sơ đồ ER 6 bảng
  hinh2_function_diagram.png  - Sơ đồ chức năng tổng quan
  hinh3_class_diagram.png     - Sơ đồ lớp UML
  hinh4_postman_login.png     - Mock Postman UI: login API
  hinh5_postman_receipt.png   - Mock Postman UI: luồng tạo + duyệt phiếu
  hinh6_swagger_ui.png        - Mock Swagger UI list endpoints

Chạy:
    python generate_diagrams.py
"""
from __future__ import annotations
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D


OUT_DIR = 'report_images'
os.makedirs(OUT_DIR, exist_ok=True)


# Mặc định dùng font hỗ trợ tiếng Việt — Times New Roman có sẵn trên Win
plt.rcParams['font.family'] = ['Times New Roman', 'DejaVu Sans']
plt.rcParams['font.size'] = 10


# ============================================================
# Hình 1 — ER diagram
# ============================================================
def draw_er_diagram():
    """Layout: 2 hàng — master (top) + transactional (bottom). FK arrows vertical, không chéo."""
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Layout: 3 master tables ở hàng trên, 3 transaction tables ở hàng dưới
    # users    products       warehouses
    #            ▲     ▲          ▲      ▲
    #            |     |          |      |
    #          (PROTECT) (CASCADE) (PROTECT)
    #            |     |          |      |
    #          receipt_details   inventory_receipts    inventory

    tables = [
        # Top row — master tables
        (0.5, 5.0, 3.5, 4.4, 'users', [
            'PK  user_id',
            'username (UNIQUE)',
            'password (PBKDF2 hash)',
            'full_name',
            'email',
            'phone',
            'user_role: admin/staff',
            'is_active',
            'is_staff (auto-sync)',
            'last_login',
        ]),
        (6.0, 6.4, 3.8, 3.0, 'products', [
            'PK  product_id',
            'product_code (UNIQUE)',
            'product_name',
            'product_type',
            'product_description',
            'is_active',
        ]),
        (11.8, 6.7, 3.8, 2.7, 'warehouses', [
            'PK  warehouse_id',
            'warehouse_name (UNIQUE)',
            'warehouse_location',
            'is_active',
        ]),
        # Bottom row — transaction tables
        (0.5, 0.4, 4.2, 3.4, 'inventory_receipts', [
            'PK  receipt_id',
            'FK  warehouse_id  →  warehouses',
            '       (on_delete=PROTECT)',
            'receipt_type: IMPORT / EXPORT',
            'receipt_status:',
            '    PENDING / APPROVED / CANCELLED',
            'created_at',
        ]),
        (5.5, 0.7, 4.8, 3.1, 'receipt_details', [
            'PK  detail_id',
            'FK  receipt_id  →  inventory_receipts',
            '       (on_delete=CASCADE)',
            'FK  product_id  →  products',
            '       (on_delete=PROTECT)',
            'quantity (>= 1)',
        ]),
        (11.0, 0.7, 4.8, 3.1, 'inventory', [
            'PK  id',
            'FK  warehouse_id  →  warehouses',
            'FK  product_id  →  products',
            'quantity',
            'UNIQUE(warehouse_id, product_id)',
        ]),
    ]

    color_header = '#3F72AF'
    color_body = '#DBE2EF'

    def draw_table(x, y, w, h, name, fields):
        head_h = 0.5
        ax.add_patch(FancyBboxPatch((x, y + h - head_h), w, head_h,
                                     boxstyle='round,pad=0.02', linewidth=1.2,
                                     edgecolor='black', facecolor=color_header))
        ax.text(x + w / 2, y + h - head_h / 2, name,
                ha='center', va='center', color='white',
                fontsize=13, fontweight='bold')
        ax.add_patch(Rectangle((x, y), w, h - head_h, linewidth=1.2,
                                edgecolor='black', facecolor=color_body))
        line_y = y + h - head_h - 0.35
        for f in fields:
            ax.text(x + 0.15, line_y, f, ha='left', va='center', fontsize=10)
            line_y -= 0.34

    for t in tables:
        draw_table(*t)

    # FK arrows — VERTICAL (không chéo), từ transaction (bottom) lên master (top)
    def fk_arrow(x1, y1, x2, y2, label='', label_offset=(0, 0.18)):
        arr = FancyArrowPatch((x1, y1), (x2, y2),
                              arrowstyle='-|>', mutation_scale=20,
                              linewidth=1.6, color='#112D4E',
                              connectionstyle='arc3,rad=0.0')
        ax.add_patch(arr)
        if label:
            mx = (x1 + x2) / 2 + label_offset[0]
            my = (y1 + y2) / 2 + label_offset[1]
            ax.text(mx, my, label, ha='center', fontsize=9, fontweight='bold',
                    color='#112D4E',
                    bbox=dict(facecolor='white', edgecolor='#3F72AF',
                              boxstyle='round,pad=0.2'))

    # receipt_details.product_id (5.5, 3.8) → products (bottom of products box)
    fk_arrow(7.0, 3.8, 7.0, 6.4, 'product_id\nPROTECT')
    # receipt_details.receipt_id (5.5, 3.8) → inventory_receipts (right side)
    fk_arrow(5.5, 2.3, 4.7, 2.3, 'receipt_id\nCASCADE',
             label_offset=(0, 0.4))
    # inventory_receipts.warehouse_id → warehouses
    fk_arrow(3.5, 3.8, 12.5, 6.7, 'warehouse_id\nPROTECT',
             label_offset=(0, -0.3))
    # inventory.product_id → products
    fk_arrow(12.5, 3.8, 8.5, 6.4, 'product_id', label_offset=(0.5, 0.2))
    # inventory.warehouse_id → warehouses
    fk_arrow(14.0, 3.8, 14.0, 6.7, 'warehouse_id')

    ax.set_title('Hình 1. Sơ đồ ER — Cơ sở dữ liệu EZWare (6 bảng, 5 ràng buộc FK)',
                 fontsize=14, fontweight='bold', pad=15)

    plt.tight_layout()
    out = os.path.join(OUT_DIR, 'hinh1_er_diagram.png')
    plt.savefig(out, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()
    return out


# ============================================================
# Hình 2 — Sơ đồ chức năng
# ============================================================
def draw_function_diagram():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # 2 actors bên trái
    def draw_actor(x, y, label):
        # đầu
        ax.add_patch(patches.Circle((x, y + 0.45), 0.25, facecolor='#F9F7F7',
                                     edgecolor='black', linewidth=1.5))
        # thân
        ax.plot([x, x], [y + 0.2, y - 0.3], 'k-', linewidth=1.5)
        # tay
        ax.plot([x - 0.35, x + 0.35], [y, y], 'k-', linewidth=1.5)
        # chân
        ax.plot([x, x - 0.25], [y - 0.3, y - 0.7], 'k-', linewidth=1.5)
        ax.plot([x, x + 0.25], [y - 0.3, y - 0.7], 'k-', linewidth=1.5)
        ax.text(x, y - 1.1, label, ha='center', fontsize=11, fontweight='bold')

    draw_actor(1.5, 6.0, 'Admin')
    draw_actor(1.5, 2.5, 'Staff')

    # Hệ thống EZWare — khung lớn
    ax.add_patch(FancyBboxPatch((4, 0.5), 9.5, 7.0,
                                 boxstyle='round,pad=0.1',
                                 linewidth=2, edgecolor='#112D4E',
                                 facecolor='#F9F7F7', linestyle='--'))
    ax.text(8.75, 7.2, 'HỆ THỐNG QUẢN LÝ KHO EZWARE',
            ha='center', fontsize=12, fontweight='bold', color='#112D4E')

    # 4 nhóm chức năng — boxes
    groups = [
        (4.5, 5.0, 4.0, 1.6, '1. Xác thực\n& Tài khoản',
         '4 endpoint\nregister, login,\nlogout, me', '#3F72AF'),
        (9.0, 5.0, 4.0, 1.6, '2. Quản lý Danh mục',
         '5 endpoint\nCRUD products,\nCRUD warehouses', '#3F72AF'),
        (4.5, 2.5, 4.0, 1.6, '3. Vận hành Kho',
         '4 endpoint\ntạo phiếu,\nthêm chi tiết,\nduyệt/hủy', '#DC5F00'),
        (9.0, 2.5, 4.0, 1.6, '4. Báo cáo',
         '2 endpoint\nxem tồn kho,\ncảnh báo tồn thấp', '#3F72AF'),
    ]
    for x, y, w, h, title, desc, color in groups:
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                     boxstyle='round,pad=0.05',
                                     linewidth=1.5, edgecolor=color,
                                     facecolor='#DBE2EF'))
        ax.text(x + w / 2, y + h - 0.3, title,
                ha='center', va='top', fontsize=11, fontweight='bold', color=color)
        ax.text(x + w / 2, y + 0.5, desc,
                ha='center', va='center', fontsize=9)

    # Actor arrows
    ax.annotate('', xy=(4.4, 6.0), xytext=(2.2, 6.0),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))
    ax.annotate('', xy=(4.4, 2.5), xytext=(2.2, 2.5),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))

    # Tổng quan
    ax.text(8.75, 1.5, '14 endpoint REST | Token Authentication | Swagger UI tự sinh',
            ha='center', fontsize=10, style='italic', color='#3F72AF')

    ax.set_title('Sơ đồ chức năng tổng quan — Hệ thống EZWare',
                 fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    out = os.path.join(OUT_DIR, 'hinh2_function_diagram.png')
    plt.savefig(out, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()
    return out


# ============================================================
# Hình 3 — Class diagram UML
# ============================================================
def draw_class_diagram():
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10)
    ax.axis('off')

    def draw_class(x, y, w, name, attrs, methods=None):
        n_attr = len(attrs)
        n_method = len(methods or [])
        head_h = 0.5
        attr_h = 0.3 * n_attr + 0.2
        method_h = 0.3 * n_method + 0.2 if methods else 0
        total_h = head_h + attr_h + method_h

        # Header
        ax.add_patch(Rectangle((x, y + total_h - head_h), w, head_h,
                                facecolor='#3F72AF', edgecolor='black', linewidth=1.5))
        ax.text(x + w / 2, y + total_h - head_h / 2, name,
                ha='center', va='center', color='white',
                fontsize=11, fontweight='bold')
        # Attributes
        ax.add_patch(Rectangle((x, y + method_h), w, attr_h,
                                facecolor='#F9F7F7', edgecolor='black', linewidth=1.5))
        for i, a in enumerate(attrs):
            ax.text(x + 0.1, y + method_h + attr_h - 0.25 - i * 0.3,
                    a, ha='left', va='center', fontsize=9)
        # Methods (optional)
        if methods:
            ax.add_patch(Rectangle((x, y), w, method_h,
                                    facecolor='#DBE2EF', edgecolor='black', linewidth=1.5))
            for i, m in enumerate(methods):
                ax.text(x + 0.1, y + method_h - 0.25 - i * 0.3,
                        m, ha='left', va='center', fontsize=9, style='italic')
        return (x, y, w, total_h)

    # 6 model classes
    user_box = draw_class(0.5, 7.0, 3.5, 'User',
        ['- user_id: AutoField',
         '- username: str (UNIQUE)',
         '- password: str (hashed)',
         '- full_name: str',
         '- user_role: str',
         '- is_active: bool'],
        ['+ la_admin(): bool',
         '+ save() syncs is_staff'])

    prod_box = draw_class(5.5, 7.5, 3.5, 'Product',
        ['- product_id: AutoField',
         '- product_code: str (UNIQUE)',
         '- product_name: str',
         '- product_type: str',
         '- is_active: bool'])

    wh_box = draw_class(11.0, 7.5, 3.5, 'Warehouse',
        ['- warehouse_id: AutoField',
         '- warehouse_name: str',
         '- warehouse_location: str',
         '- is_active: bool'])

    rec_box = draw_class(0.5, 2.0, 4.0, 'InventoryReceipt',
        ['- receipt_id: AutoField',
         '- warehouse: FK -> Warehouse',
         '- receipt_type: IMPORT/EXPORT',
         '- receipt_status: PENDING/...',
         '- created_at: DateTime'])

    det_box = draw_class(5.5, 2.0, 4.0, 'ReceiptDetail',
        ['- detail_id: AutoField',
         '- receipt: FK -> Receipt',
         '- product: FK -> Product',
         '- quantity: int (>=1)'])

    inv_box = draw_class(10.5, 2.0, 4.0, 'Inventory',
        ['- id: AutoField',
         '- warehouse: FK -> Warehouse',
         '- product: FK -> Product',
         '- quantity: int',
         'UNIQUE(warehouse, product)'])

    # Quan hệ (đường + label)
    def relation(x1, y1, x2, y2, label, style='-|>'):
        arr = FancyArrowPatch((x1, y1), (x2, y2),
                              arrowstyle=style, mutation_scale=15,
                              linewidth=1.4, color='#112D4E')
        ax.add_patch(arr)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.1, label,
                ha='center', fontsize=8,
                bbox=dict(facecolor='white', edgecolor='none', pad=1.5))

    relation(2.5, 4.4, 12.5, 7.5, '1 — *  (PROTECT)')   # Receipt → Warehouse
    relation(7.5, 4.4, 4.5, 4.4, '* — 1  (CASCADE)')    # Detail → Receipt
    relation(7.5, 5.5, 7.0, 7.5, '* — 1  (PROTECT)')    # Detail → Product
    relation(12.5, 5.5, 12.5, 7.5, '* — 1')             # Inventory → Warehouse
    relation(10.5, 3.3, 9.0, 7.5, '* — 1')              # Inventory → Product

    ax.set_title('Sơ đồ lớp UML — Các Model của EZWare',
                 fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    out = os.path.join(OUT_DIR, 'hinh3_class_diagram.png')
    plt.savefig(out, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()
    return out


# ============================================================
# Hình 4 — Mock Postman login
# ============================================================
def draw_postman_login():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_facecolor('#F4F4F4')

    # Top bar — tab + URL
    ax.add_patch(Rectangle((0.2, 7.8), 13.6, 0.8, facecolor='#FFFFFF',
                            edgecolor='#D0D0D0', linewidth=1))
    ax.text(0.5, 8.2, 'POST', fontsize=11, fontweight='bold', color='#FF7F0E',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFE4C7',
                      edgecolor='#FF7F0E', linewidth=1))
    ax.text(1.5, 8.2, 'https://ezware-backend.onrender.com/api/auth/login',
            fontsize=11, va='center', family='Consolas')
    ax.text(12.5, 8.2, 'Send',
            fontsize=11, color='white', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FF7F0E'))

    # Body section
    ax.text(0.3, 7.4, 'Body  ▸  raw  ▸  JSON',
            fontsize=10, fontweight='bold', color='#666')
    ax.add_patch(Rectangle((0.2, 4.5), 13.6, 2.7, facecolor='#FFFFFF',
                            edgecolor='#D0D0D0', linewidth=1))
    body_json = (
        '{\n'
        '    "username": "admin01",\n'
        '    "password": "123456"\n'
        '}'
    )
    ax.text(0.5, 6.9, body_json, fontsize=11, va='top', family='Consolas')

    # Response — status
    ax.text(0.3, 4.2, 'Response', fontsize=10, fontweight='bold', color='#666')
    ax.text(0.5, 3.85, '200 OK', fontsize=12, fontweight='bold', color='#28A745',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#D4EDDA',
                      edgecolor='#28A745'))
    ax.text(2.0, 3.85, 'Time: 312 ms     Size: 156 B',
            fontsize=10, color='#666', va='center')

    # Response body
    ax.add_patch(Rectangle((0.2, 0.3), 13.6, 3.2, facecolor='#1E1E1E',
                            edgecolor='#D0D0D0', linewidth=1))
    response = (
        '{\n'
        '    "token": "46af11fce98ccc453ea3ce63a58b7720bb4e04f9",\n'
        '    "user": {\n'
        '        "user_id": 1,\n'
        '        "username": "admin01",\n'
        '        "email": "",\n'
        '        "full_name": "Quản trị viên",\n'
        '        "phone": "",\n'
        '        "user_role": "admin",\n'
        '        "is_active": true\n'
        '    }\n'
        '}'
    )
    ax.text(0.5, 3.2, response, fontsize=10.5, va='top', family='Consolas',
            color='#E0E0E0')

    ax.set_title('Hình 4. Kiểm thử API đăng nhập trên Postman — '
                 'POST /api/auth/login trả về token + thông tin user',
                 fontsize=12, pad=10)

    plt.tight_layout()
    out = os.path.join(OUT_DIR, 'hinh4_postman_login.png')
    plt.savefig(out, dpi=180, bbox_inches='tight', facecolor='#F4F4F4')
    plt.close()
    return out


# ============================================================
# Hình 5 — Mock Postman receipt flow (3 panels)
# ============================================================
def draw_postman_receipt_flow():
    fig, axes = plt.subplots(3, 1, figsize=(14, 13))

    panels = [
        # (method, url, body, response_status, response, color)
        ('POST', '/api/receipts',
         '{\n  "warehouse": 1,\n  "receipt_type": "IMPORT"\n}',
         '201 Created',
         '{\n  "receipt_id": 4,\n  "warehouse": 1,\n  "warehouse_name": "Kho TP.HCM",\n  "receipt_type": "IMPORT",\n  "receipt_status": "PENDING",\n  "created_at": "2026-05-25 14:23:12",\n  "details": []\n}'),
        ('POST', '/api/receipts/4/details',
         '[\n  {"product": 1, "quantity": 50},\n  {"product": 2, "quantity": 30}\n]',
         '201 Created',
         '[\n  {"detail_id": 8, "product": 1, "product_code": "P001",\n   "product_name": "Paracetamol 500mg", "quantity": 50},\n  {"detail_id": 9, "product": 2, "product_code": "P002",\n   "product_name": "Vitamin C 1000mg", "quantity": 30}\n]'),
        ('PUT', '/api/receipts/4/status',
         '{\n  "receipt_status": "APPROVED"\n}',
         '200 OK',
         '{\n  "receipt_id": 4, "receipt_status": "APPROVED",\n  "details": [...]\n}\n→ Bảng inventory đã cộng quantity:\n   warehouse=1, product=1: +50  (tổng tồn mới)\n   warehouse=1, product=2: +30  (tổng tồn mới)'),
    ]

    method_colors = {'POST': '#FF7F0E', 'PUT': '#5BA1D0', 'GET': '#28A745'}

    for idx, (method, url, body, status_text, response) in enumerate(panels):
        ax = axes[idx]
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 4.5)
        ax.axis('off')
        ax.set_facecolor('#F4F4F4')

        # URL bar
        ax.add_patch(Rectangle((0.1, 3.8), 13.8, 0.5, facecolor='#FFFFFF',
                                edgecolor='#D0D0D0', linewidth=1))
        ax.text(0.3, 4.05, method, fontsize=10, fontweight='bold',
                color=method_colors[method],
                bbox=dict(boxstyle='round,pad=0.2',
                          facecolor='#FFE4C7' if method == 'POST'
                          else ('#D6E9F8' if method == 'PUT' else '#D4EDDA'),
                          edgecolor=method_colors[method]))
        ax.text(1.1, 4.05, f'https://ezware-backend.onrender.com{url}',
                fontsize=10, va='center', family='Consolas')

        # Body
        ax.text(0.2, 3.55, 'Body:', fontsize=9, fontweight='bold', color='#666')
        ax.add_patch(Rectangle((0.1, 2.0), 6.8, 1.5, facecolor='#FFFFFF',
                                edgecolor='#D0D0D0', linewidth=1))
        ax.text(0.3, 3.3, body, fontsize=9.5, va='top', family='Consolas')

        # Response
        ax.text(7.2, 3.55, f'Response:', fontsize=9, fontweight='bold', color='#666')
        status_color = '#28A745' if '200' in status_text or '201' in status_text else '#DC3545'
        ax.text(8.0, 3.55, status_text, fontsize=10, fontweight='bold',
                color=status_color)
        ax.add_patch(Rectangle((7.1, 0.1), 6.8, 3.4, facecolor='#1E1E1E',
                                edgecolor='#D0D0D0', linewidth=1))
        ax.text(7.3, 3.3, response, fontsize=9, va='top', family='Consolas',
                color='#E0E0E0')

        # Step label trái
        ax.text(0.2, 1.0, f'Bước {idx + 1}',
                fontsize=14, fontweight='bold', color='#3F72AF')

    fig.suptitle('Hình 5. Kiểm thử luồng tạo phiếu nhập → thêm chi tiết → duyệt phiếu '
                 '(quantity tồn kho tự cập nhật trong transaction.atomic)',
                 fontsize=12, y=1.00)
    plt.tight_layout()
    out = os.path.join(OUT_DIR, 'hinh5_postman_receipt_flow.png')
    plt.savefig(out, dpi=160, bbox_inches='tight', facecolor='#F4F4F4')
    plt.close()
    return out


# ============================================================
# Hình 6 — Mock Swagger UI list endpoints
# ============================================================
def draw_swagger_ui():
    fig, ax = plt.subplots(figsize=(14, 17))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 17)
    ax.axis('off')
    ax.set_facecolor('white')

    # URL bar
    ax.add_patch(Rectangle((0, 16.3), 14, 0.5, facecolor='#F0F0F0',
                            edgecolor='#CCC', linewidth=1))
    ax.text(0.3, 16.55,
            'URL:  https://ezware-backend.onrender.com/swagger/',
            fontsize=11, va='center', family='Consolas')

    # Title
    ax.text(7, 15.8, 'EZWare API – Swagger UI',
            ha='center', fontsize=14, fontweight='bold')
    ax.text(7, 15.4, '14 URL endpoint · 23 HTTP operations · Token Authentication',
            ha='center', fontsize=10, style='italic', color='#666')

    # 23 operations đầy đủ (đếm theo method + URL combo)
    endpoints = [
        ('POST', '/api/auth/register', 'Đăng ký tài khoản mới'),
        ('POST', '/api/auth/login', 'Đăng nhập, trả token'),
        ('POST', '/api/auth/logout', 'Đăng xuất, xóa token'),
        ('GET', '/api/auth/me', 'Xem profile user'),
        ('PUT', '/api/auth/me', 'Cập nhật profile'),
        ('GET', '/api/products', 'Danh sách sản phẩm'),
        ('POST', '/api/products', 'Tạo sản phẩm (Admin)'),
        ('GET', '/api/products/{id}', 'Xem chi tiết sản phẩm'),
        ('PUT', '/api/products/{id}', 'Cập nhật sản phẩm (Admin)'),
        ('DELETE', '/api/products/{id}', 'Xóa sản phẩm (Admin)'),
        ('GET', '/api/warehouses', 'Danh sách kho'),
        ('POST', '/api/warehouses', 'Tạo kho (Admin)'),
        ('GET', '/api/warehouses/{id}', 'Xem chi tiết kho'),
        ('PUT', '/api/warehouses/{id}', 'Cập nhật kho (Admin)'),
        ('DELETE', '/api/warehouses/{id}', 'Xóa kho (Admin)'),
        ('GET', '/api/warehouses/{id}/inventory', 'Xem tồn kho theo kho'),
        ('GET', '/api/receipts', 'Danh sách phiếu'),
        ('POST', '/api/receipts', 'Tạo phiếu nhập/xuất'),
        ('GET', '/api/receipts/{id}', 'Xem chi tiết phiếu'),
        ('DELETE', '/api/receipts/{id}', 'Xóa phiếu PENDING (Admin)'),
        ('POST', '/api/receipts/{id}/details', 'Thêm chi tiết phiếu'),
        ('PUT', '/api/receipts/{id}/status', 'Duyệt/hủy phiếu (Admin)'),
        ('GET', '/api/reports/low-stock', 'Báo cáo tồn thấp'),
    ]

    color_map = {
        'GET': ('#61AFFE', '#E5F1FC'),
        'POST': ('#49CC90', '#E2F5EB'),
        'PUT': ('#FCA130', '#FDF1E0'),
        'DELETE': ('#F93E3E', '#FCE2E2'),
    }

    y = 14.7
    row_h = 0.55
    for method, path, desc in endpoints:
        edge, fill = color_map[method]
        # Row container
        ax.add_patch(Rectangle((0.3, y - row_h + 0.1), 13.4, row_h - 0.05,
                                facecolor=fill, edgecolor=edge, linewidth=1))
        # Method box
        ax.add_patch(Rectangle((0.45, y - 0.35), 1.1, 0.4,
                                facecolor=edge, edgecolor='none'))
        ax.text(1.0, y - 0.15, method, ha='center', va='center',
                color='white', fontsize=10, fontweight='bold')
        # Path
        ax.text(1.85, y - 0.15, path, fontsize=11,
                family='Consolas', va='center', fontweight='bold')
        # Description
        ax.text(7.5, y - 0.15, desc, fontsize=10, va='center', color='#444')
        # Auth required indicator
        needs_auth = 'auth/register' not in path and 'auth/login' not in path
        ax.text(13.4, y - 0.15, '[Auth]' if needs_auth else '', fontsize=8,
                va='center', color='#666', fontweight='bold')
        y -= row_h

    ax.set_title('Hình 6. Giao diện Swagger UI tại /swagger/ — tự sinh tài liệu '
                 'cho 14 URL endpoint (23 HTTP operations)',
                 fontsize=12, pad=10)

    plt.tight_layout()
    out = os.path.join(OUT_DIR, 'hinh6_swagger_ui.png')
    plt.savefig(out, dpi=160, bbox_inches='tight', facecolor='white')
    plt.close()
    return out


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    print('Sinh hình minh hoạ cho báo cáo EZWare...')
    for func in (
        draw_er_diagram,
        draw_function_diagram,
        draw_class_diagram,
        draw_postman_login,
        draw_postman_receipt_flow,
        draw_swagger_ui,
    ):
        path = func()
        size_kb = os.path.getsize(path) / 1024
        print(f'  ✓  {path}  ({size_kb:.1f} KB)')
    print(f'\nThư mục output: {OUT_DIR}/')
