"""
知识库 Schema

定义知识库相关的请求和响应数据结构
"""
from marshmallow import Schema, fields, validate, validates, ValidationError


class AddDocumentRequest(Schema):
    """添加文档请求 Schema"""
    doc_id = fields.Str(required=True)
    content = fields.Str(required=True)
    metadata = fields.Dict(required=False, missing={})


class AddDocumentResponse(Schema):
    """添加文档响应 Schema"""
    message = fields.Str(required=True)
    doc_id = fields.Str(required=True)


class SearchDocumentsRequest(Schema):
    """搜索文档请求 Schema"""
    query = fields.Str(required=True)
    n_results = fields.Int(required=False, missing=5, validate=validate.Range(min=1, max=50))
    where = fields.Dict(required=False, missing=None)


class SearchResultItem(Schema):
    """搜索结果项 Schema"""
    document = fields.Str(required=True)
    metadata = fields.Dict(required=False, missing={})
    distance = fields.Float(required=False)


class SearchDocumentsResponse(Schema):
    """搜索文档响应 Schema"""
    query = fields.Str(required=True)
    results = fields.List(fields.Nested(SearchResultItem), required=True)
    count = fields.Int(required=True)


class DeleteDocumentRequest(Schema):
    """删除文档请求 Schema"""
    doc_id = fields.Str(required=True)


class DeleteDocumentResponse(Schema):
    """删除文档响应 Schema"""
    message = fields.Str(required=True)
    doc_id = fields.Str(required=True)


class GetDocumentsResponse(Schema):
    """获取文档列表响应 Schema"""
    results = fields.List(fields.Nested(SearchResultItem), required=True)
    count = fields.Int(required=True)
