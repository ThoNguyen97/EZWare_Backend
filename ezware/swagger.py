from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.generators import OpenAPISchemaGenerator


# Gắn tên nhóm tiếng Việt có số thứ tự để Swagger hiển thị đúng thứ tự logic:
# Xác thực -> Danh mục -> Nghiệp vụ kho -> Báo cáo.
TAG_MAP = [
    ('/auth/', '1. Xác thực & Tài khoản'),
    ('/products', '2. Danh mục - Sản phẩm'),
    ('/warehouses', '3. Danh mục - Kho'),
    ('/receipts', '4. Nghiệp vụ kho'),
    ('/reports', '5. Báo cáo'),
]

TAG_ORDER = [name for _, name in TAG_MAP]


class OrderedTagAutoSchema(SwaggerAutoSchema):
    def get_tags(self, operation_keys=None):
        for prefix, tag in TAG_MAP:
            if prefix in self.path:
                return [tag]
        return super().get_tags(operation_keys)


class OrderedSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        # Khai báo mảng tags toàn cục theo đúng thứ tự để Swagger UI hiển thị
        # các nhóm theo trình tự 1 -> 5 thay vì sắp theo alphabet đường dẫn.
        schema.tags = [{'name': name} for name in TAG_ORDER]
        return schema
