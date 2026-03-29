# Tài liệu SIEM-Detection-as-Code

Thư mục `docs/` chứa tài liệu kiến trúc, mô tả luồng xử lý, và các ghi chú lịch sử cho repository `SIEM-Detection-as-Code`.

## Cách dùng thư mục này

- Dùng `docs/architecture/` làm source of truth cho kiến trúc hiện tại.
- Dùng `docs/en/architecture/` khi cần bản tiếng Anh.
- Dùng `docs/note/` để tra lại bối cảnh lịch sử, gap review, và log thay đổi gần đây.

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
`-- note/
    |-- repo-gap-review-2026-03-23.md
    `-- logs/
```

## Nên đọc theo thứ tự nào

Nếu muốn hiểu kiến trúc hiện tại:

1. `architecture/project-architecture.md`
2. `architecture/rule-rendering-flows.md`
3. `architecture/tenants-relationship.md`
4. `architecture/mappings-relationship.md`
5. `architecture/execution-relationship.md`

Nếu muốn hiểu trạng thái thay đổi gần đây:

1. `note/repo-gap-review-2026-03-23.md`
2. `note/logs/code/*.md`

## Nguyên tắc tài liệu

- Giữ nguyên định hướng kiến trúc khi cập nhật README và note.
- Phân biệt rõ tài liệu kiến trúc với note lịch sử.
- Nếu implementation đang ở trạng thái chuyển tiếp, mô tả current state mà không thay đổi kiến trúc nền.

## Tóm tắt

`docs/` là điểm vào chính để hiểu repo. Với kiến trúc, ưu tiên `docs/architecture/`. Với lịch sử thay đổi và drift, xem `docs/note/`.
