
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/bekabigeldigmail.com/PycharmProjects/Data-Extraction-from-Invoice-Images/new_edited/key.json"
print("GOOGLE_APPLICATION_CREDENTIALS:", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

import json
from datetime import datetime
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from google.cloud import documentai_v1 as documentai


project_id = "focused-veld-466306-k2"
location = "us"
processor_id = "b3a6b671d72f41ba"

app = FastAPI(title="Document AI Form Parser with Table Extraction")


@app.post("/ocr/")
async def parse_invoice(file: UploadFile = File(...)):
    try:
        client = documentai.DocumentProcessorServiceClient()
        name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

        file_content = await file.read()
        raw_document = documentai.RawDocument(content=file_content, mime_type=file.content_type)

        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        result = client.process_document(request=request)
        document = result.document

        # ✅ Извлечение полного текста
        full_text = document.text

        # ✅ Извлечение таблиц из pages
        items = []
        text = document.text

        for page in document.pages:
            for table in page.tables:
                 for row in list(table.header_rows) + list(table.body_rows):
                    item = {}
                    cells = row.cells
                    for idx, cell in enumerate(cells):
                        try:
                            segments = cell.layout.text_anchor.text_segments
                            if segments:
                                start_idx = int(segments[0].start_index)
                                end_idx = int(segments[0].end_index)
                                cell_text = text[start_idx:end_idx].strip()
                                item[f'col_{idx}'] = cell_text
                        except Exception as e:
                            print(f"Error extracting cell: {e}")
                            continue
                    if item:
                        items.append(item)

        # ✅ Простое извлечение ключевых полей через keywords
        extracted_fields = {
            "iin": None,
            "bic": None,
            "total": None,
            "date": None
        }

        if "БИН" in full_text:
            idx = full_text.find("БИН")
            extracted_fields["iin"] = full_text[idx:idx + 30].split()[-1]

        if "БИК" in full_text:
            idx = full_text.find("БИК")
            extracted_fields["bic"] = full_text[idx:idx + 30].split()[-1]

        if "Итого" in full_text:
            idx = full_text.find("Итого")
            extracted_fields["total"] = full_text[idx:idx + 50].split()[-1]

        if "от" in full_text and "г." in full_text:
            idx1 = full_text.find("от")
            idx2 = full_text.find("г.", idx1)
            extracted_fields["date"] = full_text[idx1 + 2:idx2].strip()

        output = {
            "file_name": file.filename,
            "uploaded_at": datetime.utcnow().isoformat(),
            "text": full_text,
            "items": items,
            "extracted_fields": extracted_fields
        }

        # ✅ Сохраняем в results.json
        if os.path.exists("results.json"):
            with open("results.json", "r") as f:
                data = json.load(f)
        else:
            data = []

        data.append(output)

        with open("results.json", "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return JSONResponse(content=output)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# print("GOOGLE_APPLICATION_CREDENTIALS:", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

# import os
# # ✅ Убедись, что путь правильный и без пробелов
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/bekabigeldigmail.com/PycharmProjects/Data-Extraction-from-Invoice-Images/new_edited/key.json"
# print("GOOGLE_APPLICATION_CREDENTIALS:", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
#
# import json
# from datetime import datetime
# import uvicorn
# from fastapi import FastAPI, UploadFile, File
# from fastapi.responses import JSONResponse
# from google.cloud import documentai_v1 as documentai
#
# project_id = "focused-veld-466306-k2"
# location = "us"
# processor_id = "b3a6b671d72f41ba"
#
# app = FastAPI(title="Document AI Form Parser with Table Extraction")
#
# @app.post("/ocr/")
# async def parse_invoice(file: UploadFile = File(...)):
#     try:
#         client = documentai.DocumentProcessorServiceClient()
#         name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
#
#         file_content = await file.read()
#         raw_document = documentai.RawDocument(content=file_content, mime_type=file.content_type)
#         request = documentai.ProcessRequest(name=name, raw_document=raw_document)
#         result = client.process_document(request=request)
#         document = result.document
#
#         full_text = document.text
#
#         output = {
#             "file_name": file.filename,
#             "uploaded_at": datetime.utcnow().isoformat(),
#             "text": full_text
#         }
#
#         return JSONResponse(content=output)
#
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": str(e)})
#
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
