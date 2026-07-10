# 로컬 아카이브(AnnualReport_MD) 인제스트 트래커 (KOSPI)

- 아카이브 회사 수: **823건** (source_documents/AnnualReport_MD/, 각 머신에 로컬 배치 필요·git 미포함)
- 완료(done, Full): **779건**
- 대기(pending): **44건** (이 중 stub→Full 승급 대상 10건)

> done 기준: wiki/companies/<회사>.md 가 존재하고 is_stub:false.
> market 판정: 위키 frontmatter 우선, 없으면 원본 MD의 '상장 유형' 표(유가증권시장/코스닥시장 상장)에서 추출.
> 이 파일은 `python dart_pipeline/local_archive_status.py [--market KOSPI|KOSDAQ]` 로 재생성됩니다.
> 다음 N개사 산출: `python dart_pipeline/local_archive_status.py [--market KOSPI|KOSDAQ] --next N`

## ⏳ 대기 (상위 50건, 전체 44건)

- DB (`KOSPI`) — `source_documents/AnnualReport_MD/DB-사업보고서-2025.12.md`
- DH오토넥스 (`KOSPI`) — `source_documents/AnnualReport_MD/DH오토넥스-사업보고서-2025.12.md`
- F&F 홀딩스 (`KOSPI`) — `source_documents/AnnualReport_MD/F&F 홀딩스-사업보고서-2025.12.md`
- HL만도 (`KOSPI`) — `source_documents/AnnualReport_MD/HL만도-사업보고서-2025.12.md`
- HL홀딩스 (`KOSPI`) — `source_documents/AnnualReport_MD/HL홀딩스-사업보고서-2025.12.md`
- IPARK현대산업개발 (`KOSPI`) — `source_documents/AnnualReport_MD/IPARK현대산업개발-사업보고서-2025.12.md`
- KB금융 (`KOSPI`) — `source_documents/AnnualReport_MD/KB금융-사업보고서-2025.12.md`
- NC (`KOSPI`) — `source_documents/AnnualReport_MD/NC-사업보고서-2025.12.md`
- NICE (`KOSPI`) — `source_documents/AnnualReport_MD/NICE-사업보고서-2025.12.md`
- PKC (`KOSPI`) — `source_documents/AnnualReport_MD/PKC-사업보고서-2025.12.md`
- POSCO홀딩스 (`KOSPI`) — `source_documents/AnnualReport_MD/POSCO홀딩스-사업보고서-2025.12.md`
- SHD (`KOSPI`) — `source_documents/AnnualReport_MD/SHD-사업보고서-2025.12.md`
- SP삼화 (`KOSPI`) — `source_documents/AnnualReport_MD/SP삼화-사업보고서-2025.12.md`
- SYTS (`KOSPI`) — `source_documents/AnnualReport_MD/SYTS-사업보고서-2025.12.md`
- 국일신동 (`KOSPI`) — `source_documents/AnnualReport_MD/국일신동-사업보고서-2025.12.md`
- 나무가 (`KOSPI`) — `source_documents/AnnualReport_MD/나무가-사업보고서-2025.12.md`
- 동국제약 (`KOSPI`) — `source_documents/AnnualReport_MD/동국제약-사업보고서-2025.12.md`
- 동양생명 (`KOSPI`) — `source_documents/AnnualReport_MD/동양생명-사업보고서-2025.12.md`
- 동원금속 (`KOSPI`) — `source_documents/AnnualReport_MD/동원금속-사업보고서-2026.03.md`
- 디와이에이 (`KOSPI`) — `source_documents/AnnualReport_MD/디와이에이-사업보고서-2025.12.md`
- 삼성생명 (`KOSPI`) — `source_documents/AnnualReport_MD/삼성생명-사업보고서-2025.12.md`
- 삼성에스디에스 (`KOSPI`) — `source_documents/AnnualReport_MD/삼성에스디에스-사업보고서-2025.12.md`
- 삼성화재해상보험 (`KOSPI`) — `source_documents/AnnualReport_MD/삼성화재해상보험-사업보고서-2025.12.md`
- 신한지주 (`KOSPI`) — `source_documents/AnnualReport_MD/신한지주-사업보고서-2025.12.md`
- 싸이맥스 (`KOSPI`) — `source_documents/AnnualReport_MD/싸이맥스-사업보고서-2025.12.md`
- 아난티 (`KOSPI`) — `source_documents/AnnualReport_MD/아난티-사업보고서-2024.12.md`
- 에코프로머티 (`KOSPI`) — `source_documents/AnnualReport_MD/에코프로머티-사업보고서-2025.12.md`
- 엘에스일렉트릭 (`KOSPI`) — `source_documents/AnnualReport_MD/엘에스일렉트릭-사업보고서-2025.12.md`
- 우성머티리얼스 (`KOSPI`) — `source_documents/AnnualReport_MD/우성머티리얼스-사업보고서-2025.12.md`
- 유진증권 (`KOSPI`) — `source_documents/AnnualReport_MD/유진증권-사업보고서-2025.12.md`
- 인성정보 (`KOSPI`) — `source_documents/AnnualReport_MD/인성정보-사업보고서-2025.12.md`
- 제일연마 (`KOSPI`) — `source_documents/AnnualReport_MD/제일연마-사업보고서-2025.12.md`
- 지씨셀 (`KOSPI`) — `source_documents/AnnualReport_MD/지씨셀-사업보고서-2025.12.md`
- 지역난방공사 (`KOSPI`) — `source_documents/AnnualReport_MD/지역난방공사-사업보고서-2025.12.md`
- 케이씨씨 (`KOSPI`) — `source_documents/AnnualReport_MD/케이씨씨-사업보고서-2025.12.md`
- 케이티앤지 (`KOSPI`) — `source_documents/AnnualReport_MD/케이티앤지-사업보고서-2025.12.md`
- 코오롱인더 (`KOSPI`) — `source_documents/AnnualReport_MD/코오롱인더-사업보고서-2025.12.md`
- 트리니티항공 (`KOSPI`) — `source_documents/AnnualReport_MD/트리니티항공-사업보고서-2025.12.md`
- 티와이홀딩스 (`KOSPI`) — `source_documents/AnnualReport_MD/티와이홀딩스-사업보고서-2025.12.md`
- 티케이지휴켐스 (`KOSPI`) — `source_documents/AnnualReport_MD/티케이지휴켐스-사업보고서-2025.12.md`
- 한국항공우주 (`KOSPI`) — `source_documents/AnnualReport_MD/한국항공우주-사업보고서-2025.12.md`
- 한전산업 (`KOSPI`) — `source_documents/AnnualReport_MD/한전산업-사업보고서-2025.12.md`
- 한화생명 (`KOSPI`) — `source_documents/AnnualReport_MD/한화생명-사업보고서-2025.12.md`
- 효성 ITX (`KOSPI`) — `source_documents/AnnualReport_MD/효성 ITX-사업보고서-2025.12.md`
