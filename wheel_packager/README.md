# 목적
Wheel File Packager는 `.whl` 및 `.zip` 파일을 업로드하여 자동으로 `python.zip` 파일을 생성하도록 돕는 앱이다.  
**AWS Lambda Layer**를 생성하기 위한 목적으로, 업로드한 `.whl` 파일의 압축을 해제한 후, 모든 파일을 `python/` 폴더 내부에 정리하여 `python.zip` 파일로 압축한다. 기존 `python.zip` 파일에 추가로 압축 해제가 필요한 경우에도 사용할 수 있다.

# 기능
- `.whl` 및 `python.zip` 파일 업로드 지원
- 기존 `python.zip` 파일과 병합 가능
- 업로드한 `.whl` 파일을 자동으로 `python/` 폴더에 정리
- `python.zip` 파일이 이미 존재하면 덮어쓰기
- 처리 완료 후 업로드된 파일 목록 초기화 및 원본 .whl 파일 삭제

# 사용법
1. `tkinterdnd2` 설치 (`pip install tkinterdnd2`)
2. 프로그램 실행
3. `.whl` 또는 `python.zip` 파일을 드래그 앤 드롭하거나 직접 선택하여 업로드
4. 파일 목록에서 확인 후 **Process Files** 버튼 클릭
5. `python.zip` 파일이 생성되면 자동으로 파일 정리

# 주의사항
- 기존 `python.zip` 파일이 있으면 자동으로 덮어쓴다.
- 파일 처리가 완료되면 원본 `.whl` 파일이 삭제된다.