# Tài liệu SIEM-Detection-as-Code

Thư mục `docs/` chứa tài liệu kiến trúc, mô tả luồng xử lý, và các ghi chú lịch sử cho repository `SIEM-Detection-as-Code`.

## Cách dùng thư mục này

- Dùng `docs/architecture/` làm source of truth cho kiến trúc hiện tại.
- Dùng `docs/en/architecture/` khi cần bản tiếng Anh.
- Dùng `docs/note/` để tra lại note trong repo và bối cảnh lịch sử; dùng `log/` cho task log và review log cục bộ.

## Cấu trúc chính

```text
docs/
|-- README.md
|-- README.vi.md
|-- architecture/
|   |-- project-architecture.md
|   |-- rule-rendering-flows.md
|   |-- tenants-relationship.md
|   |-- mappings-relationship.md
|   `-- execution-relationship.md
|-- en/
|   `-- architecture/
|-- note/
|   |-- base-note.txt
|   `-- SIEM-DaC-Idea.md
`-- ../log/
    `-- YYYY-MM-DD/
        `-- <log-type>/
```

## Nên đọc theo thứ tự nào

Nếu muốn hiểu kiến trúc hiện tại:

1. `architecture/project-architecture.md`
2. `architecture/rule-rendering-flows.md`
3. `architecture/tenants-relationship.md`
4. `architecture/mappings-relationship.md`
5. `architecture/execution-relationship.md`

Nếu muốn hiểu trạng thái thay đổi gần đây:

1. `../log/2026-03-23/repo-gap-review/repo-gap-review.md`
2. `../log/YYYY-MM-DD/project-root-code-maintainer/*.md`

## Nguyên tắc tài liệu

- Giữ nguyên định hướng kiến trúc khi cập nhật README và note.
- Phân biệt rõ tài liệu kiến trúc với note lịch sử.
- Nếu implementation đang ở trạng thái chuyển tiếp, mô tả current state mà không thay đổi kiến trúc nền.
- Xem `execution/` là một lớp kiến trúc chính; chi tiết nằm tại `architecture/execution-relationship.md`.

## Tóm tắt

`docs/` là điểm vào chính để hiểu repo. Với kiến trúc, ưu tiên `docs/architecture/`. Với note trong repo, xem `docs/note/`. Với log tác vụ và review cục bộ, xem `log/`.
