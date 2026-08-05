# TOEIC Study Deck

Công cụ học TOEIC chạy offline. Python tự quét ảnh trong `data`, encode toàn bộ
ảnh thành Base64 và tạo một file `index.html` độc lập.

## Cấu trúc project

```text
__Toeic/
├── data/
│   ├── h2/
│   │   ├── test01/
│   │   │   ├── 131_BCCB.png
│   │   │   └── ...
│   │   ├── test02/
│   │   └── ...
│   ├── h3/
│   │   ├── test01/
│   │   ├── test02/
│   │   └── ...
│   └── others/
│       ├── 1_ABCD.png
│       └── grammar/
│           └── 10_BCDA.png
├── tool/
│   ├── build.py
│   └── template.html
├── index.html
└── README.md
```

Quy ước hiển thị trên giao diện:

| Folder | Tên sách trên UI |
|---|---|
| `data/h2` | Hacker 2 |
| `data/h3` | Hacker 3 |
| `data/others` | Khác |

Các test bên trong sách đặt tên `test01`, `test02`, `test03`...

Folder được phép để trống. Test hoặc sách chưa có ảnh sẽ chưa xuất hiện trong
danh sách lựa chọn trên giao diện.

## Quy ước tên ảnh

```text
<số-câu-bắt-đầu>_<chuỗi-đáp-án>.<đuôi-file>
```

Ví dụ:

```text
156_AXCD.png
```

Được hiểu là:

| Câu | Đáp án |
|---:|:---:|
| 156 | A |
| 157 | X |
| 158 | C |
| 159 | D |

Mỗi ký tự trong chuỗi đáp án ứng với một câu liên tiếp, bắt đầu từ số đầu tiên
trong tên file.

Ký tự hợp lệ:

- `A`, `B`, `C`, `D`: đáp án chính thức.
- `X`: chưa có đáp án; câu vẫn hiển thị nhưng không bắt buộc trả lời và không
  được tính điểm.

Định dạng ảnh được hỗ trợ:

- `.png`
- `.jpg`
- `.jpeg`
- `.webp`
- `.gif`

Regex được builder sử dụng:

```python
r"^(?P<start>\d+)_(?P<answers>[ABCDX]+)\.(png|jpe?g|webp|gif)$"
```

Tên file không phân biệt chữ hoa và chữ thường, nhưng nên dùng đáp án viết hoa
để dễ đọc.

## Kiểm tra dữ liệu

Builder quét đệ quy toàn bộ `data`.

Nếu có bất kỳ ảnh nào sai quy ước tên, builder sẽ:

1. Quét và liệt kê đầy đủ các ảnh không hợp lệ.
2. Báo đường dẫn cùng định dạng tên được yêu cầu.
3. Kết thúc với exit code khác `0`.
4. Không tạo mới hoặc ghi đè `index.html` hiện có.

Các file không phải ảnh và folder rỗng được bỏ qua. Nếu toàn bộ `data` chưa có
ảnh, builder vẫn tạo trang với trạng thái chưa có dữ liệu.

## Build `index.html`

Mở PowerShell tại folder `__Toeic`:

```powershell
cd D:\Work\Projects\NTA\gitlabe2\__Toeic
python .\tool\build.py
```

Nếu Python chưa được thêm vào `PATH` trên máy hiện tại:

```powershell
& "C:\Users\dthoi\AppData\Local\Programs\Python\Python312\python.exe" .\tool\build.py
```

Builder chỉ dùng Python standard library, không cần cài thêm package.

Sau khi chạy thành công, mở:

```text
D:\Work\Projects\NTA\gitlabe2\__Toeic\index.html
```

Mỗi lần thêm, xóa, đổi tên ảnh hoặc sửa đáp án trong tên file, cần chạy lại
builder để tạo `index.html` mới.

## Chức năng giao diện

### Chọn nội dung

- Chọn sách: Hacker 2, Hacker 3 hoặc Khác.
- Sau khi chọn sách, danh sách chỉ hiện các test thuộc sách đó.
- Chọn một test cụ thể hoặc “Tất cả test” để học toàn bộ sách.
- Học theo thứ tự.
- Xáo trộn ảnh ngẫu nhiên.
- Ôn lại các ảnh có câu trả lời sai trong phiên hiện tại.

### Làm và chấm bài

- Hiển thị ảnh đề mà không hiển thị tên file chứa đáp án.
- Hiển thị các radio A/B/C/D chia đều theo chiều rộng panel.
- Mỗi câu chỉ chọn được một đáp án.
- Không bắt buộc chọn câu có đáp án `X`.
- Sau khi chấm, từng câu hiển thị trạng thái:
  - `✓ Đúng` màu xanh.
  - `✕ Sai · Đáp án B` màu đỏ; lựa chọn sai màu đỏ và đáp án đúng màu xanh.
  - `— Không tính điểm` đối với câu `X`.
- Có nút chuyển về ảnh trước hoặc sang ảnh tiếp theo.

### Điểm

- Tổng số câu đúng.
- Tổng số câu sai.
- Tỷ lệ đúng trên các câu có đáp án A/B/C/D.
- Câu `X` không được đưa vào kết quả và mẫu số tính điểm.
- Điểm và danh sách bài sai được giữ trong bộ nhớ của trang; tải lại trang sẽ
  bắt đầu phiên mới.

## Cách thêm dữ liệu

Ví dụ thêm ảnh cho Hacker 3, Test 02:

```text
data/h3/test02/131_ABCD.png
data/h3/test02/135_BCDA.png
```

Ví dụ thêm bài không thuộc hai sách Hacker:

```text
data/others/1_ABCD.png
```

Hoặc chia thành nhóm riêng:

```text
data/others/vocabulary/1_ABCD.png
data/others/grammar/20_BCDA.png
```

Sau đó chạy lại `tool/build.py`. Sách, test, số câu và đáp án sẽ được suy luận
tự động; không cần tạo `answers.json`.
