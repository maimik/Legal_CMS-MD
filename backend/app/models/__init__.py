"""
SQLAlchemy модели для Legal CMS
"""
from app.models.user import User
from app.models.case import Case
from app.models.person import Person
from app.models.case_person import CasePerson
from app.models.document import Document
from app.models.case_event import CaseEvent
from app.models.legal_act import LegalAct
from app.models.case_legal_act import CaseLegalAct
from app.models.document_template import DocumentTemplate
from app.models.audit_log import AuditLog
from app.models.document_embedding import DocumentEmbedding
from app.models.system_setting import SystemSetting

__all__ = [
    "User",
    "Case",
    "Person",
    "CasePerson",
    "Document",
    "CaseEvent",
    "LegalAct",
    "CaseLegalAct",
    "DocumentTemplate",
    "AuditLog",
    "DocumentEmbedding",
    "SystemSetting",
]
