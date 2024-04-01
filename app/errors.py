# 에러메시지를 모아둔 파일입니다.

# 예시 에러 메시지
REQUIRED_INPUT_DATA = "필수 입력 항목입니다. 내용을 입력해주세요."

class RequiredInputDataError(Error):
    def __init__(self, message=REQUIRED_INPUT_DATA):
        self.message = message
        super().__init__(message)