# 로컬 아카이브(AnnualReport_MD) 인제스트 트래커

- 아카이브 회사 수: **2736건** (source_documents/AnnualReport_MD/, 각 머신에 로컬 배치 필요·git 미포함)
- 완료(done, Full): **408건**
- 대기(pending): **2328건** (이 중 stub→Full 승급 대상 124건)

> done 기준: wiki/companies/<회사>.md 가 존재하고 is_stub:false.
> market 판정: 위키 frontmatter 우선, 없으면 원본 MD의 '상장 유형' 표(유가증권시장/코스닥시장 상장)에서 추출.
> 이 파일은 `python dart_pipeline/local_archive_status.py [--market KOSPI|KOSDAQ]` 로 재생성됩니다.
> 다음 N개사 산출: `python dart_pipeline/local_archive_status.py [--market KOSPI|KOSDAQ] --next N`

## ⏳ 대기 (상위 50건, 전체 2328건)

- APS이노베이션 (`KOSDAQ`) — `source_documents/AnnualReport_MD/APS이노베이션-사업보고서-2024.12.md`
- CS (`KOSDAQ`) — `source_documents/AnnualReport_MD/CS-사업보고서-2025.12.md`
- DB (`KOSPI`) — `source_documents/AnnualReport_MD/DB-사업보고서-2025.12.md`
- DGI (`KOSDAQ`) — `source_documents/AnnualReport_MD/DGI-사업보고서-2025.12.md`
- DH오토넥스 (`KOSPI`) — `source_documents/AnnualReport_MD/DH오토넥스-사업보고서-2025.12.md`
- DXVX (`KOSDAQ`) — `source_documents/AnnualReport_MD/DXVX-사업보고서-2025.12.md`
- E8 (`KOSDAQ`) — `source_documents/AnnualReport_MD/E8-사업보고서-2025.12.md`
- EDGC (`KOSDAQ`) — `source_documents/AnnualReport_MD/EDGC-사업보고서-2025.12.md`
- EG (`KOSDAQ`) — `source_documents/AnnualReport_MD/EG-사업보고서-2025.12.md`
- EMB (`Unknown`) — `source_documents/AnnualReport_MD/EMB-사업보고서-2025.12.md`
- ES큐브 (`KOSDAQ`) — `source_documents/AnnualReport_MD/ES큐브-사업보고서-2025.12.md`
- F&F (`Private`) — `source_documents/AnnualReport_MD/F&F-사업보고서-2025.12.md`
- F&F 홀딩스 (`KOSPI`) — `source_documents/AnnualReport_MD/F&F 홀딩스-사업보고서-2025.12.md`
- FSN (`KOSDAQ`) — `source_documents/AnnualReport_MD/FSN-사업보고서-2025.12.md`
- GC메디아이 (`KOSDAQ`) — `source_documents/AnnualReport_MD/GC메디아이-사업보고서-2025.12.md`
- GH신소재 (`KOSDAQ`) — `source_documents/AnnualReport_MD/GH신소재-사업보고서-2025.12.md`
- GRT (`KOSDAQ`) — `source_documents/AnnualReport_MD/GRT-사업보고서-2025.06.md`
- GST (`KOSDAQ`) — `source_documents/AnnualReport_MD/GST-사업보고서-2025.12.md`
- HB솔루션 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HB솔루션-사업보고서-2025.12.md`
- HB인베스트먼트 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HB인베스트먼트-사업보고서-2025.12.md`
- HB테크놀러지 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HB테크놀러지-사업보고서-2025.12.md`
- HC보광산업 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HC보광산업-사업보고서-2025.12.md`
- HC홈센타 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HC홈센타-사업보고서-2025.12.md`
- HEM파마 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HEM파마-사업보고서-2025.12.md`
- HK이노엔 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HK이노엔-사업보고서-2025.12.md`
- HLB (`KOSDAQ`) — `source_documents/AnnualReport_MD/HLB-사업보고서-2025.12.md`
- HLB바이오스텝 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HLB바이오스텝-사업보고서-2025.12.md`
- HLB생명과학 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HLB생명과학-사업보고서-2025.12.md`
- HLB이노베이션 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HLB이노베이션-사업보고서-2025.12.md`
- HLB제넥스 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HLB제넥스-사업보고서-2025.12.md`
- HLB제약 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HLB제약-사업보고서-2025.12.md`
- HLB테라퓨틱스 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HLB테라퓨틱스-사업보고서-2025.12.md`
- HLB파나진 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HLB파나진-사업보고서-2025.12.md`
- HLB펩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HLB펩-사업보고서-2025.12.md`
- HL만도 (`KOSPI`) — `source_documents/AnnualReport_MD/HL만도-사업보고서-2025.12.md`
- HL홀딩스 (`KOSPI`) — `source_documents/AnnualReport_MD/HL홀딩스-사업보고서-2025.12.md`
- HPSP (`KOSDAQ`) — `source_documents/AnnualReport_MD/HPSP-사업보고서-2025.12.md`
- HRS (`KOSDAQ`) — `source_documents/AnnualReport_MD/HRS-사업보고서-2025.12.md`
- IBKS제23호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/IBKS제23호스팩-사업보고서-2025.12.md`
- IBKS제24호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/IBKS제24호스팩-사업보고서-2025.12.md`
- IBKS제25호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/IBKS제25호스팩-사업보고서-2025.12.md`
- IPARK현대산업개발 (`KOSPI`) — `source_documents/AnnualReport_MD/IPARK현대산업개발-사업보고서-2025.12.md`
- JTC (`KOSDAQ`) — `source_documents/AnnualReport_MD/JTC-사업보고서-2026.02.md`
- JW신약 (`KOSDAQ`) — `source_documents/AnnualReport_MD/JW신약-사업보고서-2025.12.md`
- JYP Ent. (`KOSDAQ`) — `source_documents/AnnualReport_MD/JYP Ent.-사업보고서-2025.12.md`
- KBG (`KOSDAQ`) — `source_documents/AnnualReport_MD/KBG-사업보고서-2025.12.md`
- KBI메탈 (`KOSDAQ`) — `source_documents/AnnualReport_MD/KBI메탈-사업보고서-2025.12.md`
- KB금융 (`KOSPI`) — `source_documents/AnnualReport_MD/KB금융-사업보고서-2025.12.md`
- KB오토시스 (`KOSDAQ`) — `source_documents/AnnualReport_MD/KB오토시스-사업보고서-2025.12.md`
- KB제29호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/KB제29호스팩-사업보고서-2025.12.md`
