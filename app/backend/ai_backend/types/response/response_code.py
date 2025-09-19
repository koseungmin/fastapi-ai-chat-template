from enum import Enum, unique


__all__ = [
    "ResponseCode"
]


@unique
class ResponseCode(Enum):

    SUCCESS  = (1, "성공")
    FAIL = (-1, "실패")
    UNDEFINED_ERROR = (-2, "정의되지 않은 오류입니다.")
    
    #AZURE_COMPLETIONS_SERVICE = (-1000 ~ -1099)
    AZURE_COMPLETIONS_IS_NULL_OR_EMPTY = (-1001, "요청한 COMPLETIONS 서비스가 유효하지 않습니다.")
    
    #OPEN_AI_SERVICE = (-1100 ~ -1199)
    OPENAI_GET_MODEL_IS_NULL_OR_EMPTY = (-1101, "요청한 GET_MODEL 서비스가 유효하지 않습니다.")
    
    # USER_SERVICE = (-1200 ~ -1299)
    USER_NOT_FOUND = (-1201, "사용자를 찾을 수 없습니다.")
    USER_ALREADY_EXISTS = (-1202, "이미 존재하는 사용자입니다.")
    USER_INVALID_CREDENTIALS = (-1203, "잘못된 인증 정보입니다.")
    
    # CHAT_SERVICE = (-1300 ~ -1399)
    CHAT_SESSION_NOT_FOUND = (-1301, "채팅 세션을 찾을 수 없습니다.")
    CHAT_MESSAGE_INVALID = (-1302, "잘못된 채팅 메시지입니다.")
    CHAT_RATE_LIMIT_EXCEEDED = (-1303, "채팅 요청 한도를 초과했습니다.")
    CHAT_CREATE_ERROR = (-1304, "채팅 생성 중 오류가 발생했습니다.")
    CHAT_DELETE_ERROR = (-1305, "채팅 삭제 중 오류가 발생했습니다.")
    CHAT_ACCESS_DENIED = (-1306, "채팅에 접근할 권한이 없습니다.")
    CHAT_MESSAGE_SEND_ERROR = (-1307, "메시지 전송 중 오류가 발생했습니다.")
    CHAT_AI_RESPONSE_ERROR = (-1308, "AI 응답 생성 중 오류가 발생했습니다.")
    CHAT_GENERATION_CANCEL_ERROR = (-1309, "응답 취소 중 오류가 발생했습니다.")
    CHAT_HISTORY_LOAD_ERROR = (-1310, "대화 기록 로드 중 오류가 발생했습니다.")
    CHAT_TITLE_GENERATION_ERROR = (-1311, "채팅 제목 생성 중 오류가 발생했습니다.")
    
    # DATABASE_SERVICE = (-1400 ~ -1499)
    DATABASE_CONNECTION_ERROR = (-1401, "데이터베이스 연결 오류가 발생했습니다.")
    DATABASE_QUERY_ERROR = (-1402, "데이터베이스 쿼리 오류가 발생했습니다.")
    DATABASE_TRANSACTION_ERROR = (-1403, "데이터베이스 트랜잭션 오류가 발생했습니다.")
    
    # CACHE_SERVICE = (-1500 ~ -1599)
    CACHE_CONNECTION_ERROR = (-1501, "캐시 연결 오류가 발생했습니다.")
    CACHE_OPERATION_ERROR = (-1502, "캐시 작업 오류가 발생했습니다.")
    
    # VALIDATION_ERROR = (-1600 ~ -1699)
    VALIDATION_ERROR = (-1601, "입력 데이터 검증 오류가 발생했습니다.")
    REQUIRED_FIELD_MISSING = (-1602, "필수 필드가 누락되었습니다.")
    INVALID_DATA_FORMAT = (-1603, "잘못된 데이터 형식입니다.")
    
    # EXTERNAL_SERVICE = (-1700 ~ -1799)
    EXTERNAL_SERVICE_ERROR = (-1701, "외부 서비스 오류가 발생했습니다.")
    EXTERNAL_SERVICE_TIMEOUT = (-1702, "외부 서비스 응답 시간 초과가 발생했습니다.")
    EXTERNAL_SERVICE_UNAVAILABLE = (-1703, "외부 서비스를 사용할 수 없습니다.")
    
    # DOCUMENT_SERVICE = (-1800 ~ -1899)
    DOCUMENT_NOT_FOUND = (-1801, "문서를 찾을 수 없습니다.")
    DOCUMENT_ALREADY_EXISTS = (-1802, "이미 존재하는 문서입니다.")
    DOCUMENT_UPLOAD_ERROR = (-1803, "문서 업로드 중 오류가 발생했습니다.")
    DOCUMENT_DOWNLOAD_ERROR = (-1804, "문서 다운로드 중 오류가 발생했습니다.")
    DOCUMENT_DELETE_ERROR = (-1805, "문서 삭제 중 오류가 발생했습니다.")
    DOCUMENT_FILE_TOO_LARGE = (-1806, "파일 크기가 너무 큽니다.")
    DOCUMENT_INVALID_FILE_TYPE = (-1807, "지원하지 않는 파일 형식입니다.")
    DOCUMENT_FOLDER_NOT_FOUND = (-1808, "폴더를 찾을 수 없습니다.")
    DOCUMENT_FOLDER_ALREADY_EXISTS = (-1809, "이미 존재하는 폴더입니다.")
    DOCUMENT_FOLDER_CREATE_ERROR = (-1810, "폴더 생성 중 오류가 발생했습니다.")
    DOCUMENT_FOLDER_DELETE_ERROR = (-1811, "폴더 삭제 중 오류가 발생했습니다.")
    DOCUMENT_FILE_TYPE_NOT_ALLOWED = (-1812, "지원하지 않는 파일 타입입니다.")
    DOCUMENT_CREATE_ERROR = (-1813, "문서 생성 중 오류가 발생했습니다.")
    DOCUMENT_UPLOAD_NOT_FOUND = (-1814, "업로드 ID를 찾을 수 없습니다.")
    DOCUMENT_UPLOAD_PROCESSING = (-1815, "업로드가 아직 처리 중입니다.")
    DOCUMENT_UPLOAD_FAILED = (-1816, "업로드 처리에 실패했습니다.")
    
    # GROUP_SERVICE = (-1900 ~ -1999)
    GROUP_NOT_FOUND = (-1901, "그룹을 찾을 수 없습니다.")
    GROUP_ALREADY_EXISTS = (-1902, "이미 존재하는 그룹입니다.")
    GROUP_MEMBER_NOT_FOUND = (-1903, "그룹 멤버를 찾을 수 없습니다.")
    GROUP_MEMBER_ALREADY_EXISTS = (-1904, "이미 그룹의 멤버입니다.")
    GROUP_MAX_MEMBERS_EXCEEDED = (-1905, "그룹의 최대 멤버 수를 초과했습니다.")
    GROUP_OWNER_CANNOT_BE_REMOVED = (-1906, "그룹 소유자는 제거할 수 없습니다.")
    GROUP_INSUFFICIENT_PERMISSION = (-1907, "그룹에 대한 권한이 부족합니다.")
    GROUP_CREATE_ERROR = (-1908, "그룹 생성 중 오류가 발생했습니다.")
    GROUP_UPDATE_ERROR = (-1909, "그룹 수정 중 오류가 발생했습니다.")
    GROUP_DELETE_ERROR = (-1910, "그룹 삭제 중 오류가 발생했습니다.")
    GROUP_MEMBER_ADD_ERROR = (-1911, "그룹 멤버 추가 중 오류가 발생했습니다.")
    GROUP_MEMBER_REMOVE_ERROR = (-1912, "그룹 멤버 제거 중 오류가 발생했습니다.")
    GROUP_MEMBER_ROLE_UPDATE_ERROR = (-1913, "그룹 멤버 역할 변경 중 오류가 발생했습니다.")
    
    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
